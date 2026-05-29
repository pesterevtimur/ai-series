# Phase 4 — Smoke-test End-to-End Implementation Plan (outline)

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.
>
> ⚠️ **OUTLINE STAGE.** Полная детализация добавляется в начале Phase 4 execution — после Phase 3 acceptance.

**Goal:** прогнать Поток A (spec § 8.1 v0.2) на 4 артефактах для acceptance ПП1 (spec § 9.7 Definition of Done).

**Architecture:** end-to-end execution через все скиллы Phase 3 — brainstorming → R-1 шляпы → adversarial-review-pass (P-9 tmp/critic-reports) → consistency-check → concern_resolution_validator → evidence-before-action → write → commit → archive critic-reports.

**Tech Stack:** все артефакты Phase 1-3. Никаких новых файлов в `tools/` или `.claude/`. Создаются только контентные артефакты в `story-bible/`, `characters/`, `scenes/`, `golden/`, `docs/critic-reports-archive/`.

**Dependencies на Phase 1-3:**
- Все 6 lint-скриптов работают (Phase 1)
- Все 6 субагентов работают и валидируются на pressure-tests (Phase 2)
- Все 8 скиллов работают, BLOCKER'ы pressure-tested (Phase 3)
- `raw/_cowork-dumps/` обработан через `add-golden-example` → `golden/` наполнен bootstrap-минимумом

---

## File Structure (планируется к созданию)

### Pre-smoke-test setup

| Файл | Назначение |
|---|---|
| `CLAUDE.md` | Контракт проекта + 4-5 законов (адаптированных из spec) |
| `README.md` | Одна страница: что это, как стартовать |
| `.mcp.json` | filesystem-MCP для Claude Desktop |
| `golden/<category>/*.md` | Bootstrap-минимум (≥3 positive в каждой из 6 категорий) — выход `add-golden-example` на 19 партиях |
| `golden/anti-examples/*.md` | Минимум по 1 anti в 4 категориях (P-15: conflicts + adversarial-passes = 0 acknowledged) |

### Smoke-test artifacts (4 шт.)

| Файл | Тип Потока A | Объём |
|---|---|---|
| `story-bible/thesis.md` | non-scene | ~150 слов |
| `story-bible/world-rules.md` | non-scene | 5 правил мира |
| `characters/<one>.md` | non-scene | 1 character (тревожная компетентность) |
| `scenes/smoke-test-dialogue.md` | scene (+ A4) | 300-500 слов, 2-3 говорящих |

### Workflow side-effects (создаваемые автоматически)

| Файл | Где | Назначение |
|---|---|---|
| `tmp/critic-reports/<artifact-id>/<critic>-<timestamp>.yaml` | tmp/ (gitignored) | P-9 — рабочие YAML до commit |
| `docs/critic-reports-archive/<artifact-id>/*.yaml` | tracked | P-9 — архив после commit |
| `decisions/D-NNN-*.md` | tracked | если есть concern/veto который шоураннер решил оставить |
| `docs/cowork-notes/<batch>.md` + `derived-anti-lessons/` | tracked | если `add-golden-example` отделил рекомендации (P-11/P-13) |

---

## Tasks (high-level)

### Task 0: Pre-smoke-test setup
**Files:** `CLAUDE.md`, `README.md`, `.mcp.json`.
**Key:** CLAUDE.md содержит 4-5 законов проекта; ссылки на spec, D-001, D-002, cost-estimate.

### Task 1: Golden corpus наполнение
**Files:** `golden/<category>/*.md` (через `add-golden-example` на 19 партиях).
**Key:**
- 19 партий из `raw/_cowork-dumps/` обрабатываются через `add-golden-example`
- P-11 split: эталоны → `golden/`, рекомендации → `docs/cowork-notes/<batch>.md`
- P-13 split: derived anti → `docs/cowork-notes/derived-anti-lessons/`
- P-12 multi-category: primary + secondary в frontmatter
- P-14: diversity_warnings либо acknowledged в `golden/README.md`, либо запросить добивку (для P-15 пропущенных партий — acknowledge)
- `golden_freshness.py --root golden` зелёный с bootstrap-порогом

### Task 2: thesis.md — non-scene artefact
**Files:** `story-bible/thesis.md` + `docs/critic-reports-archive/thesis-001/*.yaml`.
**Key:**
- Поток A полный (spec § 8.1 v0.2): brainstorming → R-1 шляпы (3 шляпы LORE/PHILOSOPHY/CHARACTER-dominant) → synthesis → adversarial-review-pass (5 критиков A5+A1+A3+A2+A6, A4 не_applicable) → tmp/critic-reports (P-9) → consistency-check → concern_resolution_validator → evidence-before-action → write → commit `bible: thesis v0.1 ...` → archive critic-reports
- Acceptance: все critic-reports валидируются через `critic_report_validator.py --smoke-test` (P-4 `category-bootstrap` допустим); `model_used` зафиксирован в каждом отчёте (P-8 auto-switch audit)

### Task 3: world-rules.md — non-scene artefact
**Files:** `story-bible/world-rules.md` + critic-reports.
**Key:** аналогично Task 2 + cross-validation с thesis.md (consistency-check проверяет references).

### Task 4: <one>.md — character-sheet non-scene artefact
**Files:** `characters/<id>.md` + critic-reports.
**Key:**
- `draft-character-sheet` с уклонами CHARACTER / CONFLICT / PHILOSOPHY-dominant (3 шляпы P-2)
- Артефакт «AI-safety-исследовательница, тревожная компетентность»
- Cross-reference на thesis.md + world-rules.md в frontmatter `references`

### Task 5: smoke-test-dialogue.md — scene artefact (+ A4)
**Files:** `scenes/smoke-test-dialogue.md` + critic-reports (включая A4).
**Key:**
- Сценка 300-500 слов с 2-3 говорящими в формате `**ИМЯ:** реплика`
- Поток A + A4 voice-check (preflight через `tools/voice_dissimilarity.py` → A4 субагент через Task tool)
- `voice-check` BLOCKER должен пройти (sim < 0.65 между всеми парами говорящих)
- A4 даёт content verdict (НЕ пустой, не auto-pass)

### Task 6: Phase 4 acceptance + smoke-test verification
**Files:** Update `docs/log.md`, возможно `tests/regression/README.md` если нашлись gaps.

**Checks per spec § 9.5 v0.2 (Critical failures):**
- ✅ pytest зелёный на всех 6 lint-скриптах
- ✅ Никакой RED pressure-сценарий не обошёл discipline-BLOCKER скилл (P-10)
- ✅ НЕ все 6 субагентов auto-approve все 4 артефакта
- ✅ Каждый subagent pass'нувший verdict имеет полный 3-element `counter_test_attempted` (P-7)
- ✅ Каждый subagent pass'нувший verdict имеет `golden_calibration_used` непуст либо `golden_unavailable_reason ∈ {category-empty, category-bootstrap, category-irrelevant}` (P-4)
- ✅ R-3.a regression veto: критики выдают veto на соответствующие RED артефакты
- ✅ R-3.b holdout pairs: verdicts разошлись на holdout (P-5)
- ✅ `consistency_check.py` зелёный на собственных fixtures
- ✅ `golden_freshness.py` зелёный (diversity_warnings acknowledged)
- ✅ Каждый адаптированный скилл имеет `lineage:` и `pressure_tested: yes`
- ✅ Каждый субагент READ-ONLY (tools: Read, Grep, Glob)
- ✅ Каждый субагент имеет `effort: max` в frontmatter (P-8)
- ✅ `adversarial-review-pass` валидирует структуру отчётов
- ✅ critic-reports живут в tmp/ → docs/critic-reports-archive/ (P-9)
- ✅ `model_used` поле — если на ≥20% critic-вызовов Sonnet → escalate D-NNN

**Если P-15 risk материализовался** (A3 систематический pass из-за пустого conflicts anti) — это **известный flagged risk**, не блокер; фиксируется как known issue для ПП2 в `docs/log.md` строкой:

```
[YYYY-MM-DD] note | ПП2 follow-up: A3/A5 показали systematic pass — нужна Cowork-партия B.4.1 (anti-examples-batch-02)
```

### Task 7: ПП1 acceptance Definition of Done
**Files:** Update `docs/log.md` финальной строкой:

```
[YYYY-MM-DD] milestone | ПП1 acceptance ✅ — 4 артефакта прошли Поток A, 6 критиков, R-3 holdout, R-2 enforcement, all lint green
```

**Commit:**
```bash
git commit -m "milestone: ПП1 ACCEPTED — infra + smoke-test done; ready for ПП2"
```

---

## Expansion checklist (заполняется в начале Phase 4)

- [ ] Прочитать spec § 8.1 v0.2 (Поток A полностью) + § 9 (acceptance criteria) + § 11.6 (P-15 risk)
- [ ] Для каждого артефакта (thesis, world-rules, character, scene) прописать exact prompts для R-1 шляп
- [ ] Прописать ожидаемые типы concern/veto от 6 критиков на каждом артефакте — чтобы checkpoint'ить когда smoke-test даёт reasonable distribution
- [ ] Add TDD-style sub-tasks: для каждой задачи Task 2-5 — «execute Поток A → проверить acceptance § 9.5 → commit»

---

## Dependencies + execution constraints

- **До старта Phase 4:** Phase 3 acceptance commit зелёный + golden bootstrap наполнен.
- **Auto-switch мониторинг — критично.** Phase 4 — самая дорогая фаза (4 артефакта × Поток A + 2 rework rounds). 5-7 окон по cost-estimate § 9.4. Каждое окно держать < 60% capacity. Если model_used показывает Sonnet — пауза до reset.
- **Pacing рекомендация.** День 5 (см. cost-estimate § 9.4):
  - Окно 1: thesis + world-rules (2 артефакта)
  - Окно 2: character + scene (2 артефакта) + acceptance verification
- **Если P-15 материализуется.** Acceptance НЕ откладывается — задача документируется как ПП2 follow-up, ПП1 закрывается как «accepted with known issue».
- **Resource budget.** ~80-100 messages на Phase 4 (см. cost-estimate); ~$0 marginal под Max 5x подписку.
