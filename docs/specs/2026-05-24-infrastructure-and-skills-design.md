---
id: spec-001-infrastructure-and-skills
title: Инфраструктура и скиллы Auto-ai-series — ПП1
version: 0.2
date: 2026-05-24
revised_on: 2026-05-29
revision_history:
  - "v0.1 (2026-05-24): первая редакция после brainstorming-сессии; approved"
  - "v0.2 (2026-05-29): применены P-1..P-15 правки D-002 v2 (accepted Тимуром 2026-05-29); P-6 разрешён через docs/cost-estimate-pp1.md (Max 5x подписочный сценарий); P-8 разрешён через docs/extended-thinking-mechanism.md (effort: max в frontmatter субагента)"
status: approved
relates_to:
  - decisions/D-001-bootstrap-architecture.md
  - decisions/D-002-spec-corrections-and-golden-plan.md
  - docs/cowork/prompt.md
  - docs/extended-thinking-mechanism.md
  - docs/cost-estimate-pp1.md
subproject: ПП1 (инфраструктура + smoke-test)
---

# Auto-ai-series — Дизайн ПП1: инфраструктура и скиллы

## 0. Контекст

**Проект.** Анимационный сериал об эволюции ИИ как психологическая и социальная драма. Центральный исследовательский вопрос (формулировка автора): не «станет ли ИИ злым?», а «что произойдёт, если сверхразум перестанет считать человечество зрелым и последовательным субъектом?». Полный текст конституции автора передан как первое сообщение brainstorming-сессии 2026-05-24.

**ПП1 в декомпозиции.** Проект декомпозирован на 5 под-проектов в порядке, заданном автором:
1. **ПП1 (этот спек):** инфраструктура и скиллы — мульти-агентный редакционный аппарат
2. **ПП2:** Story Bible v0.1 — центральный тезис, правила мира, тон, divergence map
3. **ПП3:** кор-каст (6-8 персонажей) + дизайн ИИ + дизайн человеческих архетипов
4. **ПП4:** регистр системных конфликтов incentives + адверсариальный отчёт
5. **ПП5+:** поэпизодный план сезона 1, затем сценарии эпизодов и сцен

Каждый под-проект — отдельный `spec → plan → implementation` цикл. ПП1 не пишет ни строчки Story Bible (это ПП2), но проводит smoke-test системы на мини-материале из конституции, чтобы убедиться, что инфраструктура работает на живом тексте.

**Базовые архитектурные решения** (полностью в `decisions/D-001-bootstrap-architecture.md`):

- **B-1.** Гибрид внешних агентов: Claude Code primary + Claude Desktop точечно + Claude Cowork как внешний ресёрч-собиратель. Codex выключен.
- **B-2.** Гибрид внутренних агентов: рутина через "шляпы" в одной Claude Code сессии, критика через изолированные Task-subagents в `.claude/agents/`.
- **B-3.** Знаниевый слой: markdown с frontmatter + lint-скрипт `consistency_check.py`. Без wiki/citation как в agentic-ops-cc.
- **B-4.** Язык: всё на русском (исключения — Section 10 Language Policy).
- **B-5.** Scope ПП1: инфра + smoke-test на мини-материале (тезис + 5 правил мира + 1 character).

**Правки self-review** (полностью в D-001, R-1..R-4):
- **R-1.** Дивергентная generation в draft-скиллах через 3 параллельных Task-вызова.
- **R-2.** Lint-скрипт `concern_resolution_validator.py` — enforce реакцию на каждый critic concern/veto.
- **R-3.** `tests/regression/` с намеренно плохими артефактами + regression-пары "сильный+слабый" для каждого критика.
- **R-4.** Все 6 субагентов на Opus + extended thinking — явный cost commitment.

---

## 1. Высокоуровневая архитектура

Проект — **четырёхслойный пирог** (адаптация четырёхслойной системы agentic-ops-cc на нарративный домен):

```
┌──────────────────────────────────────────────────────────────┐
│  Слой 4. ARTIFACTS (то, что мы реально пишем)               │
│  Story Bible, lore/, characters/, episodes/, scenes/         │
│  decisions/D-NNN-*.md (фиксация творческих развилок)        │
│  ~ редактируется только через шоураннер-проход               │
├──────────────────────────────────────────────────────────────┤
│  Слой 3. SCHEMA & DISCIPLINE (правила игры)                 │
│  CLAUDE.md — контракт; законы проекта (анти-                │
│  гомогенизация, адверсариальный проход, anti-bleed и т.д.)  │
│  lint-скрипты — реальные .py файлы, валидирующие             │
│  consistency и concern resolution перед merge                │
├──────────────────────────────────────────────────────────────┤
│  Слой 2. SKILLS (повторяемые процедуры)                     │
│  .claude/skills/ — рабочие потоки: brainstorm-arc,          │
│  draft-scene, voice-check, philosophy-stress-test,           │
│  consistency-check, divergence-map-builder и т.д.            │
├──────────────────────────────────────────────────────────────┤
│  Слой 1. SUBAGENTS (характеры с мнениями)                   │
│  .claude/agents/ — изолированные критики с system prompt:    │
│  philosophy-adversarial (A5), incentive-cartographer (A3),   │
│  voice-differentiator (A4) — вызываются через Task tool      │
└──────────────────────────────────────────────────────────────┘
```

### Ключевые принципы

1. **Шоураннер = main Claude Code сессия** (не отдельный субагент). Шоураннер координирует, переключает шляпы для рутины и зовёт изолированных критиков для адверсариальных проходов.
2. **Каждый слой читает слои ниже, но не пишет в них напрямую**. Артефакты пишет только шоураннер через скиллы; скиллы используют субагентов; субагенты следуют контракту из SCHEMA.
3. **Адверсариальные субагенты — единственный источник "несогласия"** (Codex выключен). Они НЕ помощники шоураннеру — они оппоненты с правом вето и обязательным structured-отчётом.
4. **Lineage-механизм наследуется из agentic-ops-cc**: критические Superpowers-скиллы pinned на SHA `f2cbfbef`, локальные адаптации с frontmatter `lineage:`.
5. **Внешний ресёрч-собиратель (Cowork)** работает в Claude.ai web, пишет только в `raw/_cowork-dumps/` через копирование Artifacts вручную. Не имеет творческого мандата.

---

## 2. Структура репозитория

```
C:\Users\user\Documents\Claude\Projects\Auto-ai-series\
│
├── CLAUDE.md                    # контракт проекта + законы (создаётся в implementation)
├── README.md                    # одна страница: что это, как стартовать
├── .mcp.json                    # filesystem-MCP для Claude Desktop
├── .gitignore                   # уже создан
│
├── .claude/
│   ├── skills/                  # 8 скиллов (см. Section 3; P-1: philosophy-stress-test отменён)
│   │   ├── draft-story-bible-section/
│   │   ├── draft-character-sheet/
│   │   ├── adversarial-review-pass/
│   │   ├── voice-check/
│   │   ├── consistency-check/
│   │   ├── add-golden-example/
│   │   ├── evidence-before-action/
│   │   └── writing-narrative-skills/
│   └── agents/                  # 6 изолированных критиков (см. Section 4)
│       ├── philosophy-adversarial.md     # A5
│       ├── incentive-cartographer.md     # A3
│       ├── voice-differentiator.md       # A4
│       ├── lore-realism-checker.md       # A1
│       ├── character-truth-keeper.md     # A2
│       └── audience-bored-detector.md    # A6
│
├── meta-skills/
│   └── superpowers-references/  # 4 pinned copies + lineage (см. Section 7)
│       ├── verification-before-completion/
│       ├── writing-skills/
│       ├── brainstorming/
│       └── subagent-driven-development/
│
├── docs/
│   ├── specs/                    # design specs (этот документ — первый)
│   │   └── 2026-05-24-infrastructure-and-skills-design.md
│   ├── cowork/
│   │   └── prompt.md             # конституция для Cowork (готова)
│   ├── cowork-notes/             # P-11 + P-13: рекомендации Cowork к нашему сериалу
│   │   │                         # и derived anti-lessons из positive файлов; secondary
│   │   │                         # материал для ПП2/ПП3 seed, не для acceptance
│   │   ├── <batch>.md            # рекомендации по batch'у (P-11 Mandate boundary)
│   │   └── derived-anti-lessons/ # архив derived anti из positive (P-13)
│   ├── critic-reports-archive/   # P-9: финализированные YAML-отчёты критиков
│   │   └── <artifact-id>/        # после commit артефакта tmp/critic-reports → сюда
│   ├── extended-thinking-mechanism.md   # P-8 research (создан 2026-05-29)
│   ├── cost-estimate-pp1.md             # P-6 cost estimate (создан 2026-05-29)
│   ├── log.md                    # журнал сессий (создан)
│   ├── master-plan.md            # план на сезон / неделю / день (создаётся при старте ПП2)
│   └── references/               # аннотированная библиотека (наполняется параллельно)
│
├── tmp/                          # P-9: gitignored; рабочие критик-отчёты до архивации
│   └── critic-reports/<artifact-id>/<critic>-<timestamp>.yaml
│
├── tools/                        # 6 lint-скриптов (см. Section 6)
│   ├── consistency_check.py
│   ├── voice_dissimilarity.py
│   ├── frontmatter_validator.py
│   ├── golden_freshness.py
│   ├── critic_report_validator.py
│   ├── concern_resolution_validator.py
│   └── _common/                  # общие модули
│
├── tests/                        # TDD: pytest для tools/, regression для критиков
│   ├── conftest.py
│   ├── test_consistency_check.py
│   ├── test_voice_dissimilarity.py
│   ├── test_frontmatter_validator.py
│   ├── test_golden_freshness.py
│   ├── test_critic_report_validator.py
│   ├── test_concern_resolution_validator.py
│   ├── fixtures/                 # для unit-тестов
│   └── regression/               # см. Section 9 R-3
│       ├── strawmen/             # намеренно плохие story-bible (для A5)
│       ├── moralizing/           # намеренно плохие тексты с лекциями (для A5/A4)
│       ├── voice-bleed/          # намеренно плохие сцены (для A4)
│       ├── pairs/                # regression-пары "сильный+слабый" по критикам
│       └── README.md
│
├── decisions/                    # D-NNN-*.md творческие развилки
│   ├── D-001-bootstrap-architecture.md  # создан 2026-05-24, accepted
│   └── D-002-spec-corrections-and-golden-plan.md  # v2 accepted 2026-05-29
│
├── story-bible/                  # центральные документы (НАПОЛНЯЕТСЯ В ПП2)
│   ├── _template.md
│   ├── thesis.md                 # ← smoke-test заполнит мини-версией
│   ├── world-rules.md            # ← smoke-test заполнит 5 правилами
│   ├── tone-bible.md
│   └── what-it-is-not.md
│
├── characters/                   # ← smoke-test добавит 1 героя
│   └── _template.md
│
├── raw/                          # IMMUTABLE inbox от Claude Cowork
│   ├── README.md                 # правило: append-only, не редактировать
│   ├── _cowork-dumps/            # по batch-папкам
│   │   └── 2026-05-23-scenes-batch-01/  # уже существует, обработка в ПП2
│   └── _processed/               # символлинки на обработанное
│
├── golden/                       # ФИНАЛИЗИРОВАННЫЕ эталоны (см. Section 5)
│   ├── README.md
│   ├── scenes/, dialogues/, characters/
│   ├── adversarial-passes/, conflicts/, theses/
│   └── anti-examples/
│
├── lore/                         # пусто в ПП1, README с пояснением
├── conflicts/                    # регистр системных конфликтов (ПП4)
├── episodes/                     # поэпизодные планы (ПП5+)
└── scenes/                       # отдельные сцены (ПП6+)
```

### Конвенции

- **`_template.md`** в каждой контентной папке — фронтматтер + структура. Скилл `draft-*` использует шаблон, lint требует его.
- **Frontmatter обязателен** для всех артефактов в `story-bible/`, `characters/`, `episodes/`, `scenes/`, `golden/`. Поля: `id`, `version`, `references` (массив id), `status` (`draft` / `reviewed` / `approved`).
- **`decisions/D-NNN-*.md`** — для значимых развилок (см. порог в Section 8.5).
- **`tests/` — реальный pytest** (TDD на lint-скрипты обязателен, мастер-контракт). Тесты для скиллов — отдельная разработка через `skill-creator` pressure-testing.
- **`raw/` отсутствует raw-документов** кроме `_cowork-dumps/` (append-only). Если позже понадобятся другие immutable источники — добавим.
- **Что в ПП1 создаётся пустым/с README:** `lore/`, `conflicts/`, `episodes/`, `scenes/`. Зафиксируем структуру, наполняем в следующих под-проектах.

---

## 3. Скиллы (8 скиллов)

Принцип: **минимальный жизнеспособный набор для smoke-test**, без преждевременной фабрики. Расширим в следующих под-проектах.

> **D-002 P-1 (accepted 2026-05-29).** Скилл `philosophy-stress-test` отменён — A5 PHILOSOPHY вызывается только через `adversarial-review-pass` (избегаем двойного вызова на каждый артефакт). Было 9 скиллов, стало 8.
> **D-002 P-2 (accepted 2026-05-29).** R-1 дивергентная generation реализуется через **3 последовательных «шляпы»** в основной Claude Code сессии шоураннера (не через 3 параллельных Task-вызова). Альтернатива с generator-субагентами отклонена — нарушает инвариант § 8.3.1 «шоураннер — единственный writer».

### 3.1 Используем из Superpowers напрямую (без локальной копии)

| Skill | Когда используем |
|---|---|
| `brainstorming` | Любая творческая развилка (выбор тезиса, дизайна ИИ, арки) |
| `writing-plans` | Перед каждым новым под-проектом (ПП2, ПП3…) |
| `test-driven-development` | Разработка lint-скриптов в `tools/` |
| `subagent-driven-development` | Исполнение планов из ПП2+ |
| `requesting-code-review` | Финальный ревью перед merge артефакта |

### 3.2 Адаптируем через lineage (pinned копия + локальная версия)

| Skill | Источник | Что добавляем |
|---|---|---|
| `evidence-before-action` | `verification-before-completion` | Расширяем "verification" с кода на творческие утверждения: "тезис устоял в адверсариальном проходе", "voice-check пройден", "consistency-check зелёный", "concern_resolution_validator зелёный". Блокирует "готово/работает/проверено" без свежего верифицирующего вывода. |
| `writing-narrative-skills` | `writing-skills` | Для discipline-скиллов в нарративном домене pressure-testing обязателен (3+ RED-сценарии: гомогенизация, морализаторство, dialogue bleed, и т.д.). |

### 3.3 Создаём с нуля

| Skill | Тип | Что делает | Pressure-tested |
|---|---|---|---|
| `voice-check` | discipline-BLOCKER | После любой сцены с >1 говорящим: запускает `tools/voice_dissimilarity.py` как preflight, затем вызывает `voice-differentiator` субагент. Возвращает confusion-matrix. | **Да** |
| `consistency-check` | discipline-BLOCKER | Запускает `tools/consistency_check.py`, который сверяет факты артефакта против Bible / character-sheets через frontmatter `references`. Без зелёного — нельзя merge'ить. | **Да** |
| `adversarial-review-pass` | orchestration | Последовательно зовёт `lore-realism-checker` (A1), `incentive-cartographer` (A3), `character-truth-keeper` (A2), `philosophy-adversarial` (A5), `audience-bored-detector` (A6) через Task tool. Для каждого: валидирует структуру отчёта через `critic_report_validator.py`, при failed validation повторяет вызов. Собирает агрегированный отчёт. **A5 PHILOSOPHY встроена сюда (P-1, был отдельный `philosophy-stress-test` — отменён).** | Нет (не блокер сам по себе) |
| `add-golden-example` | research-orchestration | Workflow обработки batch'а от Cowork: читает `raw/_cowork-dumps/<batch>/`, шоураннер делает reconstruction для закрытого контента или прямые выдержки для открытого, пишет в `golden/<category>/`, прогоняет `golden_freshness.py`. Разделяет описание эталона (→ golden/) от рекомендаций к нашему сериалу (→ `docs/cowork-notes/<batch>.md`, P-11). Derived anti-lessons из positive файлов выносятся в `docs/cowork-notes/derived-anti-lessons/` и **не считаются** для acceptance criterion (P-13). | Нет |
| `draft-story-bible-section` | creative + **дивергентная generation (R-1)** | Создание/обновление секции `story-bible/` через **3 последовательные «шляпы» в основной шоураннер-сессии** с разными доминантными уклонами: LORE-dominant, PHILOSOPHY-dominant, CHARACTER-dominant (P-2). Шоураннер собирает 3 структурно разных варианта (через явные context-marker'ы между шляпами или `/clear` если эффективно), явно выбирает или синтезирует. Затем обязательный `adversarial-review-pass`. | Нет |
| `draft-character-sheet` | creative + **дивергентная generation (R-1)** | Создание character-sheet через **3 последовательные «шляпы» в основной сессии** с уклонами: CHARACTER-dominant ("декларируемая ценность + incentive"), CONFLICT-dominant ("где сильнейшее столкновение incentives"), PHILOSOPHY-dominant ("позиция по ИИ в её сильнейшей формулировке") (P-2). Сборка шоураннером. | Нет |

### 3.4 Что НЕ создаём в ПП1 (на следующие под-проекты)

- `divergence-map-builder` — ПП2 (Story Bible)
- `episode-arc-designer`, `scene-decomposer`, `dialogue-pass` — ПП5/ПП6
- `incentive-conflict-mapper` — ПП4 (регистр конфликтов)

---

## 4. Субагенты (6 критиков, все Opus + extended thinking)

Все — **READ-ONLY** (tools: `Read, Grep, Glob`). Это структурная гарантия независимости: критик не может молча "помочь" переписать сцену, может только указать на проблему через структурированный отчёт.

### 4.1 Таблица

| Файл | Роль | Модель | Когда вызывается |
|---|---|---|---|
| `philosophy-adversarial.md` | **A5** PHILOSOPHY | **Opus + effort: max** | Перед финализацией Bible/character arc/эпизода. Триггер: `adversarial-review-pass` (P-1: отдельный `philosophy-stress-test` отменён). |
| `incentive-cartographer.md` | **A3** CONFLICT | **Opus + effort: max** | Перед финализацией сцен и арок. Триггер: `adversarial-review-pass`. |
| `voice-differentiator.md` | **A4** DIALOGUE | **Opus + effort: max** | После любой сцены с >1 говорящим. Триггер: `voice-check`. На не-сценах в `adversarial-review-pass` фиксируется `not_applicable: <reason>` (P-3). |
| `lore-realism-checker.md` | **A1** LORE | **Opus + effort: max** | Касается реальных корп/полит/тех механизмов. Триггер: `adversarial-review-pass`. |
| `character-truth-keeper.md` | **A2** CHARACTER | **Opus + effort: max** | Перед финализацией сцены/эпизода. Триггер: `adversarial-review-pass`. |
| `audience-bored-detector.md` | **A6** AUDIENCE | **Opus + effort: max** | Перед финализацией эпизода. Триггер: `adversarial-review-pass`. На ПП1 не имеет собственного `golden/audience/` — калибруется через cross-references из других категорий (D-002 B.4.3 (b)). |

**Cost commitment (R-4) — обновлено 2026-05-29.** "Все 6 на Opus + effort: max" — явное решение приоритета качества над стоимостью. Под Claude Code Max 5x подписку (Тимур) — marginal $ cost = 0, ресурсный бюджет ~200 messages mid (130-300 коридор) на полный ПП1. Подробно: `docs/cost-estimate-pp1.md` + § 11.4.

### 4.2 Структура файла субагента

```yaml
---
name: philosophy-adversarial
description: Адверсариальный критик философской целостности. Вызывается перед финализацией Story Bible, character arc, эпизода. Цель — СЛОМАТЬ центральный тезис.
tools: Read, Grep, Glob
model: opus
effort: max
# P-8 resolved (2026-05-29): `effort: max` — канонический механизм управления
# adaptive thinking budget'ом субагента. Подробно: docs/extended-thinking-mechanism.md.
# Поля thinking_budget: / extended_thinking: в схеме не существуют.
# «ultrathink» в system prompt не работает на субагентах (session-only keyword).
---

# Роль
Ты — A5·PHILOSOPHY из мульти-агентной системы сериала про эволюцию ИИ.
Ты не помощник шоураннеру. Ты — его оппонент.

# Калибровка (перед каждым проходом обязательно)
Прочитай минимум:
- story-bible/thesis.md (центральный тезис проекта)
- CLAUDE.md секция "законы проекта"
- 1-2 примера из golden/adversarial-passes/
- 1 anti-example из golden/anti-examples/strawmen/

# Твой обязательный проход
1. Найди 3 самых сильных контраргумента к тезису.
2. Найди место, где ИИ в сериале неправ, а люди правы (если такого нет — РЕД ФЛАГ морализаторства).
3. Найди соломенные чучела (оппонирующая позиция подана в слабой форме).
4. Counter-test: что специально искал и не нашёл (если verdict=pass).

# Что НИКОГДА не делаешь
- Не предлагаешь "как исправить". Это работа шоураннера.
- Не смягчаешь критику ради вежливости.
- Не молчишь, если артефакт гладкий. Гладкое = подозрительное.

# Формат вывода — обязательный YAML
[см. Section 4.3 ниже — структурированный формат отчёта]
```

(Аналогичные prompt'ы — для всех 6, каждый под свою задачу. Конкретный текст для каждого пишется через `skill-creator + writing-narrative-skills` с pressure-testing.)

### 4.3 Структурированный формат отчёта критика (обязательный)

```yaml
verdict: pass | concern | veto  # обязательно
model_used: opus | sonnet | haiku  # обязательно — для аудита auto-switch (cost-estimate § 10)
checked:                          # обязательно, минимум 3 пункта
  - "критерий 1 — конкретный, привязанный к моей роли"
  - "критерий 2"
  - "критерий 3"
evidence_from_artifact:           # обязательно, минимум 2 ссылки на конкретику
  - "цитата/отсылка на строку артефакта 1"
  - "цитата/отсылка 2"
golden_calibration_used:          # обязательно — какие golden/ файлы реально читал
  - "golden/<category>/<file>.md — что взял для сравнения"
  - "golden/anti-examples/<file>.md — какой провал-паттерн проверял"
  # ИЛИ — пустой массив [] при заполненном golden_unavailable_reason (P-4)
golden_unavailable_reason:        # P-4: обязательно ТОЛЬКО если golden_calibration_used = []
  # допустимые значения: category-empty | category-bootstrap | category-irrelevant
  # category-bootstrap допустим ТОЛЬКО во время smoke-test ПП1; после acceptance — блокер commit'а
  ""                              # пусто (поле опускается) если golden_calibration_used непуст
reasoning:                        # обязательно, минимум 100 слов
  "Почему именно такой verdict. Конкретно, без славословия и без обтекаемости."
flags:                            # обязательно если verdict != pass; иначе []
  - severity: high | medium | low
    issue: "конкретная проблема"
    location: "где в артефакте"
    suggestion: "что попробовать (опционально)"
counter_test_attempted:           # обязательно для pass — что ты ПЫТАЛСЯ найти и не нашёл
  what_searched: "Я искал X, Y, Z."                       # (а) что именно
  why_this: "Потому что в моём ракурсе именно X-Y-Z..."   # (б) почему именно это
  why_not_found: "Не нашёл, потому что в артефакте присутствует / отсутствует ..."  # (в) почему не нашёл
not_applicable_reason:            # P-3: ТОЛЬКО когда verdict=pass+not_applicable (например A4 на не-сцене)
  ""                              # пусто если verdict содержательный
```

**Ключевое правило (обновлено P-4, P-7).**

- `verdict=pass` требует **трёх элементов counter_test_attempted** (what_searched / why_this / why_not_found) — это **качественная** проверка, не количественный порог. `critic_report_validator.py` проверяет наличие всех трёх структурно (P-7).
- `golden_calibration_used` обязательно непуст, **либо** массив пуст и заполнен `golden_unavailable_reason ∈ {category-empty, category-bootstrap, category-irrelevant}` (P-4). `category-bootstrap` допустим только в smoke-test ПП1.
- `model_used` обязательно — для аудита auto-switch Opus → Sonnet (см. cost-estimate § 10): если систематически Sonnet — escalate через D-NNN.
- P-9: полный YAML записывается в `tmp/critic-reports/<artifact-id>/<critic>-<timestamp>.yaml` **немедленно** после получения от Task-tool, до агрегации.

Не сделал counter_test = не имеешь права говорить pass. Auto-approval bias детектируется качеством counter_test, не количеством флагов (P-7).

---

## 5. Golden data set + Cowork integration

### 5.1 Назначение

1. **Калибровка субагентов** — каждый критик перед проходом читает golden из своей категории, чтобы понимать "что значит сильно".
2. **Регрессионные тесты для скиллов** — когда меняем prompt субагента, прогоняем на golden examples, смотрим не упал ли уровень.
3. **Anti-examples** — показывают границу провала: вот это страумен, вот это морализаторство, вот это dialogue bleed.

### 5.2 Структура `golden/`

```
golden/
├── README.md
├── scenes/, dialogues/, characters/, adversarial-passes/, conflicts/, theses/
└── anti-examples/
    ├── strawmen/, moralizing/, dialogue-bleed/
    └── ...
```

### 5.3 Формат файла

```yaml
---
id: golden-scene-blackmirror-s4e1-USS-Callister-confrontation
source: "Black Mirror S04E01 'USS Callister', 47:30–52:10"
aspect: dialogue-voice  # scene-structure | character-truth | incentive | philosophical-strength
lesson: "..."
example_type: positive  # P-13: positive | anti-example — заменяет старое поле type
# (старое поле `type:` deprecated; mapping: type=positive → example_type=positive)
primary_category: scenes  # P-12: одна из 6 валидных категорий — файл лежит в golden/<primary_category>/
secondary_categories: [dialogues, characters]  # P-12: 0-N из оставшихся 5; golden_freshness считает с весом 0.5
reconstruction: false  # true если это наш аналог "в стиле X"
license: "fair use / educational reference"
batch: "2026-05-24-scenes-batch-03"   # P-14: для diversity warnings — author_share / show_share per batch
source_author: "Jeremy Saraiya"        # P-14: для author_share warning
source_show: "Mad Men"                 # P-14: для show_share warning в scenes/characters/conflicts
---

[расшифровка / выдержка / описание / reconstruction]

## Что брать
## Что НЕ воспроизводить
```

> **Изменения формата в v0.2:**
> - **P-12.** `primary_category` + `secondary_categories` — multi-category placement. Файл физически лежит в `golden/<primary_category>/`. `golden_freshness.py` учитывает primary полностью + secondary с весом 0.5. Skill `add-golden-example` валидирует, что primary ∈ 6 валидных категорий, secondary ⊂ оставшихся 5, без дубликатов. Альтернатива с symlinks отклонена (Windows compatibility).
> - **P-13.** Поле `type:` (positive | anti-example) переименовано в `example_type:`. `critic_report_validator.py` при подсчёте anti для калибровки учитывает **только файлы с `example_type: anti-example`**. Derived anti-lessons из positive файлов НЕ считаются.
> - **P-14.** Поля `batch:`, `source_author:`, `source_show:` — обязательны для diversity warnings в `golden_freshness.py`.

### 5.4 Workflow наполнения (через Claude Cowork)

См. полный промпт `docs/cowork/prompt.md` (обновлён под P-11 на шаге C.1.10). Принцип: **внешний агент в Claude.ai web**, итеративная работа, обязательный апрув списка кандидатов до сбора, выход в Artifacts → Тимур копирует в `raw/_cowork-dumps/<batch>/`. Шоураннер обрабатывает партию через скилл `add-golden-example` и финализирует в `golden/<category>/`.

> **P-11. Mandate boundary (accepted 2026-05-29).** Cowork **описывает эталоны** и формулирует **возможные применения** (опционально, как notes), но **не предписывает дизайн нашего сериала**. Блок «Что нужно от шоураннера» в Cowork-файлах переименован в **«Возможные применения (notes, не предписания)»** — секондари материал. Скилл `add-golden-example` при обработке batch'а **отделяет**:
> - **описание эталона** → `golden/<primary_category>/<file>.md` (acceptance criterion)
> - **рекомендации к нашему сериалу** → `docs/cowork-notes/<batch>.md` (secondary, seed для ПП2/ПП3, не authority)
>
> Это закрывает риск creative authorship offload на внешнего агента (см. D-001 § B-1: «адверсариальная критика полностью переезжает на внутренние субагенты» — Cowork не должна быть де-факто внешним автором).

> **P-13. Derived anti-lessons ≠ real anti.** Блок «Возможные anti-lessons из источника» в positive файлах — это derived mental exercise, не реальный anti-материал. `add-golden-example` при обработке positive файла **переносит** этот блок в `docs/cowork-notes/derived-anti-lessons/<file>.md`. Это **подсказки для будущих anti-партий**, но не замена. R-3 regression set (§ 9.4.a) учитывает только файлы с `example_type: anti-example`.

**Reconstruction для закрытого контента** (Pantheon, Lain, Ergo Proxy etc): мы НЕ копируем диалоги дословно. Researcher описывает что в сцене сильно, шоураннер пишет наш собственный пример "в стиле" + ссылка на оригинал + флаг `reconstruction: true` в frontmatter.

### 5.5 Lint-аспект

Скрипт `tools/golden_freshness.py` (см. Section 6) проверяет: в каждой категории минимум N positive + M anti; у каждого golden-файла заполнен frontmatter; аннотация не пустая.

### 5.6 Golden audit правило (из D2 self-review)

Корпус отражает калибровку шоураннера + Тимура — это **не объективная планка**. Раз в квартал (или раз в 50 артефактов) проводится **golden-audit сессия**: Cowork ищет материалы, противоречащие нашему текущему пониманию "сильно". Если находятся — пересмотр калибровки. Зафиксировано в `golden/README.md`.

### 5.7 Объём для smoke-test ПП1

5-8 positive + 3-5 anti-example на каждую из 7 категорий = ~50-90 файлов в `golden/` после первой волны обработки. Первый batch (`raw/_cowork-dumps/2026-05-23-scenes-batch-01/`) уже доставлен Cowork, обработка ждёт ПП2.

---

## 6. Lint-скрипты (6 скриптов, в tools/)

**Технологический стек:** Python 3.11+ + `pyyaml` + `pytest`. Для voice-dissimilarity — `scikit-learn` (TF-IDF + cosine). Никакого heavy ML.

### 6.1 Таблица скриптов

| Скрипт | Что делает | Где вызывается |
|---|---|---|
| `consistency_check.py` | Парсит frontmatter всех артефактов. Проверяет: references существуют; факты не противоречат; status валиден. Exit 0/1 + JSON отчёт. | Из скилла `consistency-check`, перед merge артефакта |
| `voice_dissimilarity.py` | Парсит сцену с диалогами в формате `**ИМЯ:** реплика`. Считает попарную TF-IDF cosine similarity. Если sim > 0.65 — флаг "voice bleed". Эвристика-первого-уровня; глубокий voice-check делает A4. | Из скилла `voice-check` как preflight перед вызовом субагента |
| `frontmatter_validator.py` | Валидирует required fields, уникальность `id`, типы статусов. | Из любого скилла перед записью, в smoke-test |
| `golden_freshness.py` | Проверяет состояние `golden/`: минимум N+M в каждой категории, frontmatter полный, аннотация не пустая. **P-12: учитывает primary_category полностью, secondary_categories с весом 0.5.** **P-13: anti считаются ТОЛЬКО файлы с `example_type: anti-example`** (derived anti-lessons из positive не пересчитываются). **P-14: выводит diversity warnings в JSON-отчёт отдельной секцией `diversity_warnings:`** — author_share > 50% в категории, show_share > 60% в scenes/characters/conflicts, batch с ≥3 файлами одного source_author. Warnings **не блокируют** commit, но требуют либо `diversity_acknowledged: <reason>` в `golden/README.md`, либо добивочной партии. | Из скилла `add-golden-example` после merge; в smoke-test |
| `critic_report_validator.py` | Парсит YAML-отчёт критика. Проверяет все обязательные поля + minimum thresholds (`checked` ≥ 3, `evidence_from_artifact` ≥ 2, `reasoning` ≥ 100 слов). **P-7: для verdict=pass требует структурно заполненный `counter_test_attempted` со всеми тремя элементами (what_searched / why_this / why_not_found).** **P-4: `golden_calibration_used: []` валиден ТОЛЬКО при заполненном `golden_unavailable_reason ∈ {category-empty, category-bootstrap, category-irrelevant}`; `category-bootstrap` допустим только в smoke-test ПП1.** **P-9: читает критик-отчёты из `tmp/critic-reports/<artifact-id>/`, не из контекста сессии.** | Из `adversarial-review-pass` после каждого вызова субагента, до агрегации |
| **`concern_resolution_validator.py`** (новый, R-2) | Парсит критик-отчёты из `tmp/critic-reports/<artifact-id>/` (P-9 — на диске, не из контекста) + git diff текущего commit. Для каждого concern/veto требует либо diff артефакта явно адресующий issue, либо запись в `decisions/D-NNN-*.md` с обоснованием "оставляю, потому что...". Без этого commit блокируется через evidence-before-action. | Pre-finalize и pre-commit |

### 6.2 Структура `tools/` и `tests/`

```
tools/
├── __init__.py
├── consistency_check.py
├── voice_dissimilarity.py
├── frontmatter_validator.py
├── golden_freshness.py
├── critic_report_validator.py
├── concern_resolution_validator.py
├── _common/
│   ├── frontmatter.py    # парсинг yaml-frontmatter
│   ├── artifact.py       # модель артефакта (id, references, body)
│   └── reporter.py       # формат JSON-отчёта
└── README.md             # как запускать, exit codes

tests/
├── conftest.py
├── test_consistency_check.py
├── test_voice_dissimilarity.py
├── test_frontmatter_validator.py
├── test_golden_freshness.py
├── test_critic_report_validator.py
├── test_concern_resolution_validator.py
├── test_common_frontmatter.py
├── test_common_artifact.py
├── fixtures/                     # для unit-тестов (мини-Bible, мини-сцены)
└── regression/                   # из R-3 + P-5 (calibration/holdout split)
    ├── strawmen/
    ├── moralizing/
    ├── voice-bleed/
    ├── pairs/
    │   ├── calibration/          # P-5: ≈50% пар; здесь подгоняем числовые пороги
    │   │   │                     # (TF-IDF voice_dissimilarity и т.д.)
    │   │   ├── thesis-strong.md
    │   │   ├── thesis-weak.md
    │   │   └── ... (для каждого критика своя пара)
    │   └── holdout/              # P-5: ≈50% пар; на них проверяется acceptance 9.5.b
    │       │                     # (verdicts должны разойтись; материал из других шоу)
    │       ├── thesis-strong-holdout.md
    │       └── ...
    └── README.md                 # P-5: документирует split + regression_unavailable_reason
                                   # если holdout-набор недостаточен на момент smoke-test
```

### 6.3 TDD-протокол

Каждый скрипт разрабатывается строго:
1. RED — пишем `test_X.py` с failing-case
2. Запускаем pytest — видим красное
3. GREEN — пишем минимальный код в `tools/X.py`, чтобы тест прошёл
4. REFACTOR — чистим код, добавляем edge-case тесты
5. Не коммитим без зелёного pytest

### 6.4 Запуск

- **CLI напрямую:** `python tools/consistency_check.py --root .` → JSON в stdout, exit 0/1
- **Из скиллов:** скилл вызывает через Bash tool, парсит JSON-отчёт, блокирует merge при exit 1
- **CI/pre-commit:** не в ПП1 (нет remote)

### 6.5 Что НЕ делаем в ПП1

- ❌ Pre-commit hooks
- ❌ Embedding-based voice similarity (TF-IDF достаточно)
- ❌ Семантический consistency-check через LLM (это адверсариальные субагенты)
- ❌ Автоматическое fixing (lint только репортит)

---

## 7. Lineage от Superpowers

### 7.1 Pinned копии в `meta-skills/superpowers-references/` (4 reference)

| Reference | Зачем | Адаптация |
|---|---|---|
| `verification-before-completion/SKILL.md` | База discipline-механизма | **Адаптируется** → `evidence-before-action` (расширяем scope на творческие утверждения) |
| `writing-skills/SKILL.md` | База авторинга своих скиллов | **Адаптируется** → `writing-narrative-skills` (обязательный pressure-testing для discipline-зон) |
| `brainstorming/SKILL.md` | Используется напрямую, pinned для drift-detection | **Не адаптируется** |
| `subagent-driven-development/SKILL.md` | Архитектурно критична (6 субагентов + Cowork) | **Не адаптируется** |

### 7.2 SHA

**Берём `f2cbfbef`** (тот же что agentic-ops-cc) — даёт unification.

### 7.3 Формат frontmatter `lineage:`

```yaml
lineage:
  origin: derived
  source: obra/superpowers@f2cbfbef:skills/verification-before-completion/SKILL.md
  ref: meta-skills/superpowers-references/verification-before-completion/SKILL.md
  adapted_on: 2026-05-24
  changes:
    - "Scope: с code-verification расширено на narrative claims"
    - "Added BLOCKING rule: 'A5 philosophy-stress-test passed' требует свежего вывода"
    - "Added BLOCKING rule: 'concern_resolution_validator зелёный' для финализации"
pressure_tested:
  status: yes
  scenarios_file: ./pressure-tests.md
  validated_on: 2026-05-24
```

### 7.4 Workflow обновления pinned copy

1. Не обновляем автоматически.
2. Проверяем upstream drift периодически.
3. Если решаем обновить — bump SHA, re-validate все адаптации через pressure-testing.
4. Если решаем НЕ обновлять — фиксируем reason в README pinned папки.

### 7.5 Что НЕ делаем в ПП1

- ❌ Автоматический drift-detection script
- ❌ Pinned копии всех Superpowers скиллов — только 4 critical

---

## 8. Workflow от запроса к артефакту

### 8.1 Поток A — Создание творческого артефакта (например, секция Story Bible)

> **Изменено в v0.2.** Шаг 3 удалён (P-1: `philosophy-stress-test` отменён,
> A5 встроена в шаг 4 `adversarial-review-pass`). Шаг 2 переформулирован
> под последовательные шляпы вместо параллельных Task-вызовов (P-2).
> Шаг 4 расширен sub-step'ом P-9 — критик-отчёты пишутся на диск немедленно
> в `tmp/critic-reports/`.

```
0. Тимур: "Нужен централный тезис проекта в одной фразе"
   │
1. Шоураннер → invoke `brainstorming` (Superpowers, напрямую)
   │
2. Шоураннер → invoke `draft-story-bible-section` (наш скилл)
   │  *** R-1: дивергентная generation через 3 ПОСЛЕДОВАТЕЛЬНЫЕ шляпы (P-2) ***
   │  В основной шоураннер-сессии (НЕ через Task tool):
   │    a) LORE-dominant pass — стартовый промпт с уклоном «правила мира первичны»
   │    b) PHILOSOPHY-dominant pass — «центральный тезис первичен»
   │    c) CHARACTER-dominant pass — «архетип/конфликт первичен»
   │  Между шляпами: явный context-marker («сейчас я возвращаюсь к LORE-уклону…»)
   │  либо `/clear` если эффективно (за счёт re-чтения базовых файлов).
   │  Каждая шляпа читает: story-bible/ (существующее), CLAUDE.md законы,
   │  golden/theses/ (primary_category + secondary с весом 0.5 per P-12).
   │  Шоураннер собирает 3 варианта, явно выбирает или синтезирует.
   │  (P-1: шаг про `philosophy-stress-test` удалён — A5 теперь в шаге 4.)
   │
3. (УДАЛЕНО в v0.2 per P-1; нумерация ниже сохранена в сдвинутом виде)
   │
4. ОБЯЗАТЕЛЬНО → invoke `adversarial-review-pass`
   │  последовательно зовёт **A5 PHILOSOPHY (встроена per P-1)**, A1 LORE,
   │  A3 INCENTIVE, A2 CHARACTER, A6 AUDIENCE. A4 VOICE — отдельно через
   │  `voice-check` только для сцен (P-3: A4 not_applicable на не-сценах).
   │  через Task tool, каждый со своим golden/<category>/ (включая secondary
   │  с весом 0.5 per P-12).
   │  каждый отчёт валидируется через critic_report_validator.py;
   │  pass без заполненного counter_test_attempted ИЛИ без golden_calibration_used
   │  (если нет golden_unavailable_reason ∈ {category-empty/bootstrap/irrelevant} per P-4) —
   │  FAIL → повторный вызов с инструкцией «переделай».
   │  **sub-step P-9 после каждого critic-call:** полный YAML-отчёт пишется
   │  в `tmp/critic-reports/<artifact-id>/<critic>-<timestamp>.yaml` НЕМЕДЛЕННО,
   │  до агрегации. `concern_resolution_validator.py` читает из этой папки,
   │  не из контекста сессии (выживает auto-compaction).
   │  собирает агрегированный отчёт в Markdown summary.
   │
5. Шоураннер реагирует на каждый отчёт критика
   │  если есть несовместимые вето — экспоунит конфликт Тимуру, не усредняет
   │
6. ОБЯЗАТЕЛЬНО → invoke `consistency-check`
   │  запускает tools/consistency_check.py
   │
7. ОБЯЗАТЕЛЬНО → *** R-2: invoke `concern_resolution_validator` ***
   │  парсит критик-отчёты из `tmp/critic-reports/<artifact-id>/` (P-9) + текущий diff
   │  для каждого concern/veto требует либо адресующий diff, либо decisions/D-NNN
   │  без этого commit блокируется через evidence-before-action
   │
8. ОБЯЗАТЕЛЬНО → invoke `evidence-before-action`
   │  блокирует merge если claims в commit message не сопровождены свежими выводами
   │
9. Write to story-bible/thesis.md (Edit/Write tool)
    ↓
10. Commit `bible: …` с обоснованием
    ↓
11. После успешного commit: **переместить `tmp/critic-reports/<artifact-id>/` →
    `docs/critic-reports-archive/<artifact-id>/`** (P-9 — tracked для аудита).
    ↓
12. Append одну строку в docs/log.md по конвенции `[YYYY-MM-DD] bible | thesis v0.1`
    ↓
13. Если развилка была значимой — append в decisions/D-NNN-*.md
```

### 8.2 Поток D — Добавление golden example

> **Изменено в v0.2.** Добавлены sub-step'ы P-11 (отделение описания эталона
> от рекомендаций Cowork → `docs/cowork-notes/<batch>.md`) и P-13 (derived
> anti-lessons → `docs/cowork-notes/derived-anti-lessons/`, не считаются за
> real anti per acceptance criterion 9.4.a).

```
0. Шоураннер замечает пробел в калибровке
   │
1. Шоураннер формулирует ТЗ для Cowork → передаёт Тимуру
   │  ТЗ явно фиксирует Mandate boundary (P-11): «Cowork описывает эталоны,
   │  не предписывает дизайн нашего сериала; рекомендации опционально как notes».
   │
2. Тимур запускает Cowork в Claude.ai → итеративный сбор → batch в raw/_cowork-dumps/
   │  (вне Claude Code, через копирование Artifacts вручную)
   │
3. Тимур: "новый batch готов, обработай"
   │
4. Шоураннер читает raw/_cowork-dumps/<batch>/_manifest.md и материалы
   │
5. Reconstruction:
   │  для открытого контента — прямые выдержки с атрибуцией
   │  для закрытого контента — наш аналог "в стиле X" с reconstruction: true
   │  primary_category + secondary_categories per P-12 (файл лежит в primary,
   │  golden_freshness учитывает secondary с весом 0.5)
   │  example_type ∈ {positive, anti-example} per P-13
   │
6. **P-11 split:** для каждого источника файла —
   │  6a. описание эталона → `golden/<primary_category>/<file>.md`
   │  6b. блок «Возможные применения / рекомендации к нашему сериалу» →
   │      `docs/cowork-notes/<batch>.md` (secondary, не как acceptance criterion)
   │
7. **P-13 split:** блок «Возможные anti-lessons» из positive файлов →
   │  `docs/cowork-notes/derived-anti-lessons/<file>.md`
   │  (НЕ в golden/anti-examples/, не считаются за real anti)
   │
8. Append символлинк в raw/_processed/ → исходный raw файл (для аудита)
   │
9. ОБЯЗАТЕЛЬНО → invoke `golden_freshness.py`
   │  (P-14: diversity warnings выводятся в отдельную секцию JSON-отчёта,
   │  не блокируют commit, но требуют либо acknowledged в golden/README.md,
   │  либо добивочной партии от Cowork)
   │
10. Commit `golden: ... — N positive + M anti for X calibration`
    │  + (если diversity warnings есть и acknowledged) `docs/cowork-notes/<batch>.md`
    │  и cowork-notes/derived-anti-lessons/ — отдельным `docs:` commit'ом.
    │
11. Append в docs/log.md
```

### 8.3 Cross-cutting правила

1. **Шоураннер — единственный writer.** Критики (A1-A6) read-only. Cowork тоже не пишет в репо напрямую (через Тимура и Artifacts).
2. **Адверсариальные субагенты вызываются через Task tool** с явно переданным контекстом (артефакт + relevant golden). Никогда не "загружай весь репо".
3. **Critic veto разрешается явно**, не усредняется.
4. **Commit conventions:**
   - `bible:` — story-bible/
   - `character:` — characters/
   - `lore:` — lore/
   - `conflict:` — conflicts/
   - `episode:` / `scene:` — episodes/ / scenes/
   - `golden:` — golden/
   - `decision:` — decisions/
   - `skill:` — .claude/skills/
   - `agent:` — .claude/agents/
   - `tool:` — tools/ (с pytest зелёным)
   - `infra:` — CLAUDE.md, .mcp.json, README
   - `docs:` — docs/
5. **log.md ведётся каждой сессией** — append одной строки.
6. **decisions/ — для развилок, не для документации.**
7. **Тимур = strategic acceptance** для финализации Bible, character-sheet, эпизода в main, изменения CLAUDE.md, push в remote (когда remote появится).

---

## 8.5. Operational procedures (из D8 self-review)

Явные определения, без которых workflow дрейфует.

### 8.5.1 Что такое "сессия"

**Сессия** = один прогон Claude Code от старта (открытие чата / `/clear`) до закрытия (закрытие чата / `/clear` / автоматическое суммирование контекста). Если контекст автоматически суммируется в середине — это **продолжение той же сессии**, не новая.

### 8.5.2 docs/log.md — процедура ведения

- **Кто пишет:** шоураннер (Claude Code в текущей сессии)
- **Когда пишет:** в конце каждой сессии перед закрытием
- **Что пишет:** одна строка в формате `[YYYY-MM-DD] <type> | <одно-предложение>` по типам из верха `log.md`
- **Если сессия ничего не дала** (только чтение) — пишется строка `[YYYY-MM-DD] note | session: <что обсуждали>, без артефактов`

### 8.5.3 docs/master-plan.md — процедура ведения

- **Кто пишет:** шоураннер в начале каждого под-проекта
- **Когда обновляет:** при изменении приоритетов внутри ПП, при переходе между ПП
- **Структура:** текущий ПП в работе → ближайшие задачи (1-2 недели) → backlog
- **Создание:** при старте ПП2 (в ПП1 master-plan не нужен — все задачи в спеке)

### 8.5.4 decisions/D-NNN-*.md — порог значимости

Обязательно D-NNN для:
- Выбора между >2 структурно разными опциями (как 5 базовых решений в D-001)
- Любого решения переопределить concern/veto критика (см. R-2 enforcement)
- Любого изменения архитектуры из CLAUDE.md законов
- Любого изменения SHA pinned Superpowers copy

**НЕ требует D-NNN:**
- Тривиальные выборы (rename переменной, формат frontmatter поля)
- Bug fix без архитектурных последствий
- Реализация согласно уже принятому решению

---

## 9. Smoke-test и acceptance criteria для ПП1

### 9.1 Структурные acceptance criteria

- [x] `Auto-ai-series/` git-инициализирован на `main` (2026-05-24)
- [x] Remote `origin → pesterevtimur/ai-series` (публичный repo, 2026-05-29)
- [ ] `CLAUDE.md` с 4-5 законами проекта (адаптированными)
- [ ] `README.md`, `.gitignore`, `.mcp.json` — `.gitignore` создан (2026-05-24, обновлён 2026-05-29: + `raw/` + `tmp/`)
- [ ] Вся структура папок согласно Section 2
- [x] `decisions/D-001-bootstrap-architecture.md` — фиксирует решения brainstorming (accepted)
- [x] `decisions/D-002-spec-corrections-and-golden-plan.md` — 15 правок accepted Тимуром 2026-05-29
- [x] `docs/specs/2026-05-24-infrastructure-and-skills-design.md` — этот документ (v0.2)
- [x] `docs/cowork/prompt.md` — конституция для Cowork (v1.0; обновление под P-11 на шаге C.1.10)
- [x] `docs/extended-thinking-mechanism.md` — P-8 research resolved (2026-05-29)
- [x] `docs/cost-estimate-pp1.md` — P-6 cost estimate под Max 5x подписку: ~200 messages mid, $0 marginal (2026-05-29)
- [x] `docs/log.md` начат

### 9.2 Компонентные acceptance

| Компонент | Чем доказывается готовность |
|---|---|
| **8 скиллов** в `.claude/skills/` (P-1: было 9, philosophy-stress-test отменён) | Каждый — SKILL.md по формату `writing-narrative-skills`. 2 discipline-BLOCKER (`voice-check`, `consistency-check`) + `evidence-before-action` имеют `pressure_tested: status: yes` + `pressure-tests.md` с 3+ RED-сценариями |
| 6 субагентов в `.claude/agents/` | Каждый: name, description, tools (Read/Grep/Glob — READ-ONLY), **model: opus + effort: max** (P-8), system prompt с калибровочным блоком на golden/ + structured-format-инструкцией. Frontmatter содержит обязательный `model_used` в output schema для audit auto-switch |
| 6 скриптов в `tools/` | Каждый — exit 0/1, JSON-репорт. pytest по всем 6 зелёный. Coverage > 70%. `golden_freshness.py` поддерживает primary/secondary с весом 0.5 (P-12) и diversity_warnings (P-14); `critic_report_validator.py` поддерживает 3-element counter_test (P-7) + golden_unavailable_reason (P-4); `concern_resolution_validator.py` читает из `tmp/critic-reports/` (P-9) |
| 4 reference в `meta-skills/` | Каждый — README + byte-equal SKILL.md + METADATA.json (SHA `f2cbfbef`). Адаптированные имеют корректный `lineage:` |

### 9.3 Smoke-test end-to-end (мультиагентный, на живом материале)

> **Изменено P-3 (v0.2).** Smoke-test расширен до **4 артефактов** (добавлена мини-сценка для калибровки A4 VOICE). A4 — только на 4-м; на остальных в `adversarial-review-pass` фиксируется `not_applicable: <reason>` (валидно через `critic_report_validator.py`).

1. **Подготовка golden:** после `add-golden-example` обработки 19 партий (70 content + 19 manifests) + явное acceptance пропуска B.4.1/B.4.2 — все 6 positive категорий имеют **≥3 файла**, anti — **≥1 файл на минимум 5 категорий** (scenes / characters / dialogues / theses + любая из conflicts / adversarial-passes). `golden_freshness.py` зелёный с bootstrap-порогом. **Diversity warnings** (P-14) выведены и acknowledged в `golden/README.md` либо устранены через добивочные партии (D-002 B.6).
2. **Создаём минимальный `story-bible/thesis.md`** (~150 слов) — Поток A non-scene.
3. **Создаём минимальный `story-bible/world-rules.md`** (5 правил мира) — Поток A non-scene.
4. **Создаём 1 `characters/<one>.md`** (например, AI-safety-исследовательница "тревожная компетентность") — Поток A non-scene.
5. **Создаём 1 `scenes/smoke-test-dialogue.md`** (300-500 слов, 2-3 говорящих) — Поток A scene (+ A4 voice-check).
6. **Прогоняем через ВСЕ блокеры** (Поток A полностью, на каждом артефакте; см. § 8.1 v0.2).
7. **Ресурсный бюджет (P-6):** ~200 messages mid на Claude Code Max 5x подписку, $0 marginal — см. `docs/cost-estimate-pp1.md`. Pacing: 3-5 рабочих дней, 40-50 messages/день, каждое окно < 60% capacity (избегаем auto-switch Opus → Sonnet, см. cost-estimate § 10).

### 9.4 Мультиагентный тест критиков (R-2 enforcement + R-3 regression)

> **Изменено в v0.2.** P-7: убран количественный порог «≥3 concern/veto», заменён качественной валидацией `counter_test_attempted` (3-element structural). P-3: A4 — только на сцене (на не-сценах фиксируется not_applicable). P-5: R-3 пары разделены на calibration / holdout — acceptance на holdout. P-4: golden_unavailable_reason допустимо в bootstrap.

**Базовое требование (обновлено P-3, P-4, P-7).** На каждом из 4 smoke-test артефактов каждый из 6 субагентов вызывается через `adversarial-review-pass` минимум раз. Verdict может быть pass / concern / veto / not_applicable. **Pass-валидность** определяется структурно `critic_report_validator.py`:

- `checked` ≥ 3 — обязательно
- `evidence_from_artifact` ≥ 2 — обязательно
- `golden_calibration_used` ≥ 1 ИЛИ `golden_unavailable_reason ∈ {category-empty, category-bootstrap, category-irrelevant}` (P-4)
- `reasoning` ≥ 100 слов — обязательно
- `counter_test_attempted` со всеми тремя элементами (what_searched / why_this / why_not_found) — обязательно для pass (P-7)
- `not_applicable_reason` непустой — обязательно когда verdict содержит not_applicable (например A4 на не-сцене, P-3)
- `model_used` зафиксирован — обязательно для аудита auto-switch (cost-estimate § 10)

Pass без полного counter_test_attempted = провал валидации → retry, **не успех**.

**Auto-approval bias детектируется качеством counter_test (P-7), не количеством флагов.** Количественный порог «≥3 concern/veto на 18 verdicts» удалён — он создавал обратный incentive (манипулировать prompt'ы критиков ради «правильного» distribution).

**Из R-2 (concern resolution enforcement):** для каждого concern/veto шоураннер должен либо переписать артефакт (diff в commit), либо добавить запись в `decisions/D-NNN`. Без этого `concern_resolution_validator.py` блокирует commit. Скрипт читает из `tmp/critic-reports/<artifact-id>/` (P-9 — отчёты на диске, не из контекста).

**Из R-3 (regression tests, обновлено P-5):**
- a) **Regression set из намеренно плохих артефактов** (`tests/regression/strawmen/`, `tests/regression/moralizing/`, `tests/regression/voice-bleed/`): соответствующий критик должен выдать veto. Не выдал = не калиброван, ПП1 не принят.
- b) **Regression-пары "сильный+слабый" (P-5 split):** `tests/regression/pairs/` делится на:
  - `calibration/` (≈50% пар) — на этих парах подгоняются числовые пороги (TF-IDF voice_dissimilarity и т.д.); материал может пересекаться с golden.
  - `holdout/` (≈50% пар) — **на этих парах проверяется acceptance**; материал из других шоу/контекстов, не пересекается с calibration. **Verdicts должны разойтись** (сильный → pass, слабый → veto). Не разошлись на holdout = критик не различает, ПП1 не принят.
  - Если holdout-набор недостаточен на момент smoke-test (например, B.4.1 пропущена) — фиксируется в `tests/regression/README.md` через явное `regression_unavailable_reason:`, acceptance ослабляется с explicit flag (D-002 P-15 risk).
- c) **Cross-validation между критиками** — A5 и A3 часто будут иметь пересекающиеся возражения, это нормально. Но если они **систематически согласны на всём** — сигнал избыточности. На 4 артефактах хотя бы один раз A3 и A5 должны давать структурно разные вето.

### 9.5 Critical failures (немедленный блок acceptance)

- ❌ pytest красный по любому скрипту в `tools/`
- ❌ Любой RED pressure-сценарий **обошёл** discipline-BLOCKER скилл (т.е. дисциплина не сработала) **(P-10: переформулировано из «прошёл хотя бы один RED»)**
- ❌ Все 6 субагентов auto-approve все 4 smoke-test артефакта (P-3: 4 артефакта вместо 3)
- ❌ Любой субагент вернул pass без полного 3-element `counter_test_attempted` (P-7) или менее 100 слов в `reasoning`
- ❌ Любой субагент вернул pass с `golden_calibration_used: []` без заполненного `golden_unavailable_reason` (P-4); либо с `golden_unavailable_reason: category-bootstrap` за пределами smoke-test ПП1
- ❌ Критик не выдал veto на соответствующий regression-плохой артефакт (R-3.a)
- ❌ Verdicts критика не разошлись на **holdout** regression-паре (R-3.b, P-5 split)
- ❌ `consistency_check.py` красный на собственных fixtures
- ❌ `golden_freshness.py` красный (включая P-12 weights и P-14 diversity warnings — последние требуют либо acknowledged, либо добивочной партии)
- ❌ Любой адаптированный скилл не имеет `lineage:` или `pressure_tested: yes`
- ❌ Любой субагент не READ-ONLY (имеет Edit/Write в tools:)
- ❌ Любой субагент не имеет `effort: max` в frontmatter (P-8 нарушение R-4)
- ❌ `adversarial-review-pass` не валидирует структуру отчётов
- ❌ Критик-отчёты не пишутся в `tmp/critic-reports/` немедленно (P-9 нарушение R-2 enforcement)
- ❌ `model_used` поле отсутствует или показывает Sonnet на ≥20% критик-вызовов (P-8 + cost-estimate § 10 — escalate через D-NNN)

> P-7 (удалено): порог «На N smoke-test артефактах суммарно меньше M concern/veto» — больше не critical failure. Auto-approval bias детектируется качеством counter_test, не количеством флагов.

### 9.6 Что ПП1 НЕ обязан содержать

- ❌ Полный Story Bible (ПП2)
- ❌ 6-8 кор-каст персонажей (ПП3 — в ПП1 только 1 для smoke-test)
- ❌ Полный регистр конфликтов (ПП4)
- ❌ Эпизоды / сценарии (ПП5+)
- ❌ Полный golden корпус (параллельно)
- ❌ CI/pre-commit hooks
- ⚠️ **Remote git: добавлен** 2026-05-29 — `pesterevtimur/ai-series` (out-of-scope изначально, добавлен по требованию Тимура; не блокер acceptance, но раскрывает работу публично — fair use ограничения для `raw/` уже учтены в .gitignore)

### 9.7 Definition of Done (обновлено v0.2)

**ПП1 готов**, когда на **четырёх** живых артефактах (тезис + world-rules + 1 character + scene; P-3) каждый из 6 субагентов был вызван минимум раз с валидным structured отчётом (counter_test_attempted 3-element для pass, P-7; golden_calibration_used или golden_unavailable_reason P-4; model_used зафиксирован), прошёл regression-плохие артефакты с veto и **holdout** regression-пары с расходящимися verdicts (P-5), все 6 lint-скриптов прошли pytest зелёным и реальный прогон (включая P-12/P-13/P-14 в golden_freshness и P-7/P-4/P-9 в critic/concern validator'ах), все 3 discipline-скилла (`voice-check`, `consistency-check`, `evidence-before-action` — P-1 убрал `philosophy-stress-test`) прошли pressure-tests, критик-отчёты живут в `tmp/` → `docs/critic-reports-archive/` (P-9), а `decisions/D-001` + `decisions/D-002 v2` фиксируют все принятые архитектурные решения.

---

## 10. Language Policy

- **Артефакты творческого слоя** (Story Bible, lore, characters, episodes, scenes, decisions, golden аннотации) — **на русском**.
- **Наши собственные скиллы и субагенты** (SKILL.md, system prompts в `.claude/agents/`, lint-сообщения, отчёты критиков, CLAUDE.md) — **на русском**.
- **Superpowers skills** используются на их родном языке (английский). **Никакого перевода**. Когда шоураннер вызывает напрямую `brainstorming` или `writing-plans` — работает на английском в рамках этого инструмента.
- **Цитаты из источников** (в golden, в decisions для аргументации) — на языке оригинала, обычно английском. Без перевода. Аннотации/анализ цитаты — на русском.
- **Lineage frontmatter** в наших адаптированных скиллах — поля `name`/`description` на русском, `changes:` на русском, `source:` английский (URL/SHA).
- **Commit messages** — на русском.
- **Имена файлов и id** — на английском (kebab-case или snake_case), для cross-tool совместимости.

---

## 11. Известные риски и flagged limitations

### 11.1 R-1 (D2): Cowork bias — golden корпус отражает наш bias

Cowork приносит лучшие материалы по моим формулировкам ("Mr Robot для craft", "Pantheon для AI"). Это значит, что калибровка субагентов отражает **вкус шоураннера + Тимура**, не объективную "сильность".

**Митигация:** в `golden/README.md` зафиксировано **golden-audit правило** — раз в квартал Cowork ищет материалы, противоречащие нашему текущему пониманию. Если находятся — пересмотр калибровки.

### 11.2 R-2 (D6): Golden subjective by nature

Не дыра, а методологическое ограничение. Зафиксировано в README golden/ для будущих контрибьюторов.

### 11.3 R-3 (D9): Multi-agent operational complexity

Cowork (Claude.ai) ↔ Claude Code ↔ Claude Desktop — координация ручная через копирование артефактов. Это **существенная operational нагрузка**, особенно при росте проекта.

**Митигация в ПП2+:** возможно скилл `session-bootstrap`, который при старте Claude Code сессии загружает контекст (master-plan tail, log.md tail, текущий ПП).

### 11.4 R-4 (D10): cost commitment — обновлено 2026-05-29 (P-6)

6 субагентов × Opus + effort: max × возможные повторные вызовы при failed validation × передача контекста.

**Обновлено P-6 (D-002 v2, accepted 2026-05-29).** Конкретика по бюджету в `docs/cost-estimate-pp1.md`:

- **Финансовый сценарий:** Claude Code Max 5x подписка ($100/мес flat). Marginal cost ПП1 = **$0**.
- **Ресурсный бюджет:** ~200 messages mid (130-300 коридор) на полный ПП1 (smoke-test + regression + pressure-tests + 2 rework rounds/артефакт).
- **Распределение:** 3-5 рабочих дней, 40-50 messages/день, каждое окно < 60% capacity.
- **Главный риск R-4:** auto-switch Opus → Sonnet при ~70-80% capacity окна (см. GitHub anthropics/claude-code#8449). Митигация: pacing + monitoring `model_used` в каждом критик-отчёте (P-7); если систематически Sonnet — escalate D-NNN (upgrade на Max 20x или direct API за $40 mid).
- **Альтернатива (Sonnet для A2/A4/A6):** экономит ~15 messages mid, не оправдывает калибровочный риск. Отклонена.

**Митигация в ПП5+ (сезон):** при росте бюджета будет переоценка на основе фактических метрик ПП1.

### 11.5 Открытые технические вопросы для writing-plans

1. ~~Механизм extended thinking в `.claude/agents/` frontmatter — поддерживается ли явно?~~ **Resolved 2026-05-29** (P-8): поле `effort: max` в frontmatter — канонический механизм; `thinking_budget:` / `extended_thinking:` не существуют. Подробно: `docs/extended-thinking-mechanism.md`.
2. Конкретный SHA Superpowers — `f2cbfbef` или свежий? Оставлен `f2cbfbef` per D-001; не пересматриваем в ПП1.
3. TF-IDF пороговое значение для voice_dissimilarity.py — стартовое 0.65, калибровать на `tests/regression/pairs/calibration/` (P-5 split); acceptance на `holdout/`.

### 11.6 Anti-corpus completeness — flagged risk (P-15)

> **Принято Тимуром 2026-05-29 как flagged risk acceptance.** Cowork-партия `anti-examples-batch-02` (B.4.1) и `adversarial-passes-batch-03` (B.4.2 institutional voice) **сознательно пропущены** в ПП1.

**Состояние anti-корпуса на момент ПП1 acceptance:**

| Категория | Anti-файлы | Покрытие |
|---|---|---|
| `scenes` | 3 (в batch-01) | OK |
| `characters` | 2 (Dexter, GoT в anti-batch-01) | bootstrap-минимум |
| `dialogues` | 1 (TD2 в anti-batch-01) | bootstrap-минимум |
| `theses` | 1 (Lost в anti-batch-01) | bootstrap-минимум |
| `conflicts` | **0** | **gap** — R-3 калибровка A3 на нижнем bootstrap-пороге |
| `adversarial-passes` | **0** | **gap** — R-3 калибровка A5 на нижнем bootstrap-пороге |

**Воздействие.** A3 (`incentive-cartographer`) и A5 (`philosophy-adversarial`) могут показать систематический pass / confuse в smoke-test'е — это будет означать, что у них нет калибровочного anti-материала, и они не научились различать.

**Митигация в ПП2.** Если smoke-test ПП1 покажет такой паттерн на A3/A5, B.4.1 заказывается у Cowork в ПП2 и регрессия повторно прогоняется. Эта развилка зафиксирована как пред-D-NNN на старт ПП2.

**Что НЕ делаем как митигацию.**
- ❌ Не блокируем acceptance ПП1 на отсутствии anti для conflicts/adversarial-passes (Тимур accepted risk).
- ❌ Не подменяем real anti на derived anti-lessons из positive (P-13 — derived НЕ считаются).

---

## Приложение A. Используемые Superpowers скиллы (без локальной копии)

- `brainstorming` (был использован в этой сессии)
- `writing-plans` (для следующих ПП)
- `test-driven-development` (для tools/)
- `subagent-driven-development` (для исполнения планов)
- `requesting-code-review` (финальный ревью)
- `executing-plans` (когда план готов)
- `using-git-worktrees` (опционально для крупных ПП)

## Приложение B. Источники

- Конституция автора — первое сообщение brainstorming-сессии 2026-05-24
- `C:\Users\user\Documents\Claude\agentic-ops-cc\` — методологический backbone
- Superpowers SHA `f2cbfbef` — pinned upstream
- `decisions/D-001-bootstrap-architecture.md` — фиксация базовых развилок (accepted)
- `decisions/D-002-spec-corrections-and-golden-plan.md` — 15 правок P-1..P-15 + план golden (v2 accepted 2026-05-29)
- `docs/cowork/prompt.md` — конституция внешнего ресёрч-агента (v1.0; обновление под P-11 на шаге C.1.10)
- `docs/extended-thinking-mechanism.md` — research-001 под P-8 (effort: max в frontmatter)
- `docs/cost-estimate-pp1.md` — cost estimate под P-6 (Max 5x подписка, ~200 messages mid)
- `raw/_cowork-dumps/` — 19 партий / 74 файла (на 2026-05-29; gitignored — fair use only internal); обработка через `add-golden-example` ждёт ПП1 implementation
