# Premium "sellable" dashboard visual recipe (React + Tailwind v4)

## When this matters
For **client-facing / sellable** apps (dashboards, POS, SaaS the user resells per-client),
a UI that is merely functional-and-correct is NOT acceptable — feedback like *"UI/UX-nya
gak menjual"* ("this UI doesn't sell") means the visual layer is a first-class deliverable,
not a polish-later afterthought. Reach for this recipe by default on such apps instead of
shipping the flat default-Tailwind look (system font, flat blue, borderless white cards).

The gap between "renders correctly" and "looks sellable" is almost entirely: **font choice,
a real brand gradient, colored icon tiles, elevation/hover, and a hero band.** Cheap to add,
huge perceived-quality jump.

## Concrete moves that made the difference
1. **Real display font** — load via `index.html` `<link>` (Plus Jakarta Sans / Inter), set
   `--font-sans` in `@theme`, tighten headings with `letter-spacing: -0.02em`. System font is
   the #1 tell of a template.
2. **Brand gradient, not flat color** — indigo→violet
   (`linear-gradient(135deg,#6366f1,#4f46e5,#7c3aed)`). Register a `brand-50…900` scale in
   `@theme` so `bg-brand-600`, `text-brand-700` etc. generate (Tailwind v4 needs colors in
   `@theme` — see tailwind-v4-vite-setup.md).
3. **Hero header band** — page title sits inside a gradient card with faint offset circles
   (`absolute -right-8 -top-8 h-40 w-40 rounded-full bg-white/10`) and a white CTA button.
   Instantly reads "product," not "admin panel."
4. **KPI cards with colored icon tiles** — each metric card gets a 12×12 rounded-2xl tile with
   its own gradient (`from-emerald-500 to-green-600`, indigo, sky, amber) + white icon + shadow.
   Color-coded scanning + depth.
5. **Elevation + hover lift** — cards use soft layered shadows and a `card-hover` utility
   (`transition; hover: translateY(-2px) + bigger shadow + brand-200 border`).
6. **Chart polish (recharts)** — dashed horizontal-only `CartesianGrid`, axis `tickLine/axisLine=false`,
   gradient area fill, dot + activeDot, rounded tooltip with shadow. Kill the bare "L-shape" look.
7. **Split login** — two-column: left = gradient brand showcase (logo, headline, feature list),
   right = clean form with rounded inputs + `focus:ring-2 ring-brand-500/30`. Center single-card
   login is the template default; the split reads bespoke.
8. **Reusable CSS utilities** in `@layer utilities`: `.gradient-brand`, `.gradient-brand-soft`,
   `.text-gradient-brand` (bg-clip-text), `.card-surface`, `.card-hover`, `.glass` (header),
   `.shadow-brand`, a `fade-in-up` `.animate-in`. Lets every page share the language cheaply.

## Semantic-color caveat
Component libs use `bg-card`, `text-primary`, `border-border`, `bg-secondary`, `text-muted-foreground`.
In Tailwind v4 these ONLY generate if declared as `--color-<token>` inside `@theme` (literal HEX,
not `var()` indirection). Register the FULL set the components reference or the missing ones render
white/naked. Full diagnosis in `references/tailwind-v4-vite-setup.md`.

## Order of attack + reusable PageHeader
- Polish **client-facing screens first** (login, dashboard, main POS/workspace) — those get
  judged in the demo. Admin/settings pages can stay on the old style and keep working while you
  migrate them page-by-page.
- Build ONE reusable `PageHeader` component (icon-tile + title + subtitle + right-aligned
  `actions` slot) and roll it across list/detail pages. Kills the inconsistent per-page
  `<h1 class="text-3xl">` sprawl and makes the app feel designed by one hand.
- Pair the redesign with the demo-seed trick (`firestore-offline-first-patterns.md` §2c) so the
  screens show real numbers/curves during review instead of all-zeros.

## Process note
When redesigning, verify visually — don't trust "build passed." Drive the running preview
(navigate → login → screenshot/vision, with a SPECIFIC question: "do KPI cards have colored icon
tiles? does the total use a gradient? is data populated?") and confirm the actual pixels changed.
A green build with an unchanged-looking screenshot means CSS didn't regenerate or the browser
cached the old bundle (hard-refresh / hashed-filename check).

## Honest-note habit
Proactively flag the remaining gap that most hurts the "final" impression even when not asked —
e.g. "product cards still use a 📦 placeholder; real thumbnails would lift this most." The user
values knowing the weak spot over a clean-sounding but incomplete hand-off.
