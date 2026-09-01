# Firestore + Dexie Offline-First Patterns (Vite SPA)

Proven patterns from building an offline-first POS app (React + TypeScript + Firebase + Dexie). These are the traps that actually broke builds and runtime.

## 1. IndexedDB CANNOT INDEX BOOLEANS

The #1 trap. `.where('synced').equals(false)` silently fails — IndexedDB indexes don't support booleans (or null, arrays). Use 0/1:

```ts
// Schema: synced is a NUMBER, not boolean
offlineQueue: 'id, type, action, synced, timestamp'

await db.offlineQueue.add({ ..., synced: 0 })
await db.offlineQueue.where('synced').equals(0).toArray()
await db.offlineQueue.update(id, { synced: 1 })
```

Type it honestly: `synced: number // 0 | 1 (booleans can't be indexed)`.

## 2. Offline-first service pattern (Firestore primary, IndexedDB fallback)

Every service function: try Firestore, catch network failure, fall back to Dexie. Mirror every successful Firestore write to local too so offline reads stay warm.

```ts
export async function listProducts(): Promise<Product[]> {
  try {
    const snap = await getDocs(query(collection(firestore, 'products'), orderBy('name')))
    return snap.docs.map(d => ({ ...d.data(), id: d.id }) as Product)
  } catch {
    return await localDb.products.orderBy('name').toArray()
  }
}
```

For offline mutations, write to a queue table and replay on reconnect:

```ts
export function useOnlineSync() {
  // listen 'online' event -> syncOfflineTransactions()
  // poll pending count every 10s for a UI badge (Wifi/WifiOff indicator)
}
```

Sync replay MUST be idempotent: check `doc.exists()` inside a Firestore transaction before re-writing, and decrement stock only once.

## 2b. Placeholder/dummy Firebase config HANGS reads — it does NOT throw (demo mode)

The try/catch fallback in §2 assumes Firestore *errors* on failure. But with a **dummy/placeholder** config (`apiKey: "<value>"`, `your_project`, etc. — common when demoing before real credentials), the Firestore SDK does NOT throw: it enters retry/backoff and the promise **hangs indefinitely**. So `getDocs()` never resolves, `catch` never fires, and the offline fallback is never reached → the whole app looks "empty" (dashboard all zeros, product list blank) even though IndexedDB has data.

Symptom: seeded/local data exists but every list renders empty; no JS error in console; network tab shows Firestore requests pending/retrying forever.

Fix: detect placeholder config at init and short-circuit straight to IndexedDB — never touch Firestore in demo mode.

```ts
// firebase.ts
const PLACEHOLDER_HINTS = ['<value>', 'your_', 'dummy', 'xxx', 'demo-']
const looksConfigured = (v?: string) =>
  !!v && !PLACEHOLDER_HINTS.some(h => v.toLowerCase().includes(h))
export const isDemoMode = !(looksConfigured(cfg.apiKey) && looksConfigured(cfg.projectId))

// every read service:
export async function listX() {
  if (isDemoMode) return await localDb.x.toArray()   // skip Firestore entirely
  try { /* Firestore */ } catch { /* offline fallback */ }
}
```

Rule of thumb: a `catch`-based offline fallback only protects against *reachable-but-failing* backends. An *unconfigured* backend needs an explicit up-front guard, because the SDK's "helpful" retry turns a config error into a silent hang.

**CRITICAL — the `isDemoMode` guard must wrap EVERY WRITE path too, not just reads.** It's easy to guard the list/get functions and forget the mutations. In demo mode a `runTransaction`/`setDoc`/`updateDoc` against a dummy config hangs or returns `permission-denied`, so:
- `checkout()` never persists the sale → transactions list stays empty even though the cart cleared and the UI flashed "success".
- `nextInvoiceNumber()` (counter-doc transaction) hangs → checkout blocks.
- Shift open/close, `adjustDeposit`/`adjustKasbon`, stock `adjustStock`, product/category CRUD all silently no-op.

Pattern for every write service: branch on `isDemoMode` to a pure-IndexedDB implementation, else the Firestore path. Examples proven this session:
```ts
// invoice number: count today's INV-* in Dexie instead of the Firestore counter doc
if (isDemoMode) {
  const prefix = `INV-${dateStr}-`
  const n = await localDb.transactions.filter(t => t.number?.startsWith(prefix)).count()
  return `${prefix}${String(n + 1).padStart(4, '0')}`
}

// checkout: decrement stock + write tx straight to Dexie (no Firestore transaction)
if (isDemoMode) {
  for (const item of cart.items) { /* localDb.products.update stock */ }
} else { await runTransaction(firestore, ...) }

// customer ledger / inventory movements have no Dexie table in the base schema —
// stash them in localStorage (JSON array, cap length) rather than migrating Dexie mid-build:
const LS = 'omni_pos_ledger'; // read/write/push helpers
```
Non-demo writes should ALSO be wrapped `try { await firestoreWrite } catch {}` then mirror to Dexie, so a real-but-offline backend degrades the same way.

Verification that catches this class of bug: after a demo checkout, navigate to the transactions/history page and assert the row appears (and the invoice count increments). A green "transaction success" toast is NOT proof of persistence — the cart clears regardless.

## 2c. Auto-seed demo data on bootstrap (idempotent, URL-controlled)

For a demo the client can click through immediately, seed IndexedDB before mounting React. Keep it idempotent (skip if data exists) and give a force flag via query param so you can reset:

```ts
// main.tsx bootstrap() before ReactDOM.createRoot
const seed = new URLSearchParams(location.search).get('seed')
if (seed !== '0') await seedDemoData(seed === '1')   // ?seed=1 forces re-seed, ?seed=0 skips
```

`seedDemoData(force)` — `if (count>0 && !force) return`; on force, `clear()` the tables first. Spread transactions across the last N days with `Date.setDate(-offset)` + random hour so the 7-day chart shows a real curve, and give a couple of products stock below `minStock` so the low-stock panel is non-empty. Makes the dashboard demo-ready without manual data entry.

## 3. Firestore transactions: ALL reads before ALL writes

Firestore rejects a transaction that reads after a write. Batch every read first:

```ts
await runTransaction(firestore, async tx => {
  // 1) ALL reads
  const snaps = await Promise.all(refs.map(r => tx.get(r)))
  // 2) ALL writes
  tx.set(doc(...), transaction)
  snaps.forEach((s, i) => tx.update(refs[i], { 'stock.total': ... }))
})
```

Use transactions for: checkout (write tx + decrement stock + inventory movement), deposit/kasbon balance adjustments (read balance → validate limit → write balance + ledger entry in one atomic op).

## 4. Sequential invoice counters via counter document

Firestore has no auto-increment. Use a `config/counters` doc:

```ts
const num = await runTransaction(firestore, async tx => {
  const snap = await tx.get(counterRef)
  const key = `invoice_${dateStr}`        // resets daily: INV-20250115-0001
  const next = (snap.data()?.[key] || 0) + 1
  tx.set(counterRef, { [key]: next }, { merge: true })
  return next
})
return `INV-${dateStr}-${String(num).padStart(4, '0')}`
```

Offline fallback: `INV-${dateStr}-OFF${timestamp suffix}` — flag it so ops can reconcile duplicates.

## 5. Ledger/audit pattern for customer balances (deposit & kasbon)

Never update a balance without a ledger entry, always in the same transaction:

- `customerLedger` collection: `{ customerId, type: 'deposit_topup'|'deposit_used'|'kasbon_added'|'kasbon_paid', amount, balanceAfter, referenceType, referenceId, createdAt }`
- Validate inside the transaction: deposit can't go negative; kasbon checked against `creditLimit`.
- Settlement at POS checkout: after transaction completes, mutate balances (kasbon used as payment → balance +, deposit used → balance −) and update customer stats (totalSpent, transactionCount, lastTransactionAt). Wrap in try/catch so a settlement failure never voids the sale — it will re-sync.

## 6. Report aggregation: client-side when volume is small

For small-store apps, pull completed transactions in a time range and aggregate in JS — simpler than maintaining pre-aggregated docs:

```ts
function computeSalesSummary(txs, startTs, endTs): SalesSummary {
  // pre-fill every day in range so charts have zero-days
  // accumulate: revenue, profit = subtotal - costPrice*baseQty,
  // daily map (YYYY-MM-DD key), top products map, payment method map
}
```

Key detail: pre-initialize the daily map for the whole range so charts render zero-days instead of gaps.

## 7. Thermal receipt printing (58/80mm)

Generate monospace HTML at fixed width (48mm body for 58mm paper, 72mm for 80mm), open a popup, `win.print()` after ~250ms delay (Firefox needs it):

```ts
const win = window.open('', '_blank', 'width=400,height=600')
win.document.write(buildReceiptHtml(tx, store, width))
win.document.close(); win.focus()
setTimeout(() => { win.print(); win.close() }, 250)
```

Use `@page { margin: 0 }`, Courier New, dashed separators, right-aligned amounts. Keep a "cetak ulang struk" button bound to the last transaction object.

## 8. TS pitfalls that bit this build (tsc strict)

- **Dexie `.get()` returns `T | undefined`** — a service typed `Customer | null` needs `(await localDb.customers.get(id)) ?? null`.
- **TanStack Query `mutationFn`** — don't pass a multi-arg function (`adjustDeposit(customerId, amount, opts)`) directly; wrap it and pass ONE object variable: `mutationFn: ({customerId, amount, opts}) => svc(customerId, amount, opts)`.
- **Union types defined elsewhere** — before writing `tier === 'vip'`, grep the type: it was `'regular'|'silver'|'gold'|'platinum'|'diamond'`. Comparisons against non-member literals are TS2367 errors under strict.
- **Unused imports fail `tsc -b`** with `noUnusedLocals` — after refactors, expect 3-5 of these; they're mechanical to clear.
- **forwardRef for shadcn-style Input** — if any component needs a ref (barcode search focus), convert to `forwardRef<HTMLInputElement, Props>` with `useId()` for the input id.

## 8b. `crypto.randomUUID()` is UNDEFINED over http://IP (non-secure context)

The trap that only shows up once you serve the app off the VPS instead of localhost. `crypto.randomUUID()` is gated to **secure contexts** — it exists on `https://…` and on `http://localhost`, but is **undefined** on `http://<IP>:port` (e.g. `http://185.245.61.91:4173`). So the build is green, localhost works, and then the moment the user opens it over the LAN/VPS IP, every code path that mints an id throws:

```
crypto.randomUUID is not a function. (In 'crypto.randomUUID()', 'crypto.randomUUID' is undefined)
```

In this app that meant "saving a product / transaction / customer / stock adjustment" crashed silently (the create looked like it did nothing). It's easy to misread as a validation bug — it isn't, it's the id generator crashing before persist.

Fix: never call `crypto.randomUUID()` directly. Add one helper and use it everywhere:

```ts
// lib/utils.ts
export function uuid(): string {
  if (typeof crypto !== 'undefined' && typeof crypto.randomUUID === 'function') {
    return crypto.randomUUID()                       // HTTPS / localhost
  }
  if (typeof crypto !== 'undefined' && crypto.getRandomValues) {
    const b = crypto.getRandomValues(new Uint8Array(16))  // works on plain HTTP too
    b[6] = (b[6] & 0x0f) | 0x40; b[8] = (b[8] & 0x3f) | 0x80
    const h = Array.from(b, x => x.toString(16).padStart(2, '0'))
    return `${h[0]}${h[1]}${h[2]}${h[3]}-${h[4]}${h[5]}-${h[6]}${h[7]}-${h[8]}${h[9]}-${h.slice(10).join('')}`
  }
  return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, c => {
    const r = Math.random() * 16 | 0; return (c === 'x' ? r : (r & 0x3) | 0x8).toString(16)
  })
}
```

`crypto.getRandomValues()` (and `crypto.subtle` is the one that's actually restricted — getRandomValues is NOT) is available in insecure contexts, so tier 2 is the real workhorse on a VPS-over-HTTP demo. Grep the whole tree for `crypto.randomUUID(` and replace all — this app had 9 files (products, transactions, customers, inventory, categories, users, shift, seed, indexeddb).

Pitfall while doing the bulk replace: if you script an "add import" pass, don't insert the `import { uuid } from './utils'` line *inside* a multi-line `import type { … }` block — it produces `TS1003 Identifier expected`. Insert after the LAST top-level import statement, or just verify the first 12 lines of each touched file compile.

Related: prefer verifying create/save flows over the **actual deployed origin** (http://IP), not just localhost — secure-context APIs (`crypto.randomUUID`, `crypto.subtle`, service workers on some setups, clipboard, geolocation) behave differently there.

## 9. Cashier shift reconciliation

Open shift records `openingCash`. On close, query the shift's completed transactions, sum cash payments minus change → `cashSales`, `expectedCash = openingCash + cashSales`, then store `closingCash` (actual count) and `difference = closingCash - expectedCash`. Store transactionCount for the shift report.

## 10. Barcode input UX

Two paths: (a) hardware scanner = fast keystrokes ending in Enter → keep a dedicated input that on Enter looks up `product.barcode` then each `unitConversions[].barcode` (multi-unit products have per-unit barcodes); (b) camera scanning via `html5-qrcode` (`facingMode: 'environment'`, `qrbox` 250x150). Add an F2-style shortcut to focus search.

## 11. Vite build verification loop

After each feature phase: `npm run build` (tsc -b && vite build) → fix errors → rebuild until clean → smoke test with `vite preview` on a port, curl for HTTP 200 + `<title>` + manifest. Run preview as a background process, curl in a follow-up call, then kill it — never `cmd &` inline in the terminal tool.
