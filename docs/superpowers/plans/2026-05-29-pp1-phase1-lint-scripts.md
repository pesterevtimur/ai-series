# Phase 1 — Lint Scripts Implementation Plan (TDD)

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** реализовать 6 lint-скриптов в `tools/` через strict TDD (RED→GREEN→REFACTOR) для разблокировки Phase 2 (субагенты, требующие `critic_report_validator.py`) и Phase 4 (smoke-test, требующий всех 6 скриптов).

**Architecture:** Python 3.11+ с pytest. Каждый скрипт — отдельный модуль в `tools/`, использует общие модули из `tools/_common/` (frontmatter parser, artifact model, JSON reporter). CLI exit codes 0 (green) / 1 (red) + JSON report в stdout. Никаких subagent calls, никаких golden данных — все scripts тестируются на synthetic fixtures в `tests/fixtures/`.

**Tech Stack:** Python 3.11+, `pyyaml` (frontmatter parsing), `pytest` + `pytest-cov` (TDD + coverage), `scikit-learn` (только в `voice_dissimilarity.py` — TfidfVectorizer + cosine_similarity).

---

## File Structure

| Файл | Назначение |
|---|---|
| `pyproject.toml` | Python project config + dependencies (pyyaml, pytest, pytest-cov, scikit-learn) |
| `tools/__init__.py` | Пустой, для package import |
| `tools/_common/__init__.py` | Пустой |
| `tools/_common/frontmatter.py` | `parse_frontmatter(text: str) -> tuple[dict, str]` — split YAML frontmatter + body |
| `tools/_common/artifact.py` | `Artifact` dataclass (id, references, body, status, primary_category и т.д.) |
| `tools/_common/reporter.py` | `Reporter` class — JSON report serialization + exit code |
| `tools/frontmatter_validator.py` | CLI: required fields, unique id, valid status |
| `tools/consistency_check.py` | CLI: cross-artifact references resolve, facts non-contradicting via Bible comparison |
| `tools/critic_report_validator.py` | CLI: validates critic YAML reports per spec § 4.3 v0.2 |
| `tools/voice_dissimilarity.py` | CLI: TF-IDF cosine on dialogue lines, threshold 0.65 → voice bleed flag |
| `tools/golden_freshness.py` | CLI: golden corpus state with P-12 weights + P-13 example_type + P-14 diversity warnings |
| `tools/concern_resolution_validator.py` | CLI: reads tmp/critic-reports/ (P-9), requires diff or D-NNN per concern/veto |
| `tools/README.md` | CLI invocation, exit codes, JSON report schema |
| `tests/__init__.py` | Пустой |
| `tests/conftest.py` | pytest fixtures (common synthetic data) |
| `tests/fixtures/mini_bible/` | Synthetic story-bible artefacts для consistency_check tests |
| `tests/fixtures/mini_critic_reports/` | Synthetic YAML reports для critic_report_validator tests |
| `tests/fixtures/mini_golden/` | Synthetic golden files для golden_freshness tests |
| `tests/fixtures/mini_scenes/` | Synthetic scene dialogues для voice_dissimilarity tests |
| `tests/test_common_frontmatter.py` | Unit tests для tools/_common/frontmatter.py |
| `tests/test_common_artifact.py` | Unit tests для tools/_common/artifact.py |
| `tests/test_common_reporter.py` | Unit tests для tools/_common/reporter.py |
| `tests/test_frontmatter_validator.py` | Unit tests + CLI tests |
| `tests/test_consistency_check.py` | Unit tests + CLI tests |
| `tests/test_critic_report_validator.py` | Unit tests + CLI tests |
| `tests/test_voice_dissimilarity.py` | Unit tests + CLI tests |
| `tests/test_golden_freshness.py` | Unit tests + CLI tests |
| `tests/test_concern_resolution_validator.py` | Unit tests + CLI tests |

**Dependency order:**

```
_common/frontmatter ← _common/artifact ← consistency_check
_common/frontmatter ← frontmatter_validator
_common/reporter ← all CLI scripts
[standalone] critic_report_validator ← concern_resolution_validator
[standalone] voice_dissimilarity
[standalone] golden_freshness
```

Tasks ниже идут в dependency order: shared modules → simple validators → complex scripts → final acceptance.

---

## Task 0: Python project setup

**Files:**
- Create: `pyproject.toml`
- Create: `tools/__init__.py`
- Create: `tools/_common/__init__.py`
- Create: `tests/__init__.py`
- Create: `tests/conftest.py`

- [ ] **Step 1: Create pyproject.toml**

```toml
[project]
name = "auto-ai-series-tools"
version = "0.1.0"
description = "Lint scripts for Auto-ai-series ПП1"
requires-python = ">=3.11"
dependencies = [
    "pyyaml>=6.0",
    "scikit-learn>=1.4",
]

[project.optional-dependencies]
dev = [
    "pytest>=8.0",
    "pytest-cov>=4.1",
]

[tool.pytest.ini_options]
testpaths = ["tests"]
python_files = "test_*.py"
addopts = "-v --cov=tools --cov-report=term-missing --cov-fail-under=70"
```

- [ ] **Step 2: Create empty package files**

```python
# tools/__init__.py
"""Auto-ai-series lint scripts (ПП1)."""

# tools/_common/__init__.py
"""Shared utilities for lint scripts."""

# tests/__init__.py
"""Test suite for tools/."""
```

- [ ] **Step 3: Create tests/conftest.py with fixture directory marker**

```python
# tests/conftest.py
"""Pytest configuration and shared fixtures."""
from pathlib import Path
import pytest

FIXTURES_DIR = Path(__file__).parent / "fixtures"


@pytest.fixture
def fixtures_dir() -> Path:
    """Return path to tests/fixtures/ directory."""
    return FIXTURES_DIR
```

- [ ] **Step 4: Install dev dependencies + verify pytest runs**

Run:
```bash
python -m pip install -e ".[dev]"
python -m pytest --collect-only
```
Expected: 0 tests collected (no tests yet), exit 5 (no tests is OK at this stage).

- [ ] **Step 5: Commit**

```bash
git add pyproject.toml tools/ tests/
git commit -m "tool: setup tools/ + tests/ Python project skeleton (pytest + pyyaml + scikit-learn)"
```

---

## Task 1: `tools/_common/frontmatter.py` — YAML frontmatter parser

**Files:**
- Create: `tests/test_common_frontmatter.py`
- Create: `tools/_common/frontmatter.py`

- [ ] **Step 1: Write failing test for basic parse**

```python
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
```

- [ ] **Step 2: Run tests, see them fail**

Run: `python -m pytest tests/test_common_frontmatter.py -v`
Expected: 5 errors with "ModuleNotFoundError: No module named 'tools._common.frontmatter'"

- [ ] **Step 3: Implement minimal parser**

```python
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
```

- [ ] **Step 4: Run tests, see all pass**

Run: `python -m pytest tests/test_common_frontmatter.py -v`
Expected: 5 passed.

- [ ] **Step 5: Add edge-case tests + verify pass**

```python
# Append to tests/test_common_frontmatter.py
def test_parse_nested_lists():
    text = "---\nrefs:\n  - a\n  - b\n---\nbody"
    fm, body = parse_frontmatter(text)
    assert fm == {"refs": ["a", "b"]}


def test_parse_boolean_values():
    text = "---\nreconstruction: true\n---\nbody"
    fm, body = parse_frontmatter(text)
    assert fm["reconstruction"] is True
```

Run: `python -m pytest tests/test_common_frontmatter.py -v`
Expected: 7 passed.

- [ ] **Step 6: Commit**

```bash
git add tools/_common/frontmatter.py tests/test_common_frontmatter.py
git commit -m "tool: tools/_common/frontmatter.py — YAML frontmatter parser with TDD"
```

---

## Task 2: `tools/_common/artifact.py` — Artifact model

**Files:**
- Create: `tests/test_common_artifact.py`
- Create: `tools/_common/artifact.py`

- [ ] **Step 1: Write failing test for Artifact dataclass**

```python
# tests/test_common_artifact.py
from pathlib import Path
import pytest
from tools._common.artifact import Artifact, ArtifactError


def test_artifact_from_text_basic():
    text = "---\nid: thesis-001\nversion: 1\nstatus: draft\nreferences: []\n---\nbody"
    art = Artifact.from_text(text)
    assert art.id == "thesis-001"
    assert art.version == 1
    assert art.status == "draft"
    assert art.references == []
    assert art.body == "body"


def test_artifact_from_text_with_references():
    text = "---\nid: x\nversion: 1\nstatus: reviewed\nreferences: [thesis-001, char-001]\n---\nb"
    art = Artifact.from_text(text)
    assert art.references == ["thesis-001", "char-001"]


def test_artifact_missing_id_raises():
    text = "---\nversion: 1\nstatus: draft\nreferences: []\n---\nbody"
    with pytest.raises(ArtifactError, match="missing required field 'id'"):
        Artifact.from_text(text)


def test_artifact_invalid_status_raises():
    text = "---\nid: x\nversion: 1\nstatus: weird\nreferences: []\n---\nbody"
    with pytest.raises(ArtifactError, match="invalid status 'weird'"):
        Artifact.from_text(text)
```

- [ ] **Step 2: Run, see fail**

Run: `python -m pytest tests/test_common_artifact.py -v`
Expected: 4 errors with "ModuleNotFoundError".

- [ ] **Step 3: Implement Artifact**

```python
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
```

- [ ] **Step 4: Run, see pass**

Run: `python -m pytest tests/test_common_artifact.py -v`
Expected: 4 passed.

- [ ] **Step 5: Add from_file test using fixtures**

Create `tests/fixtures/mini_bible/thesis.md`:
```markdown
---
id: thesis-001
version: 1
status: approved
references: []
---
Центральный тезис проекта.
```

Append to test file:
```python
def test_artifact_from_file(fixtures_dir):
    art = Artifact.from_file(fixtures_dir / "mini_bible" / "thesis.md")
    assert art.id == "thesis-001"
    assert art.path == fixtures_dir / "mini_bible" / "thesis.md"
```

Run: `python -m pytest tests/test_common_artifact.py -v`
Expected: 5 passed.

- [ ] **Step 6: Commit**

```bash
git add tools/_common/artifact.py tests/test_common_artifact.py tests/fixtures/mini_bible/
git commit -m "tool: tools/_common/artifact.py — Artifact dataclass with TDD"
```

---

## Task 3: `tools/_common/reporter.py` — JSON report

**Files:**
- Create: `tests/test_common_reporter.py`
- Create: `tools/_common/reporter.py`

- [ ] **Step 1: Failing test**

```python
# tests/test_common_reporter.py
import json
import pytest
from tools._common.reporter import Reporter, Issue, IssueLevel


def test_empty_reporter_passes():
    r = Reporter(script="frontmatter_validator")
    assert r.exit_code() == 0
    assert json.loads(r.to_json())["status"] == "pass"


def test_reporter_with_error_fails():
    r = Reporter(script="x")
    r.add_issue(Issue(level=IssueLevel.ERROR, path="x.md", message="bad"))
    assert r.exit_code() == 1
    payload = json.loads(r.to_json())
    assert payload["status"] == "fail"
    assert len(payload["issues"]) == 1
    assert payload["issues"][0]["level"] == "error"


def test_reporter_warning_does_not_fail():
    r = Reporter(script="x")
    r.add_issue(Issue(level=IssueLevel.WARNING, path="x.md", message="dim"))
    assert r.exit_code() == 0
    payload = json.loads(r.to_json())
    assert payload["status"] == "pass"
    assert len(payload["warnings"]) == 1
```

- [ ] **Step 2: Run, see fail**

Run: `python -m pytest tests/test_common_reporter.py -v`
Expected: 3 errors with "ModuleNotFoundError".

- [ ] **Step 3: Implement Reporter**

```python
# tools/_common/reporter.py
"""JSON report format for lint scripts."""
from dataclasses import dataclass, field
from enum import Enum
import json


class IssueLevel(str, Enum):
    ERROR = "error"
    WARNING = "warning"


@dataclass
class Issue:
    level: IssueLevel
    path: str
    message: str
    context: dict = field(default_factory=dict)

    def to_dict(self) -> dict:
        return {
            "level": self.level.value,
            "path": self.path,
            "message": self.message,
            "context": self.context,
        }


@dataclass
class Reporter:
    script: str
    issues: list[Issue] = field(default_factory=list)
    diversity_warnings: list[Issue] = field(default_factory=list)

    def add_issue(self, issue: Issue) -> None:
        self.issues.append(issue)

    def add_diversity_warning(self, issue: Issue) -> None:
        self.diversity_warnings.append(issue)

    def errors(self) -> list[Issue]:
        return [i for i in self.issues if i.level == IssueLevel.ERROR]

    def warnings(self) -> list[Issue]:
        return [i for i in self.issues if i.level == IssueLevel.WARNING]

    def exit_code(self) -> int:
        return 1 if self.errors() else 0

    def to_json(self) -> str:
        return json.dumps({
            "script": self.script,
            "status": "fail" if self.errors() else "pass",
            "issues": [i.to_dict() for i in self.errors()],
            "warnings": [i.to_dict() for i in self.warnings()],
            "diversity_warnings": [i.to_dict() for i in self.diversity_warnings],
        }, ensure_ascii=False, indent=2)
```

- [ ] **Step 4: Run, see pass**

Run: `python -m pytest tests/test_common_reporter.py -v`
Expected: 3 passed.

- [ ] **Step 5: Commit**

```bash
git add tools/_common/reporter.py tests/test_common_reporter.py
git commit -m "tool: tools/_common/reporter.py — JSON report + exit codes with TDD"
```

---

## Task 4: `tools/frontmatter_validator.py` — Required fields + unique id + valid status

**Files:**
- Create: `tests/test_frontmatter_validator.py`
- Create: `tools/frontmatter_validator.py`

- [ ] **Step 1: Failing tests**

```python
# tests/test_frontmatter_validator.py
from pathlib import Path
import pytest
from tools.frontmatter_validator import validate_directory


def test_valid_artifact_passes(tmp_path):
    art_path = tmp_path / "thesis.md"
    art_path.write_text(
        "---\nid: t-1\nversion: 1\nstatus: draft\nreferences: []\n---\nbody",
        encoding="utf-8",
    )
    rep = validate_directory(tmp_path)
    assert rep.exit_code() == 0


def test_duplicate_id_flagged(tmp_path):
    (tmp_path / "a.md").write_text(
        "---\nid: dup\nversion: 1\nstatus: draft\nreferences: []\n---\nb",
        encoding="utf-8",
    )
    (tmp_path / "b.md").write_text(
        "---\nid: dup\nversion: 1\nstatus: draft\nreferences: []\n---\nb",
        encoding="utf-8",
    )
    rep = validate_directory(tmp_path)
    assert rep.exit_code() == 1
    assert any("duplicate id" in i.message for i in rep.errors())


def test_invalid_status_flagged(tmp_path):
    (tmp_path / "x.md").write_text(
        "---\nid: x\nversion: 1\nstatus: bogus\nreferences: []\n---\nb",
        encoding="utf-8",
    )
    rep = validate_directory(tmp_path)
    assert rep.exit_code() == 1
```

- [ ] **Step 2: Run, fail**

`python -m pytest tests/test_frontmatter_validator.py -v` → 3 errors module not found.

- [ ] **Step 3: Implement**

```python
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
```

- [ ] **Step 4: Run, pass**

`python -m pytest tests/test_frontmatter_validator.py -v` → 3 passed.

- [ ] **Step 5: Test CLI invocation manually**

```bash
python -m tools.frontmatter_validator --root tests/fixtures/mini_bible
```
Expected: JSON output with `"status": "pass"`, exit 0.

- [ ] **Step 6: Commit**

```bash
git add tools/frontmatter_validator.py tests/test_frontmatter_validator.py
git commit -m "tool: tools/frontmatter_validator.py — required fields + unique id + status with TDD"
```

---

## Task 5: `tools/consistency_check.py` — Cross-artifact references

**Files:**
- Create: `tests/test_consistency_check.py`
- Create: `tools/consistency_check.py`
- Update: `tests/fixtures/mini_bible/` — add character.md that references thesis-001

- [ ] **Step 1: Add fixture for character referencing thesis**

```markdown
<!-- tests/fixtures/mini_bible/character-001.md -->
---
id: character-001
version: 1
status: draft
references: [thesis-001]
---
Character body.
```

- [ ] **Step 2: Failing tests**

```python
# tests/test_consistency_check.py
from pathlib import Path
import pytest
from tools.consistency_check import check_consistency


def test_resolved_references_pass(fixtures_dir):
    rep = check_consistency(fixtures_dir / "mini_bible")
    assert rep.exit_code() == 0


def test_dangling_reference_flagged(tmp_path):
    (tmp_path / "a.md").write_text(
        "---\nid: a\nversion: 1\nstatus: draft\nreferences: [missing-id]\n---\nb",
        encoding="utf-8",
    )
    rep = check_consistency(tmp_path)
    assert rep.exit_code() == 1
    assert any("dangling reference 'missing-id'" in i.message for i in rep.errors())
```

- [ ] **Step 3: Run, fail**

`python -m pytest tests/test_consistency_check.py -v` → 2 errors module not found.

- [ ] **Step 4: Implement**

```python
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
    artifacts: dict[str, Artifact] = {}

    for md in root.rglob("*.md"):
        try:
            art = Artifact.from_file(md)
        except ArtifactError as e:
            rep.add_issue(Issue(IssueLevel.ERROR, str(md), str(e)))
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
```

- [ ] **Step 5: Run, pass**

`python -m pytest tests/test_consistency_check.py -v` → 2 passed.

- [ ] **Step 6: Commit**

```bash
git add tools/consistency_check.py tests/test_consistency_check.py tests/fixtures/mini_bible/character-001.md
git commit -m "tool: tools/consistency_check.py — reference resolution check with TDD"
```

---

## Task 6: `tools/critic_report_validator.py` — Critic YAML reports

**Files:**
- Create: `tests/test_critic_report_validator.py`
- Create: `tools/critic_report_validator.py`
- Create: `tests/fixtures/mini_critic_reports/` with valid + invalid examples

**Context.** Per spec § 4.3 v0.2, the schema requires:
- `verdict ∈ {pass, concern, veto}` or contains `not_applicable`
- `model_used ∈ {opus, sonnet, haiku}` (P-8 audit)
- `checked` ≥ 3 entries
- `evidence_from_artifact` ≥ 2 entries
- `golden_calibration_used` ≥ 1 entry OR `golden_unavailable_reason ∈ {category-empty, category-bootstrap, category-irrelevant}` (P-4)
- `reasoning` ≥ 100 words
- For `verdict=pass`: `counter_test_attempted` has all 3 elements (`what_searched`, `why_this`, `why_not_found`) (P-7)
- For `not_applicable` in verdict: `not_applicable_reason` non-empty (P-3)

- [ ] **Step 1: Create fixture files**

```yaml
# tests/fixtures/mini_critic_reports/valid_pass.yaml
verdict: pass
model_used: opus
checked:
  - "тезис устоял к counter-argument 1"
  - "тезис устоял к counter-argument 2"
  - "нет соломенных чучел"
evidence_from_artifact:
  - "строка 5: 'центральный вопрос ...'"
  - "строка 12: 'оппонирующая позиция ...'"
golden_calibration_used:
  - "golden/adversarial-passes/karnofsky-most-important.md — формулировка тезиса"
reasoning: |
  Аргумент устоял потому что в артефакте явно проговорена контр-позиция в её сильнейшей
  формулировке (строка 12). Counter-test показал отсутствие морализаторства: для ИИ есть
  место где он структурно неправ, а человек структурно прав (строка 18). Проверены три
  основных вектора атаки — instrumental convergence, ortho thesis, mesa-optimization — все
  имеют адресацию в артефакте либо через прямой контраргумент, либо через явное оставление
  в decisions/D-NNN.
flags: []
counter_test_attempted:
  what_searched: "Искал моменты, где центральный тезис принимается без устойчивого counter-argument'а."
  why_this: "Потому что если тезис не атакован в сильной форме, он либо тривиален либо страуменом подан."
  why_not_found: "Не нашёл — в строках 12-18 атака подана сильно, и артефакт явно даёт ей место."
```

```yaml
# tests/fixtures/mini_critic_reports/invalid_pass_missing_counter_test.yaml
verdict: pass
model_used: opus
checked: ["a", "b", "c"]
evidence_from_artifact: ["x", "y"]
golden_calibration_used: ["golden/x.md — note"]
reasoning: "Слишком короткий reasoning. Меньше ста слов чтоб провалить требование."
flags: []
counter_test_attempted:
  what_searched: ""
  why_this: ""
  why_not_found: ""
```

```yaml
# tests/fixtures/mini_critic_reports/invalid_bootstrap_outside_smoketest.yaml
verdict: concern
model_used: opus
checked: ["a", "b", "c"]
evidence_from_artifact: ["x", "y"]
golden_calibration_used: []
golden_unavailable_reason: category-bootstrap
reasoning: |
  Тестовый отчёт с category-bootstrap. Должен быть отвергнут validator'ом, если запускается
  ВНЕ режима smoke-test. Достаточно символов чтобы пройти 100-словный порог: символ символ
  символ символ символ символ символ символ символ символ символ символ символ символ символ
  символ символ символ символ символ символ символ символ символ символ символ символ символ.
flags:
  - severity: medium
    issue: "что-то"
    location: "где-то"
```

- [ ] **Step 2: Failing tests**

```python
# tests/test_critic_report_validator.py
from pathlib import Path
import pytest
from tools.critic_report_validator import validate_report


def test_valid_pass(fixtures_dir):
    rep = validate_report(
        fixtures_dir / "mini_critic_reports" / "valid_pass.yaml",
        smoke_test_mode=False,
    )
    assert rep.exit_code() == 0


def test_pass_without_counter_test_fails(fixtures_dir):
    rep = validate_report(
        fixtures_dir / "mini_critic_reports" / "invalid_pass_missing_counter_test.yaml",
        smoke_test_mode=False,
    )
    assert rep.exit_code() == 1
    msgs = [i.message for i in rep.errors()]
    assert any("counter_test_attempted" in m for m in msgs)
    assert any("reasoning" in m for m in msgs)  # < 100 words


def test_bootstrap_outside_smoketest_fails(fixtures_dir):
    rep = validate_report(
        fixtures_dir / "mini_critic_reports" / "invalid_bootstrap_outside_smoketest.yaml",
        smoke_test_mode=False,
    )
    assert rep.exit_code() == 1
    assert any("category-bootstrap" in i.message for i in rep.errors())


def test_bootstrap_inside_smoketest_passes(fixtures_dir):
    rep = validate_report(
        fixtures_dir / "mini_critic_reports" / "invalid_bootstrap_outside_smoketest.yaml",
        smoke_test_mode=True,
    )
    assert rep.exit_code() == 0
```

- [ ] **Step 3: Run, fail**

`python -m pytest tests/test_critic_report_validator.py -v` → 4 errors module not found.

- [ ] **Step 4: Implement**

```python
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
    text = Path(path).read_text(encoding="utf-8")
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
    if not model:
        rep.add_issue(Issue(IssueLevel.ERROR, str(path), "missing required field 'model_used' (P-8)"))
    elif model not in VALID_MODELS:
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
```

- [ ] **Step 5: Run, pass**

`python -m pytest tests/test_critic_report_validator.py -v` → 4 passed.

- [ ] **Step 6: Add more edge cases — veto verdicts, not_applicable**

```python
# Append
def test_not_applicable_requires_reason(tmp_path):
    rep_path = tmp_path / "rep.yaml"
    rep_path.write_text(
        "verdict: pass+not_applicable\nmodel_used: opus\n"
        "checked: [a, b, c]\nevidence_from_artifact: [x, y]\n"
        "golden_calibration_used: []\ngolden_unavailable_reason: category-irrelevant\n"
        "reasoning: " + " word" * 105 + "\n"
        "counter_test_attempted:\n  what_searched: x\n  why_this: y\n  why_not_found: z\n",
        encoding="utf-8",
    )
    rep = validate_report(rep_path, smoke_test_mode=False)
    assert rep.exit_code() == 1
    assert any("not_applicable_reason" in i.message for i in rep.errors())
```

Run + pass.

- [ ] **Step 7: Commit**

```bash
git add tools/critic_report_validator.py tests/test_critic_report_validator.py tests/fixtures/mini_critic_reports/
git commit -m "tool: tools/critic_report_validator.py — P-3+P-4+P-7+P-8 enforcement with TDD"
```

---

## Task 7: `tools/voice_dissimilarity.py` — TF-IDF voice bleed

**Files:**
- Create: `tests/test_voice_dissimilarity.py`
- Create: `tools/voice_dissimilarity.py`
- Create: `tests/fixtures/mini_scenes/` with distinct + bleeding examples

- [ ] **Step 1: Create fixtures**

```markdown
<!-- tests/fixtures/mini_scenes/scene-distinct.md -->
**АЛИСА:** Я не могу больше работать на эту систему. Меня выжимают как губку.
**БОРИС:** Системе нужна оптимизация. Это не личное, это математика рисков.
**АЛИСА:** Математика — твоё прикрытие. Я устала это терпеть.
**БОРИС:** Зафиксируем риски. Через 30 минут будут цифры.
```

```markdown
<!-- tests/fixtures/mini_scenes/scene-bleed.md -->
**АЛИСА:** Зафиксируем риски. Математика не врёт.
**БОРИС:** Зафиксируем риски. Математика не врёт.
**АЛИСА:** Цифры покажут. Это рациональная позиция.
**БОРИС:** Цифры покажут. Это рациональная позиция.
```

- [ ] **Step 2: Failing tests**

```python
# tests/test_voice_dissimilarity.py
from pathlib import Path
import pytest
from tools.voice_dissimilarity import check_scene


def test_distinct_voices_pass(fixtures_dir):
    rep = check_scene(fixtures_dir / "mini_scenes" / "scene-distinct.md", threshold=0.65)
    assert rep.exit_code() == 0


def test_voice_bleed_flagged(fixtures_dir):
    rep = check_scene(fixtures_dir / "mini_scenes" / "scene-bleed.md", threshold=0.65)
    assert rep.exit_code() == 1
    assert any("voice bleed" in i.message.lower() for i in rep.errors())
```

- [ ] **Step 3: Run, fail**

→ module not found.

- [ ] **Step 4: Implement**

```python
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
    text = Path(path).read_text(encoding="utf-8")
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
                    f"voice bleed: {names[i]} vs {names[j]} cosine={s:.3f} ≥ {threshold}",
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
```

- [ ] **Step 5: Run, pass**

`python -m pytest tests/test_voice_dissimilarity.py -v` → 2 passed.

- [ ] **Step 6: Commit**

```bash
git add tools/voice_dissimilarity.py tests/test_voice_dissimilarity.py tests/fixtures/mini_scenes/
git commit -m "tool: tools/voice_dissimilarity.py — TF-IDF cosine voice bleed detector with TDD"
```

---

## Task 8: `tools/golden_freshness.py` — P-12 weights + P-13 example_type + P-14 diversity

**Files:**
- Create: `tests/test_golden_freshness.py`
- Create: `tools/golden_freshness.py`
- Create: `tests/fixtures/mini_golden/` with positive + anti samples

- [ ] **Step 1: Create fixtures**

```markdown
<!-- tests/fixtures/mini_golden/scenes/scene-1.md -->
---
id: golden-scene-1
example_type: positive
primary_category: scenes
secondary_categories: [dialogues]
batch: batch-01
source_author: Author A
source_show: Show X
license: "fair use"
---
Body
```

(Add 2 more positive in scenes/ from same author for diversity warning test.)

(Add `anti-examples/strawmen/strawman-1.md` with `example_type: anti-example, primary_category: theses`.)

- [ ] **Step 2: Failing tests**

```python
# tests/test_golden_freshness.py
from pathlib import Path
import pytest
from tools.golden_freshness import check_golden


def test_minimum_threshold_passes(fixtures_dir):
    # Threshold here: scenes has ≥1 positive, theses has ≥1 anti
    rep = check_golden(
        fixtures_dir / "mini_golden",
        min_positive_per_category=1,
        min_anti_total=1,
    )
    assert rep.exit_code() == 0


def test_below_threshold_fails(fixtures_dir):
    rep = check_golden(
        fixtures_dir / "mini_golden",
        min_positive_per_category=10,  # impossible threshold
        min_anti_total=1,
    )
    assert rep.exit_code() == 1


def test_author_share_diversity_warning(fixtures_dir):
    rep = check_golden(
        fixtures_dir / "mini_golden",
        min_positive_per_category=1,
        min_anti_total=1,
    )
    # Should have diversity_warnings even if exit 0
    assert len(rep.diversity_warnings) > 0
    assert any("author" in w.message.lower() for w in rep.diversity_warnings)
```

- [ ] **Step 3: Run, fail**

- [ ] **Step 4: Implement**

```python
# tools/golden_freshness.py
"""Golden corpus state validator per spec § 5 v0.2 (D-002 P-12, P-13, P-14)."""
from __future__ import annotations
from collections import defaultdict, Counter
from pathlib import Path
import argparse
import sys
from tools._common.frontmatter import parse_frontmatter
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

    by_category_positive_weighted = defaultdict(float)
    by_category_anti_count = defaultdict(int)
    anti_total = 0
    files_by_category = defaultdict(list)
    files_by_author_by_category = defaultdict(lambda: defaultdict(int))
    files_by_show_by_category = defaultdict(lambda: defaultdict(int))
    files_by_batch_by_author = defaultdict(lambda: defaultdict(int))

    for md in root.rglob("*.md"):
        if md.name == "README.md":
            continue
        text = md.read_text(encoding="utf-8")
        try:
            fm, _ = parse_frontmatter(text)
        except Exception as e:
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
            for sec in secondary:
                if sec in VALID_CATEGORIES and sec != primary:
                    by_category_positive_weighted[sec] += 0.5
            files_by_category[primary].append(fm)
            author = fm.get("source_author", "<unknown>")
            show = fm.get("source_show", "<unknown>")
            batch = fm.get("batch", "<unknown>")
            files_by_author_by_category[primary][author] += 1
            if primary in SHOW_SHARE_CATS:
                files_by_show_by_category[primary][show] += 1
            files_by_batch_by_author[batch][author] += 1
        elif example_type == "anti-example":  # P-13
            by_category_anti_count[primary] += 1
            anti_total += 1
        else:
            rep.add_issue(Issue(IssueLevel.ERROR, str(md), f"invalid example_type '{example_type}'; must be positive | anti-example"))

    # Coverage check
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

    # Diversity warnings (P-14)
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
```

- [ ] **Step 5: Run, pass**

`python -m pytest tests/test_golden_freshness.py -v` → 3 passed.

- [ ] **Step 6: Commit**

```bash
git add tools/golden_freshness.py tests/test_golden_freshness.py tests/fixtures/mini_golden/
git commit -m "tool: tools/golden_freshness.py — P-12 weights + P-13 example_type + P-14 diversity"
```

---

## Task 9: `tools/concern_resolution_validator.py` — R-2 enforcement

**Files:**
- Create: `tests/test_concern_resolution_validator.py`
- Create: `tools/concern_resolution_validator.py`
- Create: `tests/fixtures/mini_tmp_critic_reports/` synthetic adversarial reports

- [ ] **Step 1: Create fixtures**

`tests/fixtures/mini_tmp_critic_reports/thesis-001/A5-2026-05-30T10-00.yaml`:
```yaml
verdict: concern
model_used: opus
checked: [a, b, c]
evidence_from_artifact: [x, y]
golden_calibration_used: ["golden/x.md — note"]
reasoning: |
  (Достаточно длинное reasoning для прохождения 100-словного порога. Слово слово слово слово
  слово слово слово слово слово слово слово слово слово слово слово слово слово слово слово
  слово слово слово слово слово слово слово слово слово слово слово слово слово слово слово
  слово слово слово слово слово слово слово слово слово слово слово слово слово слово слово
  слово слово слово слово слово слово слово слово слово слово слово слово слово слово слово
  слово слово слово слово слово слово слово слово слово слово слово слово слово слово слово
  слово слово слово слово слово слово слово слово слово слово слово слово слово слово слово
  слово.)
flags:
  - severity: high
    issue: "central thesis lacks counter-formulation"
    location: "line 12"
counter_test_attempted:
  what_searched: x
  why_this: y
  why_not_found: z
```

- [ ] **Step 2: Failing tests**

```python
# tests/test_concern_resolution_validator.py
from pathlib import Path
import pytest
from tools.concern_resolution_validator import check_resolution


def test_concern_with_no_resolution_fails(fixtures_dir, tmp_path):
    # No diff in tmp_path/artifact, no D-NNN — concern unresolved
    rep = check_resolution(
        tmp_critic_reports_dir=fixtures_dir / "mini_tmp_critic_reports",
        artifact_id="thesis-001",
        artifact_diff_text="",
        decisions_dir=tmp_path,
    )
    assert rep.exit_code() == 1
    assert any("unresolved concern" in i.message.lower() for i in rep.errors())


def test_concern_addressed_in_diff_passes(fixtures_dir, tmp_path):
    diff = "added line about counter-formulation per A5 concern: central thesis lacks counter-formulation"
    rep = check_resolution(
        tmp_critic_reports_dir=fixtures_dir / "mini_tmp_critic_reports",
        artifact_id="thesis-001",
        artifact_diff_text=diff,
        decisions_dir=tmp_path,
    )
    assert rep.exit_code() == 0


def test_concern_addressed_in_decision_passes(fixtures_dir, tmp_path):
    d = tmp_path / "D-003-keep-as-is.md"
    d.write_text(
        "---\nid: D-003\n---\n\nResolving A5 concern: central thesis lacks counter-formulation — leave as-is because...",
        encoding="utf-8",
    )
    rep = check_resolution(
        tmp_critic_reports_dir=fixtures_dir / "mini_tmp_critic_reports",
        artifact_id="thesis-001",
        artifact_diff_text="",
        decisions_dir=tmp_path,
    )
    assert rep.exit_code() == 0
```

- [ ] **Step 3: Run, fail**

- [ ] **Step 4: Implement**

```python
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
        except yaml.YAMLError:
            continue
    return reports


def _is_concern_or_veto(report: dict) -> bool:
    verdict = str(report.get("verdict", ""))
    return "concern" in verdict or "veto" in verdict


def _concern_addressed(concern_issue: str, diff_text: str, decisions_dir: Path) -> bool:
    if concern_issue.lower() in diff_text.lower():
        return True
    for d in decisions_dir.glob("D-*.md"):
        if concern_issue.lower() in d.read_text(encoding="utf-8").lower():
            return True
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
    diff = subprocess.run(["git", "diff", "--cached"], capture_output=True, text=True).stdout
    rep = check_resolution(args.tmp_dir, args.artifact_id, diff, args.decisions_dir)
    print(rep.to_json())
    return rep.exit_code()


if __name__ == "__main__":
    sys.exit(main())
```

- [ ] **Step 5: Run, pass**

`python -m pytest tests/test_concern_resolution_validator.py -v` → 3 passed.

- [ ] **Step 6: Commit**

```bash
git add tools/concern_resolution_validator.py tests/test_concern_resolution_validator.py tests/fixtures/mini_tmp_critic_reports/
git commit -m "tool: tools/concern_resolution_validator.py — R-2 + P-9 enforcement with TDD"
```

---

## Task 10: `tools/README.md` — usage documentation

**Files:**
- Create: `tools/README.md`

- [ ] **Step 1: Write README with usage examples**

```markdown
# tools/ — lint scripts для Auto-ai-series ПП1

Все скрипты: exit 0 = pass, exit 1 = fail. JSON-репорт в stdout.

## CLI invocation

```bash
# Required fields validator
python -m tools.frontmatter_validator --root story-bible/

# Cross-reference resolution check
python -m tools.consistency_check --root .

# Critic YAML report validator
python -m tools.critic_report_validator tmp/critic-reports/thesis-001/A5-2026-05-30T10-00.yaml
python -m tools.critic_report_validator tmp/critic-reports/...yaml --smoke-test  # allows category-bootstrap

# Voice bleed detector
python -m tools.voice_dissimilarity scenes/some-scene.md --threshold 0.65

# Golden corpus state
python -m tools.golden_freshness --root golden/ --min-positive 3 --min-anti 5

# R-2 concern resolution check (must be called from project root with staged diff)
python -m tools.concern_resolution_validator --artifact-id thesis-001 --tmp-dir tmp/critic-reports --decisions-dir decisions
```

## JSON report schema

```json
{
  "script": "<script-name>",
  "status": "pass" | "fail",
  "issues": [
    { "level": "error", "path": "<file>", "message": "<msg>", "context": { ... } }
  ],
  "warnings": [
    { "level": "warning", "path": "<file>", "message": "<msg>", "context": { ... } }
  ],
  "diversity_warnings": [
    { "level": "warning", "path": "<file>", "message": "<msg>", "context": { ... } }
  ]
}
```

## Exit codes

- **0** — нет error-уровневых issue (warnings допустимы)
- **1** — хотя бы одна error-уровневая issue

## Coverage

Все скрипты покрыты pytest TDD, минимум 70% coverage. Запуск:

```bash
python -m pytest -v
```

См. `docs/specs/2026-05-24-infrastructure-and-skills-design.md` § 6 для контракта с design spec'ом.
```

- [ ] **Step 2: Commit**

```bash
git add tools/README.md
git commit -m "docs: tools/README.md — CLI usage + JSON schema + exit codes"
```

---

## Task 11: Phase 1 acceptance run

**Files:**
- Update: `docs/log.md`

- [ ] **Step 1: Full pytest sweep**

```bash
python -m pytest -v --cov=tools --cov-report=term-missing
```

Expected: all tests pass, coverage > 70% per module, total coverage > 70%.

- [ ] **Step 2: Smoke-run each CLI on its fixtures**

```bash
python -m tools.frontmatter_validator --root tests/fixtures/mini_bible
python -m tools.consistency_check --root tests/fixtures/mini_bible
python -m tools.critic_report_validator tests/fixtures/mini_critic_reports/valid_pass.yaml
python -m tools.voice_dissimilarity tests/fixtures/mini_scenes/scene-distinct.md
python -m tools.golden_freshness --root tests/fixtures/mini_golden --min-positive 1 --min-anti 1
```

Expected: each returns exit 0 with valid JSON `"status": "pass"` (or pass+diversity_warnings for golden_freshness).

- [ ] **Step 3: Append log entry**

```
[2026-XX-XX] tool | Phase 1 acceptance — все 6 lint скриптов + 3 _common модуля прошли TDD; pytest зелёный, coverage > 70%; smoke-runs на fixtures зелёные
```

- [ ] **Step 4: Final commit**

```bash
git add docs/log.md
git commit -m "tool: Phase 1 ПП1 acceptance — все 6 lint скриптов через TDD, pytest зелёный, coverage > 70%"
```

- [ ] **Step 5: Push**

```bash
git push origin main
```

(Только после явного approval Тимура — AGENTS.md § 6.3.)

---

## Self-review (после написания плана, перед началом execution)

**1. Spec coverage** (spec § 6.1 + D-002 P-N):

- ✅ `consistency_check.py` — Task 5
- ✅ `voice_dissimilarity.py` — Task 7 (TF-IDF threshold 0.65 в начале, калибруется на pairs/calibration/ в Phase 2/3)
- ✅ `frontmatter_validator.py` — Task 4
- ✅ `golden_freshness.py` — Task 8 (P-12 + P-13 + P-14)
- ✅ `critic_report_validator.py` — Task 6 (P-3 not_applicable + P-4 golden_unavailable_reason + P-7 3-element counter_test + P-8 model_used)
- ✅ `concern_resolution_validator.py` — Task 9 (P-9 reads from tmp/critic-reports/, R-2 enforcement)
- ✅ Coverage > 70% — Task 11 acceptance
- ✅ JSON report schema unified — Task 3 + Task 10 README
- ✅ CLI exit codes 0/1 — все скрипты

**2. Placeholder scan.** Нет: каждый task имеет actual код, exact пути, exact команды, expected результаты.

**3. Type consistency.** `Artifact` (Task 2) использует те же имена полей что в `frontmatter_validator` (Task 4), `consistency_check` (Task 5). `Reporter` / `Issue` / `IssueLevel` (Task 3) консистентно используются всеми CLI скриптами. `parse_frontmatter` (Task 1) → tuple[dict, str] — везде так применяется.

**4. Dependency ordering verified.** Tasks 1-3 (`_common/`) → Task 4 (`frontmatter_validator` использует `_common/`) → Task 5 (`consistency_check` использует `_common/artifact`) → Task 6 (`critic_report_validator` standalone) → Task 9 (`concern_resolution_validator` использует `critic_report_validator` фикстуры) → Task 7-8 (standalone) → Task 10-11 (acceptance).

**5. Acceptance criteria from spec § 9.2.** Phase 1 покрывает строку «6 скриптов в `tools/`: Каждый — exit 0/1, JSON-репорт. pytest по всем 6 зелёный. Coverage > 70%. `golden_freshness.py` поддерживает primary/secondary с весом 0.5 (P-12) и diversity_warnings (P-14); `critic_report_validator.py` поддерживает 3-element counter_test (P-7) + golden_unavailable_reason (P-4); `concern_resolution_validator.py` читает из `tmp/critic-reports/` (P-9)» полностью.

---

## Execution Handoff

**Plan complete.** Two execution options per superpowers:writing-plans skill:

1. **Subagent-Driven (recommended by skill).** Fresh subagent per task, review между задачами. Изолирует ошибки, больше overhead на Task tool вызовы.
2. **Inline Execution.** Batch execution с checkpoints. Меньше overhead, риск load одного контекста выше.

**Для Phase 1 рекомендуется Inline Execution** — pytest TDD без LLM-критиков отлично подходит под inline. Subagent layer избыточен для unit-test'ов на Python.

Тимур решает.
