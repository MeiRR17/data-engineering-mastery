# Interactive notebooks — ארבע מחברות מונחות

[חזרה ל־README](../README.md) · [מחברות וסרטונים](../docs/VIDEO-LEARNING.he.md)

1. פתחו `00_data_journey.ipynb` ב־VS Code עם הרחבת Jupyter או ב־JupyterLab. 
2. הפעילו את התאים לפי הסדר (`Run All`) ושנו ערך אחד כדי לבדוק השערה. כל הנתונים סינתטיים ונשמרים בזיכרון.
3. פתחו את הסרטון דרך הקישור או באמצעות `YouTubeVideo` אם Jupyter מאפשר. GitHub מציג Preview סטטי ולכן לא מבטיח ניגון וידאו.
4. הגישו תשובות ל־Checks ו־Side Quest בריפו האישי. Notebook צופה בלבד אינו מוכיח mastery.

מחברות 00–03: למידה בהקשר Data Flow, SQL, idempotent ETL וניטור. הסביבה לבדיקה: Python 3.11+, IPython/Matplotlib בשביל תצוגה; SQL ו־ETL מסתמכים על SQLite המובנה. התקנה מומלצת בתוך venv ייעודי: `python3 -m pip install jupyterlab ipykernel matplotlib nbformat nbclient`. לגרסת Production נדרש גם Cloud/CI/Docker לפי השלבים המאוחרים.

לשחזור סביבת המחברות: הפעילו venv והתקינו `python3 -m pip install -r notebooks/requirements.txt` **מתיקיית השורש**. גרסאות אלה נבדקו בסביבת Python 3.13; אם המחשב אינו תומך בגרסאות, עיינו במגבלות המודולים ובחרו גרסאות תואמות מתועדות במקום לכפות התקנה.
