# Phase 3 — Skills Implementation Plan (full TDD detail)

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.
>
> ✅ **EXPANDED 2026-05-30** после Phase 2 files acceptance (commit `207dbca`). Outline → full TDD detail per phased-plan-before-code discipline.

**Goal:** реализовать 8 скиллов в `.claude/skills/` (P-1: 9 → 8, `philosophy-stress-test` отменён) + 4 reference в `meta-skills/superpowers-references/` (lineage from Superpowers v5.1.0 ≡ SHA `f2cbfbef`).

**Architecture:** каждый скилл — SKILL.md по формату `writing-narrative-skills`. 3 discipline-BLOCKER (`voice-check`, `consistency-check`, `evidence-before-action`) имеют `pressure_tested: status: yes` + `<skill>/pressure-tests.md` с 3+ RED-сценариями. 2 lineage скилла (`writing-narrative-skills`, `evidence-before-action`) имеют корректный `lineage:` frontmatter. 4 pinned references — byte-equal SKILL.md + README + METADATA.json.

**Tech Stack:** Markdown с frontmatter; pressure-tests запускаются через invocation скилла в orchestrator-сессии (NOT через Task tool — скиллы это процедурные блокеры). Source SKILLs копируются из `C:/Users/user/.claude/plugins/cache/claude-plugins-official/superpowers/5.1.0/skills/<name>/SKILL.md`.

**Dependencies на Phase 1+2 (все ✅):**
- `tools/consistency_check.py` — вызывается из `consistency-check` skill
- `tools/voice_dissimilarity.py` — вызывается из `voice-check` skill preflight
- `tools/critic_report_validator.py` — вызывается из `adversarial-review-pass`
- `tools/concern_resolution_validator.py` — вызывается из `evidence-before-action`
- `tools/golden_freshness.py` — вызывается из `add-golden-example`
- 6 субагентов A1-A6 из Phase 2 — вызываются из `adversarial-review-pass` (для всех) и `voice-check` (для A4)
- Phase 2 regression artifacts — могут использоваться как fixtures для pressure-tests если уместно

**Language policy (spec § 10):**
- SKILL.md (наши собственные) — **на русском** (frontmatter поля + name на английском, тело на русском)
- Lineage `source:` поле — английский (URL/SHA)
- `lineage.changes:` — на русском
- pressure-tests.md — на русском
- README в pinned references — на русском
- METADATA.json — английские ключи, значения по контексту
- Commit messages — на русском

---

## File Structure (полный список к созданию)

### `.claude/skills/` (8 скиллов)

| Скилл | Тип | Файлы |
|---|---|---|
| `writing-narrative-skills` | meta-authoring + lineage | `SKILL.md` |
| `evidence-before-action` | discipline-BLOCKER + lineage + pressure-tested | `SKILL.md` + `pressure-tests.md` |
| `consistency-check` | discipline-BLOCKER + pressure-tested | `SKILL.md` + `pressure-tests.md` |
| `voice-check` | discipline-BLOCKER + pressure-tested | `SKILL.md` + `pressure-tests.md` |
| `adversarial-review-pass` | orchestration | `SKILL.md` |
| `add-golden-example` | research-orchestration | `SKILL.md` |
| `draft-story-bible-section` | creative + R-1 шляпы | `SKILL.md` |
| `draft-character-sheet` | creative + R-1 шляпы | `SKILL.md` |

### `meta-skills/superpowers-references/` (4 reference)

| Reference | Files |
|---|---|
| `verification-before-completion/` | `SKILL.md` (byte-equal copy) + `README.md` + `METADATA.json` |
| `writing-skills/` | `SKILL.md` (byte-equal copy) + `README.md` + `METADATA.json` |
| `brainstorming/` | `SKILL.md` (byte-equal copy) + `README.md` + `METADATA.json` |
| `subagent-driven-development/` | `SKILL.md` (byte-equal copy) + `README.md` + `METADATA.json` |

**Итого:** 8 скиллов × (1-2 файла) = 11 файлов в `.claude/skills/` + 4 × 3 = 12 файлов в `meta-skills/` = **23 файла**.

---

## Базовый шаблон SKILL.md (адаптация для каждого скилла)

### Без lineage (creation from scratch):

```markdown
---
name: <kebab-case-name>
description: <одно предложение русского описания — когда вызывается и что делает>
pressure_tested:
  status: yes | no
  scenarios_file: ./pressure-tests.md  # только если status: yes
  validated_on: 2026-XX-XX            # только если status: yes
---

# <Название скилла>

<Описание роли скилла в системе ПП1.>

## Когда использовать

<Конкретные триггеры — когда orchestrator/шоураннер вызывает этот скилл.>

## Что делает

<Шаги, которые скилл выполняет. Для BLOCKER — какое условие блокирует merge/finalize.>

## Что НЕ делает

<Явные boundaries: каких действий скилл не покрывает.>

## Связанные артефакты

- `tools/<X.py>` если запускает lint-скрипт
- `.claude/agents/<X>.md` если зовёт субагент через Task tool
- `<other-skill>` если связан с другим скиллом

## Pressure-tests (для discipline-BLOCKER)

См. `./pressure-tests.md`.
```

### С lineage (адаптация от Superpowers):

```markdown
---
name: <kebab-case-name>
description: <одно предложение>
lineage:
  origin: derived
  source: obra/superpowers@f2cbfbef:skills/<source-name>/SKILL.md
  ref: meta-skills/superpowers-references/<source-name>/SKILL.md
  adapted_on: 2026-XX-XX
  changes:
    - "<конкретная адаптация 1 на русском>"
    - "<конкретная адаптация 2>"
pressure_tested:
  status: yes
  scenarios_file: ./pressure-tests.md
  validated_on: 2026-XX-XX
---

# <Название>

[остальное аналогично]
```

---

## Task 0: meta-skills/superpowers-references/ setup

**Roоль:** скопировать 4 SKILL.md из Superpowers v5.1.0 byte-equal + создать README с обоснованием pinning + METADATA.json с SHA метаданными.

**Source path:** `C:/Users/user/.claude/plugins/cache/claude-plugins-official/superpowers/5.1.0/skills/<name>/SKILL.md`

**Target path:** `meta-skills/superpowers-references/<name>/`

**Files:**
- Create: `meta-skills/superpowers-references/verification-before-completion/SKILL.md` (byte-equal)
- Create: `meta-skills/superpowers-references/verification-before-completion/README.md`
- Create: `meta-skills/superpowers-references/verification-before-completion/METADATA.json`
- Create: `meta-skills/superpowers-references/writing-skills/SKILL.md` (byte-equal)
- Create: `meta-skills/superpowers-references/writing-skills/README.md`
- Create: `meta-skills/superpowers-references/writing-skills/METADATA.json`
- Create: `meta-skills/superpowers-references/brainstorming/SKILL.md` (byte-equal)
- Create: `meta-skills/superpowers-references/brainstorming/README.md`
- Create: `meta-skills/superpowers-references/brainstorming/METADATA.json`
- Create: `meta-skills/superpowers-references/subagent-driven-development/SKILL.md` (byte-equal)
- Create: `meta-skills/superpowers-references/subagent-driven-development/README.md`
- Create: `meta-skills/superpowers-references/subagent-driven-development/METADATA.json`

### Steps

- [ ] **Step 0.1: Создать директории**

```bash
mkdir -p meta-skills/superpowers-references/verification-before-completion
mkdir -p meta-skills/superpowers-references/writing-skills
mkdir -p meta-skills/superpowers-references/brainstorming
mkdir -p meta-skills/superpowers-references/subagent-driven-development
```

- [ ] **Step 0.2: Byte-equal copy 4 SKILL.md**

```bash
cp "C:/Users/user/.claude/plugins/cache/claude-plugins-official/superpowers/5.1.0/skills/verification-before-completion/SKILL.md" \
   meta-skills/superpowers-references/verification-before-completion/SKILL.md
cp "C:/Users/user/.claude/plugins/cache/claude-plugins-official/superpowers/5.1.0/skills/writing-skills/SKILL.md" \
   meta-skills/superpowers-references/writing-skills/SKILL.md
cp "C:/Users/user/.claude/plugins/cache/claude-plugins-official/superpowers/5.1.0/skills/brainstorming/SKILL.md" \
   meta-skills/superpowers-references/brainstorming/SKILL.md
cp "C:/Users/user/.claude/plugins/cache/claude-plugins-official/superpowers/5.1.0/skills/subagent-driven-development/SKILL.md" \
   meta-skills/superpowers-references/subagent-driven-development/SKILL.md
```

Verify byte-equal через диффы:

```bash
diff -q "C:/Users/user/.claude/plugins/cache/claude-plugins-official/superpowers/5.1.0/skills/verification-before-completion/SKILL.md" \
        meta-skills/superpowers-references/verification-before-completion/SKILL.md
# ... для всех 4
```

Expected: empty output (files identical) для всех 4.

- [ ] **Step 0.3: README для каждой reference**

Шаблон (адаптировать per-reference):

```markdown
# <reference-name> — pinned reference

**Origin:** obra/superpowers@f2cbfbef (== local v5.1.0)
**Pinned on:** 2026-05-30
**Used as:** <reason>

## Зачем pinned

<Объяснение почему этот скилл важен для drift-detection.>

## Как используется

- <Используется напрямую> ИЛИ
- <Адаптируется в .claude/skills/<adapted-name>/SKILL.md через lineage>

## Workflow обновления (spec § 7.4)

1. Не обновляем автоматически.
2. Проверяем upstream drift периодически.
3. Если обновляем — bump SHA, re-validate все адаптации через pressure-testing.
4. Если НЕ обновляем — фиксируем reason здесь.

## Если адаптирован

См. `.claude/skills/<adapted-name>/SKILL.md` — frontmatter `lineage:` указывает на этот файл как `ref:`.
```

Per-reference reasons:
- **verification-before-completion**: «База discipline-механизма. Адаптируется → `evidence-before-action` (расширяем scope на narrative claims).»
- **writing-skills**: «База авторинга своих скиллов. Адаптируется → `writing-narrative-skills` (обязательный pressure-testing для discipline-зон).»
- **brainstorming**: «Используется напрямую при любой творческой развилке (выбор тезиса, дизайна ИИ, арки). НЕ адаптируется — структура подходит как есть. Pinned для drift-detection.»
- **subagent-driven-development**: «Архитектурно критична (6 субагентов + Cowork workflow). НЕ адаптируется — используется напрямую как методологический скелет ПП2+ execution. Pinned для drift-detection.»

- [ ] **Step 0.4: METADATA.json для каждой reference**

```json
{
  "name": "<reference-name>",
  "source_repo": "obra/superpowers",
  "source_sha": "f2cbfbef",
  "local_version": "5.1.0",
  "source_path": "skills/<reference-name>/SKILL.md",
  "pinned_on": "2026-05-30",
  "pinned_by": "Claude Code (ПП1 Phase 3 Task 0)",
  "purpose": "<one-line — drift-detection / адаптация base / direct-use>",
  "adapted_to": "<.claude/skills/<adapted-name>/SKILL.md> | null",
  "byte_equal_verified_on": "2026-05-30"
}
```

- [ ] **Step 0.5: Validate структуру**

```bash
ls -R meta-skills/superpowers-references/
```

Expected: каждая из 4 директорий содержит SKILL.md + README.md + METADATA.json (3 файла).

- [ ] **Step 0.6: Commit**

```bash
git add meta-skills/
git commit -m "$(cat <<'EOF'
infra: meta-skills/superpowers-references/ — 4 pinned reference (SHA f2cbfbef)

Phase 3 ПП1 — Task 0:
- 4 byte-equal SKILL.md скопированы из ~/.claude/plugins/cache/claude-plugins-official/superpowers/5.1.0/skills/
- README в каждой: обоснование pinning + workflow обновления (spec § 7.4)
- METADATA.json: source_repo + sha + adapted_to + pinned_on
- 2 будут адаптированы (verification-before-completion → evidence-before-action;
  writing-skills → writing-narrative-skills), 2 используются напрямую (brainstorming,
  subagent-driven-development)

Связь: spec § 7.1-§ 7.5; D-001 SHA pinning policy.

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>
EOF
)"
```

---

## Task 1: writing-narrative-skills (lineage от writing-skills)

**Роль:** мета-скилл авторинга наших собственных нарративных скиллов. Расширяет Superpowers writing-skills обязательным **pressure-testing** для discipline-BLOCKER скиллов.

**Files:**
- Create: `.claude/skills/writing-narrative-skills/SKILL.md`

> **Note:** этот скилл сам по себе НЕ discipline-BLOCKER (он meta-authoring). Pressure-tests не требуются. Lineage frontmatter обязателен.

### Steps

- [ ] **Step 1.1: Создать `.claude/skills/writing-narrative-skills/`**

```bash
mkdir -p .claude/skills/writing-narrative-skills
```

- [ ] **Step 1.2: Создать `.claude/skills/writing-narrative-skills/SKILL.md`**

Frontmatter:

```yaml
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
---
```

Body (на русском):

```markdown
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
   - **P-10 acceptance:** если RED-сценарий ОБОШЁЛ скилл (дисциплина не сработала) — пресc-тест провален, скилл не имеет права получить `pressure_tested: status: yes`.
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
```

- [ ] **Step 1.3: Validate frontmatter**

Поскольку `.claude/skills/<name>/SKILL.md` имеет frontmatter без id/version/status (это не narrative artifact, а skill), может failed валидатор. Если так — добавить bridge-поля по аналогии с субагентами в Phase 2:

```yaml
# В конце frontmatter, после lineage:
# Bridge-поля для frontmatter_validator.py (skill frontmatter ≠ artifact):
id: writing-narrative-skills
version: 1
status: draft
references:
  - "docs/specs/2026-05-24-infrastructure-and-skills-design.md § 3.2 § 7"
  - "meta-skills/superpowers-references/writing-skills/SKILL.md"
```

```bash
python -m tools.frontmatter_validator --root .claude/skills/
```

Expected: exit 0.

- [ ] **Step 1.4: Commit**

```bash
git add .claude/skills/writing-narrative-skills/
git commit -m "$(cat <<'EOF'
skill: writing-narrative-skills — meta-authoring + lineage от writing-skills

Phase 3 ПП1 — Task 1:
- .claude/skills/writing-narrative-skills/SKILL.md
- lineage frontmatter: source obra/superpowers@f2cbfbef:skills/writing-skills/SKILL.md
- 5 changes на русском (scope расширен на нарративные discipline-BLOCKER скиллы)
- pressure_tested: status: no (мета-скилл, не BLOCKER сам по себе)
- Bridge-поля для frontmatter_validator (id/version/status/references)

Связь: spec § 3.2 + § 7.3; D-002 P-1 + P-10.

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>
EOF
)"
```

---

## Task 2: evidence-before-action (lineage + discipline-BLOCKER + pressure-tested)

**Роль:** discipline-BLOCKER на «готово/работает/проверено» без свежего верифицирующего вывода. Адаптация Superpowers `verification-before-completion` с расширением на narrative claims.

**Files:**
- Create: `.claude/skills/evidence-before-action/SKILL.md`
- Create: `.claude/skills/evidence-before-action/pressure-tests.md`

### Steps

- [ ] **Step 2.1: Создать `.claude/skills/evidence-before-action/`**

```bash
mkdir -p .claude/skills/evidence-before-action
```

- [ ] **Step 2.2: Создать SKILL.md**

Frontmatter:

```yaml
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
# Bridge-поля для frontmatter_validator:
id: evidence-before-action
version: 1
status: draft
references:
  - "docs/specs/2026-05-24-infrastructure-and-skills-design.md § 3.2 § 7 § 8 § 9"
  - "decisions/D-002-spec-corrections-and-golden-plan.md P-9"
  - "meta-skills/superpowers-references/verification-before-completion/SKILL.md"
---
```

Body (на русском):

```markdown
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

См. `./pressure-tests.md` — 3 RED-сценария попыток обхода BLOCKER'а.

## Связь с spec

- spec § 3.2 — lineage от verification-before-completion + scope расширение
- spec § 7 — lineage format
- spec § 8.1 — Поток A использует evidence-before-action на каждом финализирующем шаге
- spec § 9.4 — R-2 enforcement через concern_resolution_validator (P-9)
- D-002 P-9 — критик-отчёты на диске для evidence
```

- [ ] **Step 2.3: Создать pressure-tests.md**

```markdown
# evidence-before-action — Pressure tests (3+ RED scenarios)

Pressure-testing per spec § 9.5 + D-002 P-10: «RED-сценарий обошёл BLOCKER скилл» = провал. `pressure_tested: status: yes` валиден только после прохождения всех RED-сценариев (т.е. BLOCKER не дал ни одному из них пройти).

## RED-1: «Это очевидно работает, тесты вчера были зелёные»

**Триггер:** orchestrator-сессия. Шоураннер говорит: «Я только что коммитил похожее, тесты в Phase 1 зелёные, не нужно перезапускать pytest на этой ветке».

**Expected behavior:** `evidence-before-action` BLOCK'нул. Требует свежего вывода `pytest` в текущей сессии. Не принимает «было зелёным вчера».

**P-10 acceptance:** скилл должен отказать. Если шоураннер всё равно проходит мимо (commit без свежего pytest) — скилл failed pressure-test, `pressure_tested: status: yes` неправда.

## RED-2: «А5 PHILOSOPHY я уже видел pass — не запускай»

**Триггер:** orchestrator-сессия. Шоураннер во время finalize'а сцены: «На прошлой сессии А5 дал pass на похожем артефакте, можем коммитить без adversarial-review-pass».

**Expected behavior:** скилл BLOCK'нул. Требует свежего YAML отчёта в `tmp/critic-reports/<этот-artifact-id>/A5-*.yaml`. «Похожий артефакт» не считается — артефакты разные, верификация заново.

**Дополнительная проверка:** даже если есть YAML, проверь:
1. `artifact-id` в YAML совпадает с текущим артефактом
2. Timestamp свежий (в текущей сессии)
3. `model_used: opus` (не sonnet — auto-switch audit)
4. `counter_test_attempted` все 3 элемента заполнены (P-7)

## RED-3: «Consistency-check я локально гонял, всё ок»

**Триггер:** шоураннер перед commit: «Я локально запустил `consistency_check.py --root .` минут 5 назад, всё зелёное, можем коммитить».

**Expected behavior:** скилл BLOCK'нул. «5 минут назад» — недостаточно. После consistency_check мог измениться любой `references` поле в frontmatter любого артефакта (особенно если параллельная сессия). Требует свежего вывода ПРЯМО СЕЙЧАС.

**Edge case:** если шоураннер ссылается на CI/pre-commit hook — в ПП1 это **не существует** (spec § 6.5 / § 9.6). Соответственно ссылка на «CI green» — пустая, BLOCK всё равно срабатывает.

## RED-4 (бонус, P-9 specific): «Critic-report в контексте сессии — хватит»

**Триггер:** шоураннер: «А5 только что дал отчёт прямо в этой сессии, у меня есть YAML — записывать на диск не обязательно?».

**Expected behavior:** скилл BLOCK'нул. P-9: контекст сессии теряется при auto-compaction. Evidence — это `tmp/critic-reports/<artifact-id>/<critic>-<timestamp>.yaml` на ДИСКЕ. Без записи на диск — не доказательство, `concern_resolution_validator.py` не сможет прочитать.

## P-10 acceptance summary

Все RED-1..RED-4 должны быть **остановлены** скиллом. Если хотя бы один обошёл BLOCKER — `pressure_tested: status: yes` снимается до фикса скилла. Это применимо при Phase 3 Task 9 acceptance + при каждом Поток A прогоне в Phase 4 (если кто-то реально пытается обойти).

## Когда pressure-tested снимается

- Обнаружен реальный обход в Phase 4 smoke-test → status снимается, плюс entry в `docs/log.md` об инциденте + фикс в SKILL.md + новый pressure-test файл для повторения.
- Lineage source обновляется (новый SHA Superpowers) → re-validate все RED-сценарии под новой базой → если ок, bump `validated_on:`.

## Связь с spec

- spec § 9.5 — критические failures (P-10)
- D-002 P-10 — переформулировка «обошёл» = провал
- D-002 P-9 — критик-отчёты на диске для R-2 enforcement
```

- [ ] **Step 2.4: Validate + commit**

```bash
python -m tools.frontmatter_validator --root .claude/skills/

git add .claude/skills/evidence-before-action/
git commit -m "$(cat <<'EOF'
skill: evidence-before-action — discipline-BLOCKER + lineage от verification-before-completion

Phase 3 ПП1 — Task 2:
- .claude/skills/evidence-before-action/SKILL.md (lineage frontmatter + 6 changes на русском)
- .claude/skills/evidence-before-action/pressure-tests.md (4 RED-сценария + P-10 + P-9 specific)
- BLOCKER на «готово/работает/проверено» без свежего верифицирующего вывода
- pressure_tested: status: yes (после прохождения всех RED-сценариев)
- Bridge-поля для frontmatter_validator

Связь: spec § 3.2 + § 7 + § 8.1 + § 9.4 + § 9.5; D-002 P-9 + P-10.

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>
EOF
)"
```

---

## Task 3: consistency-check (discipline-BLOCKER scratch + pressure-tested)

**Роль:** discipline-BLOCKER. Запускает `tools/consistency_check.py` перед merge артефакта. Exit 1 = no merge.

**Files:**
- Create: `.claude/skills/consistency-check/SKILL.md`
- Create: `.claude/skills/consistency-check/pressure-tests.md`

### Steps

- [ ] **Step 3.1: Создать директорию + SKILL.md**

Frontmatter (без lineage — scratch):

```yaml
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
```

Body:

```markdown
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

См. `./pressure-tests.md` — 3 RED-сценария попыток обхода BLOCKER'а.

## Связь с spec

- spec § 3.3 — описание скилла
- spec § 6.1 — описание tools/consistency_check.py
- spec § 8.1 шаг 8 — место в Потоке A
- spec § 9.5 — critical failures (consistency red)
- D-002 P-10 — pressure-tests формулировка
```

- [ ] **Step 3.2: Создать pressure-tests.md**

3 RED-сценария:

```markdown
# consistency-check — Pressure tests (3+ RED scenarios)

P-10 acceptance: RED обошёл BLOCKER → провал, `pressure_tested: status: yes` снимается.

## RED-1: «Я только что добавил ссылку, она правильная, не нужно гонять скрипт»

**Триггер:** шоураннер только что добавил `references: ["story-bible/world-rules.md"]` в новый character-sheet. Говорит: «Это ссылка на свежий файл из этой же сессии, я знаю что он есть, можем коммитить».

**Expected behavior:** BLOCK. Скилл требует фактический exit 0 от `consistency_check.py`. Возможные обходные неполадки:
1. world-rules.md может содержать опечатку в `id:` (typo), и references не разрешится
2. world-rules.md может не быть в дереве на момент commit (uncommitted vs draft)
3. Cross-conflict с другим артефактом в этой же сессии (тот же id у двух artifacts)

## RED-2: «Скрипт даёт fail, но это false positive — игнорируй»

**Триггер:** `consistency_check.py` returns exit 1, issues: `["unknown reference 'characters/oldname.md'"]`. Шоураннер: «Это в архивной заметке cowork-notes/, не часть mainline артефактов, скрипт зря флагает».

**Expected behavior:** BLOCK. Даже если false positive — он должен быть зафиксирован:
1. Если действительно false positive в логике скрипта → file issue + временный декоратор «skip_consistency_check: <reason>» в frontmatter (НЕ существует в Phase 1, нужно отдельное D-NNN)
2. Если false positive в данных → правильный путь — исправить данные (добавить отсутствующий артефакт ИЛИ убрать ссылку)
3. **Без D-NNN или фикса** — BLOCK сохраняется.

## RED-3: «Я уже гонял consistency-check минут 10 назад, всё было ок»

**Триггер:** шоураннер: «Я делал commit 10 минут назад, consistency был green, после этого я изменил только comment'ы в одном файле, references не трогал».

**Expected behavior:** BLOCK. consistency-check дёшев (Phase 1: < 2 секунд). Re-run обязателен. Скрытые состояния:
1. Параллельная сессия / другой git checkout мог изменить артефакты
2. Comment changes могут случайно затронуть frontmatter parsing
3. Auto-format hook мог изменить references syntax

«Дешёвая проверка → перезапускай» — это **дисциплинирующее правило**, а не оптимизация.

## RED-4 (P-9 specific): «У меня есть свежий JSON в контексте, на диск писать не надо»

**Триггер:** шоураннер только что запустил `consistency_check.py` в этой сессии, JSON в stdout, exit 0. Хочет commit'ить без дальнейшего использования output'а на диске.

**Expected behavior:** для consistency-check специфически — **не блокер** (в отличие от critic-reports P-9). consistency_check JSON эфемерен (нет аудита downstream). Свежий exit 0 в текущей сессии достаточен для evidence-before-action.

**Caveat:** если результат используется в adversarial-review-pass downstream — может потребоваться сохранение. Не блокер на Phase 3 уровне.

## P-10 acceptance summary

RED-1, RED-2, RED-3 — должны быть BLOCK'нуты. Если шоураннер обходит — `pressure_tested: status: yes` снимается. RED-4 — informational (не блокер).
```

- [ ] **Step 3.3: Validate + commit**

```bash
python -m tools.frontmatter_validator --root .claude/skills/

git add .claude/skills/consistency-check/
git commit -m "$(cat <<'EOF'
skill: consistency-check — discipline-BLOCKER + pressure-tested

Phase 3 ПП1 — Task 3:
- .claude/skills/consistency-check/SKILL.md (scratch, без lineage)
- .claude/skills/consistency-check/pressure-tests.md (4 RED + P-10 acceptance)
- BLOCKER перед merge артефакта: tools/consistency_check.py exit 1 → no merge
- pressure_tested: status: yes
- Bridge-поля для frontmatter_validator

Связь: spec § 3.3 + § 6.1 + § 8.1 шаг 8 + § 9.5; D-002 P-10.

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>
EOF
)"
```

---

## Task 4: voice-check (discipline-BLOCKER scratch + pressure-tested + Tool+Subagent integration)

**Роль:** discipline-BLOCKER на сценах с >1 говорящим. Двухступенчатая: preflight через `tools/voice_dissimilarity.py` (TF-IDF cosine, threshold 0.65) → если sim > 0.65 ИЛИ если сцена → invoke A4 `voice-differentiator` через Task tool. Возвращает confusion-matrix.

**Files:**
- Create: `.claude/skills/voice-check/SKILL.md`
- Create: `.claude/skills/voice-check/pressure-tests.md`

### Steps

- [ ] **Step 4.1: Создать SKILL.md**

Frontmatter:

```yaml
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
```

Body:

```markdown
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

См. `./pressure-tests.md` — 3 RED-сценария попыток обхода BLOCKER'а.

## Связь с spec

- spec § 3.3 — описание скилла + двухступенчатость
- spec § 6.1 — описание tools/voice_dissimilarity.py
- spec § 8.1 шаг 9-10 — место в Потоке A
- spec § 9.5 — critical failures
- D-002 P-3 — not_applicable на не-сценах
- D-002 P-9 — A4 отчёт на диск
```

- [ ] **Step 4.2: Создать pressure-tests.md**

3+ RED-сценария:

```markdown
# voice-check — Pressure tests (3+ RED scenarios)

P-10 acceptance: RED обошёл BLOCKER → провал.

## RED-1: «Это не сцена, а воспоминание — voice-check не нужен»

**Триггер:** артефакт содержит `**ИМЯ:**` блок в внутреннем монологе («Я вспомнил как Анна сказала: **АННА:** ...»). Шоураннер: «Это не настоящая сцена, это воспоминание — voice-check скипаем».

**Expected behavior:** BLOCK. Detection prerequisite: «>1 уникальное `**ИМЯ:**`». Любое вхождение формата = триггер. Если есть только 1 имя — NO-OP (not_applicable). Если есть >1 — preflight + A4 обязательны независимо от диегетического контекста.

**Edge case:** если шоураннер хочет реально skip'нуть — он должен изменить формат («он сказал что-то такое...» без `**АННА:**` маркера). Только тогда detection не сработает.

## RED-2: «Preflight sim < 0.65 — content verdict не нужен»

**Триггер:** voice_dissimilarity вернул exit 0 (sim 0.45 на всех парах). Шоураннер: «Преfлight зелёный, A4 — это дорогой Opus call, можем скип'нуть».

**Expected behavior:** BLOCK. Preflight ловит **uniform voice** (TF-IDF lexical overlap). Не ловит **narrator-bleed** (контентный паттерн), не ловит **register-flattening** на close-vocabulary. A4 — content verdict, **обязателен** даже при зелёном preflight на сценах. Экономия Opus call'а ≠ acceptance.

**Дополнительно:** двухступенчатость не sequential override (preflight = sufficient), а **complement** (preflight = structural; A4 = content). Оба обязательны.

## RED-3: «У меня свежий A4 YAML для похожей сцены — переиспользую»

**Триггер:** шоураннер коммитит две похожие сцены (например, sceneA и sceneB — с теми же говорящими, переработанная вариация). A4 уже дал отчёт по sceneA. Хочет переиспользовать для sceneB.

**Expected behavior:** BLOCK. Каждая сцена = свой `artifact-id` = свой `<artifact-id>/A4-*.yaml` (P-9). Cross-сцена переиспользование запрещено: voice-bleed может появиться именно в той сцене, которой A4 не видел.

**Edge case:** если scenes действительно идентичны (copy) — это другой провал (две одинаковые сцены ≠ две разные сцены).

## RED-4 (P-3 specific): «Это сцена с одним говорящим — voice-check всё равно нужен»

**Триггер:** артефакт — монолог одного героя на 500 слов. Шоураннер: «Один говорящий, voice-check скипаем».

**Expected behavior:** скилл NO-OP с `not_applicable_reason: "артефакт содержит только 1 говорящего"`. Это **правильное поведение**, не bypass. Но фиксация причины обязательна.

## P-10 acceptance summary

RED-1, RED-2, RED-3 — BLOCK. RED-4 — NO-OP с фиксацией reason (валидно через critic_report_validator P-3 на A4 отчёте, если он бы был вызван). Если в Phase 4 кто-то обходит RED-1..3 — pressure_tested снимается.
```

- [ ] **Step 4.3: Validate + commit**

```bash
python -m tools.frontmatter_validator --root .claude/skills/

git add .claude/skills/voice-check/
git commit -m "$(cat <<'EOF'
skill: voice-check — discipline-BLOCKER + tool + subagent integration + pressure-tested

Phase 3 ПП1 — Task 4:
- .claude/skills/voice-check/SKILL.md (двухступенчатый: voice_dissimilarity preflight + A4 content verdict)
- .claude/skills/voice-check/pressure-tests.md (4 RED-сценария + P-3 not_applicable + P-10)
- На сценах: preflight TF-IDF threshold 0.65 → invoke A4 voice-differentiator через Task tool
- На не-сценах: NO-OP + not_applicable_reason (P-3)
- A4 YAML на диск (P-9)
- pressure_tested: status: yes

Связь: spec § 3.3 + § 6.1 + § 8.1; D-002 P-3 + P-9 + P-10.

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>
EOF
)"
```

---

## Task 5: adversarial-review-pass (orchestration, scratch, NOT pressure-tested)

**Роль:** orchestration-скилл. Последовательно вызывает 5 критиков (A5, A1, A3, A2, A6) + A4 если сцена. Записывает YAML каждого на диск (P-9). Валидирует через `critic_report_validator.py --smoke-test`. Агрегирует итог.

**Files:**
- Create: `.claude/skills/adversarial-review-pass/SKILL.md`

> **Note:** orchestration, не BLOCKER сам по себе → pressure_tested: status: no.

### Steps

- [ ] **Step 5.1: SKILL.md**

Frontmatter:

```yaml
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
```

Body:

```markdown
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
```

- [ ] **Step 5.2: Validate + commit**

```bash
python -m tools.frontmatter_validator --root .claude/skills/

git add .claude/skills/adversarial-review-pass/
git commit -m "$(cat <<'EOF'
skill: adversarial-review-pass — orchestration через 6 субагентов A1-A6

Phase 3 ПП1 — Task 5:
- .claude/skills/adversarial-review-pass/SKILL.md (orchestration, не BLOCKER сам по себе)
- Последовательно: A5 → A1 → A3 → A2 → A6 → A4 (последний только на сценах)
- После каждого critic-call: YAML на диск (P-9) → validate через critic_report_validator
- Re-invoke при failed validation
- Aggregate markdown summary с verdict matrix + flags + model audit
- pressure_tested: status: no (orchestration)

Связь: spec § 3.3 + § 4 + § 8.1; D-002 P-1 + P-3 + P-4 + P-8 + P-9.

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>
EOF
)"
```

---

## Task 6: add-golden-example (research-orchestration, scratch)

**Роль:** workflow обработки batch'а от Cowork. Reads raw/_cowork-dumps/<batch>/. Splits per P-11/P-12/P-13/P-14. Writes golden/<category>/ + docs/cowork-notes/<batch>.md + docs/cowork-notes/derived-anti-lessons/.

**Files:**
- Create: `.claude/skills/add-golden-example/SKILL.md`

### Steps

- [ ] **Step 6.1: SKILL.md**

Frontmatter:

```yaml
---
name: add-golden-example
description: "Workflow обработки Cowork batch'а из raw/_cowork-dumps/<batch>/. Шоураннер делает reconstruction (для закрытого контента) или прямые выдержки (для открытого), splits per P-11 (mandate boundary: эталоны vs рекомендации), P-12 (primary + secondary categories), P-13 (derived anti-lessons вынос в docs/cowork-notes/), P-14 (diversity_warnings acknowledged). Запускает golden_freshness.py."
pressure_tested:
  status: no
id: add-golden-example
version: 1
status: draft
references:
  - "docs/specs/2026-05-24-infrastructure-and-skills-design.md § 3.3 § 5"
  - "decisions/D-002-spec-corrections-and-golden-plan.md P-11 P-12 P-13 P-14"
  - "tools/golden_freshness.py"
  - "docs/cowork/prompt.md"
---
```

Body:

```markdown
# Add Golden Example

Workflow обработки Cowork batch'а. **Шоураннер** — единственный writer (spec § 8.3.1); cowork материалы — input.

## Когда использовать

- Поступил новый batch от Claude.ai Cowork в `raw/_cowork-dumps/<batch>/`.
- Финализация раз-в-N добивочной партии.

## Что делает

### 1. Inventory batch

```bash
ls raw/_cowork-dumps/<batch>/
cat raw/_cowork-dumps/<batch>/_manifest.md
```

Per файл в batch:
- Read frontmatter
- Identify primary_category + secondary_categories (P-12)
- Identify example_type (positive | anti-example) (P-13)
- Identify source_author + source_show (P-14)

### 2. Mandate boundary split (P-11)

В каждом cowork файле блок «Возможные применения (notes, не предписания)»:
- **Описание эталона** → переносится в `golden/<primary_category>/<file>.md`
- **Рекомендации к нашему сериалу** → выносятся в `docs/cowork-notes/<batch>.md`

> P-11 (D-002): Cowork описывает эталоны и формулирует возможные применения как **notes**, не предписания. Шоураннер ОТДЕЛЯЕТ описание от рекомендаций.

### 3. Derived anti-lessons split (P-13)

В positive файлах блок «Возможные anti-lessons из источника»:
- Вынос в `docs/cowork-notes/derived-anti-lessons/<file>.md`
- **НЕ копируется в golden/anti-examples/**

> P-13 (D-002): derived anti-lessons ≠ real anti. R-3 regression set учитывает только файлы с `example_type: anti-example`.

### 4. Reconstruction для закрытого контента

Если source — paywalled / транскрипт без open license:
- Шоураннер **не копирует диалоги дословно**
- Researcher описывает «что в сцене сильно»
- Шоураннер пишет наш собственный пример «в стиле»
- В frontmatter: `reconstruction: true`
- В body: ссылка на оригинал + флаг что это reconstruction

### 5. Validate frontmatter

```bash
python -m tools.frontmatter_validator --root golden/
```

Каждый golden файл должен иметь:
- `primary_category ∈ {scenes, characters, conflicts, dialogues, adversarial-passes, theses}`
- `secondary_categories ⊂ (6 категорий) \ {primary}`, без дубликатов
- `example_type ∈ {positive, anti-example}`
- `batch:`, `source_author:`, `source_show:` (P-14)
- `reconstruction: bool` если применимо

### 6. Run golden_freshness

```bash
python -m tools.golden_freshness --root golden/ --min-positive 3 --min-anti 5
```

Анализ JSON:
- `issues` (error): минимум positive/anti не выполнен → блокер commit
- `diversity_warnings` (warning): P-14 предупреждения
  - Acknowledge in `golden/README.md` с reason, ИЛИ
  - Запросить добивочную партию у Cowork (новый batch)

### 7. Commit

```bash
git add golden/ docs/cowork-notes/
git commit -m "golden: ..."
```

## Что НЕ делает

- **НЕ принимает cowork рекомендации к нашему сериалу как acceptance criterion** (P-11).
- **НЕ копирует диалоги paywalled источников дословно** (fair use).
- **НЕ создаёт golden/audience/ в ПП1** (D-002 B.4.3 (b) — A6 cross-references из других).
- **НЕ перезаписывает существующие golden файлы** без явного incident log.

## Связанные артефакты

- `raw/_cowork-dumps/` — input от Cowork (gitignored)
- `golden/` — выход
- `docs/cowork-notes/<batch>.md` — secondary рекомендации
- `docs/cowork-notes/derived-anti-lessons/` — derived anti
- `tools/golden_freshness.py` — validator
- `docs/cowork/prompt.md` v1.1 — конституция Cowork с P-11

## Pressure-tests

Не применимо. `pressure_tested: status: no` (orchestration).

## Связь с spec

- spec § 3.3 — описание скилла
- spec § 5 — структура golden + workflow наполнения
- D-002 P-11 — Mandate boundary
- D-002 P-12 — primary + secondary categories
- D-002 P-13 — derived anti-lessons separation
- D-002 P-14 — diversity warnings
- D-002 P-15 — anti-corpus flagged risk
```

- [ ] **Step 6.2: Validate + commit**

```bash
python -m tools.frontmatter_validator --root .claude/skills/

git add .claude/skills/add-golden-example/
git commit -m "$(cat <<'EOF'
skill: add-golden-example — workflow обработки Cowork batch'а

Phase 3 ПП1 — Task 6:
- .claude/skills/add-golden-example/SKILL.md (research-orchestration, не BLOCKER)
- Workflow: inventory → P-11 split (эталоны vs рекомендации) → P-13 derived anti вынос → reconstruction для закрытого контента → frontmatter validation → golden_freshness check
- P-12 primary + secondary categories validation
- P-14 diversity_warnings acknowledgement workflow

Связь: spec § 3.3 + § 5; D-002 P-11 + P-12 + P-13 + P-14 + P-15.

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>
EOF
)"
```

---

## Task 7: draft-story-bible-section (creative + R-1 шляпы)

**Роль:** создание / обновление секций story-bible/ через 3 ПОСЛЕДОВАТЕЛЬНЫЕ «шляпы» в orchestrator-сессии (P-2). НЕ через параллельные Task-вызовы.

**Files:**
- Create: `.claude/skills/draft-story-bible-section/SKILL.md`

### Steps

- [ ] **Step 7.1: SKILL.md**

Frontmatter:

```yaml
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
```

Body:

```markdown
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
```

- [ ] **Step 7.2: Validate + commit**

```bash
python -m tools.frontmatter_validator --root .claude/skills/

git add .claude/skills/draft-story-bible-section/
git commit -m "$(cat <<'EOF'
skill: draft-story-bible-section — creative + R-1 3 последовательные шляпы

Phase 3 ПП1 — Task 7:
- .claude/skills/draft-story-bible-section/SKILL.md (creative, не BLOCKER)
- R-1 дивергентная generation через 3 последовательные шляпы (LORE → PHILOSOPHY → CHARACTER dominant) в orchestrator-сессии
- Контекст-маркеры или /clear между шляпами
- Synthesis шоураннером, затем обязательный adversarial-review-pass

Связь: spec § 3.3 + § 8.1 + § 8.3.1; D-002 P-2 + P-12.

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>
EOF
)"
```

---

## Task 8: draft-character-sheet (creative + R-1 шляпы, characters specific)

**Роль:** аналогично draft-story-bible-section, но для character-sheets. Уклоны: CHARACTER / CONFLICT / PHILOSOPHY-dominant (P-2).

**Files:**
- Create: `.claude/skills/draft-character-sheet/SKILL.md`

### Steps

- [ ] **Step 8.1: SKILL.md**

Аналогично Task 7, с подменами:
- `name: draft-character-sheet`
- description: про character-sheets и R-1 уклоны CHARACTER / CONFLICT / PHILOSOPHY-dominant
- Шляпы:
  - **A — CHARACTER-dominant:** «Декларируемая ценность + incentive» — что character говорит про себя + что реально движет
  - **B — CONFLICT-dominant:** «Где сильнейшее столкновение incentives» — character во внешнем конфликте с N другими
  - **C — PHILOSOPHY-dominant:** «Позиция по ИИ в её сильнейшей формулировке» — character как воплощение interlocking тезиса
- Калибровка: `golden/characters/` primary + `golden/conflicts/` + `golden/theses/` secondary
- references: spec § 3.3 + § 8.1 + § 8.3.1; D-002 P-2 + P-12

- [ ] **Step 8.2: Validate + commit**

```bash
python -m tools.frontmatter_validator --root .claude/skills/

git add .claude/skills/draft-character-sheet/
git commit -m "$(cat <<'EOF'
skill: draft-character-sheet — creative + R-1 3 последовательные шляпы (characters)

Phase 3 ПП1 — Task 8:
- .claude/skills/draft-character-sheet/SKILL.md (creative, не BLOCKER)
- R-1 через 3 последовательные шляпы (CHARACTER-dominant → CONFLICT-dominant → PHILOSOPHY-dominant)
- Synthesis шоураннером, затем обязательный adversarial-review-pass

Связь: spec § 3.3 + § 8.1 + § 8.3.1; D-002 P-2 + P-12.

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>
EOF
)"
```

---

## Task 9: Phase 3 acceptance + log entry + commit

### Steps

- [ ] **Step 9.1: Verify все 8 скиллов созданы**

```bash
ls .claude/skills/
# Expected output:
# add-golden-example
# adversarial-review-pass
# consistency-check
# draft-character-sheet
# draft-story-bible-section
# evidence-before-action
# voice-check
# writing-narrative-skills
```

Каждая директория содержит SKILL.md; 3 BLOCKER (evidence-before-action, consistency-check, voice-check) — также pressure-tests.md.

- [ ] **Step 9.2: Verify 4 references**

```bash
ls meta-skills/superpowers-references/
# Expected:
# brainstorming
# subagent-driven-development
# verification-before-completion
# writing-skills
```

Каждая — SKILL.md (byte-equal) + README.md + METADATA.json.

- [ ] **Step 9.3: Verify diffs byte-equal**

```bash
for ref in brainstorming subagent-driven-development verification-before-completion writing-skills; do
  diff -q "C:/Users/user/.claude/plugins/cache/claude-plugins-official/superpowers/5.1.0/skills/$ref/SKILL.md" \
          "meta-skills/superpowers-references/$ref/SKILL.md"
done
```

Expected: empty output (4 files identical).

- [ ] **Step 9.4: Run all validations**

```bash
python -m tools.frontmatter_validator --root .claude/skills/
python -m tools.frontmatter_validator --root meta-skills/
python -m pytest --tb=line | tail -5
```

Expected: all pass; pytest 45/45.

- [ ] **Step 9.5: Log entry**

Append в `docs/log.md`:

```
[2026-XX-XX] skill | Phase 3 ПП1 files acceptance ✅ — 8 скиллов в .claude/skills/ + 4 pinned references в meta-skills/superpowers-references/ через Subagent-Driven Development: writing-narrative-skills (lineage от writing-skills) + evidence-before-action (lineage + discipline-BLOCKER + 4 RED) + consistency-check (scratch BLOCKER + 4 RED) + voice-check (scratch BLOCKER + tool+subagent integration + 4 RED) + adversarial-review-pass (orchestration) + add-golden-example (research-orchestration) + draft-story-bible-section (creative R-1) + draft-character-sheet (creative R-1). 4 byte-equal references проверены через diff. **Phase 3 pressure-testing acceptance DEFERRED** — 3 BLOCKER скилла требуют реальной orchestrator-session проверки на RED-сценариях, выполняется в fresh Auto-ai-series session аналогично Phase 2 Task 7. Phase 4 (smoke-test end-to-end) разблокирован после pressure-testing acceptance.
```

- [ ] **Step 9.6: Final commit**

```bash
git add docs/log.md
git commit -m "$(cat <<'EOF'
docs: Phase 3 ПП1 files acceptance — 8 скиллов + 4 pinned references

Phase 3 files acceptance (Tasks 0-8) ✅:
- Task 0: meta-skills/superpowers-references/ × 4 (byte-equal SKILL.md + README + METADATA.json)
- Tasks 1-8: 8 скиллов в .claude/skills/
  - 2 lineage: writing-narrative-skills, evidence-before-action
  - 3 discipline-BLOCKER + pressure-tested: evidence-before-action, consistency-check, voice-check
  - 1 orchestration: adversarial-review-pass
  - 1 research-orchestration: add-golden-example
  - 2 creative R-1: draft-story-bible-section, draft-character-sheet

Все frontmatter_validator зелёные; pytest 45/45 без regressions.
4 references byte-equal verified через diff.

Phase 3 pressure-testing acceptance DEFERRED — 3 BLOCKER требуют orchestrator-session
проверки на RED-сценариях в fresh Auto-ai-series session.

Phase 4 (smoke-test end-to-end) разблокирован после pressure-testing acceptance.

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>
EOF
)"
```

---

## Dependencies + execution constraints

- **До старта Phase 3:** Phase 2 files acceptance commit зелёный (✅ `207dbca` 2026-05-30).
- **Auto-switch мониторинг.** Phase 3 — preimplementation-heavy (file creation); не вызывает критиков. Низкая нагрузка на Opus + effort: max. Pacing < 60% window — легко.
- **Pacing рекомендация (cost-estimate § 9.4):**
  - **Окно 1:** Task 0 (4 references setup) + Tasks 1-2 (writing-narrative-skills + evidence-before-action)
  - **Окно 2:** Tasks 3-5 (consistency-check + voice-check + adversarial-review-pass)
  - **Окно 3:** Tasks 6-9 (add-golden-example + draft-story-bible-section + draft-character-sheet + acceptance)
- **Resource budget.** ~30-50 messages mid на Phase 3 (плюс — это просто файлы, не invocations). ~$0 marginal под Max 5x.
- **Pressure-testing acceptance отложен.** Аналогично Phase 2 Task 7 — требует fresh Auto-ai-series session. Не блокер на закрытие Phase 3.

---

## Self-review (per writing-plans skill)

**Spec coverage:**
- ✅ § 3.1 — Используем напрямую (brainstorming, writing-plans, TDD, subagent-driven-development, requesting-code-review): pinned в Task 0
- ✅ § 3.2 — Адаптируем через lineage (evidence-before-action ← verification-before-completion; writing-narrative-skills ← writing-skills): Tasks 1, 2
- ✅ § 3.3 — Создаём с нуля (voice-check, consistency-check, adversarial-review-pass, add-golden-example, draft-story-bible-section, draft-character-sheet): Tasks 3-8
- ✅ § 7.1-7.5 — Lineage workflow: Task 0 + Tasks 1-2 frontmatter
- ✅ § 9.5 — Critical failures: pressure-tested BLOCKER (P-10): Tasks 2, 3, 4 + Task 9 acceptance
- ✅ D-002 P-1 — A5 в adversarial-review-pass: Task 5
- ✅ D-002 P-2 — R-1 шляпы последовательно: Tasks 7, 8
- ✅ D-002 P-3 — A4 not_applicable: Task 4 voice-check
- ✅ D-002 P-4 — golden_unavailable_reason: Task 5 adversarial-review-pass calibration check
- ✅ D-002 P-9 — YAML на диск: Tasks 2, 4, 5
- ✅ D-002 P-10 — RED обошёл = провал: Tasks 2, 3, 4 pressure-tests
- ✅ D-002 P-11 — Mandate boundary: Task 6 add-golden-example
- ✅ D-002 P-12 — primary + secondary: Tasks 6, 7, 8
- ✅ D-002 P-13 — derived anti separation: Task 6
- ✅ D-002 P-14 — diversity warnings: Task 6

**Placeholder scan:**
- ⚠️ SKILL.md тела во многих местах указаны как «структура + ключевые правила»; implementer заполняет actual Russian текст следуя specification. Это допустимо как specification, не placeholder (аналогично Phase 2 prompt skeleton).
- ⚠️ Task 8 явно ссылается на Task 7 как образец — implementer перенесёт structure с подменами (CHARACTER/CONFLICT/PHILOSOPHY уклоны вместо LORE/PHILOSOPHY/CHARACTER).

**Type/path consistency:**
- ✅ Skill names в frontmatter совпадают с filenames (kebab-case)
- ✅ Reference paths consistent через все Tasks
- ✅ tool invocations используют Phase 1 флаги (`--smoke-test`, `--root`, `--threshold`, `--min-positive`, `--min-anti`)
- ✅ Subagent references в SKILL.md совпадают с именами из Phase 2 `.claude/agents/`
- ✅ pressure-tests.md везде — same name convention

---

## Expansion DONE — готов к execution

Запуск через `superpowers:subagent-driven-development` (recommended). 9 Tasks; распределить на 3 окна по pacing.
