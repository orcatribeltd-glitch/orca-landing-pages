#!/usr/bin/env python3
"""Builds pages/orca-brand/index.html — the "בניית מותג" SEO service page (approved copy, 27/09/2026).

It is assembled from the live home page's own components (head, header, services grid, quotes,
contact form, video carousel, footer, scripts) so both pages always share one design. Re-run after
changing orca-home: `python3 tools/build_orca_brand.py`.
"""
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
home = (ROOT / 'pages/orca-home/index.html').read_text(encoding='utf-8')
L = home.split('\n')


def lines(a, b):
    """home lines a..b, 1-based, inclusive"""
    return '\n'.join(L[a - 1:b])


def find(prefix, start=0):
    for i in range(start, len(L)):
        if L[i].lstrip().startswith(prefix):
            return i + 1
    raise SystemExit('not found: ' + prefix)


def section_end(start):
    for i in range(start - 1, len(L)):
        if L[i].strip() == '</section>':
            return i + 1
    raise SystemExit('no </section> after %d' % start)


IMG = 'https://raw.githubusercontent.com/orcatribeltd-glitch/orca-landing-pages/main/pages/orca-home/images/'
CY, MG = '#32e9da', '#e50088'


def kicker(text, center=False, mb=18):
    align = 'justify-content:center;' if center else ''
    return (f'<span style="display:inline-flex;align-items:center;{align}gap:14px;margin-bottom:{mb}px">'
            f'<span style="display:flex;flex-direction:column;gap:3px;flex:none">'
            f'<span style="width:28px;height:1px;background:{CY};box-shadow:0 0 6px {CY}"></span>'
            f'<span style="width:28px;height:1px;background:{MG};box-shadow:0 0 6px {MG};transform:translateX(-7px)"></span></span>'
            f'<span style="color:#fff;font-weight:700;font-size:15px">{text}</span></span>')


def hl(word):
    return (f'<span style="position:relative;display:inline-block;color:{CY};text-shadow:0 0 18px rgba(50,233,218,.5)">'
            f'<span aria-hidden="true" class="olp-echo" data-echo="{word}" style="position:absolute;inset:0;transform:translate(-.07em,.07em);'
            f'color:transparent;-webkit-text-stroke:1px rgba(229,0,136,.85);text-shadow:none;pointer-events:none"></span>'
            f'<span style="position:relative">{word}</span></span>')


H2 = 'font-size:clamp(32px,4.4vw,52px);font-weight:900;line-height:1.05;letter-spacing:-.01em;text-wrap:balance'
P = 'color:#b9c0d0;font-size:clamp(17px,1.5vw,19px);line-height:1.7;text-wrap:pretty'


def btn(cls, bg):
    return (f'<a class="{cls}" href="#contact" style="display:inline-flex;align-items:center;justify-content:center;min-height:58px;'
            f'padding:0 32px;border-radius:999px;background:{MG};color:#fff;font-weight:700;font-size:18px;'
            f'box-shadow:-6px 6px 0 -1px {bg},-6px 6px 0 0 {CY},0 0 24px rgba(229,0,136,.45);'
            f'transition:box-shadow 200ms cubic-bezier(0.22,0.8,0.28,1)">שריין שיחת ייעוץ ללא עלות</a>')


# ---------- head + header ----------
head_end = find('</header>')
top = lines(1, head_end)
top = top.replace('<title>אורקה טרייב – סוכנות שיווק</title>', '<title>בניית מותג לעסקים | אורקה טרייב</title>')
top = re.sub(r'\.elementor-114 ', '.elementor ', top)
# the header's section links point back to the home page; "לקוחות מספרים" and "בואו נדבר" stay on this page
for a in ('#who', '#services-grid', '#guide'):
    top = top.replace(f'href="{a}"', f'href="https://www.orcatribe.co.il/{a}"')
extra_css = '''
/* FAQ accordion (בניית מותג page) */
.orca-faq details{border-top:1px solid rgba(255,255,255,.1)}
.orca-faq details:last-child{border-bottom:1px solid rgba(255,255,255,.1)}
.orca-faq summary{list-style:none;cursor:pointer;display:flex;align-items:center;justify-content:space-between;gap:16px;min-height:44px;padding:22px 4px;font-size:clamp(18px,1.8vw,21px);font-weight:700;color:#fff}
.orca-faq summary::-webkit-details-marker{display:none}
.orca-faq summary::after{content:"+";flex:none;font:900 28px/1 "Figtree",sans-serif;color:#32e9da;transition:transform 200ms cubic-bezier(0.22,0.8,0.28,1)}
.orca-faq details[open] summary::after{transform:rotate(45deg);color:#e50088}
.orca-faq details p{color:#b9c0d0;font-size:17px;line-height:1.7;padding:0 4px 24px;max-width:72ch}
.orca-why p+p{margin-top:14px}
'''
top = top.replace('</style>\n</head>', extra_css + '</style>\n</head>', 1)

# ---------- 1. hero ----------
hero_start = find('<section data-screen-label="Hero"')
hero_end = section_end(hero_start)
hero = lines(hero_start, hero_end)
left_start = hero.index('<div style="flex:1 1 440px')
left_end = hero.index('<div style="flex:1 1 380px')
new_left = f'''<div style="flex:1 1 440px;min-width:0;display:flex;flex-direction:column;align-items:flex-start">
      {kicker('בניית מותג לעסקים', mb=28)}
      <h1 style="font-size:clamp(40px,5.2vw,64px);font-weight:900;line-height:1.04;letter-spacing:-.01em;margin-bottom:24px;text-wrap:balance">בניית מותג ברשתות, שגורמת ללקוחות לבחור <span style="white-space:nowrap">{hl('דווקא בך')}</span></h1>
      <p style="color:#fff;font-size:clamp(18px,1.7vw,21px);line-height:1.55;max-width:520px;margin-bottom:14px;text-wrap:pretty">כשלא מכירים אותך, הלקוח משווה רק מחירים.<br>כשכבר מכירים אותך, הוא מגיע לשיחה ושואל ״מתי מתחילים?״.</p>
      <p style="color:#b9c0d0;font-size:clamp(17px,1.5vw,19px);line-height:1.6;max-width:500px;margin-bottom:36px;text-wrap:pretty">אחרי 7 שנים ומאות עסקים שליווינו, פיצחנו מה הופך עסק למותג שאנשים עוקבים אחריו וקונים ממנו.</p>
      {btn('dcs8', '#001b3f')}
    </div>
    '''
hero = hero[:left_start] + new_left + hero[left_end:]
hero = hero.replace('src="images/', f'src="{IMG}')

# ---------- 2. what is brand building ----------
what = f'''<section id="what" data-screen-label="What is brand building" style="position:relative;background:#00132e;padding:clamp(72px,8vw,112px) clamp(24px,5vw,64px)">
  <div style="position:relative;max-width:780px;margin:0 auto;display:flex;flex-direction:column;align-items:center;text-align:center">
    {kicker('01/05 · מה זה בכלל', center=True)}
    <h2 style="{H2};margin-bottom:28px">מה זה בעצם {hl('בניית מותג')}?</h2>
    <p style="{P};margin-bottom:14px">בניית מותג היא כל מה שגורם לאנשים לזהות את העסק שלך, לזכור אותו ולסמוך עליו, עוד לפני שהם דיברו איתך. לוגו וצבעים הם רק החלק הקטן.</p>
    <p style="{P};margin-bottom:14px">היום מותג נבנה ברשתות: בסרטונים שאנשים רואים, בתוכן שהם שומרים ומשתפים, ובפנים שהם מתחילים להכיר.</p>
    <p style="color:#fff;font-size:clamp(19px,1.9vw,23px);font-weight:700;line-height:1.5;text-wrap:balance">ומי שמופיע להם בפיד כל שבוע, הוא הראשון שהם חושבים עליו כשהם צריכים את השירות.</p>
  </div>
</section>'''

# ---------- 3. what the process includes (home services grid, new words) ----------
svc_start = find('<section id="services"')
svc_end = section_end(svc_start)
svc = lines(svc_start, svc_end)
svc = svc.replace('id="services"', 'id="includes"').replace('data-screen-label="Services"', 'data-screen-label="Includes"')
svc = svc.replace(' id="services-grid"', '').replace('background:#00132e;padding', 'background:#001b3f;padding')
h_start = svc.index('<span style="display:inline-flex;flex-direction:column;align-items:center;gap:14px;margin-bottom:22px">')
h_end = svc.index('</p>', h_start) + len('</p>')
svc = svc[:h_start] + (f'{kicker("02/05 · מה מקבלים", center=True, mb=22)}\n'
                       f'    <h2 style="{H2};margin-bottom:20px">מה כולל תהליך {hl("בניית המותג")} אצלנו</h2>\n'
                       f'    <p style="color:#b9c0d0;font-size:18px;max-width:62ch">ארבעה דברים שעובדים ביחד, תחת קורת גג אחת.</p>') + svc[h_end:]
arts = re.findall(r'\n\s*<article .*?</article>', svc, re.S)
assert len(arts) == 4, len(arts)
cards = [
    ('הפקת סרטונים לעסקים', 'מגיעים אליך לשטח, כותבים את התסריטים ומצלמים. אתה רק צריך להגיע ולדבר.'),
    ('תוכן לרשתות חברתיות', 'סרטונים לאינסטגרם, לטיקטוק ולפייסבוק, בקצב קבוע, כך שהקהל פוגש אותך כל שבוע ולא פעם בחודש.'),
    ('אסטרטגיה לפני המצלמה', 'לפני שמצלמים סרטון אחד, מבינים מי הקהל שלך, מה מבדיל אותך מהמתחרים, ואיזה סיפור רק אתה יכול לספר.'),
    ('בניית מותג אישי', 'הופכים אותך לפנים של העסק: הסיפור שלך, הסגנון שלך והתוכן שלך. ככה לקוחות מגיעים אליך כשהם כבר מכירים אותך וסומכים עליך.'),
]
new_arts = []
for art, (title, text) in zip(arts, cards):
    art = re.sub(r'(<h3[^>]*>).*?(</h3>)', lambda m: m.group(1) + title + m.group(2), art, count=1, flags=re.S)
    art = re.sub(r'(<p(?:\s[^>]*)?>).*?(</p>)', lambda m: m.group(1) + text + m.group(2), art, count=1, flags=re.S)
    new_arts.append(art)
for old, new in zip(arts, new_arts):
    svc = svc.replace(old, new, 1)

# ---------- 4. quotes + form (home, as is) ----------
recs_start = find('<section id="recs"')
recs = lines(recs_start, section_end(recs_start))
contact_start = find('<section id="contact"')
contact = lines(contact_start, section_end(contact_start))
assert '<!--olp:form:1-->' in contact

# ---------- 5. why videos ----------
why = f'''<section id="why" data-screen-label="Why video" style="position:relative;overflow:hidden;padding:clamp(72px,8vw,112px) clamp(24px,5vw,64px)">
  <div style="position:absolute;inset:0;background:radial-gradient(620px 420px at 85% 40%,rgba(229,0,136,.10),transparent 70%);pointer-events:none"></div>
  <div class="orca-why" style="position:relative;max-width:780px;margin:0 auto;display:flex;flex-direction:column;align-items:center;text-align:center">
    {kicker('03/05 · למה סרטונים', center=True)}
    <h2 style="{H2};margin-bottom:28px">למה סרטונים בונים מותג {hl('מהר יותר')} מכל דבר אחר</h2>
    <p style="{P}">בסרטון של דקה אנשים שומעים את הקול שלך, רואים איך אתה מדבר ומבינים מה אתה יודע. אחרי כמה סרטונים הם מרגישים שהם כבר מכירים אותך.</p>
    <p style="color:#fff;font-size:clamp(19px,1.9vw,23px);font-weight:700;line-height:1.5;text-wrap:balance">וככה השיחה הראשונה איתם היא כבר ״מתי מתחילים״, ולא ״כמה זה עולה״.</p>
    <p style="{P}">אבל לא כל סרטון בונה מותג. סרטון בלי כיוון עושה כמה צפיות ונעלם. סרטון שנכתב נכון מושך מאות ואלפי תגובות ושיתופים, ומביא עוקבים שבאמת מתעניינים במה שאתה מוכר.</p>
  </div>
</section>'''

# ---------- 6. process (home's process layout, four steps) ----------
steps = [
    ('שיחת ייעוץ', 'מכירים את העסק, את הקהל ואת המטרות.'),
    ('הפיצוח', 'מוצאים את הבידול ואת הסיפור שלך, וכותבים את התסריטים.'),
    ('יום צילום', 'מגיעים אליך ומצלמים את כל הסרטונים ביום אחד.'),
    ('עריכה והעלאה', 'הסרטונים עולים לרשתות, ובודקים מה עובד כדי שהסבב הבא יהיה חזק יותר.'),
]
lis = []
for i, (t, d) in enumerate(steps):
    col, glow = (CY, 'rgba(50,233,218,.4)') if i % 2 == 0 else (MG, 'rgba(229,0,136,.4)')
    last = ';border-bottom:1px solid rgba(255,255,255,.1)' if i == len(steps) - 1 else ''
    lis.append(f'      <li style="display:grid;grid-template-columns:72px 1fr;gap:20px;padding:28px 0;border-top:1px solid rgba(255,255,255,.1){last}">'
               f'<span style="font-family:\'Figtree\',sans-serif;font-size:46px;font-weight:900;line-height:.9;letter-spacing:-.03em;color:{col};text-shadow:0 0 18px {glow}">0{i + 1}</span>'
               f'<div style="display:flex;flex-direction:column;gap:6px"><h3 style="font-size:21px;font-weight:700;line-height:1.3">{t}</h3>'
               f'<p style="color:#b9c0d0;font-size:16px">{d}</p></div></li>')
process = f'''<section id="process" data-screen-label="Process" style="position:relative;background:#00132e;padding:clamp(72px,8vw,112px) clamp(24px,5vw,64px)">
  <div style="position:absolute;inset:0;background:radial-gradient(620px 460px at 90% 10%,rgba(50,233,218,.10),transparent 70%);pointer-events:none"></div>
  <div style="position:relative;max-width:1180px;margin:0 auto;display:flex;flex-wrap:wrap;align-items:flex-start;gap:clamp(40px,6vw,88px)">
    <div class="dc-sticky" style="flex:1 1 320px;min-width:0;position:sticky;top:120px;display:flex;flex-direction:column;align-items:flex-start">
      {kicker('04/05 · התהליך')}
      <h2 style="{H2};margin-bottom:32px">איך נראה {hl('התהליך')}</h2>
      {btn('dcs19', '#00132e')}
    </div>
    <ol style="flex:1.6 1 480px;min-width:0;list-style:none;display:flex;flex-direction:column">
{chr(10).join(lis)}
    </ol>
  </div>
</section>'''

# ---------- 7. video testimonials (home, as is) ----------
vid_start = find('<section id="testimonials"')
videos = lines(vid_start, section_end(vid_start)).replace('background:#00132e;padding', 'background:#001b3f;padding')

# ---------- 8. FAQ ----------
faq = [
    ('כמה זמן לוקח לבנות מותג ברשתות?', 'תגובות ועוקבים חדשים מתחילים להגיע כבר מהסרטונים הראשונים. מותג שמביא לקוחות באופן קבוע נבנה לאורך כמה חודשים של תוכן עקבי.'),
    ('אני צריך לדעת לדבר מול מצלמה?', 'לא. רוב הלקוחות שלנו לא צילמו את עצמם אף פעם לפני שהגיעו אלינו. ביום הצילום מכוונים אותך משפט אחרי משפט.'),
    ('מה ההבדל בין בניית מותג לבין מיתוג לעסק?', 'מיתוג לעסק זה איך העסק נראה: לוגו, צבעים ופונטים. בניית מותג זה מה שאנשים חושבים ומרגישים כשהם שומעים את השם שלך. אנחנו עובדים על החלק השני, דרך תוכן וסרטונים ברשתות.'),
    ('כמה עולה בניית מותג?', 'זה תלוי בכמות הסרטונים ובקצב. בשיחת הייעוץ בונים הצעה שמתאימה לעסק ולתקציב שלך.'),
    ('אתם עובדים עם עסקים מכל הארץ?', 'כן. אנחנו עובדים עם עסקים מכל הארץ, ומגיעים לצלם אצלכם.'),
    ('אפשר לשלב גם קמפיינים ממומנים?', 'כן. אותם סרטונים עובדים גם כמודעות, ואנחנו מנהלים גם את הקמפיינים.'),
]
details = '\n'.join(f'      <details><summary>{q}</summary><p>{a}</p></details>' for q, a in faq)
faq_html = f'''<section id="faq" data-screen-label="FAQ" style="position:relative;background:#00132e;padding:clamp(72px,8vw,112px) clamp(24px,5vw,64px)">
  <div style="position:relative;max-width:860px;margin:0 auto;display:flex;flex-direction:column">
    <div style="display:flex;flex-direction:column;align-items:center;text-align:center;margin-bottom:40px">
      {kicker('05/05 · שאלות נפוצות', center=True)}
      <h2 style="{H2}">שאלות נפוצות על {hl('בניית מותג')}</h2>
    </div>
    <div class="orca-faq">
{details}
    </div>
  </div>
</section>'''

# ---------- 9. closing CTA ----------
closing = f'''<section data-screen-label="Closing" style="position:relative;overflow:hidden;padding:clamp(72px,8vw,112px) clamp(24px,5vw,64px)">
  <div style="position:absolute;inset:0;background:radial-gradient(700px 380px at 50% 50%,rgba(229,0,136,.14),transparent 70%);pointer-events:none"></div>
  <div style="position:relative;max-width:780px;margin:0 auto;display:flex;flex-direction:column;align-items:center;text-align:center">
    <h2 style="{H2};margin-bottom:22px">רוצה שיכירו את העסק שלך {hl('עוד לפני')} שמתקשרים אליך?</h2>
    <p style="{P};margin-bottom:36px">בשיחת ייעוץ ללא עלות נבין איפה העסק שלך נמצא היום, ומה הצעד הראשון לבנות ממנו מותג.</p>
    {btn('dcs8', '#001b3f')}
  </div>
</section>'''

# ---------- footer + scripts ----------
main_end = find('</main>')
body_end = find('</body>')
tail = lines(main_end, body_end - 1)
tail = re.sub(r'<script type="application/ld\+json">.*?</script>\n?', '', tail, flags=re.S)

URL = 'https://www.orcatribe.co.il/בניית-מותג/'
ld = [
    {'@context': 'https://schema.org', '@type': 'Service', 'name': 'בניית מותג לעסקים', 'serviceType': 'בניית מותג',
     'description': 'בניית מותג לעסקים ברשתות: הפקת סרטונים, תוכן לאינסטגרם, לטיקטוק ולפייסבוק, בניית מותג אישי ואסטרטגיה.',
     'url': URL, 'areaServed': {'@type': 'Country', 'name': 'ישראל'},
     'provider': {'@type': 'ProfessionalService', '@id': 'https://www.orcatribe.co.il/#business', 'name': 'אורקה טרייב', 'url': 'https://www.orcatribe.co.il/'}},
    {'@context': 'https://schema.org', '@type': 'FAQPage',
     'mainEntity': [{'@type': 'Question', 'name': q, 'acceptedAnswer': {'@type': 'Answer', 'text': a}} for q, a in faq]},
]
ld_html = ''.join('<script type="application/ld+json">' + json.dumps(x, ensure_ascii=False) + '</script>\n' for x in ld)

page = '\n'.join([
    top, '', '<main>', hero, what, svc, recs, '', contact, '', why, process, videos, faq_html, closing, tail,
]) + '\n' + ld_html + '</body>\n</html>\n'
page = page.replace('src="images/', 'src="' + IMG)
out = ROOT / 'pages/orca-brand/index.html'
out.parent.mkdir(exist_ok=True)
out.write_text(page, encoding='utf-8')
print('written', out, len(page))
