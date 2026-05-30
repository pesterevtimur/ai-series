---
name: draft-character-sheet
description: "Creative + дивергентная generation (R-1). Создание character-sheets через 3 ПОСЛЕДОВАТЕЛЬНЫЕ «шляпы» (P-2) в orchestrator-сессии шоураннера: CHARACTER-dominant pass («декларируемая ценность + incentive») → CONFLICT-dominant pass («где сильнейшее столкновение incentives») → PHILOSOPHY-dominant pass («позиция по ИИ в её сильнейшей формулировке»). НЕ через параллельные Task-вызовы (инвариант § 8.3.1). Между шляпами — context-marker или /clear. Шоураннер синтезирует, затем обязательный adversarial-review-pass."
pressure_tested:
  status: no
id: draft-character-sheet
version: 1
status: draft
references:
  - "docs/specs/2026-05-24-infrastructure-and-skills-design.md § 3.3 § 8.1 § 8.3.1"
  - "decisions/D-002-spec-corrections-and-golden-plan.md P-2 P-12"
---

# Draft Character Sheet

Creative skill с **дивергентной generation (R-1)** через 3 последовательные шляпы в orchestrator-сессии. Создаёт character-sheets в `characters/<id>.md`.

## Когда использовать

- Создаёшь нового персонажа в `characters/`.
- Обновляешь существующий character-sheet по результату событий в scenes/.

## Что делает (R-1, P-2)

### 1. Calibration

Прочитай:
- `story-bible/thesis.md` + `story-bible/world-rules.md` — каркас, в который персонаж встраивается
- `CLAUDE.md` законы проекта
- `golden/characters/` (primary) — Carmela, Peggy, Fleabag, Nora, Kim, Shiv, BoJack (диверсификация архетипов)
- `golden/conflicts/` + `golden/theses/` (secondary с весом 0.5 per P-12) — для понимания взаимосвязи character ↔ конфликт ↔ тезис

### 2. 3 последовательные шляпы (P-2)

**Шляпа A — CHARACTER-dominant pass:**
- Стартовый промпт: «Декларируемая ценность + incentive. Я пишу sheet исходя из того, что внутреннее противоречие персонажа первично: что он говорит, что реально движет, где разрыв.»
- Драфт ~200-400 слов

**Context-marker между шляпами:**

> «Сейчас я возвращаюсь к другому уклону. Предыдущий draft был CHARACTER-dominant. Следующий — CONFLICT-dominant.»

(Или `/clear` если эффективно — за счёт re-чтения базовых файлов.)

**Шляпа B — CONFLICT-dominant pass:**
- Стартовый промпт: «Где сильнейшее столкновение incentives. Персонаж определяется не своими чертами, а тем, с кем и за что он реально конфликтует — какие интересы несовместимы.»
- Драфт ~200-400 слов

**Context-marker.**

**Шляпа C — PHILOSOPHY-dominant pass:**
- Стартовый промпт: «Позиция по ИИ в её сильнейшей формулировке. Персонаж — воплощение interlocking тезиса: его сильнейший аргумент в проекте, не его слабая версия.»
- Драфт ~200-400 слов

### 3. Synthesis

Шоураннер:
- Рассматривает 3 варианта
- **Явно выбирает** один как основу ИЛИ **синтезирует** новый из частей трёх
- Записывает результат в `characters/<id>.md`
- В frontmatter: `references: [thesis, world-rules, primary golden characters used, ...]`

### 4. Обязательный adversarial-review-pass

Сразу после synthesis: invoke `.claude/skills/adversarial-review-pass/SKILL.md` (НЕ откладывая).

A2 character-truth-keeper особенно: ловит «декларация = character» (cwhat шляпа A показывает декларации — нужно что A2 проверил что они подкреплены действиями в самом sheet'е).

## Что НЕ делает

- **НЕ использует параллельные Task-вызовы для R-1** (P-2: «шоураннер — единственный writer» § 8.3.1).
- **НЕ пропускает adversarial-review-pass** после synthesis.
- **НЕ замещает brainstorming** для развилок выше уровня персонажа (типа «какой архетип брать?»).

## Связанные артефакты

- `golden/characters/` — primary калибровочный материал
- `golden/conflicts/` + `golden/theses/` — secondary
- `.claude/skills/adversarial-review-pass/SKILL.md` — обязательный downstream
- `.claude/agents/character-truth-keeper.md` — A2 как основной критик character-sheet

## Pressure-tests

Не применимо. `pressure_tested: status: no` (creative).

## Связь с spec

- spec § 3.3 — описание скилла
- spec § 8.1 шаг 2 — R-1 шляпы в Потоке A
- spec § 8.3.1 — инвариант «шоураннер — единственный writer»
- D-002 P-2 — последовательные шляпы, не параллельные субагенты
- D-002 P-12 — primary + secondary categories
