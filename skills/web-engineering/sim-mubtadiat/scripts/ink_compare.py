from playwright.sync_api import sync_playwright
from PIL import Image

def shot(path_html, out):
    with sync_playwright() as p:
        b = p.chromium.launch(args=['--no-sandbox', '--disable-dev-shm-usage',
                                    '--disable-gpu', '--single-process', '--no-zygote'])
        pg = b.new_page(viewport={'width': 900, 'height': 400})
        pg.goto('file://' + path_html, wait_until='load')
        pg.emulate_media(media='print')
        pg.wait_for_timeout(250)
        w = pg.evaluate("getComputedStyle(document.querySelector('[data-field=\"bayan-value\"]')).fontWeight")
        pg.screenshot(path=out, full_page=True)
        b.close()
    return w

def ink(path):
    im = Image.open(path).convert('RGB')
    w, h = im.size
    px = im.load()
    return sum(1 for y in range(h) for x in range(int(w * .55), w) if max(px[x, y]) < 128)

wb = shot('/tmp/bayan_mini.html', '/tmp/ink_bold.png')
wn = shot('/tmp/bayan_mini_ctrl.html', '/tmp/ink_normal.png')
ib, inr = ink('/tmp/ink_bold.png'), ink('/tmp/ink_normal.png')
print(f"BOLD  weight={wb} ink={ib}")
print(f"NORM  weight={wn} ink={inr}")
print(f"delta = {ib - inr} px (+{100*(ib-inr)/max(inr,1):.1f}%) -> bold tebih tebal" if ib > inr else "NO DIFFERENCE — bold tidak berlaku")
