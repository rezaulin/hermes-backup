#!/usr/bin/env python3
"""Reverse-engineer a table's grid structure from a reference PHOTO.

Use when the owner sends a raport/table photo and says "reproduce plek
ketiplek, kolom & garis jangan beda". Detects horizontal line bands and, for
each row band, the vertical border lines present -> a MISSING vertical line
between two data columns = a colspan/merge in that row. This is the ground-truth
method the sim-mubtadiat raport tfoot was built from (أيام التأخر rowspan,
البيان colspan, etc.).

Usage:
    python3 detect_table_grid.py <photo.jpg> [dark_thresh]

dark_thresh default 110 (lines are dark maroon/black on white). Lower to ~130
for faded scans; raise if background noise creates false lines.

Output: horizontal line y-positions (row separators) + per-band vertical line
x-positions. Compare vertical-line counts across bands: a band with FEWER
lines than the data band has merged cells there. Map x-positions to columns to
know WHICH cells merged, then set colspan/rowspan to match.

Pitfalls learned building the raport:
- Outer edges + faint lines need thr ~0.45 of band height, not 0.5.
- Group nearby columns (<=5px) into one line — anti-aliasing splits a border
  into 2-3 adjacent dark columns.
- Sample every pixel for x-lines but you can step x by 2 for the horizontal
  pass (speed) — h-lines are long so undersampling is fine.
- Maroon table borders: max(r,g,b)<thr catches them same as black; don't try to
  colour-match the exact maroon, brightness threshold is more robust.
- Verify against a color/tier classifier separately (H/O/B per-pixel) for
  font-colour zones — this script only finds GEOMETRY.
"""
import sys
from PIL import Image


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)
    path = sys.argv[1]
    thr = int(sys.argv[2]) if len(sys.argv) > 2 else 110
    im = Image.open(path).convert('RGB')
    w, h = im.size
    px = im.load()

    def is_dark(x, y):
        r, g, b = px[x, y]
        return max(r, g, b) < thr

    # --- horizontal line bands (row separators) ---
    rowdark = []
    for y in range(h):
        c = sum(1 for x in range(0, w, 2) if is_dark(x, y))
        rowdark.append(c)
    hpeaks = [y for y in range(h) if rowdark[y] > (w / 2) * 0.4]
    hbands = []
    for y in hpeaks:
        if hbands and y - hbands[-1][-1] <= 3:
            hbands[-1].append(y)
        else:
            hbands.append([y])
    hlines = [int(sum(g) / len(g)) for g in hbands]
    print(f"image size: {w}x{h}  dark_thresh={thr}")
    print(f"\nHORIZONTAL lines (row separators), {len(hlines)} found:")
    print("  " + ", ".join(str(y) for y in hlines))

    # --- vertical lines per row band ---
    def vlines(y0, y1, frac=0.45):
        span = max(1, y1 - y0)
        col = []
        for x in range(w):
            c = sum(1 for y in range(y0, y1) if is_dark(x, y))
            col.append(c)
        peaks = [x for x in range(w) if col[x] > span * frac]
        groups = []
        for x in peaks:
            if groups and x - groups[-1][-1] <= 5:
                groups[-1].append(x)
            else:
                groups.append([x])
        return [int(sum(g) / len(g)) for g in groups]

    print("\nVERTICAL lines per row band (between consecutive h-lines):")
    print("  A band with FEWER x-lines than the data band = merged cells there.")
    for i in range(len(hlines) - 1):
        y0, y1 = hlines[i] + 1, hlines[i + 1] - 1
        if y1 - y0 < 4:
            continue
        vs = vlines(y0, y1)
        print(f"  band y[{hlines[i]}..{hlines[i+1]}] ({y1-y0}px): {vs}  -> {len(vs)} v-lines")


if __name__ == '__main__':
    main()
