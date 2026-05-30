---
name: consistency-check
description: "Discipline-BLOCKER перед merge артефакта. Запускает tools/consistency_check.py: проверяет что все references в frontmatter существуют, факты не противоречат, статусы валидны. Exit 1 от скрипта = merge запрещён. Не fixes автоматически — только репортит."
pressure_tested:
  status: yes
  scenarios_file: ./pressure-tests.md
  validated_on: 2026-05-30
id: consistency-check
version: 1
status: draft
references:
  - "docs/specs/2026-05-24-infrastructure-and-skills-design.md § 3.3 § 6.1"
  - "tools/consistency_check.py"
---

# Consistency Check

Discipline-BLOCKER. Запускается перед каждым merge артефакта в `story-bible/`, `characters/`, `scenes/`. Если `tools/consistency_check.py --root .` вернул exit 1 — merge запрещён до фикса.

## Когда использовать

- Перед commit любого нового или изменённого narrative артефакта.
- Перед `adversarial-review-pass` (предупредительно — не имеет смысла гонять критиков на consistency-broken артефакте).
- В Поток A шаг финализации (spec § 8.1).

## Что делает

1. **Запускает скрипт:**
   ```bash
   python -m tools.consistency_check --root .
   ```
2. **Анализирует JSON-отчёт в stdout:**
   - `status: pass` + exit 0 → merge разрешён
   - `status: fail` + exit 1 → BLOCK. Перечисли issues с levels error.
3. **Для каждой error issue:**
   - `path:` — где проблема
   - `message:` — какая (dangling reference / invalid status / etc.)
   - `context:` — дополнительные данные если есть
4. **Не fixes автоматически.** Возвращает issues шоураннеру для ручного исправления.

## Что НЕ делает

- **НЕ проверяет творческое содержание.** Это adversarial-review-pass.
- **НЕ проверяет voice diff.** Это voice-check.
- **НЕ автофиксит.** Только репортит.
- **НЕ блокирует exploratory работу.** Только merge / finalize.

## Связанные артефакты

- `tools/consistency_check.py` — основной движок
- `tools/_common/artifact.py` — модель артефакта (references field)
- `.claude/skills/evidence-before-action/SKILL.md` — требует свежего вывода `consistency_check`
- `.claude/skills/adversarial-review-pass/SKILL.md` — gateкипит consistency перед собой

## Pressure-tests

См. `./pressure-tests.md` — 4 RED-сценария попыток обхода BLOCKER'а.

## Связь с spec

- spec § 3.3 — описание скилла
- spec § 6.1 — описание tools/consistency_check.py
- spec § 8.1 шаг 8 — место в Потоке A
- spec § 9.5 — critical failures (consistency red)
- D-002 P-10 — pressure-tests формулировка
