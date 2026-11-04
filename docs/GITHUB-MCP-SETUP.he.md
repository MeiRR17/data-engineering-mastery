# GitHub, ChatGPT ו-GitHub MCP — חיבור בטוח מההתחלה

**שני סוגי חיבור שונים:**

1. **GitHub בתוך ChatGPT** — Settings → Plugins → GitHub (ייתכן שהכינוי בממשק שונה). מאשרים את החשבון ואת הריפו. לפי OpenAI, חיבור זה מיועד לחיפוש/קריאה וניתוח קוד, *לא* להבטחת כתיבה או Push מתוך שיחה רגילה.
2. **GitHub MCP ל-Agent IDE** — VS Code + GitHub Copilot Agent או MCP host תומך. מתקינים את GitHub MCP Server הרשמי, מאשרים OAuth והרשאות לכתיבה *רק אם צריך*. בודקים אילו tools קיימים בפועל. זה מנגנון שונה מחיבור ChatGPT לקריאה. אפשר גם להשתמש ב-Codex או Agent אחר בעל הרשאות כתיבה מתאימות.

## 1 — מאגר ציבורי ותבנית

המפרסם יוצר ריפו ציבורי `data-engineering-mastery` ומפעיל Settings → General → **Template repository**. כל לומד יבחר **Use this template → Create a new repository**. מומלץ ללומד חדש להתחיל בריפו *פרטי* ולהפוך לציבורי רק כשמתאים לו; התבנית המקורית נשארת ציבורית.

## 2 — חשבון GitHub של הלומד

- פתח GitHub, בחר חשבון, הפעל 2FA, התקן Git/VS Code.
- צור עותק Template בחשבון **שלך**, לא בחשבון המורה. Clone ל-IDE שלך.
- אל תוסיף PAT או סיסמאות ל-README/PR/ChatGPT. התחבר ב-OAuth / GitHub CLI או דרך מנהל סודות מקומי.
- עבוד עם `learn/XX-feature`, פר-שלב Issue ו-PR; אל תפתח commit ישירות ל-main כשיש PR workflow.

## 3 — ChatGPT

- פתח ChatGPT → Settings → Plugins → GitHub, Connect/Authorize. בחר רק את הריפו שלך.
- בשיחה חדשה העתק את `prompts/MASTER-AGENT.he.md` או בקש לקרוא אותו מהריפו המחובר, ציין את full repo name, ובקש לאבחן את Stage 00.
- ודא שהמנטור מצליח לקרוא קובץ לדוגמה מה-repo ולהציג מקור מדויק. אם הוא לא מצליח, בדוק הרשאות והמתן עד להופעת ריפו חדש.
- **אל תניח שהחיבור יכול לדחוף קוד**; תכונה זו תלויה במוצר ובכלי הסוכן הזמינים בפועל.

## 4 — GitHub MCP בתוך VS Code

- לפי התיעוד העדכני של GitHub, אפשר לפתוח Extensions ולחפש `@mcp github`, להתקין את GitHub MCP Server הרשמי ולאשר התקנה.
- פתח Command Palette → `MCP: List Servers`, וודא שהשרת מופיע.
- השלם login OAuth בחלון המאושר; הימנע מהקלדת token אל צ'אט.
- פתח את תיקיית הריפו ב-VS Code ובחר Agent mode אם זמין, וודא שה-agent רואה את GitHub tools המורשים.
- בדיקת יכולת: קריאה של Issue קיים. לבדיקה עם הרשאות כתיבה, פתח **Issue ניסיוני או branch** רק לאחר שהלומד אישר פעולה זו.

תיעוד רשמי: https://docs.github.com/en/copilot/how-tos/provide-context/use-mcp-in-your-ide/set-up-the-github-mcp-server

שרת רשמי: https://github.com/github/github-mcp-server

ChatGPT: https://help.openai.com/en/articles/11145903-connecting-github-to-chatgpt

## 5 — פריסה ועלויות

- Supabase חיבור נפרד, בפרויקט/ארגון שהלומד בחר, ורק לאחר בדיקת העלות וההרשאות.
- לפני כל CLI שמגיע לענן: `supabase --version`, `supabase db --help`, פקודת `--remote` מפורשת ב-CLI v3; אין Deploy אוטומטי ללא review.
- בדיקות CI ב-PR לא מקבלות secrets. Workflows עם credentials/deploy מתאפשרים רק אחרי אישור מפורש של הבעלים.

## תקלה נפוצה: ריפו לא מופיע בצ'אט

בדוק חשבון GitHub נכון, הרשאת App לריפו המסוים, אישור Org owner אם דרוש, והבדלי זמינות בין Chat ו-Work. GitHub search index עשוי להתעדכן באיחור. אין לשלוח פרטי התחברות למנטור כפתרון.
