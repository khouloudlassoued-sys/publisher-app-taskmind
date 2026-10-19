import json
import os
import subprocess
import time
import xml.etree.ElementTree as ET
from pathlib import Path
from unittest.mock import Mock, patch

import pytest

import unit_test_validation as validation


BACKEND_CLASS = "sample.BookServiceImplTest"
KNOWN_BACKEND = {
    "class": BACKEND_CLASS,
    "name": "known_backend_failure",
    "kind": "failure",
    "proof": "verified on main",
}
KNOWN_FRONTEND = {
    "suite": "AppComponent",
    "name": "should render title",
    "kind": "failure",
    "proof": "verified on main",
}
FRONTEND_SUCCESS_OUTPUT = "Executed 4 of 4 SUCCESS"
FRONTEND_KNOWN_FAILURE_OUTPUT = (
    "TOTAL: 1 FAILED, 3 SUCCESS\n"
    "Chrome Headless 155.0.0.0 (Windows 10) "
    "AppComponent should render title FAILED"
)
KARMA_ANSI_OUTPUT = (
    "\x1b[1A\x1b[2K\x1b[31mChrome Headless 155.0.0.0 (Windows 10) "
    "AppComponent should render title FAILED\x1b[39m\n"
    "Chrome Headless 155.0.0.0 (Windows 10): Executed 3 of 7"
    "\x1b[31m (1 FAILED)\x1b[39m (0 secs / 0.297 secs)\n"
    "\x1b[1A\x1b[2KChrome Headless 155.0.0.0 (Windows 10): Executed 7 of 7"
    "\x1b[31m (1 FAILED)\x1b[39m (0.333 secs / 0.317 secs)\n"
    "\x1b[31mTOTAL: 1 FAILED, 6 SUCCESS\x1b[39m"
)


def _known_file(path, backend=None, frontend=None):
    path.write_text(
        json.dumps({
            "backend": [KNOWN_BACKEND] if backend is None else backend,
            "frontend": [KNOWN_FRONTEND] if frontend is None else frontend,
        }),
        encoding="utf-8",
    )
    return path


def _write_report(repo_root, cases, mtime=None):
    report_directory = repo_root / "spring-publisher-service" / "target" / "surefire-reports"
    report_directory.mkdir(parents=True, exist_ok=True)
    suite = ET.Element("testsuite")
    for classname, name, kind in cases:
        testcase = ET.SubElement(suite, "testcase", classname=classname, name=name)
        if kind:
            ET.SubElement(testcase, kind, message="test failure")
    report = report_directory / "TEST-sample.xml"
    ET.ElementTree(suite).write(report, encoding="utf-8", xml_declaration=True)
    if mtime is not None:
        os.utime(report, (mtime, mtime))
    return report


def _completed(stdout="", returncode=0, stderr=""):
    return subprocess.CompletedProcess(
        args=[],
        returncode=returncode,
        stdout=stdout,
        stderr=stderr,
    )


@pytest.fixture
def passing_test_environment(tmp_path, monkeypatch):
    monkeypatch.setattr(validation.socket, "create_connection", lambda *args, **kwargs: Mock())
    monkeypatch.delenv("JWT_SECRET", raising=False)
    monkeypatch.setenv("POSTGRES_PORT", "5432")
    backend_dir = tmp_path / "spring-publisher-service"
    backend_dir.mkdir()
    wrapper_name = "mvnw.cmd" if os.name == "nt" else "mvnw"
    (backend_dir / wrapper_name).touch()
    known_path = _known_file(tmp_path / "known_failures.json")
    return tmp_path, known_path


def test_only_known_failures_fail_no_new_findings(passing_test_environment):
    repo_root, known_path = passing_test_environment
    _write_report(repo_root, [(BACKEND_CLASS, KNOWN_BACKEND["name"], "failure")], mtime=100)
    now = Mock(return_value=100)
    runner = Mock(side_effect=[
        _completed(returncode=1),
        _completed(FRONTEND_KNOWN_FAILURE_OUTPUT, returncode=1),
    ])

    result = validation.validate_unit_tests(repo_root, known_path, runner=runner, now=now)

    assert result["status"] == "passed"
    assert result["reason"] == ""
    assert len(result["known_failures_still_failing"]) == 2
    assert result["new_failures"] == []


def test_new_backend_failure_is_reported(passing_test_environment):
    repo_root, known_path = passing_test_environment
    _write_report(
        repo_root,
        [(BACKEND_CLASS, "new_backend_failure", "failure")],
        mtime=100,
    )
    runner = Mock(side_effect=[
        _completed(returncode=1),
        _completed(FRONTEND_SUCCESS_OUTPUT),
    ])

    result = validation.validate_unit_tests(
        repo_root, known_path, runner=runner, now=lambda: 100
    )

    assert result["status"] == "failed"
    assert result["reason"] == "new_failures"
    assert result["new_failures"] == [{
        "suite": "backend",
        "class": BACKEND_CLASS,
        "name": "new_backend_failure",
        "kind": "failure",
    }]


def test_new_frontend_failure_is_parsed(passing_test_environment):
    repo_root, known_path = passing_test_environment
    _write_report(repo_root, [], mtime=100)
    output = (
        "TOTAL: 1 FAILED, 2 SUCCESS\n"
        "Chrome Headless 155.0.0.0 (Windows 10) "
        "AppComponent should newly fail FAILED"
    )
    runner = Mock(side_effect=[_completed(), _completed(output)])

    result = validation.validate_unit_tests(
        repo_root, known_path, runner=runner, now=lambda: 100
    )

    assert result["status"] == "failed"
    assert result["new_failures"] == [{
        "suite": "frontend",
        "description": "AppComponent should newly fail",
        "kind": "failure",
    }]


def test_ansi_karma_output_keeps_known_frontend_failure(passing_test_environment):
    repo_root, known_path = passing_test_environment
    _write_report(
        repo_root,
        [(BACKEND_CLASS, KNOWN_BACKEND["name"], "failure")],
        mtime=100,
    )
    runner = Mock(side_effect=[
        _completed(returncode=1),
        _completed(KARMA_ANSI_OUTPUT, returncode=1),
    ])

    result = validation.validate_unit_tests(
        repo_root, known_path, runner=runner, now=lambda: 100
    )

    assert result["frontend"]["failures"] == [{
        "description": "AppComponent should render title",
        "kind": "failure",
    }]
    assert result["frontend"]["summary"] == {"failed": 1, "success": 6}
    assert result["known_failures_still_failing"] == [
        {**KNOWN_BACKEND, "observed_kind": "failure"},
        {**KNOWN_FRONTEND, "observed_kind": "failure"},
    ]
    assert result["known_failures_now_passing"] == []


def test_duplicate_frontend_failure_description_is_counted_once(passing_test_environment):
    repo_root, known_path = passing_test_environment
    _write_report(repo_root, [], mtime=100)
    duplicate_line = (
        "\x1b[1A\x1b[2K\x1b[31mChrome Headless 155.0.0.0 (Windows 10) "
        "AppComponent should render title FAILED\x1b[39m"
    )
    output = f"{duplicate_line}\n{duplicate_line}\nTOTAL: 1 FAILED, 6 SUCCESS"
    runner = Mock(side_effect=[
        _completed(),
        _completed(output, returncode=1),
    ])

    result = validation.validate_unit_tests(
        repo_root, known_path, runner=runner, now=lambda: 100
    )

    assert result["frontend"]["failures"] == [{
        "description": "AppComponent should render title",
        "kind": "failure",
    }]
    assert result["status"] == "passed"


def test_frontend_failure_count_mismatch_fails_closed(passing_test_environment):
    repo_root, known_path = passing_test_environment
    _write_report(
        repo_root,
        [(BACKEND_CLASS, KNOWN_BACKEND["name"], "failure")],
        mtime=100,
    )
    output = KARMA_ANSI_OUTPUT.replace(
        "TOTAL: 1 FAILED, 6 SUCCESS", "TOTAL: 2 FAILED, 5 SUCCESS"
    )
    runner = Mock(side_effect=[
        _completed(returncode=1),
        _completed(output, returncode=1),
    ])

    result = validation.validate_unit_tests(
        repo_root, known_path, runner=runner, now=lambda: 100
    )

    assert result["status"] == "failed"
    assert result["reason"] == "frontend_parse_mismatch"
    assert not any(
        item.get("suite") == "frontend"
        for item in result["known_failures_now_passing"]
    )


def test_known_failure_that_passes_is_reported_as_now_passing(passing_test_environment):
    repo_root, known_path = passing_test_environment
    _write_report(repo_root, [], mtime=100)
    runner = Mock(side_effect=[
        _completed(),
        _completed(FRONTEND_SUCCESS_OUTPUT),
    ])

    result = validation.validate_unit_tests(
        repo_root, known_path, runner=runner, now=lambda: 100
    )

    assert result["status"] == "passed"
    assert result["known_failures_now_passing"] == [KNOWN_BACKEND, KNOWN_FRONTEND]


def test_stale_backend_report_is_ignored(passing_test_environment):
    repo_root, known_path = passing_test_environment
    _write_report(repo_root, [(BACKEND_CLASS, "stale_failure", "failure")], mtime=99)
    runner = Mock(return_value=_completed())

    result = validation.validate_unit_tests(
        repo_root, known_path, runner=runner, now=lambda: 100
    )

    assert result["status"] == "failed"
    assert result["reason"] == "no_backend_reports"
    assert runner.call_count == 1


def test_nonzero_backend_exit_without_reported_failures_fails_closed(
    passing_test_environment,
):
    repo_root, known_path = passing_test_environment
    _write_report(repo_root, [], mtime=100)
    runner = Mock(return_value=_completed(returncode=1))

    result = validation.validate_unit_tests(
        repo_root, known_path, runner=runner, now=lambda: 100
    )

    assert result["status"] == "failed"
    assert result["reason"] == "backend_exit_mismatch"
    assert runner.call_count == 1


def test_backend_runner_receives_absolute_existing_wrapper(passing_test_environment):
    repo_root, known_path = passing_test_environment
    _write_report(repo_root, [], mtime=100)
    runner = Mock(side_effect=[
        _completed(),
        _completed(FRONTEND_SUCCESS_OUTPUT),
    ])

    validation.validate_unit_tests(
        repo_root, known_path, runner=runner, now=lambda: 100
    )

    backend_command = runner.call_args_list[0].args[0]
    wrapper = Path(backend_command[0])
    assert wrapper.is_absolute()
    assert wrapper.name in {"mvnw.cmd", "mvnw"}
    assert wrapper.is_file()


def test_missing_maven_wrapper_prevents_runner_call(tmp_path, monkeypatch):
    monkeypatch.setattr(validation.socket, "create_connection", lambda *args, **kwargs: Mock())
    runner = Mock()

    result = validation.validate_unit_tests(
        tmp_path, tmp_path / "known_failures.json", runner=runner
    )

    assert result["status"] == "environment_error"
    assert result["reason"] == "maven_wrapper_missing"
    runner.assert_not_called()


def test_missing_npx_prevents_frontend_runner_call(passing_test_environment, monkeypatch):
    repo_root, known_path = passing_test_environment
    _write_report(repo_root, [], mtime=100)
    runner = Mock(return_value=_completed())
    monkeypatch.setattr(validation.shutil, "which", lambda executable: None)

    result = validation.validate_unit_tests(
        repo_root, known_path, runner=runner, now=lambda: 100
    )

    assert result["status"] == "environment_error"
    assert result["reason"] == "npx_missing"
    assert runner.call_count == 1


def test_unreachable_database_prevents_any_runner_call(tmp_path, monkeypatch):
    monkeypatch.setattr(
        validation.socket,
        "create_connection",
        Mock(side_effect=OSError("connection refused")),
    )
    runner = Mock()

    result = validation.validate_unit_tests(
        tmp_path, tmp_path / "missing.json", runner=runner
    )

    assert result["status"] == "environment_error"
    assert result["reason"] == "database_unreachable"
    runner.assert_not_called()


def test_missing_jwt_secret_is_generated_for_subprocess_without_leaking(
    passing_test_environment,
    monkeypatch,
    caplog,
    capsys,
):
    repo_root, known_path = passing_test_environment
    _write_report(repo_root, [], mtime=100)
    generated_secret = "test-generated-secret-must-not-leak"
    monkeypatch.setattr(validation.secrets, "token_hex", Mock(return_value=generated_secret))
    seen_environments = []

    def runner(command, **kwargs):
        seen_environments.append(kwargs["env"])
        if Path(command[0]).name in {"mvnw.cmd", "mvnw"}:
            return _completed()
        return _completed(FRONTEND_SUCCESS_OUTPUT)

    result = validation.validate_unit_tests(
        repo_root, known_path, runner=runner, now=lambda: 100
    )
    captured = capsys.readouterr()
    serialized_result = json.dumps(result)

    assert len(seen_environments) == 2
    assert all(env["JWT_SECRET"] == generated_secret for env in seen_environments)
    assert generated_secret not in serialized_result
    assert generated_secret not in captured.out
    assert generated_secret not in captured.err
    assert generated_secret not in caplog.text


def test_backend_timeout_returns_timeout_status(passing_test_environment):
    repo_root, known_path = passing_test_environment
    runner = Mock(side_effect=subprocess.TimeoutExpired(["mvnw", "test"], 600))

    result = validation.validate_unit_tests(
        repo_root, known_path, runner=runner, now=lambda: 100
    )

    assert result["status"] == "timeout"
    assert result["reason"] == "backend_timeout"
    assert runner.call_count == 1
