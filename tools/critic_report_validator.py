# tools/critic_report_validator.py
"""Validate critic YAML reports per spec § 4.3 v0.2 (D-002 P-3, P-4, P-7, P-8, P-9)."""
from __future__ import annotations
from pathlib import Path
import argparse
import sys
import yaml
from tools._common.reporter import Reporter, Issue, IssueLevel


VALID_VERDICTS = {"pass", "concern", "veto"}
VALID_GOLDEN_UNAVAILABLE = {"category-empty", "category-bootstrap", "category-irrelevant"}
VALID_MODELS = {"opus", "sonnet", "haiku"}
MIN_CHECKED = 3
MIN_EVIDENCE = 2
MIN_REASONING_WORDS = 100


def validate_report(path: Path, smoke_test_mode: bool = False) -> Reporter:
    rep = Reporter(script="critic_report_validator")
    try:
        text = Path(path).read_text(encoding="utf-8")
    except OSError as e:
        rep.add_issue(Issue(IssueLevel.ERROR, str(path), f"cannot read file: {e}"))
        return rep
    try:
        data = yaml.safe_load(text)
    except yaml.YAMLError as e:
        rep.add_issue(Issue(IssueLevel.ERROR, str(path), f"malformed YAML: {e}"))
        return rep
    if not isinstance(data, dict):
        rep.add_issue(Issue(IssueLevel.ERROR, str(path), "report must be a dict"))
        return rep

    _check_verdict(data, path, rep)
    _check_model_used(data, path, rep)
    _check_min_list(data, "checked", MIN_CHECKED, path, rep)
    _check_min_list(data, "evidence_from_artifact", MIN_EVIDENCE, path, rep)
    _check_golden_calibration(data, smoke_test_mode, path, rep)
    _check_reasoning(data, path, rep)
    _check_counter_test_if_pass(data, path, rep)
    _check_not_applicable(data, path, rep)
    return rep


def _check_verdict(data: dict, path: Path, rep: Reporter) -> None:
    verdict = data.get("verdict", "")
    base = verdict.replace("+not_applicable", "").strip()
    if base not in VALID_VERDICTS and "not_applicable" not in verdict:
        rep.add_issue(Issue(
            IssueLevel.ERROR, str(path),
            f"invalid verdict '{verdict}'; must include one of {sorted(VALID_VERDICTS)} or 'not_applicable'",
        ))


def _check_model_used(data: dict, path: Path, rep: Reporter) -> None:
    model = data.get("model_used")
    if model is None or model == "":
        rep.add_issue(Issue(IssueLevel.ERROR, str(path), "missing required field 'model_used' (P-8)"))
        return
    if not isinstance(model, str):
        rep.add_issue(Issue(
            IssueLevel.ERROR, str(path),
            f"model_used must be a string, got {type(model).__name__}",
        ))
        return
    if model not in VALID_MODELS:
        rep.add_issue(Issue(
            IssueLevel.ERROR, str(path),
            f"invalid model_used '{model}'; must be one of {sorted(VALID_MODELS)}",
        ))


def _check_min_list(data: dict, key: str, min_len: int, path: Path, rep: Reporter) -> None:
    val = data.get(key, [])
    if not isinstance(val, list) or len(val) < min_len:
        rep.add_issue(Issue(
            IssueLevel.ERROR, str(path),
            f"field '{key}' must be a list with ≥ {min_len} entries, got {len(val) if isinstance(val, list) else type(val).__name__}",
        ))


def _check_golden_calibration(data: dict, smoke_test_mode: bool, path: Path, rep: Reporter) -> None:
    used = data.get("golden_calibration_used", [])
    unavailable = data.get("golden_unavailable_reason", "")
    if not isinstance(used, list):
        rep.add_issue(Issue(IssueLevel.ERROR, str(path), "golden_calibration_used must be a list"))
        return
    if len(used) == 0:
        if not unavailable:
            rep.add_issue(Issue(
                IssueLevel.ERROR, str(path),
                "golden_calibration_used is empty but golden_unavailable_reason missing (P-4)",
            ))
            return
        if unavailable not in VALID_GOLDEN_UNAVAILABLE:
            rep.add_issue(Issue(
                IssueLevel.ERROR, str(path),
                f"invalid golden_unavailable_reason '{unavailable}'; must be one of {sorted(VALID_GOLDEN_UNAVAILABLE)}",
            ))
            return
        if unavailable == "category-bootstrap" and not smoke_test_mode:
            rep.add_issue(Issue(
                IssueLevel.ERROR, str(path),
                "golden_unavailable_reason: category-bootstrap is only valid in smoke-test mode (P-4)",
            ))


def _check_reasoning(data: dict, path: Path, rep: Reporter) -> None:
    reasoning = data.get("reasoning", "")
    words = len(str(reasoning).split())
    if words < MIN_REASONING_WORDS:
        rep.add_issue(Issue(
            IssueLevel.ERROR, str(path),
            f"reasoning must be ≥ {MIN_REASONING_WORDS} words, got {words}",
        ))


def _check_counter_test_if_pass(data: dict, path: Path, rep: Reporter) -> None:
    verdict = str(data.get("verdict", ""))
    if "pass" not in verdict:
        return
    ct = data.get("counter_test_attempted", {})
    if not isinstance(ct, dict):
        rep.add_issue(Issue(
            IssueLevel.ERROR, str(path),
            "counter_test_attempted must be a dict with what_searched / why_this / why_not_found (P-7)",
        ))
        return
    for elem in ("what_searched", "why_this", "why_not_found"):
        val = ct.get(elem, "")
        if not str(val).strip():
            rep.add_issue(Issue(
                IssueLevel.ERROR, str(path),
                f"counter_test_attempted.{elem} is empty; P-7 requires all 3 elements for verdict=pass",
            ))


def _check_not_applicable(data: dict, path: Path, rep: Reporter) -> None:
    verdict = str(data.get("verdict", ""))
    if "not_applicable" in verdict:
        reason = data.get("not_applicable_reason", "")
        if not str(reason).strip():
            rep.add_issue(Issue(
                IssueLevel.ERROR, str(path),
                "verdict contains 'not_applicable' but not_applicable_reason is empty (P-3)",
            ))


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("report", type=Path)
    parser.add_argument("--smoke-test", action="store_true", help="allow golden_unavailable_reason=category-bootstrap")
    args = parser.parse_args()
    rep = validate_report(args.report, smoke_test_mode=args.smoke_test)
    print(rep.to_json())
    return rep.exit_code()


if __name__ == "__main__":
    sys.exit(main())
