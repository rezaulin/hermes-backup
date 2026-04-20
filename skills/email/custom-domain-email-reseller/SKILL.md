---
name: custom-domain-email-reseller
description: Set up custom domain email for reselling email accounts to buyers. Covers options from free (Yandex, Cloudflare) to paid (Migadu, Purelymail), with focus on no-VPS solutions.
---

# Custom Domain Email for Reselling

Set up email on a custom domain where each "buyer" gets a unique email address and can receive OTP/verification emails.

## Use Case
Seller creates email accounts on their domain (e.g., `user@sellerdomain.com`), sells access to buyers who need to receive OTP/verification codes.

## Options Comparison

### No Web App, No VPS

| Service | Cost | Mailboxes | Auto-create | Notes |
|---------|------|-----------|-------------|-------|
| Yandex Connect | Free | 1000 | ❌ Manual | OTP for registration can fail. Custom domain support. IMAP access. Buyer logs in at mail.yandex.com |
| Migadu | $19/yr | Unlimited | ✅ API | Best value. IMAP access. Easy signup. |
| Purelymail | $10/yr | Unlimited | ✅ API | Cheapest paid option. |
| Zoho Mail | Free | **5 only** | ❌ | Not enough for reselling. |

### Cloudflare-based (no VPS, no hosting service)

| Service | Cost | How it works | Limitation |
|---------|------|--------------|------------|
| Cloudflare Email Routing | Free | Catch-all or per-address forwarding to buyer's real email | Need buyer's real email, must create routing rules |
| Cloudflare + Worker + DB | Free | Full auto-receive, store in DB, web app for buyer access | Requires building web app |

## Recommended: Yandex Connect (Free)

### Setup Steps
1. Register at `passport.yandex.com` (need phone number for OTP)
2. Go to `connect.yandex.com` → Connect domain
3. Verify domain via TXT or CNAME record in DNS
4. Add MX record: `mx.yandex.net` priority `10`
5. Add SPF TXT: `v=spf1 redirect=_spf.yandex.net`
6. Create mailboxes in Yandex dashboard

### Buyer Login
- Web: `mail.yandex.com`
- IMAP: `imap.yandex.com` port 993 (SSL)
- SMTP: `smtp.yandex.com` port 465 (SSL)

### Common Issues
- **OTP not received**: Try different phone number, use "Call me" option, or retry 2-3 times
- **Registration blocked**: Some country codes may be blocked by Yandex

## Alternative: Cloudflare Email Routing (Manual Forwarding)

### Setup Steps
1. Add domain to Cloudflare (`dash.cloudflare.com` → Add a site)
2. Change nameservers at registrar to Cloudflare's NS
3. Wait for NS propagation (15min - 48h)
4. Enable Email Routing in Cloudflare dashboard
5. Set catch-all or per-address routing rules
6. Forward to: buyer's real email OR single Gmail (manual forward)

### Pros/Cons
- ✅ Free, no VPS
- ✅ Reliable (Cloudflare infrastructure)
- ❌ Forwarding only — no independent mailbox
- ❌ Catch-all → one inbox, must manually forward to buyers
- ❌ Per-rule → need buyer's real email + manual rule creation

## DNS Records Needed (for any email hosting)

```
Type    Host    Value                       Priority
MX      @       [mail server hostname]      10
TXT     @       v=spf1 [provider spf]       -
TXT     @       [DKIM record if needed]     -
A       mail    [server IP, if self-hosted]  -
```

## Cloudflare Worker + D1 Webmail (Full Auto)

Build a self-hosted webmail where buyers log in with their email address and see their own inbox. No external service needed — 100% Cloudflare free tier.

### Architecture
```
Email → Cloudflare Email Routing (catch-all) → Worker
Worker → parses raw email → stores in D1 Database
Buyer → opens webmail app → logs in → sees own inbox
```

### Files
```
webmail-worker/
├── src/worker.js     ← Email handler + API + HTML UI (single file)
├── db/schema.sql     ← D1 tables (users + emails)
└── wrangler.toml     ← Cloudflare config
```

### D1 Schema
```sql
CREATE TABLE IF NOT EXISTS users (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  email TEXT UNIQUE NOT NULL,
  password TEXT NOT NULL,
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
CREATE TABLE IF NOT EXISTS emails (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  to_addr TEXT NOT NULL,
  from_addr TEXT,
  subject TEXT,
  body_text TEXT,
  body_html TEXT,
  raw_email TEXT,
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX idx_emails_to ON emails(to_addr);
```

### Key Implementation Details

**Email handler** — reads raw email stream, parses body, saves to D1:
```javascript
async email(message, env, ctx) {
  // Read raw stream
  const reader = message.raw.getReader();
  const chunks = [];
  while (true) {
    const { done, value } = await reader.read();
    if (done) break;
    chunks.push(value);
  }
  // Decode and parse
  const rawText = new TextDecoder().decode(concatBytes(chunks));
  const { text, html } = parseEmailBody(rawText);
  // Save to D1
  await env.DB.prepare(
    "INSERT INTO emails (to_addr, from_addr, subject, body_text, body_html, raw_email) VALUES (?,?,?,?,?,?)"
  ).bind(message.to, message.from, subject, text, html, rawText.slice(0,50000)).run();
}
```

**Auto-register on login** — any email @domain can login without pre-creating accounts:
```javascript
async function handleLogin(request, env) {
  const { email, password } = await request.json();
  if (!email.endsWith('@yourdomain.com')) return json({error: 'Invalid domain'}, 401);
  let user = await env.DB.prepare('SELECT * FROM users WHERE email = ?').bind(email).first();
  if (!user) {
    await env.DB.prepare('INSERT INTO users (email, password) VALUES (?,?)').bind(email, password).run();
    user = { email, password };
  }
  if (user.password !== password) return json({error: 'Wrong password'}, 401);
  return json({ token: btoa(`${email}:${password}`), email });
}
```

**Auth** — HTTP Basic Auth (email:password base64), checked on every API call.

**Web UI** — single HTML page embedded in worker (dark theme, mobile responsive):
- Login form → auto-register if email doesn't exist
- Inbox list with pagination
- Email detail with text/HTML/raw tabs
- Auto-extract verification code (4-8 digit regex)
- Auto-refresh every 15s

### Deploy Steps
1. `npx wrangler d1 create webmail-db` → copy database_id
2. Run schema: via D1 Console in Cloudflare Dashboard
3. Update `wrangler.toml` with database_id
4. `npx wrangler deploy`
5. Cloudflare Dashboard → Email → Email Routing → Catch-all → Send to Worker → select `webmail`

### Limitations
- D1 API via CLI often fails with "Authentication error" even with correct token — use D1 Console in Dashboard for SQL operations instead
- Email body parser handles multipart MIME, base64, quoted-printable — but complex nested MIME may fail
- No sending capability — receive-only
- No attachments extraction
- Simple auth (no JWT, no session management)

## Cost Analysis (1000 emails/year)
- Yandex: **Free**
- Migadu: **$19/year** ($0.019/email)
- Purelymail: **$10/year** ($0.01/email)
- Self-hosted VPS: **$5-10/month** (but unlimited, full control)
- Cloudflare Email Routing: **Free** (forwarding only)
- Cloudflare Worker + D1 Webmail: **Free** (full inbox, up to 100k requests/day)
