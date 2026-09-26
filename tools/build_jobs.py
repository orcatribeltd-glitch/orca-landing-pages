#!/usr/bin/env python3
"""Build the orcatribe job-openings page (/גיוס-עובדים/) in the brand language.

The role text comes from the approved screening-bot copy ("בוט סינון מועמדים - מסמך אישור v2.docx", approved by
Jonathan 18/09/2026): the role summary, the day-to-day list, the skills and the car / full-time requirements.
No salary on the page (Jonathan, 26/09/2026). All wording gender-neutral.

Usage: tools/build_jobs.py <out folder under pages/>   (orca-jobs is the live one)
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from build_legal import CSS as LEGAL_CSS, LINKS, LOGO  # noqa: E402

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'pages')
APPLY_MAIL = 'orcatribeceo@gmail.com'   # the recruitment inbox: a CV that lands here starts the WhatsApp screening bot
APPLY_SUBJECT = 'קורות חיים - משרת יוצרי תוכן'
EDIT_MAIL = 'orcatribeltd@gmail.com'   # NOT the recruitment inbox: a CV there starts the content-creator screening bot
EDIT_SUBJECT = 'קורות חיים - משרת עורכי וידאו'
EDIT_ABOUT = 'עריכת סרטונים קצרים לאינסטגרם ולטיקטוק מחומרי הגלם שצוות התוכן מצלם אצל הלקוחות.'
EDIT_SKILLS = [
    'ניסיון בעריכת תוכן קצר לרשתות',
    'שליטה בתוכנת עריכה מקצועית',
    'חוש לקצב, לכתוביות ולפתיחה שעוצרת את הגלילה',
    'תיק עבודות',
]

DOING = [
    ('אפיון בזום', 'מול הלקוח, לפני שכותבים מילה'),
    ('כתיבת התסריטים', 'לסרטונים לאינסטגרם ולטיקטוק'),
    ('ימי צילום בשטח', 'ברחבי הארץ, רובם במרכז: מצלמים, מדריכים ומנחים את הלקוח מול המצלמה'),
    ('העברה לעריכה', 'העלאת החומרים לעורכים שלנו'),
    ('קשר שוטף עם הלקוח', 'תקשורת בסיסית ותחזוקה של הקשר'),
]
SKILLS = [
    'ורבליות',
    'ביטחון עצמי',
    'נוכחות בשטח ויכולת תיאטרלית להדגים ללקוח איך לעמוד מול מצלמה',
    'התמודדות עם לקוחות שקשה להם לעמוד מול מצלמה',
    'קופירייטינג וכתיבת תסריטים',
]
SKILLS_SHORT = [
    'ורבליות, ביטחון עצמי ונוכחות בשטח',
    'יכולת להדגים ללקוח איך לעמוד מול מצלמה, גם למי שקשה לו',
    'קופירייטינג וכתיבת תסריטים',
    'משרה מלאה כשכירים, ראשון עד חמישי, בלי עבודות צד',
]
MUST = [
    'רכב או אופנוע להתנייד, כי זו משרת שטח',
    'משרה מלאה כשכירים, ראשון עד חמישי, בלי עבודות צד',
]
EXAMPLES = [
    ('כושר ותזונה', 'טיקטוק', 'https://vt.tiktok.com/ZSh3E6jJ9/'),
    ('חלקי חילוף', 'פייסבוק', 'https://www.facebook.com/share/r/1FEiutFQrm/'),
]
STEPS = [
    ('שולחים קורות חיים', 'בכפתור כאן למטה'),
    ('שיחת היכרות קצרה בוואטסאפ', 'כמה שאלות כדי לבדוק שיש התאמה'),
    ('משימת כתיבה קצרה', 'שלושה ימים להגשה'),
    ('ראיון', 'נפגשים ומכירים'),
]

CSS = LEGAL_CSS + '''
/* job openings page, built by tools/build_jobs.py */
.jb-hero{position:relative;overflow:hidden;text-align:center;padding:clamp(60px,9vw,112px) clamp(20px,5vw,64px) clamp(34px,5vw,56px)}
.jb-hero::before{content:"";position:absolute;inset:0;background:radial-gradient(620px 360px at 50% 0%,rgba(50,233,218,.14),transparent 70%),radial-gradient(520px 320px at 10% 100%,rgba(229,0,136,.10),transparent 70%);pointer-events:none}
.jb-live{position:relative;display:inline-flex;align-items:center;gap:10px;margin-bottom:22px;padding:8px 16px;border-radius:999px;border:1px solid rgba(50,233,218,.35);color:#fff;font-weight:700;font-size:15px}
.jb-live i{width:9px;height:9px;border-radius:50%;background:#32e9da;box-shadow:0 0 0 0 rgba(50,233,218,.7);animation:jbPulse 1.8s ease-out infinite}
@keyframes jbPulse{0%{box-shadow:0 0 0 0 rgba(50,233,218,.7)}100%{box-shadow:0 0 0 12px rgba(50,233,218,0)}}
.orca-legal2 .jb-hero h1{position:relative;font-size:clamp(46px,8vw,92px)}
.orca-legal2 .jb-sub{position:relative;max-width:620px;margin:20px auto 0;color:#b9c0d0;font-size:clamp(17px,1.9vw,20px);text-wrap:balance}

.jb-wrap{position:relative;max-width:1080px;margin:0 auto;padding:0 clamp(20px,5vw,64px)}
.jb-job{position:relative;border-radius:26px;background:#0a1f3d;border:1px solid rgba(255,255,255,.1);padding:clamp(26px,4vw,52px);
  box-shadow:-12px 12px 0 -1px #001b3f,-12px 12px 0 0 rgba(229,0,136,.4)}
.jb-job__top{display:flex;flex-wrap:wrap;align-items:flex-end;justify-content:space-between;gap:18px 28px;padding-bottom:26px;margin-bottom:28px;border-bottom:1px solid rgba(255,255,255,.1)}
.jb-tag{display:inline-flex;font-size:14px;font-weight:700;color:#e50088;padding:5px 12px;border-radius:999px;border:1px solid rgba(229,0,136,.45);margin-bottom:12px}
.orca-legal2 .jb-job h2{color:#fff;font-size:clamp(34px,5vw,56px);font-weight:900;line-height:1.02;letter-spacing:-.01em}
.jb-chips{display:flex;flex-wrap:wrap;gap:10px}
.jb-chip{display:inline-flex;align-items:center;gap:8px;min-height:40px;padding:0 16px;border-radius:999px;background:rgba(255,255,255,.05);border:1px solid rgba(255,255,255,.12);color:#fff;font-size:15px;font-weight:500}
.jb-chip svg{width:16px;height:16px;flex:none;stroke:#32e9da;fill:none;stroke-width:2;stroke-linecap:round;stroke-linejoin:round}
.orca-legal2 .jb-about{color:#dfe4ee;font-size:clamp(17px,1.8vw,19px);line-height:1.8;max-width:820px;margin-bottom:clamp(30px,4vw,44px)}
.jb-about b{color:#fff}
.jb-mark{color:#fff;font-weight:700;background:linear-gradient(transparent 55%,rgba(50,233,218,.35) 55%);padding:0 2px}

.jb-cols{display:grid;grid-template-columns:1.15fr 1fr;gap:clamp(22px,3vw,40px)}
.orca-legal2 .jb-h3{display:flex;align-items:center;gap:12px;color:#fff;font-size:clamp(21px,2.3vw,25px);font-weight:900;margin-bottom:18px}
.jb-h3 .ol-dash{margin-top:2px}
.jb-do{list-style:none;display:flex;flex-direction:column;gap:12px}
.jb-do li{display:flex;gap:14px;align-items:flex-start;padding:14px 16px;border-radius:16px;background:rgba(255,255,255,.035);border:1px solid rgba(255,255,255,.08)}
.jb-do .n{flex:none;display:grid;place-items:center;width:34px;height:34px;border-radius:50%;background:rgba(50,233,218,.12);border:1px solid rgba(50,233,218,.45);color:#32e9da;font-weight:900;font-size:15px}
.jb-do b{display:block;color:#fff;font-size:17px;line-height:1.35}
.jb-do span{display:block;color:#b9c0d0;font-size:15px;line-height:1.5}
.jb-list{list-style:none;display:flex;flex-direction:column;gap:11px}
.jb-list li{position:relative;padding-right:22px;color:#dfe4ee;font-size:16.5px;line-height:1.55}
.jb-list li::before{content:"";position:absolute;right:2px;top:.6em;width:8px;height:8px;border-radius:50%;background:#32e9da;box-shadow:0 0 8px #32e9da}
.jb-list li:nth-child(even)::before{background:#e50088;box-shadow:0 0 8px #e50088}
.jb-must{margin-top:26px;padding:18px 18px 18px 20px;border-radius:16px;background:rgba(229,0,136,.07);border:1px solid rgba(229,0,136,.3)}
.orca-legal2 .jb-must h4{color:#fff;font-size:16px;font-weight:900;margin-bottom:10px}
.jb-must .jb-list li{font-size:16px}

.jb-sec{padding:clamp(56px,7vw,88px) 0 0}
.jb-sec__head{text-align:center;margin-bottom:clamp(24px,3vw,36px)}
.jb-sec__head .ol-kicker{margin-bottom:10px}
.orca-legal2 .jb-sec__head h2{color:#fff;font-size:clamp(28px,3.8vw,42px);font-weight:900;line-height:1.12;text-wrap:balance}
.orca-legal2 .jb-sec__head p{color:#b9c0d0;max-width:560px;margin:10px auto 0}
.jb-ex{display:grid;grid-template-columns:repeat(2,1fr);gap:18px;max-width:760px;margin:0 auto}
.orca-legal2 a.jb-ex__card{position:relative;display:flex;align-items:center;gap:16px;padding:22px;border-radius:20px;background:rgba(255,255,255,.04);border:1px solid rgba(255,255,255,.1);color:#fff;
  transition:transform 200ms cubic-bezier(.22,.8,.28,1),border-color 200ms,box-shadow 200ms}
.orca-legal2 a.jb-ex__card:hover{transform:translateY(-4px);border-color:rgba(50,233,218,.6);box-shadow:0 0 30px rgba(50,233,218,.2);color:#fff}
.jb-ex__play{flex:none;display:grid;place-items:center;width:56px;height:56px;border-radius:50%;background:#32e9da;box-shadow:0 0 20px rgba(50,233,218,.5)}
.jb-ex__card:nth-child(2) .jb-ex__play{background:#e50088;box-shadow:0 0 20px rgba(229,0,136,.5)}
.jb-ex__play svg{width:20px;height:20px;margin-left:3px;fill:#001b3f}
.jb-ex__card:nth-child(2) .jb-ex__play svg{fill:#fff}
.jb-ex__card b{display:block;font-size:19px;font-weight:900}
.jb-ex__card span{display:block;color:#b9c0d0;font-size:14.5px}
.jb-ex__arrow{margin-right:auto;color:#b9c0d0;font-size:20px}

.jb-steps{list-style:none;display:grid;grid-template-columns:repeat(4,1fr);gap:16px;counter-reset:st}
.jb-steps li{position:relative;padding:24px 20px 22px;border-radius:20px;background:rgba(255,255,255,.035);border:1px solid rgba(255,255,255,.09)}
.jb-steps .num{display:block;font-size:44px;font-weight:900;line-height:1;margin-bottom:12px;color:transparent;-webkit-text-stroke:1.5px #32e9da;text-shadow:0 0 18px rgba(50,233,218,.35)}
.jb-steps li:nth-child(even) .num{-webkit-text-stroke-color:#e50088;text-shadow:0 0 18px rgba(229,0,136,.35)}
.jb-steps b{display:block;color:#fff;font-size:17.5px;line-height:1.3;margin-bottom:4px}
.jb-steps span{display:block;color:#b9c0d0;font-size:15px}

.jb-cta{position:relative;margin:clamp(56px,7vw,88px) auto clamp(72px,9vw,112px);max-width:880px;text-align:center;padding:clamp(34px,5vw,56px) clamp(22px,4vw,48px);border-radius:28px;overflow:hidden;
  background:radial-gradient(520px 260px at 50% 0%,rgba(50,233,218,.18),transparent 70%),radial-gradient(420px 240px at 50% 100%,rgba(229,0,136,.16),transparent 70%),#0a1f3d;border:1px solid rgba(255,255,255,.12)}
.orca-legal2 .jb-cta h2{color:#fff;font-size:clamp(30px,4.4vw,48px);font-weight:900;line-height:1.08;text-wrap:balance}
.orca-legal2 .jb-cta p{color:#b9c0d0;max-width:520px;margin:12px auto 26px;font-size:17px}
.orca-legal2 a.jb-btn{display:inline-flex;align-items:center;gap:10px;min-height:58px;padding:0 34px;border-radius:999px;background:#e50088;color:#fff;font-weight:900;font-size:18px;box-shadow:0 0 28px rgba(229,0,136,.55);
  transition:transform 160ms cubic-bezier(.22,.8,.28,1),box-shadow 160ms}
.orca-legal2 a.jb-btn:hover{transform:translateY(-2px);box-shadow:0 0 38px rgba(229,0,136,.75);color:#fff}
.jb-btn svg{width:20px;height:20px;stroke:#fff;fill:none;stroke-width:2;stroke-linecap:round;stroke-linejoin:round}
.jb-mail{display:block;margin-top:14px;color:#b9c0d0;font-size:15px}
.orca-legal2 .jb-mail a{color:#32e9da}

.jb-main{position:relative;overflow:hidden;padding:clamp(40px,6vw,80px) clamp(20px,5vw,64px) clamp(64px,8vw,104px)}
.jb-main::before{content:"";position:absolute;inset:0;background:radial-gradient(620px 380px at 85% 10%,rgba(50,233,218,.12),transparent 70%),radial-gradient(520px 360px at 10% 90%,rgba(229,0,136,.12),transparent 70%);pointer-events:none}
.jb-ad{position:relative;max-width:1120px;margin:0 auto;display:grid;grid-template-columns:1fr 1.05fr;gap:clamp(28px,5vw,64px);align-items:center}
.jb-photo{position:relative;margin:0;border-radius:26px;overflow:hidden;border:1px solid rgba(255,255,255,.12);box-shadow:-14px 14px 0 -1px #001b3f,-14px 14px 0 0 rgba(229,0,136,.45),0 30px 70px rgba(0,0,0,.45)}
.orca-legal2 .jb-photo img{display:block;width:100% !important;height:auto !important;max-width:none !important;aspect-ratio:4/5;object-fit:cover}
.jb-photo figcaption{position:absolute;top:18px;right:18px}
.jb-photo .jb-live{margin:0;background:rgba(0,19,46,.72);backdrop-filter:blur(8px);-webkit-backdrop-filter:blur(8px)}
.orca-legal2 .jb-post h1{font-size:clamp(44px,6.4vw,80px);line-height:1}
.orca-legal2 .jb-role{display:flex;flex-wrap:wrap;align-items:center;gap:12px;margin:22px 0 16px;color:#fff;font-size:clamp(28px,3.4vw,38px);font-weight:900;line-height:1.1}
.jb-role .jb-tag{margin:0}
.orca-legal2 .jb-post .jb-about{font-size:clamp(17px,1.7vw,19px);margin-bottom:20px}
.jb-post .jb-chips{margin-bottom:28px}
.orca-legal2 .jb-post .jb-h3{margin-bottom:14px}
.jb-post .jb-list{margin-bottom:30px}
.jb-role2{margin-top:clamp(34px,4vw,48px);padding-top:clamp(28px,3.5vw,40px);border-top:1px solid rgba(255,255,255,.12)}
.orca-legal2 .jb-role2 .jb-role{margin-top:0}
.jb-role2 .jb-tag{color:#32e9da;border-color:rgba(50,233,218,.45)}
.orca-legal2 a.jb-btn--cyan{background:#32e9da;color:#001b3f;box-shadow:0 0 28px rgba(50,233,218,.5)}
.orca-legal2 a.jb-btn--cyan:hover{color:#001b3f;box-shadow:0 0 38px rgba(50,233,218,.7)}
.jb-btn--cyan svg{stroke:#001b3f}
.jb-ad{align-items:start}
@media (min-width:901px){.jb-photo{position:sticky;top:110px}}
@media (max-width:900px){.jb-ad{grid-template-columns:1fr}.jb-photo{max-width:480px;margin:0 auto;width:100%}}
@media (max-width:900px){.jb-cols{grid-template-columns:1fr}.jb-steps{grid-template-columns:repeat(2,1fr)}}
@media (max-width:560px){.jb-ex{grid-template-columns:1fr}.jb-steps{grid-template-columns:1fr}.jb-job__top{align-items:flex-start}}
@media (prefers-reduced-motion:reduce){.jb-live i{animation:none}}
'''

ICON = {
    'pin': '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M12 22s7-6.2 7-12a7 7 0 1 0-14 0c0 5.8 7 12 7 12z"/><circle cx="12" cy="10" r="2.5"/></svg>',
    'clock': '<svg viewBox="0 0 24 24" aria-hidden="true"><circle cx="12" cy="12" r="9"/><path d="M12 7v5l3 2"/></svg>',
    'car': '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M5 17h14M6 17v2M18 17v2M4 13l2-5a2 2 0 0 1 1.9-1.4h8.2A2 2 0 0 1 18 8l2 5v4H4z"/><circle cx="8" cy="14" r="1"/><circle cx="16" cy="14" r="1"/></svg>',
    'cam': '<svg viewBox="0 0 24 24" aria-hidden="true"><rect x="3" y="7" width="13" height="10" rx="2"/><path d="M16 11l5-3v8l-5-3"/></svg>',
    'mail': '<svg viewBox="0 0 24 24" aria-hidden="true"><rect x="3" y="5" width="18" height="14" rx="2"/><path d="M3 7l9 6 9-6"/></svg>',
}
PLAY = '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M6 4.5v15a1 1 0 0 0 1.5.86l12.4-7.5a1 1 0 0 0 0-1.72L7.5 3.64A1 1 0 0 0 6 4.5z"/></svg>'


def kicker(text):
    return '<span class="ol-kicker"><span class="ol-dash" aria-hidden="true"><i></i><i></i></span>%s</span>' % text


def build(out):
    from urllib.parse import quote
    nav = '\n'.join('        <a href="%s"%s>%s</a>' % (u, ' aria-current="page"' if n == 'משרות פנויות' else '', n) for f, u, n in LINKS)
    doing = '\n'.join('<li><span class="n">%d</span><div><b>%s</b><span>%s</span></div></li>' % (i + 1, t, d) for i, (t, d) in enumerate(DOING))
    skills = '\n'.join('<li>%s</li>' % s for s in SKILLS_SHORT)
    must = '\n'.join('<li>%s</li>' % s for s in MUST)
    examples = '\n'.join('<a class="jb-ex__card" href="%s" target="_blank" rel="noopener"><span class="jb-ex__play">%s</span><span><b>%s</b><span>סרטון לדוגמה · %s</span></span><span class="jb-ex__arrow" aria-hidden="true">↗</span></a>' % (u, PLAY, t, p) for t, p, u in EXAMPLES)
    steps = '\n'.join('<li><span class="num">0%d</span><b>%s</b><span>%s</span></li>' % (i + 1, t, d) for i, (t, d) in enumerate(STEPS))
    mailto = 'mailto:%s?subject=%s' % (APPLY_MAIL, quote(APPLY_SUBJECT))
    edit_mailto = 'mailto:%s?subject=%s' % (EDIT_MAIL, quote(EDIT_SUBJECT))
    edit_skills = '\n'.join('<li>%s</li>' % x for x in EDIT_SKILLS)
    html = '''<!doctype html>
<html lang="he" dir="rtl">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>אנחנו מגייסים: יוצרי תוכן ועורכי וידאו – אורקה טרייב</title>
<meta name="description" content="אורקה טרייב מגייסת יוצרי תוכן ועורכי וידאו לתוכן ויראלי ברשתות.">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Heebo:wght@300;400;500;700;900&display=swap">
<style>
/* orcatribe job openings in the brand language, built by tools/build_jobs.py */%(css)s</style>
</head>
<body>
<div class="orca-legal2">
<header class="ol-header">
  <div class="ol-header__row">
    <a href="https://www.orcatribe.co.il/" aria-label="אורקה טרייב, לדף הבית"><img src="%(logo)s" alt="אורקה טרייב" width="112" height="50"></a>
    <a class="ol-back" href="https://www.orcatribe.co.il/">לדף הבית <span aria-hidden="true">←</span></a>
  </div>
</header>
<main class="jb-main">
  <div class="jb-ad">
    <figure class="jb-photo">
      <img src="images/creator-on-set.webp" alt="יוצר תוכן מצלם בעל עסק בטלפון, ביום צילום בשטח" width="880" height="1100">
      <figcaption><span class="jb-live"><i aria-hidden="true"></i>משרה פתוחה</span></figcaption>
    </figure>
    <article class="jb-post" aria-labelledby="jb-title">
      <h1>אנחנו <span class="ol-hl"><span aria-hidden="true">מגייסים</span><span>מגייסים</span></span></h1>
      <p class="jb-role"><span class="jb-tag">משרה פנויה</span><span id="jb-title">יוצרי תוכן</span></p>
      <p class="jb-about">כתיבת תסריטים לעסקים שרוצים להתפרסם באינסטגרם ובטיקטוק, אפיון מול הלקוח בזום, ו<span class="jb-mark">ימי צילום בשטח</span> שבהם מצלמים את הלקוח ומובילים אותו מול המצלמה.</p>
      <div class="jb-chips">
        <span class="jb-chip">%(i_clock)sמשרה מלאה</span>
        <span class="jb-chip">%(i_pin)sברחבי הארץ, בעיקר במרכז</span>
        <span class="jb-chip">%(i_car)sרכב או אופנוע</span>
      </div>
      <h2 class="jb-h3"><span class="ol-dash" aria-hidden="true"><i></i><i></i></span>מה מחפשים</h2>
      <ul class="jb-list">
%(skills)s
      </ul>
      <a class="jb-btn" href="%(mailto)s">%(i_mail)sשליחת קורות חיים</a>
      <span class="jb-mail">או ישירות למייל <a href="%(mailto)s">%(mail)s</a></span>
      <div class="jb-role2">
        <p class="jb-role"><span class="jb-tag">משרה פנויה</span><span>עורכי וידאו</span></p>
        <p class="jb-about">%(edit_about)s</p>
        <ul class="jb-list">
%(edit_skills)s
        </ul>
        <a class="jb-btn jb-btn--cyan" href="%(edit_mailto)s">%(i_mail)sשליחת קורות חיים ותיק עבודות</a>
      </div>
    </article>
  </div>
</main>

<footer class="ol-footer">
  <div class="ol-footer__in">
    <div class="ol-footer__row">
      <img src="%(logo)s" alt="אורקה טרייב" width="104" height="47">
      <nav aria-label="קישורים בתחתית">
%(nav)s
      </nav>
    </div>
    <div class="ol-footer__rule"></div>
    <p>כל הזכויות שמורות לאורקה טרייב בע״מ © · אברהם פצ׳ורניק 17, נס ציונה · <a href="mailto:orcatribeltd@gmail.com">orcatribeltd@gmail.com</a></p>
  </div>
</footer>
</div>
</body>
</html>
''' % dict(css=CSS, logo=LOGO, nav=nav, doing=doing, skills=skills, must=must, examples=examples, steps=steps,
           mailto=mailto, mail=APPLY_MAIL, edit_mailto=edit_mailto, edit_skills=edit_skills, edit_about=EDIT_ABOUT, k_examples=kicker('דוגמאות'), k_process=kicker('תהליך הגיוס'),
           i_clock=ICON['clock'], i_pin=ICON['pin'], i_car=ICON['car'], i_mail=ICON['mail'])
    dest = os.path.join(ROOT, out)
    os.makedirs(dest, exist_ok=True)
    open(os.path.join(dest, 'index.html'), 'w', encoding='utf-8').write(html)
    print('wrote pages/%s/index.html (%d bytes)' % (out, len(html)))


if __name__ == '__main__':
    if len(sys.argv) != 2:
        sys.exit(__doc__)
    build(sys.argv[1])
