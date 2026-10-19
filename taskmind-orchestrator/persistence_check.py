import argparse
import json
import subprocess
import sys
from pathlib import Path
from typing import Any, Callable


def _run_git(
    runner: Callable[..., Any],
    arguments: list[str],
    repo_root: Path,
) -> Any:
    return runner(
        ["git", *arguments],
        cwd=repo_root,
        capture_output=True,
        text=True,
    )


def _result(
    status: str,
    reason: str,
    feature: str,
    missing: list[str] | None = None,
    empty: list[str] | None = None,
    untracked: list[str] | None = None,
    uncommitted: list[str] | None = None,
) -> dict[str, Any]:
    return {
        "status": status,
        "reason": reason,
        "feature": feature,
        "missing": missing or [],
        "empty": empty or [],
        "untracked": untracked or [],
        "uncommitted": uncommitted or [],
    }


def check_persistence(
    repo_root: Path,
    feature: str | None = None,
    runner: Callable[..., Any] = subprocess.run,
) -> dict[str, Any]:
    repo_root = Path(repo_root)
    if feature is None:
        try:
            branch = _run_git(runner, ["rev-parse", "--abbrev-ref", "HEAD"], repo_root)
        except OSError:
            return _result("environment_error", "git_unavailable", "")
        if branch.returncode != 0:
            return _result("environment_error", "git_unavailable", "")
        feature = branch.stdout.strip()

    feature_directory = repo_root / "specs" / feature
    if not feature_directory.is_dir():
        return _result("failed", "feature_dir_missing", feature)

    missing: list[str] = []
    empty: list[str] = []
    untracked: list[str] = []
    uncommitted: list[str] = []

    for name in ("spec.md", "plan.md", "tasks.md"):
        file_path = feature_directory / name
        relative_path = file_path.relative_to(repo_root).as_posix()
        if not file_path.is_file():
            missing.append(relative_path)
            continue
        if not file_path.read_text(encoding="utf-8").strip():
            empty.append(relative_path)

        try:
            tracked = _run_git(
                runner,
                ["ls-files", "--error-unmatch", relative_path],
                repo_root,
            )
        except OSError:
            return _result(
                "environment_error", "git_unavailable", feature,
                missing, empty, untracked, uncommitted,
            )
        if tracked.returncode != 0:
            untracked.append(relative_path)
            continue

        try:
            status = _run_git(
                runner,
                ["status", "--porcelain", "--", relative_path],
                repo_root,
            )
        except OSError:
            return _result(
                "environment_error", "git_unavailable", feature,
                missing, empty, untracked, uncommitted,
            )
        if status.returncode != 0:
            return _result(
                "environment_error", "git_unavailable", feature,
                missing, empty, untracked, uncommitted,
            )
        if status.stdout.strip():
            uncommitted.append(relative_path)

    categories = (
        ("missing", missing),
        ("empty", empty),
        ("untracked", untracked),
        ("uncommitted", uncommitted),
    )
    for reason, paths in categories:
        if paths:
            return _result(
                "failed", reason, feature, missing, empty, untracked, uncommitted
            )
    return _result("passed", "", feature)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--feature")
    arguments = parser.parse_args()

    repo_root = Path(__file__).resolve().parent.parent
    result = check_persistence(repo_root, feature=arguments.feature)
    print(json.dumps(result, indent=2))
    if result["status"] == "passed":
        return 0
    if result["status"] == "environment_error":
        return 2
    return 1


if __name__ == "__main__":
    sys.exit(main())
