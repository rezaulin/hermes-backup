---
name: cloudflare-email-routing-setup
description: Set up Cloudflare Email Routing (catch-all forwarding) on a custom domain for email reselling or receiving emails without needing a mail server.
category: email
---

# Cloudflare Email Routing Setup

Use when: User wants to receive emails on their custom domain via Cloudflare (free, no VPS, no mail server needed). Useful for email reselling, OTP access for sold accounts, or simple email forwarding.

## Prerequisites
- Custom domain (Namecheap, etc.)
- Cloudflare account (free)

## Steps

### 1. Add Domain to Cloudflare
- dash.cloudflare.com → "Add a site" → enter domain
- Select **Free plan**
- Cloudflare gives 2 nameservers (e.g., `bethany.ns.cloudflare.com`, `glen.ns.cloudflare.com`)

### 2. Change Nameservers at Registrar (Namecheap)
- Namecheap → Domain List → Manage → Nameservers → "Custom DNS"
- Enter the 2 Cloudflare nameservers
- Save. Wait for propagation (15min - 48h, usually <1h)

### 3. Verify NS Propagated
```bash
dig NS domain.com +short
```
Should show Cloudflare NS, not registrar NS.

### 4. Enable Email Routing in Cloudflare
- Cloudflare dashboard → click on domain → sidebar → **Email**
- Click "Get started" / "Enable Email Routing"
- Cloudflare auto-adds MX + SPF records
- Status shows **"Unlocked"** when active

### 5. Verify Destination Email (IMPORTANT - often missed!)
- Go to **"Routes"** or **"Destination addresses"** in Email section
- Click **"Add"** → enter your email (e.g., `rezaahzani@gmail.com`)
- The destination field appears **disabled** until you add & verify
- Cloudflare sends confirmation email to that address
- Open Gmail → click verification link from Cloudflare
- Now the destination is **verified and active**

### 6. Set Up Catch-All or Individual Routes
**Catch-all** (all `*@domain.com` → your Gmail):
- Create route with custom address `*` or enable catch-all toggle
- Action: "Send to an email"
- Destination: your verified email

**Per-buyer route** (specific address → buyer's email):
- Custom address: `buyer1@domain.com`
- Action: "Send to an email"
- Destination: `buyer1@gmail.com` (must verify this email too)

## Use Cases

### Email Reselling (manual OTP forwarding)
- Catch-all → seller's Gmail
- Seller receives all emails, manually forwards OTP to buyer when needed
- Pros: Free, zero setup per buyer
- Cons: Seller is middleman

### Email Reselling (buyer independence)
- Per-buyer route → forward to buyer's real email
- Buyer gets OTP directly in their Gmail
- Pros: Buyer independent, still free
- Cons: Need buyer's real email, manual route creation per buyer

## Limitations
- Forwarding only — no standalone mailboxes
- Each destination email needs verification
- Catch-all means ALL spam also forwards
- No IMAP/POP3 — buyers can't "log in" to an email account

## Alternative for Buyer Login (Paid)
If buyers need actual mailbox login (not forwarding):
- **Migadu**: $19/year, unlimited mailboxes, IMAP access, API for auto-create
- **Purelymail**: $10/year, unlimited mailboxes, IMAP access

## Pitfalls
- NS propagation can take up to 48h — don't panic if it's slow
- Destination email appears DISABLED until you first add & verify it (common confusion point)
- Don't delete the auto-generated MX/SPF records that Cloudflare creates
- If using Namecheap DNS (not Cloudflare NS), Email Routing won't work — must use Cloudflare NS
