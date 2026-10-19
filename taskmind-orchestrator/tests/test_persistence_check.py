import subprocess
from pathlib import Path
from unittest.mock import Mock

from persistence_check import check_persistence


FILENAMES = ("spec.md", "plan.md", "tasks.md")


def _git(repo_root: Path, *arguments: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["git", *arguments],
        cwd=repo_root,
        capture_output=True,
        text=True,
        check=True,
    )


def _repository(tmp_path: Path, feature: str = "001-example") -> Path:
    repo_root = tmp_path / "repo"
    repo_root.mkdir()
    _git(repo_root, "init")
    _git(repo_root, "config", "user.name", "Test User")
    _git(repo_root, "config", "user.email", "test@example.invalid")
    feature_directory = repo_root / "specs" / feature
    feature_directory.mkdir(parents=True)
    for filename in FILENAMES:
        (feature_directory / filename).write_text(f"{filename}\n", encoding="utf-8")
    _git(repo_root, "add", "specs")
    _git(repo_root, "commit", "-m", "Add feature artifacts")
    return repo_root


def test_committed_artifacts_pass(tmp_path):
    repo_root = _repository(tmp_path)

    result = check_persistence(repo_root, feature="001-example")

    assert result == {
        "status": "passed",
        "reason": "",
        "feature": "001-example",
        "missing": [],
        "empty": [],
        "untracked": [],
        "uncommitted": [],
    }


def test_missing_artifact_is_reported(tmp_path):
    repo_root = _repository(tmp_path)
    (repo_root / "specs" / "001-example" / "plan.md").unlink()

    result = check_persistence(repo_root, feature="001-example")

    assert result["status"] == "failed"
    assert result["reason"] == "missing"
    assert result["missing"] == ["specs/001-example/plan.md"]


def test_empty_artifact_is_reported(tmp_path):
    repo_root = _repository(tmp_path)
    (repo_root / "specs" / "001-example" / "plan.md").write_text(" \n\t", encoding="utf-8")

    result = check_persistence(repo_root, feature="001-example")

    assert result["status"] == "failed"
    assert result["reason"] == "empty"
    assert result["empty"] == ["specs/001-example/plan.md"]


def test_untracked_artifact_is_reported(tmp_path):
    repo_root = _repository(tmp_path)
    feature_directory = repo_root / "specs" / "001-example"
    (feature_directory / "tasks.md").unlink()
    (feature_directory / "tasks.md").write_text("new artifact\n", encoding="utf-8")
    _git(repo_root, "rm", "--cached", "specs/001-example/tasks.md")

    result = check_persistence(repo_root, feature="001-example")

    assert result["status"] == "failed"
    assert result["reason"] == "untracked"
    assert result["untracked"] == ["specs/001-example/tasks.md"]


def test_committed_artifact_with_local_modification_is_uncommitted(tmp_path):
    repo_root = _repository(tmp_path)
    (repo_root / "specs" / "001-example" / "plan.md").write_text(
        "modified\n", encoding="utf-8"
    )

    result = check_persistence(repo_root, feature="001-example")

    assert result["status"] == "failed"
    assert result["reason"] == "uncommitted"
    assert result["uncommitted"] == ["specs/001-example/plan.md"]


def test_missing_feature_directory_is_reported(tmp_path):
    repo_root = _repository(tmp_path)

    result = check_persistence(repo_root, feature="002-missing")

    assert result["status"] == "failed"
    assert result["reason"] == "feature_dir_missing"
    assert result["feature"] == "002-missing"


def test_feature_is_derived_from_current_branch(tmp_path):
    repo_root = _repository(tmp_path, feature="feature-current-branch")
    _git(repo_root, "checkout", "-b", "feature-current-branch")

    result = check_persistence(repo_root)

    assert result["status"] == "passed"
    assert result["feature"] == "feature-current-branch"


def test_missing_git_returns_environment_error(tmp_path):
    runner = Mock(side_effect=FileNotFoundError("git not found"))

    result = check_persistence(tmp_path, runner=runner)

    assert result["status"] == "environment_error"
    assert result["reason"] == "git_unavailable"
