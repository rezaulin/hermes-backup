---
name: web-scrape-rewrite
description: Scrape article content from websites and rewrite into new articles. Use when the user wants to extract content from a web page and create a rewritten version.
---

# Web Scrape & Rewrite

## When to Use
- User wants to scrape content from a website
- User wants to rewrite/rephrase articles from web sources
- User wants to create new content based on existing web articles

## Approach: Browser-Based Scraping

**Always prefer browser tools over curl** for content scraping. Most modern websites use JS rendering, Cloudflare protection, or bot detection that blocks curl.

### Step 1: Navigate to the page
```
browser_navigate(url)
```

### Step 2: Extract content via browser_console
Use JavaScript DOM queries to extract structured content:

```javascript
// Extract article paragraphs
const article = document.querySelector('.entry-content, article, .post-content, .article-body');
if (article) {
  const paragraphs = article.querySelectorAll('p');
  const texts = [];
  for (const p of paragraphs) {
    const t = p.textContent.trim();
    if (t.length > 40) texts.push(t);
  }
  JSON.stringify({title: document.title, content: texts});
}
```

### Step 3: Rewrite the content
- Translate/rewrite into target language
- Restructure (e.g., long-form → bullet points, English → Indonesian)
- Add local context if needed
- Keep attribution to original source

### Step 4: Save as file
Write the rewritten article to `/root/articles/` as markdown.

## Common Sites & Their Selectors

| Site | Selector | Notes |
|------|----------|-------|
| WordPress blogs | `.entry-content p` | Most common |
| Ghost blogs | `.post-content p` or `article p` | |
| Wait But Why | `.entry-content p` | Works well |
| BoredPanda | Blocked by bot detection | Use browser with stealth |
| Medium | Cloudflare-protected | Requires advanced stealth |
| Reddit | curl blocked | Use JSON API: `reddit.com/r/SUB/top.json?limit=N` |
| semprot.com (XenForo) | `.message-body .bbWrapper` | Works with browser, threads via `.structItem--thread` |

### XenForo Forums (semprot.com, kaskus, etc.)

#### Thread listing
```javascript
const threads = document.querySelectorAll('.structItem--thread');
for (const t of threads) {
  const titleEl = t.querySelector('.structItem-title a:not(.labelLink)');
  const authorEl = t.querySelector('.username');
  const repliesEl = t.querySelector('.structItem-cell--meta dd');
  const prefixEl = t.querySelector('.label');
  // titleEl.href, titleEl.textContent, authorEl.textContent, repliesEl.textContent, prefixEl.textContent
}
```

#### Extract post content
```javascript
const posts = document.querySelectorAll('.message-body .bbWrapper');
// posts[0].innerText for first post (OP)
// posts.length for total posts on page
```

#### Login flow (XenForo)
1. Navigate to `/login/`
2. Type email/username into `textbox "Username atau alamat email:"`
3. Type password into `textbox "Password:"`
4. Click `button "Log in"`
5. Verify success — should see username in nav bar, error text "Password salah" on failure
6. After login, member-only sub-forums become accessible

#### Finding sub-forum URLs (after login)
```javascript
// Find all forum links on main page
const links = document.querySelectorAll('a[href*="/forums/"], a[href*="/categories/"]');
const forums = [];
for (const link of links) {
  forums.push({name: link.textContent.trim(), url: link.href});
}
```

#### XenForo search
- URL: `/search/?q=KEYWORDS&t=post&o=relevance`
- Requires login
- Can filter by forum in the search form dropdown
- Prefix filter available (e.g., "NOT NUDE", "NOT REPOST")

#### Handling NSFW/adult content in rewrite
When scraping adult forums, focus the rewrite on:
- Emotional/personal journey narrative
- Life lessons and takeaways
- Remove explicit content, keep story structure
- Add disclaimer: "Konten dewasa telah dihilangkan"

### Curl-First Approach (try before browser)
For simple sites or JSON APIs, curl is faster than browser:
```bash
curl -s -L "URL" -H "User-Agent: Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36"
```
If response is 200 but content is a Cloudflare challenge or parked domain script, fall back to browser.

## Troubleshooting

- **Blank content?** → Page uses JS lazy loading. Scroll down first with `browser_scroll('down')` then re-extract.
- **Bot detection?** → Try different user agents, or use a different source site.
- **curl works but no content?** → Content is JS-rendered. Switch to browser tools.
- **HTTP 200 but weird JS redirect?** → Likely a parked domain. Check if body contains `<title>Redirecting...</title>` or ad-detection scripts.
- **XenForo requires login?** → Some sub-forums are guest-accessible, others require auth. Try navigating without login first.

## Output Format
Save rewritten articles as markdown to `/root/articles/` with descriptive filenames.
