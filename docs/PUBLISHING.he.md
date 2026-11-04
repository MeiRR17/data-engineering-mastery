# איך מפרסמים את הריפו לציבור — צעד אחר צעד

> **סטטוס:** בשלב זה ארכיון מקומי מוכן לבדיקה; לא נוצר מאגר GitHub חדש ולא פורסמה גרסה בענן. הפרסום הוא פעולה שבעל החשבון מאשר במפורש.

## מסלול א': סקריפט מאומת, פרסום ראשוני בלבד

ב-Mac עם Homebrew:

```bash
brew install gh git
# היכנס לחשבון GitHub שלך דרך מסך אימות, ללא העברת סיסמה לצ'אט
gh auth login
```

חלץ את ZIP ופתח Terminal מתוך תיקיית `data-engineering-mastery`:

```bash
python3 scripts/validate_repo.py
python3 -m unittest discover -s tests -v
PYTHONPATH=projects/datapulse/src python3 -m unittest discover -s projects/datapulse/tests -v
bash scripts/publish_to_github.sh
```

הסקריפט בודק הרשאת GitHub, מציג את כל הקבצים שנכנסים ל-Git, **דורש אישור מפורש** לפני יצירת מאגר ציבורי, ואינו כופה Push על מאגר קיים.

## מסלול ב': GitHub Web + Git ידני

1. פתח https://github.com/new והיכנס לחשבון שאמור להיות בעל הריפו (המפרסם, לא הלומד).
2. Repository name: `data-engineering-mastery` ; Visibility: **Public**. אל תבחר 'Add README' או `.gitignore` כי הם כבר כלולים.
3. בתיקייה המקומית:

```bash
git init -b main
git add .
git commit -m "feat: publish open Data Engineering Mastery roadmap"
git remote add origin https://github.com/YOUR_GITHUB_USERNAME/data-engineering-mastery.git
git push -u origin main
```

4. בדוק ש-`README.md` מופיע וש-GitHub Actions של `Learning repository checks` עובר.
5. Settings → General → **Template repository**. ב-Settings → Branches / Rulesets הגדר הגנה על `main` ו-required CI, לפי זמינות בחשבון.
6. צור Release בשם `v0.1.0` רק לאחר שהבדיקות עברו.
7. שלח לחבר קישור לריפו הציבורי. הוא יבחר **Use this template** וייצור ריפו בבעלותו, ציבורי או פרטי לפי העדפתו.

## חניכת החבר לאחר יצירת העותק

1. הורד/שכפל את הריפו לחשבון שלו ופתח ב-VS Code.
2. הרץ `python3 scripts/system_profile.py --tier-only` — אופציונלי. אם רוצה, `--write-local` שומר פרופיל **מקומי**.
3. הרץ `python3 scripts/roadmap.py init --alias learner` ו-`python3 scripts/roadmap.py next`.
4. חבר GitHub ל-ChatGPT לצורך קריאת הקוד, ו-GitHub MCP ל-Agent IDE כשצריך פעולות כתיבה. המדריך ב-[GITHUB-MCP-SETUP](GITHUB-MCP-SETUP.he.md).
5. העתק את [פרומפט המנטור הראשי](../prompts/MASTER-AGENT.he.md) לתוך שיחה, והתחל Stage 00.
6. בסוף כל שלב: Branch → PR → CI → Evidence → מעבר שער הערכה. התקדמות הלומד לא משנה את הריפו המקורי.

## תחזוקה ציבורית

- שחרר גרסאות סמנטיות; תעד breaking changes ב-CHANGELOG.
- אסוף משוב דרך Issues ו-Discussions. אל תפרסם מבחני ידע אישיים או נתוני חומרה פרטיים.
- קבל PRs שמשפרים תרגילים, בדיקות, מקורות רשמיים ותמיכה ב-OS נוספים.
- תמוך בהרחבות נוספות אחרי Stage 13; אין להציג תוצאה מתרגיל כלשהו כהסמכה מקצועית רשמית.
