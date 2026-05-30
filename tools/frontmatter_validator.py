# tools/frontmatter_validator.py
"""Validate required fields, unique id, valid status across artifacts."""
from __future__ import annotations
from collections import defaultdict
from pathlib import Path
import argparse
import sys
from tools._common.artifact import Artifact, ArtifactError
from tools._common.reporter import Reporter, Issue, IssueLevel


def validate_directory(root: Path) -> Reporter:
    rep = Reporter(script="frontmatter_validator")
    seen_ids: dict[str, list[str]] = defaultdict(list)

    for md in root.rglob("*.md"):
        try:
            art = Artifact.from_file(md)
        except ArtifactError as e:
            rep.add_issue(Issue(IssueLevel.ERROR, str(md), str(e)))
            continue
        seen_ids[art.id].append(str(md))

    for art_id, paths in seen_ids.items():
        if len(paths) > 1:
            for p in paths:
                rep.add_issue(Issue(
                    IssueLevel.ERROR,
                    p,
                    f"duplicate id '{art_id}' (also seen at {len(paths)-1} other path(s))",
                ))
    return rep


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", default=".", type=Path)
    args = parser.parse_args()
    rep = validate_directory(args.root)
    print(rep.to_json())
    return rep.exit_code()


if __name__ == "__main__":
    sys.exit(main())
