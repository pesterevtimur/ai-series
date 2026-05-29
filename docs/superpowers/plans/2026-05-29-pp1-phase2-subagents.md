# Phase 2 — Subagents Implementation Plan (outline)

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.
>
> ⚠️ **OUTLINE STAGE.** Этот plan создан как outline после accept D-002 v2 (2026-05-29). Полная TDD-детализация будет добавлена **в начале Phase 2 execution** — после Phase 1 acceptance (commit «tool: Phase 1 ПП1 acceptance»). До тех пор только task headers + file lists + ключевые тесты. Это part of phased-plan-before-code discipline: «small focused phases beat one monster plan».

**Goal:** реализовать 6 субагентов-критиков в `.claude/agents/` (A1 LORE, A2 CHARACTER, A3 INCENTIVE, A4 VOICE, A5 PHILOSOPHY, A6 AUDIENCE), каждый Opus + effort: max + READ-ONLY tools (Read, Grep, Glob), с pressure-tests против структурных провалов калибровки.

**Architecture:** каждый субагент = `.claude/agents/<name>.md` файл с frontmatter (per spec § 4.2 v0.2 + P-8) + system prompt (per spec § 4.2 шаблон) + structured-format-инструкция (§ 4.3 v0.2). Pressure-tests на каждый — `.claude/agents/<name>-pressure-tests.md` с 3+ RED-сценариями (например: «artefact с явным auto-approval bait — критик должен НЕ pass'нуть»).

**Tech Stack:** Markdown с YAML frontmatter. Pressure-tests запускаются через Task tool (от orchestrator-сессии) на dummy-артефактах в `tests/regression/` (создаваемых здесь же). Validation отчётов критиков — через `tools/critic_report_validator.py` (Phase 1).

**Dependencies на Phase 1:**
- `tools/critic_report_validator.py` — для валидации dummy reports от каждого критика
- `tools/voice_dissimilarity.py` — preflight для A4 VOICE (но скилл `voice-check` это Phase 3)

---

## File Structure (планируется к созданию)

| Файл | Назначение |
|---|---|
| `.claude/agents/philosophy-adversarial.md` | A5 PHILOSOPHY критик |
| `.claude/agents/incentive-cartographer.md` | A3 CONFLICT критик |
| `.claude/agents/voice-differentiator.md` | A4 DIALOGUE критик |
| `.claude/agents/lore-realism-checker.md` | A1 LORE критик |
| `.claude/agents/character-truth-keeper.md` | A2 CHARACTER критик |
| `.claude/agents/audience-bored-detector.md` | A6 AUDIENCE критик |
| `.claude/agents/<name>-pressure-tests.md` | × 6 — RED-сценарии для каждого |
| `tests/regression/strawmen/` | Минимум 3 файла (RED для A5) |
| `tests/regression/moralizing/` | Минимум 2 файла (RED для A5/A4) |
| `tests/regression/voice-bleed/` | Минимум 2 файла (RED для A4) |
| `tests/regression/pairs/calibration/` | Strong+weak пары × 6 критиков для калибровки порогов |
| `tests/regression/pairs/holdout/` | Strong+weak пары × 6 критиков для acceptance (P-5) |
| `tests/regression/README.md` | Документация R-3 split + regression_unavailable_reason |

---

## Tasks (high-level, без TDD-детализации)

### Task 0: tests/regression/ setup
**Files:** `tests/regression/` структура + README.

### Task 1: A5 PHILOSOPHY — philosophy-adversarial.md
**Files:** `.claude/agents/philosophy-adversarial.md` + pressure-tests + 3 strawmen artifacts.
**Key checks:** A5 даёт veto на strawmen; counter_test_attempted заполнен для pass; reasoning ≥ 100 слов.

### Task 2: A3 INCENTIVE — incentive-cartographer.md
**Files:** `.claude/agents/incentive-cartographer.md` + pressure-tests + holdout pairs.
**Key checks:** A3 различает strong vs weak incentive-formulation на holdout pairs.

### Task 3: A2 CHARACTER — character-truth-keeper.md
**Files:** `.claude/agents/character-truth-keeper.md` + pressure-tests + holdout pairs.
**Key checks:** A2 ловит «декларация = incentive» (тривиальный character); даёт concern/veto.

### Task 4: A1 LORE — lore-realism-checker.md
**Files:** `.claude/agents/lore-realism-checker.md` + pressure-tests + holdout pairs.
**Key checks:** A1 ловит fantasy-incentive в реальной механике (например, корп-структура которой не существует).

### Task 5: A4 VOICE — voice-differentiator.md
**Files:** `.claude/agents/voice-differentiator.md` + pressure-tests + voice-bleed artifacts + holdout pairs.
**Key checks:** A4 запускает `tools/voice_dissimilarity.py` как preflight (через скилл `voice-check` Phase 3 — здесь только dummy intergration test); даёт veto на voice-bleed RED scenes.

### Task 6: A6 AUDIENCE — audience-bored-detector.md
**Files:** `.claude/agents/audience-bored-detector.md` + pressure-tests + holdout pairs.
**Key checks:** A6 не имеет собственного `golden/audience/` (B.4.3 (b) — не открываем в ПП1); калибруется через cross-references; pressure-tests фиксируют, что A6 не даёт системный pass.

### Task 7: Phase 2 acceptance
**Files:** Update `docs/log.md`.
**Checks:**
- Каждый из 6 субагентов имеет валидный frontmatter (`model: opus`, `effort: max`, `tools: Read, Grep, Glob` — READ-ONLY)
- Pressure-tests прошли для всех 6 — соответствующий критик выдал ожидаемый veto на RED-сценарии
- Dummy reports от каждого критика валидируются `tools/critic_report_validator.py --smoke-test`
- Holdout pairs для A1-A6 показывают расхождение verdicts (strong → pass с counter_test_attempted, weak → veto)
- Commit + log entry

---

## Expansion checklist (заполняется в начале Phase 2 execution)

Перед началом execution Phase 2, expand этот outline:

- [ ] Прочитать spec § 4 v0.2 + D-002 P-8 (effort: max) + research-001 (extended thinking)
- [ ] Для каждого критика (A1-A6) написать полный system prompt в Task 1-6 — calibration section, обязательный проход, что НИКОГДА не делает, формат вывода
- [ ] Для каждого критика написать 3+ RED pressure-test сценария с expected verdict
- [ ] Написать конкретные strawmen / moralizing / voice-bleed artifacts (Russian content, по конституции автора если уместно)
- [ ] Написать calibration + holdout pairs для каждого критика (10-12 файлов × 6 критиков = ~60-70 regression artifacts)
- [ ] Add TDD-style sub-tasks для каждой Task: «создать файл → запустить критик → проверить отчёт через critic_report_validator → commit»

---

## Dependencies + execution constraints

- **До старта Phase 2:** Phase 1 acceptance commit зелёный.
- **Auto-switch мониторинг.** A5 PHILOSOPHY на Opus + effort: max — самый дорогой по thinking tokens. На Max 5x подписке держать pacing < 60% window capacity. Если model_used в отчётах показывает Sonnet — пауза до reset.
- **Тимур может expand этот outline сам** в начале Phase 2 либо запросить меня. Зависит от его пропускной способности на момент Phase 2 старта.
