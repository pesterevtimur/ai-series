# tests/test_common_frontmatter.py
"""Tests for tools/_common/frontmatter.py."""
import pytest
from tools._common.frontmatter import parse_frontmatter, FrontmatterError


def test_parse_basic_frontmatter():
    text = "---\nid: foo\nversion: 1\n---\nbody text"
    fm, body = parse_frontmatter(text)
    assert fm == {"id": "foo", "version": 1}
    assert body == "body text"


def test_parse_empty_body():
    text = "---\nid: foo\n---\n"
    fm, body = parse_frontmatter(text)
    assert fm == {"id": "foo"}
    assert body == ""


def test_parse_no_frontmatter_raises():
    with pytest.raises(FrontmatterError, match="missing frontmatter"):
        parse_frontmatter("just body, no fm")


def test_parse_malformed_yaml_raises():
    text = "---\nid: foo\n  bad indent: x\n---\nbody"
    with pytest.raises(FrontmatterError, match="malformed YAML"):
        parse_frontmatter(text)


def test_parse_unclosed_frontmatter_raises():
    text = "---\nid: foo\nbody without close"
    with pytest.raises(FrontmatterError, match="unclosed frontmatter"):
        parse_frontmatter(text)


def test_parse_nested_lists():
    text = "---\nrefs:\n  - a\n  - b\n---\nbody"
    fm, body = parse_frontmatter(text)
    assert fm == {"refs": ["a", "b"]}


def test_parse_boolean_values():
    text = "---\nreconstruction: true\n---\nbody"
    fm, body = parse_frontmatter(text)
    assert fm["reconstruction"] is True


def test_parse_bom_prefix():
    text = "﻿---\nid: foo\n---\nbody"
    fm, body = parse_frontmatter(text)
    assert fm == {"id": "foo"}
    assert body == "body"
