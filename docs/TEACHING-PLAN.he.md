# תוכנית הוראה והתקדמות — Data Engineering Mastery

[14 שלבים](ROADMAP.he.md) · [מטריצת שליטה](MASTERY-MATRIX.he.md) · [פרויקט מתמשך](PROJECT-LADDER.he.md) · [מעבדות](../labs) · [בחינה עצמאית](FINAL-ASSESSMENT.he.md)

המסלול מיועד בעיקר לבוגר/ת תואר בהנדסת תוכנה, אך אינו מניח שליטה מוקדמת ב־SQL מתקדם, תפעול מסדי נתונים, רשתות, DevOps או Streaming. שיטת הלמידה: **הסבר → ניבוי → ניסוי → כשל מכוון → תיקון → מבחן מעבר חדש**.

## מתכונת שבועית מומלצת

מתחילים באבחון לפני שקובעים קצב. דוגמה ל־10–12 שעות שבועיות: 2–3 שעות תיאוריה ומדעי המחשב, 5–6 שעות בניית קוד ומעבדות, 1–2 שעות בדיקות ו־Incident Debugging, שעה Code Review והסבר עצמאי. 70% מהזמן להנדסת נתונים, 20% לגשרים רוחביים במדעי המחשב, 10% לחזרה ו־Transfer.

הזמנים להלן משוערים בלבד; **מתקדמים לפי שער היכולת, לא לפי שבועות שחלפו**.

| Phase | Stages | Suggested focus | Acceptance artifact |
|---|---|---|---|
| A — Engineering foundations | 00–03 | Git/OS, SQL, Python, idempotent local ETL | מקור→שכבה מעובדת, בדיקות ושחזור |
| B — Data product core | 04–05 | PostgreSQL, permissions, warehouse, dbt | Fact/Dim עם SCD2 ו־RLS |
| C — Reliable data product | 06–09 | DAG, Quality, API, CI/CD, rollback | Pipeline שהוגדר, נבדק ושוחזר |
| D — Scale and streaming | 10–11 | Spark, shuffle, skew, Kafka, offsets | תוצאות זהות Light/Full, Replay |
| E — Operations | 12 | SLO, backup/restore, alerting, cost, RBAC | דו"ח Incident עם ראיות |
| F — Independent delivery | 13 | Integrated capstone, ADR, interview, exam | PR ו־Demo, מבחן חדש וביקורת |

## זרימת שיעור סטנדרטי

1. **Define:** מי הצרכן? מה Grain של מקור הנתונים ומהו תרחיש הכשל?
2. **Predict:** הלומד מתאר את התוצאה או את Error Code לפני הרצת הקוד.
3. **Investigate:** תיעוד רשמי, Notebook, CS bridge והדגמה קצרה.
4. **Implement:** לומד מממש `starter.py` או `starter.sql` ב־Branch אישי.
5. **Break:** כשל אמיתי או מוזרק — Null, כפילות, Crash, Replay, Permission Denied, Staleness.
6. **Repair:** תיקון ממוקד ובדיקת Regression.
7. **Defend:** הסבר Tradeoffs ללא AI, ובחינת Transfer חדשה שאינה שאלה מתוך התרגיל המקורי.
8. **Record:** PR + Commit + Command + Test Output מסונן + ADR/Reflection + הערכת מנטור.

## משימות מעשיות חובה לפי נושא

- **SQL:** Query שלא מכפילה Facts ב־Join, Window Functions ו־`EXPLAIN` ב־Postgres.
- **Python:** Parser עמיד לטיפוסים שגויים, timestamps, nulls ו־schema drift.
- **ETL:** at-least-once input עם sink idempotent ו־Transaction Atomicity.
- **PostgreSQL:** Negative RLS/GRANT tests, migration, query performance.
- **Warehouse/dbt:** fact grain, SCD2, UTC day mart, data tests and lineage.
- **Orchestration:** DAG, Retry Budget, bounded backfill, failure checkpoint.
- **Quality:** contract version, completeness, freshness, quarantine without raw private payload.
- **Serving:** GET allowlist, correct average denominator, stale/error states, unauthorized-write denial.
- **Delivery:** deterministic build, hash verification, artifact provenance caveats, promotion and verified rollback.
- **Spark:** local JVM plan, repartition, Shuffle, Window, skew, comparison with simpler engines.
- **Kafka:** actual broker run for full mode, consumer group offsets, replay and post-commit acknowledgement loss.
- **Operations:** restore-to-new, threat model, cost assumptions, alert SLO definitions and incident runbook.
- **Capstone:** architecture review, secure end-to-end demo, three ADRs, unseen exam and reviewer signoff.

## אפשרויות ציוד

**Light:** Python 3.11+ ו־SQLite — כולם יכולים להתחיל. **Moderate:** Docker/PostgreSQL ו־dbt מקומי. **Full:** Java, PySpark, Kafka single-broker, זיכרון פנוי ומחשב מתאים. אין צורך ב־GPU. אם אין ציוד Full, אין מסמנים שליטה ב־Kafka/Spark כאילו המעבדה רצה — מתעדים `deferred` ומבצעים בהמשך בסביבה מאושרת.

לענן ולתשתיות מרוחקות נדרש אישור בעל החשבון, תקציב וגבולות אבטחה. לא מחייבים לומד לשלם עבור שירות ענן כדי להתחיל ללמוד, אבל אין דרך להוכיח פריסה/אבטחה בענן ללא סביבת בדיקה אמיתית.

## מי מקבל אישור סיום?

אחרי שכל 14 השלבים הושלמו בקוד עצמאי, כל שערי המעבר תועדו, מבחן הגמר עבר עם תרחיש חדש, קוד הגמר נבדק, אירוע כשל ושחזור הוצגו ובוחן מוסמך אישר. האישור יהיה **פנימי ללמידה** ולא הסמכה חיצונית. כלי ה־CI בודקים קוד ודוגמאות, לא אישיות או ניסיון תעסוקתי.
