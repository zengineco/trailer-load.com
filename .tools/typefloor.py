# -*- coding: utf-8 -*-
"""
SHIP GATE: no text below the TYPE FLOOR anywhere in the product.

Vince has raised tiny text roughly six times over three months. Every previous
pass fixed the instances it happened to look at; nothing prevented the next one
from landing. This does. It fails the build, so 8px cannot come back.

FLOOR = 11px. This is a keyboard-and-mouse game on desktop displays; there is no
reason for 8px anywhere. If a string does not fit at 11px, the string is too long
-- cut words, do not shrink type.

Catches all three ways a size gets set in this codebase:
  1. CSS            font-size:10px
  2. CSS clamp()    font-size:clamp(8px,1.3vh,10px)   <- the MINIMUM is what ships
                                                        on a short viewport
  3. Canvas 2D      cx.font="bold 8px 'Share Tech Mono'"   (invisible to CSS greps
                                                            -- this is where the
                                                            SmallsSort bin labels
                                                            hid for eight versions)

Exit 0 = clean. Exit 1 = something is under the floor.
"""
import io, os, re, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FLOOR = 11.0

PAGES = [
    'index.html', 'lock-in.html', 'privacy.html', 'terms.html',
    'ss/index.html', 'me/index.html', 'dashboard/index.html',
    'for-districts/index.html', 'for-districts/program-overview.html',
]

# an explicitly reviewed exemption needs a reason, not just a line number
ALLOW = {
    # (file, matched-text): why it is allowed to sit under the floor
}

CSS_SIZE = re.compile(r'font-size\s*:\s*([0-9]*\.?[0-9]+)px', re.I)
CSS_CLAMP = re.compile(r'font-size\s*:\s*clamp\(\s*([0-9]*\.?[0-9]+)px', re.I)
# canvas: cx.font="bold 8px 'X'"  /  cx.font=(hi?7:6)+"px 'X'"  /  cx.font="bold "+n+"px"
CANVAS_LIT = re.compile(r'\.font\s*=\s*["\'][^"\']*?([0-9]*\.?[0-9]+)px', re.I)
CANVAS_TERN = re.compile(r'\.font\s*=\s*\(\s*\w+\s*\?\s*([0-9]*\.?[0-9]+)\s*:\s*([0-9]*\.?[0-9]+)\s*\)\s*\+\s*["\']px', re.I)
CANVAS_CONCAT = re.compile(r'\.font\s*=\s*["\'][^"\']*["\']\s*\+\s*\(\s*\w+\s*\?\s*([0-9]*\.?[0-9]+)\s*:\s*([0-9]*\.?[0-9]+)\s*\)\s*\+\s*["\']px', re.I)


def scan(rel):
    path = os.path.join(ROOT, rel)
    if not os.path.exists(path):
        return [('MISSING FILE', 0, rel, 0)]
    hits = []
    for i, line in enumerate(io.open(path, encoding='utf-8'), 1):
        stripped = line.strip()
        for rx, kind in ((CSS_SIZE, 'css'), (CSS_CLAMP, 'clamp-min')):
            for m in rx.finditer(line):
                v = float(m.group(1))
                if v < FLOOR:
                    hits.append((kind, v, stripped[:130], i))
        for m in CANVAS_LIT.finditer(line):
            v = float(m.group(1))
            if v < FLOOR:
                hits.append(('canvas', v, stripped[:130], i))
        for rx in (CANVAS_TERN, CANVAS_CONCAT):
            for m in rx.finditer(line):
                for g in m.groups():
                    v = float(g)
                    if v < FLOOR:
                        hits.append(('canvas', v, stripped[:130], i))
    return hits


SHRINK_TAG = re.compile(r'<(small|sub|sup)\b', re.I)
FLOOR_RULE = re.compile(r'small\s*,\s*sub\s*,\s*sup\s*\{[^}]*font-size', re.I)


def bare_shrink_tags(rel):
    """<small>/<sub>/<sup> carry NO font-size, so they fall to the browser's 0.8em
    and can land under the floor with nothing for the size scan to grep. A 10px
    '(mobile)' label survived exactly this way. Require an explicit floor rule."""
    path = os.path.join(ROOT, rel)
    if not os.path.exists(path):
        return None
    src = load = io.open(path, encoding='utf-8').read()
    n = len(SHRINK_TAG.findall(src))
    if n and not FLOOR_RULE.search(src):
        return n
    return None


def main():
    total = 0
    for rel in PAGES:
        hits = scan(rel)
        hits = [h for h in hits if (rel, h[2]) not in ALLOW]
        if not hits:
            continue
        print('\n%s  -- %d under the %gpx floor' % (rel, len(hits), FLOOR))
        for kind, v, text, ln in sorted(hits, key=lambda h: h[1]):
            print('  %-9s %5.1fpx  :%-5d %s' % (kind, v, ln, text))
        total += len(hits)

    for rel in PAGES:
        n = bare_shrink_tags(rel)
        if n:
            print('\n%s  -- %d bare <small>/<sub>/<sup> and NO floor rule' % (rel, n))
            print('  These inherit the browser 0.8em shrink and render under %gpx' % FLOOR)
            print('  with no font-size declaration for the size scan to see.')
            print('  Add:  small,sub,sup{font-size:%gpx;}  as the first rule' % FLOOR)
            print('  (after @import, if the sheet has one -- @import must stay first).')
            total += n

    print('')
    if total:
        print('TYPE FLOOR: %d VIOLATION(S) under %gpx.' % (total, FLOOR))
        print('Fix by CUTTING WORDS, not by shrinking type.')
        return 1
    print('TYPE FLOOR: CLEAN -- nothing under %gpx anywhere.' % FLOOR)
    return 0


if __name__ == '__main__':
    sys.exit(main())
