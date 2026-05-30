---
name: writing-narrative-skills
description: "Мета-скилл авторинга нарративных скиллов в Auto-ai-series. Адаптирует Superpowers writing-skills: для discipline-BLOCKER скиллов в нарративном домене (voice-check, consistency-check, evidence-before-action) обязателен pressure-testing — минимум 3 RED-сценария + frontmatter pressure_tested: status: yes."
lineage:
  origin: derived
  source: "obra/superpowers@f2cbfbef:skills/writing-skills/SKILL.md"
  ref: "meta-skills/superpowers-references/writing-skills/SKILL.md"
  adapted_on: 2026-05-30
  changes:
    - "Scope: с code-skills расширено на нарративные discipline-BLOCKER скиллы"
    - "Обязательное pressure-testing для скиллов с императивами refuse/block/stop"
    - "Минимум 3 RED-сценария в pressure-tests.md (per spec § 9.5)"
    - "Frontmatter pressure_tested: status: yes + scenarios_file + validated_on"
    - "P-10 формулировка: «RED обошёл скилл» = провал (т.е. дисциплина НЕ сработала)"
pressure_tested:
  status: no
# Bridge-поля для frontmatter_validator.py:
id: writing-narrative-skills
version: 1
status: draft
references:
  - "docs/specs/2026-05-24-infrastructure-and-skills-design.md § 3.2 § 7"
  - "meta-skills/superpowers-references/writing-skills/SKILL.md"
---

# Writing Narrative Skills

Мета-скилл авторинга **наших собственных** нарративных скиллов в `.claude/skills/`. Развивает Superpowers `writing-skills` под специфику discipline-BLOCKER скиллов в нарративном домене (Auto-ai-series).

## Когда использовать

- Создаёшь новый скилл в `.claude/skills/` который проверяет / блокирует / отказывает (BLOCKER-семантика).
- Адаптируешь существующий Superpowers скилл через lineage и хочешь добавить нарративные правила.
- Pressure-tested существующий скилл нужно расширить новыми RED-сценариями (например, после первого smoke-test обнаружился обход).

## Что делает

1. **Frontmatter:** валидирует наличие `name`, `description`, `pressure_tested.status` (yes для discipline; no для creative/orchestration).
2. **Body структура (обязательно):**
   - Когда использовать
   - Что делает
   - Что НЕ делает (boundaries)
   - Связанные артефакты
   - Pressure-tests (для discipline-BLOCKER)
3. **Pressure-testing (для discipline-BLOCKER):**
   - Минимум 3 RED-сценария в `<skill>/pressure-tests.md`
   - Каждый RED: триггер обхода + ожидаемое поведение скилла + проверка
   - **P-10 acceptance:** если RED-сценарий ОБОШЁЛ скилл (дисциплина не сработала) — пресс-тест провален, скилл не имеет права получить `pressure_tested: status: yes`.
4. **Lineage (если адаптируется):**
   - `source:` указывает SHA + path в upstream
   - `ref:` указывает локальную pinned копию в `meta-skills/superpowers-references/`
   - `changes:` перечисляет КОНКРЕТНЫЕ адаптации на русском
   - `adapted_on:` дата адаптации

## Что НЕ делает

- **НЕ заменяет Superpowers writing-skills для не-нарративных скиллов** (для code-skills используй upstream напрямую).
- **НЕ требует pressure-testing для creative / orchestration скиллов** (creative: draft-* семейство; orchestration: adversarial-review-pass, add-golden-example) — там разные acceptance criteria.
- **НЕ автоматизирует pressure-testing** — это ручной процесс шоураннера + orchestrator, не CI.

## Связанные артефакты

- `meta-skills/superpowers-references/writing-skills/SKILL.md` — pinned source
- `.claude/skills/evidence-before-action/SKILL.md` — образец lineage + pressure-tested
- `.claude/skills/consistency-check/SKILL.md` — образец scratch + pressure-tested
- `.claude/skills/voice-check/SKILL.md` — образец scratch + pressure-tested + tool integration

## Pressure-tests

Не применимо — `writing-narrative-skills` не discipline-BLOCKER. `pressure_tested: status: no` в frontmatter.

## Связь с spec

- spec § 3.2 — адаптация writing-skills с pressure-testing требованием
- spec § 7 — lineage workflow
- spec § 9.5 — pressure-tests RED acceptance (P-10 переформулировано)
- D-002 P-1 / P-10 — pressure-tests как часть acceptance
