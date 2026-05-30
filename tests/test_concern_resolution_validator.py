# tests/test_concern_resolution_validator.py
from pathlib import Path
import pytest
from tools.concern_resolution_validator import check_resolution


def test_concern_with_no_resolution_fails(fixtures_dir, tmp_path):
    rep = check_resolution(
        tmp_critic_reports_dir=fixtures_dir / "mini_tmp_critic_reports",
        artifact_id="thesis-001",
        artifact_diff_text="",
        decisions_dir=tmp_path,
    )
    assert rep.exit_code() == 1
    assert any("unresolved concern" in i.message.lower() for i in rep.errors())


def test_concern_addressed_in_diff_passes(fixtures_dir, tmp_path):
    diff = "added line about counter-formulation per A5 concern: central thesis lacks counter-formulation"
    rep = check_resolution(
        tmp_critic_reports_dir=fixtures_dir / "mini_tmp_critic_reports",
        artifact_id="thesis-001",
        artifact_diff_text=diff,
        decisions_dir=tmp_path,
    )
    assert rep.exit_code() == 0


def test_concern_addressed_in_decision_passes(fixtures_dir, tmp_path):
    d = tmp_path / "D-003-keep-as-is.md"
    d.write_text(
        "---\nid: D-003\n---\n\nResolving A5 concern: central thesis lacks counter-formulation — leave as-is because...",
        encoding="utf-8",
    )
    rep = check_resolution(
        tmp_critic_reports_dir=fixtures_dir / "mini_tmp_critic_reports",
        artifact_id="thesis-001",
        artifact_diff_text="",
        decisions_dir=tmp_path,
    )
    assert rep.exit_code() == 0
