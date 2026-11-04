# Troubleshooting — ספר אבחון תקלות ללומד

[חזרה ל־README](../README.md). **כלל בסיס:** אל תעתיק פקודה הרסנית מ־AI בלי לקרוא אותה. שמור על מקור המידע ועל סודות. התקדמות טובה כוללת *למה נכשל*, לא רק *מה תקנתי*.

## קודם כל, פרוטוקול אבחון

1. רשום **Expected vs Actual** ובאיזה שלב אירע הכשל (Extract / Validate / Transform / Load / Serve).
2. העתק את הודעת השגיאה **ללא טוקנים, כתובות פרטיות, שמות משתמש או dump של נתונים רגישים**.
3. בצע Reproduction מינימלי על fixture קטן; אל תרוץ שוב ושוב על Production.
4. בדוק גרסאות, Config, סכימה, רשת, הרשאות ולוגים. בצע שינוי יחיד בכל ניסיון.
5. תן לסוכן AI לתאר שלוש השערות, ובחן אותן. בסיום הוסף בדיקה שמונעת רגרסיה.

## תקלות התחלה

| סימפטום | אבחון בטוח | פתרון ראשון |
|---|---|---|
| `python3: command not found` | `python --version` או `py -3 --version` | התקנת Python דרך מקור רשמי; Windows לרוב `py -3` |
| `ModuleNotFoundError` | נתח מסלול import ו־venv | פתח root נכון, הפעל venv והתקן רק dependencies מוסכמות |
| Git לא מזהה Branch | `git status`, `git branch --show-current` | ודא clone ותיקיית root; אל תמחק `.git` |
| `roadmap.py init` נכשל | `learner/progress.json` קיים | שמור אותו: השתמש ב־status, לא ב־init חוזר |
| `No module named datapulse` | `pwd` והגדרת `PYTHONPATH` | השתמש בפקודה המדויקת ב־README |
| Test נכשל אחרי Windows newline | בדוק encoding/line endings | השתמש ב־UTF-8 ונרמל את ה־fixture |
| Jupyter לא מציג וידאו | בדוק חסימת iframe / GitHub preview | פתח קישור YouTube רגיל; המשך בתאים גם בלי וידאו |
| Docker לא עולה | `docker info` ו־RAM פנוי | פתח Docker Desktop/engine; למסלול Light עבור ל־SQLite |
| `port already allocated` | תהליך אחר מאזין בפורט | בחר פורט אחר; אל תעצור שירות שאינו שלך |

## תקלות Data Engineering

| סימפטום | בדיקה | תיקון/לקח |
|---|---|---|
| 429 API | status, Retry-After | backoff מוגבל + caching; לא לולאה אינסופית |
| Timeout | latency, connect vs read timeout | bounded retries, pagination, circuit breaking אם צריך |
| Schema drift | diff בין payloads | validation + quarantine + versioned contract |
| חסרים אירועים | watermark, timestamps, pagination | overlapping window, late arrivals, dedup |
| כפילויות | unique business key, run ID | upsert עם idempotent semantics |
| Rows עוברות אף ששגויות | assert business invariants | tests ב־ingest וגם ב־curated |
| Spurious NULL | inspect parsing and locale | explicit timezone/type handling |
| SQL לא תואם | inspect join grain and grouping | one-to-many diagnostic query |
| SQL איטי | EXPLAIN (ANALYZE) על dev ומדידת baseline | index/partition רק לאחר אבחון |
| שמירה חלקית | run logs, transaction state | transaction + checkpoint + retry safety |
| Pipeline נתקע ב־DAG | task dependency, worker logs | retries מוגבלים + alert + backfill |
| Spark OOM | partitions, shuffle spill, RAM | sample+measure; reduce input/concurrency |
| Kafka replays | offsets, partitions, consumer group | dedup, checkpoint, event semantics |
| אירוע מגיע מאוחר | event time vs processing time | allowed lateness + correction strategy |
| Data staleness | source/ingest/processed timestamps | freshness SLI and alert |

## Supabase / GitHub / ענן

| סימפטום | שורש אפשרי | מה בודקים |
|---|---|---|
| REST table לא נגישה | GRANT / Data API exposure / RLS | expose schema, GRANT מתאים ו־RLS |
| `permission denied` | role/policy/column access | test anon/authenticated, לא לבטל RLS כפתרון |
| View חושפת נתונים | view definer behavior | `security_invoker = true` כשנתמך ו־GRANT מוגבל |
| Secret מופיע בדפדפן | env prefix או קובץ frontend | revoke + rotate immediately; להעביר לשרת |
| `supabase` command unknown | CLI version mismatch | `supabase --help`, `supabase db --help`, docs רשמיים |
| Missing migrations | CLI local/remote out of sync | migration list + review; לא `db reset --remote` |
| PR CI נכשל | dependency/OS/path/version | reproduce local, inspect exact failing step |
| PR לא נוצר | missing GitHub tool permissions | בדוק capabilities; manual CLI fallback |
| Cloud bill rises | jobs/egress/storage | stop authorized job, budget monitoring, cost review |
| Secrets leaked in repo | tracked `.env` or key | revoke/rotate, scan history, investigate access |

## דיווח תקלה יעיל ב־Issue

**What I expected:** …  
**What happened:** …  
**Smallest reproduce:** …  
**Versions/system category:** light/moderate/full (לא מפרט מלא)  
**What I tried:** …  
**What might break if we change it:** …  
**Redacted logs and test command:** …

תהליך האבחון עצמו הוא חלק ממבחן המעבר: אם פתרת בגלל copy/paste, תן לעצמך הזדמנות להסביר מה היה שגוי ולכתוב regression test.
