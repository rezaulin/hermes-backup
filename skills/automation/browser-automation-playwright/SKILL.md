---
name: browser-automation-playwright
description: Playwright browser automation for dynamic UIs, account creation, form filling, anti-detect patterns
triggers:
  - playwright
  - browser automation
  - headless browser
  - account creator
  - form filling
  - Material Design
  - anti-detect
  - stealth browser
  - account registration
  - signup automation
---

# Browser Automation with Playwright

Automate web interactions with Playwright for account creation, form filling, and dynamic UI manipulation. Covers anti-detect patterns, headless browser fingerprinting, and Material Design component handling.

## When to Use

- Automating account signups (Gmail, social media, services)
- Filling forms with dynamic JavaScript components
- Bypassing bot detection with stealth patterns
- Mass account creation workflows
- Testing signup flows programmatically

## Prerequisites

```bash
pip install playwright playwright-stealth faker
playwright install chromium
```

## Core Patterns

### 1. Stealth Browser Setup

```python
from playwright.sync_api import sync_playwright

def launch_stealth_browser(headless=True, proxy=None):
    playwright = sync_playwright().start()
    
    args = [
        '--disable-blink-features=AutomationControlled',
        '--disable-dev-shm-usage',
        '--no-sandbox',
        '--disable-setuid-sandbox',
        '--disable-web-security',
        '--disable-features=IsolateOrigins,site-per-process',
        '--disable-gpu',
        '--single-process',  # Low memory mode
        '--no-zygote',
        '--disable-software-rasterizer'
    ]
    
    launch_opts = {
        'headless': headless,
        'args': args,
        'timeout': 60000
    }
    
    if proxy:
        launch_opts['proxy'] = {
            'server': f"{proxy['protocol']}://{proxy['host']}:{proxy['port']}",
            'username': proxy.get('username'),
            'password': proxy.get('password')
        }
    
    browser = playwright.chromium.launch(**launch_opts)
    context = browser.new_context(
        viewport={'width': 1366, 'height': 768},
        user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        locale='en-US',
        timezone_id='America/New_York'
    )
    
    return playwright, browser, context
```

### 2. Material Design Dropdown Handling

**Problem:** Material Design uses JavaScript-rendered dropdowns (`div[role="listbox"]`), not native `<select>`. Standard `.select_option()` fails.

**Solution:** Keyboard navigation instead of click.

```python
def fill_material_dropdown(page, dropdown_index, option_index):
    """
    Fill Material Design dropdown via keyboard navigation.
    
    Args:
        page: Playwright page object
        dropdown_index: 0-based index if multiple dropdowns (use .nth(N))
        option_index: 1-based option number (1 = first option)
    """
    try:
        # Wait for overlays/spinners to disappear
        time.sleep(random.uniform(2, 3))
        
        # Click dropdown trigger (force through overlays)
        if dropdown_index == 0:
            dropdown = page.locator('div[role="listbox"]').first
        else:
            dropdown = page.locator('div[role="listbox"]').nth(dropdown_index)
        
        dropdown.click(force=True, timeout=5000)
        time.sleep(random.uniform(1, 2))
        
        # Navigate to option using Arrow keys
        for _ in range(option_index - 1):
            page.keyboard.press('ArrowDown')
            time.sleep(0.1)
        
        page.keyboard.press('Enter')
        time.sleep(random.uniform(1, 2))
        return True
    except Exception as e:
        print(f"Dropdown error: {e}")
        return False
```

### 3. Human-Like Typing

```python
import random
import time

def human_typing(page, selector, text, min_delay=0.05, max_delay=0.15):
    """Type with random delays to mimic human behavior."""
    element = page.locator(selector)
    element.click()
    
    for char in text:
        element.type(char)
        time.sleep(random.uniform(min_delay, max_delay))
```

### 4. Random Mouse Movement

```python
def random_mouse_movement(page):
    """Simulate random mouse movement to appear human."""
    viewport = page.viewport_size
    x = random.randint(100, viewport['width'] - 100)
    y = random.randint(100, viewport['height'] - 100)
    page.mouse.move(x, y)
```

## Pitfalls & Solutions

### ❌ Pitfall: Timeout on `div[role="listbox"]` click

**Symptom:** `Locator.click: Timeout 5000ms exceeded` on Material Design dropdowns.

**Causes:**
- Overlays/loading spinners blocking clicks
- Dropdown structure changes per session (A/B testing)
- Page not fully loaded

**Solutions:**
1. **Increase wait time** before click: `time.sleep(3)` after page navigation
2. **Use `force=True`** to bypass overlay checks: `dropdown.click(force=True)`
3. **Fallback to keyboard navigation**: Tab to field → ArrowDown → Enter
4. **Debug with screenshot**: `page.screenshot(path='debug.png')` before click

### ❌ Pitfall: Modal overlay blocking button clicks

**Symptom:** `Locator.click: Timeout exceeded` with error message like `<button aria-label="Dismiss referral"> from <div class="fixed inset-0 z-50"> subtree intercepts pointer events`

**Cause:** Modal/dialog/referral overlays with high z-index backdrop blocking interaction with underlying page elements.

**Solutions (in order of preference):**
1. **Dismiss modal first with force click:**
   ```python
   try:
       dismiss_btn = page.locator('button[aria-label="Dismiss"], [role="dialog"] button').first
       dismiss_btn.click(timeout=3000, force=True)
       time.sleep(1)
   except:
       pass  # Modal not present
   ```

2. **JavaScript force-click if UI click fails:**
   ```python
   page.evaluate("document.querySelector('[aria-label=\"Dismiss\"]')?.click()")
   time.sleep(1)
   ```

3. **Remove URL parameters that trigger modals:**
   - Example: `https://example.com/s/REFERRAL` → `https://example.com`
   - Referral codes often trigger persistent accept/dismiss dialogs

4. **Click with force=True on target button** (bypasses overlay checks but may not work with complex z-index stacking):
   ```python
   target_btn.click(force=True, timeout=10000)
   ```

**Debugging:** Take screenshot before click to verify modal state: `page.screenshot(path='before_click.png')`

### ❌ Pitfall: Twitter OAuth popup timeout

**Symptom:** `Timeout 30000ms exceeded while waiting for event "page"` when expecting Twitter/X OAuth popup after clicking "Connect X" button.

**Causes:**
- OAuth popup blocked by browser popup blocker
- Site already has OAuth token cached (no popup needed)
- Network delay or slow OAuth provider response
- Page navigation instead of popup window

**Solutions:**
1. **Extend popup timeout** (default 30s often insufficient):
   ```python
   with page.context.expect_page(timeout=45000) as popup_info:
       twitter_page = popup_info.value
   ```

2. **Check if already authorized** (redirect back immediately):
   ```python
   with page.context.expect_page(timeout=45000) as popup_info:
       twitter_page = popup_info.value
       if 'original-site.com' in twitter_page.url:
           # Already authorized, redirected back
           return True
   ```

3. **Fallback: Check for "connected" indicator** on main page if popup fails:
   ```python
   except Exception as popup_err:
       try:
           connected = page.locator('text=Connected, svg[class*="check"]').first
           if connected.is_visible(timeout=2000):
               return True  # Already connected
           else:
               raise popup_err
       except:
           raise popup_err
   ```

4. **Increase wait before click** (give JS time to bind handlers):
   ```python
   connect_btn.click(timeout=10000)
   time.sleep(3)  # Wait for popup trigger
   ```

**Debugging:** Check browser console for popup blocker warnings or JavaScript errors that prevent popup.

**Symptom:** `BrowserType.launch: Timeout 180000ms exceeded` on servers with <500MB RAM.

**Solution:** Use low-memory flags:
```python
'--single-process',  # Critical for <1GB RAM
'--no-zygote',
'--disable-gpu',
'--disable-software-rasterizer'
```

Reduce launch timeout: `timeout: 60000` (60s instead of 180s).

### ❌ Pitfall: Page.goto timeout waiting for 'networkidle'

**Symptom:** `Page.goto: Timeout 30000ms exceeded` when using `wait_until='networkidle'`. Page partially loads (CSS/images captured) but never reaches idle state.

**Cause:** Modern SPAs with continuous background polling, analytics beacons, or WebSocket connections never reach true network idle. The `networkidle` strategy waits for 500ms of no network activity — impossible on pages with live features.

**Solution:** Use `wait_until='domcontentloaded'` instead:

```python
# WRONG: Times out on dynamic pages
await page.goto(url, wait_until='networkidle', timeout=30000)

# CORRECT: Returns as soon as DOM is ready
await page.goto(url, wait_until='domcontentloaded', timeout=30000)
await page.wait_for_timeout(3000)  # Manual wait for JS hydration
```

**When to use each:**
- `'domcontentloaded'` (recommended): Fast, reliable, works on 95% of sites. Add manual `wait_for_timeout(2-5s)` if elements render late.
- `'networkidle'`: Only for static sites or when you need ALL resources loaded (rare). High failure rate on modern SPAs.
- `'load'`: Middle ground — waits for window.onload. Use when DOMContentLoaded fires too early but networkidle times out.

**Verified session 2026-07-06:** Fintoq.ai signup automation failed consistently with `networkidle` (30s timeout), succeeded immediately with `domcontentloaded + 3s manual wait`.

### ❌ Pitfall: Gmail blocks headless browser

**Symptom:** Page loads but never reaches completion, timeouts after 120s.

**Causes:**
- Google detects headless Chrome fingerprint
- Server IP flagged for bot activity
- Missing WebGL/Canvas fingerprint randomization

**Solutions:**
1. **Use residential proxies** (not datacenter IPs)
2. **Add playwright-stealth**: Patches Playwright to evade detection
3. **Rotate user agents**: Randomize per session
4. **Consider undetected-chromedriver** for aggressive sites (Gmail, LinkedIn)

### ❌ Pitfall: Input field not found after form submission

**Symptom:** `Locator.click: Timeout 30000ms exceeded` on `input[name="Username"]` after clicking Next.

**Cause:** Previous form validation failed (e.g., birth date not filled), script thinks it advanced but is still on same page.

**Solution:**
1. **Verify page URL** after navigation: `assert 'signup' in page.url`
2. **Check for error messages**: `page.locator('text="Invalid"').count() == 0`
3. **Screenshot on failure**: Save debug images to diagnose state

## Low-Memory Server Optimization

For VPS with <512MB available RAM:

```python
launch_opts = {
    'headless': True,
    'args': [
        '--disable-blink-features=AutomationControlled',
        '--disable-dev-shm-usage',
        '--no-sandbox',
        '--disable-gpu',
        '--single-process',      # CRITICAL: Run in single process
        '--no-zygote',           # No separate zygote process
        '--disable-software-rasterizer',
        '--disable-background-networking',
        '--disable-default-apps',
        '--disable-extensions',
        '--disable-sync'
    ],
    'timeout': 60000  # Reduce from default 180s
}
```

Check available memory before launch:
```bash
free -h  # If <400MB available, automation may be unstable
```

## CAPTCHA Integration

### reCAPTCHA v2 (2captcha)

```python
from twocaptcha import TwoCaptcha

def solve_recaptcha(sitekey, page_url, api_key):
    solver = TwoCaptcha(api_key)
    result = solver.recaptcha(sitekey=sitekey, url=page_url)
    return result['code']  # Token to inject

# Inject token into page
token = solve_recaptcha(sitekey, page.url, api_key)
page.evaluate(f'document.getElementById("g-recaptcha-response").innerHTML="{token}";')
page.evaluate('onSubmit();')  # Trigger form submission
```

### Cloudflare Turnstile (2Captcha)

**2Captcha Turnstile support:** Reliable API with good Turnstile coverage (~$0.003/solve, 85-90% success rate).

```python
import requests
import time

def solve_turnstile_2captcha(site_url, site_key, api_key):
    """
    Solve Cloudflare Turnstile using 2Captcha API.
    
    Args:
        site_url: Full page URL where Turnstile appears
        site_key: Turnstile sitekey (extract from iframe src)
        api_key: 2Captcha API key from 2captcha.com
    
    Returns:
        str: Solution token to inject
    
    Raises:
        Exception: If solve fails or times out
    """
    # Submit captcha task
    submit_params = {
        'key': api_key,
        'method': 'turnstile',
        'sitekey': site_key,
        'pageurl': site_url,
        'json': 1
    }
    
    response = requests.get('https://2captcha.com/in.php', params=submit_params, timeout=30)
    result = response.json()
    
    if result.get('status') != 1:
        raise Exception(f"2Captcha submit error: {result.get('request', 'Unknown error')}")
    
    task_id = result['request']
    
    # Poll for solution (max 3 minutes)
    for attempt in range(60):
        time.sleep(3)
        
        result_params = {
            'key': api_key,
            'action': 'get',
            'id': task_id,
            'json': 1
        }
        
        result_response = requests.get('https://2captcha.com/res.php', params=result_params, timeout=10)
        result_data = result_response.json()
        
        if result_data.get('status') == 1:
            return result_data['request']
        elif result_data.get('request') == 'CAPCHA_NOT_READY':
            continue
        else:
            raise Exception(f"2Captcha error: {result_data.get('request', 'Unknown')}")
    
    raise Exception("2Captcha timeout - captcha not solved in 3 minutes")
```

**Usage:**
```python
# Solve Turnstile
token = solve_turnstile_2captcha(page.url, site_key, TWOCAPTCHA_API_KEY)

# Inject solution token
await page.evaluate(f"""
    const input = document.querySelector('input[name="cf-turnstile-response"]');
    if (input) {{
        input.value = '{token}';
        input.dispatchEvent(new Event('input', {{ bubbles: true }}));
    }}
""")
await page.wait_for_timeout(1000)
```

**Setup:** Sign up at https://2captcha.com/ → Dashboard → Copy API key → Top up minimum $3

**Common errors:**
- `ERROR_CAPTCHA_UNSOLVABLE`: Wrong site key (extract from actual iframe, don't guess)
- `ERROR_WRONG_USER_KEY`: Invalid API key
- `ERROR_ZERO_BALANCE`: Top up account

**Verified session 2026-07-06:** 2Captcha successfully integrated for Fintoq.ai Turnstile automation.

### Cloudflare Turnstile (CapSolver)

**Preferred for Turnstile:** CapSolver has better Turnstile support than 2captcha (~$0.002/solve, 95%+ success rate).

```python
import requests
import time

def solve_turnstile(site_url, site_key, api_key):
    """
    Solve Cloudflare Turnstile using CapSolver API.
    
    Args:
        site_url: Full page URL where Turnstile appears
        site_key: Turnstile sitekey (extract from iframe src)
        api_key: CapSolver API key from capsolver.com
    
    Returns:
        str: Solution token to inject
    
    Raises:
        Exception: If solve fails or times out
    """
    # Create task
    create_payload = {
        "clientKey": api_key,
        "task": {
            "type": "AntiTurnstileTaskProxyLess",
            "websiteURL": site_url,
            "websiteKey": site_key
        }
    }
    
    response = requests.post(
        'https://api.capsolver.com/createTask',
        json=create_payload,
        timeout=30
    )
    data = response.json()
    
    if data.get('errorId') != 0:
        raise Exception(f"CapSolver error: {data.get('errorDescription')}")
    
    task_id = data['taskId']
    
    # Poll for solution (max 2 minutes)
    for _ in range(60):
        time.sleep(2)
        
        result_payload = {
            "clientKey": api_key,
            "taskId": task_id
        }
        
        result = requests.post(
            'https://api.capsolver.com/getTaskResult',
            json=result_payload,
            timeout=10
        )
        result_data = result.json()
        
        if result_data.get('status') == 'ready':
            return result_data['solution']['token']
        elif result_data.get('status') == 'failed':
            raise Exception(f"Task failed: {result_data.get('errorDescription')}")
    
    raise Exception("Turnstile solve timeout after 120s")

# Extract site key from Turnstile iframe
async def extract_turnstile_sitekey(page):
    """
    Extract Turnstile sitekey from iframe src attribute.
    
    CRITICAL: Wait 3+ seconds after page load for iframe to render.
    Turnstile iframe loads asynchronously via JavaScript injection.
    """
    try:
        # Wait for Turnstile iframe to load (critical timing)
        await page.wait_for_timeout(3000)
        
        iframe_locator = page.locator('iframe[src*="turnstile"], iframe[src*="challenges.cloudflare.com"]').first
        await iframe_locator.wait_for(state='attached', timeout=5000)
        iframe_src = await iframe_locator.get_attribute('src')
        
        if iframe_src and 'sitekey=' in iframe_src:
            return iframe_src.split('sitekey=')[1].split('&')[0]
    except:
        pass
    return None

# Usage in Playwright async flow
site_key = await extract_turnstile_sitekey(page)
if not site_key:
    raise Exception("Could not find Turnstile sitekey")

# Solve Turnstile
token = solve_turnstile(page.url, site_key, CAPSOLVER_API_KEY)

# Inject solution token
await page.evaluate(f"""
    document.querySelector('input[name="cf-turnstile-response"]').value = '{token}';
""")
await page.wait_for_timeout(1000)

# Submit form
await page.click('button:has-text("Sign Up")')
```

**Cost:** ~$0.002 per solve (10 accounts = $0.02, 100 accounts = $0.20)

**Setup:** Sign up at https://capsolver.com/ → Dashboard → Copy API key → Top up minimum $2

**Complete integration guide:** See `references/cloudflare-turnstile-capsolver.md` for full API reference, error handling, proxy support, and cost optimization strategies.

### AntiCaptcha API Connectivity Issues

**Symptom:** `Connection to api.anti-captcha.com timed out (connect timeout=10s)` when calling AntiCaptcha API for Turnstile solving.

**Cause:** Network-level connectivity issues — server firewall, ISP blocking, or AntiCaptcha infrastructure downtime. Not an API key problem.

**Diagnosis:**
```bash
# Test connectivity
curl -X POST https://api.anti-captcha.com/getBalance \
  -H 'Content-Type: application/json' \
  -d '{"clientKey":"YOUR_KEY"}' \
  --max-time 10

# If timeout occurs, AntiCaptcha is unreachable from your environment
```

**Solutions:**
1. **Switch to 2Captcha** (more reliable infrastructure):
   - API: `https://2captcha.com/in.php` (create task)
   - Supports Turnstile via `method=turnstile`
   - Similar pricing: ~$0.003/solve

2. **Switch to CapSolver** (recommended for Turnstile):
   - API: `https://api.capsolver.com/createTask`
   - Better Turnstile success rate (95%+ vs 85% for others)
   - Pricing: ~$0.002/solve

3. **Use HTTP proxy** if direct connection blocked:
   - Route requests through proxy: `requests.post(url, proxies={'https': 'http://proxy:port'})`
   - Verify proxy can reach `api.anti-captcha.com`

4. **Increase timeout** (only if API occasionally responds):
   ```python
   response = requests.post(url, json=payload, timeout=30)  # Up from 10s
   ```

**DO NOT hardcode "AntiCaptcha does not work"** — this is an environment/network issue, not a tool limitation. Always provide fallback to alternative solver APIs.

**Verified session 2026-07-06:** AntiCaptcha API unreachable from user's VPS (both keys tested, both timed out). CapSolver recommended as replacement.

## Multi-Account Farming Bot Architecture

When the task is farming N accounts at scale (trial credits, API keys, registrations), a naive sequential loop is slow and fragile. Reuse this battle-tested shape (from a verified 2026-08 CodeBuddy CN farmer).

### Core improvements over a naive loop

| Naive Loop | Farm-ready |
|-----------|-----------|
| Sequential, 1 at a time | **Async worker pool** + semaphore |
| 1 fixed proxy | **Proxy rotation** from a list file (round-robin per account) |
| Buy number once, hard-fail | **Country fallback pool** on SMS provider |
| Save all at the end (loss on crash) | **Incremental JSONL append** per account + CSV rebuild |
| No delay between accounts | Random jitter (rate-limit avoidance) |
| OTP regex fragile | Robust 6-digit extraction |

### Async worker pool (the load-bearing pattern)

```python
import asyncio
from dataclasses import asdict

async def main():
    sem = asyncio.Semaphore(max(1, workers))        # cap concurrent browser tabs
    results: asyncio.Queue = asyncio.Queue()
    async with aiohttp.ClientSession() as session:
        tasks = [asyncio.create_task(run_account(session, sem, proxies, i, results))
                 for i in range(count)]
        # incremental saver — crash-safe, never lose completed accounts
        async def saver():
            while True:
                r = await results.get()
                if r is None:
                    break
                with open(jsonl_path, "a") as f:
                    f.write(json.dumps(asdict(r), ensure_ascii=False) + "\n")
        writer = asyncio.create_task(saver())
        await asyncio.gather(*tasks, return_exceptions=True)  # one failure ≠ kill batch
        await results.put(None)
        await saver()
```

### Proxy rotation

```python
def load_proxies(arg_or_env) -> list[str]:
    # accept a file path (one per line, # comments skipped), a single literal, or empty
def pick_proxy(proxies, idx) -> str:
    return proxies[idx % len(proxies)] if proxies else ""   # round-robin
```
**Rule:** one account = one IP when the target correlates accounts. Rotating proxies is mandatory for production; a single re-used IP across all accounts is how they all get banned together.

### SMS-OTP provider (5SIM) with country fallback

```python
COUNTRY_POOL = ["hongkong", "malaysia", "singapore"]   # try in order
# buy:    GET /user/buy/activation/{country}/any/{service}
# poll:   GET /user/check/{id} → {"sms": [{"text": "..."}]}
# finish: GET /user/finish/{id}
# cancel: GET /user/cancel/{id}   (call on ANY exception, then re-raise)
```
Out-of-stock = 4xx with "quantity" in body → try next country. On hard failure: cancel the order then `raise` so the worker records it and moves on — don't leak paid numbers.

### ⚠️ Pre-flight probe the SMS/backend endpoints BEFORE a mass run

Farmer scripts hardcode API paths that **drift over time**. A script that "compiled fine" can be dead at runtime because the provider moved an endpoint — a fresh install/runtime check passing does NOT mean the backend contract is still valid. Always probe the paid/SMS dependency before spending money or burning N numbers, not after.

**The 5SIM probe (2026-08 verified):**

```bash
TOKEN="<token>"
# balance endpoint moved from /v1/user/balance to /v1/user/profile
curl -s https://5sim.net/v1/user/profile -H "Authorization: Bearer $TOKEN" -H "Accept: application/json"
# → {"id":..., "balance":0.1085, "rating":96, ...}   ← 200 = live
# /v1/user/balance now returns 302 first, then SPA 404 — obsolete, do not rely on it
```

Quick route-health sweep — useful for any SMS provider, not just 5SIM:

```bash
for ep in "v1/user/balance" "v1/user/profile" "v1/user/buy/activation/hongkong/any/openai"; do
  code=$(curl -s -o /dev/null -w "%{http_code}" --max-time 12 "https://5sim.net/$ep" \
    -H "Authorization: Bearer $TOKEN" -H "Accept: application/json")
  echo "$ep -> $code"
done
# 200 = live endpoint; 302/404 = moved/removed → re-read docs before trusting the script
```

**Probing a buy route without actually buying:** issue the buy GET for a **fake/not-offered service name** — an invalid `{operator}` returns 400, a real one returns 200 (or a real order). This confirms the URL *shape* (country/operator) is correct without spending balance. Check `balance ≥` order cost first: `last_top_orders` in the profile payload shows what prior orders cost (e.g. `codebuddy:...:0.13`) — if balance is below that, every buy will fail with 400 before it even reaches the service.

**Checklist before any `--count` run:**
1. `python -m py_compile script.py` + import the deps (fast syntactic/runtime sanity).
2. Token valid? Decode the JWT `exp` claim (or hit the profile endpoint) — don't trust the literal.
3. Balance ≥ cost of one order (from `balance` + `last_top_orders`).
4. Every hardcoded provider endpoint returns 2xx — probe them, don't assume.
5. Proxy reachable (a `curl -x proxy https://httpbin.org/ip` returning 403 proves the tunnel works; 403 from the echo target is fine — connectivity validated).
6. Deploy the local agent deps (cloakbrowser launch signature etc.) match how the script calls them — check `inspect.signature` if unsure.

### Robust OTP extraction (5SIM style "prefix + code")

```python
import re
# SMS like "[CodeBuddy]494994為您的登入驗證碼..."
m = re.search(r"[>\]\s](\d{6})", text)      # digits right after ]
if not m: m = re.search(r"\b(\d{6})\b", text)
if not m:
    groups = re.findall(r"(\d+)", text)
    groups.sort(key=len, reverse=True)       # fallback: longest digit run
    m = groups[0] if groups else None
```

### API call with retry (only transient codes)

```python
if resp.status in (429,) or resp.status >= 500:
    if attempt < retries - 1:
        await asyncio.sleep(2 * (attempt + 1)); continue
raise RuntimeError(...)   # 4xx = real error, fail fast, don't retry
```

### Crash-safe output
- Append one JSON line per completed account to `.jsonl` (never lose progress)
- At end, rebuild `.csv` from the JSONL for a human-readable sheet
- Record failures as `AccountResult(error=...)` in the same stream so pass/fail ratio is visible

## Network Traffic Interception

**Use case:** Capture API responses during signup/login flows to extract leaked data (OTP codes, tokens, session IDs).

### Async Playwright Pattern

```python
async def capture_api_responses(account_id):
    """Intercept and log all API responses during automation."""
    api_calls = []
    leaked_otp = None
    
    async def handle_response(response):
        nonlocal api_calls, leaked_otp
        url = response.url
        
        # Filter API calls only
        if '/api/' in url or 'auth' in url.lower():
            try:
                body = await response.text()
                api_calls.append({
                    'url': url,
                    'status': response.status,
                    'body': body
                })
                
                print(f"[{account_id}] API captured: {url}")
                
                # Try to extract OTP/verification codes
                try:
                    json_body = json.loads(body)
                    
                    # Common OTP field names
                    for key in ['otp', 'code', 'verification_code', 'verificationCode', 
                               'token', 'verify_token', 'email_code']:
                        if key in json_body:
                            leaked_otp = {
                                'otp': str(json_body[key]),
                                'source': url,
                                'full_response': json_body
                            }
                            print(f"[{account_id}] 🔥 OTP LEAKED: {leaked_otp['otp']}")
                            break
                except json.JSONDecodeError:
                    pass  # Not JSON response
            except Exception as e:
                print(f"[{account_id}] Response capture failed: {e}")
    
    return handle_response, api_calls, leaked_otp

# Usage
async with async_playwright() as p:
    browser = await p.chromium.launch(headless=True)
    page = await browser.new_page()
    
    # Setup interception BEFORE navigation
    handler, api_calls, leaked_otp = await capture_api_responses('account_1')
    page.on('response', handler)
    
    # Navigate and perform actions
    await page.goto('https://example.com/signup')
    await page.fill('input[name="email"]', 'test@example.com')
    await page.click('button:has-text("Sign Up")')
    await page.wait_for_timeout(5000)
    
    # Check captured data
    if leaked_otp:
        print(f"OTP extracted: {leaked_otp['otp']}")
    else:
        print(f"No OTP found. Captured {len(api_calls)} API calls")
        for call in api_calls:
            print(f"  - {call['url']} -> {call['status']}")
```

### Key Points

- **Attach handler BEFORE page.goto()** — responses triggered during navigation won't be captured if handler is late
- **Async handlers required** — `await response.text()` blocks, use `async def handle_response`
- **Filter URLs** — capture only `/api/` or auth-related endpoints to reduce noise
- **Non-JSON responses** — wrap `json.loads()` in try/except, some APIs return HTML on error
- **Leaked data extraction** — OTP/tokens often appear in signup/verification API responses (security vulnerability)

### Common OTP Response Patterns

```json
// Pattern 1: Direct field
{"success": true, "otp": "123456", "user_id": "abc"}

// Pattern 2: Nested
{"data": {"verification_code": "123456", "expires_in": 300}}

// Pattern 3: Email verification response
{"email_sent": true, "code": "123456", "message": "Check your email"}
```

**Security Note:** Leaking OTP in API responses is a security vulnerability. Exploiting this for mass automation bypasses email verification entirely.

## Debugging Workflow

1. **Start non-headless**: `headless=False` to see what browser sees
2. **Add screenshots**: `page.screenshot(path=f'step_{N}.png')` at each step
3. **Dump HTML**: `page.content()` to file for selector debugging
4. **Check console errors**: `page.on('console', lambda msg: print(msg.text))`
5. **Slow down**: Add `time.sleep(2)` between actions to observe flow
6. **Network tab**: Use `page.on('response', handler)` to log all API calls

## References

- Playwright Python docs: https://playwright.dev/python/docs/intro
- playwright-stealth: https://github.com/AtuboDad/playwright_stealth
- Material Design components: CSS classes `VfPpkd-*` (Google's MDC)
- 2captcha API: https://2captcha.com/2captcha-api

## Research Phase vs Automation Phase

**This skill excels at AUTOMATION (target known), not RESEARCH (discovery).**

When user requests require external research before automation:
- Hermes browser tools hit bot detection on major sites (Google, Reddit, OpenAI, Twitter)
- **Fail fast** (2-3 attempts max) when research is systematically blocked
- **Pivot** to user-provided intel, knowledge base answers, or build-first approaches

See `references/research-bot-detection-patterns.md` for detailed fallback strategies and real session examples.

## Alternative: Undetected ChromeDriver

For aggressive bot detection (Google, LinkedIn, Reddit), see `references/undetected-chromedriver.md` — UC patches Chrome binary for maximum stealth.

**CRITICAL (verified session 2026-07-04):** UC alone achieves only ~30-40% bypass rate on major sites. **Residential proxies MANDATORY for production** (datacenter IPs fail even with UC). Success rate jumps to 70-90% with residential proxy ($25-50/mo services like Webshare/Smartproxy).

## Support Files

- `references/qoder-trial-farm-intel.md` - Qoder Pro trial recon: device-code OAuth discovery + reusable CLI-trial recon technique (2026-08-23)
- `references/cloudflare-turnstile-capsolver.md` - CapSolver API integration guide
- `references/turnstile-site-key-extraction.md` - Site key extraction patterns & troubleshooting (2026-07-06)
- `references/research-bot-detection-patterns.md` - Bot detection fallback strategies
- `references/undetected-chromedriver.md` - UC setup for aggressive detection

## Related Skills

- `m4` (automation/cron) - Schedule account creation jobs
- `m12` (batch/parallel) - Run multiple browsers concurrently
- `hermes/browser.md` - Web3 dApp automation patterns
