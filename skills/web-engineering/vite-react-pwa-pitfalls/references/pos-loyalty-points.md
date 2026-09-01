# POS Loyalty Points — Earn/Burn/Expiry Pattern

Complete blueprint for implementing loyalty points in a POS system (earn on purchase, burn for discount, optional expiry). Based on real implementation in Omni POS (Vite + React + Zustand + Firestore/IndexedDB).

## Architecture Overview

```
StoreConfig.loyalty (LoyaltyConfig)     ← settings, editable by admin
    ↓
Customer.points (balance counter)        ← single source of truth for saldo
CustomerLedgerEntry (points_earned/redeemed/expired/adjusted) ← audit trail
    ↓
CartStore.pointsToBurn (optional number) ← UI state: how many points to use
    ↓
checkout() → earn + burn calculation → save transaction + update customer points
    ↓
ReceiptDialog + receipt.ts → display points earned/burned on nota
```

## 1. Types

### LoyaltyConfig (embed in StoreConfig)
```ts
export interface LoyaltyConfig {
  enabled: boolean
  earnRate: number           // Rp X = 1 poin (e.g. 10000)
  burnRate: number           // 1 poin = Rp Y (e.g. 100)
  minBurn: number            // min poin to burn (e.g. 10)
  maxBurnPercent: number     // max % of total payable by points (0-100, e.g. 50)
  tierMultiplier: Record<CustomerTier, number>  // regular:1, silver:1.2, gold:1.5...
  expiryMonths: number       // 0 = no expiry
}
```
Embed in `StoreConfig.loyalty?: LoyaltyConfig` — single config doc, no separate collection.

### Transaction fields
```ts
pointsEarned?: number      // poin yang didapat dari transaksi ini
pointsRedeemed?: number    // poin yang dipakai untuk diskon
pointsDiscountRp?: number  // nominal diskon dari poin (Rupiah)
```

### LedgerEntry extension
Add `points_earned | points_redeemed | points_expired | points_adjusted` to ledger type union.
Add optional fields: `pointsAmount?: number`, `earnedAt?: number`, `expiresAt?: number`.

## 2. Default Config
```ts
export const DEFAULT_LOYALTY_CONFIG: LoyaltyConfig = {
  enabled: false,           // off by default, admin turns on
  earnRate: 10000,          // Rp 10.000 = 1 poin
  burnRate: 100,            // 1 poin = Rp 100
  minBurn: 10,              // minimum 10 poin to use
  maxBurnPercent: 50,       // max 50% of total
  tierMultiplier: { regular: 1, silver: 1.2, gold: 1.5, platinum: 2, diamond: 3 },
  expiryMonths: 0,          // no expiry by default
}
```

## 3. Calculation Functions (pure, testable)

### Earn
```ts
function calculateEarnedPoints(total: number, customer: Customer, config: LoyaltyConfig): EarnResult {
  if (!config.enabled) return { points: 0, multiplier: 1, basePoints: 0 }
  const basePoints = Math.floor(total / config.earnRate)
  const multiplier = config.tierMultiplier[customer.tier] || 1
  const points = Math.floor(basePoints * multiplier)
  return { points, multiplier, basePoints }
}
```
**Key:** earn calculated on FINAL total (after burn discount), so burning points doesn't inflate earned points.

### Burn
```ts
function calculateBurnPoints(total, customerPoints, requestedPoints, config): BurnResult {
  if (!config.enabled || customerPoints < config.minBurn) return zero
  const maxDiscountRp = (total * config.maxBurnPercent) / 100
  const maxPointsFromTotal = Math.floor(maxDiscountRp / config.burnRate)
  const maxPoints = Math.min(customerPoints, maxPointsFromTotal)
  const pointsToBurn = requestedPoints !== undefined ? Math.min(requestedPoints, maxPoints) : maxPoints
  if (pointsToBurn < config.minBurn) return zero
  const discountAmount = pointsToBurn * config.burnRate
  return { pointsToBurn, discountAmount, newTotal: Math.max(0, total - discountAmount) }
}
```
**Key:** burn capped by `maxBurnPercent` of total — prevents paying 100% with points (store needs some cash flow).

## 4. Cart Store Integration

Add `pointsToBurn?: number` to cart state. Reset to `undefined` when:
- Customer changes (`setCustomer` action)
- Cart cleared (`clear` action)

No `pointsDiscountRp` in store — calculated at checkout (needs async `getStoreConfig`).

## 5. Checkout Flow

```
1. Calculate cart.total() (existing)
2. Load settings → getStoreConfig() → loyalty config
3. If customer + loyalty enabled:
   a. Get customer data (points balance)
   b. If pointsToBurn > 0: calculateBurnPoints → get discountRp, newTotal
   c. calculateEarnedPoints(finalTotal, customer, config) → get pointsEarned
4. Build Transaction with pointsEarned, pointsRedeemed, pointsDiscountRp
5. Save transaction + update stock (existing flow)
6. Update customer points: adjustPoints(customerId, -pointsRedeemed, ...) then adjustPoints(customerId, +pointsEarned, ...)
7. Clear cart (includes pointsToBurn reset)
```

**Order matters:** burn FIRST (reduces total), then earn on reduced total. Burn THEN earn in customer update too (burn first so if points go to 0, earn adds back).

## 6. adjustPoints Function

```ts
async function adjustPoints(customerId, amount, opts: { type, referenceId, createdBy }): Promise<void> {
  // Dual-path: isDemoMode → IndexedDB + localStorage ledger
  //            online → Firestore runTransaction (atomic balance update + ledger entry)
  const newPoints = Math.max(0, customer.points + amount)
  // Update Customer.points
  // Push CustomerLedgerEntry with type, pointsAmount, referenceId
}
```
Use `runTransaction` for Firestore (atomic read-modify-write on customer.points).

## 7. UI Components

### CartPanel (customer info area)
- Show saldo poin next to customer name: `⭐ {points} poin`
- If loyalty enabled + has customer:
  - Input field "Min {minBurn} poin" + "Pakai" button + "Semua" button
  - Preview: "{points} poin = -{formatCurrency(discountRp)}"
  - Error messages: "Minimum X poin", "Saldo tidak cukup"
- Display final total = cart.total() - pointsDiscountRp

### ReceiptDialog (nota preview)
After payment rows, before footer:
```
⭐ Poin didapat          +{pointsEarned}
⭐ Poin dipakai          -{pointsRedeemed}
  (Diskon poin)          -{formatCurrency(pointsDiscountRp)}
```

### Receipt thermal print (receipt.ts)
Same info as ReceiptDialog — add after change/kembalian rows.

## 8. Implementation Sequence (PITFALL)

Correct order for checkout-adjacent features:
1. **Types first** — LoyaltyConfig, extend Transaction, extend CustomerLedgerEntry
2. **Default config** — in settings.ts, embed in DEFAULT_STORE_CONFIG
3. **Pure functions** — loyalty.ts (calculateEarnedPoints, calculateBurnPoints)
4. **adjustPoints** — in customers.ts (dual-path demo/Firestore)
5. **Cart store** — add pointsToBurn field + setPointsToBurn action + reset on clear/setCustomer
6. **Checkout** — import loyalty + adjustPoints, calculate in checkout function
7. **UI** — CartPanel burn input, ReceiptDialog display
8. **Build check** — `npm run build` after each phase

### Common build errors to expect:
- **Unused import** — `CustomerTier` imported but only used in Record type → remove from import
- **Interface mismatch** — declaring `pointsDiscountAmount()` in CartState interface but not implementing → either implement or remove from interface
- **Duplicate import** — when patching manually, watch for double `import { adjustPoints }` lines
- **Dynamic import warning** — if `getCustomer` is already statically imported elsewhere, don't also `await import('./customers')` — use the static import consistently

## 9. Future: Expiry System (Lazy FIFO)

Not yet implemented. Approach when ready:
- Each `points_earned` ledger entry gets `earnedAt` and `expiresAt` timestamps
- Burn uses FIFO: deduct from oldest earned batch first
- Periodic check (or at checkout): reduce balance for expired points, log `points_expired` entry
- UI warning: "X poin kadaluarsa dalam 30 hari"
- Requires querying pointsLedger by customerId + type=points_earned, sorted by earnedAt
