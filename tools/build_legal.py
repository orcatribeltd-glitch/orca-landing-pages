#!/usr/bin/env python3
"""Rebuild the orcatribe legal pages (privacy, terms, accessibility) in the brand language.

The legal text itself is taken verbatim from each page's current .orca-legal__body and never edited here.
Design: Obsidian 04 Knowledge/02 Brand & Design/Orca Tribe — Brand Language (DNA system).md — minimal variant.
Usage: tools/build_legal.py   (rewrites pages/orca-privacy, orca-terms, orca-accessibility)
"""
import os, re

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'pages')
PAGES = [  # folder, title before the highlight, highlight word, kicker
    ('orca-privacy', 'מדיניות', 'פרטיות', ''),
    ('orca-terms', 'תנאי', 'שימוש', ''),
    ('orca-accessibility', 'הצהרת', 'נגישות', 'נגישות האתר'),
]

CSS = '''
body{margin:0;background:#001b3f}
.orca-legal2{direction:rtl;text-align:right;background:#001b3f;color:#b9c0d0;font-family:"Heebo",system-ui,sans-serif;font-size:17px;line-height:1.75;-webkit-font-smoothing:antialiased;overflow-x:clip}
.orca-legal2 *{box-sizing:border-box}
.orca-legal2 a{color:#32e9da;text-decoration:none}
.orca-legal2 a:hover{color:#fff}
.orca-legal2 h1,.orca-legal2 h2,.orca-legal2 h3,.orca-legal2 p,.orca-legal2 ul,.orca-legal2 ol{margin:0;padding:0}
.ol-header{position:sticky;top:0;z-index:50;background:rgba(0,19,46,.78);backdrop-filter:blur(18px) saturate(120%);-webkit-backdrop-filter:blur(18px) saturate(120%);border-bottom:1px solid rgba(255,255,255,.1)}
.ol-header__row{max-width:1180px;margin:0 auto;padding:0 clamp(20px,4vw,40px);min-height:78px;display:flex;align-items:center;justify-content:space-between;gap:24px}
.ol-header img{width:112px;height:auto;display:block}
.orca-legal2 a.ol-back{display:inline-flex;align-items:center;gap:8px;min-height:44px;padding:0 20px;border-radius:999px;border:1px solid rgba(255,255,255,.14);color:#fff;font-weight:500;font-size:15px;transition:border-color 120ms cubic-bezier(.22,.8,.28,1),box-shadow 120ms cubic-bezier(.22,.8,.28,1)}
.orca-legal2 a.ol-back:hover{border-color:#32e9da;box-shadow:0 0 18px rgba(50,233,218,.25);color:#fff}
.ol-hero{position:relative;overflow:hidden;padding:clamp(56px,8vw,104px) clamp(24px,5vw,64px) clamp(28px,4vw,48px)}
.ol-hero::before{content:"";position:absolute;inset:0;background:radial-gradient(620px 380px at 85% 20%,rgba(50,233,218,.10),transparent 70%),radial-gradient(520px 360px at 10% 90%,rgba(229,0,136,.10),transparent 70%);pointer-events:none}
.ol-wrap{position:relative;max-width:820px;margin:0 auto}
.ol-kicker{display:inline-flex;align-items:center;gap:14px;margin-bottom:18px;color:#fff;font-weight:700;font-size:15px}
.ol-dash{display:flex;flex-direction:column;gap:3px;flex:none}
.ol-dash i{display:block;width:28px;height:1px;background:#32e9da;box-shadow:0 0 8px #32e9da}
.ol-dash i+i{background:#e50088;box-shadow:0 0 8px #e50088;transform:translateX(-7px)}
.orca-legal2 h1{color:#fff;font-size:clamp(40px,6vw,64px);font-weight:900;line-height:1.03;letter-spacing:-.01em;text-wrap:balance}
.ol-hl{position:relative;display:inline-block;color:#32e9da;text-shadow:0 0 18px rgba(50,233,218,.5)}
.ol-hl span[aria-hidden]{position:absolute;inset:0;transform:translate(-.07em,.07em);color:transparent;-webkit-text-stroke:1px rgba(229,0,136,.85);text-shadow:none;pointer-events:none}
.ol-hl span+span{position:relative}
.ol-card{position:relative;max-width:820px;margin:0 auto clamp(64px,8vw,104px);padding:clamp(26px,4vw,48px);border-radius:22px;background:#0a1f3d;border:1px solid rgba(255,255,255,.1);
  box-shadow:-10px 10px 0 -1px #001b3f,-10px 10px 0 0 rgba(229,0,136,.35)}
.ol-body p{margin:0 0 14px}
.ol-body p:empty{display:none}
.ol-body b,.ol-body strong{color:#fff;font-weight:700}
.ol-body span[style*="font-weight: 400"]{font-weight:400 !important}
.ol-body h2,.ol-body h3{color:#fff;font-size:clamp(21px,2.4vw,26px);font-weight:900;line-height:1.25;margin:34px 0 12px;padding-top:26px;border-top:1px solid rgba(255,255,255,.1)}
.ol-body h2:first-child,.ol-body h3:first-child{margin-top:0;padding-top:0;border-top:0}
.ol-body h2 b,.ol-body h3 b{font-weight:900}
.ol-body ul,.ol-body ol{list-style:none;margin:6px 0 16px}
.ol-body li{position:relative;padding-right:22px;margin-bottom:8px}
.ol-body li::before{content:"";position:absolute;right:2px;top:.72em;width:7px;height:7px;border-radius:50%;background:#32e9da;box-shadow:0 0 8px #32e9da}
.ol-body li:nth-child(even)::before{background:#e50088;box-shadow:0 0 8px #e50088}
.ol-body ol{counter-reset:ol}
.ol-footer{background:#00132e;border-top:1px solid rgba(255,255,255,.1);padding:48px clamp(24px,5vw,64px) 36px;color:#b9c0d0;font-size:15px}
.ol-footer__in{max-width:1180px;margin:0 auto;display:flex;flex-direction:column;gap:24px}
.ol-footer__row{display:flex;flex-wrap:wrap;gap:24px;align-items:center;justify-content:space-between}
.ol-footer img{width:104px;height:auto;display:block}
.ol-footer nav{display:flex;flex-wrap:wrap;gap:6px 24px}
.orca-legal2 .ol-footer nav a{color:#b9c0d0;padding:10px 0}
.orca-legal2 .ol-footer nav a:hover,.orca-legal2 .ol-footer nav a[aria-current]{color:#fff}
.ol-footer__rule{height:1px;background:linear-gradient(90deg,transparent,rgba(255,255,255,.18),transparent)}
.ol-footer p{font-size:14px}
.orca-legal2 .ol-footer p a{color:#b9c0d0}
@media (prefers-reduced-motion:reduce){.orca-legal2 *{transition:none !important}}
'''

LINKS = [('orca-privacy', 'https://www.orcatribe.co.il/מדיניות-פרטיות/', 'מדיניות פרטיות'),
         ('orca-terms', 'https://www.orcatribe.co.il/תנאי-שימוש/', 'תנאי שימוש'),
         ('orca-accessibility', 'https://www.orcatribe.co.il/הצהרת-נגישות/', 'נגישות האתר'),
         (None, 'https://www.orcatribe.co.il/גיוס-עובדים/', 'משרות פנויות')]
LOGO = 'https://www.orcatribe.co.il/wp-content/uploads/2026/03/Asset-1-1.svg'


def body_of(folder):
    s = open(os.path.join(ROOT, folder, 'index.html'), encoding='utf-8').read()
    m = re.search(r'<div class="orca-legal__body">(.*?)</div>\s*</main>', s, re.S) or \
        re.search(r'<div class="ol-body">(.*?)</div>\s*</article>', s, re.S)
    if not m:
        raise SystemExit('legal text not found in %s' % folder)
    return m.group(1).strip()


def page(folder, t1, hl, kicker, body):
    nav = '\n'.join('        <a href="%s"%s>%s</a>' % (u, ' aria-current="page"' if f == folder else '', n) for f, u, n in LINKS)
    title = '%s %s' % (t1, hl)
    kicker_html = ('      <span class="ol-kicker"><span class="ol-dash" aria-hidden="true"><i></i><i></i></span>%s</span>\n' % kicker) if kicker else ''
    return '''<!doctype html>
<html lang="he" dir="rtl">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>%(title)s – אורקה טרייב</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Heebo:wght@300;400;500;700;900&display=swap">
<style>
/* orcatribe legal page in the brand language (DNA system), built by tools/build_legal.py. The legal text is verbatim. */%(css)s</style>
</head>
<body>
<div class="orca-legal2">
<header class="ol-header">
  <div class="ol-header__row">
    <a href="https://www.orcatribe.co.il/" aria-label="אורקה טרייב, לדף הבית"><img src="%(logo)s" alt="אורקה טרייב" width="112" height="50"></a>
    <a class="ol-back" href="https://www.orcatribe.co.il/">לדף הבית <span aria-hidden="true">←</span></a>
  </div>
</header>
<main>
  <section class="ol-hero">
    <div class="ol-wrap">
%(kicker_html)s      <h1>%(t1)s <span class="ol-hl"><span aria-hidden="true">%(hl)s</span><span>%(hl)s</span></span></h1>
    </div>
  </section>
  <article class="ol-card">
    <div class="ol-body">
%(body)s
    </div>
  </article>
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
''' % dict(title=title, css=CSS, logo=LOGO, kicker_html=kicker_html, t1=t1, hl=hl, body=body, nav=nav)


if __name__ == '__main__':
    for folder, t1, hl, kicker in PAGES:
        body = body_of(folder)
        # the old page repeated its own title as the first heading of the text: drop only that exact duplicate
        html = page(folder, t1, hl, kicker, body)
        open(os.path.join(ROOT, folder, 'index.html'), 'w', encoding='utf-8').write(html)
        print(folder, len(body), 'chars of legal text kept')
