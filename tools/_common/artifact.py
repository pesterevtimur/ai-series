# tools/_common/artifact.py
"""Artifact model — shared dataclass for all artifacts with frontmatter."""
from dataclasses import dataclass, field
from pathlib import Path
from .frontmatter import parse_frontmatter, FrontmatterError


VALID_STATUSES = frozenset({"draft", "reviewed", "approved"})
REQUIRED_FIELDS = ("id", "version", "status", "references")


class ArtifactError(ValueError):
    pass


@dataclass
class Artifact:
    id: str
    version: int
    status: str
    references: list[str]
    body: str
    raw_frontmatter: dict = field(repr=False)
    path: Path | None = None

    @classmethod
    def from_text(cls, text: str, path: Path | None = None) -> "Artifact":
        try:
            fm, body = parse_frontmatter(text)
        except FrontmatterError as e:
            raise ArtifactError(f"frontmatter error: {e}") from e

        for required in REQUIRED_FIELDS:
            if required not in fm:
                raise ArtifactError(f"missing required field '{required}' in frontmatter")

        status = fm["status"]
        if status not in VALID_STATUSES:
            raise ArtifactError(
                f"invalid status '{status}'; must be one of {sorted(VALID_STATUSES)}"
            )

        return cls(
            id=fm["id"],
            version=fm["version"],
            status=status,
            references=list(fm["references"]),
            body=body,
            raw_frontmatter=fm,
            path=path,
        )

    @classmethod
    def from_file(cls, path: Path) -> "Artifact":
        text = Path(path).read_text(encoding="utf-8")
        return cls.from_text(text, path=Path(path))
