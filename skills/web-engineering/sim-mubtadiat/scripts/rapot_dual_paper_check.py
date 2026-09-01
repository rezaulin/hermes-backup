#!/usr/bin/env python3
"""Dual-paper print check for SIM Mubtadiat raport (rapot.html).

WHY: phone print previews paginate on the PRINTER's paper (usually A4),
NOT the CSS @page F4 size — a raport that fits F4 can still overflow to
2 pages on the owner's phone. This probe verifies 1 page/semester on BOTH.

Usage:
  1. Insert a temp session (delete afterwards!):
     docker exec simmubtadiat-db-1 psql -U mubtadiaat -d mubtadiaat_db -c \
       "INSERT INTO sessions (id, user_id, expired_at) VALUES ('<uuid>', 1, now() + interval '2 hours');"
  2. python3 rapot_dual_paper_check.py <uuid>

Requires: pip install playwright pypdf; system Chrome at /usr/bin/google-chrome.
Test subject: santri 110 Ruqoyyah (Ibtida'iyah kelas 6, bagian A) — adjust
the filter values (tingkatan=1, kelas=12, bagian=31) if test data changes.
Exit code 0 = PASS (exactly 2 pages for the 2 semesters on both papers).
"""
import asyncio
import sys

from playwright.async_api import async_playwright
from pypdf import PdfReader

SID = sys.argv[1] if len(sys.argv) > 1 else sys.exit(
    "usage: rapot_dual_paper_check.py <session_uuid>")


async def build_sheets(page):
    await page.goto("http://127.0.0.1:8080/rapot.html", wait_until="networkidle")
    # Patch window.print BEFORE clicking Cetak or the flow opens a dialog.
    await page.evaluate("window.print = () => {};")

    def setv(el_id, val):
        return page.evaluate(
            f"() => {{ const s = document.getElementById('{el_id}'); s.value = '{val}'; "
            "s.dispatchEvent(new Event('change', {bubbles:true})); }")

    # Cascade options load asynchronously per change — wait between each.
    await setv('filter-tingkatan', '1'); await page.wait_for_timeout(300)
    await setv('filter-kelas', '12');    await page.wait_for_timeout(300)
    await setv('filter-bagian', '31');   await page.wait_for_timeout(300)
    await page.evaluate("""() => {
      const s = document.getElementById('filter-semester');
      s.value = [...s.options].find(o => o.textContent.includes('Keduanya')).value;
      s.dispatchEvent(new Event('change', {bubbles:true}));
    }""")
    await page.click("button:has-text('Tampilkan Santri')")
    await page.wait_for_timeout(800)
    await page.click(".btn-print-single")
    await page.wait_for_timeout(1500)
    await page.evaluate(
        "document.querySelectorAll('aside, .no-print').forEach(e => e.style.display='none')")


async def run(paper):
    async with async_playwright() as p:
        # --single-process WAJIB: multi-process renderer crashes (Page
        # crashed) pada halaman apa pun yang load font/iframe, baik di
        # system google-chrome maupun playwright chromium (isolated
        # 2026-08-24: semua varian HTML crash kecuali --single-process).
        browser = await p.chromium.launch(
            args=["--no-sandbox", "--single-process",
                  "--disable-dev-shm-usage", "--disable-gpu"])
        ctx = await browser.new_context(viewport={"width": 1280, "height": 1800})
        await ctx.add_cookies([{"name": "session_id", "value": SID,
                                "domain": "127.0.0.1", "path": "/"}])
        page = await ctx.new_page()
        await build_sheets(page)
        await page.emulate_media(media="print")

        # True content height: zero min-height so offsetHeight = content,
        # not the footer-pinning min-height.
        heights = await page.evaluate("""
        () => [...document.querySelectorAll('.rapot-sheet')].map((s,i) => {
            s.style.minHeight = '0';
            const kids = [...s.children].reduce((a,c)=>a+c.offsetHeight,0);
            return {sem: i+1, content_mm: +(kids/96*25.4).toFixed(1)};
        })""")
        await page.evaluate(
            "document.querySelectorAll('.rapot-sheet').forEach(s => s.style.minHeight='')")

        out = f"/tmp/rapot_check_{paper}.pdf"
        zero = {"top": "0mm", "bottom": "0mm", "left": "0mm", "right": "0mm"}
        if paper == "a4":
            # prefer_css_page_size=False -> format A4 wins over the page's
            # @page F4: simulates a phone preview using the printer's A4.
            await page.pdf(path=out, format="A4", print_background=True,
                           prefer_css_page_size=False, margin=zero)
        else:
            # prefer_css_page_size=True -> the page's own @page F4 applies:
            # exactly what an F4 printer sees.
            await page.pdf(path=out, width="215.9mm", height="330.2mm",
                           print_background=True, prefer_css_page_size=True,
                           margin=zero)
        await browser.close()

        pages = len(PdfReader(out).pages)
        print(f"[{paper.upper()}] content: {heights}  PDF pages: {pages} "
              "(expect 2 for the 2 semesters)")
        return pages


async def main():
    a4 = await run("a4")
    f4 = await run("f4")
    ok = (a4 == 2 and f4 == 2)
    print("RESULT:", "PASS — 1 page/semester on both A4 and F4"
          if ok else f"FAIL (a4={a4}, f4={f4})")
    sys.exit(0 if ok else 1)


asyncio.run(main())
