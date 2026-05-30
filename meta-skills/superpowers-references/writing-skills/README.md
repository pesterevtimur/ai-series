# writing-skills — pinned reference

**Origin:** obra/superpowers@f2cbfbef (== local v5.1.0)
**Pinned on:** 2026-05-30
**Used as:** база авторинга своих скиллов для адаптации

## Зачем pinned

База авторинга своих скиллов. Адаптируется в `.claude/skills/writing-narrative-skills/` с **обязательным pressure-testing** для discipline-зон в нарративном домене (минимум 3 RED-сценария + frontmatter `pressure_tested: status: yes`).

## Как используется

- Адаптируется в `.claude/skills/writing-narrative-skills/SKILL.md` через `lineage:` frontmatter
- Source-of-truth для skill-frontmatter structure + body sections

## Workflow обновления (spec § 7.4)

1. Не обновляем автоматически.
2. Проверяем upstream drift периодически.
3. Если обновляем — bump SHA, re-validate все адаптации через pressure-testing.
4. Если НЕ обновляем — фиксируем reason здесь.

## Адаптации

См. `.claude/skills/writing-narrative-skills/SKILL.md` — frontmatter `lineage.ref:` указывает на этот файл.
