# tools/voice_dissimilarity.py
"""Compute TF-IDF cosine similarity between speakers; flag if > threshold (voice bleed)."""
from __future__ import annotations
from collections import defaultdict
from pathlib import Path
import argparse
import re
import sys
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from tools._common.reporter import Reporter, Issue, IssueLevel


_SPEAKER_RE = re.compile(r"^\*\*([А-ЯA-Z][А-ЯA-Z\s]*?):\*\*\s*(.+)$", re.MULTILINE)


def _extract_lines_per_speaker(text: str) -> dict[str, str]:
    by_speaker: dict[str, list[str]] = defaultdict(list)
    for m in _SPEAKER_RE.finditer(text):
        name, line = m.group(1).strip(), m.group(2).strip()
        by_speaker[name].append(line)
    return {name: " ".join(lines) for name, lines in by_speaker.items()}


def check_scene(path: Path, threshold: float = 0.65) -> Reporter:
    rep = Reporter(script="voice_dissimilarity")
    try:
        text = Path(path).read_text(encoding="utf-8")
    except OSError as e:
        rep.add_issue(Issue(IssueLevel.ERROR, str(path), f"cannot read file: {e}"))
        return rep
    speakers = _extract_lines_per_speaker(text)
    if len(speakers) < 2:
        rep.add_issue(Issue(IssueLevel.WARNING, str(path), "fewer than 2 speakers; skip"))
        return rep
    names = list(speakers.keys())
    texts = [speakers[n] for n in names]
    vec = TfidfVectorizer().fit_transform(texts)
    sim = cosine_similarity(vec)
    for i in range(len(names)):
        for j in range(i + 1, len(names)):
            s = sim[i, j]
            if s >= threshold:
                rep.add_issue(Issue(
                    IssueLevel.ERROR,
                    str(path),
                    f"voice bleed: {names[i]} vs {names[j]} cosine={s:.3f} >= {threshold}",
                    context={"speaker_a": names[i], "speaker_b": names[j], "similarity": float(s)},
                ))
    return rep


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("scene", type=Path)
    parser.add_argument("--threshold", default=0.65, type=float)
    args = parser.parse_args()
    rep = check_scene(args.scene, threshold=args.threshold)
    print(rep.to_json())
    return rep.exit_code()


if __name__ == "__main__":
    sys.exit(main())
