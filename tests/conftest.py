# tests/conftest.py
"""Pytest configuration and shared fixtures."""
from pathlib import Path
import pytest

FIXTURES_DIR = Path(__file__).parent / "fixtures"


@pytest.fixture
def fixtures_dir() -> Path:
    """Return path to tests/fixtures/ directory."""
    return FIXTURES_DIR
