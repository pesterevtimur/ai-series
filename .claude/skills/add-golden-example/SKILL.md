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
