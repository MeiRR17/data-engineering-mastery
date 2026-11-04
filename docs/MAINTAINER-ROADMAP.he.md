# Maintainer Roadmap — תוכנית להשלמת המסלול הציבורי

[README](../README.md). **המסמכים החדשים אינם הוכחה שכל מעבדות השלבים הושלמו.** זהו Backlog להרחבה איכותית, עם תנאי קבלה מפורשים.

| Release | תוכן | Gate לפני תיוג |
|---|---|---|
| v0.2.x | README מלא, Visuals, Notebook tutorials 00–03, קישורי וידאו | 4 מחברות רצות, בדיקות יחידה, המחברות ו־DataPulse תקינות, קישורים תקינים |
| v0.3 | Notebook 04–07, SQL/Postgres exercises + automated grader, סביבות light/full | Expected outputs + adversarial tests |
| v0.4 | Supabase isolated project + migrations + security tests | Cloud smoke, RLS negative tests, no secrets in frontend |
| v0.5 | Analytics Engineering/dbt, warehouse/modeling | full data lineage + recomputable metrics |
| v0.6 | Orchestration, incremental/backfills, quality | replay and fault-injection passes |
| v0.7 | CI/CD, monitoring, recovery + costs | deploy, rollback, recovery evidence |
| v0.8 | Spark + Kafka labs light/full alternatives | benchmark + replay tests |
| v0.9 | Capstone grading, community review, multilingual materials | peer review and reproducible portfolio |
| v1.0 | Fully implemented end-to-end curriculum | external review + comprehensive CI + audited docs |

**פיתוח קהילתי:** פתחו Issue עבור תרגיל חדש, ציינו רמת קושי, מטרות, test oracle, dataset provenance, privacy, resource requirements ו־failure cases; לאחר מכן PR אחד עם fixture קטן, הבדיקות, פתרון למדריך בנפרד (לא בנתיב שהלומד אמור לראות) וקישור תיעוד. אין להעלות סרטונים או חומרים מוגנים שהועתקו. גם לגרסה ציבורית 'מושלמת' יש תחזוקה מתמדת, כי כלים ותיעוד משתנים.

### Foundation-labs increment

The Stage 01–03 offline SQL/Python/ETL reference graders and learner starters are under development on a feature branch; **v0.3 is not complete** until notebook 04–07, SQL/PostgreSQL coverage and release gates are implemented and independently reviewed.
