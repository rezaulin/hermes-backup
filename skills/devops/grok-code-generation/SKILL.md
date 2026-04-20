---
name: grok-code-generation
description: Generate code using xAI Grok API for large projects — chunked workflow to avoid timeouts
---

## When to Use
- User has xAI API key with Grok access ($50 credit)
- Need to generate a large frontend/backend project
- Subagent models aren't capable enough for the task

## xAI API Setup
- **Endpoint**: `https://api.x.ai/v1/chat/completions`
- **Model**: `grok-3-fast` (fastest) or `grok-3` (more capable)
- **Auth**: `Authorization: Bearer {XAI_API_KEY}`
- **Format**: OpenAI-compatible API

## Critical Finding: Chunked Generation
Grok API **times out** with large prompts (180s+). Solution: break into focused sub-tasks.

### Workflow
1. **Generate structure first** (HTML shell, page containers, CSS framework)
2. **Generate JS in focused chunks** (auth, CRUD, reports, etc.)
3. **Each chunk: 1 topic, ~8K max_tokens**
4. **Assemble parts** into final file
5. **Clean up** part files

### Example Chunk Breakdown for SPA
| Chunk | Content | max_tokens |
|---|---|---|
| Part 1 | HTML structure + CSS | 16000 |
| Part 2a | Auth, nav, dark mode | 8000 |
| Part 2b | Feature-specific logic | 8000 |
| Part 2c | CRUD operations | 8000 |
| Part 2d | Reports/exports | 8000 |
| Part 2e | Settings, misc | 8000 |

### Python Helper
```python
import requests, json

def ask_grok(prompt, api_key, max_tokens=8000, timeout=300):
    resp = requests.post("https://api.x.ai/v1/chat/completions",
        headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
        json={
            "model": "grok-3-fast",
            "messages": [{"role": "user", "content": prompt}],
            "max_tokens": max_tokens,
            "temperature": 0  # deterministic for code
        },
        timeout=timeout
    )
    return resp.json()["choices"][0]["message"]["content"]
```

### Prompt Tips
- Always say "Return ONLY code, no explanation"
- Be specific about API endpoints, auth method, field names
- Include context (API reference) but keep it concise
- Use `temperature: 0` for code generation
- Don't include large code previews in prompt — just describe the structure

### Assembly Pattern
```python
# Clean up code fences from Grok output
import re
def clean_script(s):
    s = re.sub(r'^```\w*\n?', '', s.strip())
    s = re.sub(r'\n?```$', '', s)
    s = re.sub(r'^<script[^>]*>\s*', '', s)
    s = re.sub(r'\s*</script>\s*$', '', s)
    return s.strip()

# Combine parts
combined = html_part + "\n<script>\n" + js_part_a + js_part_b + "\n</script>\n</body></html>"
```

## Real-World Findings (2026-04-19 pesantren-v2 project)
Generated a full 74KB SPA (Tailwind + Alpine.js) in ~2 minutes using 6 chunks.

### What worked
- **HTML structure chunk**: max_tokens=16000 worked fine, generated 29KB
- **JS chunks**: max_tokens=8000, each took 7-40 seconds
- **Prompt size matters**: Including full API reference (2KB) was fine. Including server.js preview (5KB) caused timeout on the second call. Keep context under 3KB.
- **temperature=0** gave consistent, correct code

### What failed
- **Full context in prompt**: Passing server.js (3K chars) + API reference + HTML preview = timeout at 180s. Solution: just pass API reference, not code previews.
- **Subagent approach**: xiaomi/mimo-v2-pro model couldn't handle the task (created empty file). Grok via direct API call worked.
- **Python f-string conflicts**: Alpine.js syntax like `x-data=\"{tab:'home'}\"` breaks Python f-strings. Pass prompt as regular string, not f-string.
- **Broken Alpine.js scope architecture**: Grok generated separate `x-data` scopes for login, main, modal, toast — each with its own `page` variable. Login couldn't transition to main app. Symptom: only "Tutup"/"Simpan" modal visible. Root cause: Alpine.js isolates each `x-data` scope; shared state requires single root scope or `Alpine.store()`.

### Assembly checklist
1. Strip ``` code fences from all parts
2. Remove wrapping `<script>` tags from JS parts
3. Remove `</body></html>` from HTML part before appending JS
4. Fix Alpine.js version (Grok uses 2.x, need 3.x)
5. Deduplicate helper functions (toast, api, $) across chunks
6. Combine: HTML + `<script>` + part_a + part_b + ... + `</script></body></html>`

## Pitfalls
- **Timeout**: Prompts >3K input chars (excluding the API key) risk timeout. Keep context focused.
- **Alpine.js version**: Grok defaults to Alpine 2.x. Always specify "Alpine.js 3.x" and replace in output.
- **Code fences**: Grok wraps output in ``` blocks. Strip before assembly.
- **Duplicate functions**: Each chunk may re-define helpers (toast, api). Deduplicate on merge.
- **API key in command**: Use env vars or secure storage, not inline in commands.
- **Python string conflicts**: Don't use f-strings for prompts containing JS/Alpine syntax with curly braces.
- **Double-escaped HTML quotes**: Grok may output `\\\\\\\"` instead of `\\\"` inside x-data or onclick attributes. Search for `\\\\\\\"` in generated HTML and fix before running. This causes Alpine.js to silently fail and all pages render simultaneously.
- **Separate x-data scopes**: Grok may generate multiple independent `x-data` blocks (e.g. login div, main content div, modal div, toast div) each with their own `page` or `modalOpen` variable. Alpine.js scopes are isolated — `@click="page='home'"` in one scope can't affect `x-show="page==='home'"` in another. Fix: consolidate into a single root `x-data` with all state, or use `Alpine.store()` for shared state. Symptom: only modal buttons ("Tutup"/"Simpan") visible, rest of app blank.
- **All pages visible at once**: If page containers don't hide/show correctly, check for: (1) broken x-if/x-show syntax from escaped quotes, (2) missing Alpine.js CDN load, (3) conflicting inline x-data with Alpine.data() registrations.

## Self-Contained Chunks (2026-04-19 finding)
Each JS chunk prompt should be **self-contained** — describe what functions to write with API endpoints inline. Don't include previous chunks' output as context (it bloats the prompt and causes timeout). Each chunk should work independently as if it's the only script.

Bad: Include Part 2a output (4KB) in Part 2b prompt → timeout
Good: Part 2b prompt just says "Write functions for loadAbsensi(), simpanAbsensi(), etc. using GET /api/absensi" → 7 seconds

## Generating HTML Structure Tips
- Specify "use Alpine.js 3.x via CDN" explicitly or Grok defaults to 2.x
- Say "Tailwind CSS via CDN with <script src='https://cdn.tailwindcss.com'></script>"
- Include all page containers in HTML even if empty — JS fills them later
- Dark mode: specify class="dark" on html element, use Tailwind dark: prefix

## Post-Generation Workflow
After assembling the Grok output:

1. **Commit immediately** as baseline before any manual changes:
   ```bash
   git add -A && git commit -m "feat: Initial frontend generated by Grok"
   ```
2. **Test in browser** before modifying — verify pages hide/show, login works, no raw JS visible
3. **If issues found**, fix them on a separate commit (don't amend the Grok baseline)
4. **Rollback pattern** if manual changes break things:
   ```bash
   git log --oneline  # find the Grok commit hash
   git reset --hard <grok-commit-hash>
   pm2 restart <app-name>
   ```

This keeps the Grok-generated code as a safe fallback point.

## Deployment Gotcha: Port Mismatch After Copy/Deploy
When copying a codebase to a new directory or VPS, the server may default to a different port than the reverse proxy expects. Example: server.js defaults to `PORT=3000` but nginx proxies to `3001`.

Symptom: 502 Bad Gateway, pm2 shows "Server jalan" but curl returns nginx error.

Fix:
```bash
# Check what port nginx expects
grep proxy_pass /etc/nginx/sites-enabled/*

# Check what port the server defaults to
grep PORT server.js

# Fix by setting PORT in pm2
PORT=3001 pm2 restart app-name --update-env
```

Always verify port alignment between server and reverse proxy before assuming code is broken.

## Sub-Agent Deployment (2026-04-19 finding: WebSantri Next.js project)

When spawning a sub-agent with `model="xai/grok-3-fast"` for deployment tasks, the sub-agent
used `xiaomi/mimo-v2-pro` as its runtime model (not Grok). Grok was used only for the
`delegate_task` parent context. The sub-agent created ~95% of the code but hit issues:

### What the sub-agent got right
- Project initialization with create-next-app
- Prisma schema design
- API routes (11 endpoints)
- Page components for all CRUD views
- Auth system skeleton (lib/auth.ts)

### What the sub-agent missed
- No login page (directory created but file missing)
- No NextAuth route handler (`app/api/auth/[...nextauth]/route.ts` empty)
- No middleware.ts for route protection
- No dashboard layout (sidebar)
- No root page redirect to /login

### What broke during manual fixes

**Prisma 7.x incompatibility with SQLite:**
- Sub-agent installed `prisma@7.7.0` — newer Prisma has breaking changes
- `url` property in `datasource db` no longer supported in schema files (must be in prisma.config.ts)
- SQLite doesn't support Prisma enums in Prisma 5.x either
- Fix: `npm install prisma@5 @prisma/client@5` + replace all `enum` with `String` fields
- Replace `enum Role { ADMIN USTADZ }` with `role String @default("USTADZ")` on the model
- Remove `prisma.config.ts` (Prisma 7.x artifact)

**NextAuth v5 (Auth.js) gotchas:**
- `UntrustedHost` error on non-localhost: add `trustHost: true` to NextAuth config
- `MissingCSRF` error when POSTing to `/api/auth/callback/credentials` manually from curl
- Fix: use `signIn("credentials", { username, password, redirect: false })` from `next-auth/react`
- Requires `SessionProvider` wrapper in root layout (client component)
- The route handler at `app/api/auth/[...nextauth]/route.ts` must export `handlers`:
  ```typescript
  import { handlers } from "@/lib/auth";
  export const { GET, POST } = handlers;
  ```

**Environment variables for NextAuth:**
```
NEXTAUTH_SECRET="any-random-secret"
NEXTAUTH_URL="https://your-domain.com"
```
Without `NEXTAUTH_URL`, auth callbacks fail silently.

### Deployment checklist for Next.js on VPS
1. SSH + install Node.js 20+, nginx, certbot, pm2
2. Create project, install deps, setup Prisma
3. Write all code (or generate with Grok)
4. `npx prisma generate && npx prisma db push` (creates SQLite DB)
5. `npm run build`
6. `PORT=3002 pm2 start npm --name appname -- start`
7. nginx reverse proxy config → `proxy_pass http://127.0.0.1:PORT`
8. Cloudflare DNS A record via API: `curl -X POST "https://api.cloudflare.com/client/v4/v1/zones/{zone}/dns_records" -H "Authorization: Bearer {token}" -d '{"type":"A","name":"subdomain.domain.com","content":"VPS_IP","proxied":true}'`
9. `certbot --nginx -d subdomain.domain.com --non-interactive --agree-tos --register-unsafely-without-email`
10. Seed database via API endpoint or `npx prisma db seed`

### SSH patterns for remote VPS deployment
```bash
# Install sshpass first
apt-get install -y sshpass

# Remote command
sshpass -p 'password' ssh -o StrictHostKeyChecking=no root@VPS_IP 'command'

# File transfer (avoids heredoc timeout issues with long files)
sshpass -p 'password' scp -o StrictHostKeyChecking=no localfile root@VPS_IP:/remote/path/

# Timeout issue: SSH heredocs with >100 chars can hang. Use scp instead.
```

### Alpine.js scope bug (detailed)
Grok generated this broken pattern:
```html
<!-- BROKEN: separate scopes -->
<div x-data="{ page: 'login' }" x-show="page === 'login'">...</div>
<div x-data="{ page: 'home' }" x-show="page === 'home'">...</div>
```
Each `x-data` creates an isolated scope. `page` in scope 1 ≠ `page` in scope 2.
Fix: single root scope:
```html
<!-- CORRECT: shared scope -->
<div x-data="{ page: 'login' }">
  <div x-show="page === 'login'">...</div>
  <div x-show="page === 'home'">...</div>
</div>
```

## Cost
- grok-3-fast: ~$5 per 1M input tokens, $15 per 1M output tokens
- A full SPA generation (~50K output tokens) costs ~$0.75
- $50 credit = ~65 full projects
- Sub-agent with 100 iterations: ~30 min wall time, model cost varies by model used
