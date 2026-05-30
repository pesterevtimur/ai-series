# tests/test_common_artifact.py
from pathlib import Path
import pytest
from tools._common.artifact import Artifact, ArtifactError


def test_artifact_from_text_basic():
    text = "---\nid: thesis-001\nversion: 1\nstatus: draft\nreferences: []\n---\nbody"
    art = Artifact.from_text(text)
    assert art.id == "thesis-001"
    assert art.version == 1
    assert art.status == "draft"
    assert art.references == []
    assert art.body == "body"


def test_artifact_from_text_with_references():
    text = "---\nid: x\nversion: 1\nstatus: reviewed\nreferences: [thesis-001, char-001]\n---\nb"
    art = Artifact.from_text(text)
    assert art.references == ["thesis-001", "char-001"]


def test_artifact_missing_id_raises():
    text = "---\nversion: 1\nstatus: draft\nreferences: []\n---\nbody"
    with pytest.raises(ArtifactError, match="missing required field 'id'"):
        Artifact.from_text(text)


def test_artifact_invalid_status_raises():
    text = "---\nid: x\nversion: 1\nstatus: weird\nreferences: []\n---\nbody"
    with pytest.raises(ArtifactError, match="invalid status 'weird'"):
        Artifact.from_text(text)


def test_artifact_from_file(fixtures_dir):
    art = Artifact.from_file(fixtures_dir / "mini_bible" / "thesis.md")
    assert art.id == "thesis-001"
    assert art.path == fixtures_dir / "mini_bible" / "thesis.md"
