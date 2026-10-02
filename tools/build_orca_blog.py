#!/usr/bin/env python3
"""Builds the two repo pages that dress the blog (Jonathan, 02/10/2026):

  pages/orca-blog-post/index.html  every post   (markers filled by the plugin: title, date, reading time, content)
  pages/orca-blog/index.html       /category/blog/  (marker <!--olp:posts--> becomes the article cards)

Both are assembled from the live home page's own components (head, header, contact form, footer,
scripts), like build_orca_brand.py, so the blog always shares the site's design. The plugin (1.13.0+)
renders them around WordPress posts; see "blog" in sites.json. Re-run after changing orca-home:
`python3 tools/build_orca_blog.py`.
"""
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
home = (ROOT / 'pages/orca-home/index.html').read_text(encoding='utf-8')
L = home.split('\n')
CY, MG = '#32e9da', '#e50088'
BLOG = 'https://www.orcatribe.co.il/category/blog/'


def lines(a, b):
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


def kicker(text, center=False, mb=18, href=None):
    align = 'justify-content:center;' if center else ''
    label = (f'<a href="{href}" style="color:#fff;font-weight:700;font-size:15px">{text}</a>' if href
             else f'<span style="color:#fff;font-weight:700;font-size:15px">{text}</span>')
    return (f'<span style="display:inline-flex;align-items:center;{align}gap:14px;margin-bottom:{mb}px">'
            f'<span style="display:flex;flex-direction:column;gap:3px;flex:none">'
            f'<span style="width:28px;height:1px;background:{CY};box-shadow:0 0 6px {CY}"></span>'
            f'<span style="width:28px;height:1px;background:{MG};box-shadow:0 0 6px {MG};transform:translateX(-7px)"></span></span>'
            f'{label}</span>')


def hl(word):
    return (f'<span style="position:relative;display:inline-block;color:{CY};text-shadow:0 0 18px rgba(50,233,218,.5)">'
            f'<span aria-hidden="true" class="olp-echo" data-echo="{word}" style="position:absolute;inset:0;transform:translate(-.07em,.07em);'
            f'color:transparent;-webkit-text-stroke:1px rgba(229,0,136,.85);text-shadow:none;pointer-events:none"></span>'
            f'<span style="position:relative">{word}</span></span>')


BLOG_CSS = '''
/* ---- blog (build_orca_blog.py) ---- */
.olp-article{max-width:760px;margin:0 auto;padding:clamp(48px,7vw,96px) clamp(20px,5vw,32px) clamp(56px,7vw,96px)}
.olp-article-head{display:flex;flex-direction:column;align-items:flex-start;margin-bottom:clamp(32px,4vw,48px)}
.olp-article-head h1{color:#fff !important;font-size:clamp(34px,4.6vw,54px);font-weight:900;line-height:1.08;letter-spacing:-.01em;text-wrap:balance;margin-bottom:18px}
.olp-article-meta{color:#b9c0d0;font-size:15px;display:flex;gap:10px;align-items:center}
.olp-article-meta i{width:4px;height:4px;border-radius:50%;background:#32e9da;display:inline-block}
.olp-article-body{color:#d7dce6;font-size:clamp(17px,1.4vw,19px);line-height:1.85}
.olp-article-body>*+*{margin-top:18px}
.olp-article-body h2{color:#fff !important;font-size:clamp(25px,2.8vw,32px);font-weight:900;line-height:1.2;margin-top:52px;padding-top:28px;border-top:1px solid rgba(255,255,255,.1)}
.olp-article-body h3{color:#fff !important;font-size:clamp(20px,2vw,23px);font-weight:700;line-height:1.3;margin-top:34px}
.olp-article-body p{text-wrap:pretty}
.olp-article-body strong{color:#fff;font-weight:700}
.olp-article-body a{color:#32e9da;text-decoration:underline;text-underline-offset:4px;font-weight:700}
.olp-article-body a:hover{color:#fff}
.olp-article-body ul,.olp-article-body ol{padding-right:0;list-style:none;display:flex;flex-direction:column;gap:10px}
.olp-article-body ul li{position:relative;padding-right:24px}
.olp-article-body ul li::before{content:"";position:absolute;right:2px;top:.72em;width:8px;height:8px;border-radius:50%;background:#e50088;box-shadow:0 0 8px rgba(229,0,136,.6)}
.olp-article-body ol{counter-reset:olp}
.olp-article-body ol li{position:relative;padding-right:34px;counter-increment:olp}
.olp-article-body ol li::before{content:counter(olp);position:absolute;right:0;top:0;font:900 18px/1.85 "Figtree",sans-serif;color:#32e9da}
.olp-article-body blockquote{border-right:3px solid #e50088;padding:6px 20px 6px 0;color:#fff;font-size:1.1em}
.olp-article-body table{width:100%;border-collapse:collapse;font-size:16px;display:block;overflow-x:auto}
.olp-article-body th,.olp-article-body td{border-bottom:1px solid rgba(255,255,255,.12);padding:10px 12px;text-align:right}
.olp-article-body th{color:#fff}
.olp-article-body img{max-width:100%;height:auto;border-radius:18px}
.olp-article-body .wp-block-media-text,.olp-article-body .olp-side{display:grid;grid-template-columns:minmax(0,1fr) minmax(0,1fr);gap:clamp(20px,3vw,36px);align-items:center;margin:40px 0}
.olp-article-body .wp-block-media-text.has-media-on-the-right,.olp-article-body .olp-side.olp-side-flip{direction:ltr}
.olp-article-body .wp-block-media-text.has-media-on-the-right>*,.olp-article-body .olp-side.olp-side-flip>*{direction:rtl}
.olp-article-body .wp-block-media-text__media,.olp-article-body .olp-side figure{margin:0}
.olp-article-body .wp-block-media-text__media img,.olp-article-body .olp-side img{width:100%;height:auto;aspect-ratio:4/3;object-fit:cover;border-radius:22px;box-shadow:0 0 0 1px rgba(255,255,255,.08),0 18px 48px rgba(0,0,0,.35),0 0 32px rgba(50,233,218,.10)}
.olp-article-body .wp-block-media-text__content{padding:0 !important}
.olp-article-body .wp-block-media-text__content>*+*{margin-top:14px}
.olp-article-body figure.wp-block-image{margin:36px 0}
.olp-article-body figure.wp-block-image img{border-radius:22px}
.olp-article-body figcaption{color:#8f98ab;font-size:14px;text-align:center;margin-top:10px}
@media (max-width:760px){.olp-article-body .wp-block-media-text,.olp-article-body .olp-side{grid-template-columns:1fr}.olp-article-body .wp-block-media-text__media,.olp-article-body .olp-side figure{order:-1}}
.olp-back{display:inline-flex;align-items:center;min-height:44px;margin-top:40px;color:#32e9da;font-weight:700}
.olp-posts{display:grid;grid-template-columns:repeat(auto-fill,minmax(min(100%,330px),1fr));gap:24px}
.olp-post-card{display:flex;flex-direction:column;gap:12px;padding:28px;border-radius:24px;background:rgba(255,255,255,.04);border:1px solid rgba(255,255,255,.1);color:#fff;transition:border-color 200ms,transform 200ms}
.olp-post-card:hover{border-color:#32e9da;transform:translateY(-3px);color:#fff}
.olp-post-card img{width:100%;aspect-ratio:16/9;object-fit:cover;border-radius:16px}
.olp-post-card h2{color:#fff !important;font-size:clamp(22px,2.2vw,26px);font-weight:900;line-height:1.2;text-wrap:balance}
.olp-post-card p{color:#b9c0d0 !important;font-size:16px;line-height:1.65}
.olp-post-date{color:#b9c0d0;font-size:14px}
.olp-post-more{margin-top:auto;padding-top:6px;color:#32e9da;font-weight:700}
.olp-posts-empty{color:#b9c0d0;text-align:center}
'''

# ---------- head + header (home, shared) ----------
head_end = find('</header>')
top = lines(1, head_end)
top = re.sub(r'<title>.*?</title>', '<title>הבלוג של אורקה טרייב</title>', top, count=1)
top = re.sub(r'\.elementor-114 ', '.elementor ', top)
for a in ('#who', '#services-grid', '#guide', '#recs', '#contact', '#testimonials'):
    top = top.replace(f'href="{a}"', f'href="https://www.orcatribe.co.il/{a}"')
top = top.replace('</style>\n</head>', BLOG_CSS + '</style>\n</head>', 1)

# ---------- contact form (home, as is; the plugin fills <!--olp:form:1--> with the home page's form) ----------
contact_start = find('<section id="contact"')
contact = lines(contact_start, section_end(contact_start))
assert '<!--olp:form:1-->' in contact

# ---------- footer + scripts ----------
tail = lines(find('</main>'), find('</body>') - 1)
tail = re.sub(r'<script type="application/ld\+json">.*?</script>\n?', '', tail, flags=re.S)

post = f'''<section data-screen-label="Article" style="position:relative">
  <div style="position:absolute;inset:0;background:radial-gradient(700px 420px at 85% 0%,rgba(50,233,218,.09),transparent 70%);pointer-events:none"></div>
  <article class="olp-article" style="position:relative">
    <header class="olp-article-head">
      {kicker('הבלוג של אורקה טרייב', href=BLOG)}
      <h1><!--olp:post-title--></h1>
      <div class="olp-article-meta"><span><!--olp:post-date--></span><i></i><span><!--olp:post-reading--></span></div>
    </header>
    <div class="olp-article-body">
<!--olp:post-content-->
    </div>
    <a class="olp-back" href="{BLOG}">← לכל המאמרים בבלוג</a>
  </article>
</section>'''

index = f'''<section data-screen-label="Blog hero" style="position:relative;overflow:hidden;padding:clamp(64px,8vw,104px) clamp(20px,5vw,64px) clamp(32px,4vw,48px)">
  <div style="position:absolute;inset:0;background:radial-gradient(700px 400px at 50% 0%,rgba(229,0,136,.14),transparent 70%);pointer-events:none"></div>
  <div style="position:relative;max-width:780px;margin:0 auto;display:flex;flex-direction:column;align-items:center;text-align:center">
    {kicker('בלוג', center=True)}
    <h1 style="font-size:clamp(38px,5vw,60px);font-weight:900;line-height:1.05;letter-spacing:-.01em;margin-bottom:18px;text-wrap:balance">הבלוג של {hl('אורקה טרייב')}</h1>
    <p style="color:#b9c0d0;font-size:clamp(17px,1.5vw,19px);line-height:1.65;max-width:60ch">מאמרים על שיווק לעסקים, תוכן ויראלי וקמפיינים ממומנים, מתוך העבודה שלנו בשטח.</p>
  </div>
</section>
<section data-screen-label="Posts" style="position:relative;padding:0 clamp(20px,5vw,64px) clamp(72px,8vw,112px)">
  <div style="max-width:1180px;margin:0 auto">
<!--olp:posts-->
  </div>
</section>'''

for name, body in (('orca-blog-post', post), ('orca-blog', index)):
    page = '\n'.join([top, '', '<main>', body, '', contact, tail]) + '\n</body>\n</html>\n'
    out = ROOT / 'pages' / name / 'index.html'
    out.parent.mkdir(exist_ok=True)
    out.write_text(page, encoding='utf-8')
    print('written', out, len(page))
