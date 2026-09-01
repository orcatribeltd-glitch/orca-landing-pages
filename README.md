# Orca Landing Pages

דפי נחיתה מסונכרנים עם WordPress דרך GitHub.

## מבנה

```
pages/
├── mashpian/
│   └── index.html
├── influence-club/
│   └── index.html
└── [שם-דף-חדש]/
    └── index.html
```

## התקנה (פעם אחת)

### 1. WordPress - הוספת Shortcode

העתק את הקובץ `wordpress/landing-page-shortcode.php` לתיקייה:
```
wp-content/mu-plugins/landing-page-shortcode.php
```

(אם התיקייה `mu-plugins` לא קיימת - צור אותה)

### 2. GitHub Secrets

ב-Settings → Secrets → Actions, הוסף:

| Secret | ערך |
|--------|-----|
| `FTP_SERVER` | כתובת השרת מ-Fast Cloud |
| `FTP_USERNAME` | שם משתמש FTP |
| `FTP_PASSWORD` | סיסמת FTP |

### 3. יצירת תיקייה בשרת

צור תיקייה ריקה:
```
wp-content/landing-pages/
```

## שימוש

### הוספת דף נחיתה חדש

1. צור תיקייה חדשה תחת `pages/`
2. הוסף קובץ `index.html` עם ה-HTML
3. Push ל-main

### שימוש באלמנטור

1. צור דף חדש
2. הוסף Shortcode widget
3. כתוב: `[landing_page name="שם-התיקייה"]`
4. מתחתיו הוסף Form widget (לשמירת לידים)

## דוגמה

```
[landing_page name="mashpian"]
```

יטען את הקובץ: `wp-content/landing-pages/mashpian/index.html`
