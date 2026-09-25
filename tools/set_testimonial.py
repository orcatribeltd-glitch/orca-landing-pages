#!/usr/bin/env python3
"""Fill testimonial card N of the orca home page with a real YouTube video (click-to-load).

Usage: tools/set_testimonial.py <page index.html> <card number 1..> <youtube url or id> "<name>" "<field>"
The card shows YouTube's own vertical thumbnail (lazy) and loads the player only on click.
"""
import re, sys, urllib.request


def best_thumb(vid):
    """YouTube makes some sizes only after a first request, and answers a missing one with a grey 120x90 image: check real sizes."""
    for f in ('oardefault', 'oar2', 'maxresdefault', 'hq720', 'hqdefault'):
        try:
            r = urllib.request.urlopen('https://i.ytimg.com/vi/%s/%s.jpg' % (vid, f), timeout=10)
            if r.status == 200 and len(r.read()) > 5000:
                return f
        except Exception:
            pass
    return 'hqdefault'

def yt_id(u):
    m = re.search(r'(?:shorts/|v=|youtu\.be/|embed/)([A-Za-z0-9_-]{11})', u)
    return m.group(1) if m else (u if re.fullmatch(r'[A-Za-z0-9_-]{11}', u) else None)

def main(path, n, url, name, field):
    s = open(path, encoding='utf-8').read()
    vid = yt_id(url)
    if not vid:
        sys.exit('no YouTube id in %s' % url)
    label = 'VIDEO %02d' % int(n)
    li = s.find('>' + label + '</div>')
    if li < 0:
        sys.exit('card %s is not a placeholder any more (no "%s")' % (n, label))
    card = s.rfind('<div style="flex:none;width:260px;scroll-snap-align:start', 0, li)
    head = s[card:li]
    head = head.replace('<b style="font-size:17px;line-height:1.3">שם הלקוח</b>', '<b style="font-size:17px;line-height:1.3">%s</b>' % name, 1)
    head = re.sub(r'(font-weight:500">)התחום של הלקוח(</span>)', lambda m: m.group(1) + field + m.group(2), head, count=1)
    box = head.rfind('<div class="dcs')
    head = head[:box] + '<div data-yt="%s" role="button" tabindex="0" aria-label="לצפייה בעדות של %s"' % (vid, name) + head[box + 4:]
    # the placeholder label becomes the thumbnail
    lab_start = head.rfind('<div style="position:absolute;inset:0;display:grid;place-items:center;color:#8a93a8')
    head = head[:lab_start] + '<img src="https://i.ytimg.com/vi/%s/%s.jpg" alt="%s, %s" loading="lazy" decoding="async" onload="if(this.naturalWidth<=120&&this.dataset.f!=2){this.onerror()}" onerror="if(!this.dataset.f){this.dataset.f=1;this.src=this.src.replace(\'oardefault\',\'oar2\')}else if(this.dataset.f==1){this.dataset.f=2;this.src=this.src.replace(\'oar2\',\'hqdefault\')}" style="position:absolute;inset:0;width:100%%;height:100%%;object-fit:cover"><div style="display:none">' % (vid, best_thumb(vid), name, field) + head[lab_start + len('<div style="position:absolute;inset:0;display:grid;place-items:center;color:#8a93a8'):]
    s = s[:card] + head + s[li:]
    s = s.replace('<div style="display:none">;font-family:\'JetBrains Mono\',monospace;font-size:12.5px;letter-spacing:.06em;padding-top:120px">' + label + '</div>', '', 1)
    open(path, 'w', encoding='utf-8').write(s)
    print('card %s: %s (%s) · %s' % (n, name, field, vid))

if __name__ == '__main__':
    if len(sys.argv) != 6:
        sys.exit(__doc__)
    main(*sys.argv[1:])
