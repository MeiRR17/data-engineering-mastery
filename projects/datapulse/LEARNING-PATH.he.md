# DataPulse — פרויקט המשכים

DataPulse אינו רק דמו. זה פרויקט המתפתח לאורך שלבים, כשכל שלב מכניס קושי חדש ומדד איכות.

| שלב | מה מוסיפים | מדד מעבר |
|---|---|---|
| 01 | Window queries, indexes, explain | plan מנומק ושאילתות תקינות |
| 02 | Parser נקי, types, exceptions | 3 בדיקות edge cases שהלומד כתב |
| 03 | SQLite loader ו-Upsert | טעינה כפולה אינה משנה counts |
| 04 | Migration/RLS/Supabase | public read only, secret server only |
| 05 | Mart facts/dimensions | consistency לנתוני מקור |
| 06 | DAG + retries/backfill | controlled failure test |
| 07 | Contract + quarantine + lineage | broken input blocked |
| 08 | Dashboard + KPI semantics | UI עובד ומדד מוגדר ב-SQL |
| 09 | CI/CD + migrations + rollback | מעבר גרסה ושחזור מתועדים |
| 10 | Spark branch | measured local benchmark |
| 11 | Kafka exercise | duplicates/ordering/restart |
| 12 | SLO + incident | restore drill with evidence |
| 13 | Capstone | demo, ADR, tests, PR, technical writeup |

**אסור להעתיק קוד פתרון של Agent ללא הבנה.** הלומד צריך לכתוב מימוש, להריץ בדיקות, לעצב schema, לתעד החלטות ולהסביר למה בחר בכל רכיב.
