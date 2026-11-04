# Stage 04 — פריסת DataPulse ל-Supabase אחרי מעבדת PostgreSQL

[מעבדה מקומית](../labs/04-postgres/README.md) · [DataPulse](../projects/datapulse/README.md)

## לפני הענן

בצע תחילה את כל בדיקות PostgreSQL המקומיות עם Docker. אין בכך אימות ל-Supabase Auth או ל-Data API. השתמש רק בפרויקט Supabase חדש ומבודד שנבחר על ידי הלומד, לאחר בדיקת עלויות והסכמה מפורשת; לעולם לא על בסיס נתונים קיים.

## מסלול פריסה מבוקר — צעד אחר צעד

1. בדוק שה-CLI העדכני מותקן: supabase --version, supabase --help, supabase migration --help, supabase db --help. אם פקודה אינה קיימת פעל לפי התיעוד הרשמי במקום לנחש.
2. בספריית ניסוי חדשה, אם נדרש, אתחל באמצעות supabase init. צור קובץ Migration דרך supabase migration new datapulse_initial — לעולם לא באמצעות שם Timestamp מומצא.
3. העתק לתוך קובץ Migration שנוצר בפועל, לאחר בדיקת SQL, את מקור הסכמה: projects/datapulse/database/001_init.sql. אין צורך להעביר את bootstrap.sql של המעבדה — הוא יוצר Roles מדומים ומיועד אך ורק ל-Docker.
4. בדוק איזו סביבת Supabase מקושרת, מי הבעלים ומה צפוי להיחשף. ודא שזה פרויקט ניסוי חדש, ואז קבל אישור לפני העלאת Migration או יצירת חיובים.
5. ב-2026 החשיפה של טבלאות חדשות ב-public ל-Data API כבר אינה אוטומטית בכל הפרויקטים. אמת גם את הגדרות חשיפת ה-API, בנוסף ל-GRANT ול-RLS. חשוף רק קריאה לנתונים מעובדים ו-Views שאושרו.
6. שמור מפתח Publishable בצד לקוח רק תחת הרשאות מוגבלות. מפתח Secret או Service Role נשמר ב-Backend/CI Secrets בלבד — לא בדפדפן, לא בריפו ולא בצילום מסך.
7. בדיקות חיוביות בענן: קריאת earthquakes ו-daily_stats ב-REST דרך מפתח Publishable, טעינה מאובטחת של נתונים סינתטיים דרך Backend, ושאילתות UTC נכונות.
8. בדיקות שליליות בענן: anon אינו מסוגל לקרוא raw_earthquakes ו-ingest_runs, להוסיף/למחוק earthquakes או להפעיל את ingest_earthquake_batch.
9. בדוק replay של אותו Batch, עדכון מקור מאוחר, כשל של נתון פגום ו-Atomic Rollback. הרץ Advisors לאבטחה ולביצועים, תעד ממצאים ותקן כשלים.
10. תעד PR, Commit SHA, קובץ Migration, תוצאות בדיקות ועלות. סמן deployed רק לאחר Smoke Test מרחוק — לא בגלל מעבר Docker בלבד.

## אבחון תקלות

| תקלה | בדוק |
|---|---|
| 401/403 | מפתח, Session, GRANT, RLS, הגדרות Data API |
| שאילתה מחזירה אפס שורות | Policy, נתונים, פילטרים ו-Timezone |
| View דולף | security_invoker, grants ו-owner |
| Raw/Curated אינם מסונכרנים | פונקציית טעינה, Transaction, Source Updated |
| Migration נכשלת | היסטוריית Migrations ו-Schema Drift |
| עלויות לא צפויות | ריצות, אחסון, Compute, בקשות ותזמון |

## מבחן סיום

Stage 04 הוא locally-tested לאחר מעבר PostgreSQL CI; integration-tested/deployed דורש ראיות Supabase אמיתיות עם בדיקות RLS, Data API, אבטחה, טרנזקציות וניטור.

מקורות: [Supabase migrations](https://supabase.com/docs/guides/deployment/database-migrations), [Supabase RLS](https://supabase.com/docs/guides/database/postgres/row-level-security), [Views](https://supabase.com/docs/guides/database/views), [Securing Data API](https://supabase.com/docs/guides/api/securing-your-api.md).
