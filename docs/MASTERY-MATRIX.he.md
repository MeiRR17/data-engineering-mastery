# מטריצת שליטה — איך יודעים שמבינים Data Engineering?

[חזרה ל־README](../README.md) · [רובריקה](ASSESSMENT.md)

לכל נושא מדרגים **הוכחה** ולא תחושת ביטחון: 0 לא מכיר; 1 יכול להסביר; 2 מממש בעזרת הנחיה; 3 מממש ומאבחן לבד; 4 מצדיק tradeoffs ומעביר ידע לבעיה חדשה. **רמה 4 במסלול אינה Senior job title**.

| נושא ליבה | בדיקת יכולת 3–4 | Stage |
|---|---|---|
| SQL: joins/windows/nulls | להסביר cardinality ולכתוב שאילתות לא מוכנות | 01 |
| Transactions/indexes | EXPLAIN וניתוח lock/ACID/phantom | 01, 04 |
| Python types/tests | parser עמיד לקלט משתנה | 02 |
| APIs/rate limits | backoff, timeout, pagination | 02–03 |
| ETL + incremental | upsert, watermark, replay, late data | 03–04 |
| Warehouse/modeling | grain, fact/dim, SCD, cost | 05 |
| Batch Orchestration | DAG, retries, restart, backfill | 06 |
| Quality + lineage | completeness, uniqueness, freshness, source | 07 |
| Serving & privacy | SQL accuracy, cache, RLS, access tests | 08 |
| Cloud + IaC | separate environments, secrets, rollback | 09 |
| Spark | shuffles, skew, memory, benchmark vs local | 10 |
| Kafka / streaming | ordering, at-least-once, windows, schema | 11 |
| Ops/security | SLO/SLI, alert, restore, incident | 12 |
| Production capstone | reproducible demo, risk/cost/architecture | 13 |

### חובה להסביר לפני שמתקדמים

1. מדוע בחרת Pipeline *ולא* קריאה ישירה ל־API בכל Dashboard?
2. מה קורה כשה־Source חוזר על אותן רשומות או משנה את הסכימה?
3. מהו ה־grain בכל Fact, וכיצד בדקת שאין fan-out?
4. כיצד מונעים נתוני Demo ב־Production?
5. איך יודעים מה סיבת כשל בשתיים לפנות בוקר?
6. מה האיכות המינימלית שבה מותר לפרסם תוצאה?
7. מה עלות חישוב חוזר / Backfill ומה האלטרנטיבה?
8. מה נחשף לאנונימי ומדוע RLS לבדו אינו מספיק בלי הרשאות GRANT נכונות?
9. אם Spark מהיר פחות מ־DuckDB עבור 10MB, האם נכשלנו?
10. איך מוכיחים שחזור ולא רק שיש קובץ גיבוי?

### סטטוס מקצועי אמין לאחר פרויקט

- `implemented`: בוצע קוד או תכנון, לא בהכרח עברו בדיקות.
- `locally-tested`: הבדיקות הרלוונטיות עברו על נתוני דוגמה.
- `integration-tested`: שירותים ומסדי נתונים מחוברים נבדקו.
- `deployed`: סביבת ענן עובדת ונבדקה מרחוק.
- `operationally-validated`: מדדי SLO, אירועים, שחזור, עלות ואבטחה נבדקו.

אסור לעבור מדיווח `locally-tested` ל־`deployed` בלי בדיקה אמיתית בענן. ספריית הכלים המקומית שומרת **דיווח עצמי**, ולא מוכיחה כשירות רשמית.
