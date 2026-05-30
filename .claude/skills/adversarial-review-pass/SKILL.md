---
name: adversarial-review-pass
description: "Orchestration. Последовательно вызывает 5 критиков (A5, A1, A3, A2, A6) + A4 если артефакт — сцена. После каждого critic-call записывает YAML в tmp/critic-reports/<artifact-id>/<critic>-<timestamp>.yaml (P-9). Валидирует через critic_report_validator.py --smoke-test (или без --smoke-test после ПП1 acceptance). При failed validation повторяет вызов. Агрегирует markdown summary."
pressure_tested:
  status: no
id: adversarial-review-pass
version: 1
status: draft
references:
  - "docs/specs/2026-05-24-infrastructure-and-skills-design.md § 3.3 § 8.1"
  - "decisions/D-002-spec-corrections-and-golden-plan.md P-1 P-3 P-9"
  - "tools/critic_report_validator.py"
  - ".claude/agents/philosophy-adversarial.md"
  - ".claude/agents/incentive-cartographer.md"
  - ".claude/agents/character-truth-keeper.md"
  - ".claude/agents/lore-realism-checker.md"
  - ".claude/agents/voice-differentiator.md"
  - ".claude/agents/audience-bored-detector.md"
---

# Adversarial Review Pass

Orchestration. Гонит артефакт через 5-6 субагентов-критиков последовательно. Собирает структурированные YAML-отчёты, валидирует структуру, агрегирует summary.

## Когда использовать

- Перед финализацией любого narrative артефакта (story-bible/, characters/, scenes/, theses/).
- В Поток A шаг 4 (spec § 8.1 v0.2). После voice-check (если сцена) и consistency-check.
- НЕ в exploratory stage (draft → review → polish).

## Что делает

### 1. Calibration check (prerequisite)

- Verify `golden/` категории не пусты для каждого критика (или они корректно заполняют `golden_unavailable_reason ∈ {category-empty, category-bootstrap, category-irrelevant}` per P-4).
- В bootstrap ПП1 — `category-bootstrap` допустим (D-002 P-4).

### 2. Sequential invocation (5-6 критиков)

**Порядок:** A5 → A1 → A3 → A2 → A6 → A4 (последний только для сцен).

**Per critic:**
```
Task(
  subagent_type="<critic-name>",
  description="<short>",
  prompt="Прочитай <artifact-path> и выдай YAML отчёт по формату из твоего system prompt. <дополнительный контекст>."
)
```

После получения output от Task tool:
1. **Запиши YAML на диск** (P-9):
   ```
   mkdir -p tmp/critic-reports/<artifact-id>
   write tmp/critic-reports/<artifact-id>/<critic>-<ISO-timestamp>.yaml
   ```
   Это **обязательно** — `concern_resolution_validator.py` читает только с диска (P-9).
2. **Validate структуру:**
   ```bash
   python -m tools.critic_report_validator tmp/critic-reports/<artifact-id>/<critic>-<timestamp>.yaml --smoke-test
   ```
   - Exit 0 → отчёт валиден
   - Exit 1 → re-invoke с инструкцией: «Твой предыдущий отчёт failed validation: <issues>. Перевыдай по формату».
3. **A4 specifically:** на не-сценах фиксируется `verdict: pass + not_applicable_reason` (P-3) — это валидный verdict.

### 3. Aggregation

Собирай markdown summary:

```markdown
# Adversarial review summary — <artifact-id>

| Critic | Verdict | Severity | Counter-test | Model |
|---|---|---|---|---|
| A5 PHILOSOPHY | <pass/concern/veto> | <high/medium/low/-> | <ok/missing> | opus |
| A1 LORE | ... | ... | ... | ... |
| A3 INCENTIVE | ... | ... | ... | ... |
| A2 CHARACTER | ... | ... | ... | ... |
| A6 AUDIENCE | ... | ... | ... | ... |
| A4 VOICE | <verdict / not_applicable> | ... | ... | ... |

## Flags (concern + veto, severity ≥ medium)

- A5 [high]: <issue> — <location>
- ...

## Counter-test missing (для verdict=pass — должно быть пусто)

- ... (если что-то здесь — re-invoke + не commit)

## Model audit (P-8 / cost-estimate § 10)

- Все opus — OK
- Есть sonnet → escalate D-NNN (см. cost-estimate § 10)

## Не сработавшие критики

- ... (если технически not_applicable — A4 на не-сцене — фиксируем reason)
```

### 4. Handoff в evidence-before-action

После завершения adversarial-review-pass — handoff в `evidence-before-action` для следующих утверждений в сессии:
- «A5 не нашёл проблем» → требует свежего <artifact-id>/A5-*.yaml (есть)
- «adversarial-review-pass прошёл» → требует свежего summary (есть)

## Что НЕ делает

- **НЕ переписывает артефакт.** Только репортит через критиков.
- **НЕ принимает решение commit/not-commit.** Решение — за шоураннером + `evidence-before-action` + `concern_resolution_validator.py`.
- **НЕ пресс-тестирует сам себя.** orchestration, не discipline-BLOCKER.

## Связанные артефакты

- 6 субагентов A1-A6 в `.claude/agents/`
- `tools/critic_report_validator.py` — валидация YAML
- `tools/concern_resolution_validator.py` — downstream R-2 enforcement (читает с tmp/)
- `.claude/skills/evidence-before-action/SKILL.md` — после adversarial-review-pass требует свежего summary

## Pressure-tests

Не применимо. `pressure_tested: status: no`.

## Связь с spec

- spec § 3.3 — описание скилла
- spec § 8.1 шаг 4 — место в Потоке A
- spec § 4 — субагенты A1-A6 структура
- D-002 P-1 — A5 встроена сюда (philosophy-stress-test отменён)
- D-002 P-3 — A4 not_applicable на не-сценах
- D-002 P-9 — YAML на диск, не из контекста
- D-002 P-8 — model_used аудит
- D-002 P-4 — golden_unavailable_reason в bootstrap
