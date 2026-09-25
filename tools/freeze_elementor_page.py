#!/usr/bin/env python3
"""Freeze a live Elementor page into pages/<name>/index.html for the plugin's convert step.

Usage: tools/freeze_elementor_page.py <page url> <wp page id> <name>

The page's own rendered markup and its stylesheet (post-<id>.css) are copied as they
are, so the copy is exact by construction. Parts that need Elementor at runtime are
cut out and replaced by markers the plugin fills with the real Elementor element:
  - the direct parent of every form widget   -> <!--olp:form:n-->   (plugin: forms)
  - video, nav-menu, loop-carousel widgets and
    anything holding a popup link             -> <!--olp:keep:ID-->  (plugin: keep)
Prints the "keep" list to put in sites.json next to the page.
"""
import re
import sys
import urllib.request

LIVE_WIDGETS = ('video.default', 'nav-menu.default', 'loop-carousel.post', 'media-carousel.default', 'slides.default')
EL_OPEN = re.compile(r'<div class="elementor-element elementor-element-([a-z0-9]+) ([^"]*)"[^>]*>')


def get(url):
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0 orca-freeze'})
    return urllib.request.urlopen(req, timeout=30).read().decode('utf-8')


def outer_end(doc, start):
    depth = 0
    for m in re.compile(r'<div\b|</div>').finditer(doc, start):
        depth += 1 if m.group(0) == '<div' else -1
        if depth == 0:
            return m.end()
    raise ValueError('unbalanced divs from %d' % start)


def elements(doc):
    """(id, start, end, opening tag, parent id) for every Elementor element, in document order."""
    out, stack = [], []
    for m in EL_OPEN.finditer(doc):
        s, e = m.start(), outer_end(doc, m.start())
        while stack and stack[-1][2] <= s:
            stack.pop()
        parent = stack[-1][0] if stack else None
        item = (m.group(1), s, e, m.group(0), parent)
        out.append(item)
        stack.append(item)
    return out


def main(url, pid, name):
    sep = '&' if '?' in url else '?'
    h = get(url + sep + 'olp_freeze=1')
    head = re.search(r'<div data-elementor-type="(wp-page|wp-post)" data-elementor-id="%s"[^>]*>' % pid, h)
    if not head:
        sys.exit('page document %s not found at %s' % (pid, url))
    doc = h[head.start():outer_end(h, head.start())]
    els = elements(doc)
    by_id = {e[0]: e for e in els}

    cuts = {}   # id -> marker
    form_n = 0
    for eid, s, e, tag, parent in els:
        body = doc[s:e]
        wt = re.search(r'data-widget_type="([^"]+)"', tag)
        wt = wt.group(1) if wt else ''
        if wt == 'form.default':
            form_n += 1
            holder = parent or eid
            cuts[holder] = '<!--olp:form:%d-->' % form_n
        elif wt in LIVE_WIDGETS or (wt and 'popup%3Aopen' in body):
            cuts.setdefault(eid, '<!--olp:keep:%s-->' % eid)

    # outermost cuts only: a cut inside another cut goes with it
    def inside(a, b):
        return by_id[b][1] < by_id[a][1] and by_id[a][2] <= by_id[b][2]
    final = {k: v for k, v in cuts.items() if not any(inside(k, o) for o in cuts if o != k)}
    for k in sorted(final, key=lambda k: by_id[k][1], reverse=True):
        _, s, e, _, _ = by_id[k]
        doc = doc[:s] + final[k] + doc[e:]

    doc = doc.replace(head.group(0), '<div class="elementor elementor-%s olp-frozen">' % pid, 1)

    css_href = re.search(r"<link rel='stylesheet' id='elementor-post-%s-css' href='([^']+)'" % pid, h)
    css = get(css_href.group(1)) if css_href else ''
    links = ['<link rel="stylesheet" id="olp-%s" href="%s">' % (lid, href)
             for lid, href in re.findall(r"<link rel='stylesheet' id='([^']+)' href='([^']+)'", h)
             if lid.startswith(('widget-', 'e-shapes', 'swiper', 'e-swiper', 'e-animation'))]
    title = re.search(r'<title>([^<]*)</title>', h)
    page = '''<!doctype html>
<html lang="he" dir="rtl">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>%s</title>
%s
<style>
/* faithful copy of the Elementor page %s (frozen by tools/freeze_elementor_page.py): its own stylesheet and rendered markup.
   Live parts stay Elementor, placed by the plugin at the olp:keep / olp:form markers. */
%s
</style>
</head>
<body>
%s
</body>
</html>
''' % (title.group(1) if title else name, '\n'.join(links), pid, css, doc)
    import os
    root = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'pages', name)
    os.makedirs(root, exist_ok=True)
    with open(os.path.join(root, 'index.html'), 'w') as f:
        f.write(page)
    keep = [k for k, v in final.items() if v.startswith('<!--olp:keep')]
    keep.sort(key=lambda k: by_id[k][1])
    print('wrote pages/%s/index.html (%d bytes), forms %d' % (name, len(page), form_n))
    print('keep:', keep)
    print('markers:', re.findall(r'<!--olp:[a-z]+:[a-z0-9]+-->', page))


if __name__ == '__main__':
    if len(sys.argv) != 4:
        sys.exit(__doc__)
    main(sys.argv[1], sys.argv[2], sys.argv[3])
