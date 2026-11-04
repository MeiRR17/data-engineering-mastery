# Assessment, evidence, and honesty

## Five dimensions, each 0–4

| Dimension | 0 | 1 | 2 | 3 | 4 |
|---|---|---|---|---|---|
| Concepts | cannot explain | definitions | explains example | explains tradeoffs | transfers to unfamiliar scenario |
| Independent implementation | none | follows copy/paste | completes with hints | implements independently | decomposes and reviews novel tasks |
| Testing/debugging | no tests | smoke-only | normal cases | edge/failure tests | reproducible incident analysis |
| Architecture | no model | basic diagram | justified structure | compares alternatives | defends constraints and cost |
| Operations/security | unsafe/unknown | checklist awareness | restricted dev setup | measured logging+RLS+recovery | rehearsed incident, bounded risk |

**Passing a module:** deliverable exists, unit/integration tests appropriate to the stage pass (or limitations documented), at least 3/4 in Concepts and Independent Implementation, no known critical security failure, and a reviewer confirms evidence. Project completer scripts only log self-reported milestones; no automated career label.

**Review protocol:** show original learner-authored code or pair-programming transcript, a novel what-if variation, two short questions answered without AI, observed test output with source/commit, and an ADR or reflection. External reviewer optional for basic modules, strongly recommended for capstone.

**Scoring statement template:** 'Stage X: Self-reported complete; verification status = not independently verified; passed unit tests locally on date; cloud deployment not checked.'

**Good evidence:** a real PR URL, reproducible test command, redacted log, benchmarking note, schema diagram, screenshot of *non-sensitive* outputs, linked postmortem. A private repo can use local paths/commit SHA; don't publish confidential data to prove competence.

**Portfolio progression:** Stages 00–02: foundations evidence; 03–05: junior-level project exposure; 06–09: end-to-end delivery evidence; 10–12: advanced systems exposure; 13: portfolio-ready proof. **None of these labels alone establishes actual employment level.**
