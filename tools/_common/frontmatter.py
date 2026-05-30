# tools/_common/frontmatter.py
"""Parse YAML frontmatter from Markdown files."""
import re
import yaml


class FrontmatterError(ValueError):
    pass


_FM_PATTERN = re.compile(
    r"^---\n(.*?)\n---\n(.*)$",
    re.DOTALL,
)


def parse_frontmatter(text: str) -> tuple[dict, str]:
    if not text.startswith("---\n"):
        raise FrontmatterError("missing frontmatter (no opening '---')")
    match = _FM_PATTERN.match(text)
    if not match:
        raise FrontmatterError("unclosed frontmatter (no closing '---')")
    yaml_text, body = match.groups()
    try:
        fm = yaml.safe_load(yaml_text) or {}
    except yaml.YAMLError as e:
        raise FrontmatterError(f"malformed YAML: {e}") from e
    if not isinstance(fm, dict):
        raise FrontmatterError(f"frontmatter must be a dict, got {type(fm).__name__}")
    return fm, body.rstrip("\n")
