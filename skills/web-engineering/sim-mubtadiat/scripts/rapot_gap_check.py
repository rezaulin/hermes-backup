#!/usr/bin/env python3
"""Raport ink-to-border gap check — reference-photo edition.

Measures the distance from TEXT INK to ruled table lines on a photo of the
physical raport, in mm. Used to set the CSS padding spec so printed text
never touches the borders (owner rule 2026-08-24: "jangan sampai ada text
menyentuh garis, terutama huruf yang arah penulisannya ke bawah" — Arabic
descenders خ ج ح ع غ ي ق).

Calibration: photo = full A4 page → 1px = 297mm / image_height_px.
Adjust TABLE_TOP/TABLE_BOTTOM and the column x-ranges per photo.

Usage:  python3 rapot_gap_check.py <rapot_photo.jpg>
Deps:   pip install pillow
"""
import sys
from PIL import Image

# --- tune per photo ---
TABLE_TOP, TABLE_BOTTOM = 95, 640      # y-range of the grades table
COL_X = [(55, 162), (162, 240), (240, 354), (354, 476), (476, 511)]
COLN = ['العامة', 'الخاصة', 'الفنون', 'الكتب', 'الرقم']  # right-to-left
HLINE_MIN_DARK = 300                    # px count to call a horizontal border
INK_MAX = 185                           # loose threshold: faded scans are gray


def is_ink(r, g, b):
    if r < INK_MAX and g < INK_MAX and b < INK_MAX:
        # exclude green pen annotations (owner circles items in green)
        if g > 80 and g > r * 1.25 and g > b * 1.25:
            return False
        return True
    return False


def main():
    path = sys.argv[1] if len(sys.argv) > 1 else sys.exit('usage: rapot_gap_check.py <photo.jpg>')
    im = Image.open(path).convert('RGB')
    w, h = im.size
    px = im.load()
    mm = 297.0 / h
    print(f'image {w}x{h}  ->  1px = {mm:.3f}mm\n')

    # horizontal border lines
    hlines = [y for y in range(TABLE_TOP, TABLE_BOTTOM)
              if sum(1 for x in range(COL_X[0][0], COL_X[-1][1])
                     if is_ink(*px[x, y])) > HLINE_MIN_DARK]
    grouped = []
    if hlines:
        s = p = hlines[0]
        for y in hlines[1:]:
            if y - p > 2:
                grouped.append((s + p) // 2); s = y
            p = y
        grouped.append((s + p) // 2)
    print('row borders y:', grouped)

    def ink_extent(x0, x1, y0, y1):
        top = bottom = None
        for y in range(y0 + 3, y1 - 2):          # 3px border margin
            if sum(1 for x in range(x0 + 3, x1 - 3) if is_ink(*px[x, y])) >= 3:
                if top is None:
                    top = y
                bottom = y
        return top, bottom

    gaps_b, gaps_a = [], []
    for y0, y1 in zip(grouped, grouped[1:]):
        parts = []
        for (cx0, cx1), cn in zip(COL_X, COLN):
            t, b = ink_extent(cx0, cx1, y0, y1)
            if t is None:
                continue
            gb, ga = (y1 - 2 - b) * mm, (t - y0 - 2) * mm
            gaps_b.append(gb); gaps_a.append(ga)
            parts.append(f'{cn}:b{gb:.2f}/a{ga:.2f}')
        if parts:
            print(f'row y{y0}-{y1}: {" | ".join(parts)}')

    if gaps_b:
        import statistics as st
        print(f'\nGap BAWAH (ink -> garis bawah) mm: '
              f'min={min(gaps_b):.2f} median={st.median(gaps_b):.2f} max={max(gaps_b):.2f}')
        print(f'Gap ATAS  (garis atas -> ink) mm: '
              f'min={min(gaps_a):.2f} median={st.median(gaps_a):.2f} max={max(gaps_a):.2f}')
        print(f'\nTarget for web raport: padding such that min ink gap >= '
              f'{min(gaps_b):.2f}mm (measured on PDF via band_check method).')


if __name__ == '__main__':
    main()
