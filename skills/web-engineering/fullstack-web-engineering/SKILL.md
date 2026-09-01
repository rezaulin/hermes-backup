---
name: fullstack-web-engineering
description: Comprehensive full-stack web engineering guide for AI agents — covers product, UX, design, frontend, backend, database, API, auth, security, integrations, performance, testing, deployment, observability, and maintenance.
version: 1.0
tags: [web, fullstack, react, typescript, architecture, security, deployment, design-system]
---

# FULL-STACK WEB ENGINEERING FOR AI AGENTS

> Version: 1.0
> Purpose: Teach an AI agent to plan, design, build, test, secure, deploy, and maintain production-quality web applications.

---

## 01 — PURPOSE

This skill defines how an AI agent should approach complete web projects.

The agent is responsible for more than generating attractive UI.

It must reason across:

- PRODUCT, UX, DESIGN
- FRONTEND, BACKEND, DATABASE, API
- AUTH, SECURITY, INTEGRATIONS
- PERFORMANCE, TESTING, DEPLOYMENT
- OBSERVABILITY, MAINTENANCE

Core principle:

> Build a coherent product system, not a collection of pages.

The agent must convert vague requirements into explicit technical and design decisions.

Do not begin coding immediately when the architecture is unclear.

---

## 02 — PRIMARY WORKFLOW

```
USER REQUIREMENTS → PROJECT DISCOVERY → PRODUCT DEFINITION
→ UX / INFORMATION ARCHITECTURE → DESIGN DIRECTION
→ TECHNICAL ARCHITECTURE → DATA MODEL → API CONTRACT
→ FRONTEND ARCHITECTURE → BACKEND IMPLEMENTATION
→ INTEGRATIONS → SECURITY → TESTING → PERFORMANCE
→ DEPLOYMENT → OBSERVABILITY → QA → ITERATION
```

Never skip architecture merely because the project appears small.
However, do not over-engineer simple projects.

---

## 03 — REQUIREMENT ANALYSIS

Before implementation, extract:

- Project, Website / application type, Primary purpose
- Target users, Primary user action, Secondary actions
- Business rules, Required pages, Required data
- External services, Authentication, Payments, File uploads
- Admin requirements, Deployment target

Separate into: **Functional** (what it must do), **Non-functional** (how it must behave), **Constraints** (budget, APIs, hosting, deadline).

---

## 04 — REQUIREMENT PRIORITY

Classify: P0 (mandatory), P1 (important), P2 (useful), P3 (optional).

Priority order:
```
Security > Correctness > Data integrity > Accessibility > Core UX > Performance > Visual polish > Nice-to-have
```

---

## 05 — PROJECT TYPES

Identify first: Static website, Marketing, Portfolio, Blog, E-commerce, Dashboard, SaaS, Booking, Marketplace, Community, CMS, Admin panel, AI app, API service, Automation, Internal tool.

Do not force every project into the same architecture.

---

## 06 — ARCHITECTURE SELECTION

> Choose the simplest architecture that safely satisfies the requirements.

Options: Static, SSR, SSG, SPA, Server-rendered, Monolith, Modular monolith, SOA, Microservices, Serverless, Event-driven, Worker-based.

Prefer modular monolith over microservices unless justified.

---

## 07 — DEFAULT TECHNOLOGY STACK

**Frontend:** React, TypeScript, Vite, Tailwind CSS

> Tailwind v4 pitfall: if the app builds but renders **completely unstyled** (elements present, no layout/colors), the `@tailwindcss/vite` plugin is almost certainly missing from `vite.config.ts` — v4 does NOT use `tailwind.config.js`+PostCSS by default. See `references/tailwind-v4-vite-setup.md` for one-line diagnosis (grep built CSS for `.flex{`) and fix.
**Backend:** Node.js, TypeScript, Fastify/Express
**Database:** PostgreSQL (prefer relational for transactional apps)
**Validation:** Zod or equivalent
**Testing:** Vitest, Playwright
**Deployment:** Vercel, Cloudflare, Railway, Fly.io, Docker, VPS

---

## 08–12 — DESIGN SYSTEM

Define before coding components:
- Brand, Positioning, Visual direction
- Color system (every color must have a role: bg, text, border, accent, interactive, success, warning, error)
- Typography system (assign fonts by function: display, body, UI, mono)
- Spacing, Grid, Radius, Borders, Elevation, Motion
- Design tokens centralized in `:root` CSS variables

Use `clamp()` for fluid typography. Never scatter arbitrary values.

---

## 13–14 — INFORMATION ARCHITECTURE & UX FLOW

Define page structure before implementation. Every section needs: Purpose, Content, Hierarchy, Interaction, Responsive behavior.

Map user journeys. Every flow needs: loading, success, error, empty state, retry behavior.

---

## 15–16 — COMPONENT ARCHITECTURE & STATE

Clear responsibility per component. Avoid giant components and needless abstractions.

Classify state:
- **Local UI:** isMenuOpen, activeTab
- **Server:** users, projects, orders
- **URL:** page, filter, search
- **Persistent client:** theme, cart, preferences

Do not introduce global state for trivial local state.

---

## 17–18 — DATA FETCHING & FORMS

Define: endpoint, method, request, response, loading, error, cache, retry.

Every form: fields, types, required, validation, error messages, submission, loading, success, failure, reset.

Client-side validation for UX. Server-side validation is mandatory for security.

---

## 19–21 — BACKEND, API DESIGN, HTTP STATUS

Separate: Routes → Validation → Business Logic → Data Access → Database.

Define endpoints explicitly with auth, authorization, input/output schema, status codes, error format, rate limits.

Use status codes intentionally. Never return 200 for everything.

Consistent error response:
```json
{ "error": { "code": "VALIDATION_ERROR", "message": "...", "fields": {} } }
```

---

## 22–25 — DATABASE

Start from domain entities. Define: PK, FK, required/nullable, unique, indexes, timestamps, relationships.

Use migrations — versioned, repeatable, reviewable, deployable.

Enforce integrity at DB level (UNIQUE, NOT NULL, FK, CHECK, INDEX).

Use transactions when operations must succeed/fail together. Rollback on failure.

---

## 26–28 — AUTH & SESSIONS

Authentication = Who is the user?
Authorization = What can they do?

Prefer secure HttpOnly cookies. Never store sensitive credentials in localStorage.

Passwords: never plaintext, use strong hashing.

Define roles explicitly (guest, user, editor, admin, owner). Enforce server-side.

Session cookies: HttpOnly, Secure, SameSite, appropriate expiration, rotation.

---

## 29–34 — SECURITY

Validate every untrusted input (body, query, params, headers, files, webhooks).

Baseline: XSS, SQL injection, CSRF, SSRF, path traversal, command injection, prototype pollution, broken access control, credential leakage, rate abuse, file upload abuse, dependency vulns.

Never hardcode secrets. Use env vars or secret manager.

Configure CORS intentionally. Never `Access-Control-Allow-Origin: *` for sensitive APIs.

Rate-limit: login, signup, password reset, OTP, search, AI endpoints, payments.

---

## 35–36 — FILE UPLOADS & STORAGE

Never trust filename, extension, or client MIME type.

Validate: size, content type, file signature, dimensions, allowed formats.

Generate safe server-side names. Use object storage for production media.

Separate: database, object storage, cache, temporary filesystem.

---

## 37–39 — PAYMENTS, WEBHOOKS, IDEMPOTENCY

Payment flow: client → server → provider → webhook → server verification → database.

Never trust client to confirm payment. Verify server-side.

Webhooks: signature verification, timestamp validation, idempotency, duplicate handling, logging.

Idempotent operations: payment, order, email, reservation, webhook processing.

---

## 40–42 — EMAIL, BACKGROUND JOBS, QUEUES

Email: provider, sender, template, trigger, retry, failure behavior. Don't block HTTP on slow email — queue it.

Workers for: email, video/image processing, AI generation, exports, scraping, sync.

Queue: job type, payload, retry count, backoff, timeout, dead-letter, idempotency, concurrency.

---

## 43–45 — CACHING, SEARCH, PAGINATION

Cache layers: browser, CDN, app, Redis, DB query cache. Define TTL, invalidation, stale behavior, key, fallback.

Search: query, filters, sort, pagination, indexing strategy. Don't load entire datasets client-side.

Pagination: offset or cursor. Never expose unlimited DB results.

---

## 46–49 — OBSERVABILITY, ERRORS, REQUEST IDS, ANALYTICS

Track: errors, latency, volume, failed jobs, auth failures, payment failures, critical events.

Structured logs: `{ "level", "event", "requestId", "timestamp" }`. Never log passwords, tokens, keys.

Request/correlation IDs for debugging distributed operations.

Only collect required analytics. Define events, properties, conversions, privacy, retention.

---

## 50 — SEO

For public sites: title, description, canonical, robots, sitemap, semantic HTML, Open Graph, structured data.

Use real content. No keyword stuffing. Private dashboards: SEO is not priority.

---

## 51–54 — PERFORMANCE, IMAGES, FONTS, ACCESSIBILITY

Prioritize: LCP, CLS, INP, TTFB, image/JS payload, font loading, server/DB latency.

Images: correct dimensions, modern formats, responsive sizes, lazy loading, explicit dimensions.

Fonts: only required families, weights, subsets. Appropriate `font-display`.

Accessibility minimum: semantic HTML, keyboard nav, visible focus, color contrast, alt text, labels, form errors, reduced motion, touch targets. Never communicate by color alone.

---

## 55–58 — TESTING & CI/CD

Layers: Unit → Integration → E2E → Visual QA.

Always test highest-risk flows: signup, login, checkout, payment, booking, admin mutation, uploads, webhooks.

CI/CD: install → lint → typecheck → test → build → deploy (only if checks pass).

---

## 59–61 — CODE QUALITY, ENV, BACKUP

Before completion: no unused imports, no dead code, no duplicated logic, no hardcoded secrets, no unnecessary deps, no broken types, no console noise.

Maintain `.env.example` with placeholders. Never commit real secrets.

DB backup: strategy, retention, restore procedure. A backup is useless if you can't restore.

---

## 62–65 — DEPLOYMENT, DOCKER, HEALTH CHECKS, CRON

Pre-deploy verify: env vars, DB, migrations, storage, domain, HTTPS, CORS, cookies, webhooks, email, cron, health checks, logging.

Docker: multi-stage, small runtime, non-root, health checks. Use when it improves reproducibility/deployment.

Health check: lightweight `GET /health`. Don't make it expensive.

Cron: schedule, timezone, idempotency, failure behavior, logging, retry.

---

## 66–70 — INTEGRATIONS, AI, ADMIN, AUDIT, PRIVACY

Third-party: credentials, request, response, timeout, retry, rate limit, error mapping, fallback, logging.

AI: API keys server-side. Define model, timeout, token/cost limits, retry, fallback, content validation, rate limits.

Admin: every action authorized server-side. Sensitive mutations auditable.

Audit logs: actor, action, target, timestamp, result, request ID.

Privacy: collect only necessary data. Define what, why, where, who, how long, how to delete.

---

## 71–78 — STATES, QA CHECKLISTS, PRODUCTION GATE

Every data page: loading, empty, error, success, partial data.

Design QA: typography, spacing, alignment, images, contrast, hierarchy, responsive, animation, consistency.

Security QA: secrets, auth, authorization, validation, injection, CSRF, XSS, rate limits, uploads, webhooks, cookies, headers, deps.

Performance QA: hero speed, images, CLS, animations, API latency, queries, pagination, caching, bundle size.

Functional QA: nav, forms, validation, auth, CRUD, uploads, payments, webhooks, emails, jobs, admin, errors.

Responsive QA: mobile narrow/wide, tablet, desktop, large desktop.

Browser QA: Chromium, Firefox, Safari, mobile browser.

Production gate: Architecture ✓, Core ✓, Security ✓, DB ✓, Errors ✓, A11y ✓, Perf ✓, Testing ✓, Deploy ✓, Monitor ✓, Backup ✓.

---

## 79–81 — DECISION RULES

Do not over-engineer (microservices, K8s, event buses without need).
Do not under-engineer (secrets in frontend, trust client, skip validation).

Key rules:
- Static only → CDN/static generation
- Transactional → relational DB
- Auth exists → secure session architecture
- Sensitive mutation → server-side validation + auth
- Payment → verify provider server-side
- Webhook → verify signature + idempotency
- Expensive async → background job
- Large dataset → paginate
- User uploads → validate + object storage
- Public content → SEO priority
- Private dashboard → UX over SEO
- Feature not required → don't add architecture

---

## 82–86 — DEBUGGING, TRUTH, CONSISTENCY, DOCS

Debug: Reproduce → Observe → Identify boundary → Inspect inputs/outputs → Logs → State → Fix root cause → Regression test → Verify.

Source of truth: auth=server, payment=provider, authorization=server, inventory=DB, UI=frontend, design=design system.

Data consistency across systems: transactions, idempotency, retries, compensation.

Document: README, setup, env vars, DB, migrations, dev, test, build, deploy, architecture, API, limitations.

---

## 87–91 — STRUCTURE, DESIGN+ENG, PREMIUM/FUTURISTIC/JAPANESE

Reasonable full-stack structure:
```
project/
├── app/ ├── components/ ├── features/ ├── lib/ ├── hooks/
├── styles/ ├── public/
├── server/ (routes, controllers, services, repositories, schemas, middleware, jobs)
├── db/ (schema, migrations, seeds)
├── tests/ (unit, integration, e2e)
├── scripts/ ├── docs/ ├── .env.example
```

Design and engineering must agree (e.g., "drawer opens" → accessible dialog + focus mgmt + scroll lock).

Premium ≠ gold/black/glow/glass. Premium = typography + spacing + images + restraint + micro-interactions.

For client-facing / resellable apps, "renders correctly" is NOT the bar — a flat default-Tailwind look (system font, flat blue, borderless white cards) reads as an unfinished template and draws "UI-nya gak menjual" feedback. See `references/premium-dashboard-visual-recipe.md` for concrete cheap-but-high-impact moves (display font, brand gradient, colored KPI icon tiles, hero band, elevation/hover, recharts polish, split login), and ALWAYS verify a redesign visually in the running preview (navigate → screenshot/vision), not just via a green build — a passing build with an unchanged screenshot means the CSS didn't regenerate or the browser cached the old bundle.

When the user says they ALREADY HAVE a design they like (a deployed URL, an extracted CSS bundle) and wants an app to match it, do NOT design fresh — extract and port the real tokens + layout. See `references/adopting-extracted-design-language.md` (regex-extract `:root` + component classes from minified CSS → register palette in Tailwind v4 `@theme` → re-point Button/Card/Input atoms → scripted bulk regex pass over leaf pages → dark-theme Recharts explicitly → verify with browser-vision). The user's shipped design always beats anything you'd invent.

Futuristic: choose one direction (editorial, industrial, Japanese, scientific, speculative, cybernetic). Not always neon cyberpunk.

Japanese: negative space, asymmetry, precision, modular grids, editorial typography, quiet hierarchy, material contrast, controlled red.

---

## 92–96 — AGENT BEHAVIOR & DIRECTIVES

Agent must: reason before implementation, prefer explicit constraints, reuse conventions, inspect before changing, preserve working code, make minimal safe changes, test regression risks.

Never rewrite a functioning project just because a different architecture looks cleaner.

Change classification: UI-only, Frontend logic, API, Database, Auth, Security, Infrastructure.

**No fake completion:** Never claim "implemented/tested/secure/deployed/working" without verification. If unverified, state "not verified".

Final directive:
```
UNDERSTAND → DESIGN → ARCHITECT → MODEL → IMPLEMENT → SECURE → TEST → OPTIMIZE → DEPLOY → OBSERVE → VERIFY
```

Priority:
```
INTENT > CORRECTNESS > SECURITY > DATA INTEGRITY > UX > DESIGN > PERFORMANCE > MAINTENABILITY > DECORATIVE EFFECTS
```

Goal: beautiful + usable + correct + secure + maintainable + observable + deployable.

---

## ADDITIONS — REAL-TIME / WEBSOCKETS

When real-time updates are needed (chat, live dashboards, notifications, collaborative editing):

Options: WebSocket, Server-Sent Events (SSE), Long Polling, Push Notifications.

- WebSocket for bidirectional (chat, collaboration)
- SSE for unidirectional server→client (feeds, dashboards)
- Always handle: connection drop, reconnection, heartbeat, auth on connect
- Scale: connection pooling, pub/sub (Redis), horizontal scaling strategy
- Security: authenticate on connect, validate messages, rate limit per connection

---

## ADDITIONS — INTERNATIONALIZATION (i18n)

When multi-language support is needed:

- Choose strategy: URL-based (`/en/about`), subdomain (`en.site.com`), or accept-language header
- Externalize all user-facing strings (never hardcode)
- Use i18n libraries: `react-intl`, `next-intl`, `vue-i18n`
- Handle: RTL languages, date/number formatting, pluralization rules
- Content: translate at source, not in components
- Fallback: always have a default language
- SEO: `hreflang` tags for search engines

---

## ADDITIONS — PWA (PROGRESSIVE WEB APP)

Beyond manifest.webmanifest:

- Service Worker: caching strategy (cache-first, network-first, stale-while-revalidate)
- Offline-first: core content available offline
- Push notifications: permission flow, payload handling, unsubscribing
- Installability: `beforeinstallprompt` event
- Background sync for offline actions
- Test: Lighthouse PWA audit, real device testing

For offline-first data apps (Firestore + IndexedDB/Dexie): see `references/firestore-offline-first-patterns.md` — IndexedDB can't index booleans (use 0/1), Firestore transactions need all-reads-before-writes, counter-doc invoice numbers, ledger/audit balance pattern, thermal receipt printing, the `isDemoMode` guard that must wrap every WRITE (not just reads) when running on a dummy Firebase config, and the `crypto.randomUUID()`-is-undefined-over-`http://IP` secure-context trap (use a `getRandomValues` fallback `uuid()` helper) that silently breaks every save once the app is served off a VPS IP instead of localhost.

---

## ADDITIONS — FEATURE FLAGS & GRADUAL ROLLOUT

For controlled feature releases:

- Define: flag name, rollout percentage, user segments, environment
- Tools: LaunchDarkly, Unleash, custom DB-based, env vars for simple cases
- Always: cleanup old flags, don't accumulate dead flags
- A/B testing: statistical significance, user assignment consistency
- Kill switch: ability to disable features without deployment

---

## ADDITIONS — MULTI-TENANCY

For SaaS with tenant isolation:

Strategies: separate DB per tenant, shared DB + tenant_id column, schema per tenant.

- Never leak data across tenants (row-level security, middleware tenant resolution)
- Subdomain or path-based tenant routing
- Tenant-specific: branding, settings, quotas, billing
- Migrations must apply to all tenant databases/schemas
- Test: verify tenant isolation at every level

---

## ADDITIONS — DATA EXPORT & IMPORT

When users need data portability:

- Export formats: CSV, JSON, PDF
- Import: validate schema, handle duplicates, report errors
- Large exports: stream/queue (don't block HTTP)
- GDPR right to data portability
- Bulk operations: progress tracking, cancellation, partial failure handling

---

## ADDITIONS — API VERSIONING

When APIs evolve over time:

Strategies: URL-based (`/api/v1/`), header-based (`Accept: application/vnd.api.v2`), query param (`?version=2`).

- Never break existing clients without deprecation period
- Deprecation: communicate timeline, provide migration guide
- Sunset header for deprecated versions
- Maintain old version for N months after new version release

---

## ADDITIONS — MONOREPO & WORKSPACE MANAGEMENT

When multiple packages share code:

- Tools: Turborepo, Nx, pnpm workspaces
- When to use: shared components, multiple apps, internal libraries
- When not to use: single app, simple project
- Handle: shared dependencies, version alignment, build caching
- CI: only build affected packages, not everything

---

## ADDITIONS — ERROR BOUNDARIES & GRACEFUL DEGRADATION

Frontend resilience:

- React Error Boundaries: catch component crashes, show fallback UI
- API error boundaries: retry with backoff, cached data fallback
- Offline detection: show offline banner, queue mutations
- Partial data: render what you have, don't blank the whole page
- Skeleton screens: show structure while loading

---

## ADDITIONS — NOTIFICATION SYSTEM

Push and in-app notifications:

- Types: push (browser/mobile), in-app, email, SMS
- User preferences: granular control (what, when, channel)
- Delivery: queue-based, respect rate limits, deduplication
- Templates: reusable, localized, with action buttons
- Tracking: delivery status, open rate, click-through

---

## ADDITIONS — DEPENDENCY MANAGEMENT

Maintain project health:

- Lockfiles: always commit (package-lock.json, yarn.lock, pnpm-lock.yaml)
- Security: `npm audit`, Dependabot, Snyk, or equivalent
- Update strategy: regular updates, test before merge, don't auto-merge major
- Peer deps: verify compatibility before updating
- Bundle analysis: monitor size changes, catch accidental bloat
- License compliance: check for incompatible licenses in commercial projects

---

## ADDITIONS — GRAPHQL CONSIDERATION

When REST isn't sufficient:

Use GraphQL when: multiple clients need different data shapes, deeply nested data, over-fetching is costly.

Don't use when: simple CRUD, file uploads are primary, team unfamiliar, simple public API.

Handle: N+1 queries (DataLoader), query depth limits, complexity analysis, persisted queries, caching strategy.

---

## ADDITIONS — SSR HYDRATION

For Next.js / Nuxt / Remix patterns:

- Understand: SSR → HTML → hydrate → interactive
- Common issues: hydration mismatch, flash of unstyled content, client-only components
- Streaming SSR: partial hydration, Suspense boundaries
- Selective hydration: prioritize above-the-fold
- Test: both SSR and client-only rendering paths

---

## ADDITIONS — COMPLIANCE & LEGAL

GDPR, CCPA, and similar regulations:

- Cookie consent: granular, no pre-checked boxes, no dark patterns
- Data deletion: "right to be forgotten" — cascade delete, verify
- Data access: users can request their data
- Consent tracking: log what was consented to, when, version
- Data residency: store in required region when mandated
- Privacy policy: keep current, link from relevant places
- Children's data: COPPA compliance if applicable

---

## ADDITIONS — MOBILE-SPECIFIC UX

Beyond responsive layout:

- Gesture handling: swipe, pinch, long-press
- Haptic feedback on mobile interactions
- Safe areas: notch, home indicator (`env(safe-area-inset-*)`)
- Pull-to-refresh pattern
- Bottom navigation for mobile-first apps
- Touch targets: minimum 44x44px
- Keyboard handling: input types, avoid layout shift
- Status bar styling for installed PWAs

For adapting a DESKTOP-first two-pane app (list+cart, master+detail, POS) to phones, see `references/mobile-layout-two-pane-apps.md`. Key rule this user enforces: the secondary pane must FLOAT as a FAB + bottom-sheet on mobile, NOT stack below the primary pane ("keranjang harusnya menggantung bukan dibawah produk"). Also covers: gate every fixed `h-[…vh]`/`overflow` behind `lg:` (unprefixed heights clip the mobile stack), never ship semantic grid class names that aren't actually defined in CSS (they collapse to one ragged column — use Tailwind `grid-cols-2 lg:grid-cols-4` or define the class under `@layer utilities`), shrink long currency KPI values (`text-xl md:text-2xl` + `truncate`/`min-w-0`), make the shared Dialog a bottom-sheet on mobile (`items-end sm:items-center`, pinned shrink-0 header/footer + scrolling content) so tall payment/form modals don't force scroll-hunting, show a post-checkout receipt dialog with an explicit Cetak/Tutup CHOICE (never auto-print) and print via CSS `@media print` scoping (never `window.open` popup), and that you can't claim mobile is verified from a desktop-width browser screenshot.