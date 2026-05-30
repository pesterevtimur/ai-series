# tests/test_critic_report_validator.py
from pathlib import Path
import pytest
from tools.critic_report_validator import validate_report


def test_valid_pass(fixtures_dir):
    rep = validate_report(
        fixtures_dir / "mini_critic_reports" / "valid_pass.yaml",
        smoke_test_mode=False,
    )
    assert rep.exit_code() == 0


def test_pass_without_counter_test_fails(fixtures_dir):
    rep = validate_report(
        fixtures_dir / "mini_critic_reports" / "invalid_pass_missing_counter_test.yaml",
        smoke_test_mode=False,
    )
    assert rep.exit_code() == 1
    msgs = [i.message for i in rep.errors()]
    assert any("counter_test_attempted" in m for m in msgs)
    assert any("reasoning" in m for m in msgs)  # < 100 words


def test_bootstrap_outside_smoketest_fails(fixtures_dir):
    rep = validate_report(
        fixtures_dir / "mini_critic_reports" / "invalid_bootstrap_outside_smoketest.yaml",
        smoke_test_mode=False,
    )
    assert rep.exit_code() == 1
    assert any("category-bootstrap" in i.message for i in rep.errors())


def test_bootstrap_inside_smoketest_passes(fixtures_dir):
    rep = validate_report(
        fixtures_dir / "mini_critic_reports" / "invalid_bootstrap_outside_smoketest.yaml",
        smoke_test_mode=True,
    )
    assert rep.exit_code() == 0


def test_not_applicable_requires_reason(tmp_path):
    rep_path = tmp_path / "rep.yaml"
    rep_path.write_text(
        "verdict: pass+not_applicable\nmodel_used: opus\n"
        "checked: [a, b, c]\nevidence_from_artifact: [x, y]\n"
        "golden_calibration_used: []\ngolden_unavailable_reason: category-irrelevant\n"
        "reasoning: " + " word" * 105 + "\n"
        "counter_test_attempted:\n  what_searched: x\n  why_this: y\n  why_not_found: z\n",
        encoding="utf-8",
    )
    rep = validate_report(rep_path, smoke_test_mode=False)
    assert rep.exit_code() == 1
    assert any("not_applicable_reason" in i.message for i in rep.errors())
