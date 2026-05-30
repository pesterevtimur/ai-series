# tools/concern_resolution_validator.py
"""R-2 enforcement (D-002 P-9): require diff or D-NNN entry for each concern/veto."""
from __future__ import annotations
from pathlib import Path
import argparse
import subprocess
import sys
import yaml
from tools._common.reporter import Reporter, Issue, IssueLevel


def _load_critic_reports(tmp_critic_reports_dir: Path, artifact_id: str) -> list[dict]:
    artifact_dir = tmp_critic_reports_dir / artifact_id
    if not artifact_dir.is_dir():
        return []
    reports = []
    for yaml_file in sorted(artifact_dir.glob("*.yaml")):
        try:
            data = yaml.safe_load(yaml_file.read_text(encoding="utf-8"))
            if isinstance(data, dict):
                data["_source_file"] = str(yaml_file)
                reports.append(data)
        except (yaml.YAMLError, OSError, UnicodeDecodeError):
            continue
    return reports


def _is_concern_or_veto(report: dict) -> bool:
    verdict = str(report.get("verdict", ""))
    return "concern" in verdict or "veto" in verdict


def _concern_addressed(concern_issue: str, diff_text: str, decisions_dir: Path) -> bool:
    if concern_issue.lower() in diff_text.lower():
        return True
    if not decisions_dir.is_dir():
        return False
    for d in decisions_dir.glob("D-*.md"):
        try:
            if concern_issue.lower() in d.read_text(encoding="utf-8").lower():
                return True
        except (OSError, UnicodeDecodeError):
            continue
    return False


def check_resolution(
    tmp_critic_reports_dir: Path,
    artifact_id: str,
    artifact_diff_text: str,
    decisions_dir: Path,
) -> Reporter:
    rep = Reporter(script="concern_resolution_validator")
    reports = _load_critic_reports(tmp_critic_reports_dir, artifact_id)
    for report in reports:
        if not _is_concern_or_veto(report):
            continue
        flags = report.get("flags", []) or []
        for flag in flags:
            if not isinstance(flag, dict):
                continue
            issue = str(flag.get("issue", "")).strip()
            if not issue:
                continue
            if not _concern_addressed(issue, artifact_diff_text, decisions_dir):
                rep.add_issue(Issue(
                    IssueLevel.ERROR,
                    report.get("_source_file", "<unknown>"),
                    f"unresolved concern: '{issue}' — neither addressed in diff nor in decisions/D-NNN",
                ))
    return rep


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--tmp-dir", default="tmp/critic-reports", type=Path)
    parser.add_argument("--artifact-id", required=True)
    parser.add_argument("--decisions-dir", default="decisions", type=Path)
    args = parser.parse_args()
    try:
        diff = subprocess.run(["git", "diff", "--cached"], capture_output=True, text=True, check=False).stdout
    except (OSError, subprocess.SubprocessError):
        diff = ""
    rep = check_resolution(args.tmp_dir, args.artifact_id, diff, args.decisions_dir)
    print(rep.to_json())
    return rep.exit_code()


if __name__ == "__main__":
    sys.exit(main())
