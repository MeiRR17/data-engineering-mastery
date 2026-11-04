# DataPulse — Deployment checklist, לא מדריך ל-Push עיוור

## שלב 1: ללא ענן

```bash
PYTHONPATH=projects/datapulse/src python3 -m unittest discover -s projects/datapulse/tests -v
PYTHONPATH=projects/datapulse/src python3 -m datapulse.ingest --fixture projects/datapulse/data/sample.geojson --dry-run
```

**המצב הנכון:** `loaded_rows: 0` — Dry Run. הדוגמה סינתטית.

## שלב 2: חשבון ופרויקט נפרדים

1. בחר ארגון Supabase בבעלות הלומד ובדוק עלות לפני יצירה; לעולם אל תשתמש במאגר של מישהו אחר כתרגול.
2. בחר Region, שמור סיסמאות רק במנהל סודות/סביבה מקומית מאובטחת.
3. בדוק `supabase --version` ו-`supabase db --help`. CLI v3: פקודות DB מכוונות **לוקאלית** אלא אם משתמשים במפורש ב-`--remote`.
4. מקומית מתוך `projects/datapulse`, הרץ `supabase init` אם לא קיים `supabase/config.toml`; `bash scripts/create_migration.sh` כדי ליצור מיגרציה באמצעות CLI (ולא שם זמן מומצא).
5. התנסה לוקאלית לפי `supabase start` / `supabase db reset` **רק בסביבת פיתוח**. אל תריץ reset מול פרויקט מרוחק.
6. בדוק migration ו-SQL/RLS. לפריסה לפרויקט *שהלומד אישר*, השתמש ב-CLI `db push --remote` לאחר בדיקה עם `--help` וקבלת confirmation, או SQL Editor כמסלול חלופי אחד בלבד.

## שלב 3: אבטחה לפני Public

- [ ] `public.raw_earthquakes`, `public.earthquakes`, `public.ingest_runs`: RLS פעיל.
- [ ] `anon` אינו יכול INSERT/UPDATE/DELETE אף טבלה.
- [ ] `anon` יכול לקרוא **רק** את טבלת/תצוגת הדשבורד המותרת.
- [ ] פונקציית ingest אינה ניתנת לביצוע עם publishable key / anon.
- [ ] `daily_stats` משתמשת ב-`security_invoker=true` ו-GRANT מוגבל.
- [ ] Secrets בשרת/CI בלבד; Publishable key בדפדפן אך ורק עם RLS נכון.
- [ ] DB advisors (security+performance) נבדקו; כל חריגה תועדה או תוקנה.

## שלב 4: טעינה ו-Idempotency

- `SUPABASE_URL` ו-`SUPABASE_SECRET_KEY` **רק בצד השרת/טרמינל מאובטח**.
- הרץ feed קטן, בדוק counts ב-SQL Editor ו-confirm source URL.
- הרץ שוב: אין שורות כפולות לאותו `event_id`; עדכונים חדשים מטופלים כראוי.
- סמלץ timeout, payload invalid, 429 ומפתח שגוי; אסור שיוצג success שקרי.
- השווה checksums, מספר rejected rows והסבר את השינויים.

## שלב 5: Dashboard

- הרץ דמו `python3 -m http.server 8080` מתוך `projects/datapulse/web`, ופתח `?demo=1`.
- לפריסה סטטית, השתמש בספק כגון Vercel, Root Directory=`projects/datapulse/web` כאשר מחברים את הריפו הראשי; הגדר רק משתני Publishable + URL ציבורי.
- אמת בפועל HTTP, loading/error/empty states, ולעולם אל תסתמך על screenshot לבדו.

## שלב 6: תזמון מבוקר

- דוגמת Workflow נמצאת ב-`examples/workflows/ingest.yml.example`. אל תפעיל אותה בלי החלטת הלומד.
- לאחר אישור, העתק לשורש `.github/workflows/datapulse-ingest.yml`, עדכן את פקודת ההרצה ואת `PYTHONPATH` כך שיתאימו לשורש המונוריפו.
- הגדר GitHub Repository Secrets בממשק GitHub ואת `DATAPULSE_ENABLED=true` רק לאחר בדיקה.
- בדוק Run, Logs, resource quotas, alerting, failure paths, review של הוצאות.

## ראיות נדרשות בסוף

- URL לשירות חי (אם אושר Deploy), מדדים שעודכנו בזמן ובדיקת endpoint.
- PR commit SHA, CI link, query checks ו-RLS negative tests.
- Runbook: היכן מחפשים לוגים, איך מריצים backfill, איך משחזרים, איך מכבים schedulers.
- תיעוד עלות משוערת, מגבלות API ותדירות טעינה.

**הפריסה עצמה לא מבוצעת בחבילת לימוד זו; אין טענה ל-Production readiness ללא בדיקות בענן.**
