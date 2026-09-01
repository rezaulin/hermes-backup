# Adopting an existing design language into a Tailwind v4 app

When the user already has a design they like (often a **previously deployed app**
whose CSS you can extract) and wants a new/other app to match it, don't invent a
fresh look — **port the real one**. This is a class-level migration technique, proven
by re-skinning a light-theme POS into the user's production dark-glassmorphism design.

## 0. Rule: the user's shipped design beats anything you'd design fresh
If the user says "I already have a nice UI, learn from it" and points at a URL or an
extracted bundle, treat that as the source of truth. Extract its tokens verbatim
rather than approximating — approximations read as "generic" and get rejected.

## 1. Extract the design tokens from the deployed CSS
Deployed SPA CSS is minified but the `:root{}` block and component classes are intact.
Pull them programmatically (regex), don't eyeball a screenshot:

```python
css = open('assets/index-XXXX.css').read()
root = re.search(r':root\{([^}]*)\}', css).group(1)      # --bg-primary, --accent-*, --glass-*, --radius-*
classes = sorted(set(re.findall(r'\.([a-zA-Z][\w-]+)(?=[\{,:\s.])', css)))  # inventory of component classes
# then print full rules for the layout/component classes you care about:
for m in re.finditer(r'(\.'+name+r'[\w-]*(?:[:> ][^{]*)?)\{([^}]*)\}', css): ...
```

Capture: color tokens (bg/text/accent/glass), radius scale, font family, shadow/blur
values, and the **layout classes** (`.sidebar`, `.topbar`, `.nav-item.active`,
`.glass`, `.glass-btn*`, `.glass-input`, `.responsive-table`, keyframes, media queries).
A screenshot (`browser_vision`) is useful to confirm the *feel* (dark? glass? accent
color?) but the CSS is where the exact numbers live.

## 2. Port tokens into Tailwind v4 `@theme` — NOT just `:root`
Tailwind v4 only generates `bg-card`/`text-primary`/`border-border` utilities when the
color is declared as `--color-<name>` inside `@theme{}` (see
`tailwind-v4-vite-setup.md` §"Second layer"). So register the extracted palette twice:
- `@theme { --color-background: #0f111a; --color-primary: #6d28d9; ... }` → utilities
- `:root { --bg-primary: ...; --glass-bg: ...; --glass-blur: blur(12px); ... }` → the
  raw vars consumed by the ported component classes.

Then drop the extracted component classes verbatim into `@layer components`
(`.glass`, `.glass-btn-primary`, `.glass-input`, `.sidebar`, `.nav-item`, `.topbar`,
`.avatar`, `.stat-icon`, `.responsive-table`) and keyframes/utilities into
`@layer utilities`. Keep the vendor prefixes (`-webkit-backdrop-filter`) — glassmorphism
needs them.

## 3. Re-point the shared UI primitives once
Change the atoms so every page inherits the new look for free:
- `Button` → render `glass-btn glass-btn-{primary|secondary|danger|ghost}` (map
  `outline`→secondary so existing call-sites keep working).
- `Card` → just `.glass`.
- `Input` → `.glass-input` (+ `.with-icon`, `.input-error`).
- Layout shell → swap top-nav for `.sidebar` + `.topbar` + `.mobile-bottom-nav`
  (drawer on ≤768px with `.sidebar-backdrop`).

## 4. Bulk-convert the leaf pages with a scripted regex pass
Feature pages carry hard-coded light utilities (`text-gray-500`, `bg-white`,
`border-gray-200`, `text-blue-600`). Converting 15+ files by hand is slow and
error-prone — run ONE `execute_code` pass with an ordered replacement table
(longer/more-specific patterns first), then a second pass for leftovers
(`bg-white`, chart `stroke="#f0f0f0"`, recharts `contentStyle`, native `<select>` →
add `[&>option]:bg-[var(--bg-secondary)]`). Example mapping that worked:
`text-gray-500 → text-[var(--text-secondary)]`, `bg-gray-50 → bg-white/5`,
`border-gray-200 → border-[var(--glass-border)]`, `text-blue-600 → text-brand-400`,
`bg-white → bg-[var(--bg-secondary)]`, `text-red-600 → text-red-400` (dark theme wants
the 400 shades, not 600). Rebuild after each pass; `noUnusedLocals` will flag icons you
stopped using — clear them mechanically.

## 5. Recharts needs explicit dark theming
Charts don't inherit CSS vars. Set per-component: `CartesianGrid stroke="#ffffff10"`,
axis `stroke="#a0a8b9"` + `tickLine={false} axisLine={false}`, and a shared dark
`Tooltip contentStyle` (`background:#1a1d2d`, `border:1px solid #ffffff1a`, white text).
Recolor series to the brand palette (violet `#8b5cf6`, emerald `#10b981`).

## 6. Verify with the browser-vision loop, not assumptions
After building + `vite preview`, drive the real page: `browser_navigate` → type demo
creds → click Masuk → `browser_vision` with a pointed question ("dark theme? sidebar?
glass cards? accent color? data populated?"). Vision catches "it built but still looks
light/naked" that a green build hides. This is the same loop that caught the two
Tailwind-v4 styling bugs earlier in the same project.

## Pitfalls
- Porting only the palette but leaving layout as top-nav loses the whole feel — the
  sidebar/topbar structure IS most of the design. Port structure too.
- Forgetting `@theme` registration → semantic utilities silently no-op (naked UI).
- Native `<select>`/`<option>` stay white-on-white in dark mode until you add
  `[&>option]:bg-[var(--bg-secondary)]`.
- `100dvh` + `position:fixed` body from the source can trap scrolling; keep the app's
  own scroll container (`.page-content { overflow-y:auto }`).
