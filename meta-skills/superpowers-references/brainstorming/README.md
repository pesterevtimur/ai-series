# brainstorming — pinned reference

**Origin:** obra/superpowers@f2cbfbef (== local v5.1.0)
**Pinned on:** 2026-05-30
**Used as:** используется напрямую, pinned для drift-detection

## Зачем pinned

Используется напрямую при любой творческой развилке (выбор тезиса, дизайна ИИ, арки, имени персонажа). НЕ адаптируется — структура подходит как есть. Pinned для drift-detection: если upstream поменяется, мы хотим знать.

## Как используется

- Напрямую через Skill tool (`Skill brainstorming`) шоураннером
- Не адаптируется; локальная копия здесь — снимок для сравнения с upstream

## Workflow обновления (spec § 7.4)

1. Не обновляем автоматически.
2. Проверяем upstream drift периодически.
3. Если обновляем — bump SHA, re-validate все адаптации через pressure-testing.
4. Если НЕ обновляем — фиксируем reason здесь.

## Адаптации

Нет (`adapted_to: null` в METADATA.json).
