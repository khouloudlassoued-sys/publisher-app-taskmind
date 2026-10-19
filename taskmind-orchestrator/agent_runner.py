import hashlib
import fnmatch
import shutil
import subprocess
from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class RunResult:
    status: str
    detail: str
    exit_code: int | None
    stdout_tail: str
    changed_paths: list[str] = field(default_factory=list)


def _run_git_status(repo_root):
    result = subprocess.run(
        ["git", "status", "--porcelain", "--untracked-files=all"],
        cwd=repo_root,
        capture_output=True,
        text=True,
        check=True,
    )
    return result.stdout


def _get_git_status_paths(repo_root):
    status_output = _run_git_status(repo_root)
    paths = set()
    for line in status_output.splitlines():
        if len(line) < 4:
            continue
        path = line[3:]
        if " -> " in path:
            path = path.rsplit(" -> ", 1)[1]
        paths.add(Path(path).as_posix())
    return paths


def _run_copilot(command, repo_root, timeout_s):
    return subprocess.run(
        command,
        cwd=repo_root,
        capture_output=True,
        text=True,
        timeout=timeout_s,
        check=False,
    )


def _file_fingerprint(path):
    if not path.is_file():
        return None
    digest = hashlib.sha256()
    with path.open("rb") as file:
        for chunk in iter(lambda: file.read(8192), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _fingerprints_for_paths(paths, repo_root):
    return {
        path: _file_fingerprint(Path(repo_root) / Path(path))
        for path in paths
    }


def _changed_paths(before_paths, after_paths, before_fingerprints, repo_root):
    changed = set(after_paths - before_paths)
    for path, before_fingerprint in before_fingerprints.items():
        if _file_fingerprint(Path(repo_root) / Path(path)) != before_fingerprint:
            changed.add(path)
    return sorted(changed)


def _expected_relative_path(expected_output, repo_root):
    expected_path = Path(expected_output)
    root_path = Path(repo_root).resolve()
    if expected_path.is_absolute():
        try:
            expected_path = expected_path.resolve().relative_to(root_path)
        except ValueError:
            return expected_path.as_posix()
    return expected_path.as_posix()


def _output_tail(stdout):
    if isinstance(stdout, bytes):
        stdout = stdout.decode("utf-8", errors="replace")
    return (stdout or "")[-500:]


def run_agent(
    agent,
    prompt,
    expected_output,
    repo_root,
    timeout_s=600,
    allow_write=True,
    allowed_globs=None,
):
    root_path = Path(repo_root)
    expected_path = None
    if expected_output is not None:
        expected_path = Path(expected_output)
        if not expected_path.is_absolute():
            expected_path = root_path / expected_path

    try:
        before_paths = _get_git_status_paths(root_path)
    except (OSError, subprocess.CalledProcessError) as error:
        return RunResult("failed", f"Could not read git status: {error}", None, "")

    before_fingerprints = _fingerprints_for_paths(before_paths, root_path)
    before_fingerprint = _file_fingerprint(expected_path) if expected_path is not None else None
    if allowed_globs is None and expected_path is None:
        return RunResult("failed", "Expected output path is required.", None, "")
    executable = shutil.which("copilot")
    if executable is None:
        return RunResult("failed", "Could not find the copilot executable.", None, "")

    command = [executable, f"--agent={agent}", "-p", prompt, "--no-ask-user", "-s"]
    if allow_write:
        command.append("--allow-tool=write")

    try:
        process_result = _run_copilot(command, root_path, timeout_s)
    except subprocess.TimeoutExpired as error:
        return RunResult("timeout", f"Agent exceeded timeout of {timeout_s} seconds.", None,
                         _output_tail(error.stdout))
    except OSError as error:
        return RunResult("failed", f"Could not start copilot: {error}", None, "")

    exit_code = process_result.returncode
    stdout_tail = _output_tail(process_result.stdout)

    if expected_path is not None:
        after_fingerprint = _file_fingerprint(expected_path)
        if after_fingerprint is None:
            return RunResult("failed", f"Expected output does not exist after agent run (exit code: {exit_code}).",
                             exit_code, stdout_tail)
        if before_fingerprint is not None and after_fingerprint == before_fingerprint:
            return RunResult("failed", f"Expected output was not changed (exit code: {exit_code}).",
                             exit_code, stdout_tail)

    try:
        after_paths = _get_git_status_paths(root_path)
    except (OSError, subprocess.CalledProcessError) as error:
        return RunResult("failed", f"Could not read git status after agent run: {error}",
                         exit_code, stdout_tail)

    changed_paths = _changed_paths(
        before_paths, after_paths, before_fingerprints, root_path
    )
    if allowed_globs is not None:
        allowed_paths = [
            path
            for path in changed_paths
            if any(fnmatch.fnmatch(path, pattern) for pattern in allowed_globs)
        ]
        unexpected_paths = sorted(set(changed_paths) - set(allowed_paths))
        if unexpected_paths:
            return RunResult(
                "unexpected_changes",
                "Unexpected changed paths: " + ", ".join(unexpected_paths),
                exit_code,
                stdout_tail,
                changed_paths,
            )
        if not allowed_paths:
            return RunResult(
                "failed", "No allowed path was changed", exit_code, stdout_tail,
                changed_paths,
            )
        return RunResult("ok", "Allowed paths were changed.", exit_code, stdout_tail, changed_paths)

    expected_relative_path = _expected_relative_path(expected_output, root_path)
    unexpected_paths = sorted(set(changed_paths) - {expected_relative_path})
    if unexpected_paths:
        return RunResult(
            "unexpected_changes",
            "Unexpected changed paths: " + ", ".join(unexpected_paths),
            exit_code,
            stdout_tail,
        )

    return RunResult("ok", "Expected output was created or changed.", exit_code, stdout_tail)
