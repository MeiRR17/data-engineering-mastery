# מחברות Jupyter וסרטוני YouTube — לומדים, מיישמים וממשיכים

[חזרה ל־README](../README.md). **הפרויקט אינו מארח, מוריד או מפיץ מחדש סרטונים.** הווידאו מופיע באמצעות הפניית צפייה ל־YouTube המקורי. יצירות חיצוניות הן של בעליהן ובכפוף לתנאים שלהם.

## מה קורה בפועל?

1. פתחו Notebook ב־VS Code + הרחבת Jupyter, או ב־JupyterLab (`python3 -m pip install jupyterlab ipykernel` בתוך venv נפרד, לאחר בדיקת המשאבים).
2. פתחו את המחברת והפעילו את תאי ההסבר לפי הסדר. בתא הווידאו, `IPython.display.YouTubeVideo` יכול להציג נגן אם סביבת Jupyter, החיבור לרשת והגדרות הדפדפן מאפשרים זאת.
3. **חשוב:** GitHub מציג תצוגת Notebook סטטית, ולא מובטח שיציג iframe או נגן YouTube. כל Notebook מכיל גם קישור צפייה ישיר שנפתח ב־YouTube. אין להניח שהווידאו יופעל בתוך GitHub עצמו.
4. לאחר קטע צפייה *קצר* יש תרגיל לבצע, טעות לגלות ושאלת העברה. צפייה לא מסמנת שלב כהושלם.
5. אם אין YouTube (רשת מוגבלת/הנגשה), משתמשים בתיעוד הרשמי ובתרגיל שמופיע במחברת; תוצאות הלימוד אינן תלויות בסרטון.

## מחברות מוכנות להפעלה

| Notebook | סוג | קישור צפייה / חומר חיצוני | מושג CS שמתחבר |
|---|---|---|---|
| [00: מסע הנתון](../notebooks/00_data_journey.ipynb) | Intro + data flow | [DataTalks.Club — What is orchestration?](https://www.youtube.com/watch?v=-JLnp-iLins) | data provenance, types |
| [01: בלש SQL](../notebooks/01_sql_detective.ipynb) | Relational reasoning | [Harvard CS50 SQL](https://www.youtube.com/watch?v=WXk7yDqsKxs) | joins, B-Trees, normalization |
| [02: מעבדת כשל ETL](../notebooks/02_etl_failure_lab.ipynb) | Replay + dedup | [Zoomcamp dlt workshop](https://www.youtube.com/watch?v=5eMytPBgmVs) | invariants, idempotency |
| [03: ניטור Pipeline](../notebooks/03_pipeline_observatory.ipynb) | Reliability / charts | [Zoomcamp orchestration](https://www.youtube.com/watch?v=1pu_C_oOAMA) | SLIs, failure detection |

### סרטון SQL לדוגמה

[![צפייה בקורס Harvard CS50 SQL ב־YouTube](https://img.youtube.com/vi/WXk7yDqsKxs/hqdefault.jpg)](https://www.youtube.com/watch?v=WXk7yDqsKxs)

הקישור הוא לקורס מלא שמסביר יסודות SQL באופן שיטתי. לא חייבים לצפות בכל הקורס לפני שניגשים ל־Notebook 01; אפשר לצפות רק בנושאים שבהם אבחון המנטור זיהה פער.

## קורסי וידאו משלימים לפי נושא

| תחום | מקור מבוקר | הוראת שימוש |
|---|---|---|
| SQL/DB fundamentals | https://cs50.harvard.edu/sql/ | תרגול SQL לצד Problem Sets |
| CLI, Git, shell, debugging | https://missing.csail.mit.edu/ | למי שמתקשה ב־Stage 00 |
| Docker + Terraform | https://github.com/DataTalksClub/data-engineering-zoomcamp/tree/main/01-docker-terraform | לפני ענן |
| Orchestration | https://github.com/DataTalksClub/data-engineering-zoomcamp/tree/main/02-workflow-orchestration | לפני Stage 06 |
| BigQuery/warehouse | https://github.com/DataTalksClub/data-engineering-zoomcamp/tree/main/03-data-warehouse | Stage 05 |
| dbt | https://github.com/DataTalksClub/data-engineering-zoomcamp/tree/main/04-analytics-engineering | Stage 05–07 |
| Spark | https://github.com/DataTalksClub/data-engineering-zoomcamp/tree/main/06-batch | Stage 10 |
| Kafka/streaming | https://github.com/DataTalksClub/data-engineering-zoomcamp/tree/main/07-streaming | Stage 11 |

הרשימה מפנה לתיעוד המקורי שמכיל קישורי וידאו עדכניים לכל שיעור, ולא מקבעת מזהי וידאו שלא אומתו. כך גם אם קורס משנה סרטונים, המקור הרשמי נשאר מקום האמת.

## איך המנטור משתמש בווידאו בצורה אפקטיבית?

המנטור בוחר **מקטע רלוונטי אחד**, מגדיר לפני הצפייה שתי שאלות, ומשלים אחרי הצפייה שלושה דברים: קוד קצר שעובד; Counterexample שהלומד מתקן; והסבר עצמאי של *למה זה עובד*. מי שכבר עובר את מבחן האבחון יכול לדלג על הצפייה ולבצע אתגר מתקדם. אין לתת לווידאו להחליף עבודה אמיתית עם נתונים.

### בהמשך

אפשר להוסיף מחברות ייעודיות לכל 14 המודולים ולשלב Quick Quizzes ובדיקות אוטומטיות של ה־Notebook. **בגרסה זו יש 4 מחברות ממומשות, לא 14**, והסרטונים אינם מאוחסנים בשרת הפרויקט.
