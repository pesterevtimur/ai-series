---
id: golden-readme
title: Golden data set — README + политики корпуса
date: 2026-05-29
status: bootstrap
phase: pre-implementation
relates_to:
  - docs/specs/2026-05-24-infrastructure-and-skills-design.md § 5 § 9.3 § 11.1 § 11.2
  - decisions/D-002-spec-corrections-and-golden-plan.md § P-11 § P-12 § P-13 § P-14 § P-15
  - docs/cowork/prompt.md v1.1
---

# Golden data set — README

Этот файл — **заготовка** для финального `golden/README.md`. Создан на шаге C.1 пункт 11
(после accept D-002 v2 Тимуром 2026-05-29) до старта ПП1 implementation. Фиксирует
политики корпуса, чтобы скилл `add-golden-example` при первом запуске не дрейфовал.

После первого прогона `add-golden-example` README обновляется фактическими цифрами
и фиксирует diversity-acknowledged. Сейчас все статусы **bootstrap / pending**.

---

## 1. Назначение golden корпуса

1. **Калибровка субагентов.** Каждый из 6 критиков (A1 LORE, A2 CHARACTER, A3 INCENTIVE,
   A4 VOICE, A5 PHILOSOPHY, A6 AUDIENCE) перед адверсариальным проходом читает golden из
   своей primary_category — чтобы понимать, что значит «сильно» в этой категории.
2. **Регрессионные тесты** для скиллов: когда меняется prompt субагента, перегоняем
   на тех же golden examples, смотрим не упал ли уровень.
3. **Anti-examples** показывают границу провала: вот это страумен, морализаторство,
   voice-bleed.

Подробнее: spec § 5.1.

---

## 2. Структура корпуса

```
golden/
├── README.md                       ← этот файл
├── scenes/                         ← scene-structure эталоны
├── dialogues/                      ← voice-differentiation эталоны
├── characters/                     ← character-truth эталоны
├── conflicts/                      ← incentive-conflict эталоны
├── adversarial-passes/             ← philosophical-strength эталоны
├── theses/                         ← central-thesis эталоны
└── anti-examples/
    ├── strawmen/                   ← слабые версии оппонирующей позиции
    ├── moralizing/                 ← морализаторские монологи
    ├── dialogue-bleed/             ← voice-bleed
    └── ...                         ← добавляются по мере сбора
```

Файл физически лежит в `golden/<primary_category>/` (P-12). При необходимости
учитывается в дополнительных категориях через `secondary_categories` с весом 0.5
(см. § 6 ниже).

---

## 3. Frontmatter golden-файла (обязательный)

```yaml
---
id: golden-<source-slug>-<short-id>
source: "<Show name> <SxxEyy> '<Episode title>', <timecode-or-section>"
aspect: <scene-structure | character-truth | incentive | philosophical-strength | dialogue-voice | thesis-formulation>
lesson: "<краткая формулировка чему этот эталон учит критика, на русском>"
example_type: positive            # P-13: positive | anti-example — заменяет старое type
primary_category: scenes          # P-12: одна из 6 валидных категорий
secondary_categories: []          # P-12: 0-N из оставшихся 5, без дубликатов primary
reconstruction: false             # true если это наш аналог "в стиле X"
license: "fair use / educational reference"
batch: "<batch-id-from-cowork>"   # P-14
source_author: "<Author name>"    # P-14
source_show: "<Show or essay subject>"  # P-14
---
```

См. также: spec § 5.3.

---

## 4. P-11 политика — golden vs cowork-notes

> **Граница mandate (P-11).** Cowork описывает эталоны; не предписывает дизайн нашего сериала.

При обработке батча через скилл `add-golden-example`:
- **описание эталона** → `golden/<primary_category>/<file>.md` (acceptance material)
- **блок «Возможные применения / рекомендации к нашему сериалу»** → `docs/cowork-notes/<batch>.md`
  (secondary, seed для ПП2/ПП3, не authority)

Это не теряет рекомендации Cowork — оно их **изолирует** от калибровочного материала
критиков. Если рекомендация Cowork окажется ценной, шоураннер вытащит её из cowork-notes
в ПП2/ПП3 при необходимости.

---

## 5. P-13 политика — derived anti-lessons ≠ real anti

> **Derived ≠ real.** Блок «Возможные anti-lessons из источника» в positive файлах — это derived mental exercise.

- `critic_report_validator.py` при подсчёте anti для калибровки учитывает **только**
  файлы с `example_type: anti-example` в frontmatter.
- Derived anti-lessons из positive **не считаются** для acceptance criterion 9.4.a.
- Скилл `add-golden-example` при обработке positive файла переносит блок «Возможные
  anti-lessons» в `docs/cowork-notes/derived-anti-lessons/<file>.md` (архив, не часть golden).

Будущие anti-партии заказываются у Cowork отдельно, с явным `example_type: anti-example`
по каждому файлу.

---

## 6. P-12 политика — primary + secondary, без symlinks

- Файл физически в `golden/<primary_category>/`.
- `secondary_categories: [...]` — 0-N категорий из оставшихся 5, без дубликатов primary.
- `golden_freshness.py` учитывает файл как:
  - в primary — полностью (+1.0 к подсчёту category coverage)
  - в каждой secondary — с весом 0.5 (+0.5 к подсчёту category coverage)
- Критик при калибровке через `golden_calibration_used` указывает primary_category файла,
  не вычитает дробной доли.
- Альтернатива через symlinks отклонена (Windows compatibility + git).

---

## 7. P-14 — diversity warnings + diversity_acknowledged

`golden_freshness.py` выводит warnings в отдельную секцию JSON-отчёта (не блокеры commit'а):

| Условие | Warning |
|---|---|
| `author_share > 50%` в любой категории | "author X dominates category Y" |
| `show_share > 60%` в `scenes` / `characters` / `conflicts` | "show X dominates category Y" |
| Одна партия (`batch:`) содержит ≥3 файла одного `source_author` | "author X concentrated in batch Y" |

**Что делать с warnings.** Либо:

a) Заказать у Cowork добивочную партию с явным запросом diversity, и устранить gap.
b) Зафиксировать **diversity_acknowledged** в этом README, секция § 7.1 ниже,
   с явным reason почему перекос остаётся.

### 7.1 Diversity acknowledged log

> Каждая запись = один acknowledged warning. Формат:
> ```
> [YYYY-MM-DD] <category>: <warning> — acknowledged: <reason>
> ```

(Пусто на этапе bootstrap; заполняется после первого прогона `add-golden-example`
и `golden_freshness.py`.)

```
[ ] (заполнится после первого прогона)
```

---

## 8. Golden audit правило (квартально / per 50 артефактов)

> Spec § 5.6 + § 11.1 + § 11.2.

**Принцип.** Корпус отражает калибровку шоураннера + Тимура — **не объективную планку**.
Регулярный audit предотвращает дрейф в self-confirming bias.

**Триггер.** Раз в квартал ИЛИ при достижении 50 финализированных артефактов
(scenes/characters/conflicts суммарно), что наступит раньше.

**Процедура.**
1. Шоураннер инициирует golden-audit сессию.
2. Cowork получает ТЗ: «искать материалы, **противоречащие** нашему текущему пониманию
   "сильно" в категории X». Не материалы того же типа — материалы, которые ломают наш
   текущий критерий.
3. Если находятся — пересмотр калибровки (новые golden / переоценка существующих).
4. Audit фиксируется в `docs/log.md` строкой `[YYYY-MM-DD] golden | audit-N — пересмотр категории X / no change`.

### 8.1 Golden audit log

```
[ ] (заполнится после первого квартального audit'а)
```

---

## 9. Известные flagged risks

### 9.1 Cowork bias (spec § 11.1)

Cowork приносит лучшие материалы по нашим формулировкам ("Mr Robot для craft", "Pantheon
для AI"). Калибровка субагентов отражает **вкус шоураннера + Тимура**, не объективную
"сильность". Митигация — golden-audit (§ 8).

### 9.2 Golden subjective by nature (spec § 11.2)

Не дыра, а методологическое ограничение. Корпус — bootstrap-инструмент калибровки,
не объективная истина. Будущие контрибьюторы могут предложить альтернативные критерии
через D-NNN-*.md.

### 9.3 P-15 — Anti-corpus completeness (spec § 11.6)

> Зафиксировано как flagged risk acceptance Тимуром 2026-05-29.

**Состояние на ПП1 bootstrap acceptance** (после пропуска Cowork-партий B.4.1 и B.4.2):

| Категория | Anti-файлы | Статус |
|---|---|---|
| `scenes` | 3 (в anti-batch-01) | OK |
| `characters` | 2 (Dexter, GoT) | bootstrap-минимум |
| `dialogues` | 1 (TD2) | bootstrap-минимум |
| `theses` | 1 (Lost) | bootstrap-минимум |
| `conflicts` | **0** | **gap** — R-3 калибровка A3 на нижнем bootstrap-пороге |
| `adversarial-passes` | **0** | **gap** — R-3 калибровка A5 на нижнем bootstrap-пороге |

**Действие при materialization risk'а:** если ПП1 smoke-test покажет систематический
pass / confuse на A3 или A5 — B.4.1 anti-examples-batch-02 (для conflicts + adversarial
+ voice-bleed) заказывается у Cowork в ПП2, R-3 регрессия для соответствующих критиков
повторно прогоняется.

---

## 10. Acceptance bootstrap state (на старт ПП1 implementation)

После accept D-002 v2 и до старта ПП1 implementation корпус **пуст** —
`raw/_cowork-dumps/` содержит 19 партий × 74 content файла, но обработка через
`add-golden-example` ещё не запущена (это часть ПП1 implementation, шаг 13 D-002 C.1).

После первого прогона `add-golden-example` ожидаемое состояние:

| Категория | Positive (target) | Anti (target) | Acceptance |
|---|---|---|---|
| `scenes` | ≥3 (saturated до ~19) | ≥1 | OK |
| `characters` | ≥3 (~20) | ≥1 | OK |
| `dialogues` | ≥3 (~7) | ≥1 | OK |
| `theses` | ≥3 (~4) | ≥1 | OK |
| `conflicts` | ≥3 (~10) | 0 (acknowledged P-15) | flagged |
| `adversarial-passes` | ≥3 (~7) | 0 (acknowledged P-15) | flagged |

`golden_freshness.py` должен пройти зелёным с bootstrap-порогом (учётом P-14 warnings
acknowledged либо устранённых).

---

## 11. История изменений README

- **2026-05-29 v0 (bootstrap).** Создан как заготовка на шаге C.1 пункт 11 D-002 v2
  acceptance. Корпус ещё не наполнен. Diversity-acknowledged + golden-audit log пусты.
  Будут заполняться после первого прогона `add-golden-example` в ПП1 implementation.
