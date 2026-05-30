# tests/test_frontmatter_validator.py
from pathlib import Path
import pytest
from tools.frontmatter_validator import validate_directory


def test_valid_artifact_passes(tmp_path):
    art_path = tmp_path / "thesis.md"
    art_path.write_text(
        "---\nid: t-1\nversion: 1\nstatus: draft\nreferences: []\n---\nbody",
        encoding="utf-8",
    )
    rep = validate_directory(tmp_path)
    assert rep.exit_code() == 0


def test_duplicate_id_flagged(tmp_path):
    (tmp_path / "a.md").write_text(
        "---\nid: dup\nversion: 1\nstatus: draft\nreferences: []\n---\nb",
        encoding="utf-8",
    )
    (tmp_path / "b.md").write_text(
        "---\nid: dup\nversion: 1\nstatus: draft\nreferences: []\n---\nb",
        encoding="utf-8",
    )
    rep = validate_directory(tmp_path)
    assert rep.exit_code() == 1
    assert any("duplicate id" in i.message for i in rep.errors())


def test_invalid_status_flagged(tmp_path):
    (tmp_path / "x.md").write_text(
        "---\nid: x\nversion: 1\nstatus: bogus\nreferences: []\n---\nb",
        encoding="utf-8",
    )
    rep = validate_directory(tmp_path)
    assert rep.exit_code() == 1
