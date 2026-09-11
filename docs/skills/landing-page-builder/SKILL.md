---
name: landing-page-builder
description: "Build premium landing pages for Jonathan. Use when asked to create a landing page, sales page, lead capture page, webinar registration page, or checkout pre-page. Triggers: 'build a landing page', 'create a sales page', 'design a page', 'דף נחיתה', 'דף מכירה'. This skill defines Jonathan's exact design standard - dark premium aesthetic with gradient backgrounds, single-word highlights, glow effects, and central container layout."
metadata:
  version: 3.0.0
---

# Landing Page Builder

Build premium landing pages following Jonathan's exact design standard.

---

## Workflow (Updated 2026-09-10 — GitHub pipeline, proven on rachel-pottery.co.il)

### הגישה: HTML בריפו, וורדפרס מושך לבד

**לא עושים:**
- ❌ הדבקת HTML ידנית בווידג'ט HTML באלמנטור (כל תיקון = הדבקה מחדש)
- ❌ JSON של עמוד שלם לאלמנטור
- ❌ Playwright לחיצה-לחיצה
- ❌ תמונות שמאוחסנות באתר אחר (נמחקות, והדף נשבר)

**כן עושים:**
- ✅ ה-HTML חי בריפו `orcatribeltd-glitch/orca-landing-pages` תחת `pages/<שם>/index.html`, תמונות ב-`pages/<שם>/images/`
- ✅ באתר מותקן התוסף `orca-landing-pages` (בריפו, `wordpress/`). בעמוד: ווידג'ט Shortcode עם `[landing_page name="<שם>"]`
- ✅ הטופס וכל מה שפועל (כפתור, קישור) — ווידג'טים אמיתיים של אלמנטור, בתבנית `templates/<שם>-form.json` שנבנית מ-`templates/build_<שם>_form.py`
- ✅ תיקון = עריכת הקובץ, commit, push. ה-webhook מרענן את האתר. אף אחד לא נוגע בוורדפרס

### תהליך העבודה

1. איסוף מידע: קופי, צבעים, מטרת הדף, לאן הלידים הולכים.
2. בניית HTML מלא (מסמך שלם מותר — התוסף מחלץ את הגוף ואת ה-CSS).
3. תצוגה מקדימה ליהונתן **לפני** push (Artifact או שרת מקומי). סבבי תיקון קורים כאן, לא באתר.
4. push לריפו. אימות מבחוץ: `curl` לעמוד החי ובדיקת סימון שנמצא **בתוך** `<body>`.
5. תבנית טופס: לבנות בסקריפט, לבדוק תחת CSS "עוין" (ראה סקיל elementor-landing-build), לשלוח ל-JSON.
6. הוראות ליהונתן — ראה "Output Format".

### הגדרות עמוד באלמנטור (פעם אחת לכל דף)

1. הגדרות עמוד → פריסה → **Elementor Canvas** (מוריד כותרת, תפריט ופוטר של האתר).
2. הקונטיינר של ה-Shortcode: רוחב מלא, ריווח פנימי 0.
3. ייבוא תבנית טופס **רק** מהמסך הישן: `wp-admin/edit.php?post_type=elementor_library&tabs_group=library` → "ייבוא תבניות". ספריית הענן החדשה זורקת "This source does not support import".
4. אחרי הוספת התבנית לעמוד: קונטיינר → מתקדם → מחלקות CSS חייב להכיל את המחלקה (הייבוא לפעמים מוחק אותה).

### שמות שדות בטופס (ID)

אסור: `date`, `time`, `page_url`, `user_agent`, `remote_ip`, `form_id`, `form_name`. אלמנטור שולח את אלה ב-webhook ודורס את מה שהמשתמש הקליד (תאריך מבוקש הפך לתאריך השליחה, 10/09/2026). תאריך מבוקש = `visit_date`.

### לידים לגיליון (Zapier)

Actions After Submit → Webhook → כתובת Catch Hook של זאפייר, עם **Advanced Data** דלוק (שולח גם את כתובת העמוד). מקור הליד לפי `utm_source` בקישור (ביו באינסטגרם ≠ קמפיין), ממופה לעמודה "מקור".

### זמן עדכון — נמדד, לא מובטח

| אתר | push → וורדפרס | push → גולש | למה |
|---|---|---|---|
| influence-club.co.il (אוהד) | 8 שניות | 8 שניות | תוסף SpeedyCache מתנקה בפרסום-מחדש שהתוסף שלנו מבצע |
| rachel-pottery.co.il (רחל) | מיד | 15–25 דקות | זיכרון עמודים בשרת (FastCloud). **החלטת יהונתן 11/09/2026: להשאיר ככה**, לא שווה את הטרחה |

איך מודדים נכון: סימון **גלוי** בדף (`<span data-build="…" hidden>` או `data-olp-ref` בעטיפה מגרסה 1.5.0), לא הערת HTML — תוספי זיכרון מוחקים הערות והמדידה משקרת. לפני שמאשימים את השרת: לקרוא את 300 הבייטים האחרונים של הדף, תוספי זיכרון חותמים שם. מעקף לבדיקה: `?v=1` בכתובת מציג את הגרסה הטרייה. פרטים: אובסידיאן "01 Projects/Landing Pages — GitHub to WordPress Pipeline".

---

## Before Starting

### Gather This Context (ask if not provided):

1. **Color Palette**
   - Reference/example for colors?
   - Build palette together?
   - Brand colors if relevant

2. **Copy & Content**
   - Main headline
   - Subheadline
   - Benefits/features
   - CTA text
   - Urgency elements

3. **Page Purpose**
   - Lead capture → needs Form Widget
   - Pre-checkout → redirect to payment
   - Registration → needs Form Widget
   - Information only → HTML only

4. **Form Requirements**
   - Fields needed (name, email, phone, etc.)
   - What happens after submit (redirect URL)
   - Save lead? (requires Elementor Form Widget)

---

## Design Standard (Non-Negotiable)

### Background
- **NEVER flat black** - always gradient with depth
- Dark base (#08080B or #0D0D0D)
- Radial gradients with accent colors at low opacity
- Optional: repeating-linear-gradient for subtle pattern

### Headlines
- **HIGHLIGHT ONE WORD ONLY** - critical
- Use color or gradient on the highlighted word
- Add text-shadow/glow for depth
- Rest in white

### Visual Effects
- Glow effects (box-shadow with accent color)
- Subtle borders (rgba white or accent)
- Premium, minimal aesthetic

### Typography
- **Heebo** for Hebrew (400, 700, 900)
- **Suez One** for special headlines
- Import from Google Fonts

### Layout
- Flexbox containers
- Centered content
- Generous padding (80px+ on desktop)
- Mobile: reduce padding, stack columns

---

## Output Format

### For WordPress/Elementor (ברירת המחדל, מגרסה 1.6.0 של התוסף):

**עמוד חדש = שלושה קבצים בריפו ו-push. אף אחד לא נוגע בוורדפרס:**
1. `pages/<שם>/index.html` — הדף (פונטים, CSS, תוכן). לאתר קיים: להעתיק את חלקי הפונטים וה-CSS מדף קיים באותו אתר.
2. `templates/<שם>.json` — תבנית **עמוד** של אלמנטור (`"type":"page"`, `page_settings` עם `elementor_canvas` ורקע), שמכילה קונטיינר עם ווידג'ט Shortcode `[landing_page name="<שם>"]`, וקונטיינר עם ווידג'ט Form אמיתי. נבנה מסקריפט `templates/build_<שם>.py`.
3. שורה ב-`pages.json` בשורש: `{"site":"<דומיין>","name":"<שם>","slug":"<כתובת>","title":"<כותרת>","template":"templates/<שם>.json"}`.

בכל push התוסף באתר יוצר עמוד חסר **כטיוטה** מהתבנית. עמוד קיים לא משתנה לעולם.

**מה נשאר ליהונתן, בכוונה:** לאשר את התצוגה המקדימה לפני push; לפתוח את הטיוטה ולקבוע Actions After Submit (לאן הלידים); ללחוץ פרסם. לאתר חדש: התקנת התוסף וסוד ל-webhook, פעם אחת.

**מלכודת שנצפתה (11/09/2026):** אלמנטור משמיט `_css_classes` מקונטיינר שנוצר מתבנית. לכן העיצוב של כרטיס הטופס לא סומך על המחלקה: ה-HTML של הדף מצמיד אותה בעצמו לקונטיינר שמכיל את הטופס (סקריפט קטן בסוף הדף, ראה `pages/mashpian-cancel/index.html`). לעשות כך בכל דף חדש.

**מה לא מוסרים:** קובץ JSON להורדה, קוד HTML להדבקה, הוראות ייבוא. הכל דרך הריפו.

### For Static Hosting (Vercel/Netlify):

HTML מלא עם טופס שמתחבר לשירות חיצוני (Make/Zapier webhook).

---

## Reference: Color Palette Template

```css
/* Influence Club style */
--bg-deep: #08080B;
--bg-section: #0A0A0D;
--accent-gold: #F2C230;
--accent-gold-light: #FFDE7A;
--accent-cyan: #38E1C6;
--accent-green: #2ED47A;
--text-primary: #FFFFFF;
--text-secondary: #A6A6B2;
--text-muted: #8E8E9A;
--border-subtle: rgba(255,255,255,0.1);
```

---

## Reference: Good vs Bad Headlines

**Good (ONE word highlighted):**
- "הצטרפו לפורטל הכשרת **יוצרי** התוכן"
- "מה אתה מקבל **בפורטל?**"

**Bad (too many words):**
- "הצטרפו **לפורטל הכשרת יוצרי התוכן**"
- "**מה אתה מקבל בפורטל?**"

---

## Checklist Before Delivery

- [ ] HTML מושלם עם כל העיצוב
- [ ] Fonts מחוברים (Google Fonts link)
- [ ] Mobile responsive (media queries או flex-direction)
- [ ] צבעים תואמים למפרט
- [ ] הוראות ברורות להוספה לאלמנטור
- [ ] מקום מסומן לטופס (אם צריך)

---

*Last updated: 2026-08-30*
*Based on research: modern designers use HTML directly, not JSON/Playwright*
