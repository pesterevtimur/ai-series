---
id: spec-001-infrastructure-and-skills
title: Инфраструктура и скиллы Auto-ai-series — ПП1
version: 0.1
date: 2026-05-24
status: approved
relates_to:
  - decisions/D-001-bootstrap-architecture.md
  - docs/cowork/prompt.md
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
│   ├── skills/                  # 9 скиллов (см. Section 3)
│   │   ├── draft-story-bible-section/
│   │   ├── draft-character-sheet/
│   │   ├── adversarial-review-pass/
│   │   ├── philosophy-stress-test/
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
│   ├── log.md                    # журнал сессий (создан)
│   ├── master-plan.md            # план на сезон / неделю / день (создаётся при старте ПП2)
│   └── references/               # аннотированная библиотека (наполняется параллельно)
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
│   └── D-001-bootstrap-architecture.md  # создан
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

## 3. Скиллы (9 скиллов)

Принцип: **минимальный жизнеспособный набор для smoke-test**, без преждевременной фабрики. Расширим в следующих под-проектах.

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
| `philosophy-stress-test` | discipline-BLOCKER | Запускает изолированный субагент `philosophy-adversarial` через Task tool на любом крупном артефакте. Возвращает 3 сильнейших контраргумента + где тезис сломан + что делать. Без зелёного отчёта нельзя финализировать артефакт. | **Да** |
| `voice-check` | discipline-BLOCKER | После любой сцены с >1 говорящим: запускает `tools/voice_dissimilarity.py` как preflight, затем вызывает `voice-differentiator` субагент. Возвращает confusion-matrix. | **Да** |
| `consistency-check` | discipline-BLOCKER | Запускает `tools/consistency_check.py`, который сверяет факты артефакта против Bible / character-sheets через frontmatter `references`. Без зелёного — нельзя merge'ить. | **Да** |
| `adversarial-review-pass` | orchestration | Последовательно зовёт `lore-realism-checker` (A1), `incentive-cartographer` (A3), `character-truth-keeper` (A2), `philosophy-adversarial` (A5), `audience-bored-detector` (A6) через Task tool. Для каждого: валидирует структуру отчёта через `critic_report_validator.py`, при failed validation повторяет вызов. Собирает агрегированный отчёт. | Нет (не блокер сам по себе) |
| `add-golden-example` | research-orchestration | Workflow обработки batch'а от Cowork: читает `raw/_cowork-dumps/<batch>/`, шоураннер делает reconstruction для закрытого контента или прямые выдержки для открытого, пишет в `golden/<category>/`, прогоняет `golden_freshness.py`. | Нет |
| `draft-story-bible-section` | creative + **дивергентная generation (R-1)** | Создание/обновление секции `story-bible/` через **3 параллельных Task-вызова** с разными доминантными уклонами: LORE-dominant, PHILOSOPHY-dominant, CHARACTER-dominant. Шоураннер собирает 3 структурно разных варианта, явно выбирает или синтезирует. Затем обязательный `adversarial-review-pass`. | Нет |
| `draft-character-sheet` | creative + **дивергентная generation (R-1)** | Создание character-sheet через 3 параллельных Task-вызова с уклонами: CHARACTER-dominant ("декларируемая ценность + incentive"), CONFLICT-dominant ("где сильнейшее столкновение incentives"), PHILOSOPHY-dominant ("позиция по ИИ в её сильнейшей формулировке"). Сборка шоураннером. | Нет |

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
| `philosophy-adversarial.md` | **A5** PHILOSOPHY | **Opus + ext.thinking** | Перед финализацией Bible/character arc/эпизода. Триггер: `philosophy-stress-test` скилл. |
| `incentive-cartographer.md` | **A3** CONFLICT | **Opus + ext.thinking** | Перед финализацией сцен и арок. Триггер: `adversarial-review-pass`. |
| `voice-differentiator.md` | **A4** DIALOGUE | **Opus + ext.thinking** | После любой сцены с >1 говорящим. Триггер: `voice-check`. |
| `lore-realism-checker.md` | **A1** LORE | **Opus + ext.thinking** | Касается реальных корп/полит/тех механизмов. Триггер: `adversarial-review-pass`. |
| `character-truth-keeper.md` | **A2** CHARACTER | **Opus + ext.thinking** | Перед финализацией сцены/эпизода. Триггер: `adversarial-review-pass`. |
| `audience-bored-detector.md` | **A6** AUDIENCE | **Opus + ext.thinking** | Перед финализацией эпизода. Триггер: `adversarial-review-pass`. |

**Cost commitment (R-4).** "Все 6 на Opus + extended thinking" — явное решение приоритета качества над стоимостью. См. Section 11 risks.

### 4.2 Структура файла субагента

```yaml
---
name: philosophy-adversarial
description: Адверсариальный критик философской целостности. Вызывается перед финализацией Story Bible, character arc, эпизода. Цель — СЛОМАТЬ центральный тезис.
tools: Read, Grep, Glob
model: opus
# extended thinking максимально включено через все доступные механизмы:
# - model: opus в frontmatter
# - инструкция "ultrathink перед каждым выводом" в system prompt
# - env-переменные если поддерживаются (проверить в implementation phase)
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
reasoning:                        # обязательно, минимум 100 слов
  "Почему именно такой verdict. Конкретно, без славословия и без обтекаемости."
flags:                            # обязательно если verdict != pass; иначе []
  - severity: high | medium | low
    issue: "конкретная проблема"
    location: "где в артефакте"
    suggestion: "что попробовать (опционально)"
counter_test_attempted:           # обязательно для pass — что ты ПЫТАЛСЯ найти и не нашёл
  "Я искал X, Y, Z. Не нашёл, потому что в артефакте присутствует / отсутствует ..."
```

**Ключевое правило:** verdict=pass требует заполненного `counter_test_attempted`. Pass — это не отсутствие возражений, это активно выполненный counter-test, который не сработал. Не сделал counter-test = не имеешь права говорить pass. Валидация через `tools/critic_report_validator.py`.

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
type: positive  # positive | anti-example
reconstruction: false  # true если это наш аналог "в стиле X"
license: "fair use / educational reference"
---

[расшифровка / выдержка / описание / reconstruction]

## Что брать
## Что НЕ воспроизводить
```

### 5.4 Workflow наполнения (через Claude Cowork)

См. полный промпт `docs/cowork/prompt.md`. Принцип: **внешний агент в Claude.ai web**, итеративная работа, обязательный апрув списка кандидатов до сбора, выход в Artifacts → Тимур копирует в `raw/_cowork-dumps/<batch>/`. Шоураннер обрабатывает партию через скилл `add-golden-example` и финализирует в `golden/<category>/`.

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
| `golden_freshness.py` | Проверяет состояние `golden/`: минимум N+M в каждой категории, frontmatter полный, аннотация не пустая. | Из скилла `add-golden-example` после merge; в smoke-test |
| `critic_report_validator.py` | Парсит YAML-отчёт критика. Проверяет все обязательные поля + minimum thresholds (`checked` ≥ 3, `evidence_from_artifact` ≥ 2, для pass — `counter_test_attempted` непустой и `reasoning` ≥ 100 слов). | Из `adversarial-review-pass` после каждого вызова субагента, до агрегации |
| **`concern_resolution_validator.py`** (новый, R-2) | Парсит последний adversarial-review отчёт + git diff текущего commit. Для каждого concern/veto требует либо diff артефакта явно адресующий issue, либо запись в `decisions/D-NNN-*.md` с обоснованием "оставляю, потому что...". Без этого commit блокируется через evidence-before-action. | Pre-finalize и pre-commit |

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
└── regression/                   # из R-3
    ├── strawmen/
    ├── moralizing/
    ├── voice-bleed/
    ├── pairs/
    │   ├── thesis-strong.md
    │   ├── thesis-weak.md
    │   ├── character-strong.md
    │   ├── character-weak.md
    │   └── ... (для каждого критика своя пара)
    └── README.md
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

```
0. Тимур: "Нужен централный тезис проекта в одной фразе"
   │
1. Шоураннер → invoke `brainstorming` (Superpowers, напрямую)
   │
2. Шоураннер → invoke `draft-story-bible-section` (наш скилл)
   │  *** R-1: дивергентная generation ***
   │  Запускает 3 ПАРАЛЛЕЛЬНЫХ Task-вызова:
   │    a) LORE-dominant generator
   │    b) PHILOSOPHY-dominant generator
   │    c) CHARACTER-dominant generator
   │  Каждый читает: story-bible/ (существующее), CLAUDE.md законы, golden/theses/
   │  Каждый возвращает СТРУКТУРНО РАЗНЫЙ драфт
   │  Шоураннер собирает 3 варианта, явно выбирает или синтезирует
   │
3. ОБЯЗАТЕЛЬНО → invoke `philosophy-stress-test`
   │  вызывает A5 субагент через Task tool с изолированным контекстом
   │  A5 читает: артефакт + golden/adversarial-passes/ + golden/anti-examples/strawmen/
   │  возвращает: structured YAML отчёт (verdict / checked / evidence / reasoning / counter_test)
   │  validation через critic_report_validator.py
   │
4. Шоураннер реагирует: переписывает драфт ИЛИ явно фиксирует в decisions/D-NNN
   │
5. ОБЯЗАТЕЛЬНО → invoke `adversarial-review-pass`
   │  последовательно зовёт A1, A3, A2, A6 (A4 — отдельно через voice-check для сцен)
   │  через Task tool, каждый со своим golden/<category>/ для калибровки
   │  каждый отчёт валидируется через critic_report_validator.py
   │  если validation FAIL — повторный вызов с инструкцией "переделай"
   │  собирает агрегированный отчёт в Markdown summary
   │
6. Шоураннер реагирует на каждый отчёт критика
   │  если есть несовместимые вето — экспоунит конфликт Тимуру, не усредняет
   │
7. ОБЯЗАТЕЛЬНО → invoke `consistency-check`
   │  запускает tools/consistency_check.py
   │
8. ОБЯЗАТЕЛЬНО → *** R-2: invoke `concern_resolution_validator` ***
   │  парсит последний adversarial-review отчёт + текущий diff
   │  для каждого concern/veto требует либо адресующий diff, либо decisions/D-NNN
   │  без этого commit блокируется через evidence-before-action
   │
9. ОБЯЗАТЕЛЬНО → invoke `evidence-before-action`
   │  блокирует merge если claims в commit message не сопровождены свежими выводами
   │
10. Write to story-bible/thesis.md (Edit/Write tool)
    ↓
11. Commit `bible: …` с обоснованием
    ↓
12. Append одну строку в docs/log.md по конвенции `[YYYY-MM-DD] bible | thesis v0.1`
    ↓
13. Если развилка была значимой — append в decisions/D-NNN-*.md
```

### 8.2 Поток D — Добавление golden example

```
0. Шоураннер замечает пробел в калибровке
   │
1. Шоураннер формулирует ТЗ для Cowork → передаёт Тимуру
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
   │
6. Write to golden/<category>/<file>.md
   │
7. Append символлинк в raw/_processed/ → исходный raw файл (для аудита)
   │
8. ОБЯЗАТЕЛЬНО → invoke `golden_freshness.py`
   │
9. Commit `golden: ... — N positive + M anti for X calibration`
   │
10. Append в docs/log.md
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

- [ ] `Auto-ai-series/` git-инициализирован на `main`
- [ ] `CLAUDE.md` с 4-5 законами проекта (адаптированными)
- [ ] `README.md`, `.gitignore`, `.mcp.json`
- [ ] Вся структура папок согласно Section 2
- [ ] `decisions/D-001-bootstrap-architecture.md` — фиксирует решения brainstorming
- [ ] `docs/specs/2026-05-24-infrastructure-and-skills-design.md` — этот документ
- [ ] `docs/cowork/prompt.md` — конституция для Cowork
- [ ] `docs/log.md` начат

### 9.2 Компонентные acceptance

| Компонент | Чем доказывается готовность |
|---|---|
| 9 скиллов в `.claude/skills/` | Каждый — SKILL.md по формату `writing-narrative-skills`. 3 discipline-BLOCKER имеют `pressure_tested: status: yes` + `pressure-tests.md` с 3+ RED-сценариями |
| 6 субагентов в `.claude/agents/` | Каждый: name, description, tools (Read/Grep/Glob — READ-ONLY), model: opus, system prompt с калибровочным блоком на golden/ + structured-format-инструкцией |
| 6 скриптов в `tools/` | Каждый — exit 0/1, JSON-репорт. pytest по всем 6 зелёный. Coverage > 70% |
| 4 reference в `meta-skills/` | Каждый — README + byte-equal SKILL.md + METADATA.json (SHA `f2cbfbef`). Адаптированные имеют корректный `lineage:` |

### 9.3 Smoke-test end-to-end (мультиагентный, на живом материале)

1. **Подготовка golden:** минимум 4-5 positive + 2-3 anti в категориях, для которых Cowork собрал материал (scenes — есть; dialogues/characters/theses — параллельно). `golden_freshness.py` зелёный.
2. **Создаём минимальный story-bible/thesis.md** (на основе тезиса из конституции, ~150 слов).
3. **Прогоняем через ВСЕ блокеры** (см. Поток A полностью).
4. **Создаём 1 character-sheet** (например, AI-safety-исследовательница "тревожная компетентность").
5. **Создаём минимальный world-rules.md** (5 правил мира).

### 9.4 Мультиагентный тест критиков (R-2 enforcement + R-3 regression)

**Базовое требование:** На каждом из 3 smoke-test артефактов каждый из 6 субагентов должен вернуть полный structured отчёт. Verdict может быть pass / concern / veto, **но pass без заполненных полей `checked` (3+), `evidence_from_artifact` (2+), `golden_calibration_used` (1+), `reasoning` (100+ слов) и `counter_test_attempted` (явная попытка) — считается провалом**, не успехом.

**Дополнительно:** на 3 артефактах суммарно должно быть **минимум 3 concern или veto** (распределение свободное). Если все 18 verdicts = pass — это сигнал auto-approval bias, не успех.

**Из R-2 (concern resolution enforcement):** для каждого concern/veto шоураннер должен либо переписать артефакт (diff в commit), либо добавить запись в `decisions/D-NNN`. Без этого `concern_resolution_validator.py` блокирует commit.

**Из R-3 (regression tests):**
- a) **Regression set из намеренно плохих артефактов** (`tests/regression/strawmen/`, `tests/regression/moralizing/`, `tests/regression/voice-bleed/`): соответствующий критик должен выдать veto. Не выдал = не калиброван, ПП1 не принят.
- b) **Regression-пары "сильный+слабый"** (`tests/regression/pairs/`) для каждого из 6 критиков: verdicts должны разойтись (сильный → pass, слабый → veto). Не разошлись = критик не различает.
- c) **Cross-validation между критиками** — A5 и A3 часто будут иметь пересекающиеся возражения, это нормально. Но если они **систематически согласны на всём** — сигнал избыточности. На 3 артефактах хотя бы один раз A3 и A5 должны давать структурно разные вето.

### 9.5 Critical failures (немедленный блок acceptance)

- ❌ pytest красный по любому скрипту в `tools/`
- ❌ Любой discipline-BLOCKER скилл прошёл хотя бы один RED pressure-сценарий
- ❌ Все 6 субагентов auto-approve все 3 smoke-test артефакта
- ❌ Любой субагент вернул pass с пустым `counter_test_attempted` или менее 100 слов в `reasoning`
- ❌ Любой субагент вернул pass без явного `golden_calibration_used`
- ❌ На 3 smoke-test артефактах суммарно меньше 3 concern/veto
- ❌ Критик не выдал veto на соответствующий regression-плохой артефакт (R-3.a)
- ❌ Verdicts критика не разошлись на regression-паре (R-3.b)
- ❌ `consistency_check.py` красный на собственных fixtures
- ❌ `golden_freshness.py` красный
- ❌ Любой адаптированный скилл не имеет `lineage:` или `pressure_tested: yes`
- ❌ Любой субагент не READ-ONLY (имеет Edit/Write в tools:)
- ❌ `adversarial-review-pass` не валидирует структуру отчётов

### 9.6 Что ПП1 НЕ обязан содержать

- ❌ Полный Story Bible (ПП2)
- ❌ 6-8 кор-каст персонажей (ПП3 — в ПП1 только 1 для smoke-test)
- ❌ Полный регистр конфликтов (ПП4)
- ❌ Эпизоды / сценарии (ПП5+)
- ❌ Полный golden корпус (параллельно)
- ❌ CI/pre-commit hooks
- ❌ Remote git (только локальный)

### 9.7 Definition of Done (одной фразой)

**ПП1 готов**, когда на трёх живых артефактах (тезис + 1 character + 5 правил мира) каждый из 6 субагентов был вызван хотя бы раз с структурированным отчётом, суммарно дал минимум 3 concern/veto, прошёл regression-плохие артефакты с veto и regression-пары с расходящимися verdicts, все 6 lint-скриптов прошли pytest зелёным и реальный прогон, все discipline-скиллы прошли pressure-tests, а `decisions/D-001-bootstrap-architecture.md` фиксирует все принятые архитектурные решения.

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

### 11.4 R-4 (D10): Token cost — explicit commitment

6 субагентов × Opus + extended thinking × возможные повторные вызовы при failed validation × передача контекста = **десятки тысяч токенов на каждый артефакт**. На полный сезон (10 эпизодов × N сцен) это может выйти в значительную сумму.

**Принято:** оставляем "все 6 на Opus + ext.thinking" по запросу Тимура (приоритет качества). Альтернатива (Opus для A5/A3/A1, Sonnet для A2/A4/A6) отклонена в D-001 R-4.

**Митигация:** если cost станет блокером в ПП5+ — пересмотреть с этой альтернативой.

### 11.5 Открытые технические вопросы для writing-plans

1. Механизм extended thinking в `.claude/agents/` frontmatter — поддерживается ли явно?
2. Конкретный SHA Superpowers — `f2cbfbef` или свежий?
3. TF-IDF пороговое значение для voice_dissimilarity.py — стартовое 0.65, калибровать на R-3 парах.

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
- `decisions/D-001-bootstrap-architecture.md` — фиксация развилок
- `docs/cowork/prompt.md` — конституция внешнего ресёрч-агента
- `raw/_cowork-dumps/2026-05-23-scenes-batch-01/` — первый собранный batch (7 материалов + manifest), обработка ждёт ПП2
