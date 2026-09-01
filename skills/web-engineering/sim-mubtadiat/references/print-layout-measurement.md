# Print Layout Measurement Workflow

**Session 2026-08-25** — Complete diagnostic pattern for solving HTML-to-print overflow issues when matching a physical reference photo. This workflow emerged from debugging SIM Mubtadiat raport that went from 1 page → 5 pages → back to 1 page per semester.

## Overview

When a print layout overflows (extra pages, text touching borders, footer-pinning broken), **never guess CSS values**. Use this sequence:

1. Render live output to PDF/PNG
2. Measure total sheet height in mm
3. Drill down to component heights (header, table, footer)
4. Identify overrides killing `margin-top:auto`
5. Apply surgical fixes iteratively
6. Verify with dual-paper test before deploy

## Step-by-Step Scripts

### 1. Render Live Report to PDF/PNG

```python
#!/usr/bin/env python3
"""Render rapot live and save PDF + PNG for measurement."""
import asyncio
from playwright.async_api import async_playwright

FILTERS = {"filter-tahun-ajaran":"2026/2027", "filter-tingkatan":"1", 
           "filter-kelas":"12", "filter-bagian":"31"}
APP = "http://127.0.0.1:8080"

async def main():
    sid = open('/tmp/sid.txt').read().strip()
    async with async_playwright() as p:
        b = await p.chromium.launch(
            args=["--no-sandbox","--disable-dev-shm-usage",
                  "--disable-gpu","--single-process","--no-zygote"])
        
        ctx = await b.new_context(viewport={"width":1200,"height":1700})
        
        # Block CDNs to prevent renderer crashes on low-RAM VPS
        async def route(r):
            u = r.request.url
            await (r.continue_() if (u.startswith("http://127.0.0.1") or u.startswith("file:")) else r.abort())
        await ctx.route("**/*", route)
        
        await ctx.add_cookies([{"name":"session_id","value":sid,"domain":"127.0.0.1","path":"/"}])
        pg = await ctx.new_page()
        await pg.goto(APP+"/rapot.html", wait_until="domcontentloaded", timeout=60000)
        await pg.wait_for_timeout(800)
        
        # Drive filters via real data
        await pg.evaluate("""window.print=()=>{}""")
        for fid,val in FILTERS.items():
            await pg.evaluate("""([id,val])=>{const s=document.getElementById(id);s.value=val;s.dispatchEvent(new Event('change',{bubbles:true}));}""",[fid,val])
            await pg.wait_for_timeout(400)
        
        await pg.click(".btn-print-single")
        await pg.wait_for_timeout(1500)
        
        # Save PNG render
        sheets = await pg.query_selector_all('.rapot-sheet')
        for i,sh in enumerate(sheets):
            await sh.screenshot(path=f"/tmp/live_sem{i+1}.png")
        
        # Generate PDF (print media)
        await pg.emulate_media(media="print")
        await pg.pdf(path="/tmp/live_F4.pdf", width="215.9mm", height="330.2mm", 
                     print_background=True, prefer_css_page_size=True,
                     margin={"top":"0","bottom":"0","left":"0","right":"0"})
        
        await b.close()

if __name__ == "__main__":
    asyncio.run(main())
```

### 2. Measure Section Heights

```python
#!/usr/bin/env python3
"""Measure each section's height in mm after print rendering."""
import asyncio
from playwright.async_api import async_playwright

APP = "http://127.0.0.1:8080"
sid = open('/tmp/sid.txt').read().strip()

async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(
            args=["--no-sandbox","--disable-dev-shm-usage",
                  "--disable-gpu","--single-process","--no-zygote"])
        
        ctx = await b.new_context(viewport={"width":1200,"height":1700})
        async def route(r):
            u = r.request.url
            await (r.continue_() if (u.startswith("http://127.0.0.1") or u.startswith("file:")) else r.abort())
        await ctx.route("**/*", route)
        await ctx.add_cookies([{"name":"session_id","value":sid,"domain":"127.0.0.1","path":"/"}])
        pg = await ctx.new_page()
        
        await pg.goto(APP+"/rapot.html", wait_until="domcontentloaded", timeout=60000)
        await pg.wait_for_timeout(800)
        await pg.evaluate("window.print=()=>{}")
        
        # Set filters
        FILTERS = {"filter-tahun-ajaran":"2026/2027", "filter-tingkatan":"1", 
                   "filter-kelas":"12", "filter-bagian":"31"}
        for fid,val in FILTERS.items():
            await pg.evaluate("""([id,val])=>{const s=document.getElementById(id);s.value=val;s.dispatchEvent(new Event('change',{bubbles:true}));}""",[fid,val])
            await pg.wait_for_timeout(400)
        
        await pg.click(".btn-print-single")
        await pg.wait_for_timeout(1500)
        
        # Measure section heights
        data = await pg.evaluate("""()=>{
          const mm=x=>+(x/96*25.4).toFixed(1);
          const sh=document.querySelector('.rapot-sheet');
          
          // Sheet-level metrics
          const kids=[...sh.children].map(c=>({
            cls:c.className.slice(0,30)||'table-wrap',
            mm:mm(c.offsetHeight)
          }));
          
          // Table breakdown
          tbl = sh.querySelector('table');
          if(tbl){
            kids.push({cls:'thead',mm:mm(tbl.querySelector('thead').offsetHeight)});
            kids.push({cls:'tbody',mm:mm(tbl.querySelector('tbody').offsetHeight)});
            rows = tbl.querySelectorAll('tbody tr');
            kids.push({cls:'tbody_rows',count:rows.length});
            if(rows.length>0) kids.push({cls:'row_mm',mm:mm(rows[0].offsetHeight)});
            kids.push({cls:'tfoot',mm:mm(tbl.querySelector('tfoot').offsetHeight)});
          }
          
          return {sheet_total:mm(sh.offsetHeight), children:kids};
        }""")
        
        import json; print(json.dumps(data, indent=1))
        await b.close()

if __name__ == "__main__":
    asyncio.run(main())
```

### 3. Compare Component Breakdown

```python
#!/usr/bin/env python3
"""Detailed component breakdown for each sheet."""
import asyncio
from playwright.async_api import async_playwright

APP = "http://127.0.0.1:8080"
sid = open('/tmp/sid.txt').read().strip()

async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(args=["--no-sandbox","--disable-dev-shm-usage",
                                          "--disable-gpu","--single-process","--no-zygote"])
        
        ctx = await b.new_context(viewport={"width":1200,"height":1700})
        async def route(r):
            u = r.request.url
            await (r.continue_() if (u.startswith("http://127.0.0.1") or u.startswith("file:")) else r.abort())
        await ctx.route("**/*", route)
        await ctx.add_cookies([{"name":"session_id","value":sid,"domain":"127.0.0.1","path":"/"}])
        pg = await ctx.new_page()
        
        await pg.goto(APP+"/rapot.html", wait_until="domcontentloaded", timeout=60000)
        await pg.wait_for_timeout(800)
        await pg.evaluate("window.print=()=>{}")
        
        FILTERS = {"filter-tahun-ajaran":"2026/2027", "filter-tingkatan":"1", 
                   "filter-kelas":"12", "filter-bagian":"31"}
        for fid,val in FILTERS.items():
            await pg.evaluate("""([id,val])=>{const s=document.getElementById(id);s.value=val;s.dispatchEvent(new Event('change',{bubbles:true}));}""",[fid,val])
            await pg.wait_for_timeout(400)
        
        await pg.evaluate("""()=>{const s=document.getElementById('filter-semester');const o=[...s.options].find(o=>o.textContent.includes('Keduanya'));s.value=o.value;s.dispatchEvent(new Event('change',{bubbles:true}));}""")
        await pg.click("button:has-text('Tampilkan Santri')")
        await pg.wait_for_timeout(1000)
        await pg.click(".btn-print-single")
        await pg.wait_for_timeout(1500)
        await pg.emulate_media(media="print")
        await pg.wait_for_timeout(300)
        
        data = await pg.evaluate("""()=>{
          const mm=x=>+(x/96*25.4).toFixed(1);
          return [...document.querySelectorAll('.rapot-sheet')].map((sh,i)=>{
            const kids=[...sh.children].map(c=>({
              c:c.className.slice(0,20)||'table-wrap',
              mm:mm(c.offsetHeight)
            }));
            return {sheet:i, total:mm(sh.offsetHeight), content:kids.reduce((a,k)=>a+k.mm,0), kids};
          });
        }""")
        
        import json; print(json.dumps(data, indent=1))
        await b.close()

if __name__ == "__main__":
    asyncio.run(main())
```

## Expected Metrics (F4 Paper)

| Component | Typical Height | Notes |
|-----------|---------------|-------|
| Header block | ~34mm | Title + logo + nama sekolah |
| Student data | ~25mm | Name/stambuk/kelas rows |
| Table thead | ~15-18mm | Column headers |
| Table tbody | ~125-140mm | Depends on number of rows |
| Table tfoot | ~30-40mm | Total + absen + bayan |
| Signature box | ~25-30mm | Footer pinning should work |
| **Total sheet** | **~260-285mm** | F4 content area limit = 285mm |

If any sheet exceeds 285mm → check for these culprits:

1. **tfoot th padding** - if `padding: 1.27cm` → tfoot blooms to 100mm+
   - Fix: `padding: 1px 6px 4px 6px` (matches reference photo)
   
2. **signature-box margin-top override** - `.signature-box { margin-top: 1.27cm !important }` kills `margin-top:auto`
   - Fix: remove the override, let auto pin work
   
3. **table row line-height** - default 1.5 → bloated rows
   - Fix: `line-height: 1.1`, `padding-bottom: 3px` instead of 4px
   
4. **table margin-top** - large gap between student data and table
   - Fix: `margin-top: 0.6cm` instead of 1.27cm

## Bug Patterns Discovered (2026-08-25)

| Bug Pattern | Symptom | Fix |
|-------------|---------|-----|
| tfoot padding 1.27cm | Rapport goes to 5 pages | `padding: 1px 6px 4px 6px` |
| signature-box margin-top 1.27cm | Sheet always 284mm+ (overflow) | Remove override, let auto pin |
| Line-height 1.22 | Rows tall, overflow | Reduce to 1.1 |
| Min-height 285mm mepet | Rounding errors → page break | Reduce to 270mm headroom |

## Verification Checklist

Before deploying print-layout changes:

- [ ] Run `/tmp/render_live.py` → check sheet heights in mm
- [ ] Run `/tmp/measure.py` → verify no single component is bloated
- [ ] Run `/root/.hermes/skills/web-engineering/sim-mubtadiat/scripts/rapot_dual_paper_check.py <session_uuid>` → A4 & F4 both show 2 pages (1 per semester)
- [ ] Visual side-by-side comparison vs reference photo (send as MEDIA attachments)
- [ ] Bump cache version (`CACHE_NAME v27 → v28`) before deploying (Cloudflare 4h trap)

## References

- `web-engineering/sim-mubtadiat/SKILL.md` — CRITICAL LEARNING section
- `scripts/rapot_print_check.py` — official verification script
- `scripts/rapot_pdf_gap_check.py` — measure ink-to-border gaps in rendered PDF
- `/opt/simmubtadiat/frontend/rapot.html` — actual implementation (v28)
- Session scripts: `/tmp/render_live.py`, `/tmp/measure.py`, `/tmp/measure2.py`
