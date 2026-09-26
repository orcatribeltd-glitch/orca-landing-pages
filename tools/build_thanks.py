#!/usr/bin/env python3
"""Build the orcatribe thank-you page (/ty/) in the brand language, with the two free guides to pick and watch at once.

Design: Obsidian 04 Knowledge/02 Brand & Design/Orca Tribe — Brand Language (DNA system).md, same family as the legal pages.
The Stardust book and the goldfish cover are taken from the home page (pages/orca-home), so both pages stay in step.
Copy is the page's own ("קיבלנו את הפרטים שלך…") and the guides' own lines from the home page.

Usage: tools/build_thanks.py <out folder under pages/> [--stardust YOUTUBE_ID] [--goldfish YOUTUBE_ID]
A guide without a video id opens a placeholder, so the page must not go live (orca-thanks) until both ids are set.
"""
import os
import re
import shutil
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from build_legal import CSS as LEGAL_CSS, LINKS, LOGO  # noqa: E402

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'pages')


def outer_div(s, start):
    depth = 0
    for m in re.compile(r'<div\b|</div>').finditer(s, start):
        depth += 1 if m.group(0) == '<div' else -1
        if depth == 0:
            return s[start:m.end()]
    raise SystemExit('unbalanced div at %d' % start)


def stardust_book():
    home = open(os.path.join(ROOT, 'orca-home', 'index.html'), encoding='utf-8').read()
    i = home.find('width:236px;height:320px')
    if i < 0:
        raise SystemExit('Stardust book not found on the home page')
    book = outer_div(home, home.rfind('<div', 0, i))
    # the home card squeezes and tilts it inline; here a class drives size, tilt and float
    return re.sub(r'^<div style="[^"]*"', '<div class="ty-book"', book, count=1)


CSS = LEGAL_CSS + '''
/* thank-you page: hero + pick-a-guide, built by tools/build_thanks.py */
.ty-hero{position:relative;overflow:hidden;text-align:center;padding:clamp(56px,8vw,96px) clamp(20px,5vw,64px) clamp(24px,4vw,40px)}
.ty-hero::before{content:"";position:absolute;inset:0;background:radial-gradient(560px 340px at 50% 0%,rgba(50,233,218,.14),transparent 70%);pointer-events:none}
.ty-check{position:relative;display:block;width:88px;height:88px;margin:0 auto 26px;filter:drop-shadow(0 0 16px rgba(50,233,218,.55))}
.ty-check circle{fill:none;stroke:#32e9da;stroke-width:2.5;stroke-dasharray:252;stroke-dashoffset:252;animation:tyDraw 900ms cubic-bezier(.22,.8,.28,1) 150ms forwards}
.ty-check path{fill:none;stroke:#fff;stroke-width:4;stroke-linecap:round;stroke-linejoin:round;stroke-dasharray:60;stroke-dashoffset:60;animation:tyDraw 500ms cubic-bezier(.22,.8,.28,1) 800ms forwards}
@keyframes tyDraw{to{stroke-dashoffset:0}}
.orca-legal2 .ty-hero h1{position:relative;font-size:clamp(38px,6vw,64px)}
.orca-legal2 .ty-sub{position:relative;max-width:560px;margin:18px auto 0;color:#b9c0d0;font-size:clamp(17px,1.8vw,19px);text-wrap:balance}

.ty-pick{position:relative;padding:clamp(40px,6vw,72px) clamp(20px,5vw,64px) clamp(72px,9vw,120px)}
.ty-pick::before{content:"";position:absolute;inset:0;background:radial-gradient(520px 360px at 12% 70%,rgba(229,0,136,.10),transparent 70%),radial-gradient(520px 360px at 88% 40%,rgba(50,233,218,.08),transparent 70%);pointer-events:none}
.ty-pick__head{position:relative;text-align:center;margin-bottom:clamp(30px,4vw,46px)}
.ty-pick__head .ol-kicker{margin-bottom:14px}
.orca-legal2 .ty-pick__head h2{color:#fff;font-size:clamp(30px,4.2vw,46px);font-weight:900;line-height:1.1;letter-spacing:-.01em;text-wrap:balance}

.ty-choices{position:relative;max-width:1080px;margin:0 auto;display:grid;grid-template-columns:1fr auto 1fr;align-items:stretch;gap:clamp(16px,2.4vw,28px)}
.ty-or{align-self:center;display:grid;place-items:center;width:58px;height:58px;border-radius:50%;background:#001b3f;border:1px solid rgba(255,255,255,.18);color:#fff;font-weight:900;font-size:18px;box-shadow:0 0 0 6px rgba(0,27,63,.9),0 0 26px rgba(50,233,218,.25)}
.ty-card{position:relative;display:flex;flex-direction:column;border-radius:24px;background:rgba(255,255,255,.04);border:1px solid rgba(255,255,255,.1);overflow:hidden;cursor:pointer;
  transition:transform 220ms cubic-bezier(.22,.8,.28,1),border-color 220ms,box-shadow 220ms}
.ty-card:hover,.ty-card:focus-within{transform:translateY(-6px)}
.ty-card--cyan:hover,.ty-card--cyan:focus-within{border-color:rgba(50,233,218,.6);box-shadow:0 18px 50px rgba(0,0,0,.35),0 0 34px rgba(50,233,218,.22)}
.ty-card--pink:hover,.ty-card--pink:focus-within{border-color:rgba(229,0,136,.6);box-shadow:0 18px 50px rgba(0,0,0,.35),0 0 34px rgba(229,0,136,.25)}
.ty-stage{position:relative;height:clamp(270px,30vw,330px);display:grid;place-items:center;overflow:hidden;perspective:1200px;border-bottom:1px solid rgba(255,255,255,.1)}
.ty-card--cyan .ty-stage{background:radial-gradient(closest-side,rgba(50,233,218,.18),transparent)}
.ty-card--pink .ty-stage{background:radial-gradient(closest-side,rgba(229,0,136,.2),transparent)}
.ty-float{animation:tyFloat 5.5s ease-in-out infinite}
.ty-card--pink .ty-float{animation-delay:-2.7s}
@keyframes tyFloat{0%,100%{transform:translateY(-6px)}50%{transform:translateY(8px)}}
.ty-book{position:relative;width:236px;height:320px;transform:scale(.9) rotateY(22deg) rotateX(4deg);transform-style:preserve-3d;transition:transform 420ms cubic-bezier(.22,.8,.28,1)}
.ty-card:hover .ty-book{transform:scale(.94) rotateY(8deg) rotateX(2deg)}
/* the WordPress theme sizes every img (height:auto, max-width:100%); the cover keeps its own size */
.orca-legal2 img.ty-cover{display:block;height:clamp(236px,26vw,280px) !important;width:auto !important;max-width:none !important;filter:drop-shadow(-18px 22px 36px rgba(0,0,0,.6));transform:rotate(-3deg);transition:transform 420ms cubic-bezier(.22,.8,.28,1)}
.orca-legal2 .ty-card:hover img.ty-cover{transform:rotate(0) scale(1.04)}
.ty-sticker{position:absolute;top:20px;right:18px;z-index:2;display:inline-flex;align-items:center;gap:7px;padding:9px 16px;border-radius:999px;background:#e50088;color:#fff;font-weight:900;font-size:15px;line-height:1;transform:rotate(-7deg);box-shadow:-5px 5px 0 -1px #0a1f3d,-5px 5px 0 0 #32e9da,0 0 24px rgba(229,0,136,.6)}
.ty-play{position:absolute;left:50%;top:50%;z-index:3;width:74px;height:74px;margin:-37px 0 0 -37px;border-radius:50%;display:grid;place-items:center;background:rgba(0,19,46,.55);border:1px solid rgba(255,255,255,.35);backdrop-filter:blur(6px);-webkit-backdrop-filter:blur(6px);
  opacity:0;transform:scale(.8);transition:opacity 220ms,transform 220ms cubic-bezier(.22,.8,.28,1)}
.ty-card:hover .ty-play{opacity:1;transform:scale(1)}
.ty-play svg{width:26px;height:26px;margin-left:4px;fill:#fff}
.ty-body{flex:1;display:flex;flex-direction:column;align-items:flex-start;gap:12px;padding:26px 26px 28px}
.ty-tag{display:inline-flex;font-size:14px;font-weight:700;padding:5px 12px;border-radius:999px}
.ty-card--cyan .ty-tag{color:#32e9da;border:1px solid rgba(50,233,218,.35)}
.ty-card--pink .ty-tag{color:#e50088;border:1px solid rgba(229,0,136,.4)}
.orca-legal2 .ty-body h3{color:#fff;font-size:clamp(23px,2.4vw,27px);font-weight:900;line-height:1.15;text-wrap:balance}
.ty-body p{color:#b9c0d0;font-size:16px;line-height:1.65;text-wrap:pretty}
.ty-body p b{color:#fff}
.ty-mark{color:#fff;font-weight:700;background:linear-gradient(transparent 55%,rgba(50,233,218,.35) 55%);padding:0 2px}
.ty-under{text-decoration:underline;text-decoration-color:#e50088;text-decoration-thickness:2px;text-underline-offset:6px}
.orca-legal2 button.ty-go{margin-top:auto;display:inline-flex;align-items:center;gap:10px;min-height:54px;padding:0 28px;border-radius:999px;border:0;font:inherit;font-weight:700;font-size:17px;color:#001b3f;cursor:pointer;
  transition:transform 160ms cubic-bezier(.22,.8,.28,1),box-shadow 160ms}
.ty-card--cyan .ty-go{background:#32e9da;box-shadow:0 0 22px rgba(50,233,218,.45)}
.ty-card--pink .ty-go{background:#e50088;color:#fff;box-shadow:0 0 22px rgba(229,0,136,.5)}
.ty-go svg{width:14px;height:14px;fill:currentColor}
.ty-go:hover{transform:translateY(-2px)}
.ty-go:focus-visible{outline:2px solid #fff;outline-offset:3px}

.ty-modal{width:min(1040px,94vw);max-width:none;max-height:94vh;padding:0;border:1px solid rgba(255,255,255,.14);border-radius:22px;background:#0a1f3d;color:#fff;box-shadow:0 30px 90px rgba(0,0,0,.6),0 0 40px rgba(50,233,218,.15);overflow:hidden;direction:rtl;font-family:"Heebo",system-ui,sans-serif}
.ty-modal::backdrop{background:rgba(0,10,26,.82);backdrop-filter:blur(6px);-webkit-backdrop-filter:blur(6px)}
.ty-modal[open]{animation:tyPop 260ms cubic-bezier(.22,.8,.28,1)}
@keyframes tyPop{from{opacity:0;transform:translateY(14px) scale(.98)}to{opacity:1;transform:none}}
.ty-modal__bar{display:flex;align-items:center;justify-content:space-between;gap:16px;padding:14px 18px 14px 14px;border-bottom:1px solid rgba(255,255,255,.1)}
.ty-modal__title{font-weight:900;font-size:clamp(17px,2vw,20px);line-height:1.3}
.ty-x{flex:none;width:44px;height:44px;border-radius:50%;border:1px solid rgba(255,255,255,.18);background:transparent;color:#fff;font-size:22px;line-height:1;cursor:pointer}
.ty-x:hover{border-color:#32e9da;box-shadow:0 0 16px rgba(50,233,218,.3)}
.ty-frame{position:relative;aspect-ratio:16/9;background:#000}
.ty-frame iframe{position:absolute;inset:0;width:100%;height:100%;border:0}
.ty-soon{position:absolute;inset:0;display:grid;place-items:center;text-align:center;padding:24px;color:#b9c0d0;font-size:17px;background:radial-gradient(closest-side,rgba(50,233,218,.12),transparent)}
.ty-modal__foot{display:flex;flex-wrap:wrap;align-items:center;justify-content:space-between;gap:12px;padding:14px 18px;color:#b9c0d0;font-size:15px}
.ty-switch{display:inline-flex;align-items:center;gap:8px;min-height:44px;padding:0 18px;border-radius:999px;border:1px solid rgba(255,255,255,.18);background:transparent;color:#fff;font:inherit;font-weight:700;font-size:15px;cursor:pointer}
.ty-switch:hover{border-color:#e50088;box-shadow:0 0 16px rgba(229,0,136,.3)}

@media (max-width:860px){
  .ty-choices{grid-template-columns:1fr;max-width:520px}
  .ty-or{justify-self:center;margin:-6px 0}
  .ty-play{display:none}
  .ty-book{transform:scale(.82) rotateY(18deg) rotateX(4deg)}
}
@media (prefers-reduced-motion:reduce){.ty-float,.ty-modal[open]{animation:none}.ty-check circle,.ty-check path{animation:none;stroke-dashoffset:0}}
'''

PLAY = '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M6 4.5v15a1 1 0 0 0 1.5.86l12.4-7.5a1 1 0 0 0 0-1.72L7.5 3.64A1 1 0 0 0 6 4.5z"/></svg>'
FLAME = ('<svg viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="#fff" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">'
         '<path d="M8.5 14.5A2.5 2.5 0 0 0 11 12c0-1.38-.5-2-1-3-1.07-2.14-.22-4.05 2-6 .5 2.5 2 4.9 4 6.5 2 1.6 3 3.5 3 5.5a7 7 0 1 1-14 0c0-1.15.43-2.29 1-3a2.5 2.5 0 0 0 2.5 2.5z"></path></svg>')


def build(out, yt):
    book = stardust_book()
    nav = '\n'.join('        <a href="%s">%s</a>' % (u, n) for f, u, n in LINKS)
    html = '''<!doctype html>
<html lang="he" dir="rtl">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>קיבלנו את הפרטים שלך – אורקה טרייב</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Heebo:wght@300;400;500;700;900&display=swap">
<style>
/* orcatribe thank-you page in the brand language, built by tools/build_thanks.py */%(css)s</style>
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
  <section class="ty-hero">
    <svg class="ty-check" viewBox="0 0 88 88" aria-hidden="true"><circle cx="44" cy="44" r="40"/><path d="M27 45.5l11.5 11L61 33"/></svg>
    <h1>קיבלנו את <span class="ol-hl"><span aria-hidden="true">הפרטים</span><span>הפרטים</span></span> שלך</h1>
    <p class="ty-sub">חוזרים אליך בקרוב לשיחה קצרה, לפני שנקבע לך שיחת ייעוץ ללא עלות.</p>
  </section>

  <section class="ty-pick" aria-labelledby="ty-pick-h">
    <div class="ty-pick__head">
      <span class="ol-kicker"><span class="ol-dash" aria-hidden="true"><i></i><i></i></span>הדרכות במתנה</span>
      <h2 id="ty-pick-h">בינתיים, בחר הדרכה <span class="ol-hl"><span aria-hidden="true">לצפייה מיידית</span><span>לצפייה מיידית</span></span></h2>
    </div>
    <div class="ty-choices">
      <article class="ty-card ty-card--cyan" data-guide="stardust" data-yt="%(yt_stardust)s" data-title="אבק כוכבים: איך יוצרים תוכן שמגיע למאות אלפי צפיות">
        <div class="ty-stage">
          <span class="ty-sticker">%(flame)sחדש מהתנור!</span>
          <div class="ty-float">%(book)s</div>
          <span class="ty-play" aria-hidden="true">%(play)s</span>
        </div>
        <div class="ty-body">
          <span class="ty-tag">הדרכה · אבק כוכבים</span>
          <h3>איך יוצרים תוכן שמגיע למאות אלפי צפיות ובונה מותג חזק ברשתות</h3>
          <p>מייצר שיח, <span class="ty-mark">מאות תגובות ושיתופים</span> וגורם לקהל איכותי לעקוב אחריך, <b>בלי להשקיע <span class="ty-under">שקל אחד</span> על פרסום ממומן!</b></p>
          <button type="button" class="ty-go">%(play)sלצפייה עכשיו</button>
        </div>
      </article>
      <span class="ty-or" aria-hidden="true">או</span>
      <article class="ty-card ty-card--pink" data-guide="goldfish" data-yt="%(yt_goldfish)s" data-title="פסיכולוגיית ״דג הזהב״">
        <div class="ty-stage">
          <div class="ty-float"><img class="ty-cover" src="images/guide-goldfish.webp" alt="כריכת ההדרכה: פסיכולוגיית דג הזהב" width="610" height="913"></div>
          <span class="ty-play" aria-hidden="true">%(play)s</span>
        </div>
        <div class="ty-body">
          <span class="ty-tag">הדרכה · דג הזהב</span>
          <h3>פסיכולוגיית ״דג הזהב״</h3>
          <p>כדי לשווק טוב ולהביא לקוחות מדויקים, אתה צריך לחשוב בדיוק כמו הלקוח הפוטנציאלי שלך. בהדרכה תלמד איך לדבר בשפה של <span class="ty-mark">״דג זהב״ עסיסי</span>, כזה שאתה רוצה שיהפוך ללקוח שלך.</p>
          <button type="button" class="ty-go">%(play)sלצפייה עכשיו</button>
        </div>
      </article>
    </div>
  </section>
</main>

<dialog class="ty-modal" aria-labelledby="ty-modal-title">
  <div class="ty-modal__bar">
    <span class="ty-modal__title" id="ty-modal-title"></span>
    <button type="button" class="ty-x" data-close aria-label="סגירה">×</button>
  </div>
  <div class="ty-frame"></div>
  <div class="ty-modal__foot">
    <span>נהנית? יש עוד אחת מחכה לך</span>
    <button type="button" class="ty-switch" data-switch></button>
  </div>
</dialog>

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
<script>
(function(){
  var modal=document.querySelector('.ty-modal'); if(!modal) return;
  var frame=modal.querySelector('.ty-frame'), title=modal.querySelector('.ty-modal__title'), sw=modal.querySelector('[data-switch]');
  var cards=[].slice.call(document.querySelectorAll('.ty-card')), current=null;
  function play(card){
    current=card;
    var id=(card.getAttribute('data-yt')||'').trim();
    title.textContent=card.getAttribute('data-title');
    frame.innerHTML='';
    if(id){
      var f=document.createElement('iframe');
      f.src='https://www.youtube-nocookie.com/embed/'+encodeURIComponent(id)+'?autoplay=1&rel=0&modestbranding=1&playsinline=1';
      f.title=card.getAttribute('data-title');
      f.allow='autoplay; encrypted-media; picture-in-picture; fullscreen';
      f.allowFullscreen=true;
      frame.appendChild(f);
    } else {
      frame.innerHTML='<div class="ty-soon">הסרטון של ההדרכה הזו עוד לא חובר</div>';
    }
    var other=cards.filter(function(c){return c!==card;})[0];
    sw.textContent=other?('לצפייה ב'+(other.getAttribute('data-guide')==='stardust'?'״אבק כוכבים״':'״דג הזהב״')+' ←'):'';
    if(!modal.open){ if(modal.showModal) modal.showModal(); else modal.setAttribute('open',''); }
  }
  function close(){ frame.innerHTML=''; if(modal.open){ modal.close ? modal.close() : modal.removeAttribute('open'); } }
  cards.forEach(function(card){ card.addEventListener('click',function(){ play(card); }); });
  sw.addEventListener('click',function(){ var other=cards.filter(function(c){return c!==current;})[0]; if(other) play(other); });
  modal.addEventListener('click',function(e){ if(e.target===modal||e.target.closest('[data-close]')) close(); });
  modal.addEventListener('close',function(){ frame.innerHTML=''; });
})();
</script>
</body>
</html>
''' % dict(css=CSS, logo=LOGO, nav=nav, book=book, play=PLAY, flame=FLAME,
           yt_stardust=yt.get('stardust', ''), yt_goldfish=yt.get('goldfish', ''))
    dest = os.path.join(ROOT, out)
    os.makedirs(os.path.join(dest, 'images'), exist_ok=True)
    shutil.copyfile(os.path.join(ROOT, 'orca-home', 'images', 'guide-goldfish.webp'), os.path.join(dest, 'images', 'guide-goldfish.webp'))
    open(os.path.join(dest, 'index.html'), 'w', encoding='utf-8').write(html)
    missing = [k for k in ('stardust', 'goldfish') if not yt.get(k)]
    print('wrote pages/%s/index.html (%d bytes)%s' % (out, len(html), (', no video yet for: ' + ', '.join(missing)) if missing else ''))


if __name__ == '__main__':
    args = sys.argv[1:]
    if not args:
        sys.exit(__doc__)
    out, yt = args[0], {}
    rest = args[1:]
    while rest:
        k = rest.pop(0)
        if k in ('--stardust', '--goldfish'):
            v = rest.pop(0)
            if not re.fullmatch(r'[A-Za-z0-9_-]{11}', v):
                sys.exit('not a YouTube id: %s' % v)
            yt[k[2:]] = v
    if out == 'orca-thanks' and len(yt) < 2:
        sys.exit('the live thank-you page needs both video ids (--stardust and --goldfish)')
    build(out, yt)
