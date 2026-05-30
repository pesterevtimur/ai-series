# tests/test_golden_freshness.py
from pathlib import Path
import pytest
from tools.golden_freshness import check_golden


def test_minimum_threshold_passes(fixtures_dir):
    # min_positive_per_category=0 is vacuous — accepts empty categories
    # anti_total=1 is satisfied by the 1 anti-example in fixtures
    rep = check_golden(
        fixtures_dir / "mini_golden",
        min_positive_per_category=0,
        min_anti_total=1,
    )
    assert rep.exit_code() == 0


def test_below_threshold_fails(fixtures_dir):
    rep = check_golden(
        fixtures_dir / "mini_golden",
        min_positive_per_category=10,
        min_anti_total=1,
    )
    assert rep.exit_code() == 1


def test_author_share_diversity_warning(fixtures_dir):
    rep = check_golden(
        fixtures_dir / "mini_golden",
        min_positive_per_category=1,
        min_anti_total=1,
    )
    # 3/3 files in scenes are by Author A → author_share 100% > 50% threshold
    assert len(rep.diversity_warnings) > 0
    assert any("author" in w.message.lower() for w in rep.diversity_warnings)
