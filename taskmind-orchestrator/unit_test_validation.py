import json
import os
import re
import secrets
import shutil
import socket
import subprocess
import sys
import time
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Any, Callable


BACKEND_TIMEOUT_S = 600
FRONTEND_TIMEOUT_S = 600
FRONTEND_FAILURE_PATTERN = re.compile(
    r"^Chrome Headless .*?\(Windows[^)]*\)\s+(?!:\s*Executed\b)(.+?)\s+FAILED\s*$",
    re.MULTILINE,
)
FRONTEND_TOTAL_PATTERN = re.compile(r"TOTAL: (\d+) FAILED, (\d+) SUCCESS")
FRONTEND_EXECUTED_PATTERN = re.compile(r"Executed (\d+) of (\d+) SUCCESS")


def _result(
    status: str,
    reason: str,
    backend: dict[str, Any] | None = None,
    frontend: dict[str, Any] | None = None,
    new_failures: list[dict[str, Any]] | None = None,
    known_failures_still_failing: list[dict[str, Any]] | None = None,
    known_failures_now_passing: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    return {
        "status": status,
        "reason": reason,
        "backend": backend or {},
        "frontend": frontend or {},
        "new_failures": new_failures or [],
        "known_failures_still_failing": known_failures_still_failing or [],
        "known_failures_now_passing": known_failures_now_passing or [],
    }


def _decode_output(output: str | bytes | None) -> str:
    if isinstance(output, bytes):
        return output.decode("utf-8", errors="replace")
    return output or ""


def _strip_ansi(text: str) -> str:
    return re.sub(r"\x1b\[[0-9;?]*[A-Za-z]", "", text)


def _read_backend_failures(report_directory: Path, started_at: float) -> tuple[list[dict[str, str]], int]:
    failures: list[dict[str, str]] = []
    fresh_report_count = 0

    for report_path in report_directory.glob("TEST-*.xml"):
        try:
            if report_path.stat().st_mtime < started_at:
                continue
            root = ET.parse(report_path).getroot()
        except (OSError, ET.ParseError):
            continue

        fresh_report_count += 1
        for testcase in root.iter("testcase"):
            kind = None
            if testcase.find("failure") is not None:
                kind = "failure"
            elif testcase.find("error") is not None:
                kind = "error"
            if kind is not None:
                failures.append(
                    {
                        "class": testcase.get("classname", ""),
                        "name": testcase.get("name", ""),
                        "kind": kind,
                    }
                )

    return failures, fresh_report_count


def _parse_frontend_output(output: str) -> tuple[list[dict[str, str]], dict[str, int] | None]:
    descriptions = dict.fromkeys(
        match.group(1) for match in FRONTEND_FAILURE_PATTERN.finditer(output)
    )
    failures = [
        {"description": description, "kind": "failure"}
        for description in descriptions
    ]
    total_match = FRONTEND_TOTAL_PATTERN.search(output)
    if total_match:
        summary = {
            "failed": int(total_match.group(1)),
            "success": int(total_match.group(2)),
        }
        return failures, summary

    executed_match = FRONTEND_EXECUTED_PATTERN.search(output)
    if executed_match:
        summary = {
            "failed": 0,
            "success": int(executed_match.group(1)),
        }
        return failures, summary

    return failures, None


def _matching_known_frontend_failure(
    failure: dict[str, str],
    known_frontend: list[dict[str, Any]],
) -> dict[str, Any] | None:
    for known in known_frontend:
        if failure["description"] == f'{known.get("suite", "")} {known.get("name", "")}':
            return known
    return None


def _read_known_failures(path: Path) -> dict[str, list[dict[str, Any]]]:
    with path.open(encoding="utf-8") as file:
        known = json.load(file)
    return {
        "backend": known.get("backend", []),
        "frontend": known.get("frontend", []),
    }


def validate_unit_tests(
    repo_root: Path,
    known_failures_path: Path,
    runner: Callable[..., Any] = subprocess.run,
    now: Callable[[], float] = time.time,
) -> dict[str, Any]:
    repo_root = Path(repo_root)
    known_failures_path = Path(known_failures_path)

    port = int(os.environ.get("POSTGRES_PORT", "5432"))
    try:
        connection = socket.create_connection(("localhost", port), timeout=3)
        connection.close()
    except (OSError, ValueError):
        return _result("environment_error", "database_unreachable")

    process_env = os.environ.copy()
    if not process_env.get("JWT_SECRET"):
        process_env["JWT_SECRET"] = secrets.token_hex(64)

    backend_dir = repo_root / "spring-publisher-service"
    wrapper = backend_dir / ("mvnw.cmd" if os.name == "nt" else "mvnw")
    if not wrapper.is_file():
        return _result("environment_error", "maven_wrapper_missing")
    backend_command = [str(wrapper), "test"]

    backend_started_at = now()
    try:
        backend_process = runner(
            backend_command,
            cwd=backend_dir,
            env=process_env.copy(),
            capture_output=True,
            timeout=BACKEND_TIMEOUT_S,
        )
    except subprocess.TimeoutExpired:
        return _result(
            "timeout",
            "backend_timeout",
            backend={"status": "timeout", "failures": [], "reports": 0},
        )
    except OSError as error:
        return _result(
            "environment_error",
            "backend_runner_error",
            backend={"status": "environment_error", "detail": str(error), "failures": [], "reports": 0},
        )

    backend_failures, backend_report_count = _read_backend_failures(
        repo_root / "spring-publisher-service" / "target" / "surefire-reports",
        backend_started_at,
    )
    backend_info = {
        "status": "passed" if not backend_failures else "failed",
        "exit_code": backend_process.returncode,
        "failures": backend_failures,
        "reports": backend_report_count,
    }
    if backend_report_count == 0:
        backend_info["status"] = "failed"
        return _result("failed", "no_backend_reports", backend=backend_info)
    if backend_process.returncode != 0 and not backend_failures:
        return _result("failed", "backend_exit_mismatch", backend=backend_info)

    npx = shutil.which("npx")
    if npx is None:
        return _result("environment_error", "npx_missing", backend=backend_info)
    frontend_env = process_env.copy()
    frontend_env["NG_CLI_ANALYTICS"] = "false"
    frontend_command = [
        npx,
        "ng",
        "test",
        "--watch=false",
        "--browsers=ChromeHeadless",
    ]
    try:
        frontend_process = runner(
            frontend_command,
            cwd=repo_root / "angular-publisher-service",
            env=frontend_env,
            capture_output=True,
            timeout=FRONTEND_TIMEOUT_S,
        )
    except subprocess.TimeoutExpired:
        return _result(
            "timeout",
            "frontend_timeout",
            backend=backend_info,
            frontend={"status": "timeout", "failures": [], "summary": None},
        )
    except OSError as error:
        return _result(
            "environment_error",
            "frontend_runner_error",
            backend=backend_info,
            frontend={"status": "environment_error", "detail": str(error), "failures": [], "summary": None},
        )

    frontend_output = "\n".join(
        part
        for part in (
            _strip_ansi(_decode_output(frontend_process.stdout)),
            _strip_ansi(_decode_output(frontend_process.stderr)),
        )
        if part
    )
    frontend_failures, frontend_summary = _parse_frontend_output(frontend_output)
    frontend_info = {
        "status": "passed" if not frontend_failures else "failed",
        "exit_code": frontend_process.returncode,
        "failures": frontend_failures,
        "summary": frontend_summary,
    }
    if frontend_summary is None:
        frontend_info["status"] = "failed"
        return _result(
            "failed",
            "no_frontend_summary",
            backend=backend_info,
            frontend=frontend_info,
        )
    frontend_parse_mismatch = (
        frontend_summary["failed"] != len(frontend_failures)
    )

    try:
        known_failures = _read_known_failures(known_failures_path)
    except (OSError, json.JSONDecodeError) as error:
        return _result(
            "environment_error",
            "known_failures_unreadable",
            backend=backend_info,
            frontend=frontend_info,
        )

    known_backend = known_failures["backend"]
    known_frontend = known_failures["frontend"]
    new_failures: list[dict[str, Any]] = []
    known_failures_still_failing: list[dict[str, Any]] = []

    failed_backend_keys = set()
    for failure in backend_failures:
        key = (failure["class"], failure["name"])
        failed_backend_keys.add(key)
        known = next(
            (
                item
                for item in known_backend
                if item.get("class") == failure["class"] and item.get("name") == failure["name"]
            ),
            None,
        )
        if known is None:
            new_failures.append({"suite": "backend", **failure})
        else:
            known_failures_still_failing.append({**known, "observed_kind": failure["kind"]})

    failed_frontend_descriptions = set()
    for failure in frontend_failures:
        description = failure["description"]
        failed_frontend_descriptions.add(description)
        known = _matching_known_frontend_failure(failure, known_frontend)
        if known is None:
            new_failures.append({"suite": "frontend", **failure})
        else:
            known_failures_still_failing.append({**known, "observed_kind": failure["kind"]})

    known_failures_now_passing = [
        known
        for known in known_backend
        if (known.get("class"), known.get("name")) not in failed_backend_keys
    ]
    if not frontend_parse_mismatch:
        known_failures_now_passing.extend(
            known
            for known in known_frontend
            if f'{known.get("suite", "")} {known.get("name", "")}' not in failed_frontend_descriptions
        )

    if frontend_parse_mismatch:
        return _result(
            "failed",
            "frontend_parse_mismatch",
            backend=backend_info,
            frontend=frontend_info,
            new_failures=new_failures,
            known_failures_still_failing=known_failures_still_failing,
            known_failures_now_passing=known_failures_now_passing,
        )

    if new_failures:
        return _result(
            "failed",
            "new_failures",
            backend=backend_info,
            frontend=frontend_info,
            new_failures=new_failures,
            known_failures_still_failing=known_failures_still_failing,
            known_failures_now_passing=known_failures_now_passing,
        )

    return _result(
        "passed",
        "",
        backend=backend_info,
        frontend=frontend_info,
        known_failures_still_failing=known_failures_still_failing,
        known_failures_now_passing=known_failures_now_passing,
    )


def main() -> int:
    script_directory = Path(__file__).resolve().parent
    repo_root = script_directory.parent
    result = validate_unit_tests(repo_root, script_directory / "known_failures.json")
    print(json.dumps(result, indent=2))
    if result["status"] == "passed":
        return 0
    if result["status"] in {"environment_error", "timeout"}:
        return 2
    return 1


if __name__ == "__main__":
    sys.exit(main())
