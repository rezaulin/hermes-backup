# Tailwind CSS v4 + Vite — setup & the "no-styling" bug

## Symptom
App builds cleanly and JS runs (elements present, text visible, routing works),
but the page looks **unstyled / naked**: no layout, sidebar and content stacked
vertically, no colors, no spacing. Vision/screenshot shows "UI pecah" — components
render but every utility class is a no-op.

## Root cause
Tailwind v4 changed how it plugs into the build. In v4 you do NOT use
`tailwind.config.js` + PostCSS by default. Instead:

- `src/index.css` contains `@import "tailwindcss";`
- The build MUST run the **`@tailwindcss/vite`** plugin to scan source and generate
  utility classes.

If the plugin is missing, `@import "tailwindcss"` still compiles — but it only emits
the `@theme` block (CSS variables like `--color-red-500`, font tokens). **Zero
utility classes** (`.flex`, `.grid`, `.min-h-screen`, `.bg-gray-50`) are generated.
Build succeeds, so nothing errors — the UI is just silently unstyled.

## Fast diagnosis (no browser needed)
```bash
# 1. Find the built CSS and grep for real utility classes:
grep -oE '\.(flex|grid|min-h-screen|bg-gray-50)\{' dist/assets/*.css | head
#   -> if EMPTY, utilities aren't generated (bug confirmed)
#   -> if present, styling is wired; look elsewhere

# 2. Confirm plugin presence:
ls node_modules/@tailwindcss/vite    # missing dir = not installed
grep -n "tailwindcss" vite.config.ts # must import + call the plugin
```
A tiny built CSS that's mostly `@theme{...--color-*...}` with no `.flex{}` etc. is
the tell.

## Fix
```bash
npm install -D @tailwindcss/vite@^4   # match tailwindcss major version
```
```ts
// vite.config.ts
import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import tailwindcss from '@tailwindcss/vite'   // <-- add

export default defineConfig({
  plugins: [react(), tailwindcss()],           // <-- register
})
```
Rebuild. Built CSS should jump in size and now contain the utility classes.
After redeploy, **hard-refresh the browser** (Ctrl+Shift+R) — the old unstyled CSS
is cached under a hashed name but the HTML may be cached too.

## Second layer: semantic color tokens render "white/naked" even AFTER the plugin works
This is a distinct, sneakier bug that appears once the plugin is installed. Generic
utilities (`flex`, `grid`, `bg-gray-50`) generate fine, but the app still looks
**white and washed-out**: cards have no surface/border, brand color is gone, borders
vanish. Components render, layout is roughly right, but there's no color/depth.

### Root cause
Component libraries (shadcn-style) use **semantic tokens** as utility classes:
`bg-background`, `bg-card`, `text-primary`, `text-muted-foreground`, `border-border`,
`bg-secondary`, `bg-muted`, `ring-ring`, `bg-destructive`, etc.

In Tailwind v4 these utilities are ONLY generated if the color is registered inside a
`@theme { --color-<name>: ... }` block. If the values live only in a plain
`:root { --color-...: ... }` (v3 mental model / shadcn v3 template), v4 does NOT emit
`.bg-card{}`, `.text-primary{}`, `.border-border{}` — those classes become no-ops and
every surface falls back to transparent/inherited white.

### Fast diagnosis
```bash
# grep the BUILT css for semantic tokens the components actually use:
for c in bg-background bg-card text-primary text-muted-foreground border-border bg-primary; do
  n=$(grep -oE "\.${c}[{: ]" dist/assets/*.css | head -1); echo "$c => ${n:-MISSING}"; done
# ALL MISSING while .flex{}/.grid{} exist  => semantic tokens not in @theme (this bug)

# find which semantic tokens the source relies on (so you register the right ones):
grep -rhoE '\b(bg|text|border|ring)-(background|foreground|card|popover|primary|secondary|muted|accent|destructive|border|input|ring)(-foreground)?\b' src/ | sort -u
```

### Fix
Add a `@theme` block in `src/index.css` (right after `@import "tailwindcss";`) that
declares every semantic color as `--color-<token>`. Use literal HEX (not `var(...)`
indirection) so the v4 generator resolves them:
```css
@import "tailwindcss";
@theme {
  --color-background: #ffffff;  --color-foreground: #0f172a;
  --color-card: #ffffff;        --color-card-foreground: #0f172a;
  --color-primary: #2563eb;     --color-primary-foreground: #ffffff;
  --color-secondary: #f1f5f9;   --color-secondary-foreground: #0f172a;
  --color-muted: #f1f5f9;       --color-muted-foreground: #64748b;
  --color-accent: #f1f5f9;      --color-accent-foreground: #0f172a;
  --color-destructive: #dc2626; --color-destructive-foreground: #ffffff;
  --color-border: #e2e8f0;      --color-input: #e2e8f0;  --color-ring: #2563eb;
}
```
Rebuild, re-verify with the grep above (should now print `.bg-card{` etc.), redeploy,
hard-refresh. Register the FULL set the components reference — a partial set leaves the
missing ones as no-ops (e.g. `bg-secondary` still white).

> Debug order for "unstyled Tailwind v4": (1) are generic utilities like `.flex{}` in
> the built CSS? No → plugin missing (layer 1). Yes but app still white/naked → grep
> semantic tokens; MISSING → register them in `@theme` (layer 2). Two separate fixes.

## Notes
- v3 used `postcss.config.js` + `tailwind.config.js` + `@tailwind base/components/utilities`.
  v4 uses `@import "tailwindcss"` + the Vite plugin (or `@tailwindcss/postcss`).
  Don't mix mental models — check which major is in `package.json`.
- Same class of bug hits any framework: if utilities aren't generated, the integration
  (plugin/PostCSS) is missing, not the CSS import.
- shadcn/ui templates written for v3 put tokens in `:root` only. Porting to v4 requires
  mirroring those tokens into `@theme` or the `bg-card`/`text-primary`/`border-border`
  utilities silently disappear.
