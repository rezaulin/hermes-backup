#!/usr/bin/env python3
"""Verifikasi cascade CSS untuk sel البيان tanpa render halaman penuh:
ambil <style> asli dari rapot.html + baris tfoot BAYAN asli, render mini-page
di chromium (low-mem flags) dan baca computed style."""
import asyncio, re, json
from playwright.async_api import async_playwright

src = open('/opt/simmubtadiat/frontend/rapot.html', encoding='utf-8').read()
styles = re.findall(r'<style[^>]*>(.*?)</style>', src, re.S)
css = "\n".join(styles)
# baris tfoot البيان persis dari template
row = re.search(r'(<tr data-field="bayan-box".*?</tr>)', src, re.S).group(1)
row = row.replace('style="display:none;"', 'style="display:table-row;"')
row = row.replace('>-</td>', '>المثبت</td>')

page = f"""<!doctype html><html><head><meta charset="utf-8"><style>{css}</style></head>
<body><div class="rapot-sheet"><table><tfoot>{row}</tfoot></table></div></body></html>"""
open('/tmp/bayan_mini.html', 'w', encoding='utf-8').write(page)


async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(args=[
            "--no-sandbox", "--disable-dev-shm-usage", "--disable-gpu",
            "--single-process", "--no-zygote", "--disable-extensions",
            "--disable-background-networking", "--disable-sync",
            "--renderer-process-limit=1", "--js-flags=--max-old-space-size=128",
        ])
        ctx = await b.new_context(viewport={"width": 900, "height": 400})
        await ctx.route("**/*", lambda r: asyncio.ensure_future(
            r.continue_() if r.request.url.startswith("file:") else r.abort()))
        pg = await ctx.new_page()
        await pg.goto("file:///tmp/bayan_mini.html", wait_until="load", timeout=30000)
        for media in ("screen", "print"):
            await pg.emulate_media(media=media)
            await pg.wait_for_timeout(200)
            r = await pg.evaluate("""()=>{const td=document.querySelector('[data-field="bayan-value"]');
              const cs=getComputedStyle(td);
              return {text:td.textContent.trim(),color:cs.color,fontWeight:cs.fontWeight,
                      fontFamily:cs.fontFamily.split(',')[0],fontSize:cs.fontSize,
                      inlineColor:td.style.color||'(none)'};}""")
            print(media.upper(), json.dumps(r, ensure_ascii=False))
        await pg.emulate_media(media="print")
        await pg.screenshot(path="/tmp/bayan_mini.png", full_page=True)
        await b.close()
    print("shot: /tmp/bayan_mini.png")

asyncio.run(main())
