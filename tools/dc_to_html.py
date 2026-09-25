#!/usr/bin/env python3
"""Convert a Claude Design export (.dc.html) into a plain page for pages/<name>/index.html.

Usage: tools/dc_to_html.py <file.dc.html> <out index.html> [--drop-section LABEL ...] [--form]

What it handles (the parts of the .dc format a browser can't read on its own):
  - <helmet> styles and font links are kept; design-system bundle/scripts are dropped
  - style-hover / style-active / style-focus attributes become CSS classes with !important rules
  - <sc-if value="{{ isDesktop }}"> / isMobile / menuOpen become responsive blocks (1080px breakpoint)
  - onClick="{{ toggleMenu | closeMenu | next | prev }}", ref="{{ trackRef }}" become data-dc hooks
    served by a small vanilla script; {{ stickyPos }} becomes sticky with a <1000px static override
  - {{ helix }} becomes an empty mount that the script fills (same dots, rungs and timing)
  - --form: the design's <form> is replaced by <!--olp:form:1--> (the real Elementor form)
  - --drop-section LABEL removes <section data-screen-label="LABEL"> (placeholder sections)
  - image URLs pointing at this repo's pages/<x>/images/ become relative images/
"""
import re
import sys

DESK = 1080


def outer_end(s, start, tag):
    depth = 0
    for m in re.compile(r'<%s\b|</%s>' % (tag, tag)).finditer(s, start):
        depth += 1 if not m.group(0).startswith('</') else -1
        if depth == 0:
            return m.end()
    raise ValueError('unbalanced <%s> at %d' % (tag, start))


def main(src, out, drop, with_form):
    s = open(src, encoding='utf-8').read()
    helmet = re.search(r'<helmet>(.*?)</helmet>', s, re.S).group(1)
    body = s[s.index('</helmet>') + len('</helmet>'):s.rindex('</x-dc>')]

    styles = '\n'.join(re.findall(r'<style>(.*?)</style>', helmet, re.S))
    fonts = [l for l in re.findall(r'<link[^>]+>', helmet) if 'fonts.googleapis' in l]

    for label in drop:
        m = re.search(r'<section[^>]*data-screen-label="%s"' % re.escape(label), body)
        if m:
            body = body[:m.start()] + body[outer_end(body, m.start(), 'section'):]

    if with_form:
        i = body.index('<form')
        body = body[:i] + '<!--olp:form:1-->' + body[outer_end(body, i, 'form'):]

    # responsive conditionals
    body = re.sub(r'<sc-if value="\{\{ isDesktop \}\}"[^>]*>', '<div class="dc-desk">', body)
    body = re.sub(r'<sc-if value="\{\{ isMobile \}\}"[^>]*>', '<div class="dc-mob">', body)
    body = re.sub(r'<sc-if value="\{\{ menuOpen \}\}"[^>]*>', '<div class="dc-menu" hidden>', body)
    body = body.replace('</sc-if>', '</div>')

    body = body.replace('onClick="{{ toggleMenu }}"', 'data-dc="toggle"')
    body = body.replace('onClick="{{ closeMenu }}"', 'data-dc="close"')
    body = body.replace('onClick="{{ next }}"', 'data-dc="next"')
    body = body.replace('onClick="{{ prev }}"', 'data-dc="prev"')
    body = body.replace('ref="{{ trackRef }}"', 'data-dc-track')
    body = body.replace('onSubmit="{{ noSubmit }}"', '')
    body = body.replace('{{ helix }}', '<div data-dc-helix></div>')
    # {{ stickyPos }} = sticky only from 1000px up: tag exactly the elements that used it
    body = re.sub(r'<([a-zA-Z0-9-]+)([^>]*?)style="([^"]*?)position:\{\{ stickyPos \}\}',
                  lambda m: '<%s class="dc-sticky"%sstyle="%sposition:sticky' % (m.group(1), m.group(2), m.group(3)), body)

    # state styles -> classes
    rules, n = [], [0]

    def state(m):
        tag = m.group(0)
        found = re.findall(r'style-(hover|active|focus)="([^"]*)"', tag)
        if not found:
            return tag
        n[0] += 1
        cls = 'dcs%d' % n[0]
        for kind, css in found:
            decl = ';'.join(d.strip() + ' !important' for d in css.split(';') if d.strip())
            sel = {'hover': ':hover', 'active': ':active', 'focus': ':focus'}[kind]
            rules.append('.%s%s{%s}' % (cls, sel, decl))
        tag = re.sub(r'\s*style-(hover|active|focus)="[^"]*"', '', tag)
        if 'class="' in tag:
            tag = tag.replace('class="', 'class="%s ' % cls, 1)
        else:
            tag = re.sub(r'^<([a-zA-Z0-9-]+)', r'<\1 class="%s"' % cls, tag, count=1)
        return tag

    body = re.sub(r'<[a-zA-Z][^>]*\bstyle-(?:hover|active|focus)=[^>]*>', state, body)

    body = re.sub(r'https://raw\.githubusercontent\.com/orcatribeltd-glitch/orca-landing-pages/[0-9a-f]+/pages/[a-z0-9-]+/images/', 'images/', body)

    leftovers = re.findall(r'\{\{[^}]*\}\}|<sc-if|style-hover', body)
    if leftovers:
        sys.exit('unconverted pieces left: %s' % sorted(set(leftovers)))

    css = styles + '''
/* converted from Claude Design by tools/dc_to_html.py */
.dc-desk{display:contents}.dc-mob{display:none}
@media (max-width:%dpx){.dc-desk{display:none}.dc-mob{display:contents}}
.dc-menu[hidden]{display:none !important}
@media (min-width:%dpx){.dc-menu{display:none !important}}
@media (max-width:999px){.dc-sticky{position:static !important}}
''' % (DESK - 1, DESK) + '\n'.join(rules)

    script = r'''<script>
(function(){
  var menu=document.querySelector('.dc-menu');
  document.addEventListener('click',function(e){
    var t=e.target.closest('[data-dc]'); if(!t) return;
    var a=t.getAttribute('data-dc'), track=document.querySelector('[data-dc-track]');
    if(a==='toggle'&&menu){menu.hidden=!menu.hidden;}
    if(a==='close'&&menu){menu.hidden=true;}
    if(a==='next'&&track){track.scrollBy({left:-284,behavior:'smooth'});}
    if(a==='prev'&&track){track.scrollBy({left:284,behavior:'smooth'});}
  });
  var mount=document.querySelector('[data-dc-helix]'); if(!mount) return;
  var N=60,T=4.2,row=document.createElement('div');
  row.style.cssText='display:flex;height:100%;padding:0 2vw';
  for(var i=0;i<N;i++){
    var d=-(i/N)*T*1.75+'s',col=document.createElement('div');
    col.style.cssText='position:relative;flex:1 1 0;height:100%';
    var rung=document.createElement('span');
    rung.style.cssText='position:absolute;left:50%;top:50%;width:1px;height:144px;margin-top:-72px;background:linear-gradient(180deg,rgba(50,233,218,.55),rgba(229,0,136,.55));animation:orcaRung '+T+'s linear '+d+' infinite';
    col.appendChild(rung);
    [['#32e9da','orcaA'],['#e50088','orcaB']].forEach(function(p){
      var dot=document.createElement('span');
      dot.style.cssText='position:absolute;left:50%;top:50%;width:8px;height:8px;margin:-4px;border-radius:50%;background:'+p[0]+';box-shadow:0 0 10px '+p[0]+';animation:'+p[1]+' '+T+'s ease-in-out '+d+' infinite';
      col.appendChild(dot);
    });
    row.appendChild(col);
  }
  mount.style.height='100%'; mount.appendChild(row);
})();
</script>'''

    title = re.search(r'<title>(.*?)</title>', s)
    page = '''<!doctype html>
<html lang="he" dir="rtl">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>%s</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
%s
<style>
%s
</style>
</head>
<body>
<div class="orca-dc" dir="rtl">
%s
</div>
%s
</body>
</html>
''' % (title.group(1) if title else 'אורקה טרייב – סוכנות שיווק', '\n'.join(fonts), css, body.strip(), script)
    open(out, 'w', encoding='utf-8').write(page)
    print('wrote %s: %d bytes, %d state classes, sections %s' % (out, len(page), n[0], re.findall(r'data-screen-label="([^"]+)"', body)))


if __name__ == '__main__':
    args = sys.argv[1:]
    if len(args) < 2:
        sys.exit(__doc__)
    drop, form = [], False
    rest = args[2:]
    while rest:
        a = rest.pop(0)
        if a == '--drop-section':
            drop.append(rest.pop(0))
        elif a == '--form':
            form = True
    main(args[0], args[1], drop, form)
