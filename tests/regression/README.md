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

- На calibration — подгоняем числовые пороги
- На holdout — проверяем что критик различает в принципе

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
