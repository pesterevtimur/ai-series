# tools/ — lint scripts для Auto-ai-series ПП1

Все скрипты: exit 0 = pass, exit 1 = fail. JSON-репорт в stdout. Реализованы через TDD в Phase 1.

## CLI invocation

```bash
# Required fields + unique id + valid status (P-1..P-2 v0.2)
python -m tools.frontmatter_validator --root story-bible/

# Cross-reference resolution check
python -m tools.consistency_check --root .

# Critic YAML report validator (P-3, P-4, P-7, P-8 v0.2)
python -m tools.critic_report_validator tmp/critic-reports/thesis-001/A5-2026-05-30T10-00.yaml
python -m tools.critic_report_validator <report> --smoke-test  # allows category-bootstrap (P-4)

# Voice bleed detector (TF-IDF cosine, threshold 0.65)
python -m tools.voice_dissimilarity scenes/some-scene.md --threshold 0.65

# Golden corpus state (P-12 weights + P-13 example_type + P-14 diversity)
python -m tools.golden_freshness --root golden/ --min-positive 3 --min-anti 5

# R-2 concern resolution check (D-002 P-9 — reads tmp/critic-reports/)
python -m tools.concern_resolution_validator --artifact-id thesis-001 \
    --tmp-dir tmp/critic-reports --decisions-dir decisions
```

## JSON report schema

```json
{
  "script": "<script-name>",
  "status": "pass" | "fail",
  "issues": [
    { "level": "error", "path": "<file>", "message": "<msg>", "context": { } }
  ],
  "warnings": [
    { "level": "warning", "path": "<file>", "message": "<msg>", "context": { } }
  ],
  "diversity_warnings": [
    { "level": "warning", "path": "<file>", "message": "<msg>", "context": { } }
  ]
}
```

## Exit codes

- **0** — нет error-уровневых issue (warnings и diversity_warnings допустимы)
- **1** — хотя бы одна error-уровневая issue

`diversity_warnings` (P-14) — отдельный bucket; не блокирует commit, но требует acknowledgement в `golden/README.md` либо добивочной партии от Cowork.

## Shared modules

`tools/_common/`:
- `frontmatter.py` — `parse_frontmatter(text) → (dict, body)` + `FrontmatterError`. Strips UTF-8 BOM.
- `artifact.py` — `Artifact` dataclass + `from_text` / `from_file` classmethods. Validates required fields (id, version, status, references), valid status (`draft | reviewed | approved`), type guards for references (list, accepts `null` as `[]`) and version (must be int).
- `reporter.py` — `Reporter` + `Issue` + `IssueLevel`. JSON serialization handles `Path` objects (str-coerce), accepts string `level` (auto-coerce to `IssueLevel`).

## Coverage

Все 6 скриптов покрыты pytest TDD. Минимум 70% coverage по проекту:

```bash
python -m pytest -v
```

## Robustness invariants

Все CLI скрипты:
- Валидируют `root.exists() and root.is_dir()` (где применимо)
- Пропускают `README.md`, `CHANGELOG.md`, `_*.md` (документация / template / manifest)
- Ловят `OSError` / `UnicodeDecodeError` per-file и продолжают
- Эмитят Issue вместо crash на malformed input

## Связь с design spec

Каждый скрипт реализует требование из:
- spec § 6.1 v0.2 — таблица скриптов и их назначений
- D-002 P-N v2 — конкретные правки enforcement (P-3, P-4, P-7, P-8, P-9, P-12, P-13, P-14)
- spec § 9.2 — acceptance criteria для ПП1

См. `docs/specs/2026-05-24-infrastructure-and-skills-design.md` § 6 для полного контракта.
