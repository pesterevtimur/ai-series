# tests/test_consistency_check.py
from pathlib import Path
import pytest
from tools.consistency_check import check_consistency


def test_resolved_references_pass(fixtures_dir):
    rep = check_consistency(fixtures_dir / "mini_bible")
    assert rep.exit_code() == 0


def test_dangling_reference_flagged(tmp_path):
    (tmp_path / "a.md").write_text(
        "---\nid: a\nversion: 1\nstatus: draft\nreferences: [missing-id]\n---\nb",
        encoding="utf-8",
    )
    rep = check_consistency(tmp_path)
    assert rep.exit_code() == 1
    assert any("dangling reference 'missing-id'" in i.message for i in rep.errors())
