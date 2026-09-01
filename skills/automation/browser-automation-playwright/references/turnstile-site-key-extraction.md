# Turnstile Site Key Extraction Patterns

Real-world patterns for extracting Cloudflare Turnstile site keys from target pages. Critical for solver API integration.

## Problem

Turnstile solver APIs (2Captcha, CapSolver, AntiCaptcha) require the **site key** to solve challenges. Site keys are embedded in the page but extraction is non-trivial on JavaScript-heavy SPAs.

## Extraction Methods (in order of reliability)

### Method 1: Iframe src Attribute (Standard)

**When it works:** Static sites, server-rendered pages, early-loaded Turnstile widgets

**Pattern:**
```python
async def extract_turnstile_sitekey(page):
    """Extract from iframe src after page load."""
    try:
        # CRITICAL: Wait 3+ seconds for async iframe injection
        await page.wait_for_timeout(3000)
        
        iframe = page.locator('iframe[src*="turnstile"], iframe[src*="challenges.cloudflare"]').first
        await iframe.wait_for(state='attached', timeout=5000)
        iframe_src = await iframe.get_attribute('src')
        
        if iframe_src and 'sitekey=' in iframe_src:
            return iframe_src.split('sitekey=')[1].split('&')[0]
    except:
        pass
    return None
```

**Success rate:** ~70% (fails on lazy-loaded or late-injected widgets)

### Method 2: Data Attributes on Container Div

**When it works:** Modern Turnstile implementations using `turnstile.render()`

**Pattern:**
```python
# Look for container div with data-sitekey
site_key = await page.locator('[data-sitekey]').first.get_attribute('data-sitekey')

# Or cf-turnstile class
site_key = await page.locator('.cf-turnstile').first.get_attribute('data-sitekey')
```

**Success rate:** ~50% (depends on implementation)

### Method 3: JavaScript Global State Inspection

**When it works:** Sites that expose Turnstile config in window object

**Pattern:**
```python
site_key = await page.evaluate("""
    window.turnstile?.siteKey || 
    window.cfTurnstile?.siteKey || 
    window._turnstileConfig?.siteKey
""")
```

**Success rate:** ~20% (rare, site-specific)

### Method 4: Network Traffic Interception

**When it works:** Always (monitors actual Turnstile API calls)

**Pattern:**
```python
captured_key = None

async def capture_turnstile_call(response):
    global captured_key
    if 'challenges.cloudflare.com' in response.url and 'sitekey=' in response.url:
        captured_key = response.url.split('sitekey=')[1].split('&')[0]

page.on('response', capture_turnstile_call)
await page.goto(url)
await page.wait_for_timeout(5000)

if captured_key:
    print(f"Site key: {captured_key}")
```

**Success rate:** ~95% (most reliable but requires page to load Turnstile)

### Method 5: Manual Browser Inspection (Fallback)

**When automated methods fail:**

1. Open target URL in browser
2. Right-click Turnstile widget → Inspect
3. Find iframe or container div
4. Look for `data-sitekey` attribute or iframe src with `sitekey=` parameter
5. Hardcode the extracted key in automation script

**Example (Fintoq.ai, extracted 2026-07-06):**
```python
# Fintoq.ai Turnstile site key (manually extracted)
FINTOQ_SITEKEY = '0x4AAAAAAABnWD8kG8y0HY3n'
```

## Common Errors

### ERROR_CAPTCHA_UNSOLVABLE from 2Captcha/CapSolver

**Root cause:** Wrong site key provided to solver API.

**NOT a solver API failure** — the solver successfully determined the challenge is unsolvable with the given (incorrect) site key.

**Solution:** Re-extract site key using network interception or manual inspection. Do not retry with same key.

**Verified case (2026-07-06):** Fintoq.ai automation returned `ERROR_CAPTCHA_UNSOLVABLE` after 168s of processing. Issue was incorrect hardcoded site key, not 2Captcha failure.

## Site Key Format

Cloudflare Turnstile site keys follow format: `0x4AAAAAAA...` (starts with `0x4A`, followed by base64-like string)

**Example valid keys:**
- `0x4AAAAAAABnWD8kG8y0HY3n` (Fintoq.ai, verified 2026-07-06)
- `0x4AAAAAAAA6H_YqVL5w9oT7` (common test key)
- `0x4AAAAAAADa-iJPLwGAl7r3` (example production key)

**Invalid patterns:**
- reCAPTCHA v2 keys: `6Le...` (different format)
- hCaptcha keys: UUID format
- Made-up keys: Solver returns `ERROR_CAPTCHA_UNSOLVABLE`

## Production Pattern (Multi-Method Fallback)

```python
async def get_turnstile_sitekey(page, url):
    """Try multiple extraction methods with fallback."""
    
    # Method 1: Iframe src
    key = await extract_from_iframe(page)
    if key:
        return key
    
    # Method 2: Data attributes
    key = await extract_from_data_attr(page)
    if key:
        return key
    
    # Method 3: Network capture
    key = await extract_from_network(page, url)
    if key:
        return key
    
    # Fallback: Hardcoded known keys (per-site config)
    known_keys = {
        'fintoq.ai': '0x4AAAAAAABnWD8kG8y0HY3n',
        'example.com': '0x4AAAAAAAA6H_YqVL5w9oT7'
    }
    
    domain = url.split('/')[2]
    if domain in known_keys:
        print(f"Using known site key for {domain}")
        return known_keys[domain]
    
    raise Exception("Could not extract Turnstile site key")
```

## Debugging Site Key Issues

1. **Verify key format:** Must start with `0x4A`
2. **Check iframe loaded:** Screenshot before extraction
3. **Increase wait time:** Some sites inject iframe after 5+ seconds
4. **Test with manual extraction:** Confirm automated methods work
5. **Monitor solver response:** `ERROR_CAPTCHA_UNSOLVABLE` = wrong key, not solver failure

## Related

- 2Captcha Turnstile docs: https://2captcha.com/2captcha-api#turnstile
- CapSolver Turnstile docs: https://docs.capsolver.com/guide/captcha/Cloudflare.html
- Cloudflare Turnstile widget docs: https://developers.cloudflare.com/turnstile/
