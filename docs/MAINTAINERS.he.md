# מדריך מפעיל המאגר הציבורי

1. פתח Repository חדש בשם `data-engineering-mastery` במשתמש/ארגון שבחרת, עם Visibility = Public. הימנע מ-README אוטומטי כשדוחפים קוד קיים, כדי למנוע קונפליקט.
2. בדוק במחשב מקומי: `python3 scripts/validate_repo.py`, `python3 -m unittest discover -s tests -v`, וגם בדיקות DataPulse.
3. דחוף branch `main` ושמור על branch protection / rulesets: PR review ו-CI checks. הפעל Settings → General → Template repository.
4. עבור Issues: הוסף labels: `learning`, `curriculum`, `bug`, `good first issue`, `security`, `documentation`; ודא שבקשות לימוד אישיות לא מכילות נתונים רגישים.
5. פרסם גרסת `v0.1.0` רק אחרי בדיקת CI. השאר Roadmap ותוכנית הרחבות פתוחים לדיון קהילתי.
6. כל לומד יוצר Repository אישי מתוך Template. אין צורך להעניק לכולם כתיבה ל-repository המרכזי.
7. מומלץ לנהל הפרדה: upstream = curriculum+fixtures; student repo = progress+assignments; optional hosted demos = resources paid/owned by learner.
8. לפני שדרוג גרסאות Supabase CLI/ SDK ו-GitHub MCP בדוק docs/changelog, בצע QA וכתוב breaking-change note.

**לא כל ה-14 השלבים ממומשים כפרויקט Production כרגע.** בגרסה זו יש סילבוס, רובריקה, Mentor, scripts, DataPulse Starter ובדיקות; המודולים המתקדמים כוללים משימות ותוצרי יעד שצריך לפתח עליהם הרחבות. הימנע מהצגת skeleton כהסמכה מלאה או תוכן שגמור בפרודקשן.

## פרסום ראשון במכונה של המפרסם

ראה את [מדריך הפרסום](PUBLISHING.he.md). ניתן להריץ `bash scripts/publish_to_github.sh` עם אישור מפורש ורק בחשבון בעל הריפו. אין במערכת הרשאה ליצור ריפו מרוחק ללא כלי מורשה מתאים.
