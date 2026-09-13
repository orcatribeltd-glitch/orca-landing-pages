#!/usr/bin/env python3
"""משפיען בדיגיטל — התאמת כל דפי הריפו לפלטת המותג (13/09/2026, לפי הוראת יהונתן).

פלטה: כתום FF7A1A, כתום שרוף E8590C, כחול כהה 0F2A44, תכלת 7FC6E0.
מריצים פעם אחת על pages/mashpian*/index.html ו-pages/influence-footer/index.html.
"""
import re, sys, pathlib

HEX = {
    'F2C230': 'FF7A1A',  # זהב → כתום (הדגשות, כפתורים, ספרות)
    'FFDE7A': 'FFB27A',  # זהב בהיר → כתום בהיר (קצה גרדיאנט)
    'FFD75E': 'FFA04D',  # זהב hover → כתום hover
    '38E1C6': '7FC6E0',  # טורקיז → תכלת (תגיות, קו משני)
    'B8E9E0': 'C9E6F2',  # גוון טורקיז בהיר → גוון תכלת בהיר
    '2ED47A': 'E8590C',  # ירוק → כתום שרוף (כפתורי פעולה)
    '5CF0A4': 'FF7A1A',  # ירוק בהיר (קצה גרדיאנט) → כתום
    '05130C': 'FFFFFF',  # טקסט כהה על ירוק → לבן על כתום שרוף
    '0A0A0C': '0F2A44',  # טקסט כהה על זהב → כחול כהה על כתום
    '08080B': '0B1F33',  # שחור עמוק → כחול כהה עמוק
    '0A0A0D': '0F2A44',  # שחור → כחול כהה (המותג)
    '0A0C0E': '0D2440',  # שחור-כחלחל → כחול כהה
    'A6A6B2': 'B7C4D3',  # אפור טקסט → אפור-כחלחל
    'C9C9D2': 'D5DEE8',
    '8E8E9A': '93A3B5',
    '9A9AA6': '9DACBD',
    '7E7E8A': '8797AB',
}
RGB = {
    '242,194,48': '255,122,26',   # זהב
    '56,225,198': '127,198,224',  # טורקיז
    '46,212,122': '232,89,12',    # ירוק
}
BODY_RULE = 'html,body{max-width:100%;overflow-x:hidden;}'
BODY_NEW = 'html,body{max-width:100%;overflow-x:hidden;} body{background:#0F2A44 !important;}'

def rebrand(text):
    def hx(m):
        return '#' + HEX.get(m.group(1).upper(), m.group(1))
    text = re.sub(r'#([0-9A-Fa-f]{6})\b', hx, text)
    def rg(m):
        key = re.sub(r'\s+', '', m.group(2))
        return m.group(1) + RGB.get(key, m.group(2))
    text = re.sub(r'(rgba?\()\s*([0-9]{1,3}\s*,\s*[0-9]{1,3}\s*,\s*[0-9]{1,3})', rg, text)
    if BODY_RULE in text and 'body{background:#0F2A44' not in text:
        text = text.replace(BODY_RULE, BODY_NEW, 1)
    return text

if __name__ == '__main__':
    files = sys.argv[1:] or [str(p) for p in pathlib.Path('pages').glob('mashpian*/index.html')] + ['pages/influence-footer/index.html']
    for f in files:
        p = pathlib.Path(f)
        raw = p.read_bytes().decode('utf-8')
        # לא נוגעים בפונטים המוטמעים (שורות 3-4): מחליפים רק מחוץ ל-@font-face
        parts = raw.split('</style>', 1) if '@font-face' in raw[:5000] else ['', raw]
        if len(parts) == 2 and '@font-face' in parts[0]:
            out = parts[0] + '</style>' + rebrand(parts[1])
        else:
            out = rebrand(raw)
        changed = sum(1 for a, b in zip(raw, out) if a != b) or (len(raw) != len(out))
        p.write_bytes(out.encode('utf-8'))
        print(f'{f}: {"updated" if out != raw else "unchanged"}')
