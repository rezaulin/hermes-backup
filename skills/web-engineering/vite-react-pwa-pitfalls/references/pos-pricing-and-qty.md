# POS Pricing & Quantity Patterns (grosir/retail Indonesia)

Domain logic yang sering diminta di POS toko/grosir. Bukan bug — ini pola fitur
reusable. Dikonfirmasi langsung dengan user (Omni POS) via diskusi bertahap.

## Selalu diskusikan dulu sebelum implement
Pricing punya banyak varian. JANGAN asumsi — tanya user opsi konkret dengan
contoh angka. Keputusan kunci yang harus dipastikan:
- Cara hitung tiering (pecah ke satuan besar dulu vs semua kena harga grosir)
- Threshold (otomatis dari isi-dus vs set manual)
- Harga tier (otomatis dari harga dus÷isi vs input manual)
- Berlaku ke satuan count saja atau weight juga
- Level akses ubah harga (semua kasir vs manajer)

## 1. Input qty bebas
Field qty di keranjang & dialog pakai `type="text" inputMode="decimal"` (BUKAN
`type=number` step +/- saja). Parse `parseFloat(v.replace(',', '.'))` biar terima
koma (Indonesia) & titik. `onFocus={e => e.target.select()}` biar gampang timpa.

## 2. Kilogram / weight desimal
Kalau `product.baseUnit.type === 'weight'`: qty boleh desimal (0,25 / 1,5).
Harga = qty × harga/kg. Tombol cepat: 0.25 / 0.5 / 1 / 2 / 5. TANPA tiering.
Satuan `count` tetap integer.

## 3. Tiered / grosir pricing (HANYA base unit type=count)
Konsep: produk punya konversi dus (mis. dus isi 20, harga Rp60.000). Harga grosir
per-pcs = harga_dus / factor = Rp3.000. Kalau qty ≥ factor → SEMUA qty pakai harga
grosir itu (opsi yang dipilih user: "semua 35 pcs × 3.000", BUKAN pecah 1 dus + 15 pcs).
Ambil tier TERTINGGI yang factor-nya ≤ qty (harga per-base terendah).

```ts
// lib/products.ts
export function buildCartTiers(product) {
  if (product.baseUnit.type !== 'count') return []
  return (product.unitConversions || [])
    .filter(c => c.unit.type === 'count' && c.factor > 1 && c.price > 0)
    .map(c => ({ factor: c.factor, unitName: c.unit.name, pricePerBase: c.price / c.factor }))
    .sort((a, b) => a.factor - b.factor)
}
export function resolveTierPrice(listPrice, qty, tiers) {
  let best = { price: listPrice, label: undefined }
  for (const t of tiers)
    if (qty >= t.factor && t.pricePerBase < best.price)
      best = { price: t.pricePerBase, label: `harga ${t.unitName}` }
  return best
}
```
Tiering HANYA berlaku kalau user jual di BASE unit. Kalau user pilih satuan dus
langsung, harga = dus.price × qty (normal, bukan tiering).
Recalc di cart store: kalau `!item.manualPrice && item.tiers?.length`, terapkan
`resolveTierPrice(baseListPrice, qty, tiers)` tiap qty berubah.

## 4. Override harga manual saat checkout
Ketuk baris "qty × harga" di keranjang → input harga baru → `setItemPrice()`.
Set `manualPrice: true` → matikan auto-tier untuk item itu (harga manual menang).
Simpan `baseListPrice` (harga list asli) terpisah dari `pricePerUnit` (harga efektif).

## 5. Dialog pilih satuan + qty saat klik produk
- Multi-satuan (ada konversi ber-harga) ATAU produk weight → buka dialog:
  pilih satuan + input qty/berat + preview tier + preview total.
- Produk 1-satuan biasa (count) → langsung masuk keranjang, skip dialog.
Barcode scan → route lewat handler yang sama (buka dialog / langsung sesuai jenis).

## CartItem fields tambahan
`unitType`, `baseListPrice`, `tiers[]`, `manualPrice`, `appliedTier` (label mis.
"harga Dus"). Badge di keranjang: `· harga Dus` (emerald) kalau tier aktif,
`· manual` (amber) kalau harga di-override.
