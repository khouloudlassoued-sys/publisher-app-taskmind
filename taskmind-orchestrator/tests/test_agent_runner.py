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
