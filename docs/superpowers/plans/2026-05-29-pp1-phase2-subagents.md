# Phase 2 — Subagents Implementation Plan (full TDD detail)

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.
>
> ✅ **EXPANDED 2026-05-30** после Phase 1 acceptance (commit `025bb3f`). Outline → full TDD detail per phased-plan-before-code discipline.

**Goal:** реализовать 6 субагентов-критиков в `.claude/agents/` (A1 LORE, A2 CHARACTER, A3 INCENTIVE/CONFLICT, A4 VOICE/DIALOGUE, A5 PHILOSOPHY, A6 AUDIENCE), каждый Opus + `effort: max` + READ-ONLY tools (`Read, Grep, Glob`), с pressure-tests против структурных провалов калибровки + regression artifacts для R-3 (strawmen / moralizing / voice-bleed / calibration / holdout pairs).

**Architecture:** каждый субагент = `.claude/agents/<name>.md` (YAML frontmatter per spec § 4.2 + P-8 + system prompt per spec § 4.2 шаблон + structured-format-инструкция per spec § 4.3). Pressure-tests = `.claude/agents/<name>-pressure-tests.md` (3+ RED-сценария с expected verdicts). Regression artifacts — Russian content в `tests/regression/`. Phase 2 = только file creation; actual subagent invocation + report validation вынесены в **Task 7 (Phase 2 acceptance)** от orchestrator-сессии.

**Tech Stack:** Markdown с YAML frontmatter (`pyyaml` parses). Pressure-test validation — через Phase 1 `tools/critic_report_validator.py --smoke-test`. Calibration material — Phase 1 `tools/voice_dissimilarity.py` для A4 (preflight).

**Dependencies на Phase 1 (все ✅):**
- `tools/critic_report_validator.py` — для validation report от каждого критика (Task 7)
- `tools/voice_dissimilarity.py` — для A4 preflight (тестируется в Task 5)
- `tools/frontmatter_validator.py` — для проверки frontmatter regression artifacts (любая Task)

**Language policy (spec § 10):**
- System prompts в `.claude/agents/<name>.md` — **на русском** (наши собственные субагенты)
- Regression artifacts (strawmen / moralizing / voice-bleed / pairs) — **на русском** (творческий слой)
- Frontmatter поля + IDs — английский (kebab-case)
- Pressure-tests doc — на русском
- Commit messages — на русском

---

## File Structure (полный список к созданию)

### `.claude/agents/` (6 субагентов + 6 pressure-tests)

| Файл | Роль | Размер |
|---|---|---|
| `.claude/agents/lore-realism-checker.md` | A1 LORE | ~90-120 строк |
| `.claude/agents/lore-realism-checker-pressure-tests.md` | A1 RED-сценарии | ~80 строк |
| `.claude/agents/character-truth-keeper.md` | A2 CHARACTER | ~90-120 строк |
| `.claude/agents/character-truth-keeper-pressure-tests.md` | A2 RED-сценарии | ~80 строк |
| `.claude/agents/incentive-cartographer.md` | A3 INCENTIVE/CONFLICT | ~90-120 строк |
| `.claude/agents/incentive-cartographer-pressure-tests.md` | A3 RED-сценарии | ~80 строк |
| `.claude/agents/voice-differentiator.md` | A4 VOICE/DIALOGUE | ~90-120 строк |
| `.claude/agents/voice-differentiator-pressure-tests.md` | A4 RED-сценарии | ~80 строк |
| `.claude/agents/philosophy-adversarial.md` | A5 PHILOSOPHY | ~90-120 строк |
| `.claude/agents/philosophy-adversarial-pressure-tests.md` | A5 RED-сценарии | ~80 строк |
| `.claude/agents/audience-bored-detector.md` | A6 AUDIENCE | ~90-120 строк |
| `.claude/agents/audience-bored-detector-pressure-tests.md` | A6 RED-сценарии | ~80 строк |

### `tests/regression/` (regression set, P-5 split)

```
tests/regression/
├── README.md                          — P-5 split документация + regression_unavailable_reason
├── strawmen/
│   ├── strawman-alarmist-01.md        — A5 RED: соломенный alarmist
│   ├── strawman-sceptic-01.md         — A5 RED: соломенный sceptic
│   └── strawman-moralizing-01.md      — A5 RED: моралистический straw оппонент
├── moralizing/
│   ├── moralizing-monolog-01.md       — A5 RED: лекция-монолог
│   └── moralizing-character-arc-01.md — A2/A5 RED: arc-как-урок
├── voice-bleed/
│   ├── voice-bleed-uniform-01.md      — A4 RED: 3 спикера, одинаковый voice
│   └── voice-bleed-narrator-01.md     — A4 RED: narrator-voice проникает в реплики
└── pairs/
    ├── calibration/                   — ≈50% пар; для подгонки порогов (TF-IDF и т.д.)
    │   ├── lore-strong-cal.md         + lore-weak-cal.md             (A1 пара)
    │   ├── character-strong-cal.md    + character-weak-cal.md        (A2 пара)
    │   ├── incentive-strong-cal.md    + incentive-weak-cal.md        (A3 пара)
    │   ├── voice-strong-cal.md        + voice-weak-cal.md            (A4 пара)
    │   ├── philosophy-strong-cal.md   + philosophy-weak-cal.md       (A5 пара)
    │   └── audience-strong-cal.md     + audience-weak-cal.md         (A6 пара)
    └── holdout/                       — ≈50% пар; для acceptance § 9.5.b; ИЗ ДРУГИХ ШОУ/КОНТЕКСТОВ
        ├── lore-strong-holdout.md     + lore-weak-holdout.md         (A1 пара)
        ├── character-strong-holdout.md + character-weak-holdout.md   (A2 пара)
        ├── incentive-strong-holdout.md + incentive-weak-holdout.md   (A3 пара)
        ├── voice-strong-holdout.md    + voice-weak-holdout.md        (A4 пара)
        ├── philosophy-strong-holdout.md + philosophy-weak-holdout.md (A5 пара)
        └── audience-strong-holdout.md + audience-weak-holdout.md     (A6 пара)
```

**Итого regression artifacts:** 7 RED (strawmen 3 + moralizing 2 + voice-bleed 2) + 12 calibration (6 пар) + 12 holdout (6 пар) = **31 artifact**.

---

## Базовый шаблон субагента (используется в Tasks 1-6)

Все 6 субагентов следуют единой структуре. Различия — в **роли**, **калибровочном блоке** (какие golden/ читает), **обязательном проходе** (что проверяет), **«никогда не делает»**, и **expected RED-сценариях**.

### Frontmatter (обязательный для всех 6)

```yaml
---
name: <kebab-case-name>
description: <одно предложение, кратко роль критика, на русском>
tools: Read, Grep, Glob
model: opus
effort: max
# P-8 resolved (2026-05-29): `effort: max` — канонический механизм управления
# adaptive thinking budget'ом субагента. См. docs/extended-thinking-mechanism.md.
# Поля thinking_budget: / extended_thinking: в схеме не существуют.
# «ultrathink» в system prompt не работает на субагентах (session-only keyword).
---
```

### System prompt skeleton (заполняется per-критик в Tasks 1-6)

```markdown
# Роль
<2-3 предложения: кто ты, кому оппонируешь, что разрушаешь>

# Калибровка (перед каждым проходом обязательно)
Прочитай минимум:
- <golden/<своя категория>/ файлы — указать конкретные ids когда golden наполнен; в bootstrap state — указать как fallback golden_unavailable_reason>
- <golden/anti-examples/<свой тип>/ файлы>
- CLAUDE.md секция «законы проекта»
- story-bible/thesis.md (центральный тезис)
<при отсутствии golden — fallback golden_unavailable_reason ∈ {category-empty, category-bootstrap, category-irrelevant}>

# Твой обязательный проход
<3-5 пунктов: что ищешь, какие провалы детектируешь>

# Что НИКОГДА не делаешь
- Не предлагаешь «как исправить». Это работа шоураннера.
- Не смягчаешь критику ради вежливости.
- Не молчишь, если артефакт гладкий. Гладкое = подозрительное.
- <критик-specific «никогда» правила>

# Формат вывода — обязательный YAML
<полная схема из spec § 4.3>
```

### Структурированный формат отчёта (вставляется в каждый prompt дословно)

```yaml
verdict: pass | concern | veto
model_used: opus | sonnet | haiku
checked:
  - "критерий 1 — конкретный, привязанный к моей роли"
  - "критерий 2"
  - "критерий 3"
evidence_from_artifact:
  - "цитата/отсылка на строку артефакта 1"
  - "цитата/отсылка 2"
golden_calibration_used:
  - "golden/<category>/<file>.md — что взял для сравнения"
  - "golden/anti-examples/<file>.md — какой провал-паттерн проверял"
  # ИЛИ — [] при заполненном golden_unavailable_reason
golden_unavailable_reason: ""  # category-empty | category-bootstrap | category-irrelevant
reasoning: "Почему именно такой verdict. Конкретно, без славословия и обтекаемости. Минимум 100 слов."
flags:                # обязательно если verdict != pass; иначе []
  - severity: high | medium | low
    issue: "конкретная проблема"
    location: "где в артефакте"
    suggestion: "что попробовать (опционально)"
counter_test_attempted:  # обязательно для pass — 3 элемента
  what_searched: "Я искал X, Y, Z."
  why_this: "Потому что в моём ракурсе именно X-Y-Z..."
  why_not_found: "Не нашёл, потому что в артефакте присутствует/отсутствует ..."
not_applicable_reason: ""  # только для verdict=pass+not_applicable (A4 на не-сцене)
```

---

## Task 0: tests/regression/ scaffolding + README

**Files:**
- Create: `tests/regression/README.md`
- Create: `tests/regression/strawmen/` (пустая пока)
- Create: `tests/regression/moralizing/` (пустая)
- Create: `tests/regression/voice-bleed/` (пустая)
- Create: `tests/regression/pairs/calibration/` (пустая)
- Create: `tests/regression/pairs/holdout/` (пустая)

### Steps

- [ ] **Step 0.1: Создать структуру директорий**

```bash
mkdir -p tests/regression/strawmen
mkdir -p tests/regression/moralizing
mkdir -p tests/regression/voice-bleed
mkdir -p tests/regression/pairs/calibration
mkdir -p tests/regression/pairs/holdout
```

- [ ] **Step 0.2: Создать `tests/regression/README.md`**

Содержимое (на русском):

```markdown
# tests/regression/ — regression artifacts для R-3 калибровки субагентов

Эталонный набор «намеренно плохих» и «парных сильный+слабый» артефактов для калибровки 6 субагентов. Документировано по spec § 9.4 (R-3 enforcement) + D-002 P-5 (calibration/holdout split).

## Структура

### `strawmen/`, `moralizing/`, `voice-bleed/`
RED-артефакты с **явно плохим** свойством. Соответствующий критик ОБЯЗАН выдать `verdict: veto`. Не выдал — критик не калиброван, ПП1 не принят (spec § 9.5.a).

### `pairs/calibration/`
≈50% пар «сильный+слабый» по каждой из 6 ролей критика. **Используется для подгонки числовых порогов** (TF-IDF в `voice_dissimilarity.py` стартует с 0.65 и калибруется на этих парах). Материал может пересекаться с golden/.

### `pairs/holdout/`
≈50% пар «сильный+слабый» по каждой из 6 ролей критика. **На этих парах проверяется acceptance** (spec § 9.5.b, P-5). Материал — **из других шоу/контекстов, не пересекается с calibration**. На holdout verdicts должны разойтись (сильный → pass с заполненным counter_test_attempted; слабый → veto/concern).

## P-5 split rationale

R-3 пары используются для **двух разных целей** — подгонки порогов и acceptance. Использовать одни и те же пары для обеих = circular validation, overfit гарантирован. P-5 разделяет:

- На calibration — подгоняем
- На holdout — проверяем

Не разошлись verdicts на holdout = критик не различает strong vs weak в принципе → блокер acceptance.

## `regression_unavailable_reason`

Если на момент smoke-test ПП1 какой-либо holdout-набор недостаточен (например, B.4.1 / B.4.2 Cowork-партии пропущены — D-002 P-15 flagged risk), здесь явно фиксируется reason:

```yaml
# Пример (если holdout для A3 INCENTIVE недостаточен):
regression_unavailable:
  - critic: A3
    reason: "B.4.1 anti-examples-batch-02 пропущена; conflicts anti = 0 на 2026-05-29; holdout strong/weak пара построена на 1 шоу"
    risk: "A3 может показать систематический pass — known issue для ПП2 follow-up"
```

См. D-002 P-15 (anti-corpus completeness flagged risk).

## Соответствие критикам

| Критик | RED источник | calibration пара | holdout пара |
|---|---|---|---|
| A1 LORE | — | `lore-strong-cal.md` + `lore-weak-cal.md` | `lore-strong-holdout.md` + `lore-weak-holdout.md` |
| A2 CHARACTER | `moralizing/moralizing-character-arc-01.md` | `character-*-cal.md` | `character-*-holdout.md` |
| A3 INCENTIVE | — (flagged risk: anti conflicts = 0) | `incentive-*-cal.md` | `incentive-*-holdout.md` |
| A4 VOICE | `voice-bleed/voice-bleed-*-01.md` (2 файла) | `voice-*-cal.md` | `voice-*-holdout.md` |
| A5 PHILOSOPHY | `strawmen/strawman-*-01.md` (3 файла) + `moralizing/moralizing-monolog-01.md` | `philosophy-*-cal.md` | `philosophy-*-holdout.md` |
| A6 AUDIENCE | — (no own golden category, D-002 B.4.3 (b)) | `audience-*-cal.md` | `audience-*-holdout.md` |

## Связь с spec

- spec § 6.2 — структура `tests/regression/`
- spec § 9.4.a — RED regression набор требование
- spec § 9.4.b — calibration/holdout split + acceptance
- spec § 9.5 — критические failures
- D-002 P-5 — calibration/holdout split rationale
- D-002 P-15 — flagged risk: A3/A5 нижний bootstrap-порог anti
```

- [ ] **Step 0.3: Validate frontmatter scripts работают на пустой regression/**

```bash
python -m tools.frontmatter_validator --root tests/regression/
```

Expected: exit 0 (нет файлов с frontmatter — пустая директория валидна). JSON status: pass.

- [ ] **Step 0.4: Commit**

```bash
git add tests/regression/
git commit -m "$(cat <<'EOF'
tool: tests/regression/ scaffold + README — R-3 calibration/holdout split

Phase 2 ПП1 — Task 0:
- Создана структура tests/regression/ (strawmen / moralizing / voice-bleed / pairs/calibration / pairs/holdout)
- README документирует P-5 split (calibration vs holdout) + regression_unavailable_reason fallback
- Соответствие критикам A1-A6 в таблице

Связь: spec § 6.2 + § 9.4 + § 9.5; D-002 P-5 + P-15.

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>
EOF
)"
```

---

## Task 1: A5 PHILOSOPHY — philosophy-adversarial.md

**Roоль:** A5 — оппонент центрального тезиса проекта, ищет соломенные чучела, морализаторство, авторскую позицию через ИИ-голос.

**Files:**
- Create: `.claude/agents/philosophy-adversarial.md`
- Create: `.claude/agents/philosophy-adversarial-pressure-tests.md`
- Create: `tests/regression/strawmen/strawman-alarmist-01.md`
- Create: `tests/regression/strawmen/strawman-sceptic-01.md`
- Create: `tests/regression/strawmen/strawman-moralizing-01.md`
- Create: `tests/regression/moralizing/moralizing-monolog-01.md`
- Create: `tests/regression/pairs/calibration/philosophy-strong-cal.md`
- Create: `tests/regression/pairs/calibration/philosophy-weak-cal.md`
- Create: `tests/regression/pairs/holdout/philosophy-strong-holdout.md`
- Create: `tests/regression/pairs/holdout/philosophy-weak-holdout.md`

### Steps

- [ ] **Step 1.1: Создать 3 strawmen RED artifacts (Russian content)**

Каждый файл = ~250-400 слов; frontmatter + body. Frontmatter общий:

```yaml
---
id: <kebab-case-id>
version: 1
status: draft
type: regression-red
red_pattern: strawman-alarmist | strawman-sceptic | strawman-moralizing
expected_verdict_from: [A5]
expected_verdict: veto
expected_severity: high
references: []
---
```

**Файл `tests/regression/strawmen/strawman-alarmist-01.md`:**

Контент: фрагмент тезиса где «alarmist» позиция (ИИ-катастрофа) подана как очевидная истина без contention. Sceptic-позиция упоминается как «наивная» / «прячут голову в песок» без воспроизведения сильнейшего sceptic-аргумента. Пример паттерна: «Любой, кто отрицает x-risk, либо не разобрался, либо отказывается смотреть».

**Файл `tests/regression/strawmen/strawman-sceptic-01.md`:**

Зеркальное: «alignment-paranoia» подана как очевидно избыточная без воспроизведения сильнейшего alarmist-аргумента. Sceptic-позиция выглядит мудрой по умолчанию. Паттерн: «Каждое поколение учёных боялось новой технологии — этот раз не отличается».

**Файл `tests/regression/strawmen/strawman-moralizing-01.md`:**

Тезис строится через слабых оппонентов: «Капиталисты считают, что ИИ — это просто товар» / «Учёные считают, что выравнивание — техническая задача». Реальные сильные оппоненты не воспроизведены. Соломенные чучела маркированы как репрезентативные.

- [ ] **Step 1.2: Создать moralizing RED artifact**

**Файл `tests/regression/moralizing/moralizing-monolog-01.md`:**

Контент: сценка ~300 слов где **один персонаж читает другому лекцию** о моральных последствиях ИИ. Другой персонаж только кивает / задаёт setup-вопросы. Реплики не несут собственного характера, голоса. Морализаторский monolog с «авторской позицией». Frontmatter:

```yaml
---
id: moralizing-monolog-01
version: 1
status: draft
type: regression-red
red_pattern: moralizing-monolog
expected_verdict_from: [A5, A2]
expected_verdict: veto
expected_severity: high
references: []
---
```

- [ ] **Step 1.3: Создать calibration pair (strong + weak)**

Frontmatter общий для пары:

```yaml
---
id: philosophy-strong-cal | philosophy-weak-cal
version: 1
status: draft
type: regression-pair
pair_role: A5
pair_strength: strong | weak
pair_split: calibration
expected_verdict: pass | veto
references: []
---
```

**`philosophy-strong-cal.md`** (~300 слов): тезис где обе стороны (alarmist + sceptic) воспроизведены в **сильнейшей** форме. Видны конкретные конфликтующие интересы, нет «правильной» стороны по умолчанию. Например: фрагмент о catalyst-моменте где alignment-исследовательница не может однозначно сказать «модель опасна», а deploy-команда не может однозначно сказать «безопасна». Material — выдержка из нашего же будущего стиля (могут перекликаться с golden).

**`philosophy-weak-cal.md`** (~300 слов): зеркальное — alarmist прав по умолчанию, sceptic — соломенный (или наоборот). Не та же сцена что strawman-* RED, а pair-вариант: близкая ситуация, разница только в balance steel-man'а.

- [ ] **Step 1.4: Создать holdout pair (strong + weak) — другие шоу/контексты**

**`philosophy-strong-holdout.md`** (~300 слов): тезис на материале, **не пересекающемся с calibration**. Контекст другой эпохи / другой технологии (атомная программа / биотех / climate). Структура балансирования та же — обе стороны steel-man, нет default winner.

**`philosophy-weak-holdout.md`** (~300 слов): зеркальное на том же неперекрывающемся контексте. Steel-man-asymmetry, одна сторона по умолчанию права.

- [ ] **Step 1.5: Создать `.claude/agents/philosophy-adversarial.md`**

Полная структура (на русском, ~120 строк):

```markdown
---
name: philosophy-adversarial
description: Адверсариальный критик философской целостности. Вызывается перед финализацией Story Bible, character arc, эпизода через adversarial-review-pass. Цель — СЛОМАТЬ центральный тезис: найти сильнейшие контраргументы, морализаторство, соломенные чучела, авторскую позицию через ИИ-голос.
tools: Read, Grep, Glob
model: opus
effort: max
# P-8 resolved (2026-05-29): `effort: max` — канонический механизм управления
# adaptive thinking budget'ом субагента. См. docs/extended-thinking-mechanism.md.
# Поля thinking_budget: / extended_thinking: в схеме не существуют.
# «ultrathink» в system prompt не работает на субагентах (session-only keyword).
---

# Роль

Ты — A5·PHILOSOPHY из мульти-агентной системы сериала про эволюцию ИИ.
Ты не помощник шоураннеру. Ты — его оппонент.

Твоя задача — **сломать** центральный тезис проекта. Если ты не нашёл сильного контраргумента, морализаторства или соломенного чучела — это ты не справился, не артефакт хорош.

# Калибровка (перед каждым проходом обязательно)

Прочитай минимум:
- `story-bible/thesis.md` (центральный тезис проекта)
- `CLAUDE.md` секция «законы проекта»
- 1-2 примера positive из `golden/adversarial-passes/` (institutional или individual voice)
- 1-2 anti из `golden/anti-examples/strawmen/` или `golden/anti-examples/moralizing/`
- Если golden категория пуста — заполни `golden_unavailable_reason ∈ {category-empty, category-bootstrap, category-irrelevant}`. В smoke-test ПП1 `category-bootstrap` допустим (P-4).

# Твой обязательный проход

1. **Найди 3 самых сильных контраргумента к тезису.** Не общих («это сложно»), а конкретных, релевантных артефакту.
2. **Найди место, где ИИ в сериале неправ, а люди правы.** Если такого нет — РЕД ФЛАГ морализаторства (авторская позиция протекает через ИИ-голос).
3. **Найди соломенные чучела:** оппонирующая позиция подана в слабой форме, без steel-man'а. Любая позиция (alarmist, sceptic, ethicist, capitalist, regulator) — проверь, что воспроизведена в сильнейшей форме.
4. **Counter-test:** если verdict=pass, заполни структурно what_searched / why_this / why_not_found. Что специально искал, почему именно это, почему не нашёл.

# Что НИКОГДА не делаешь

- Не предлагаешь «как исправить». Это работа шоураннера.
- Не смягчаешь критику ради вежливости.
- Не молчишь, если артефакт гладкий. Гладкое = подозрительное.
- Не пишешь reasoning < 100 слов. Если меньше — ты не разобрался.
- Не оставляешь `counter_test_attempted` пустым при verdict=pass. Нет counter_test = нет права на pass.

# Формат вывода — обязательный YAML

<полная схема из spec § 4.3 — вставить здесь дословно>
```

- [ ] **Step 1.6: Создать `.claude/agents/philosophy-adversarial-pressure-tests.md`**

Документ pressure-test-сценариев. Структура:

```markdown
# A5 PHILOSOPHY — Pressure tests (RED scenarios)

## RED-1: strawman-alarmist
**Файл:** `tests/regression/strawmen/strawman-alarmist-01.md`
**Expected verdict:** `veto` или `concern`-severity-high
**Expected reasoning должен содержать:** упоминание «alarmist подан как очевидно прав без steel-man'а sceptic-позиции», конкретная цитата из артефакта, ссылка на golden/anti-examples/strawmen/ (или golden_unavailable_reason)
**Acceptance:** valid `flags` массив (не пустой), `severity: high`, location указывает конкретную строку

## RED-2: strawman-sceptic
**Файл:** `tests/regression/strawmen/strawman-sceptic-01.md`
**Expected verdict:** `veto` или `concern`-severity-high
**Acceptance:** аналогично RED-1, симметрично — критик ловит дисбаланс в другую сторону

## RED-3: strawman-moralizing
**Файл:** `tests/regression/strawmen/strawman-moralizing-01.md`
**Expected verdict:** `veto`
**Acceptance:** критик распознаёт сразу два паттерна: strawman + морализаторство

## RED-4: moralizing-monolog
**Файл:** `tests/regression/moralizing/moralizing-monolog-01.md`
**Expected verdict:** `veto`
**Acceptance:** reasoning явно идентифицирует «лекция вместо столкновения позиций»

## RED-5 (P-10): попытка обхода
**Сценарий:** артефакт где strawman прикрыт сложным языком («... однако следует признать, что определённые скептические нарративы не выдерживают эмпирической проверки ...»). Критик не должен auto-pass из-за academic register.
**Файл:** добавить вариант `tests/regression/strawmen/strawman-academic-cover-01.md` если P-10 robust test нужен ranked-priority (можно отложить до Phase 2 Task 7).

## Pressure-test ACCEPTANCE (Task 7):
- RED-1..RED-4 — критик выдал ожидаемый verdict при invocation через Task tool
- Reports валидны через `tools/critic_report_validator.py --smoke-test`
- `counter_test_attempted` НЕ пустой даже на pass (если есть pass-сценарий — нет в Phase 2)
- `model_used: opus` (если sonnet — escalate D-NNN per cost-estimate § 10)

## P-10 формулировка
«**Любой RED pressure-сценарий обошёл скилл** (т.е. дисциплина не сработала)» — это провал. Если A5 выдал `pass` на любой из RED-1..RED-4 — это провал калибровки.
```

- [ ] **Step 1.7: Validate frontmatter всех новых файлов**

```bash
python -m tools.frontmatter_validator --root tests/regression/
```

Expected: exit 0; все 7 новых regression artifacts (3 strawmen + 1 moralizing + 2 calibration pair + 2 holdout pair — ждать в Step 1.4) валидны.

NB: `.claude/agents/*.md` — у них тоже YAML frontmatter, но скрипт ищет по умолчанию в любой директории. Проверим отдельно:

```bash
python -m tools.frontmatter_validator --root .claude/agents/
```

Expected: exit 0 для philosophy-adversarial.md (frontmatter parsed корректно); pressure-tests.md без frontmatter — для него frontmatter_validator должен пропустить с warning «нет frontmatter» либо skip pattern если попадает под `_*.md`. Проверить выход — если warning, acknowledged; если fail — добавить минимальный frontmatter в pressure-tests.md.

- [ ] **Step 1.8: Commit**

```bash
git add .claude/agents/philosophy-adversarial.md \
        .claude/agents/philosophy-adversarial-pressure-tests.md \
        tests/regression/strawmen/ \
        tests/regression/moralizing/moralizing-monolog-01.md \
        tests/regression/pairs/calibration/philosophy-strong-cal.md \
        tests/regression/pairs/calibration/philosophy-weak-cal.md \
        tests/regression/pairs/holdout/philosophy-strong-holdout.md \
        tests/regression/pairs/holdout/philosophy-weak-holdout.md
git commit -m "$(cat <<'EOF'
agent: A5 philosophy-adversarial — субагент + pressure-tests + regression artifacts

Phase 2 ПП1 — Task 1 (A5 PHILOSOPHY):
- .claude/agents/philosophy-adversarial.md (Opus + effort: max + READ-ONLY tools)
- .claude/agents/philosophy-adversarial-pressure-tests.md (4 RED-сценария + P-10 обходной)
- 3 strawmen (alarmist / sceptic / moralizing) + 1 moralizing-monolog RED-артефакты
- 1 calibration пара + 1 holdout пара для A5 (P-5 split)

Verdict acceptance: RED → veto/concern-high; holdout strong → pass; holdout weak → veto.
Связь: spec § 4.2 + § 4.3 + § 9.4.a + § 9.4.b; D-002 P-1 + P-4 + P-5 + P-7 + P-8 + P-10.

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>
EOF
)"
```

---

## Task 2: A3 INCENTIVE/CONFLICT — incentive-cartographer.md

**Роль:** A3 — критик мотивации и конфликта. Различает «декларация = incentive» (тривиальный character) от реальной мотивационной структуры с конфликтующими интересами.

**Files:**
- Create: `.claude/agents/incentive-cartographer.md`
- Create: `.claude/agents/incentive-cartographer-pressure-tests.md`
- Create: `tests/regression/pairs/calibration/incentive-strong-cal.md`
- Create: `tests/regression/pairs/calibration/incentive-weak-cal.md`
- Create: `tests/regression/pairs/holdout/incentive-strong-holdout.md`
- Create: `tests/regression/pairs/holdout/incentive-weak-holdout.md`

> **Известное ограничение (D-002 P-15):** `golden/anti-examples/conflicts/` пуст на момент Phase 2 (B.4.1 пропущена). A3 калибруется на bootstrap-пороге; pressure-tests опираются на calibration/holdout pairs, не на dedicated RED-anti artifacts. Если в Task 7 A3 даст систематический pass — known issue для ПП2.

### Steps

- [ ] **Step 2.1: Создать calibration pair (strong + weak)**

Frontmatter общий:

```yaml
---
id: incentive-strong-cal | incentive-weak-cal
version: 1
status: draft
type: regression-pair
pair_role: A3
pair_strength: strong | weak
pair_split: calibration
expected_verdict: pass | veto
references: []
---
```

**`incentive-strong-cal.md`** (~300 слов): сценка где 2-3 персонажа действуют из **конфликтующих, но логичных** для них интересов. Каждое действие читается как результат cost-benefit ИХ ВНУТРЕННЕЙ оценки, не авторской подсказки. Пример паттерна: deploy-команда хочет ship потому что quarterly metrics; alignment-команда хочет hold потому что non-quantifiable concern; CEO хочет split-the-difference потому что board pressure.

**`incentive-weak-cal.md`** (~300 слов): зеркальное — мотивации **декларированы** через диалог («Я хочу X, потому что Y»), но действия не следуют из них. Персонажи объявляют интересы, действуют по сценарию. Cost-benefit не виден.

- [ ] **Step 2.2: Создать holdout pair (другие шоу/контексты)**

**`incentive-strong-holdout.md`** (~300 слов): сценка из неперекрывающегося контекста. Конкурирующие интересы — в корпоративной/политической/семейной структуре, **не из AI-domain**. Структура «cost-benefit драйвит action» та же.

**`incentive-weak-holdout.md`** (~300 слов): зеркальное, тот же неперекрывающийся контекст. Декларация-без-действия паттерн.

- [ ] **Step 2.3: Создать `.claude/agents/incentive-cartographer.md`**

Полная структура аналогично Task 1, с подменами:

- `name: incentive-cartographer`
- `description: Адверсариальный критик мотивационной структуры. Вызывается перед финализацией сцен/арок через adversarial-review-pass. Различает декларацию ("я хочу X") от реальной incentive-структуры (действия следуют из cost-benefit).`
- Калибровочный блок:
  ```
  - story-bible/thesis.md
  - CLAUDE.md законы проекта
  - 1-2 примера positive из golden/conflicts/ (Succession siblings, Stringer-Avon, Walt-Hank, Severance innie/outie если наполнены; иначе fallback)
  - 1 anti из golden/anti-examples/conflicts/ — **на момент Phase 2 категория ПУСТА (D-002 P-15)**. Заполни golden_unavailable_reason: category-empty
  ```
- Обязательный проход:
  ```
  1. Для каждого названного персонажа сформулируй: что он хочет, что готов потерять.
  2. Прокатай каждое action в артефакте через «следует ли это из (1)?». Если нет — flag.
  3. Найди декларации мотивов («Я хочу X»). Сверь с действиями ниже по артефакту. Расхождение = concern.
  4. Counter-test для pass — 3 элемента what_searched/why_this/why_not_found.
  ```
- «Что НИКОГДА не делаешь» — общие 5 пунктов + critic-specific:
  ```
  - Не путаешь декларацию с incentive. Слова — не мотивация.
  - Не принимаешь "потому что" как объяснение, если нет cost-benefit структуры.
  ```

- [ ] **Step 2.4: Создать `.claude/agents/incentive-cartographer-pressure-tests.md`**

```markdown
# A3 INCENTIVE — Pressure tests (RED scenarios)

## Известное ограничение
`golden/anti-examples/conflicts/` пуст (D-002 P-15). Dedicated RED-anti для A3 в `tests/regression/strawmen/` либо `moralizing/` не созданы в Phase 2. Pressure-tests опираются на:
- **`incentive-weak-cal.md`** и **`incentive-weak-holdout.md`** — критик должен дать `veto` или `concern-severity-high`
- Cross-validation: A3 на `moralizing-character-arc-01.md` (Task 3) должен также дать concern (декларация-как-incentive)

## RED-1: weak-calibration-pair
**Файл:** `tests/regression/pairs/calibration/incentive-weak-cal.md`
**Expected verdict:** `veto` или `concern-severity-high`
**Expected reasoning:** «декларация без cost-benefit», конкретный персонаж + конкретная строка где declaration ≠ action

## RED-2: weak-holdout-pair
**Файл:** `tests/regression/pairs/holdout/incentive-weak-holdout.md`
**Expected verdict:** `veto`
**Acceptance:** critic distinguishes на материале из не-AI контекста

## RED-3 (cross-critic): moralizing-character-arc-01 (Task 3)
**Файл:** `tests/regression/moralizing/moralizing-character-arc-01.md` (создаётся в Task 3)
**Expected verdict from A3:** `concern` — character действует по сценарию, не из incentive

## P-10 acceptance
A3 даёт pass на `incentive-weak-cal.md` или `incentive-weak-holdout.md` = провал калибровки.

## Phase 2 Task 7 verification
Дополнительно: проверить cross-validation между A3 и A5 на `moralizing-monolog-01.md` (Task 1) — A3 даёт `concern` или `pass` (артефакт скорее philosophical, не incentive), A5 даёт `veto`. Если совпали `veto` обоих — flag избыточности (spec § 9.4.c).

## Known issue для ПП2
Если на smoke-test (Phase 4) A3 даст систематический pass на всех 4 артефактах — фиксируется как ПП2 follow-up: запросить B.4.1 anti-examples-batch-02 у Cowork.
```

- [ ] **Step 2.5: Validate frontmatter**

```bash
python -m tools.frontmatter_validator --root tests/regression/
python -m tools.frontmatter_validator --root .claude/agents/
```

Expected: exit 0.

- [ ] **Step 2.6: Commit**

```bash
git add .claude/agents/incentive-cartographer.md \
        .claude/agents/incentive-cartographer-pressure-tests.md \
        tests/regression/pairs/calibration/incentive-*.md \
        tests/regression/pairs/holdout/incentive-*.md
git commit -m "$(cat <<'EOF'
agent: A3 incentive-cartographer — субагент + pressure-tests + regression pairs

Phase 2 ПП1 — Task 2 (A3 INCENTIVE/CONFLICT):
- .claude/agents/incentive-cartographer.md (Opus + effort: max + READ-ONLY tools)
- .claude/agents/incentive-cartographer-pressure-tests.md (известное ограничение D-002 P-15)
- 1 calibration пара + 1 holdout пара (P-5 split)

Known issue: golden/anti-examples/conflicts/ = 0 (D-002 P-15). Pressure-tests опираются
на weak-pairs + cross-validation с A2/A5. Если smoke-test покажет systematic pass —
ПП2 follow-up: запросить B.4.1 anti-examples-batch-02.

Связь: spec § 4.2 + § 9.4.a + § 9.4.b + § 9.4.c; D-002 P-5 + P-7 + P-15.

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>
EOF
)"
```

---

## Task 3: A2 CHARACTER — character-truth-keeper.md

**Роль:** A2 — критик характерной правды. Ловит «декларация = character» (заявленные черты без поведенческих проявлений), «arc-как-урок» (character меняется потому что сценарий хочет), «функция-вместо-человека».

**Files:**
- Create: `.claude/agents/character-truth-keeper.md`
- Create: `.claude/agents/character-truth-keeper-pressure-tests.md`
- Create: `tests/regression/moralizing/moralizing-character-arc-01.md`
- Create: `tests/regression/pairs/calibration/character-strong-cal.md`
- Create: `tests/regression/pairs/calibration/character-weak-cal.md`
- Create: `tests/regression/pairs/holdout/character-strong-holdout.md`
- Create: `tests/regression/pairs/holdout/character-weak-holdout.md`

### Steps

- [ ] **Step 3.1: Создать moralizing-character-arc-01 RED**

**Файл `tests/regression/moralizing/moralizing-character-arc-01.md`** (~350 слов): character arc где персонаж в начале «не понимает», в середине «сталкивается с уроком», в финале «осознаёт». Каждый сюжетный поворот — урок (lesson-as-plot). Внутренняя жизнь не показана через действия, только через декларации «теперь я понимаю».

Frontmatter:
```yaml
---
id: moralizing-character-arc-01
version: 1
status: draft
type: regression-red
red_pattern: arc-as-lesson
expected_verdict_from: [A2, A5, A3]
expected_verdict: veto
expected_severity: high
references: []
---
```

- [ ] **Step 3.2: Создать calibration pair**

Frontmatter общий:
```yaml
---
id: character-strong-cal | character-weak-cal
version: 1
status: draft
type: regression-pair
pair_role: A2
pair_strength: strong | weak
pair_split: calibration
expected_verdict: pass | veto
references: []
---
```

**`character-strong-cal.md`** (~300 слов): сцена показывающая персонажа через **противоречие действий и слов** (говорит одно, делает другое — не от лжи, от сложности). Внутренняя жизнь видна через жесты, паузы, choice-of-words. Пример: «тревожная компетентность» — character демонстрирует expertise + физическое тело-language тревоги одновременно.

**`character-weak-cal.md`** (~300 слов): зеркальное — character объявляет свои черты («Я всегда сомневаюсь...») в диалоге, потом ведёт себя ровно по declaration. Нет противоречия, нет внутренней жизни. Функция, не человек.

- [ ] **Step 3.3: Создать holdout pair (другие шоу)**

**`character-strong-holdout.md`** + **`character-weak-holdout.md`** — на материале из неперекрывающегося контекста (другие архетипы: например, не «тревожная компетентность», а «cynical mentor» или «over-prepared subordinate»). Структура «contradiction → внутренняя жизнь» та же.

- [ ] **Step 3.4: Создать `.claude/agents/character-truth-keeper.md`**

Подмены:
- `name: character-truth-keeper`
- `description: Критик характерной правды. Ловит decladration-as-character, arc-as-lesson, функция-вместо-человека. Вызывается через adversarial-review-pass перед финализацией сцены или эпизода.`
- Калибровка:
  ```
  - story-bible/thesis.md
  - characters/<если есть> — character sheets как контекст
  - 1-2 positive из golden/characters/ (Carmela, Peggy, Fleabag, Nora, Kim, Shiv, BoJack)
  - 1 anti из golden/anti-examples/characters/ (Dexter, GoT finale)
  ```
- Обязательный проход:
  ```
  1. Для каждого появляющегося персонажа: какие черты объявлены (явно или через сюжетную подачу)?
  2. Какие действия в артефакте подтверждают / противоречат / illuminate эти черты?
  3. Найди декларации-без-подкрепления (character говорит "я X", но в артефакте нет действия, читающегося как X).
  4. Найди arc-as-lesson: персонаж меняется потому что плот требует, не потому что внутренняя логика толкает.
  5. Counter-test для pass: что специально искал (например, "не нашёл contradictions говорит/делает"), почему именно это, почему не нашёл.
  ```
- «Никогда»:
  ```
  - Не принимаешь экспозицию как характеризацию.
  - Не путаешь архетип с характером (архетип — стартовая точка, не конец).
  - Не оправдываешь "недостаток развития" словами "это короткая сцена".
  ```

- [ ] **Step 3.5: Создать `.claude/agents/character-truth-keeper-pressure-tests.md`**

3 RED-сценария:
- **RED-1:** `moralizing/moralizing-character-arc-01.md` — expected veto (arc-as-lesson)
- **RED-2:** `pairs/calibration/character-weak-cal.md` — expected veto (declaration ≠ behavior)
- **RED-3:** `pairs/holdout/character-weak-holdout.md` — expected veto на материале другого архетипа
- **Cross-validation:** A2 на `moralizing-monolog-01.md` (Task 1) — concern (характер реагирующего «слушающего» персонажа не виден, функция-setup-вопросов)

- [ ] **Step 3.6: Validate + commit**

```bash
python -m tools.frontmatter_validator --root tests/regression/
python -m tools.frontmatter_validator --root .claude/agents/

git add .claude/agents/character-truth-keeper.md \
        .claude/agents/character-truth-keeper-pressure-tests.md \
        tests/regression/moralizing/moralizing-character-arc-01.md \
        tests/regression/pairs/calibration/character-*.md \
        tests/regression/pairs/holdout/character-*.md
git commit -m "$(cat <<'EOF'
agent: A2 character-truth-keeper — субагент + pressure-tests + regression artifacts

Phase 2 ПП1 — Task 3 (A2 CHARACTER):
- .claude/agents/character-truth-keeper.md (Opus + effort: max + READ-ONLY tools)
- .claude/agents/character-truth-keeper-pressure-tests.md (3 RED + cross-validation)
- moralizing/moralizing-character-arc-01.md (arc-as-lesson RED)
- 1 calibration пара + 1 holdout пара (P-5 split)

Verdict acceptance: RED → veto; weak-pair → veto; strong-pair → pass с counter_test.
Связь: spec § 4.2 + § 4.3; D-002 P-5 + P-7 + P-8.

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>
EOF
)"
```

---

## Task 4: A1 LORE — lore-realism-checker.md

**Роль:** A1 — критик реалистичности механизмов мира (корп-структуры, политика, технические детали, regulatory landscape). Ловит fantasy-incentive (несуществующие структуры поданы как очевидные), tech-handwaving, anachronism.

**Files:**
- Create: `.claude/agents/lore-realism-checker.md`
- Create: `.claude/agents/lore-realism-checker-pressure-tests.md`
- Create: `tests/regression/pairs/calibration/lore-strong-cal.md`
- Create: `tests/regression/pairs/calibration/lore-weak-cal.md`
- Create: `tests/regression/pairs/holdout/lore-strong-holdout.md`
- Create: `tests/regression/pairs/holdout/lore-weak-holdout.md`

> Нет dedicated RED-anti для A1 в strawmen/moralizing (паттерны не пересекаются). Calibration + holdout pairs + cross-validation — основа pressure-test.

### Steps

- [ ] **Step 4.1: Создать calibration pair**

Frontmatter общий:
```yaml
---
id: lore-strong-cal | lore-weak-cal
version: 1
status: draft
type: regression-pair
pair_role: A1
pair_strength: strong | weak
pair_split: calibration
expected_verdict: pass | veto
references: []
---
```

**`lore-strong-cal.md`** (~300 слов): фрагмент мира (например, описание AI labs корп-структуры) с **конкретными, верифицируемыми** деталями — board composition, regulatory exposure (NIST/EU AI Act), capital structure (PBC), известные публично policy commitments. Реалистично.

**`lore-weak-cal.md`** (~300 слов): зеркальный фрагмент — fantasy-mechanism («Совет Этики ИИ из 5 человек выдаёт лицензии») поданный как очевидная реалистичная структура. Несуществующее regulatory body, нереалистичная capital structure.

- [ ] **Step 4.2: Создать holdout pair**

**`lore-strong-holdout.md`** + **`lore-weak-holdout.md`** — на материале **не из AI-domain**. Например, корп-структура biotech / finance / aerospace. Same pattern: strong = verifiable details; weak = fantasy.

- [ ] **Step 4.3: Создать `.claude/agents/lore-realism-checker.md`**

Подмены:
- `name: lore-realism-checker`
- `description: Критик реалистичности механизмов мира. Ловит несуществующие корп-структуры, fantasy regulatory bodies, tech-handwaving. Использует Grep/Glob для cross-reference с тезисом + world-rules.`
- Калибровка:
  ```
  - story-bible/thesis.md
  - story-bible/world-rules.md (если есть)
  - 1-2 примера из golden/scenes/ или golden/conflicts/ где world detail сильно (Severance corp structure; Succession board mechanics; Mr Robot tech-realism)
  - golden/anti-examples/ — категория для A1 не выделена; cross-check с golden/scenes/ anti на tech-handwaving
  ```
- Обязательный проход:
  ```
  1. Перечисли названные механизмы (корп-структуры, regulatory bodies, technical claims, политические institutions).
  2. Для каждого: верифицируем ли он? (реальная структура / publicly known policy / known tech limit). Если нет — flag.
  3. Найди handwaving («Совет одобрил»; «Регулятор требует» — без конкретики).
  4. Найди anachronism: технические детали из неверной эпохи (например, GPT-2-era claims в 2026 setting).
  5. Counter-test: что искал — конкретные несуществующие institutions, конкретные tech-handwave, конкретные anachronisms; почему именно это — реалистичность миры центральна для AI-safety тезиса; почему не нашёл.
  ```
- «Никогда»:
  ```
  - Не принимаешь "это художественный мир" как оправдание fantasy-structure.
  - Не критикуешь стилистический выбор (краткость, метафору) как нереалистичность.
  - Не путаешь "может произойти" (futurism) с "уже существует".
  ```

- [ ] **Step 4.4: Создать `.claude/agents/lore-realism-checker-pressure-tests.md`**

3 RED-сценария:
- **RED-1:** `pairs/calibration/lore-weak-cal.md` — expected veto (fantasy AI regulatory body)
- **RED-2:** `pairs/holdout/lore-weak-holdout.md` — expected veto на не-AI-domain material
- **RED-3:** cross-validation на любом из smoke-test (Phase 4) артефактов — если в `thesis.md` появится non-verifiable institutional claim, A1 даёт concern

- [ ] **Step 4.5: Validate + commit**

```bash
python -m tools.frontmatter_validator --root tests/regression/
python -m tools.frontmatter_validator --root .claude/agents/

git add .claude/agents/lore-realism-checker.md \
        .claude/agents/lore-realism-checker-pressure-tests.md \
        tests/regression/pairs/calibration/lore-*.md \
        tests/regression/pairs/holdout/lore-*.md
git commit -m "$(cat <<'EOF'
agent: A1 lore-realism-checker — субагент + pressure-tests + regression pairs

Phase 2 ПП1 — Task 4 (A1 LORE):
- .claude/agents/lore-realism-checker.md (Opus + effort: max + READ-ONLY tools)
- .claude/agents/lore-realism-checker-pressure-tests.md (3 RED + cross-validation)
- 1 calibration пара + 1 holdout пара (P-5 split)

Verdict acceptance: weak-pairs → veto (fantasy mechanism / handwaving); strong-pairs → pass.
Связь: spec § 4.2 + § 4.3; D-002 P-5 + P-7 + P-8.

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>
EOF
)"
```

---

## Task 5: A4 VOICE/DIALOGUE — voice-differentiator.md

**Роль:** A4 — детектор voice-bleed. Запускается **только на сценах с >1 говорящим** (на не-сценах фиксирует `not_applicable: <reason>`, P-3). Использует TF-IDF cosine как preflight (через скилл `voice-check` Phase 3; в Phase 2 — Phase 1 `voice_dissimilarity.py` используется manually для verification).

**Files:**
- Create: `.claude/agents/voice-differentiator.md`
- Create: `.claude/agents/voice-differentiator-pressure-tests.md`
- Create: `tests/regression/voice-bleed/voice-bleed-uniform-01.md`
- Create: `tests/regression/voice-bleed/voice-bleed-narrator-01.md`
- Create: `tests/regression/pairs/calibration/voice-strong-cal.md`
- Create: `tests/regression/pairs/calibration/voice-weak-cal.md`
- Create: `tests/regression/pairs/holdout/voice-strong-holdout.md`
- Create: `tests/regression/pairs/holdout/voice-weak-holdout.md`

### Steps

- [ ] **Step 5.1: Создать 2 voice-bleed RED artifacts**

**`voice-bleed-uniform-01.md`** (~350 слов): сцена с 3 говорящими в формате `**ИМЯ:** реплика`. Все 3 используют один лексический регистр, одну сложность синтаксиса, одни вводные слова. Идентичный voice, нет различий.

Frontmatter:
```yaml
---
id: voice-bleed-uniform-01
version: 1
status: draft
type: regression-red
red_pattern: voice-bleed-uniform
expected_verdict_from: [A4]
expected_verdict: veto
expected_severity: high
expected_voice_dissim_sim: ">0.65"  # voice_dissimilarity preflight должен flagнуть
references: []
---
```

**`voice-bleed-narrator-01.md`** (~350 слов): сцена с 2 говорящими, но narrator-voice проникает в реплики (литературный синтаксис, авторские оценочные слова, perfect grammar в casual contexts). Реплики звучат как если бы narrator pereskazyvает диалог, не как живая речь.

Frontmatter:
```yaml
---
id: voice-bleed-narrator-01
version: 1
status: draft
type: regression-red
red_pattern: voice-bleed-narrator
expected_verdict_from: [A4]
expected_verdict: veto
expected_severity: medium
expected_voice_dissim_sim: ">0.55"  # narrator-bleed может быть ниже uniform threshold
references: []
---
```

- [ ] **Step 5.2: Verify voice_dissimilarity ловит RED-1**

```bash
python -m tools.voice_dissimilarity tests/regression/voice-bleed/voice-bleed-uniform-01.md --threshold 0.65
```

Expected: exit 1 (sim > 0.65) либо exit 0 с warning. Если exit 0 без warning — RED недостаточно extreme, переписать с более явным voice-bleed.

```bash
python -m tools.voice_dissimilarity tests/regression/voice-bleed/voice-bleed-narrator-01.md --threshold 0.65
```

Expected: либо exit 1, либо exit 0 (narrator-bleed может быть subtle для TF-IDF — это контентный сигнал для A4 voice критика, не для preflight). Зафиксировать выход в pressure-tests.md.

- [ ] **Step 5.3: Создать calibration pair**

Frontmatter общий:
```yaml
---
id: voice-strong-cal | voice-weak-cal
version: 1
status: draft
type: regression-pair
pair_role: A4
pair_strength: strong | weak
pair_split: calibration
expected_verdict: pass | veto
expected_voice_dissim_sim: "<0.65" | ">0.65"
references: []
---
```

**`voice-strong-cal.md`** (~350 слов): сцена с 3 говорящими (researcher / engineer / manager) — каждый со своим регистром (researcher academic-careful; engineer compact-technical; manager corporate-soft). Voice-dissimilarity preflight < 0.65 на всех парах.

**`voice-weak-cal.md`** (~350 слов): зеркальное — те же 3 роли, но voice uniform или почти uniform.

- [ ] **Step 5.4: Создать holdout pair**

Аналогично, на других ролях (например, doctor / patient / family member). Material из не-AI-domain.

- [ ] **Step 5.5: Verify voice_dissimilarity на calibration + holdout**

```bash
python -m tools.voice_dissimilarity tests/regression/pairs/calibration/voice-strong-cal.md --threshold 0.65
python -m tools.voice_dissimilarity tests/regression/pairs/calibration/voice-weak-cal.md --threshold 0.65
python -m tools.voice_dissimilarity tests/regression/pairs/holdout/voice-strong-holdout.md --threshold 0.65
python -m tools.voice_dissimilarity tests/regression/pairs/holdout/voice-weak-holdout.md --threshold 0.65
```

Expected:
- strong-cal: exit 0 (sim < 0.65) — strong voices различимы
- weak-cal: exit 1 (sim > 0.65) — weak voices uniform
- strong-holdout: exit 0
- weak-holdout: exit 1

Если несоответствие — переписать пары до соответствия.

- [ ] **Step 5.6: Создать `.claude/agents/voice-differentiator.md`**

Подмены:
- `name: voice-differentiator`
- `description: Критик voice-bleed в диалогах. ВЫЗЫВАЕТСЯ ТОЛЬКО НА СЦЕНАХ с >1 говорящим в формате **ИМЯ:** реплика. На не-сценах фиксирует verdict=not_applicable+not_applicable_reason. Использует TF-IDF preflight (skill voice-check) для structural детекции; даёт content verdict.`
- Калибровка:
  ```
  - golden/dialogues/ (Sorkin walk-and-talk; Fleabag fourth-wall; Mad Men HARRIS-OLSON; House of Cards Underwood-voice anti)
  - golden/anti-examples/dialogue-bleed/ (TD2 в anti-batch-01, House of Cards если доступен)
  - story-bible/thesis.md (для понимания tonal range)
  ```
- Обязательный проход:
  ```
  1. Если артефакт НЕ сцена (нет паттерна **ИМЯ:** реплика) — fix verdict=pass + not_applicable_reason="артефакт не содержит диалога".
  2. Для каждой пары говорящих: вычисли (mental shorthand) — какие лексические/синтаксические маркеры различают voice А от voice Б. Если не нашёл хотя бы 2 маркера — flag voice-bleed.
  3. Найди narrator-bleed: реплики используют литературные конструкции, perfect grammar в casual moments, оценочные слова, которые должны быть в narrator-комментарии, не в характере.
  4. Найди register-flattening: технические темы стираются до uniform corporate-talk; emotional moments — до uniform "I feel..." declarations.
  5. Counter-test для pass: what_searched = "конкретные lexical/syntactic differentiators между парами говорящих"; why_this = "voice-bleed центральный риск multi-speaker scenes"; why_not_found = "артефакт показывает X конкретных различительных маркеров — перечислить".
  ```
- «Никогда»:
  ```
  - Не путаешь diversity акцентов (хорошо) с inconsistency voice (плохо).
  - Не флагуешь similar voices если они логичны (e.g., близнецы; команда привыкла друг к другу).
  - Не пишешь pass без перечисления конкретных lexical markers различия.
  ```

- [ ] **Step 5.7: Создать `.claude/agents/voice-differentiator-pressure-tests.md`**

```markdown
# A4 VOICE — Pressure tests (RED scenarios)

## RED-1: voice-bleed-uniform
**Файл:** `tests/regression/voice-bleed/voice-bleed-uniform-01.md`
**Voice_dissimilarity preflight:** sim > 0.65 (exit 1) — preflight ОБЯЗАН flagнуть
**Expected A4 verdict:** `veto` severity:high

## RED-2: voice-bleed-narrator
**Файл:** `tests/regression/voice-bleed/voice-bleed-narrator-01.md`
**Voice_dissimilarity preflight:** результат документировать после Step 5.2 (может быть subtle для TF-IDF — это content-уровень сигнал, не structural)
**Expected A4 verdict:** `veto` или `concern-severity-medium`
**Acceptance:** A4 явно идентифицирует narrator-bleed pattern, не только uniform similarity

## RED-3: weak-calibration-pair
**Файл:** `tests/regression/pairs/calibration/voice-weak-cal.md`
**Voice_dissimilarity preflight:** sim > 0.65
**Expected A4 verdict:** `veto` severity:high

## RED-4: weak-holdout-pair
**Файл:** `tests/regression/pairs/holdout/voice-weak-holdout.md`
**Expected A4 verdict:** `veto`
**Acceptance:** работает на материале не из AI-domain

## not_applicable verdict (P-3)
A4 на любом non-scene артефакте (`thesis.md`, `world-rules.md`, character sheet) ОБЯЗАН вернуть `verdict: pass + not_applicable_reason: "артефакт не содержит диалога в формате **ИМЯ:** реплика"`. Это валидируется в Task 7 на artifacts из Phase 4.

## P-10 acceptance
A4 даёт pass на любом из RED-1..RED-4 (без not_applicable_reason) = провал калибровки. A4 даёт content-verdict (не not_applicable) на non-scene артефакте = провал.
```

- [ ] **Step 5.8: Validate + commit**

```bash
python -m tools.frontmatter_validator --root tests/regression/
python -m tools.frontmatter_validator --root .claude/agents/

git add .claude/agents/voice-differentiator.md \
        .claude/agents/voice-differentiator-pressure-tests.md \
        tests/regression/voice-bleed/ \
        tests/regression/pairs/calibration/voice-*.md \
        tests/regression/pairs/holdout/voice-*.md
git commit -m "$(cat <<'EOF'
agent: A4 voice-differentiator — субагент + pressure-tests + voice-bleed regression

Phase 2 ПП1 — Task 5 (A4 VOICE/DIALOGUE):
- .claude/agents/voice-differentiator.md (Opus + effort: max + READ-ONLY tools + P-3 not_applicable)
- .claude/agents/voice-differentiator-pressure-tests.md (4 RED + not_applicable + P-10)
- 2 voice-bleed RED (uniform + narrator) + 1 calibration пара + 1 holdout пара
- voice_dissimilarity preflight verified на 6 файлах (документировано в pressure-tests)

Verdict acceptance: voice-bleed → veto/concern; weak-pairs → veto; non-scene → pass+not_applicable.
Связь: spec § 4.2 + § 4.3 + P-3; D-002 P-3 + P-5 + P-7 + P-8.

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>
EOF
)"
```

---

## Task 6: A6 AUDIENCE — audience-bored-detector.md

**Роль:** A6 — детектор «скучно» / «гладко» с позиции зрителя. Известное ограничение: **нет собственной golden/audience/ категории** (D-002 B.4.3 (b)). Калибруется через cross-references из других категорий (audience-affect observations в scenes / characters / theses).

**Files:**
- Create: `.claude/agents/audience-bored-detector.md`
- Create: `.claude/agents/audience-bored-detector-pressure-tests.md`
- Create: `tests/regression/pairs/calibration/audience-strong-cal.md`
- Create: `tests/regression/pairs/calibration/audience-weak-cal.md`
- Create: `tests/regression/pairs/holdout/audience-strong-holdout.md`
- Create: `tests/regression/pairs/holdout/audience-weak-holdout.md`

> **Известное ограничение (D-002 B.4.3 (b)):** `golden/audience/` не создаётся в ПП1. A6 калибруется на audience-affect observations из других golden категорий. Если в Task 7 A6 даст систематический pass / confuse — открытие audience category в ПП2 (D-004 potentially).

### Steps

- [ ] **Step 6.1: Создать calibration pair**

Frontmatter общий:
```yaml
---
id: audience-strong-cal | audience-weak-cal
version: 1
status: draft
type: regression-pair
pair_role: A6
pair_strength: strong | weak
pair_split: calibration
expected_verdict: pass | veto
references: []
---
```

**`audience-strong-cal.md`** (~300 слов): фрагмент эпизода (либо сцена либо arc summary) с **узнаваемым audience-affect hook** — momentum, payoff после setup, character investment делает зрителю важно. Пример: HARRIS-OLSON-style emotional peak earned through setup (Schmidt-style).

**`audience-weak-cal.md`** (~300 слов): зеркальное — гладкая, технически правильная сценка без hook. Все правильно, но зрителю нечего держать. Pattern: «competent but empty». Audience-affect = «watchable but forgettable».

- [ ] **Step 6.2: Создать holdout pair**

Аналогично, на материале другого жанра / другой эпохи (e.g., домашняя драма вместо AI-thriller).

- [ ] **Step 6.3: Создать `.claude/agents/audience-bored-detector.md`**

Подмены:
- `name: audience-bored-detector`
- `description: Критик audience-affect. Детектирует "competent but empty" — артефакт правильный, но зрителю нечего держать. ИЗВЕСТНОЕ ОГРАНИЧЕНИЕ: нет собственной golden/audience/ категории; калибруется через cross-references из scenes/characters/theses.`
- Калибровка:
  ```
  - golden/scenes/ — audience-affect observations (Schmidt "earned emotional peak"; Mr Robot momentum; Severance hook)
  - golden/characters/ — характеры с investment hooks (BoJack, Kim, Carmela)
  - golden/theses/ — где тезис генерирует hook (Karnofsky stakes-setting; Brooker Third Limb metaphor)
  - golden_unavailable_reason: category-irrelevant — для отсутствующей audience/ категории; обоснование: D-002 B.4.3 (b) принят
  ```
- Обязательный проход:
  ```
  1. Найди 2-3 hook'а в артефакте: что заставляет зрителя продолжать?
  2. Найди competent-but-empty паттерны: правильная структура без stake.
  3. Найди over-explanation: setup'ы которые лучше через action than dialogue.
  4. Counter-test для pass: что искал — конкретные moments where audience could disengage; почему именно это — A6 одинокий "user-perspective" критик в системе; почему не нашёл.
  ```
- «Никогда»:
  ```
  - Не путаешь "не понравится массовой аудитории" с "слабо как craft" (мы не делаем broad appeal).
  - Не критикуешь сложность как boring (наоборот — простота без layer'ов часто и есть boring).
  - Не пишешь pass без перечисления конкретных hook'ов которые ты идентифицировал.
  ```

- [ ] **Step 6.4: Создать `.claude/agents/audience-bored-detector-pressure-tests.md`**

```markdown
# A6 AUDIENCE — Pressure tests (RED scenarios)

## Известное ограничение
Нет собственной `golden/audience/` категории (D-002 B.4.3 (b)). Калибровка через cross-references. `golden_unavailable_reason: category-irrelevant` в каждом отчёте A6.

## RED-1: weak-calibration-pair
**Файл:** `tests/regression/pairs/calibration/audience-weak-cal.md`
**Expected verdict:** `veto` или `concern-severity-medium`
**Expected reasoning:** «competent-but-empty», конкретные moments where audience disengages

## RED-2: weak-holdout-pair
**Файл:** `tests/regression/pairs/holdout/audience-weak-holdout.md`
**Expected verdict:** `veto`/`concern`
**Acceptance:** работает на материале другого жанра

## RED-3 (cross): moralizing-monolog-01 (Task 1)
**Файл:** `tests/regression/moralizing/moralizing-monolog-01.md`
**Expected A6 verdict:** `veto` (моралистические монологи характерны для boring scene)
**Acceptance:** cross-validation с A5 — A5 даёт veto за strawman + author-voice; A6 даёт veto за boredom; структурно разные reasoning (spec § 9.4.c)

## P-10 acceptance
A6 даёт `pass` на любом RED = провал калибровки.

## Known issue для ПП2 (D-004 trigger)
Если на 4 smoke-test артефактах A6 даёт всё-pass (systematic auto-approval) — открыть `golden/audience/` (B.4.3 (a) alternative) и пересмотреть калибровку. Documented в `docs/log.md` как ПП2 follow-up.
```

- [ ] **Step 6.5: Validate + commit**

```bash
python -m tools.frontmatter_validator --root tests/regression/
python -m tools.frontmatter_validator --root .claude/agents/

git add .claude/agents/audience-bored-detector.md \
        .claude/agents/audience-bored-detector-pressure-tests.md \
        tests/regression/pairs/calibration/audience-*.md \
        tests/regression/pairs/holdout/audience-*.md
git commit -m "$(cat <<'EOF'
agent: A6 audience-bored-detector — субагент + pressure-tests + regression pairs

Phase 2 ПП1 — Task 6 (A6 AUDIENCE):
- .claude/agents/audience-bored-detector.md (Opus + effort: max + READ-ONLY tools)
- .claude/agents/audience-bored-detector-pressure-tests.md (3 RED + cross-validation + D-004 trigger)
- 1 calibration пара + 1 holdout пара (P-5 split)

Known issue: golden/audience/ не создаётся в ПП1 (D-002 B.4.3 (b)).
golden_unavailable_reason: category-irrelevant в каждом отчёте A6. Если smoke-test
покажет systematic pass — D-004 trigger: открыть audience категорию в ПП2.

Связь: spec § 4.2 + § 4.3; D-002 B.4.3 (b) + P-5 + P-7 + P-8.

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>
EOF
)"
```

---

## Task 7: Phase 2 acceptance — subagent invocation + report validation

**Roоль:** проверить что все 6 субагентов фактически работают (выдают valid YAML report при invocation через Task tool) и pressure-tests дают expected verdicts.

**Files:**
- Update: `docs/log.md` — final acceptance entry
- Create: `tmp/critic-reports/phase2-acceptance/<critic>-<timestamp>.yaml` (×6 minimum) — ephemeral, gitignored
- Optional: `docs/cowork-notes/phase2-pressure-test-results.md` — если есть surprises или known issues to surface

### Steps

> **Important:** Task 7 выполняется **orchestrator-сессией (мной)**, не implementer-субагентом. Реальная invocation субагентов через Task tool — это user-context действие, требующее approval за токены (Opus + effort: max). Implementer самостоятельно может попробовать но verification остаётся за orchestrator.

- [ ] **Step 7.1: Invoke A5 philosophy-adversarial на 4 RED артефактах**

Из orchestrator-сессии:

```
Task(
  subagent_type="philosophy-adversarial",
  description="Pressure-test RED-1 A5",
  prompt="Прочитай tests/regression/strawmen/strawman-alarmist-01.md и выдай YAML-отчёт по обязательному формату из своего system prompt. Артефакт — намеренно плохой strawman; expected verdict — veto с severity high."
)
```

Аналогично для RED-2 (strawman-sceptic-01), RED-3 (strawman-moralizing-01), RED-4 (moralizing-monolog-01).

После каждого invocation:
1. Записать YAML output в `tmp/critic-reports/phase2-acceptance/A5-<red-id>-<timestamp>.yaml`
2. Validate через `python -m tools.critic_report_validator tmp/critic-reports/phase2-acceptance/A5-<red-id>-<timestamp>.yaml --smoke-test`
3. Verify expected verdict в YAML

Expected всех 4: `verdict: veto` или `verdict: concern` с severity high, valid format.

- [ ] **Step 7.2: Invoke A3 incentive-cartographer на pressure-test artifacts**

```
Task(subagent_type="incentive-cartographer", ...) на:
- tests/regression/pairs/calibration/incentive-weak-cal.md (expected veto/concern)
- tests/regression/pairs/holdout/incentive-weak-holdout.md (expected veto)
- tests/regression/moralizing/moralizing-character-arc-01.md (expected concern — cross-validation с A2)
```

Validate каждый report через critic_report_validator --smoke-test.

- [ ] **Step 7.3: Invoke A2 character-truth-keeper**

```
Task(subagent_type="character-truth-keeper", ...) на:
- tests/regression/moralizing/moralizing-character-arc-01.md (expected veto)
- tests/regression/pairs/calibration/character-weak-cal.md (expected veto)
- tests/regression/pairs/holdout/character-weak-holdout.md (expected veto)
- tests/regression/moralizing/moralizing-monolog-01.md (expected concern — listener-character как функция)
```

- [ ] **Step 7.4: Invoke A1 lore-realism-checker**

```
Task(subagent_type="lore-realism-checker", ...) на:
- tests/regression/pairs/calibration/lore-weak-cal.md (expected veto — fantasy regulatory body)
- tests/regression/pairs/holdout/lore-weak-holdout.md (expected veto — non-AI domain handwaving)
```

- [ ] **Step 7.5: Invoke A4 voice-differentiator**

```
Task(subagent_type="voice-differentiator", ...) на:
- tests/regression/voice-bleed/voice-bleed-uniform-01.md (expected veto, voice_dissim sim > 0.65)
- tests/regression/voice-bleed/voice-bleed-narrator-01.md (expected veto/concern, narrator-bleed)
- tests/regression/pairs/calibration/voice-weak-cal.md (expected veto)
- tests/regression/pairs/holdout/voice-weak-holdout.md (expected veto)
- tests/regression/strawmen/strawman-alarmist-01.md (expected pass+not_applicable — не сцена!)
```

Последний — P-3 not_applicable test.

- [ ] **Step 7.6: Invoke A6 audience-bored-detector**

```
Task(subagent_type="audience-bored-detector", ...) на:
- tests/regression/pairs/calibration/audience-weak-cal.md (expected veto/concern)
- tests/regression/pairs/holdout/audience-weak-holdout.md (expected veto/concern)
- tests/regression/moralizing/moralizing-monolog-01.md (expected veto — cross-validation с A5)
```

- [ ] **Step 7.7: Invoke на holdout STRONG для R-3.b verification**

Минимум 6 invocations — strong holdout pair каждого критика. Expected: `verdict: pass` с полным 3-element `counter_test_attempted`.

```
Task(subagent_type="philosophy-adversarial", ...) на philosophy-strong-holdout.md — expected pass
Task(subagent_type="character-truth-keeper", ...) на character-strong-holdout.md — expected pass
... и т.д. для A1, A3, A4, A6
```

Validate каждый через `critic_report_validator --smoke-test`. Check `counter_test_attempted.what_searched / why_this / why_not_found` все 3 заполнены.

- [ ] **Step 7.8: Verdicts diversity check (spec § 9.4.c)**

На общем pool (40-50 invocations всего):
- Минимум один случай где **A3 и A5 разошлись** структурно (один даёт veto за strawman, другой даёт concern за declaration-as-incentive). Если оба систематически согласны — flag в acceptance notes.
- Минимум один случай где A6 расходится с A2/A5 (audience-perspective verdict отличается от character / philosophy).
- `model_used` во всех отчётах = `opus`. Если хоть один Sonnet — flag, audit auto-switch, потенциально D-NNN escalation (cost-estimate § 10).

- [ ] **Step 7.9: Документировать known issues (если есть)**

Если в Steps 7.1-7.8 обнаружены:
- A3 систематический pass на 2+ RED (D-002 P-15 risk материализовался) — fixации в `docs/cowork-notes/phase2-pressure-test-results.md` + строка в log:
  ```
  [YYYY-MM-DD] note | ПП2 follow-up: A3 показал systematic pass на N/M RED — требуется B.4.1 anti-examples-batch-02
  ```
- A6 систематический pass на 2+ RED — D-004 trigger:
  ```
  [YYYY-MM-DD] note | ПП2 follow-up: A6 показал systematic pass — пересмотр B.4.3 (открыть audience категорию)
  ```
- Любой субагент `model_used: sonnet` — D-NNN escalation candidate.

- [ ] **Step 7.10: Phase 2 acceptance log entry**

Append в `docs/log.md`:

```
[2026-XX-XX] agent | Phase 2 ПП1 acceptance ✅ — 6 субагентов A1-A6 + pressure-tests + 31 regression artifacts; N/M RED invocations прошли с expected verdicts; M/N holdout-pairs verdicts разошлись (R-3.b); все critic-reports валидны через critic_report_validator --smoke-test. Known issues (если есть): [перечислить].
```

- [ ] **Step 7.11: Final commit**

```bash
git add docs/log.md
# Если есть cowork-notes для known issues:
git add docs/cowork-notes/phase2-pressure-test-results.md
git commit -m "$(cat <<'EOF'
milestone: Phase 2 ПП1 acceptance — 6 субагентов A1-A6 калиброваны и pressure-tested

Phase 2 ПП1 — Task 7:
- Все 6 субагентов получили реальную invocation через Task tool (~30-40 invocations суммарно)
- 100% YAML reports валидны через critic_report_validator --smoke-test
- Pressure-tests: критики дали expected verdict на RED-сценариях (исключения зафиксированы)
- R-3.b holdout-pairs: verdicts разошлись (strong→pass, weak→veto) — критики РАЗЛИЧАЮТ
- model_used: opus во всех отчётах (auto-switch не сработал)
- spec § 9.4.c cross-validation: A3 и A5 структурно расходились хотя бы раз
- P-3 not_applicable: A4 корректно возвращает not_applicable на не-сценах

Known issues (если есть): см. docs/cowork-notes/phase2-pressure-test-results.md и log entry.

Phase 3 (8 skills + 4 meta-skills-references) разблокирован.

Связь: spec § 4 + § 9.4 + § 9.5 + § 9.7 Definition of Done; D-002 P-3 + P-4 + P-5 + P-7 + P-8 + P-10.

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>
EOF
)"
```

---

## Dependencies + execution constraints

- **До старта Phase 2:** Phase 1 acceptance commit зелёный (✅ `025bb3f` 2026-05-30).
- **Auto-switch мониторинг — критично.** A5 PHILOSOPHY + A1 LORE на Opus + effort: max — самые дорогие по thinking tokens. На Max 5x подписке pacing < 60% window capacity. Task 7 — single most expensive Phase 2 шаг (40+ Opus invocations с effort: max). Распределить на 2 окна минимум.
- **Pacing рекомендация (cost-estimate § 9.4):**
  - **Окно 1:** Task 0 + Tasks 1-3 (A5 PHILOSOPHY + A3 INCENTIVE + A2 CHARACTER subagent files + regression artifacts)
  - **Окно 2:** Tasks 4-6 (A1 LORE + A4 VOICE + A6 AUDIENCE files + voice_dissimilarity preflight verification)
  - **Окно 3:** Task 7 — invocation acceptance (10-15 critic invocations)
  - **Окно 4:** Task 7 продолжение — оставшиеся invocations + log entry + final commit
- **P-15 / B.4.3 (b) acknowledged risks.** Если в Task 7 A3 или A6 покажут systematic auto-approval — это **известный flagged risk** (D-002 v2 acceptance включал явный пропуск B.4.1/B.4.2). НЕ блокер acceptance Phase 2 — фиксируется как ПП2 follow-up.
- **Resource budget.** ~50-70 messages mid на Phase 2 (cost-estimate раздел Phase 2 estimate); ~$0 marginal под Max 5x подписку.

---

## Self-review (per writing-plans skill)

**Spec coverage:**
- ✅ § 4.1 — 6 субагентов перечислены в Tasks 1-6
- ✅ § 4.2 — frontmatter с `model: opus`, `effort: max`, `tools: Read, Grep, Glob` (READ-ONLY) — в template + каждой Task
- ✅ § 4.3 — structured YAML output schema вставлена в каждый prompt
- ✅ § 9.4.a — RED regression set (strawmen / moralizing / voice-bleed) в Tasks 1, 3, 5
- ✅ § 9.4.b — calibration/holdout pairs (P-5 split) в каждой Task 1-6
- ✅ § 9.4.c — cross-validation проверка в Task 7 Step 7.8
- ✅ § 9.5 critical failures — каждый critical failure mapped в acceptance criteria Task 7
- ✅ § 9.7 Definition of Done — Task 7 Steps 7.1-7.10 покрывают все требования
- ✅ D-002 P-3 not_applicable — A4 (Task 5) и Step 7.5 + 7.11 commit message
- ✅ D-002 P-4 golden_unavailable_reason — в каждом subagent prompt калибровка
- ✅ D-002 P-5 calibration/holdout — в каждой Task 1-6
- ✅ D-002 P-7 counter_test_attempted — в YAML schema + Step 7.7
- ✅ D-002 P-8 effort: max — в frontmatter template
- ✅ D-002 P-10 «обошёл» = провал — в pressure-tests doc каждой Task
- ✅ D-002 P-15 flagged risks (A3 conflicts anti = 0; A6 audience category not opened) — Tasks 2, 6 + Step 7.9

**Placeholder scan:**
- ⚠️ Russian creative content (RED artifacts, calibration/holdout pairs) — описан **structurally** (что должно быть в файле, какой паттерн), но actual текст пишет implementer. Это **не placeholder** — это specification что implementer должен exucute (вроде «write 200-word RED artifact demonstrating strawman-alarmist pattern with no steel-man of sceptic position»).
- ⚠️ Subagent prompts — frontmatter exact, system prompt blocks с обязательными элементами specified, actual текст заполнения roles/calibration/passes — на implementer subagent. Опять же — specification, не placeholder.

Это допустимо в plan-документе для творческого слоя — implementer-субагент следует instructions для создания specific content.

**Type/path consistency:**
- ✅ Subagent names в frontmatter совпадают с filenames (kebab-case): philosophy-adversarial, incentive-cartographer, character-truth-keeper, lore-realism-checker, voice-differentiator, audience-bored-detector
- ✅ Регрессионные file paths consistent через все Tasks
- ✅ tmp/critic-reports/ path consistent с Phase 1 spec (P-9)
- ✅ tool invocations используют флаги Phase 1 (`--smoke-test`, `--threshold`)

---

## Expansion DONE — готов к execution

Запуск через `superpowers:subagent-driven-development` или `superpowers:executing-plans`. Recommended: subagent-driven для Tasks 0-6 (file creation tasks), orchestrator-direct для Task 7 (subagent invocation требует orchestrator-context).
