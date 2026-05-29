# Phase 3 — Skills Implementation Plan (outline)

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.
>
> ⚠️ **OUTLINE STAGE.** Полная TDD-детализация добавляется в начале Phase 3 execution — после Phase 2 acceptance.

**Goal:** реализовать 8 скиллов в `.claude/skills/` (P-1: было 9, philosophy-stress-test отменён) + 4 reference в `meta-skills/superpowers-references/` (lineage from Superpowers SHA `f2cbfbef`).

**Architecture:** каждый скилл — SKILL.md по формату `writing-narrative-skills`. 3 discipline-BLOCKER (`voice-check`, `consistency-check`, `evidence-before-action`) имеют `pressure_tested: status: yes` + `<skill>-pressure-tests.md` с 3+ RED-сценариями.

**Tech Stack:** Markdown с frontmatter; pressure-tests запускаются через invocation скилла в orchestrator-сессии (NOT через Task tool — скиллы это процедурные блокеры).

**Dependencies на Phase 1+2:**
- `tools/consistency_check.py`, `tools/voice_dissimilarity.py`, `tools/concern_resolution_validator.py` — вызываются из соответствующих BLOCKER скиллов
- 6 субагентов из Phase 2 — вызываются из `adversarial-review-pass` (для A1-A6) и `voice-check` (для A4)
- 4 reference в `meta-skills/superpowers-references/` — pinned SHA `f2cbfbef` (verification-before-completion, writing-skills, brainstorming, subagent-driven-development)

---

## File Structure (планируется к созданию)

### .claude/skills/ (8 скиллов)

| Скилл | Тип | Файл |
|---|---|---|
| `voice-check` | discipline-BLOCKER | `.claude/skills/voice-check/SKILL.md` + `pressure-tests.md` |
| `consistency-check` | discipline-BLOCKER | `.claude/skills/consistency-check/SKILL.md` + `pressure-tests.md` |
| `evidence-before-action` | discipline-BLOCKER + lineage | `.claude/skills/evidence-before-action/SKILL.md` + `pressure-tests.md` |
| `adversarial-review-pass` | orchestration | `.claude/skills/adversarial-review-pass/SKILL.md` |
| `add-golden-example` | research-orchestration | `.claude/skills/add-golden-example/SKILL.md` |
| `draft-story-bible-section` | creative + R-1 шляпы | `.claude/skills/draft-story-bible-section/SKILL.md` |
| `draft-character-sheet` | creative + R-1 шляпы | `.claude/skills/draft-character-sheet/SKILL.md` |
| `writing-narrative-skills` | meta-authoring + lineage | `.claude/skills/writing-narrative-skills/SKILL.md` |

### meta-skills/superpowers-references/ (4 pinned reference)

| Reference | Использование |
|---|---|
| `verification-before-completion/` | Source для адаптации `evidence-before-action` (см. P-8 / spec § 7.3 lineage frontmatter) |
| `writing-skills/` | Source для адаптации `writing-narrative-skills` |
| `brainstorming/` | Used напрямую — pinned для drift-detection |
| `subagent-driven-development/` | Used напрямую — pinned для drift-detection |

Каждая reference содержит: `README.md` (зачем pinned), byte-equal `SKILL.md` (копия с upstream SHA `f2cbfbef`), `METADATA.json` (SHA + дата pinning).

---

## Tasks (high-level)

### Task 0: meta-skills/superpowers-references/ setup
**Files:** 4 reference папки + lineage METADATA.json.

### Task 1: writing-narrative-skills (lineage от writing-skills)
**Files:** `.claude/skills/writing-narrative-skills/SKILL.md` + lineage frontmatter.
**Key:** discipline-скиллы в нарративном домене обязательно pressure-tested (3+ RED-сценарии).

### Task 2: evidence-before-action (lineage от verification-before-completion)
**Files:** `.claude/skills/evidence-before-action/SKILL.md` + `pressure-tests.md` + lineage frontmatter.
**Key:** расширяет verification на narrative claims (тезис устоял, voice-check пройден, consistency-check зелёный, concern_resolution_validator зелёный). BLOCKER на «готово/работает/проверено» без свежего вывода.
**Pressure-tests:** 3+ RED-сценария — попытки обхода скилла («это очевидно работает», «я только что коммитил похожее»).

### Task 3: consistency-check (discipline-BLOCKER)
**Files:** `.claude/skills/consistency-check/SKILL.md` + `pressure-tests.md`.
**Key:** запускает `tools/consistency_check.py` (Phase 1); BLOCKER на merge при exit 1.
**Pressure-tests:** 3+ RED — попытки коммитить артефакт с dangling reference.

### Task 4: voice-check (discipline-BLOCKER)
**Files:** `.claude/skills/voice-check/SKILL.md` + `pressure-tests.md`.
**Key:** запускает `tools/voice_dissimilarity.py` (preflight) → если sim > 0.65 → вызывает A4 voice-differentiator (Task tool). Возвращает confusion-matrix.
**Pressure-tests:** 3+ RED — voice-bleed сцены, которые скилл должен ловить.

### Task 5: adversarial-review-pass (orchestration)
**Files:** `.claude/skills/adversarial-review-pass/SKILL.md`.
**Key:**
- Последовательно зовёт A5, A1, A3, A2, A6 (через Task tool); A4 только для сцен (на не-сценах фиксирует `not_applicable: <reason>`)
- После каждого critic-call — sub-step P-9: записать YAML отчёт в `tmp/critic-reports/<artifact-id>/<critic>-<timestamp>.yaml` ИЗ orchestrator'а (субагенты read-only)
- Validate отчёт через `tools/critic_report_validator.py --smoke-test` (если в smoke-test режиме) или без флага
- При failed validation — повторный вызов с инструкцией «переделай»
- Собирает агрегированный markdown summary

### Task 6: add-golden-example (research-orchestration)
**Files:** `.claude/skills/add-golden-example/SKILL.md`.
**Key:**
- Читает `raw/_cowork-dumps/<batch>/_manifest.md` и материалы
- P-11 split: описание эталона → `golden/<primary_category>/`, рекомендации → `docs/cowork-notes/<batch>.md`
- P-13 split: derived anti-lessons из positive → `docs/cowork-notes/derived-anti-lessons/`
- Reconstruction логика (открытый vs закрытый контент)
- Запускает `tools/golden_freshness.py` после merge
- P-12 multi-category: frontmatter с primary_category + secondary_categories
- P-14: проверяет diversity_warnings в JSON-отчёте — либо acknowledge в `golden/README.md`, либо запросить добивку

### Task 7: draft-story-bible-section (creative + R-1 шляпы)
**Files:** `.claude/skills/draft-story-bible-section/SKILL.md`.
**Key (P-2):** 3 ПОСЛЕДОВАТЕЛЬНЫЕ шляпы в orchestrator-сессии (LORE / PHILOSOPHY / CHARACTER-dominant), НЕ параллельные Task-вызовы. Явные context-marker'ы между шляпами либо `/clear`. Шоураннер собирает 3 драфта, выбирает или синтезирует. Затем обязательный `adversarial-review-pass`.

### Task 8: draft-character-sheet (creative + R-1 шляпы)
**Files:** `.claude/skills/draft-character-sheet/SKILL.md`.
**Key:** аналогично Task 7 с уклонами CHARACTER / CONFLICT / PHILOSOPHY-dominant.

### Task 9: Phase 3 acceptance
**Files:** Update `docs/log.md`.
**Checks:**
- Каждый из 8 скиллов имеет валидную SKILL.md
- 3 discipline-BLOCKER (`voice-check`, `consistency-check`, `evidence-before-action`) имеют `pressure_tested: status: yes` в frontmatter + соответствующий `pressure-tests.md` файл
- Pressure-tests прошли для всех 3 BLOCKER'ов (RED-сценарии не обходят дисциплину; P-10: «обошёл RED» = провал)
- 2 lineage скилла (`writing-narrative-skills` + `evidence-before-action`) имеют корректный `lineage:` frontmatter с SHA `f2cbfbef`
- 4 reference в `meta-skills/` имеют byte-equal SKILL.md + METADATA.json
- `adversarial-review-pass` корректно делает sub-step P-9 (tmp/critic-reports на диск)
- `add-golden-example` корректно splits golden/ vs cowork-notes/ vs derived-anti-lessons/
- Commit + log entry

---

## Expansion checklist (заполняется в начале Phase 3)

- [ ] Прочитать spec § 3 v0.2 (все 8 скиллов) + § 7 (lineage) + writing-narrative-skills pressure-testing требование
- [ ] Для каждого discipline-BLOCKER написать 3+ конкретных RED pressure-сценария
- [ ] Для adversarial-review-pass прописать exact sub-step P-9 wire-up: «после Task call → шоураннер записывает YAML на диск через Write tool → tools/critic_report_validator.py читает с диска»
- [ ] Add TDD sub-tasks для каждой Task

---

## Dependencies + execution constraints

- **До старта Phase 3:** Phase 2 acceptance commit зелёный.
- **Auto-switch мониторинг.** Phase 3 включает первые smoke-runs `adversarial-review-pass` для pressure-test'ов BLOCKER скиллов — это 5 Opus critic-calls × несколько runs. Самая дорогая Phase 3 task — Task 5 (adversarial-review-pass) — может потребовать половины окна.
