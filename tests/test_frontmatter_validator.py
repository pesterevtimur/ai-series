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


def test_nonexistent_root_flagged(tmp_path):
    rep = validate_directory(tmp_path / "does-not-exist")
    assert rep.exit_code() == 1
    assert any("does not exist" in i.message for i in rep.errors())


def test_root_is_file_flagged(tmp_path):
    f = tmp_path / "x.md"
    f.write_text("---\nid: x\nversion: 1\nstatus: draft\nreferences: []\n---\nb", encoding="utf-8")
    rep = validate_directory(f)
    assert rep.exit_code() == 1
    assert any("not a directory" in i.message for i in rep.errors())


def test_readme_and_underscore_files_skipped(tmp_path):
    (tmp_path / "README.md").write_text("# Not an artefact", encoding="utf-8")
    (tmp_path / "_template.md").write_text("---\nplaceholder: yes\n---\ntpl", encoding="utf-8")
    (tmp_path / "real.md").write_text(
        "---\nid: r\nversion: 1\nstatus: draft\nreferences: []\n---\nb",
        encoding="utf-8",
    )
    rep = validate_directory(tmp_path)
    assert rep.exit_code() == 0  # README and _template skipped; real.md is valid


def test_non_utf8_file_flagged(tmp_path):
    bad = tmp_path / "bad.md"
    bad.write_bytes(b"---\nid: x\n---\n\xff\xfe binary")
    rep = validate_directory(tmp_path)
    assert rep.exit_code() == 1
    assert any("not valid UTF-8" in i.message for i in rep.errors())
