# tests/test_voice_dissimilarity.py
from pathlib import Path
import pytest
from tools.voice_dissimilarity import check_scene


def test_distinct_voices_pass(fixtures_dir):
    rep = check_scene(fixtures_dir / "mini_scenes" / "scene-distinct.md", threshold=0.65)
    assert rep.exit_code() == 0


def test_voice_bleed_flagged(fixtures_dir):
    rep = check_scene(fixtures_dir / "mini_scenes" / "scene-bleed.md", threshold=0.65)
    assert rep.exit_code() == 1
    assert any("voice bleed" in i.message.lower() for i in rep.errors())
