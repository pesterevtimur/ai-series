---
id: lore-strong-cal
version: 1
status: draft
type: regression-pair
pair_role: A1
pair_strength: strong
pair_split: calibration
expected_verdict: pass
references: []
---

# Фрагмент world-rules — корп-структура и regulatory exposure лаборатории «Atlas Labs»

## Корпоративная форма

«Atlas Labs» — Public Benefit Corporation, инкорпорирована в штате Делавэр под DGCL §362. Public benefit purpose в уставе: «responsible development of advanced AI systems for the long-term benefit of humanity». Долгосрочная цель закреплена параллельно фидуциарной обязанности перед акционерами — это не освобождает совет от обязанности максимизировать акционерную стоимость, но даёт юридическую защиту от иска акционеров за решения, мотивированные benefit purpose.

## Капитал и инвесторы

Серия C закрыта в 2024 на 7.5 миллиардов долларов; lead — Lightspeed; participating — Google ($2B компонент cloud commitments), Salesforce Ventures, Spark Capital. Структура голосов: founders сохраняют supermajority через class B (10:1). Класс B автоматически конвертируется в класс A при transfer, кроме transfer в trust founder'а.

## Совет директоров (по состоянию на 2026)

Семь мест. Три — founders. Три — independent (один от Series A lead, два независимых, утверждённых обеими сторонами). Одно — long-term benefit trust, имеющий право назначать и снимать board members и обладающий правом veto по узкому списку решений (изменение mission, M&A выше threshold, разрыв RSP).

## Regulatory exposure

- **EU AI Act:** frontier-системы лаборатории попадают под Article 51 (general-purpose AI models with systemic risk), threshold 10^25 FLOPs training compute. Обязательства: model evaluations, adversarial testing, serious incident reporting в EU AI Office в течение 15 дней.
- **US Executive Order 14110** (Biden, октябрь 2023; статус под Trump-administration review): pre-training compute reporting threshold 10^26 FLOPs через Defense Production Act. Лаборатория отчитывается дважды в год.
- **NIST AI Risk Management Framework 1.0** (январь 2023, generic profile + GenAI profile июль 2024): применяется добровольно, mapping в внутреннем RMF policy.

## Policy commitments

Подписант **Frontier Model Forum** (вместе с Anthropic, OpenAI, Google DeepMind, Microsoft). Внутренний Responsible Scaling Policy v2.4 — ASL-classification по capability thresholds, обязательное pre-deployment evaluation на CBRN / cyber / autonomy uplift, паузы при достижении threshold до подтверждения safety measures.
