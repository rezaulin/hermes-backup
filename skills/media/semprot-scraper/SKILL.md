---
name: semprot-scraper
description: Scrape and extract content from semprot.com (Indonesian XenForo forum) - login, browse forums, scrape threads, extract verbatim (copas) or rewrite articles.
version: 1.2
dependencies:
  - browser_tool
---

# Semprot.com Scraper

Scrape content from semprot.com (Indonesian XenForo forum). Requires login for member-only sections.

## Login

```javascript
// Navigate to login page
browser_navigate("https://www.semprot.com/login/")

// Fill credentials
browser_type(ref="#login-form input[name='login']", text="email_or_username")
browser_type(ref="#login-form input[name='password']", text="password")
browser_click(ref="#login-form button[type='submit']")

// Verify login - should see username in nav bar
browser_snapshot()
```

## Forum Structure

After login, accessible forums include:

| Forum | URL | Description |
|-------|-----|-------------|
| Gambar Cewek Indonesia IGO | `/forums/gambar-cewek-indonesia-igo.326/` | IGO photos (Member Only) |
| IGO Art Photography | `/forums/igo-art-photography.31/` | Art photography |
| Film Cewek Indonesia IGO | `/forums/film-cewek-indonesia-igo.11/` | IGO videos |
| Cerita | `/forums/cerita.42/` | Stories |
| Cerita Bersambung | `/forums/cerita-bersambung.139/` | Serialized stories |
| Cerita Lucu | `/forums/cerita-lucu.50/` | Funny stories |
| Setengah Baya | `/forums/setengah-baya.294/` | Mature stories (Member Only) |
| Jasa Tulis Cerita | `/forums/jasa-tulis-cerita.369/` | Story writing services |
| Wisata | `/forums/wisata.317/` | Travel experiences |
| Kuliner | `/forums/kuliner.140/` | Food stories |

## Scrape Thread List

```javascript
// After navigating to a forum page
browser_console(expression: `
  const threads = document.querySelectorAll('.structItem--thread');
  const data = [];
  for (let i = 0; i < Math.min(threads.length, 20); i++) {
    const titleEl = threads[i].querySelector('.structItem-title a:not(.labelLink)');
    const authorEl = threads[i].querySelector('.username');
    const repliesEl = threads[i].querySelector('.structItem-cell--meta dd');
    const prefixEl = threads[i].querySelector('.label');
    if (titleEl) {
      data.push({
        title: titleEl.textContent.trim(),
        url: titleEl.href,
        author: authorEl ? authorEl.textContent.trim() : '',
        replies: repliesEl ? repliesEl.textContent.trim() : '',
        prefix: prefixEl ? prefixEl.textContent.trim() : ''
      });
    }
  }
  JSON.stringify(data);
`)
```

## Scrape Thread Content

### All posts on current page
```javascript
browser_console(expression: `
  const posts = document.querySelectorAll('.message--post');
  const data = [];
  for (const post of posts) {
    const authorEl = post.querySelector('.message-name a, .username');
    const author = authorEl ? authorEl.textContent.trim() : '';
    const contentEl = post.querySelector('.message-body .bbWrapper');
    const text = contentEl ? contentEl.innerText.trim() : '';
    if (text.length > 30) {
      data.push({author, content: text, length: text.length});
    }
  }
  JSON.stringify({totalPosts: posts.length, posts: data});
`)
```

### OP posts only (most useful for cerita threads)
```javascript
// First find the OP author name, then filter
browser_console(expression: `
  const posts = document.querySelectorAll('.message--post');
  const results = [];
  for (const post of posts) {
    const authorEl = post.querySelector('.message-name a, .username');
    const author = authorEl ? authorEl.textContent.trim() : '';
    if (author === 'OP_USERNAME') {
      const contentEl = post.querySelector('.message-body .bbWrapper');
      const text = contentEl ? contentEl.innerText.trim() : '';
      if (text.length > 30) {
        results.push({content: text, length: text.length});
      }
    }
  }
  JSON.stringify(results);
`)
```

### OP posts with images and links
```javascript
browser_console(expression: `
  const posts = document.querySelectorAll('.message--post');
  const results = [];
  for (const post of posts) {
    const authorEl = post.querySelector('.message-name a, .username');
    const author = authorEl ? authorEl.textContent.trim() : '';
    if (author === 'OP_USERNAME') {
      const contentEl = post.querySelector('.message-body .bbWrapper');
      const text = contentEl ? contentEl.innerText.trim() : '';
      // Get images (exclude smilies/emoji/avatar)
      const imgs = contentEl ? contentEl.querySelectorAll('img') : [];
      const imageUrls = [];
      for (const img of imgs) {
        if (img.src && !img.src.includes('smilies') && !img.src.includes('emoji') && !img.src.includes('avatar')) {
          imageUrls.push(img.src);
        }
      }
      // Get links
      const links = contentEl ? contentEl.querySelectorAll('a') : [];
      const linkUrls = [];
      for (const link of links) {
        const href = link.href;
        if (href && !href.includes('semprot.com/members') && !href.includes('#')) {
          linkUrls.push({text: link.textContent.trim(), href: href});
        }
      }
      results.push({content: text, images: imageUrls, links: linkUrls, length: text.length});
    }
  }
  JSON.stringify(results);
`)
```

### Get total pages
```javascript
browser_console(expression: `
  const pageNav = document.querySelector('.pageNav-main');
  const pages = pageNav ? pageNav.querySelectorAll('li').length : 0;
  const lastPage = pageNav ? pageNav.querySelector('li:last-child a') : null;
  JSON.stringify({totalPages: pages, lastPageUrl: lastPage ? lastPage.href : 'none'});
`)
```

### Post links (UPDATE X references)
OP posts sometimes contain internal links like "UPDATE 1", "UPDATE 2" that point to specific posts. These are revealed after expanding spoilers. The links follow the pattern:
- `https://www.semprot.com/threads/SLUG.THREAD_ID/post-POST_ID`
- Navigate directly to these URLs to get the linked content

### Important: Session Expiry
Login sessions expire frequently between page navigations. Check if redirected to login page and re-login before continuing. The login form fields are:
- `ref=e9` (username) and `ref=e10` (password) typically
- Always call `browser_snapshot()` first to get correct refs
```

## Search (Requires Login)

```
https://www.semprot.com/search/?q=keywords&t=post&o=relevance
```

Or use the search form:
```javascript
browser_type(ref=searchbox, text="search keywords")
browser_click(ref=search_button)
```

## Pagination

Thread pages: `/threads/thread-slug.THREAD_ID/page-N`
Forum pages: `/forums/forum-slug.FORUM_ID/page-N`

## Finding Forums Dynamically

Use browser_console to discover all forum links on the page when unsure of exact URL:
```javascript
browser_console(expression: `
  const links = document.querySelectorAll('a');
  const found = [];
  for (const l of links) {
    const text = l.textContent.trim().toLowerCase();
    if (text.includes('keyword')) {
      found.push({text: l.textContent.trim(), href: l.href});
    }
  }
  JSON.stringify(found);
`)
```

## Thread Types

Before scraping, check what kind of thread it is:

| Type | Examples | Content | Approach |
|------|----------|---------|----------|
| **Narrative (Cerita)** | Setengah Baya, Cerita Bersambung | Long text posts, dialogue, story arcs | Extract OP text verbatim across all pages |
| **Photo/Share (IGO)** | Gambar IGO, GF/Binor threads | Images + short captions, reply chains | Extract images + captions, not text-heavy |
| **Mixed** | Some IGO threads with SSI stories | Both photos and narrative text | Extract both text and images |

Check the first 1-2 OP posts to determine type. If OP posts are mostly images with <100 chars text, it's a photo thread — don't scrape expecting long narrative text. Ask the user if they want photo extraction instead.

## Extracting Images

When thread content includes images (photo threads, or mixed threads):

```javascript
// Get images from OP posts, including lazy-loaded
browser_console(expression: `
  const posts = document.querySelectorAll('.message--post');
  const results = [];
  for (const post of posts) {
    const authorEl = post.querySelector('.message-name a, .username');
    const author = authorEl ? authorEl.textContent.trim() : '';
    if (author === 'OP_USERNAME') {
      const contentEl = post.querySelector('.message-body .bbWrapper');
      const text = contentEl ? contentEl.innerText.trim() : '';
      const imgs = contentEl ? contentEl.querySelectorAll('img') : [];
      const imageUrls = [];
      for (const img of imgs) {
        // Exclude smilies, emojis, avatars
        if (img.src && !img.src.includes('smilies') && !img.src.includes('emoji') && !img.src.includes('avatar')) {
          imageUrls.push(img.src);
        }
      }
      // Handle lazy-loaded images (data-src attribute)
      const lazyImgs = contentEl ? contentEl.querySelectorAll('[data-src]') : [];
      for (const el of lazyImgs) {
        const ds = el.getAttribute('data-src');
        if (ds && (ds.includes('.jpg') || ds.includes('.png') || ds.includes('.jpeg') || ds.includes('.webp') || ds.includes('.gif'))) {
          imageUrls.push(ds);
        }
      }
      results.push({content: text, images: imageUrls, length: text.length});
    }
  }
  JSON.stringify(results);
`)
```

Image hosts commonly used: `imagebam.com`, `imagetwist.com`, `imgbox.com`. Thumbnail URLs (containing `_t` suffix like `MESRWUV_t.jpg`) can usually be converted to full-size by removing the `_t`.

## Expanding Spoilers (CRITICAL)

XenForo spoiler sections hide content — images, video links, and text. **Always expand spoilers BEFORE extracting content**, otherwise you'll miss hidden links/images.

```javascript
// Step 1: Expand all spoilers on the page
browser_console(expression: `
  const spoilers = document.querySelectorAll('.bbCodeSpoiler-button');
  spoilers.forEach(btn => btn.click());
  'Spoilers expanded: ' + spoilers.length;
`)

// Step 2: Then extract content (images, links, text) as usual
// Spoiler content will now be visible in the DOM
```

After expanding, also extract **all links** from OP posts — these often point to:
- Specific update posts within the thread (internal post links)
- Video hosts (streamtape.net, sendvid.com, etc.)
- External image hosts

```javascript
// Extract all links from OP posts
const links = contentEl ? contentEl.querySelectorAll('a') : [];
const linkUrls = [];
for (const link of links) {
  const href = link.href;
  // Filter out member profiles, anchors, navigation
  if (href && !href.includes('semprot.com/members') && !href.includes('semprot.com/login') && !href.includes('#')) {
    linkUrls.push({text: link.textContent.trim(), href: href});
  }
}
```

### Following Internal Post Links

Many OP posts contain "UPDATE 1", "UPDATE 2" etc. that are links to other posts within the thread. These links look like:
- `/threads/SLUG.THREAD_ID/post-POSTID` — redirects to the page containing that post
- `/goto/post?id=POSTID` — direct post reference

To get their content, navigate to each link URL, then extract the OP's post from that page. The post ID format is `js-post-POSTID` in the DOM.

### Common Hidden Content in Spoilers

| Content Type | Hosts | Extraction |
|---|---|---|
| Video | streamtape.net, sendvid.com, vimeo | Link URL directly |
| Images | imagebam.com, imgbox.com | Thumbnail + full-size link |
| Text | Inline in spoiler | innerText after expansion |

## Content Output Modes

User may want either:
1. **Verbatim copy-paste (copas)** — extract full original text as-is, no rewriting. Use `.innerText` extraction from DOM, save to file or return directly. This is the more common request.
2. **Rewritten articles** — restructure, translate, clean up content for publishing.

Always confirm with user which mode before scraping. Default to verbatim if user says "copas".

## Verbatim OP Extraction (Copas Mode)

When user wants full original story content without summaries:

1. Navigate to thread, note the OP author username
2. Extract OP's posts only (filter out "lanjut"/"mantap" replies)
3. Loop through ALL pages (check pagination with `.pageNav-main`)
4. Handle session expiration — browser sessions expire between page navigations on semprot.com. Always check for login redirect and re-login if needed before continuing

```javascript
// Extract only OP's substantial posts (>30 chars) from current page
browser_console(expression: `
  const posts = document.querySelectorAll('.message--post');
  const results = [];
  for (const post of posts) {
    const authorEl = post.querySelector('.message-name a, .username');
    const author = authorEl ? authorEl.textContent.trim() : '';
    if (author === 'OP_USERNAME') {
      const contentEl = post.querySelector('.message-body .bbWrapper');
      const text = contentEl ? contentEl.innerText.trim() : '';
      if (text.length > 30) {
        results.push({content: text, length: text.length});
      }
    }
  }
  JSON.stringify(results);
`)
```

### Handling Session Expiration

semprot.com sessions expire frequently between page loads. After every `browser_navigate()`, check if redirected to login:
- If page title contains "Log in", re-login with credentials before continuing
- Login flow: navigate to `/login/`, type username, type password, click login button
- "Ingat saya" is checked by default but doesn't prevent expiry on new page loads in headless browser

### Pagination Check

```javascript
browser_console(expression: `
  const pageNav = document.querySelector('.pageNav-main');
  const pages = pageNav ? pageNav.querySelectorAll('li').length : 0;
  JSON.stringify({totalPages: pages});
`)
```

## Article Rewriting Workflow (Mode 2)

1. Scrape original content from thread
2. Translate/restructure to target language
3. Remove explicit/adult content, focus on narrative/emotional journey
4. Add sections, headers, bullet points for readability
5. Add source attribution and disclaimer

## Twitter/X Scraping (Brave Search Fallback)

When X login or API is unavailable, use Brave Search to find tweets by keyword:
```bash
curl -s "https://search.brave.com/search?q=site%3Ax.com+KEYWORD&source=web" | grep -oP 'x\.com/[^/]+/status/\d+' | sort -u
```
Returns tweet URLs. Content reading requires X login (browser) or API keys.

## Important Notes

- Session may expire — re-login if redirected to login page
- "Ingat saya" checkbox is checked by default (session persists longer)
- Some forums require minimum post count or account age
- Respect rate limits — don't hammer the server
- Adult content exists — handle responsibly when rewriting
- OP posts are spread across pages sparsely — use post ID links from spoilers to find them efficiently
- Imagebam thumbnail URLs end with `_t.jpg` — remove `_t` for full-size images
- Thread listing can be found dynamically via link search (see "Finding Forums Dynamically" section) when exact URL unknown