# Removing an image background (logos/icons) — flood-fill recipe

Extracted from SKILL.md 2026-08-29 to keep SKILL.md under its size limit. Applies to the madrasa logo and every PWA/app icon in `frontend/public/`.

## Use EDGE FLOOD-FILL, never global brightness→alpha

The naive recipe (brightest-channel-as-alpha, black→transparent) is WRONG for logos whose ARTWORK CONTAINS BLACK (outlines, text): it wipes both the background AND the artwork's black parts. Production result when this was tried: owner sent a screenshot — *"koq malah gak jelas bos, ada komponen hilang warna aslinya malah ketutup"* (icon looked broken, components missing).

**Diagnose first**: `collections.Counter` of pixels — if the logo's own black/dark outline color appears as a distinct population INSIDE the logo (e.g. dark-gray `(52,44,42)` among the gold), brightness-threshold removal WILL destroy it.

## Correct recipe (PIL, no numpy)

Flood-fill the background connected to the image border; keep everything else.

```python
from PIL import Image, ImageFilter
from collections import deque

src = Image.open('logo.jpg').convert('RGB')
src = src.filter(ImageFilter.MedianFilter(3))   # denoise JPEG speckle FIRST
img = src; w, h = img.size; px = img.load()

THRESH = 75  # background if max(px) < THRESH — tune per image
dark = lambda x, y: max(px[x, y]) < THRESH
visited = bytearray(w * h); q = deque()

for x in range(w):
    for y in (0, h - 1):
        if dark(x, y): q.append((x, y)); visited[y * w + x] = 1
for y in range(h):
    for x in (0, w - 1):
        if dark(x, y) and not visited[y * w + x]: q.append((x, y)); visited[y * w + x] = 1

while q:  # 8-direction flood
    x, y = q.popleft()
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = x + dx, y + dy
            if 0 <= nx < w and 0 <= ny < h and not visited[ny * w + nx] and dark(nx, ny):
                visited[ny * w + nx] = 1; q.append((nx, ny))

mask = Image.new('L', (w, h), 255); apx = mask.load()
for i, v in enumerate(visited):
    if v: apx[i % w, i // w] = 0

mask = mask.filter(ImageFilter.GaussianBlur(1.5))   # FEATHER — see below
rgba = img.convert('RGBA'); rgba.putalpha(mask)
rgba.save('logo.png', optimize=True)
```

## Two quality steps that make it look professional, not template

Discovered when the owner said the first result was *"masih ada yang kurang"*:

1. **Denoise the JPEG source first** — `MedianFilter(3)`. Compression speckle around gold/dark edges otherwise leaks into the result. Related: when the owner sends a "transparent PNG" over Telegram as a PHOTO, Telegram converts it to RGB JPEG and alpha is lost — ask them to resend via "Send as File/Document"; meanwhile process the black-bg JPEG with this recipe.
2. **Feather the alpha edge** — flood-fill alone gives HARD binary alpha (0% partial pixels) → jagged staircase edges, very visible at sidebar/icon sizes and on sharp phone screens. `mask.filter(ImageFilter.GaussianBlur(1.5))` on the L-mode mask before `putalpha`.

## Verification (do this every time)

- Background % removed matches only the TRUE background (e.g. 38.6% for the madrasa logo).
- Opaque dark pixels still REMAIN in the logo: count `p[3] > 200 and max(p[:3]) < 80` → must be **> 0**. Zero means the artwork's blacks got eaten and the result will look broken.
- Feathering worked: count partial-alpha pixels `20 <= p[3] <= 230` → was 0% before, should be **~1%+** after.

Only use the simpler brightness→alpha approach when you've confirmed the logo contains NO dark tones at all.

## Asset state

`frontend/public/logo.jpg` = black background original. `logo-v3.png` = current transparent version (flood-fill + feathered). All references use `logo-v3.png`; do NOT regenerate with the brightness method or the sidebar/avatar icons regress. Raport print header uses the separate monochrome `/logo-raport-bw-v5.png`.

Version-suffix bump (`logo-v4.png`, `icon-192-v7.png`, …) is MANDATORY on any logo/icon change — Cloudflare caches unhashed statics ~4h and OS launchers cache PWA icons. Sed-update all references (18 HTML + main.js + xss.js + manifest.json) when bumping.

## General image-diagnosis triage

When vision/OCR can't read a screenshot: PIL pixel stats first — dominant-color `Counter`, corner-pixel sampling (background color), brightness, edge density — before asking the owner.
