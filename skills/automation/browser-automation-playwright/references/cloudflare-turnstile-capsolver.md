# Cloudflare Turnstile Integration with CapSolver

Complete reference for automating Cloudflare Turnstile challenges using CapSolver API in Playwright workflows.

## Overview

**CapSolver** is the recommended solver for Cloudflare Turnstile (better success rate than 2captcha for Turnstile specifically).

- **Success Rate:** 95%+ on standard Turnstile
- **Cost:** ~$0.002 per solve
- **Response Time:** 5-15 seconds average
- **Provider:** https://capsolver.com/

## Setup

### 1. Create CapSolver Account

```bash
# Visit https://capsolver.com/
# Sign up → Dashboard → API Key (copy)
# Add funds: Minimum $2 (covers ~1000 solves)
```

### 2. Install Dependencies

```bash
pip install playwright requests
playwright install chromium
```

### 3. Configuration

```python
CAPSOLVER_API_KEY = 'CAP-XXXXXXXXXXXXXXXXXXXXXXXX'  # From dashboard
CAPSOLVER_CREATE_URL = 'https://api.capsolver.com/createTask'
CAPSOLVER_RESULT_URL = 'https://api.capsolver.com/getTaskResult'
```

## Implementation

### Extract Turnstile Site Key

Turnstile site key is embedded in the iframe `src` attribute:

```python
async def extract_turnstile_sitekey(page):
    """
    Extract Turnstile sitekey from iframe.
    
    Returns:
        str: Site key (e.g., '0x4AAAAAAAB...')
        None: If iframe not found
    """
    try:
        # Wait for Turnstile iframe to load
        await page.wait_for_selector('iframe[src*="turnstile"]', timeout=10000)
        
        # Get iframe src attribute
        iframe_src = await page.locator('iframe[src*="turnstile"]').first.get_attribute('src')
        
        # Extract sitekey parameter
        if 'sitekey=' in iframe_src:
            site_key = iframe_src.split('sitekey=')[1].split('&')[0]
            return site_key
    except Exception as e:
        print(f"Failed to extract site key: {e}")
    
    return None
```

### Solve Turnstile Challenge

```python
import requests
import time

def solve_turnstile(site_url, site_key, api_key):
    """
    Solve Cloudflare Turnstile using CapSolver API.
    
    Args:
        site_url (str): Full URL of page with Turnstile (e.g., 'https://example.com/signup')
        site_key (str): Turnstile sitekey extracted from iframe
        api_key (str): CapSolver API key
    
    Returns:
        str: Solution token to inject into page
    
    Raises:
        Exception: If solve fails or times out
    """
    # Step 1: Create solve task
    create_payload = {
        "clientKey": api_key,
        "task": {
            "type": "AntiTurnstileTaskProxyLess",  # Use proxy version if needed
            "websiteURL": site_url,
            "websiteKey": site_key
        }
    }
    
    try:
        response = requests.post(
            'https://api.capsolver.com/createTask',
            json=create_payload,
            timeout=30
        )
        response.raise_for_status()
        data = response.json()
    except Exception as e:
        raise Exception(f"Failed to create task: {e}")
    
    # Check for API errors
    if data.get('errorId') != 0:
        error_code = data.get('errorCode', 'UNKNOWN')
        error_desc = data.get('errorDescription', 'No description')
        raise Exception(f"CapSolver API error [{error_code}]: {error_desc}")
    
    task_id = data.get('taskId')
    if not task_id:
        raise Exception("No task ID returned from CapSolver")
    
    # Step 2: Poll for solution (max 2 minutes)
    for attempt in range(60):
        time.sleep(2)
        
        result_payload = {
            "clientKey": api_key,
            "taskId": task_id
        }
        
        try:
            result_response = requests.post(
                'https://api.capsolver.com/getTaskResult',
                json=result_payload,
                timeout=10
            )
            result_response.raise_for_status()
            result_data = result_response.json()
        except Exception as e:
            print(f"Poll attempt {attempt + 1} failed: {e}")
            continue
        
        status = result_data.get('status')
        
        if status == 'ready':
            # Solution ready
            solution = result_data.get('solution', {})
            token = solution.get('token')
            if token:
                return token
            else:
                raise Exception("Solution ready but no token in response")
        
        elif status == 'failed':
            # Task failed
            error_desc = result_data.get('errorDescription', 'Unknown error')
            raise Exception(f"Task failed: {error_desc}")
        
        elif status == 'processing':
            # Still processing, continue polling
            continue
        
        else:
            print(f"Unknown status: {status}")
            continue
    
    # Timeout after 60 attempts (120 seconds)
    raise Exception("Turnstile solve timeout after 120 seconds")
```

### Inject Solution and Submit

```python
async def solve_and_submit_turnstile(page, site_url, api_key):
    """
    Complete Turnstile solve workflow in Playwright.
    
    Args:
        page: Playwright page object
        site_url: Current page URL
        api_key: CapSolver API key
    
    Returns:
        bool: True if solved and submitted successfully
    """
    try:
        # Extract site key
        site_key = await extract_turnstile_sitekey(page)
        if not site_key:
            raise Exception("Could not extract Turnstile site key")
        
        print(f"Site key: {site_key}")
        
        # Solve via CapSolver
        print("Solving Turnstile...")
        token = solve_turnstile(site_url, site_key, api_key)
        print(f"Turnstile solved! Token: {token[:20]}...")
        
        # Inject solution token
        await page.evaluate(f"""
            // Turnstile response is stored in hidden input
            const input = document.querySelector('input[name="cf-turnstile-response"]');
            if (input) {{
                input.value = '{token}';
            }} else {{
                console.error('Turnstile response input not found');
            }}
        """)
        
        # Wait for injection to complete
        await page.wait_for_timeout(1000)
        
        # Submit form
        await page.click('button[type="submit"], button:has-text("Sign Up")')
        
        return True
        
    except Exception as e:
        print(f"Turnstile solve failed: {e}")
        return False
```

## Common Errors

### Error: `errorCode: ERROR_INVALID_TASK_DATA`

**Cause:** Invalid site key or site URL format.

**Solution:**
- Verify site key extraction: `print(site_key)`
- Ensure URL is full path: `https://example.com/signup` (not just `example.com`)
- Check iframe is loaded before extraction

### Error: `errorCode: ERROR_KEY_DOES_NOT_EXIST`

**Cause:** Invalid or expired API key.

**Solution:**
- Verify API key from dashboard: https://capsolver.com/dashboard
- Check for typos or extra spaces
- Regenerate API key if necessary

### Error: `errorCode: ERROR_ZERO_BALANCE`

**Cause:** Insufficient CapSolver account balance.

**Solution:**
- Check balance: https://capsolver.com/dashboard
- Top up minimum $2

### Error: Task status remains `processing` indefinitely

**Cause:** Turnstile challenge too complex or site blocking solver.

**Solution:**
- Use proxy version: `"type": "AntiTurnstileTask"` with proxy config
- Retry with different user agent or IP
- Some sites have advanced Turnstile detection (enterprise plan)

## Proxy Support

For sites that check IP reputation or require residential IPs:

```python
create_payload = {
    "clientKey": api_key,
    "task": {
        "type": "AntiTurnstileTask",  # With proxy (not ProxyLess)
        "websiteURL": site_url,
        "websiteKey": site_key,
        "proxy": "http://username:password@proxy.example.com:8080"
    }
}
```

Playwright browser should use same proxy for consistency.

## Cost Optimization

### Batch Accounts Sequentially

```python
# DON'T: Launch 100 browsers in parallel (wastes solves on failures)
for account in accounts:
    result = await process_account(account)
    if not result['success']:
        break  # Stop if pattern fails

# DO: Test 1 account first, then scale
```

### Cache Site Keys

```python
# Extract once per domain
SITE_KEYS = {
    'example.com': '0x4AAAAAAAB...',
    'another.com': '0x4BBBBBBB...'
}

site_key = SITE_KEYS.get(domain) or await extract_turnstile_sitekey(page)
```

### Reuse Tokens (If Valid)

Some Turnstile tokens are valid for 2-5 minutes. If submitting multiple forms on same page quickly, you can reuse token.

**Warning:** Most sites invalidate token after first use. Test before assuming reusability.

## Testing Without CapSolver

For development/debugging, you can manually solve Turnstile:

```python
# Launch non-headless
browser = await p.chromium.launch(headless=False)

# Wait for manual solve
print("Solve Turnstile manually in browser...")
await page.wait_for_timeout(30000)  # 30 seconds to solve

# Continue automation
await page.click('button[type="submit"]')
```

## Real-World Example: Fintoq.ai

```python
async def fintoq_signup_with_turnstile(email, username, password, referral_code, api_key):
    """Complete Fintoq.ai signup with Turnstile auto-solve."""
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        
        # Navigate to signup
        await page.goto(f'https://fintoq.ai/signup?referral={referral_code}')
        
        # Fill form
        await page.fill('input[placeholder*="Username"]', username)
        await page.fill('input[type="email"]', email)
        await page.fill('input[type="password"]', password)
        
        # Solve Turnstile
        success = await solve_and_submit_turnstile(
            page,
            page.url,
            api_key
        )
        
        if success:
            await page.wait_for_timeout(5000)
            print("Signup complete!")
        
        await browser.close()
        return success
```

## Related Documentation

- CapSolver API docs: https://docs.capsolver.com/
- Cloudflare Turnstile: https://developers.cloudflare.com/turnstile/
- Playwright Python: https://playwright.dev/python/
