#!/usr/bin/env python3
"""Raport PDF ink-gap band check — rendered-output edition.

Verifies that the PRINTED raport (headless-Chrome PDF from
rapot_dual_paper_check.py) keeps >= ~0.8mm between text INK and table
borders. Word bboxes LIE for Arabic fonts (metrics carry huge
ascent/descent; bbox gaps read ~0.15pt regardless of real spacing) — this
script rasterizes at 300 DPI and scans real dark pixels per row band.

Usage:
    python3 rapot_dual_paper_check.py <uuid>      # produces /tmp/rapot_check_f4.pdf
    python3 rapot_pdf_gap_check.py /tmp/rapot_check_f4.pdf [page_index=1]

Deps: pip install pymupdf pillow

Output: per-row per-column gaps (top/bottom, mm) + global minimum.
Pass criterion: min gap >= 0.74mm (physical-reference minimum).
"""
import sys
import io
import pymupdf
from PIL import Image

DPI = 300
SCALE = DPI / 72.0
MMPT = 25.4 / 72.0
INK_DARK = 130  # rendered PDF ink is crisp black; strict threshold OK


def main():
    pdf = sys.argv[1] if len(sys.argv) > 1 else '/tmp/rapot_check_f4.pdf'
    page_idx = int(sys.argv[2]) if len(sys.argv) > 2 else len(pymupdf.open(pdf)) - 1

    doc = pymupdf.open(pdf)
    pg = doc[page_idx]

    # Borders render as thin RECTANGLES ('re'), not line items ('l').
    h_lines, v_lines = set(), set()
    for d in pg.get_drawings():
        for item in d['items']:
            if item[0] != 're':
                continue
            r = item[1]
            wdt, hgt = r.x1 - r.x0, r.y1 - r.y0
            if hgt <= 3.0 and wdt > 5:
                h_lines.add(round((r.y0 + r.y1) / 2, 2))
            elif wdt <= 3.0 and hgt > 5:
                v_lines.add(round((r.x0 + r.x1) / 2, 2))
    h_lines, v_lines = sorted(h_lines), sorted(v_lines)
    print('H lines y(pt):', h_lines)
    print('V lines x(pt):', v_lines)

    pix = pg.get_pixmap(dpi=DPI)
    im = Image.open(io.BytesIO(pix.tobytes('png'))).convert('RGB')
    px = im.load()
    W, H = im.size

    def band_gaps(y0, y1):
        out = {}
        for i in range(len(v_lines) - 1):
            ix0, ix1 = int((v_lines[i] + 2) * SCALE), int((v_lines[i + 1] - 2) * SCALE)
            iy0, iy1 = int((y0 + 2.5) * SCALE), int((y1 - 2.5) * SCALE)
            top = bottom = None
            for y in range(iy0, iy1):
                if any(px[x, y][0] < INK_DARK for x in range(ix0, ix1)):
                    top = y
                    break
            for y in range(iy1 - 1, iy0 - 1, -1):
                if any(px[x, y][0] < INK_DARK for x in range(ix0, ix1)):
                    bottom = y
                    break
            if top is not None:
                out[i] = (round((top / SCALE - y0) * MMPT, 2),
                          round((y1 - bottom / SCALE) * MMPT, 2))
        return out

    all_gaps = []
    print('\nrow (y0-y1 pt) | col: gap_top/gap_bottom (mm), col0 = rightmost')
    for y0, y1 in zip(h_lines, h_lines[1:]):
        if y0 < 260:          # skip header zone; tune if layout changes
            continue
        res = band_gaps(y0, y1)
        if not res:
            continue
        all_gaps.extend(g for pair in res.values() for g in pair)
        print(f'y{y0}-{y1}: ' + ' | '.join(f'c{i}:{a}/{b}' for i, (a, b) in sorted(res.items())))

    if all_gaps:
        m = min(all_gaps)
        verdict = 'PASS' if m >= 0.74 else 'FAIL — increase cell padding'
        print(f'\nMIN ink-to-border gap: {m:.2f}mm  ({verdict}; '
              f'reference photo minimum = 0.74mm)')
        sys.exit(0 if m >= 0.74 else 1)


if __name__ == '__main__':
    main()
