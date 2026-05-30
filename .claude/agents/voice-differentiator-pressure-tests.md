---
id: voice-differentiator-pressure-tests
version: 1
status: draft
type: doc
references:
  - "docs/specs/2026-05-24-infrastructure-and-skills-design.md § 4.2 § 4.3 § 9.4.b § 9.4.c § 9.5"
  - "decisions/D-002-spec-corrections-and-golden-plan.md P-3 P-4 P-7 P-8 P-10 P-15"
  - ".claude/agents/voice-differentiator.md"
---

# A4 VOICE — Pressure tests (RED scenarios)

Документ калибровочных RED-сценариев для субагента `voice-differentiator`. Acceptance — Task 7 Phase 2 (Task tool invocation + validator проверка отчётов).

## Известное ограничение (D-002 P-15, расширительно)

`golden/anti-examples/dialogue-bleed/` пуст на момент Phase 2 ПП1 (по аналогии с P-15 для conflicts; ПП2 B.4.1 добавит dialogue-bleed bucket). Pressure-tests A4 опираются на dedicated RED-артефакты в `tests/regression/voice-bleed/` (uniform + narrator) и на regression-пары calibration + holdout.

## Voice_dissimilarity preflight — фактические значения (зафиксированы 2026-05-30)

Прогон `python -m tools.voice_dissimilarity <file> --threshold 0.65`:

| Файл | Спикеры | Парные cosine sim | Threshold 0.65 | Exit |
|---|---|---|---|---|
| `voice-bleed-uniform-01.md` | АННА / МАРКУС / ЛЕНА | все три пары ≈ 0.988 | флагнуто (≥ 0.65) | 1 |
| `voice-bleed-narrator-01.md` | АННА / КИРИЛЛ | ≈ 0.236 | НЕ флагнуто (< 0.65) | 0 |
| `pairs/calibration/voice-strong-cal.md` | ИРИНА / СТАС / БОРИС | все ниже 0.65 | НЕ флагнуто (различимы) | 0 |
| `pairs/calibration/voice-weak-cal.md` | ИРИНА / СТАС / БОРИС | все три пары = 1.000 | флагнуто | 1 |
| `pairs/holdout/voice-strong-holdout.md` | ДОКТОР ВАХ / ГРИГОРИЙ / ОЛЕСЯ | ≈ 0.11–0.15 | НЕ флагнуто (различимы) | 0 |
| `pairs/holdout/voice-weak-holdout.md` | ДОКТОР ВАХ / ГРИГОРИЙ / ОЛЕСЯ | все три пары = 1.000 | флагнуто | 1 |

**Вывод по preflight'у:** TF-IDF ловит uniform-voice (структурный bleed) на дефолтном пороге, но НЕ ловит narrator-bleed (контентный bleed, sim ≈ 0.236). Narrator-bleed — это явно A4 content-уровень задача, не preflight.

## RED-1: voice-bleed-uniform

**Файл:** `tests/regression/voice-bleed/voice-bleed-uniform-01.md`
**Voice_dissimilarity preflight:** sim ≈ 0.988 (exit 1) — preflight ОБЯЗАН flagнуть
**Expected A4 verdict:** `veto` severity:high
**Expected reasoning должен содержать:** распознавание uniform voice — все три говорящих (АННА safety / МАРКУС product / ЛЕНА comms) используют идентичные вводные («Послушайте, коллеги», «Понимаете», «Знаете», «Я думаю, нам нужно зафиксировать»), идентичную структуру предложений («X — это Y, и Y требует Z»), идентичные риторические шаги. Должно быть отмечено: содержательные роли в сцене несовместимы с uniform voice — researcher по безопасности vs product manager vs comms lead должны иметь дифференцированный регистр (terminology, hedging vs decisiveness vs corporate-soft). В weak-сцене все трое звучат как один автор, проговаривающий три позиции.
**Acceptance:** valid `flags` массив, минимум один `severity: high`, location указывает на конкретные повторяющиеся конструкции (вводные «Послушайте/Понимаете/Знаете» у всех трёх; финальный блок «фиксация — это процесс / Процесс требует протокола» идентичен дословно у всех трёх). `counter_test_attempted` не пустой даже при veto.

## RED-2: voice-bleed-narrator

**Файл:** `tests/regression/voice-bleed/voice-bleed-narrator-01.md`
**Voice_dissimilarity preflight:** sim ≈ 0.236 (exit 0) — preflight НЕ флагует, это ожидаемо (narrator-bleed контентный, не структурный сигнал)
**Expected A4 verdict:** `veto` severity:medium-high (либо `concern` severity:high — приемлемо при чётком reasoning)
**Expected reasoning должен содержать:** распознавание narrator-bleed pattern, не uniform similarity. Конкретно: (а) литературные конструкции в репликах («тонкая улыбка тронула мои губы», «глубокая печаль, которую я ощущаю»), которых не должно быть в устной речи; (б) perfect grammar в эмоциональном раскисе — 19-летний младший брат после ссоры с девушкой не говорит «Мне кажется, что в этой ситуации требуется значительно более выраженная эмоциональная реакция», он говорит «Аня, ну ёлки... ты че, вообще не реагируешь?»; (в) оценочные конструкции из narrator-комментария проникают в реплики («важно отметить, что», «следует понимать», «нельзя не признать»); (г) полное отсутствие маркеров живой речи (нет обрывов, «короче», «ну типа», заполнителей). Reasoning должен явно сформулировать: голос нарратора подменил голоса обоих говорящих, и это контентный bleed, не структурный.
**Acceptance:** A4 явно идентифицирует narrator-bleed pattern (минимум 2 из 4 признаков из обязательного прохода Step 4). location указывает на конкретные фразы. Если A4 даёт `concern` (не `veto`) — приемлемо, при условии что reasoning явно объясняет, почему severity не high (например, narrator-bleed не разрушает сцену так, как uniform-voice, потому что всё ещё видны разные позиции — просто оба персонажа звучат как один литературный автор).

## RED-3: weak-calibration-pair

**Файл:** `tests/regression/pairs/calibration/voice-weak-cal.md`
**Voice_dissimilarity preflight:** sim = 1.000 (exit 1) — preflight ОБЯЗАН flagнуть
**Expected A4 verdict:** `veto` severity:high
**Expected reasoning должен содержать:** распознавание uniform voice на тех же трёх ролях (researcher / engineer / manager), что и в strong-паре (`voice-strong-cal.md`). В weak-cal реплики ИРИНЫ / СТАСА / БОРИСА дословно идентичны (cosine = 1.000) — это маркер либо copy-paste авторства, либо радикального сглаживания. Сравнение с strong-паре: там ИРИНА использует nested clauses + hedging («если ограничиться тем, что мы реально видим», «при прочих равных»); СТАС — telegraphic technical («Quantization-артефакт не сходится», «Час работы. Делаем?»); БОРИС — corporate semi-questions («как бы это влияет», «давайте я попробую sync up»). Различительные маркеры в strong полностью отсутствуют в weak.
**Acceptance:** verdict идентичен structure с RED-1 — минимум один `severity: high`, location указывает на идентичность реплик (все три первые реплики начинаются с «Послушайте, коллеги, давайте обсудим аномалию probe-три и инцидент во вторник» — дословно). `counter_test_attempted` не пустой даже при veto.

## RED-4: weak-holdout-pair (не AI-domain)

**Файл:** `tests/regression/pairs/holdout/voice-weak-holdout.md`
**Voice_dissimilarity preflight:** sim = 1.000 (exit 1) — preflight ОБЯЗАН flagнуть
**Expected A4 verdict:** `veto` severity:high
**Expected reasoning должен содержать:** распознавание того же паттерна uniform-voice на материале другого домена (медицинская палата, не AI-lab) и на трёх несовместимых ролях (онколог в халате / 67-летний прораб / 32-летний редактор-дочь). Должно быть отмечено: ДОКТОР ВАХ в weak звучит идентично пациенту, что невозможно в реальности (онколог использует medical terminology, прораб — рабочий лексикон, дочь-редактор — литературные конструкции). Сравнение с strong-holdout: там ДОКТОР ВАХ говорит «узел в правой доле семь миллиметров, без признаков инвазии в плевру»; ГРИГОРИЙ — «Семь миллиметров — это сколько по рублю?»; ОЛЕСЯ — «возможно, было бы полезно, если бы вы могли показать на анатомической модели». Если A4 даёт `veto` на calibration weak, но `pass`/`concern-low` на holdout weak (или наоборот) — это признак domain-overfitting: критик прошит на AI-vocabulary (researcher/engineer/manager pattern) вместо паттерна uniform-voice. Escalate в D-NNN.
**Acceptance:** verdict идентичен RED-1/RED-2/RED-3 по structure. Работает на не-AI материале без потери качества.

## not_applicable verdict (P-3) test

**Файл:** `tests/regression/strawmen/strawman-alarmist-01.md` (создан в Task 1)
**Тип:** Story Bible эссе — не содержит формата `**ИМЯ:** реплика`, только вшитые цитаты внутри прозы («Все, кто говорит, что выравнивание — преувеличенная проблема...»).
**Expected A4 verdict:** `pass` + `not_applicable_reason: "артефакт не содержит диалога в формате **ИМЯ:** реплика"`
**Acceptance:** A4 ОБЯЗАН вернуть `pass + not_applicable_reason`. Содержательный `pass / concern / veto` без not_applicable_reason на не-сцене = провал P-3 разграничения. A4 не должен растягиваться на территорию A5 (philosophy) или A2 (character) — для этого артефакта первичен A5 (strawman pattern), и A5 даёт `veto`. Reasoning A4 короткий, но не пустой: «артефакт — Story Bible эссе, прозаический текст с вшитыми цитатами в narrative, не диалог; формат **ИМЯ:** реплика отсутствует; A4 не применим». `counter_test_attempted` заполнен (что искал — паттерн **ИМЯ:** реплика; почему именно это — это структурный триггер A4; почему не нашёл — артефакт это сплошная проза без речевых блоков).

## Cross-validation: A4 ↔ другие критики

- **A4 на `voice-bleed-uniform-01.md`** — A4 первичен (`veto`). Если A5 даёт `veto` за «корпоративная пустота как пропаганда» — приемлемо при разных ракурсах (A4: uniform voice; A5: содержательная пустота). Если A2 даёт `veto` за «все три персонажа — функции» — flag избыточности с A4 (один артефакт, два критика по сути одинаковому reasoning).
- **A4 на `voice-bleed-narrator-01.md`** — A4 первичен (`veto`/`concern`). A2 может дать `concern` за «оба персонажа звучат одинаково взрослыми и литературными» — это смежная зона, но допустимая разграничительность (A4: голос нарратора подменил персонажей; A2: эмоциональная сцена не показывает живую речь).
- **A4 на любом thesis.md / characters/<sheet>.md / world-rules.md** — `pass + not_applicable_reason`. Если A4 даёт содержательный verdict — провал P-3.

## P-10 acceptance

A4 даёт `pass` (без not_applicable_reason) на любом из RED-1..RED-4 = провал калибровки.
A4 даёт содержательный `pass / concern / veto` (без not_applicable_reason) на non-scene артефакте = провал P-3.

При первом таком провале — escalate в decision (D-NNN) с разбором: prompt не покрыл паттерн / model auto-switch на sonnet съел precision / пустота `golden/anti-examples/dialogue-bleed/` привела к слабой негативной калибровке / P-3 разграничение в prompt сформулировано слабо.

## Phase 2 Task 7 verification

Дополнительные проверки в Task 7:
- Holdout consistency: A4 на `voice-strong-holdout` = `pass`, A4 на `voice-weak-holdout` = `veto`. Если оба `pass` или оба `veto` — calibration broken.
- Domain consistency: A4 даёт `veto` одинакового structure на `voice-weak-cal` (AI-domain researcher/engineer/manager) и `voice-weak-holdout` (медицинская палата doctor/patient/family). Систематическое расхождение verdict'ов между доменами → domain-overfitting → escalate.
- not_applicable consistency: A4 на 3+ non-scene артефактах (`strawman-alarmist-01.md`, `moralizing-monolog-01.md` если он считается монологом, любой character sheet из Phase 4) ОБЯЗАН возвращать `pass + not_applicable_reason`. Если хотя бы один — содержательный verdict, P-3 broken.

## Known issue для ПП2

Если на smoke-test (Phase 4) A4 даст систематический pass на `voice-bleed-narrator-01.md` — фиксируется как ПП2 follow-up: запросить B.4.1 `anti-examples-batch-02` с dialogue-bleed bucket у Cowork, заполнить `golden/anti-examples/dialogue-bleed/` минимум 3 примерами (uniform-voice / narrator-bleed / register-flattening), и пересмотреть калибровочный блок A4 с включением anti-examples — особенно narrator-bleed примеров (House of Cards Underwood-voice anti, Sorkin uniform-walk-and-talk без дифференциации).

Если A4 даст содержательный verdict на `strawman-alarmist-01.md` (не not_applicable) — фиксируется как ПП2 follow-up: усилить P-3 формулировку в prompt, добавить явное правило «scene detection через regex **ИМЯ:** реплика — обязательный первый шаг».

## Связь со spec и D-002

- spec § 4.2 — структура файла субагента
- spec § 4.3 — структурированный YAML формат отчёта
- spec § 9.4.b — R-3 regression набор обязателен (calibration + holdout + voice-bleed dedicated по A4)
- spec § 9.4.c — overlap detection между критиками
- spec § 9.5 — критические failures (RED → veto required)
- D-002 P-3 — not_applicable_reason для критика вне его зоны
- D-002 P-4 — `golden_unavailable_reason: category-bootstrap` в ПП1
- D-002 P-7 — качественная валидация `counter_test_attempted` (в том числе для pass+not_applicable)
- D-002 P-8 — `effort: max` как механизм adaptive thinking budget
- D-002 P-10 — формулировка «RED обошёл скилл = провал»
- D-002 P-15 — пустота `golden/anti-examples/` как bootstrap-блокер (применяется к dialogue-bleed/ по аналогии)
