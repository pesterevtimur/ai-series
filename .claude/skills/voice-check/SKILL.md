---
name: voice-check
description: "Discipline-BLOCKER для сцен с >1 говорящим в формате **ИМЯ:** реплика. Двухступенчатый: preflight через tools/voice_dissimilarity.py (TF-IDF cosine, threshold 0.65), затем content verdict от A4 voice-differentiator через Task tool. Возвращает confusion-matrix. На не-сценах NO-OP (фиксирует not_applicable_reason, P-3)."
pressure_tested:
  status: yes
  scenarios_file: ./pressure-tests.md
  validated_on: 2026-05-30
id: voice-check
version: 1
status: draft
references:
  - "docs/specs/2026-05-24-infrastructure-and-skills-design.md § 3.3 § 6.1"
  - "tools/voice_dissimilarity.py"
  - ".claude/agents/voice-differentiator.md"
---

# Voice Check

Discipline-BLOCKER. Запускается после любой сцены с >1 говорящим. Двухступенчатый:

1. **Preflight (структурный):** `tools/voice_dissimilarity.py` — TF-IDF cosine similarity между всеми парами говорящих. Threshold 0.65 (калибруется на `tests/regression/pairs/calibration/voice-*.md`).
2. **Content verdict (семантический):** A4 `voice-differentiator` субагент через Task tool — даёт verdict pass / concern / veto с конкретными lexical markers различия / провала.

## Когда использовать

- После любой сцены с форматом `**ИМЯ:** реплика` где >1 уникальное имя.
- В Поток A шаг 9-10 (spec § 8.1).
- Перед commit сцены в `scenes/`.

## Что делает

1. **Detection:** проверяет наличие >1 уникального `**ИМЯ:**` в артефакте.
   - Если 0-1 — NO-OP, фиксирует `not_applicable_reason: "артефакт не содержит диалога с >1 говорящим"`. (P-3)
2. **Preflight:**
   ```bash
   python -m tools.voice_dissimilarity scenes/<file>.md --threshold 0.65
   ```
   - Exit 0 (sim < 0.65 на всех парах) → структурно ок
   - Exit 1 (sim > 0.65 хотя бы на одной паре) → структурно flagged
3. **Content verdict (A4):**
   - Invoke через Task tool: `Task(subagent_type="voice-differentiator", prompt="Прочитай <file> и выдай YAML отчёт...")`.
   - A4 даёт verdict + flags с конкретными lexical/syntactic markers
4. **Confusion matrix (return):**
   - По всем парам говорящих: preflight sim score + A4 verdict per pair
   - Aggregate verdict: если хотя бы одна пара flagged → concern (preflight) или veto (A4) → BLOCK merge.
5. **Persist:** YAML отчёт A4 → `tmp/critic-reports/<artifact-id>/A4-<timestamp>.yaml` (P-9).

## Что НЕ делает

- **НЕ запускается на не-сценах.** Фиксирует not_applicable + reason.
- **НЕ заменяет adversarial-review-pass.** A4 — один из 6 критиков; voice-check специализирован но не покрывает A1/A2/A3/A5/A6.
- **НЕ fixes voice-bleed.** Только репортит. Шоураннер переписывает сцену.

## Связанные артефакты

- `tools/voice_dissimilarity.py` — preflight движок
- `.claude/agents/voice-differentiator.md` — A4 субагент для content verdict
- `.claude/skills/evidence-before-action/SKILL.md` — требует свежего exit 0 voice-check
- `.claude/skills/adversarial-review-pass/SKILL.md` — на сценах voice-check выполняется до adversarial-review-pass (cheap preflight)
- `tests/regression/voice-bleed/` + `tests/regression/pairs/calibration/voice-*.md` — regression fixtures для P-5

## Pressure-tests

См. `./pressure-tests.md` — 4 RED-сценария попыток обхода BLOCKER'а.

## Связь с spec

- spec § 3.3 — описание скилла + двухступенчатость
- spec § 6.1 — описание tools/voice_dissimilarity.py
- spec § 8.1 шаг 9-10 — место в Потоке A
- spec § 9.5 — critical failures
- D-002 P-3 — not_applicable на не-сценах
- D-002 P-9 — A4 отчёт на диск
