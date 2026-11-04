# Release Readiness — מצב הפרויקט והשלמה מבוקרת

[README](../README.md) · [Maintainer roadmap](MAINTAINER-ROADMAP.he.md)

## מה זמין בגרסה v0.2.0?

- README בעברית ובאנגלית, מסלול של 14 שלבים, מחברות Jupyter, דיאגרמות, מנטור AI ותרגילי Stage 00/01.
- DataPulse starter עם Python ETL, PostgreSQL/Supabase migration, fixture סינתטי, בדיקות וממשק Dashboard לדוגמה.
- כלים מקומיים לאבחון חומרה ולמעקב התקדמות, ללא שליחת מידע אישי אוטומטית.
- הקוד, התיעוד והדוגמאות פורסמו בריפו הציבורי. אימות מקומי של 29 בדיקות עבר; אין בכך הוכחה לפריסת ענן.

**אין לטעון שהמסלול כולו ממומש או שהושגה הסמכה מקצועית.** סימון השלמת Stage במעקב הוא דיווח עצמי, לא מבחן יכולת עצמאי. סטטוס GitHub Actions נבדק ישירות בלשונית Actions.

## מפת החלטות לבעל הריפו

1. GitHub → Settings → General → **Template repository**: לסמן; ללא הסימון אין Use this template.
2. להוסיף About, description ו־topics רלוונטיים (data-engineering, python, sql, supabase, jupyter, roadmap).
3. לבדוק שה־CI של `.github/workflows/ci.yml` הושלם בהצלחה; כאשר הוא בתור אין להציג אותו כירוק.
4. להגדיר Branch protection ו־PR review בהתאם לתוכנית ולהרשאות GitHub.
5. להימנע מפרסום `.env`, service_role, PAT, פלט חומרה או `learner/progress.json`.
6. לבקש ממשתתף חיצוני לבצע את Stage 00 ללא עזרה, ולתעד קשיי התקנה ב־Issue.

## בדיקות אימות

```bash
python3 scripts/validate_repo.py
python3 -m unittest discover -s tests -v
PYTHONPATH=projects/datapulse/src python3 -m unittest discover -s projects/datapulse/tests -v
PYTHONPATH=projects/datapulse/src python3 -m datapulse.ingest --fixture projects/datapulse/data/sample.geojson --dry-run
```

אם הריפו כבר קיים ורוצים לעדכן אותו מקובצי מקור מקומיים, מריצים:
`bash scripts/update_existing_repo_via_pr.sh MeiRR17/data-engineering-mastery`.
הסקריפט מציע Pull Request בלבד, אחרי בדיקות ואישור מפורש; הוא אינו ממזג או משנה main ישירות.

## סוגיות פתוחות ומבחני קבלה

- [#1 — מוכנות לפרסום](https://github.com/MeiRR17/data-engineering-mastery/issues/1)
- [#2 — v0.3: מעבדות וגריידר אדפטיבי](https://github.com/MeiRR17/data-engineering-mastery/issues/2)
- [#3 — v0.4: DataPulse + Supabase עם פריסה מאומתת](https://github.com/MeiRR17/data-engineering-mastery/issues/3)
- [#4 — v0.5: Warehouse, Orchestration, איכות נתונים](https://github.com/MeiRR17/data-engineering-mastery/issues/4)
- [#5 — v0.6: Cloud, CI/CD, אבטחה ו־Recovery](https://github.com/MeiRR17/data-engineering-mastery/issues/5)
- [#6 — v0.7–0.9: Spark, Kafka ועיבוד מבוזר](https://github.com/MeiRR17/data-engineering-mastery/issues/6)
- [#7 — v1.0: פרויקט גמר וביקורת קבלה עצמאית](https://github.com/MeiRR17/data-engineering-mastery/issues/7)

כל Release צריך בדיקות, מימוש אמיתי, תיעוד, מבחן כשל וראיית משתמש. שינוי גרסה אינו יכול להסתמך על הוספת טקסט בלבד.
