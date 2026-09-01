# POS Software Licensing & Pricing (Indonesian Market)

> Business model knowledge for selling POS/kasir software as desktop install with license system. Covers perpetual vs subscription, hardware binding, tiering, and pricing strategy for Indonesian retail clients.

## Vendor Models in the Wild (Indonesian POS market)

### Fully Offline (Traditional)
- Data 100% di komputer klien, NO cloud backup
- Hardisk rusak / kena virus = **beli ulang dari awal** (re-purchase)
- Lisensi terikat hardware (MAC + disk serial + CPU ID)
- Ganti hardisk / komputer = lisensi mati, harus bayar activation fee lagi (~250rb, max 3x/tahun)
- "Langganan" di sini biasanya = **sewa lisensi** (stop bayar = software terkunci) atau **maintenance contract** (software tetap jalan tapi gak di-support)

### Cloud/Hybrid (Modern: Moka, Pawoon, Majoo)
- Langganan 150-500rb/bulan
- Data di-sync ke cloud (hardisk rusak = data aman)
- Owner bisa pantau dari HP
- Vendor punya recurring revenue

### OMNI POS Positioning (Hybrid Offline-First)
- Install di komputer lokal (offline-first, tetap jalan tanpa internet)
- Optional cloud sync (upgrade feature)
- License validation butuh internet (ringan, ~1KB per check)
- Data klien 100% di komputer mereka (selling point: privasi)

## Pricing Tiers (Recommended)

| | **Basic** | **Pro** | **Enterprise** |
|--|-----------|---------|-----------------|
| Harga | Rp 2.500.000 | Rp 5.000.000 | Rp 10.000.000 |
| Kasir | 1 | 3 | Unlimited |
| POS Kasir | ✅ | ✅ | ✅ |
| Produk & Pelanggan | ✅ | ✅ | ✅ |
| Inventori | ❌ | ✅ | ✅ |
| Laporan Dasar | ✅ | ✅ | ✅ |
| Laporan Lengkap (25) | ❌ | ✅ | ✅ |
| Akuntansi Double-Entry | ❌ | ❌ | ✅ |
| Surat Jalan | ❌ | ✅ | ✅ |
| Import/Export Excel | ❌ | ✅ | ✅ |
| Retur (jual & beli) | ❌ | ❌ | ✅ |
| PO/Supplier | ❌ | ❌ | ✅ |
| Loyalty Points | ❌ | ✅ | ✅ |
| Multi-gudang | ❌ | ❌ | ✅ |
| Support | WA jam kerja | WA 12 jam | WA + Remote 24 jam |
| Update | 1 tahun | 1 tahun | Lifetime |
| Target | Toko kecil/warung | Toko menengah/kafe | Retail chain/grosir |

## Recurring Revenue Streams

| Item | Harga | Frequency |
|------|-------|-----------|
| Perpanjangan lisensi (Basic/Pro) | 20% dari harga beli | Tahunan |
| Re-aktivasi (ganti komputer) | Rp 250.000 | Max 3x/tahun |
| Training on-site | Rp 500.000/sesi (2 jam) | Per request |
| Data migration (dari software lama) | Rp 1.000.000 | Per project |
| Cloud backup add-on | Rp 100.000/bulan | Bulanan |
| Multi-device sync add-on | Rp 100.000/bulan | Bulanan |
| Custom feature request | Nego | Per project |

## License System Architecture

### License Key Format
```
OMNI-XXXX-XXXX-XXXX-XXXX (20 karakter)
Encrypted payload: edition + max_kasir + modules + expiry + client_id
```

### Activation Flow (Offline-Friendly)
```
KLIEN                          VENDOR
1. Install app                  │
2. App generate HWID            │
3. WA/telepon: "HWID saya XYZ"  │
                                4. Input HWID + tier di License Generator
                                5. Generate activation code
6. Input code di app            │
7. Verify → ✅ AKTIF            │
```

### License States
```
TRIAL (30 hari, watermark DEMO)
  → NEEDS ACTIVATION (trial habis, input key)
    → ACTIVE (full access sesuai tier)
      → EXPIRED (tahunan, perlu perpanjang)
      → LOCKED (revoke oleh vendor)
```

### Grace Period
- License server down → app tetap jalan 7 hari (last-known-good)
- No internet → app tetap jalan (offline mode), license check deferred
- HWID mismatch → re-activation flow (free, max 3x/tahun)

## Revenue Projection

```
Tahun 1: 20 klien × rata-rata Pro (5jt)     = Rp 100.000.000
Tahun 2: 40 klien baru + 20 renewal          = Rp 210.000.000
Tahun 3: 60 klien baru + 60 renewal          = Rp 330.000.000
+ maintenance + re-aktivasi + training + add-ons
= recurring revenue grows each year
```

## Cost to Operate

| Item | Cost | When |
|------|------|------|
| Electron + electron-builder | Rp 0 | Always |
| Cloudflare Workers (license API) | Rp 0 | <100K clients |
| Cloudflare D1 (license DB) | Rp 0 | <5GB data |
| GitHub Releases (host .exe) | Rp 0 | Always |
| Code signing certificate | ~Rp 3.000.000/yr | Optional |
| **Total phase 1** | **Rp 0** | **Free** |

## Selling Points vs Competitors

| OMNI POS Advantage | Why it matters |
|--------------------|---------------|
| Data 100% di komputer klien | Privasi, no vendor lock-in |
| Offline-first | Toko di area tanpa internet tetap jalan |
| Akuntansi double-entry (PSAK) | Competitor mahal baru punya |
| No "beli ulang kalau rusak" | License re-activation murah |
| Multi-device sync (add-on) | Upsell opportunity |
| Dark glassmorphism UI | Modern look, stands out |

## Key Insight: "Data di komputer sendiri" ≠ No Cloud Needed

Even fully offline POS vendors need a THIN cloud layer for:
1. **License validation** — prevent unlimited copying
2. **Activation server** — automate key generation
3. **Blacklist/revoke** — disable non-paying clients

This can run on Cloudflare Workers FREE tier (100K req/day = thousands of clients).
