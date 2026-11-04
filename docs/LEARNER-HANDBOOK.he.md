# מדריך הלומד — מבוגר הנדסת תוכנה ועד מערכת נתונים שפועלת

חזרה ל־[README](../README.md). זהו ה־Runbook ללומד ולמנטור. המטרה היא **ללמוד כיצד לעשות**, לא למסור את כל העבודה ל־AI. התואר מאפשר דילוג מושכל על יסודות שנבדקו, לא דילוג אוטומטי.

## יום 0 — הקמה ללא ענן

1. צרו חשבון GitHub משלכם, הגדירו 2FA ושמרו על אישורי הכניסה במנהל סודות. הורידו Git, Python 3.11+ ו־VS Code. זכרו את המקום שאליו שמרתם את הפרויקט.
2. העתיקו את הריפו דרך Template, או חלצו ZIP. פתחו אותו ב־VS Code ובדקו שתיקיית השורש מכילה `scripts/` ו־`curriculum/`.
3. ב־Terminal הריצו `python3 --version`, `git --version`, ואז `python3 scripts/system_profile.py`. לא מריצים `sudo` או התקנות שרירותיות.
4. הריצו `python3 scripts/validate_repo.py` ו־`python3 -m unittest discover -s tests -v`.
5. בצעו `python3 scripts/roadmap.py init --alias learner` (פעם אחת) ואז `status`, `next`, `start 00`.
6. פתחו את [מחברת 00](../notebooks/00_data_journey.ipynb) ב־JupyterLab או ב־VS Code עם Jupyter extension והפעילו **Run All**; קראו קודם את מטרת כל תא. אם אין Jupyter, עברו על התאים ב־GitHub והריצו את קוד Python בקובץ מקומי — הלמידה אינה חסומה.
7. פתחו Issue ראשון בריפו הפרטי או הציבורי שלכם. כותרת: `Stage 00 — environment + initial assessment`; גוף: מטרות, פקודות, תוצאה, בעיה, ראיות מסוננות. לאחר מכן Branch `learn/00-foundation`.
8. התחילו שיחת ChatGPT חדשה והדביקו את הפקודה בסוף [MASTER-AGENT](../prompts/MASTER-AGENT.he.md). בלי חיבור GitHub, ציינו את שם המודול והעתיקו רק קבצים רלוונטיים.

## מבנה תיקיות — מה עושים בכל מקום?

| מקום | תפקיד הלומד | ניתן לערוך? |
|---|---|---|
| `README.md` | מפה והתחלה מהירה | כן, דרך PR |
| `curriculum/modules/XX.md` | דרישות השלב, שאלות ו־Exit Gate | אל תדלגו על הדרישות |
| `curriculum/cs-bridges/` | עקרונות מדעי המחשב שקשורים למשימה | קריאה + ניסוי |
| `notebooks/` | ניסויים קצרים עם וידאו, קוד וגרפים | ב־PR שלכם; אל תשמרו סודות |
| `labs/` | אתגרי מעבדה ומקרי כשל | כן |
| `projects/datapulse/` | המערכת המתפתחת העיקרית | כן, בהדרגה |
| `scripts/` | אבחון, תכנון מפגש, מעקב התקדמות | שינויים רק עם בדיקות |
| `learner/progress.json` | הערות וראיות פרטיות | **מקומי בלבד** |
| `docs/` | runbooks, פריסה, תרחישי כשל | כן, בתרומות |
| `.github/` | CI, PR ו־Issue templates | עיינו לפני שינוי |

## אבחון והתאמה אישית

המנטור מעריך 0–4 בחמישה ממדים (הבנת מושגים, ביצוע עצמאי, בדיקות, תכנון, תפעול), ובודק תחילה: SQL (`JOIN`, `GROUP BY`, `NULL`), Python (dict/list, exceptions, modules, tests), Linux (process, files, environment variables), networking (HTTP, DNS, retry), DB (keys, indexes, ACID), Git/PR ו־complexity. כל טעות משמשת לבחירת שיעור; לא לתווית קבועה.

חוזה למידה לכל מפגש: `Stage`, בעיה מעשית, מה תסביר לבד, אורך המפגש, מנגנון בדיקה, Side Quest אופציונלי. המנטור משאיר ללומד לפחות ניסיון עצמאי אחד לפני הצגת פתרון; אם נתקעים, נותן רמז בשלוש רמות (כיוון, טכניקה, דוגמה חלקית). עיקרון: **הפחתת תמיכה בהדרגה**.

### בחירת סביבת ריצה

- `light`: SQLite / DuckDB / notebooks קטנים; להכיר Spark/Kafka דרך סימולציה וצפייה, לא להסתיר את המגבלה.
- `moderate`: PostgreSQL ב־Docker *אם זמין*, בדיקות לוקאליות, דאטה קטן והגבלת זיכרון; אפשר לבחור Supabase בענן אחרי בדיקת עלות.
- `full`: ניסויי Spark/Kafka מקומיים בנפרד, עם נפחי נתונים שמצדיקים זאת; גם כאן קודם baseline של SQL/DuckDB.

אין חובת GPU. אם יש הגבלות פרטיות/מחשב ארגוני, משתמשים ב־GitHub Codespaces או שירות ענן רק לאחר בדיקת המדיניות והעלות, בלי להעתיק מידע ארגוני.

## מחזור העבודה בכל שלב — 11 פעולות

1. **הגדר בעיה:** מי צורך את הנתונים? אילו freshness/accuracy/cost/security constraints קיימים?
2. **שרטט Data Flow:** מקור, קליטה, סכימה, עיבוד, אחסון, צרכן; סמן מה ידוע ומה הנחה.
3. **כתוב Definition of Done:** תוצר, מדד אחד לפחות, שגיאות קלט, חזרה על הרצה, תיעוד ותהליך בדיקה.
4. **התחל מהפתרון הפשוט:** SQL / Python / SQLite / Postgres; אל תבחר Spark/Kafka בלי צורך מדיד.
5. **צור Issue ו־Branch:** `learn/XX-topic`, Commit קטן, PR שמציג תוצאה שניתן לשחזר.
6. **נסה בכוחות עצמך:** 20–30 דקות לפני פתרון מלא; אם אין התקדמות, בקש רמז ממוקד או הסבר מושגי.
7. **בצע ניסוי מדעי המחשב:** למשל index לעומת sequential scan, memory מול disk, at-least-once מול dedup.
8. **בדוק הצלחות וכשלים:** unit, integration, schema, duplicate, null, retry, malformed, access, load; תעד *מה באמת רץ*.
9. **אמת מקור ו־Lineage:** מזהה אירוע, זמן, source URL או קובץ, hash / batch ID; אל תערבב נתוני דוגמה עם אמת.
10. **ערוך Review:** מה מחיר הפתרון, למה האלטרנטיבות לא נבחרו, איך עושים rollback, האם המפתח הסודי מוגן?
11. **מבחן מעבר:** הסבר בעל פה/בכתב, שינוי לא צפוי, מציאת באג, ביקורת עמית/מנטור; רק אז תעד את השלב כ־self-reported והמשך.

## למידה במפגש בודד של 75 דקות

| זמן | שלב | למה |
|---|---|---|
| 0–8 | חידה תפעולית: פלט שגוי/קוד איטי | סקרנות ויכולת לאבחן |
| 8–23 | ניסיון עצמאי + סימון הנחות | לא להיות תלוי ב־AI |
| 23–35 | סרטון/תיעוד ממוקד + CS bridge | ללמוד מושג בהקשר |
| 35–55 | מימוש + בדיקות | למידה באמצעות בנייה |
| 55–65 | Failure injection קטן ומבוקר | לא להניח ש־happy path מספיק |
| 65–75 | הסבר עצמי + משימת מחר | שימור ידע וידע העברה |

אם עייפים או יש רק 25 דקות: בחרו בעיה אחת, ניסוי אחד ושאלת הבנה אחת. אל תדחסו שלוש טכנולוגיות חדשות למפגש.

## תרחישי אמת שחייבים לשלוט בהם

| תרחיש | למה זה קורה | הוכחה מעשית |
|---|---|---|
| API מחזיר 429/503 | Rate limit / outage | backoff, limit retries, no silent data loss |
| API מחזיר אותן רשומות | At-least-once ingest | unique keys ו־idempotent upsert |
| JSON חסר שדה | Schema drift | quarantine ותיעוד חוזה |
| timestamp עם timezone | UTC/local ambiguity | datetime מודע לאזור זמן |
| NULL, duplicates, outliers | איכות מקור | tests + metrics + rejection policy |
| מחיקת קובץ raw | חוסר reproducibility | checksum / raw retention policy |
| טעינה חלקית ונפילה | Partial transaction | retry / checkpoint / consistency check |
| SQL איטי | Full scan, skew, no index | EXPLAIN + baseline + benchmark |
| טבלת Fact מנופחת | join cardinality / bad grain | query assertions + grain docs |
| DAG רץ פעמיים | retries / overlap | dedup + concurrency policy |
| Backfill כבד | historical recomputation | partition scope + cost cap |
| Kafka אירועים לא בסדר | async partitions | event time + dedup + late events |
| Spark איטי | shuffle/spill/data skew | measurements, repartitioning |
| Dashboard חושף נתונים | RLS / view / API policy | anon tests + negative tests |
| secret הועלה ל־Git | leakage | revoke/rotate + clean history safely |
| ענן עולה כסף | unbounded jobs/storage | budget alerts, limits, cleanup plan |
| טעות migration | schema changes | migrations versioned + backup + rollback strategy |
| מחיקה/שחזור | recovery | backup/restore smoke test בסביבת dev |
| QA עובר אבל תוצאה שגויה | wrong business definition | compare expected counts & samples |
| חוסר ב־observability | errors without signals | freshness/volume/error SLI + alert |

[ספר פתרון התקלות](TROUBLESHOOTING.he.md) כולל שיטות אבחון פרטניות.

## כיצד לממש פריסה בפועל (אחרי שלבים 03–09)

**Phase A — local:** ריצה עם fixture, בדיקות, הסבר סכימה ו־`--dry-run`. **Phase B — isolated dev:** פרויקט Supabase חדש של הלומד בלבד, בדיקת עלות באזור/ארגון נבחרים. **Phase C — migrations:** בדיקה במחשב או בענן מבודד; שמירת SQL בספריית migrations וב־PR. **Phase D — secure app:** שרת ETL שומר secrets; דפדפן מקבל רק publishable key ו־RLS/GRANT שהוגדרו במפורש. **Phase E — scheduled delivery:** runner נפרד, rate limits, health checks, no production secrets in PR CI. **Phase F — ops:** checks, dashboard, error reporting, documented rollback, budget alarm, backup/restore rehearsal. ראו [Deployment checklist](../projects/datapulse/DEPLOYMENT-CHECKLIST.he.md).

**אין לבצע `supabase db reset --remote` במערכת עם מידע חשוב**. לפני פקודות CLI בודקים `supabase --version` ו־`supabase <command> --help`, כי חתימות משתנות. מדריך עדכני: https://supabase.com/docs/guides/local-development/cli-workflows

## כשמסיימים שלב

פותחים PR עם: מטרה, סכימה, source + sample, פקודות הרצה, דוגמאות פלט, בדיקות כולל negatives, אבטחה, עלויות, rollback, מה קרה כששברנו את המערכת, ושתי תשובות עצמיות. מבקשים Reviewer. לאחר review מעדכנים `roadmap.py complete` כ**דיווח עצמי**. כדי להציג סטטוס מסונן לחיבור GitHub: `python3 scripts/roadmap.py export-summary`, בודקים את הקובץ ו**רק אז** מחליטים אם לבצע Commit לריפו האישי.

## למידה מתמשכת ותיק עבודות

אחרי Stage 13 בחרו התמחות אחת: Analytics (dbt/semantic), Streaming (Kafka/Flink), Platform (Iceberg/Delta), AI Data (RAG/embeddings), או Architecture/SRE. לכל הרחבה צריך benchmark, עלות, security review, incident drill ו־case study. התקדמות במסלול אינה תחליף לניסיון צוותי או חובת מעסיק.
