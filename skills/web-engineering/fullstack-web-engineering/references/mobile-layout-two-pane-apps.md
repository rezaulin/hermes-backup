# Making a desktop-first two-pane app work on mobile (POS/dashboard)

Learnings from adapting a desktop 2-column POS (product grid + cart) to phones.
The user's standard is explicit: **the secondary pane must FLOAT (FAB + bottom-sheet), not stack below the primary pane.** Feedback verbatim: *"keranjang harusnya menggantung bukan dibawah produk"* and *"cek semua layout handpone yang belum simetris"*. Treat "just stack the columns vertically" as a wrong answer for master/detail or list/cart layouts.

## 1. Two-pane (list + cart/detail) → FAB + bottom-sheet on mobile

Desktop: `grid lg:grid-cols-3` with product list `lg:col-span-2` + cart in the right column.
Mobile: DON'T let the cart render as a second stacked block under the list — it pushes the list off-screen and looks broken (user sees "keranjang doang").

Pattern that satisfied the user:
- Primary pane (product grid) takes the full mobile width, with `pb-20` so the last row clears the FAB.
- Cart column: `hidden lg:block` — hidden entirely on mobile.
- A floating pill button `fixed bottom-20 right-4 z-40 lg:hidden`, shown only when the cart has items, badged with item count + live total. `bottom-20` clears the mobile bottom-nav (~64px).
- Tapping the FAB opens a bottom-sheet: full-screen `fixed inset-0 z-50 flex flex-col justify-end`, dimmed backdrop (`bg-black/60 backdrop-blur-sm`, click to close), sheet `rounded-t-3xl max-h-[85vh]` sliding up via the existing `slideUpFade` keyframe.
- Reuse the SAME cart component in both places via an `embedded` prop that hides its internal header (the sheet already has one). Reset `cartOpen=false` after a successful checkout so the sheet dismisses.

```tsx
{cart.items.length > 0 && !cartOpen && (
  <button className="lg:hidden fixed bottom-20 right-4 z-40 glass-btn-primary rounded-full …"
          onClick={() => setCartOpen(true)}>
    <ShoppingCart/> <badge>{cart.items.length}</badge> {formatCurrency(cart.total())}
  </button>
)}
{cartOpen && (
  <div className="lg:hidden fixed inset-0 z-50 flex flex-col justify-end">
    <div className="absolute inset-0 bg-black/60 backdrop-blur-sm" onClick={close}/>
    <div className="relative glass rounded-t-3xl max-h-[85vh] flex flex-col"
         style={{ animationName:'slideUpFade' }}>
      …<CartPanel embedded/>…
    </div>
  </div>
)}
```

## 2. Fixed heights are desktop-only — gate them behind `lg:`

The original bug: `style={{ height: 'calc(100vh - 220px)' }}` + `overflow-hidden` applied at ALL breakpoints. On a 1-column mobile stack this pins the container and clips the list to near-zero height, so only the cart below shows. Fix: move the fixed height and overflow to `lg:` only, give the mobile pane a natural `min-h-[60vh]`:

```
lg:h-[calc(100vh-220px)]          // height only on desktop
lg:col-span-2 glass p-4 lg:overflow-hidden min-h-[60vh] lg:min-h-0
```

Rule: any `h-[…vh]`, `overflow-hidden`, or `overflow-y-auto` meant to make a desktop pane scroll internally MUST be `lg:`-prefixed, or it breaks the mobile stack.

## 3. Custom CSS grid classes that aren't defined → cards collapse to one ragged column

Dashboard used `<div className="dashboard-top-grid">` / `dashboard-bottom-grid` but those classes were **never defined in any CSS** (they weren't Tailwind utilities and weren't in index.css). Result: no grid at all — KPI cards stacked in one column and looked unstyled on every viewport. Two ways to avoid:
- Prefer Tailwind responsive utilities directly: `grid grid-cols-2 gap-4 lg:grid-cols-4` for KPI tiles, `grid grid-cols-1 lg:grid-cols-[2fr_1fr] gap-4` for chart+side-panel.
- If you keep a semantic class name, you MUST define it (in Tailwind v4 put it under `@layer utilities` in index.css) with an explicit `@media (min-width:1024px)` bump. A class name alone does nothing.

Good mobile default for KPI tiles is **2 columns**, not 1 (1 wastes vertical space) and not 4 (too cramped) — go 4 only at `lg:`.

## 4. Long values overflow narrow tiles

Currency KPI values (`Rp 5.280.270`) truncated to `Rp 811…` inside 2-col mobile tiles. Drop the tile value from `text-3xl` to `text-xl md:text-2xl` and keep `truncate` + a `min-w-0` parent so flex children can actually shrink.

## 5. Wide tables: horizontal scroll is an acceptable minimum

Every data table wrapped in `overflow-x-auto` stays usable on mobile (swipe sideways) — that's the functional baseline and was fine for this app. The prettier upgrade is the `.responsive-table` card-collapse pattern (thead hidden, each `td` becomes a row with a `data-label` pseudo-element) already defined in index.css; use it when the client wants tables to read as cards on phones. Either is acceptable; a table that simply overflows the viewport with no scroll wrapper is not.

## 6. Modals/dialogs → bottom-sheet on mobile (centered modals force scroll-hunting)

A shared `Dialog` centered with `items-center` + padding looks fine on desktop but on a phone a tall dialog (payment, product form) overflows the viewport centered, so the user must scroll UP to see the total and DOWN to find the confirm button. Verbatim complaint: *"menu pembayaran harus geser lagi keatas baru ketemu"*. Fix the shared Dialog once and every consumer benefits:

- Container: `flex items-end justify-center sm:items-center sm:p-4` — sheet sticks to the bottom on mobile, centers on desktop.
- Panel: `rounded-t-3xl sm:rounded-2xl`, `max-h-[92vh] sm:max-h-[90vh]`, `flex flex-col overflow-hidden`, entrance `slide-in-from-bottom-4 sm:zoom-in-95`.
- Make `DialogHeader`/`DialogFooter` `shrink-0` and `DialogContent` `overflow-y-auto` so the header (total) and footer (confirm button) stay pinned while only the middle scrolls. This is what removes the scroll-hunting.

## 7. Post-transaction receipt: in-app dialog with a print CHOICE, never an auto popup

Two corrections landed here: (a) *"setelah transaksi selesai harusnya ada pilihan cetak nota atau tidak"* — do NOT auto-print on checkout; show a success dialog offering **Cetak Nota** vs **Tutup**. (b) *"cetak gak usah popup tapi dalam aplikasi"* — do NOT print via `window.open(...).print()`; popup windows are blocked/janky on mobile browsers.

Pattern:
- On checkout success, open a `ReceiptDialog` that renders the receipt as a normal in-DOM node (white `.receipt-print` block inside the dark glass dialog) so the user previews it.
- Print with CSS `@media print` scoping instead of a popup: hide everything (`body * { visibility: hidden }`), reveal only `.receipt-print, .receipt-print *`, position it top-left, force `color:#000;background:#fff`. Trigger with `window.print()` after toggling a `printing-receipt` body class; also add `.print\:hidden { display:none !important }` so the dialog's own buttons don't get printed.
- Keep the old HTML-string builder only if you still want a thermal-printer raw path; the in-app dialog is the default UX.

## 8. Verifying mobile without a resize API

The browser tool ran at a fixed 1280px width this session, so mobile breakpoints couldn't be exercised live — desktop layout was verified visually and mobile was reasoned from the `lg:`/`@media` rules + user screenshots. When you can't resize: (a) confirm desktop still looks right after the change, (b) read back the exact breakpoint classes/media queries, (c) ask the user for a phone screenshot to close the loop. Don't claim mobile is verified from a desktop-width screenshot.
