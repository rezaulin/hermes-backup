# Extracting a Design System from a Deployed App's CSS Bundle

Use case: the user has an old/other deployed app whose look they love and wants a
different app restyled to match it. You don't need the source — the production CSS
bundle IS the design system. Pull it, read the tokens, replicate.

## Workflow

1. Download the built CSS from the deployed URL (see main SKILL Step 2), e.g.
   `curl -s -o design.css https://the-app.web.app/assets/index-<hash>.css`.
2. Extract the design tokens — the `:root{}` block is the whole palette/typography/radius spec:
   ```python
   import re
   css = open('design.css').read()
   root = re.search(r':root\{([^}]*)\}', css)
   for d in root.group(1).split(';'):
       if d.strip(): print(d.strip())
   ```
   You get `--bg-primary`, `--accent-primary`, `--glass-bg`, `--glass-blur`, `--radius-*`,
   `--font-family`, etc. — copy these verbatim into the target app.
3. Extract the component classes to see the actual construction (glassmorphism, sidebar,
   nav-item active state, responsive-table→cards). List class names, then print each rule:
   ```python
   classes = sorted(set(re.findall(r'\.([a-zA-Z][\w-]+)(?=[\{,:\s.])', css)))
   # then regex out `.<name>{...}` bodies for the ones you care about
   ```
4. Note the responsive strategy from `@media` queries (this app: sidebar 260px on desktop,
   fixed drawer + `.mobile-bottom-nav` under 768px, `.responsive-table` collapses `<td>`
   into stacked rows using `td:before{content:attr(data-label)}`).
5. Grep the JS bundle for the Indonesian/domain nav labels to confirm feature parity
   (Dashboard, Kasir, Produk, …).

## Replicating in a Tailwind v4 target

- Put the extracted `--color-*` tokens in BOTH `@theme{}` (so utilities like `bg-card`,
  `text-primary`, `border-border` generate — see `tailwind-v4-vite-setup.md`) AND `:root{}`
  (so the ported raw component classes like `.glass`, `.glass-btn` resolve `var(--...)`).
- Port the component classes into `@layer components{}` almost verbatim — `.glass`,
  `.glass-btn(-primary|-secondary|-danger|-ghost)`, `.glass-input`, `.sidebar`, `.topbar`,
  `.nav-item(.active)`, `.stat-icon`, `.mobile-bottom-nav`, `.responsive-table`.
- Wrap the app UI component library (Button/Card/Input) to emit those classes instead of
  ad-hoc Tailwind utilities, so every page inherits the look without per-page edits.
- Bulk-convert leftover light-theme utilities across feature pages with a scripted
  find-replace map (`text-gray-500`→`text-[var(--text-secondary)]`, `bg-white`→
  `bg-[var(--bg-secondary)]`, `text-blue-600`→`text-brand-400`, chart `stroke="#f0f0f0"`→
  dark grid, recharts `contentStyle` → dark tooltip). Then a build + grep pass for
  residual `bg-white`/`border-gray-`/`text-gray-` to catch stragglers.

## Verify by comparison

Screenshot the original login/dashboard, screenshot your port, and diff visually
(vision tool). Match: dark bg, accent color, glass card translucency, sidebar active
indicator, gradient logo tile. This is design-parity QA, not pixel-perfect cloning.
