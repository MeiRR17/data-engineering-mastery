# Roadmap 2026–2028 — מההתחלה ועד מעבר לתפקיד

המסלול הוא **Competency-Based** ולא רק צבירת שעות. קהל היעד הוא בוגרי הנדסת תוכנה ובעלי רקע קרוב, אך מי שחסר יסוד יכול להיעזר בקישורים למדעי המחשב ובתוכנית גישור.

| Stage | מומחיות | רמת יעד | פרויקט / ראיה |
|---|---|---|---|
| 00 | Onboarding + אבחון מדעי המחשב והחומרה | בסיס | סביבת עבודה + אבחון |
| 01 | SQL/PostgreSQL | בסיס | חלונות, JOINs, EXPLAIN |
| 02 | Python Data | בסיס | Parser, typing, tests |
| 03 | Batch ETL | ליבה | מקור → SQLite (idempotent) |
| 04 | PostgreSQL + Supabase Sandbox כתוספת | ליבה | migration + RLS + ingest; ענן ייבדק רק בסביבה מאושרת |
| 05 | Modeling/Warehouse | ליבה | Star Schema + marts |
| 06 | Orchestration | ליבה | DAG עם Backfill |
| 07 | Contracts/Quality | ליבה | Quality gate + lineage |
| 08 | Analytics/Data APIs | ליבה | Dashboard ב-Production-style |
| 09 | Release Engineering / CI/CD | מתקדם | חבילה שחזורית, אימות, Release ו־Rollback מקומיים |
| 10 | Spark/Big Data | מתקדם | עיבוד PySpark מקומי, Shuffle, Skew; Benchmark מבוזר בהרחבה |
| 11 | Kafka/Streaming | מתקדם | duplicate, restart, late event |
| 12 | Reliability/Governance | מתקדם | incident drill, backup/restore |
| 13 | Capstone/Career | תיק עבודות | demo, ADR, PR review, mock interview |

## הערכת שלבי יסודות באמצעות קוד

[Foundations Labs לשלבים 01–03](FOUNDATIONS-LABS.he.md) מאפשרים לבדוק קוד של הלומד באמצעות grader. כל Stage דורש גם הסבר עצמאי ופתרון Transfer חדש; הצלחה בגריידר אינה הסמכה מקצועית.

## שלוש שכבות בכל שלב

1. **Engineering:** בניית מערכת נתונים מדידה ושחזורית עם בדיקות.
2. **Computer Science:** `curriculum/cs-bridges/` — מדוע הפתרון עובד, לא רק כיצד להעתיק קוד.
3. **Side Quest:** הסתעפות מעניינת ומוגבלת בזמן מתוך `curriculum/side-quests.json`.

## מסלול רוחב מקביל (Foundations Passport)

בכל Stage מצטרף ניסוי קטן ממדעי המחשב או מתחום טכנולוגי משיק. 12 משימות חקר מכסות את 14 השלבים; המטרה היא יכולת להתמודד עם בעיות לא מוכרות, לא השלמת רשימת טכנולוגיות. [מפת הרוחב וכללי הביטחון](BREADTH-FOUNDATIONS.he.md) · `python3 scripts/breadth_quest.py recommend --stage 03`.

## הערכת זמן גמישה

- 5–7 שעות בשבוע: כ-15–24+ חודשים עד Capstone, מותנה ברקע ונגישות ציוד/ענן.
- 10–15 שעות בשבוע: כ-9–15+ חודשים לשערי היסוד והליבה ולפרויקט גמר ראשוני.
- 20+ שעות בשבוע: ניתן להתקדם מהר יותר, אך רק אם מבחני ההעברה והתוצרים אכן מוכיחים הבנה.

המספרים אינם הסמכה או הבטחה לתעסוקה. החל מ-Stage 03 התיק העיקרי הוא DataPulse שמתפתח מ-ETL מקומי עד deployment ותפעול; Stage 10–12 מוסיפים מערכות גדולות רק כשיש הצדקה.

## מסלולי הרחבה אחרי Stage 13 (מומחיות רציפה)

- **Data Platform:** Iceberg/Delta, schema registry, governance, platform self-service, chargeback/showback.
- **Analytics Engineering:** dbt, semantic layers, metrics, slowly changing dimensions, warehouse tuning.
- **Streaming Specialist:** Flink, event-time windows, watermarks, stateful processing, exactly-once caveats.
- **AI Data Infrastructure:** RAG ingestion, chunk quality, embeddings, lineage/evaluation, vector retrieval and PII governance.
- **Architecture/Staff:** multi-region tradeoffs, ADRs, mentoring, SLIs/SLOs, incident reviews and cost optimization.

לכל התמחות מתקדמת יש להגדיר Capstone נוסף עם baseline, cost model, tests, security review וכתיבת פוסט טכני.
