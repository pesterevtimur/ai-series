# tools/consistency_check.py
"""Check that all frontmatter references resolve to existing artifact ids."""
from __future__ import annotations
from pathlib import Path
import argparse
import sys
from tools._common.artifact import Artifact, ArtifactError
from tools._common.reporter import Reporter, Issue, IssueLevel


def check_consistency(root: Path) -> Reporter:
    rep = Reporter(script="consistency_check")

    if not root.exists():
        rep.add_issue(Issue(
            IssueLevel.ERROR, str(root), f"root path does not exist: {root}",
        ))
        return rep
    if not root.is_dir():
        rep.add_issue(Issue(
            IssueLevel.ERROR, str(root), f"root path is not a directory: {root}",
        ))
        return rep

    artifacts: dict[str, Artifact] = {}

    for md in root.rglob("*.md"):
        if md.name in ("README.md", "CHANGELOG.md") or md.name.startswith("_"):
            continue
        try:
            art = Artifact.from_file(md)
        except ArtifactError as e:
            rep.add_issue(Issue(IssueLevel.ERROR, str(md), str(e)))
            continue
        except UnicodeDecodeError as e:
            rep.add_issue(Issue(
                IssueLevel.ERROR, str(md),
                f"file is not valid UTF-8: {e.reason}",
            ))
            continue
        artifacts[art.id] = art

    known_ids = set(artifacts.keys())
    for art in artifacts.values():
        for ref in art.references:
            if ref not in known_ids:
                rep.add_issue(Issue(
                    IssueLevel.ERROR,
                    str(art.path),
                    f"dangling reference '{ref}' (not found in corpus)",
                ))
    return rep


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", default=".", type=Path)
    args = parser.parse_args()
    rep = check_consistency(args.root)
    print(rep.to_json())
    return rep.exit_code()


if __name__ == "__main__":
    sys.exit(main())
