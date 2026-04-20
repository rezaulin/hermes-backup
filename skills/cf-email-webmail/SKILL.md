---
name: cf-email-webmail
description: Build a self-hosted webmail system on Cloudflare Workers + D1. Receives emails via Email Routing, stores in D1, serves a simple web inbox. Free tier, no external services.
category: devops
---

# Cloudflare Email Webmail Worker

Self-hosted webmail using Cloudflare Workers + D1 + Email Routing. Receives all emails to a custom domain, stores in D1, users login via web to view inbox.

## Architecture

```
Email → Cloudflare Email Routing → Worker (email handler) → D1 Database
User → Worker (HTTP) → Login → Query D1 → Show inbox
```

## Files

```
webmail-worker/
├── src/worker.js     # Worker: email handler + API + HTML UI
├── db/schema.sql     # D1 schema (users + emails tables)
├── wrangler.toml     # Cloudflare config
└── README.md
```

## D1 Schema

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
CREATE INDEX idx_emails_created ON emails(created_at);
```

## Setup Steps

1. **Create D1 Database** via Cloudflare Dashboard:
   - Workers & Pages → D1 SQL Database → Create
   - Run schema SQL in D1 Console
   - Note the `database_id`

2. **wrangler.toml**:
```toml
name = "webmail"
main = "src/worker.js"
compatibility_date = "2024-12-01"
send_email = []

[[d1_databases]]
binding = "DB"
database_name = "webmail-db"
database_id = "YOUR_DATABASE_ID"
```

3. **Deploy**:
```bash
CLOUDFLARE_API_TOKEN="xxx" npx wrangler deploy
```

4. **Setup Email Routing**:
   - Domain → Email → Email Routing → Get started
   - Catch-all → Send to Worker → select `webmail`

## Key Implementation Details

### Email Handler
- `message.raw` is a ReadableStream — must read chunks manually
- Parse multipart MIME to extract text/html body
- Limit raw_email storage to 50KB (D1 row size considerations)

### Auto-Create Users
Any `@domain.com` email can login without pre-registration:
```javascript
if (!user) {
  await env.DB.prepare('INSERT INTO users (email, password) VALUES (?, ?)')
    .bind(email, password).run();
}
```

### Auth Pattern
Simple Basic Auth via base64 token (email:password). No JWT/session needed for simple use case.

### API Routes
- `POST /api/login` — returns token
- `GET /api/inbox?page=N` — list emails (paginated)
- `GET /api/email?id=N` — single email detail
- `POST /api/delete` — delete email

## Pitfalls

- **D1 via CLI may fail** if API token lacks D1:Edit permission — create database and run SQL via Dashboard instead
- **localStorage 5MB limit** — don't store large base64 images in localStorage; use postMessage for live preview
- **Email body parsing** — real emails are complex (multipart, base64, quoted-printable); the simple parser handles common cases but may fail on edge cases
- **No sending** — this is receive-only. For sending, need SMTP relay or Cloudflare Email Workers (when available)
- **Token auth is basic** — fine for internal/personal use; for production, add rate limiting and stronger auth

## Deployment via Wrangler CLI

```bash
# Auth via env var (avoids interactive login)
export CLOUDFLARE_API_TOKEN="cfut_..."

# Create D1 (if token has permission, otherwise do via Dashboard)
npx wrangler d1 create webmail-db

# Run schema
npx wrangler d1 execute webmail-db --remote --file=./db/schema.sql

# Deploy
npx wrangler deploy
```

## Tested: April 2026
Working on Cloudflare free tier. Domain: reviewtechno.me.
