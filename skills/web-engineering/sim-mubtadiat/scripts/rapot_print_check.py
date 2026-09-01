#!/usr/bin/env python3
"""Headless raport print check for SIM Mubtadiat (rapot.html).

Renders the real app in system Chrome via Playwright, drives the actual
filter -> Tampilkan Santri -> Cetak flow (window.print patched out),
measures each .rapot-sheet in mm, then emulates print media and exports a
PDF with prefer_css_page_size=True so the page's own @page rule applies.

Prints:
  - per-sheet on-screen height in mm (budgets: F4 printable 297mm, A4 ~264mm)
  - PDF page count for BOTH F4 and A4 (1 semester MUST be exactly 1 page on
    EACH — the owner's phone print preview paginates by the printer's paper
    size, usually A4, ignoring @page F4; checking F4 alone is not enough)
  - first chars of each PDF page (Arabic comes out glyph-reversed, but
    a REPEATED table header on page 2 = the table got split)

Setup (once):  pip install playwright pypdf
Auth:  create a session row directly in the DB first, e.g.
  INSERT INTO sessions (id, user_id, expired_at)
  VALUES ('<uuid>', 1, now() + interval '2 hours');
(user 1 = admin/pimpinan; users with is_password_changed=false get 403 on
every API route regardless of session validity)

Usage:  python3 rapot_print_check.py <session_uuid>
Filter ids below default to santri 110 (Ruqoyyah, Ibtida'iyah kelas 6,
bagian A) = tingkatan 1 / kelas 12 / bagian 31 on TA 2026/2027. Edit the
FILTERS dict to target another santri.
"""
import asyncio
import re
import sys

from playwright.async_api import async_playwright

FILTERS = {
    "filter-tahun-ajaran": "2026/2027",
    "filter-tingkatan": "1",
    "filter-kelas": "12",
    "filter-bagian": "31",
}
SEMESTER_OPTION_TEXT = "Keduanya"  # render BOTH semesters (sem 2 is the tall one)
APP = "http://127.0.0.1:8080"
CHROME = "/usr/bin/google-chrome"


async def main():
    if len(sys.argv) < 2:
        sys.exit("usage: rapot_print_check.py <session_uuid>")
    sid = sys.argv[1]

    async with async_playwright() as p:
        browser = await p.chromium.launch(executable_path=CHROME, args=["--no-sandbox","--disable-dev-shm-usage","--disable-gpu","--single-process","--no-zygote"])
        ctx = await browser.new_context(viewport={"width": 1280, "height": 1800})
        await ctx.add_cookies([{"name": "session_id", "value": sid, "domain": "127.0.0.1", "path": "/"}])
        page = await ctx.new_page()
        await page.goto(APP + "/rapot.html", wait_until="networkidle")

        # Kill the print dialog before the Cetak click triggers window.print()
        await page.evaluate("window.print = () => { window.__printed = true; }")

        # Set filters one at a time (kelas/bagian options load on change)
        for fid, val in FILTERS.items():
            await page.evaluate(
                """([id, val]) => {
                     const s = document.getElementById(id);
                     if (!s) throw new Error('missing select ' + id);
                     s.value = val;
                     s.dispatchEvent(new Event('change', {bubbles: true}));
                   }""",
                [fid, val],
            )
            await page.wait_for_timeout(300)

        await page.evaluate(
            """(txt) => {
                 const s = document.getElementById('filter-semester');
                 const o = [...s.options].find(o => o.textContent.includes(txt));
                 if (!o) throw new Error('semester option not found');
                 s.value = o.value;
                 s.dispatchEvent(new Event('change', {bubbles: true}));
               }""",
            SEMESTER_OPTION_TEXT,
        )

        await page.click("button:has-text('Tampilkan Santri')")
        await page.wait_for_timeout(800)
        await page.click(".btn-print-single")
        await page.wait_for_timeout(1500)

        info = await page.evaluate(
            """() => [...document.querySelectorAll('.rapot-sheet')].map((s, i) => ({
                 sheet: i,
                 height_mm: +(s.offsetHeight / 96 * 25.4).toFixed(1),
                 child_sum_mm: +([...s.children].reduce((a, c) => a + c.offsetHeight, 0) / 96 * 25.4).toFixed(1)
               }))"""
        )
        print("on-screen sheets (budgets: F4 printable 297mm / A4 ~264mm):")
        for row in info:
            h = row["height_mm"]
            flag = "OK (fits A4+F4)" if h <= 264 else ("OK F4 only — A4 SPLITS" if h <= 297 else "OVERFLOW even on F4")
            print(f"  sheet {row['sheet']}: {h}mm (children {row['child_sum_mm']}mm) {flag}")

        # Hide app chrome, keep sheets
        await page.evaluate("document.querySelectorAll('aside, .no-print').forEach(e => e.style.display='none')")
        await page.screenshot(path="/tmp/rapot_screen.png", full_page=True)

        await page.emulate_media(media="print")
        # F4: honor the page's own @page size/margins
        await page.pdf(
            path="/tmp/rapot_print_F4.pdf",
            width="215.9mm",
            height="330.2mm",
            print_background=True,
            prefer_css_page_size=True,
            margin={"top": "0mm", "bottom": "0mm", "left": "0mm", "right": "0mm"},
        )
        # A4: what the owner's phone print preview actually does (printer paper wins)
        await page.pdf(
            path="/tmp/rapot_print_A4.pdf",
            format="A4",
            print_background=True,
            prefer_css_page_size=False,
            margin={"top": "0mm", "bottom": "0mm", "left": "0mm", "right": "0mm"},
        )
        await browser.close()

    from pypdf import PdfReader

    n_semesters = len(info) or 1
    for label, path in (("F4", "/tmp/rapot_print_F4.pdf"), ("A4", "/tmp/rapot_print_A4.pdf")):
        r = PdfReader(path)
        status = "PASS" if len(r.pages) == n_semesters else "FAIL"
        print(f"\n[{label}] PDF pages: {len(r.pages)} (expect exactly {n_semesters} — one per semester) {status}")
        for i, pg in enumerate(r.pages):
            t = (pg.extract_text() or "").strip()
            print(f"--- {label} page {i + 1} ({len(t)} chars): {t[:120]!r}")

    print("\nartifacts: /tmp/rapot_screen.png, /tmp/rapot_print_F4.pdf, /tmp/rapot_print_A4.pdf")


asyncio.run(main())
