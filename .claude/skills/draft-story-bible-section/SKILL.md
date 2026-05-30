---
name: draft-story-bible-section
description: "Creative + дивергентная generation (R-1). Создание секций story-bible/ через 3 ПОСЛЕДОВАТЕЛЬНЫЕ «шляпы» (P-2) в orchestrator-сессии шоураннера: LORE-dominant pass → PHILOSOPHY-dominant pass → CHARACTER-dominant pass. НЕ через параллельные Task-вызовы (инвариант § 8.3.1: шоураннер — единственный writer). Между шляпами — context-marker или /clear. Шоураннер собирает 3 варианта, синтезирует. Затем обязательный adversarial-review-pass."
pressure_tested:
  status: no
id: draft-story-bible-section
version: 1
status: draft
references:
  - "docs/specs/2026-05-24-infrastructure-and-skills-design.md § 3.3 § 8.1 § 8.3.1"
  - "decisions/D-002-spec-corrections-and-golden-plan.md P-2 P-12"
---

# Draft Story Bible Section

Creative skill с **дивергентной generation (R-1)** через 3 последовательные шляпы в orchestrator-сессии. Создаёт секции `story-bible/` (thesis.md, world-rules.md, conflict-register.md, etc.).

## Когда использовать

- Создаёшь новую секцию story-bible (тезис, правила мира, регистр конфликтов).
- Обновляешь существующую секцию по результату изменений в characters/, scenes/.

## Что делает (R-1, P-2)

### 1. Calibration

Прочитай:
- `story-bible/` (существующее) — что уже есть
- `CLAUDE.md` законы проекта
- `golden/theses/` (primary_category + secondary с весом 0.5 per P-12)
- `golden/scenes/` примеры если уместно

### 2. 3 последовательные шляпы (P-2)

**Шляпа A — LORE-dominant pass:**
- Стартовый промпт: «Правила мира первичны. Я пишу секцию исходя из того, что технические/корп/политические механизмы — конструирующие, философия и характер вторичны.»
- Драфт ~150-300 слов

**Context-marker между шляпами:**

> «Сейчас я возвращаюсь к другому уклону. Предыдущий draft был LORE-dominant. Следующий — PHILOSOPHY-dominant.»

(Или `/clear` если эффективно — за счёт re-чтения базовых файлов.)

**Шляпа B — PHILOSOPHY-dominant pass:**
- Стартовый промпт: «Центральный тезис первичен. Мир и характеры — иллюстративная среда для тезиса.»
- Драфт ~150-300 слов

**Context-marker.**

**Шляпа C — CHARACTER-dominant pass:**
- Стартовый промпт: «Архетип/конфликт первичен. Тезис и мир — последствия того, что люди делают.»
- Драфт ~150-300 слов

### 3. Synthesis

Шоураннер:
- Рассматривает 3 варианта
- **Явно выбирает** один как основу ИЛИ **синтезирует** новый из частей трёх
- Записывает результат в `story-bible/<section>.md`
- В frontmatter: `references: [primary golden files used, ...]`

### 4. Обязательный adversarial-review-pass

Сразу после synthesis: invoke `.claude/skills/adversarial-review-pass/SKILL.md` (НЕ откладывая).

## Что НЕ делает

- **НЕ использует параллельные Task-вызовы для R-1** (P-2: «шоураннер — единственный writer» § 8.3.1).
- **НЕ пропускает adversarial-review-pass** после synthesis.
- **НЕ замещает brainstorming** для развилок выше уровня секции (для развилок типа «какой жанр?» используй Superpowers `brainstorming` напрямую).

## Связанные артефакты

- `golden/theses/` — primary калибровочный материал
- `golden/scenes/` — secondary
- `.claude/skills/adversarial-review-pass/SKILL.md` — обязательный downstream
- Superpowers `brainstorming` — upstream для развилок выше

## Pressure-tests

Не применимо. `pressure_tested: status: no` (creative).

## Связь с spec

- spec § 3.3 — описание скилла
- spec § 8.1 шаг 2 — R-1 шляпы в Потоке A
- spec § 8.3.1 — инвариант «шоураннер — единственный writer»
- D-002 P-2 — последовательные шляпы, не параллельные субагенты
- D-002 P-12 — primary + secondary categories
