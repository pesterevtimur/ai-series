# tools/golden_freshness.py
"""Golden corpus state validator per spec § 5 v0.2 (D-002 P-12, P-13, P-14)."""
from __future__ import annotations
from collections import defaultdict
from pathlib import Path
import argparse
import sys
from tools._common.frontmatter import parse_frontmatter, FrontmatterError
from tools._common.reporter import Reporter, Issue, IssueLevel


VALID_CATEGORIES = {"scenes", "dialogues", "characters", "conflicts", "adversarial-passes", "theses"}
SHOW_SHARE_CATS = {"scenes", "characters", "conflicts"}
AUTHOR_SHARE_THRESHOLD = 0.50
SHOW_SHARE_THRESHOLD = 0.60
BATCH_AUTHOR_CONCENTRATION = 3


def check_golden(
    root: Path,
    min_positive_per_category: int = 3,
    min_anti_total: int = 5,
) -> Reporter:
    rep = Reporter(script="golden_freshness")

    if not root.exists():
        rep.add_issue(Issue(IssueLevel.ERROR, str(root), f"root path does not exist: {root}"))
        return rep
    if not root.is_dir():
        rep.add_issue(Issue(IssueLevel.ERROR, str(root), f"root path is not a directory: {root}"))
        return rep

    by_category_positive_weighted: dict[str, float] = defaultdict(float)
    anti_total = 0
    files_by_author_by_category: dict[str, dict[str, int]] = defaultdict(lambda: defaultdict(int))
    files_by_show_by_category: dict[str, dict[str, int]] = defaultdict(lambda: defaultdict(int))
    files_by_batch_by_author: dict[str, dict[str, int]] = defaultdict(lambda: defaultdict(int))

    for md in root.rglob("*.md"):
        if md.name in ("README.md", "CHANGELOG.md") or md.name.startswith("_"):
            continue
        try:
            text = md.read_text(encoding="utf-8")
        except OSError as e:
            rep.add_issue(Issue(IssueLevel.ERROR, str(md), f"cannot read file: {e}"))
            continue
        except UnicodeDecodeError as e:
            rep.add_issue(Issue(IssueLevel.ERROR, str(md), f"not valid UTF-8: {e.reason}"))
            continue
        try:
            fm, _ = parse_frontmatter(text)
        except FrontmatterError as e:
            rep.add_issue(Issue(IssueLevel.ERROR, str(md), f"frontmatter parse: {e}"))
            continue

        primary = fm.get("primary_category")
        secondary = fm.get("secondary_categories", []) or []
        example_type = fm.get("example_type")

        if primary not in VALID_CATEGORIES:
            rep.add_issue(Issue(IssueLevel.ERROR, str(md), f"invalid primary_category '{primary}'"))
            continue

        if example_type == "positive":
            by_category_positive_weighted[primary] += 1.0
            if isinstance(secondary, list):
                for sec in secondary:
                    if sec in VALID_CATEGORIES and sec != primary:
                        by_category_positive_weighted[sec] += 0.5
            author = fm.get("source_author", "<unknown>")
            show = fm.get("source_show", "<unknown>")
            batch = fm.get("batch", "<unknown>")
            files_by_author_by_category[primary][author] += 1
            if primary in SHOW_SHARE_CATS:
                files_by_show_by_category[primary][show] += 1
            files_by_batch_by_author[batch][author] += 1
        elif example_type == "anti-example":
            anti_total += 1
        else:
            rep.add_issue(Issue(
                IssueLevel.ERROR, str(md),
                f"invalid example_type '{example_type}'; must be positive | anti-example",
            ))

    # Coverage check (P-12)
    for cat in VALID_CATEGORIES:
        if by_category_positive_weighted[cat] < min_positive_per_category:
            rep.add_issue(Issue(
                IssueLevel.ERROR, str(root),
                f"category '{cat}': positive coverage {by_category_positive_weighted[cat]:.1f} < {min_positive_per_category}",
            ))

    if anti_total < min_anti_total:
        rep.add_issue(Issue(
            IssueLevel.ERROR, str(root),
            f"anti-example total {anti_total} < {min_anti_total}",
        ))

    # Diversity warnings (P-14) — non-blocking
    for cat, authors in files_by_author_by_category.items():
        total = sum(authors.values())
        if total > 0:
            for author, count in authors.items():
                share = count / total
                if share > AUTHOR_SHARE_THRESHOLD:
                    rep.add_diversity_warning(Issue(
                        IssueLevel.WARNING, str(root),
                        f"author '{author}' dominates category '{cat}': {share:.0%} share",
                    ))
    for cat, shows in files_by_show_by_category.items():
        total = sum(shows.values())
        if total > 0:
            for show, count in shows.items():
                share = count / total
                if share > SHOW_SHARE_THRESHOLD:
                    rep.add_diversity_warning(Issue(
                        IssueLevel.WARNING, str(root),
                        f"show '{show}' dominates category '{cat}': {share:.0%} share",
                    ))
    for batch, authors in files_by_batch_by_author.items():
        for author, count in authors.items():
            if count >= BATCH_AUTHOR_CONCENTRATION:
                rep.add_diversity_warning(Issue(
                    IssueLevel.WARNING, str(root),
                    f"author '{author}' concentrated in batch '{batch}': {count} files",
                ))

    return rep


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", default="golden", type=Path)
    parser.add_argument("--min-positive", default=3, type=int)
    parser.add_argument("--min-anti", default=5, type=int)
    args = parser.parse_args()
    rep = check_golden(args.root, min_positive_per_category=args.min_positive, min_anti_total=args.min_anti)
    print(rep.to_json())
    return rep.exit_code()


if __name__ == "__main__":
    sys.exit(main())
