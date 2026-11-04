# פרויקט בהמשכים — לא 14 תוכניות שננטשות

[חזרה ל־README](../README.md) · [DataPulse](../projects/datapulse/README.md)

**עיקרון:** אותו מוצר DataPulse עובר גלגולים עם כל שלב. דוגמאות ראשוניות הן fixture, לא נתוני אמת. מותר לבחור תחום אחר (תחבורה, מזג אוויר, Open Data) ובלבד שהבדיקות/סכמות/מדדי איכות זהים בעקרון.

| Stage | גרסת הפרויקט | תוצר מוסבר | בדיקה שצריכה להיכשל כששוברים את הקוד |
|---|---|---|---|
| 00 | Project Zero | סביבת עבודה, Git, notebook | script חסר / גרסת Python לא מתאימה |
| 01 | SQL Lab | טבלת אירועים ושאילתות | duplicate key, bad join |
| 02 | Parser | מפענח נתונים עם type validation | missing magnitude / invalid timestamps |
| 03 | Local ETL | ingest ב־SQLite/Local | two runs → duplicate count changes |
| 04 | Cloud DB | Supabase ב־dev | anon can insert / RLS bypass |
| 05 | Analytics Mart | fact_event + dim_time + aggregates | incorrect grain or double counting |
| 06 | Scheduler | DAG עם retry/backfill | one failed task remains unreported |
| 07 | Quality | anomaly/quarantine/contract | malformed batch enters curated data |
| 08 | Serving | dashboard, read-only API | unauthorized access / stale display |
| 09 | Delivery | CI, deploy, rollback, docs | broken deploy with green CI |
| 10 | Big Data Lab | PySpark benchmark | wrong aggregation or data skew |
| 11 | Stream Lab | Kafka simulation/events | duplicate/out-of-order not handled |
| 12 | Operations | alert + incident playbook | missing freshness alert / restore fails |
| 13 | Portfolio | project showcase + ADR | new engineer cannot reproduce system |

## בכל גרסה שלוש משימות

**Core:** צעד השלב. **CS Bridge:** הסבר תיאורטי עם ניסוי שאפשר לשחזר. **Side Quest:** הרחבה אופציונלית של 10–25 דקות. אל תגדירו את Side Quest כחובה למעבר; הוא מיועד לעורר סקרנות.

## מתי אפשר להתחיל לפרסם פרויקט לתיק עבודות?

אחרי Stage 03 אפשר להציג ETL מקומי ולציין במפורש שזהו Demo. Stage 04–09 מוכיחים יכולת End-to-End בענן אם הפריסה נבדקה בפועל. Stage 10–12 מוכיחים היכרות עם Scale, Streaming ו־Ops. Stage 13 מציג case study מלא, אבל אינו שקול אוטומטית לניסיון עבודה בתפקיד Senior.
