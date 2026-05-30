---
name: evidence-before-action
description: "Discipline-BLOCKER на любое утверждение готово/работает/проверено/пройдено без свежего верифицирующего вывода в той же сессии. Расширяет verification-before-completion на narrative claims (тезис устоял в адверсариальном проходе, voice-check зелёный, consistency-check зелёный, concern_resolution_validator зелёный)."
lineage:
  origin: derived
  source: "obra/superpowers@f2cbfbef:skills/verification-before-completion/SKILL.md"
  ref: "meta-skills/superpowers-references/verification-before-completion/SKILL.md"
  adapted_on: 2026-05-30
  changes:
    - "Scope: с code-verification расширено на narrative claims в Auto-ai-series"
    - "BLOCKING rule: «A5 philosophy-adversarial pass'нул» требует свежего YAML отчёта в tmp/critic-reports/"
    - "BLOCKING rule: «consistency-check зелёный» требует свежего exit 0 от tools/consistency_check.py"
    - "BLOCKING rule: «voice-check зелёный» требует свежего exit 0 от voice-check скилла (preflight + A4 verdict)"
    - "BLOCKING rule: «concern_resolution_validator зелёный» требует свежего exit 0 для R-2 enforcement (D-002 P-9: читает из tmp/critic-reports/)"
    - "BLOCKING rule: «golden_freshness зелёный» требует свежего exit 0 (включая P-12 weights + P-14 diversity warnings acknowledged)"
pressure_tested:
  status: yes
  scenarios_file: ./pressure-tests.md
  validated_on: 2026-05-30
id: evidence-before-action
version: 1
status: draft
references:
  - "docs/specs/2026-05-24-infrastructure-and-skills-design.md § 3.2 § 7 § 8 § 9"
  - "decisions/D-002-spec-corrections-and-golden-plan.md P-9"
  - "meta-skills/superpowers-references/verification-before-completion/SKILL.md"
---

# Evidence Before Action

Discipline-BLOCKER. Любая фраза «готово / работает / проверено / пройдено / зелёный / выполнено» требует **свежего верифицирующего вывода в той же сессии**. Память о предыдущем прогоне не считается. Ссылка на «было зелёным вчера» не считается.

## Когда использовать

Триггеры (любое утверждение в ходе сессии):
- «Тесты прошли»
- «Артефакт готов»
- «Voice-check пройден»
- «Consistency green»
- «A5 не нашёл проблем»
- «Concern resolution clean»
- «Golden freshness зелёный»
- «Diversity warnings acknowledged»
- «Все критики дали pass»

## Что делает (BLOCKING-логика)

1. **Идентифицируй утверждение.** Какое именно? Чем доказывается?
2. **Запроси доказательство в текущей сессии:**
   - Для code claims → exit code + хвост стандартного вывода последней команды
   - Для critic claims → путь к свежему YAML в `tmp/critic-reports/<artifact-id>/<critic>-<timestamp>.yaml` (P-9)
   - Для tool claims → JSON-отчёт скрипта в stdout + exit code (Phase 1 tools)
3. **Если доказательство ≥1 сообщения назад / не в текущей сессии → BLOCK.** Шоураннер обязан перезапустить проверку.
4. **Если доказательство присутствует:**
   - Проверь свежесть (timestamp / последовательность вызовов)
   - Проверь соответствие (тот же артефакт? те же критики? те же входы?)
   - Если ок → action разрешён.

## Что НЕ делает

- **НЕ верифицирует творческое качество.** «Сцена хорошая» — не утверждение готово, это субъективная оценка. (Адверсариальный проход + critic verdicts дают доказательство, не оценка.)
- **НЕ заменяет адверсариальный проход.** Просто требует доказательства того, что он был выполнен в текущей сессии.
- **НЕ блокирует exploratory работу.** Только финализацию / commit / merge / приём артефакта.

## Связанные артефакты

- `meta-skills/superpowers-references/verification-before-completion/SKILL.md` — pinned source
- `tools/concern_resolution_validator.py` — основной источник «свежего exit 0» для R-2
- `tools/consistency_check.py` — источник «свежего exit 0» для consistency claim
- `tools/critic_report_validator.py` — источник «свежего exit 0» для critic format claim
- `.claude/skills/voice-check/SKILL.md` — другой discipline-BLOCKER, дополняет
- `.claude/skills/consistency-check/SKILL.md` — другой discipline-BLOCKER, дополняет

## Pressure-tests

См. `./pressure-tests.md` — 4 RED-сценария попыток обхода BLOCKER'а.

## Связь с spec

- spec § 3.2 — lineage от verification-before-completion + scope расширение
- spec § 7 — lineage format
- spec § 8.1 — Поток A использует evidence-before-action на каждом финализирующем шаге
- spec § 9.4 — R-2 enforcement через concern_resolution_validator (P-9)
- D-002 P-9 — критик-отчёты на диске для evidence
