import subprocess
from pathlib import Path
from unittest.mock import patch

from agent_runner import run_agent


def _mock_run_agent(paths_before, paths_after, process_side_effect):
    git_status = patch("agent_runner._get_git_status_paths", side_effect=[paths_before, paths_after])
    copilot = patch("agent_runner.shutil.which", return_value="copilot")
    process = patch("agent_runner._run_copilot", side_effect=process_side_effect)
    return git_status, copilot, process


def _completed(returncode=0, stdout="agent output"):
    return subprocess.CompletedProcess(args=["copilot"], returncode=returncode, stdout=stdout, stderr="")


def test_run_agent_success(tmp_path):
    expected = Path("specs") / "result.md"
    output_path = tmp_path / expected

    def run_process(command, repo_root, timeout_s):
        output_path.parent.mkdir(parents=True)
        output_path.write_text("Generated report", encoding="utf-8")
        return _completed(returncode=1)

    mocks = _mock_run_agent(set(), {expected.as_posix()}, run_process)
    with mocks[0], mocks[1], mocks[2]:
        result = run_agent("reviewer", "Review the change", expected, tmp_path)

    assert result.status == "ok"
    assert result.exit_code == 1
    assert result.stdout_tail == "agent output"


def test_run_agent_fails_when_output_is_missing_even_with_zero_exit_code(tmp_path):
    mocks = _mock_run_agent(set(), set(), lambda *args: _completed(returncode=0))
    with mocks[0], mocks[1], mocks[2]:
        result = run_agent("reviewer", "Review the change", "report.md", tmp_path)

    assert result.status == "failed"
    assert "exit code: 0" in result.detail


def test_run_agent_reports_unexpected_changes(tmp_path):
    expected = Path("report.md")
    output_path = tmp_path / expected
    other_path = Path("unrelated.txt")

    def run_process(command, repo_root, timeout_s):
        output_path.write_text("Generated report", encoding="utf-8")
        return _completed()

    mocks = _mock_run_agent(set(), {expected.as_posix(), other_path.as_posix()}, run_process)
    with mocks[0], mocks[1], mocks[2]:
        result = run_agent("reviewer", "Review the change", expected, tmp_path)

    assert result.status == "unexpected_changes"
    assert other_path.as_posix() in result.detail


def test_run_agent_returns_timeout(tmp_path):
    timeout_error = subprocess.TimeoutExpired("copilot", 1, output="partial output")
    mocks = _mock_run_agent(set(), set(), lambda *args: (_ for _ in ()).throw(timeout_error))
    with mocks[0], mocks[1], mocks[2]:
        result = run_agent("reviewer", "Review the change", "report.md", tmp_path, timeout_s=1)

    assert result.status == "timeout"
    assert result.stdout_tail == "partial output"


def test_run_agent_fails_when_existing_output_is_unchanged(tmp_path):
    expected = Path("report.md")
    (tmp_path / expected).write_text("Existing report", encoding="utf-8")
    mocks = _mock_run_agent(set(), set(), lambda *args: _completed(returncode=0))
    with mocks[0], mocks[1], mocks[2]:
        result = run_agent("reviewer", "Review the change", expected, tmp_path)

    assert result.status == "failed"
    assert "was not changed" in result.detail


def test_allowed_globs_accepts_and_reports_matching_new_files(tmp_path):
    spring_file = "spring-publisher-service/src/test/java/X/FooTest.java"
    angular_file = "angular-publisher-service/src/a/b/foo.spec.ts"

    def run_process(command, repo_root, timeout_s):
        for relative_path in (spring_file, angular_file):
            path = tmp_path / relative_path
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text("new file", encoding="utf-8")
        return _completed()

    mocks = _mock_run_agent(
        set(),
        {spring_file, angular_file},
        run_process,
    )
    with mocks[0], mocks[1], mocks[2]:
        result = run_agent(
            "reviewer",
            "Review changes",
            None,
            tmp_path,
            allowed_globs=[
                "spring-publisher-service/src/test/*",
                "angular-publisher-service/src/*.spec.ts",
            ],
        )

    assert result.status == "ok"
    assert result.changed_paths == sorted([spring_file, angular_file])


def test_allowed_globs_rejects_changed_file_outside_patterns(tmp_path):
    source_path = "spring-publisher-service/src/main/java/Foo.java"
    source_file = tmp_path / source_path
    source_file.parent.mkdir(parents=True)
    source_file.write_text("before", encoding="utf-8")

    def run_process(command, repo_root, timeout_s):
        source_file.write_text("after", encoding="utf-8")
        return _completed()

    mocks = _mock_run_agent(
        {source_path},
        {source_path},
        run_process,
    )
    with mocks[0], mocks[1], mocks[2]:
        result = run_agent(
            "reviewer",
            "Review changes",
            None,
            tmp_path,
            allowed_globs=["spring-publisher-service/src/test/*"],
        )

    assert result.status == "unexpected_changes"
    assert result.changed_paths == [source_path]
    assert source_path in result.detail


def test_allowed_globs_fails_when_no_allowed_path_changed(tmp_path):
    mocks = _mock_run_agent(set(), set(), lambda *args: _completed())
    with mocks[0], mocks[1], mocks[2]:
        result = run_agent(
            "reviewer",
            "Review changes",
            None,
            tmp_path,
            allowed_globs=["spring-publisher-service/src/test/*"],
        )

    assert result.status == "failed"
    assert result.detail == "No allowed path was changed"
    assert result.changed_paths == []


def test_existing_dirty_file_changed_during_run_is_unexpected_in_expected_mode(tmp_path):
    dirty_path = "dirty.txt"
    dirty_file = tmp_path / dirty_path
    dirty_file.write_text("before", encoding="utf-8")
    expected = Path("report.md")

    def run_process(command, repo_root, timeout_s):
        dirty_file.write_text("after", encoding="utf-8")
        (tmp_path / expected).write_text("Generated report", encoding="utf-8")
        return _completed()

    mocks = _mock_run_agent(
        {dirty_path},
        {dirty_path, expected.as_posix()},
        run_process,
    )
    with mocks[0], mocks[1], mocks[2]:
        result = run_agent("reviewer", "Review changes", expected, tmp_path)

    assert result.status == "unexpected_changes"
    assert dirty_path in result.detail


def test_existing_dirty_file_unchanged_during_run_is_not_unexpected(tmp_path):
    dirty_path = "dirty.txt"
    (tmp_path / dirty_path).write_text("unchanged", encoding="utf-8")
    expected = Path("report.md")

    def run_process(command, repo_root, timeout_s):
        (tmp_path / expected).write_text("Generated report", encoding="utf-8")
        return _completed()

    mocks = _mock_run_agent(
        {dirty_path},
        {dirty_path, expected.as_posix()},
        run_process,
    )
    with mocks[0], mocks[1], mocks[2]:
        result = run_agent("reviewer", "Review changes", expected, tmp_path)

    assert result.status == "ok"
