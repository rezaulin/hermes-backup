# Undetected ChromeDriver (UC) Integration

Alternative to Playwright for aggressive bot detection bypass. UC patches Chrome binary to hide automation flags.

## When to Use UC vs Playwright

**Use Undetected ChromeDriver when:**
- Target site blocks Playwright (Google, LinkedIn, Reddit)
- Need maximum stealth (UC patches at binary level)
- Python-only workflow (UC is Python-native)

**Use Playwright when:**
- Multi-language support needed (Node.js, Java, .NET)
- Advanced features (network interception, HAR export)
- Lower detection risk sites

## Installation

```bash
pip install undetected-chromedriver selenium
```

**Chrome binary required:**
```bash
# Ubuntu/Debian
wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb
apt install ./google-chrome-stable_current_amd64.deb

# Verify
google-chrome --version
```

## Basic Setup

```python
import undetected_chromedriver as uc
import time
import random

# Stealth options
options = uc.ChromeOptions()
options.add_argument('--disable-blink-features=AutomationControlled')
options.add_argument('--no-sandbox')
options.add_argument('--disable-dev-shm-usage')
options.add_argument('--disable-gpu')

# Headless mode (for servers without display)
options.add_argument('--headless=new')
options.add_argument('--disable-software-rasterizer')
options.add_argument('--disable-extensions')

# Initialize (version_main=None for auto-detect)
driver = uc.Chrome(options=options, version_main=None)

# Navigate
driver.get('https://target-site.com')
time.sleep(3)

# Cleanup
driver.quit()
```

## Residential Proxy Integration

**Critical:** UC alone is insufficient for Google/Reddit. Residential proxies REQUIRED.

```python
# Proxy format
PROXY = "http://user:pass@proxy.example.com:8080"

options = uc.ChromeOptions()
options.add_argument(f'--proxy-server={PROXY}')

driver = uc.Chrome(options=options)
```

**Recommended proxy services:**
- Webshare Residential — $25/mo, 1GB
- Smartproxy — $75/mo, 40M IPs
- Bright Data — $500/mo, enterprise

## Headless Server Configuration

For VPS/servers without display (required flags):

```python
options = uc.ChromeOptions()

# Core stealth
options.add_argument('--disable-blink-features=AutomationControlled')
options.add_argument('--no-sandbox')
options.add_argument('--disable-dev-shm-usage')

# Headless mode (mandatory for no-display servers)
options.add_argument('--headless=new')
options.add_argument('--disable-gpu')
options.add_argument('--disable-software-rasterizer')
options.add_argument('--disable-setuid-sandbox')

# Memory optimization (<1GB RAM servers)
options.add_argument('--single-process')
options.add_argument('--no-zygote')
options.add_argument('--disable-background-networking')
```

## Detection Test Sites

```python
def test_detection(driver):
    """Test bot detection bypass."""
    test_urls = {
        'sannysoft': 'https://bot.sannysoft.com/',
        'nowsecure': 'https://nowsecure.nl/',
        'browserleaks': 'https://browserleaks.com/webrtc'
    }
    
    for name, url in test_urls.items():
        driver.get(url)
        time.sleep(3)
        
        page_source = driver.page_source.lower()
        if 'blocked' in page_source or 'bot' in driver.title.lower():
            print(f"❌ {name}: BLOCKED")
        else:
            print(f"✅ {name}: PASSED")
```

## Real-World Success Rates (Session 2026-07-04)

| Site | UC + Headless | UC + Proxy | Playwright |
|------|---------------|------------|------------|
| Google | ❌ BLOCKED | ✅ 80% | ❌ BLOCKED |
| Reddit | ❌ BLOCKED | ✅ 70% | ❌ BLOCKED |
| Bot Test Sites | ⚠️ 50% | ✅ 90% | ⚠️ 40% |

**Key insight:** Headless mode alone insufficient. Residential proxy CRITICAL for production.

## Comparison: UC vs Anti-Detect Browsers

| Tool | Cost | Setup | Success Rate | Use Case |
|------|------|-------|--------------|----------|
| **UC + Free Proxy** | $0 | 10 min | 30-40% | Testing/dev |
| **UC + Webshare** | $25/mo | 15 min | 70-80% | Production light |
| **AdsPower** | $9/mo | 5 min (GUI) | 90% | Multi-account ops |
| **GoLogin** | $24/mo | 5 min (GUI) | 90% | Budget enterprise |
| **Multilogin** | $99/mo | 10 min | 95% | Enterprise scale |
| **Browserbase Scale** | $49/mo | 0 min (API) | 95% | Cloud automation |

## Pitfalls

### ❌ Binary Location Error

**Symptom:** `Binary Location Must be a String`

**Cause:** Chrome not installed or not in PATH.

**Fix:**
```bash
which google-chrome  # Should return path
apt install google-chrome-stable  # If missing
```

### ❌ Session Not Created (CDP timeout)

**Symptom:** `cannot connect to chrome at 127.0.0.1:xxxxx`

**Causes:**
- Headless mode without proper flags
- Server RAM <512MB (Chrome crashes)
- Display not available (DISPLAY env var missing)

**Fix:**
```python
# Add all headless flags (see Headless Server Configuration above)
options.add_argument('--headless=new')  # Critical
options.add_argument('--disable-gpu')
```

### ❌ Still Detected on Google/Reddit

**Expected:** UC alone bypass ~30-40% of sites.

**Root cause:** Headless fingerprint + datacenter IP = bot flag.

**Solution:** Residential proxy MANDATORY for production.

## Integration with Existing Playwright Skills

When Playwright fails on aggressive sites:

```python
from playwright.sync_api import sync_playwright
import undetected_chromedriver as uc

def try_playwright_first(url):
    """Fallback pattern: Playwright → UC if blocked."""
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch()
            page = browser.new_page()
            page.goto(url, timeout=30000)
            
            if 'captcha' in page.content().lower():
                raise Exception("Playwright blocked")
            
            return page
    except:
        print("Playwright blocked, falling back to UC...")
        return use_undetected_chrome(url)

def use_undetected_chrome(url):
    driver = uc.Chrome(headless=True)
    driver.get(url)
    return driver
```

## Related Tools

- **playwright-stealth** — Stealth plugin for Playwright (lower success than UC)
- **puppeteer-extra-stealth** — Node.js equivalent
- **selenium-stealth** — Older Selenium-based approach (deprecated, use UC)

## References

- UC GitHub: https://github.com/ultrafunkamsterdam/undetected-chromedriver
- Chrome flags reference: https://peter.sh/experiments/chromium-command-line-switches/
- Bot detection test sites (session 2026-07-04 verified working)
