# tests/test_common_reporter.py
import json
import pytest
from tools._common.reporter import Reporter, Issue, IssueLevel


def test_empty_reporter_passes():
    r = Reporter(script="frontmatter_validator")
    assert r.exit_code() == 0
    assert json.loads(r.to_json())["status"] == "pass"


def test_reporter_with_error_fails():
    r = Reporter(script="x")
    r.add_issue(Issue(level=IssueLevel.ERROR, path="x.md", message="bad"))
    assert r.exit_code() == 1
    payload = json.loads(r.to_json())
    assert payload["status"] == "fail"
    assert len(payload["issues"]) == 1
    assert payload["issues"][0]["level"] == "error"


def test_reporter_warning_does_not_fail():
    r = Reporter(script="x")
    r.add_issue(Issue(level=IssueLevel.WARNING, path="x.md", message="dim"))
    assert r.exit_code() == 0
    payload = json.loads(r.to_json())
    assert payload["status"] == "pass"
    assert len(payload["warnings"]) == 1


def test_reporter_serializes_path_object():
    from pathlib import Path
    r = Reporter(script="x")
    r.add_issue(Issue(level=IssueLevel.ERROR, path=Path("some/file.md"), message="m"))
    payload = json.loads(r.to_json())
    assert payload["issues"][0]["path"] == str(Path("some/file.md"))


def test_reporter_accepts_string_level():
    r = Reporter(script="x")
    r.add_issue(Issue(level="error", path="x.md", message="m"))
    assert r.exit_code() == 1
    payload = json.loads(r.to_json())
    assert payload["issues"][0]["level"] == "error"
