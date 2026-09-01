---
name: osint-username-recon
description: "Passive OSINT on a handle/username (Telegram, X/Twitter, etc) — enumerate footprint across platforms, resolve display names, detect dead/wrong leads, and answer 'which groups is this person in' without any authenticated API. Load when user gives a username/handle and wants identity, footprint, or group-membership recon."
tags: [osint, recon, telegram, twitter, username, footprint, passive]
triggers:
  - osint
  - OSINT
  - recon username
  - username footprint
  - gabung group apa
  - who is
---

# OSINT Username Recon

Passive, no-auth playbook for footprinting a handle. Works from a plain datacenter IP; heavy WAF targets (Cloudflare) may need CloakBrowser / residential proxies, everything below degrades gracefully.

**Operator context:** jarvis does OSINT as prep for deeper checks (identity → phone/email → breach DBs). Deliver a findings table + explicit "checked, not found" list + ranked next moves; no lectures.

## 1. Telegram (usually the anchor)

- `curl -sk https://t.me/<handle>` → parse `<meta property="og:title" content="...">` for the display name. `og:description` often says "You can contact @... right away". Default `t_logo_2x.png` og:image = **no profile photo** (low-effort/burner signal).
- `t.me/s/<handle>` = channel-view; if it returns the same contact page (not posts), the handle is a user, not a channel.
- Nearby handles are usually DIFFERENT people (`@jhontol` vs `@jhontolll`); always title-check before merging.

## 2. X/Twitter — the metadata page

Straight `curl -skL -A <chrome UA> https://x.com/<handle>` returns the profile page even as a guest (unlike many platforms):
- `<title>` = `Display Name (@handle) / X`
- `<meta name="description">` = `N followers · M following. Location. Joined Mon YYYY. See the latest conversations...`
- If location/joined absent → account not found / suspended.
- Page is a landing shell: **no** tweet text, `rest_id`, `screen_name`, or follow-list data in the HTML (guest token API returns 89 Invalid/expired) — don't waste time grepping for them. To get the 5-following list you need an authenticated session or a working Nitter/twstalker mirror (usually Cloudflare'd now).

## 3. Platform existence sweep (username)

`curl -skL -o /dev/null -w "%{http_code}"` per candidate; cheap and parallelizable:
- **Useful**: instagram, tiktok, facebook, youtube `@u`, reddit `/user/`, github, twitch (301 = maybe, follow up), x.com (200 = account page), t.me (200).
- **Trap: 200 != exists.** Steam (`Steam Community :: Error`, `id/<u>` may redirect), Discord, Threads, Pinterest, Snapchat return 200 with a *default/error* page for non-existent users. **Verify 200s by grepping the body** for a real `"username":"..."`, `<title>Error</title>`, or "doesn't exist" — never report a hit from status code alone.
- Target platforms may rate-limit IG aggressively (429 after a couple hits) — sequential requests, low volume.

## 4. Group membership ("dia gabung group apa aja") — passive ceiling

Telegram group membership is **PRIVATE**; passive engines only index users who *posted/noticed* in public groups:
- **Lyzem** (`https://lyzem.com/search?q=<handle>`): grep for `N results – <ms>` in body. 0 results = never posted publicly in indexed groups. Also search the *display name* (same engine).
- **Combot** (`https://combot.org/telegram/u/<handle>`): 404 = user not in their public-group index (gives member counts otherwise).
- **Telemetr / TGStat**: useful but Cloudflare-walled from datacenter IPs; retry via browser later, don't block on it.
- If display name also yields 0 across engines and the X profile is minimal (1 follower, no bio): strong conclusion = **private-chat activity / burner account**, not a group joiner. Say that plainly instead of inventing leads.

## 5. Search engines

- **DuckDuckGo html endpoint** (`html.duckduckgo.com/html/?q="<handle>"`) works unauthenticated; parse `result__a` anchors. Bing works too — **watch out**: its result links are `bing.com/ck/a` redirect wrappers that need `u=a1aHR0...` base64 decode to reveal the real URL.
- Google blocks plain curl (000) — skip or use browser.
- Exact-quote the handle AND the display name; similarity-looking names on other platforms (e.g. "apanyak" in India) are usually unrelated — note resemblance, don't merge.

## Pitfalls

- **Status 200 on unknown-user pages is the #1 false positive.** Always body-verify.
- **Don't over-invest**: minimal footprint (1 follower, no photo, no bio, no group hits) IS the finding — report "burner/low-profile" and stop rather than inventing platforms to check.
- Guest-token X API and most Nitter mirrors are dead/Cloudflare'd from datacenter IPs — don't burn time, note the auth requirement and move on.
- Group membership has no free passive answer beyond the search engines above; if the user needs the real list (mutual groups), the only reliable path is an authenticated Telegram session (`contacts.search` / client API) — offer it as the next step, don't fake it.
