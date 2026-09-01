---
name: vite-react-pwa-pitfalls
description: Bug fixes and gotchas untuk Vite + React + Tailwind v4 PWA (offline-first, Firebase optional, demo mode). Load saat build/debug SPA POS/dashboard yang di-deploy via HTTP IP (bukan HTTPS), pakai Tailwind v4, IndexedDB/Dexie, layout mobile bottom-sheet, drawer sidebar, tabel responsive, atau elemen fixed/floating yang tidak nempel viewport. Covers 10 bug nyata yang bikin app "jalan tapi salah" secara senyap.
---

# Vite + React + Tailwind v4 PWA — Proven Pitfalls & Fixes

Skill ini merekam bug REAL yang ketemu saat build POS PWA (Omni POS), semuanya "silent" — build sukses, tapi app salah. Tiap bug ada gejala, root cause, diagnosis, fix.

## Trigger: load skill ini kalau
- App Vite+React tampil **putih polos / tanpa style** padahal build sukses
- Deploy lewat `http://IP:port` (bukan HTTPS/localhost) dan ada error `crypto.randomUUID is not a function`
- Pakai Firebase config dummy/placeholder dan operasi write/read **hang** atau `permission-denied`
- Layout dialog/keranjang di mobile numpuk / harus scroll cari tombol
- Elemen `fixed`/floating (FAB, sticky bar) malah ikut scroll, tidak nempel viewport
- Klik dialog "nggak respon" / tampilan tumpuk saat overlay dibuka dari dalam overlay lain
- Tombol yang pakai `prompt()`/`confirm()`/`alert()` error di HP
- Tailwind v4 dengan semantic color tokens (`bg-card`, `text-primary`) yang tidak ke-generate

---

## BUG 1 — Tailwind v4: plugin hilang → SEMUA utility no-op
**Gejala:** build sukses, HTML ter-render, tapi UI telanjang (elemen ada, tanpa layout/warna).
**Root cause:** Tailwind v4 TIDAK pakai `tailwind.config.js` + PostCSS by default. Butuh plugin `@tailwindcss/vite` di `vite.config.ts`. Kalau lupa, `@import "tailwindcss"` cuma emit CSS variabel, tanpa utility class.
**Diagnosis (30 detik):** grep CSS hasil build untuk `.flex{` — kalau kosong, plugin hilang.
```bash
grep -oE '\.(flex|grid|min-h-screen)\{' dist/assets/*.css | head
```
**Fix:**
```bash
npm install -D @tailwindcss/vite
```
```ts
// vite.config.ts
import tailwindcss from '@tailwindcss/vite'
export default defineConfig({ plugins: [react(), tailwindcss()] })
```

## BUG 2 — Tailwind v4: semantic tokens render "putih polos" MESKI plugin sudah jalan
**Gejala (lapisan kedua, lebih licik):** utility umum (`flex`, `grid`) jalan, TAPI komponen pakai `bg-card`, `text-primary`, `border-border` → tetap transparan/putih.
**Root cause:** di v4, token warna WAJIB didaftarkan di blok `@theme {}`, bukan cuma di `:root` sebagai CSS var biasa. Kalau cuma di `:root`, utility-nya tidak digenerate.
**Diagnosis:** grep `.bg-card{` di CSS build → kosong.
**Fix (index.css):**
```css
@import "tailwindcss";
@theme {
  --color-background: #0f111a;
  --color-card: #1a1d2d;
  --color-primary: #6d28d9;
  --color-border: #ffffff14;
  /* ...semua semantic token */
}
```

## BUG 3 — `crypto.randomUUID is not a function` di HTTP non-localhost
**Gejala:** simpan produk/transaksi/apapun yang generate ID → crash senyap (form gagal submit tanpa error jelas).
**Root cause:** `crypto.randomUUID()` HANYA ada di **secure context** (HTTPS atau localhost). Diakses lewat `http://IP:port` → `undefined`.
**Fix:** helper `uuid()` dengan fallback berjenjang, ganti SEMUA `crypto.randomUUID()`.
```ts
// lib/utils.ts
export function uuid(): string {
  if (typeof crypto !== 'undefined' && typeof crypto.randomUUID === 'function') return crypto.randomUUID()
  if (typeof crypto !== 'undefined' && crypto.getRandomValues) {
    const b = crypto.getRandomValues(new Uint8Array(16))
    b[6] = (b[6] & 0x0f) | 0x40; b[8] = (b[8] & 0x3f) | 0x80
    const h = Array.from(b, x => x.toString(16).padStart(2, '0'))
    return `${h[0]}${h[1]}${h[2]}${h[3]}-${h[4]}${h[5]}-${h[6]}${h[7]}-${h[8]}${h[9]}-${h[10]}${h[11]}${h[12]}${h[13]}${h[14]}${h[15]}`
  }
  return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, c => {
    const r = Math.random()*16|0; return (c==='x'?r:(r&0x3|0x8)).toString(16)
  })
}
```
Cari semua pemakaian: `search_files pattern="crypto\.randomUUID"`. HATI-HATI saat auto-insert import — jangan sisipkan `import` di TENGAH multiline `import type { ... }` block (bikin syntax error); sisipkan setelah baris import terakhir yang komplet.

## BUG 4 — Firebase dummy config bikin operasi hang / permission-denied (demo mode)
**Gejala:** app pakai config Firebase placeholder biar bisa demo tanpa credentials, tapi transaksi/data tidak tersimpan, atau console penuh `permission-denied`, atau operasi menggantung.
**Root cause:** service layer nyoba Firestore DULU (`try { firestore } catch { indexeddb }`). Dengan config dummy, Firestore tidak langsung throw — malah retry/hang atau balikin permission-denied, jadi fallback IndexedDB tidak jalan bersih.
**Fix:** deteksi demo mode eksplisit + dual-path. JANGAN andalkan try/catch.
```ts
// lib/firebase.ts
export const isDemoMode =
  !import.meta.env.VITE_FIREBASE_API_KEY ||
  import.meta.env.VITE_FIREBASE_API_KEY === 'dummy_api_key'
```
```ts
// tiap service (products/customers/transactions/inventory/shift):
export async function create(data) {
  const id = uuid()
  if (isDemoMode) { await localDb.table.put(rec); return rec }  // IndexedDB langsung
  try { await setDoc(...) } catch {}
  await localDb.table.put(rec)
  return rec
}
```
Untuk counter (invoice number) yang biasanya pakai Firestore `runTransaction`, di demo mode hitung dari IndexedDB (`localDb.transactions.filter(...).count()`). Ledger/movement yang butuh koleksi terpisah bisa disimpan di `localStorage` JSON array saat demo.

**Nuance penting (bikin bug ini muncul 2x): READ/LIST juga wajib branch `isDemoMode`, bukan cuma WRITE.** Firestore query dengan config dummy sering balikin **array kosong** (bukan throw), jadi pola `try { getDocs } catch { indexeddb }` TIDAK jatuh ke fallback — list senyap kosong padahal data ada di IndexedDB. Gejala nyata: transaksi/hold tersimpan (notif "berhasil"), tapi daftarnya kosong. Fix: `if (isDemoMode) return localDb...` di AWAL fungsi list/get, sebelum sentuh Firestore. Audit SEMUA fungsi (list, get, count, delete), jangan cuma create/update.

**Nuance lapis 3 (bikin transaksi MACET/HANG, bukan cuma kosong): create/update/delete yang TIDAK branch demo-mode bikin app FREEZE saat dipanggil di alur kritis.** Ketemu nyata: `customers.ts` create/update/delete DULU nyoba `setDoc/updateDoc(firestore, ...)` DULU baru `catch → localDb`. Dengan config dummy, Firestore SDK tidak langsung throw — dia RETRY BACKOFF (hang beberapa detik / selamanya) sebelum fallback jalan. Efek: transaksi TANPA pelanggan lancar (tak sentuh customers), tapi transaksi DENGAN pelanggan MACET karena checkout memanggil `updateCustomer()` (update totalSpent/transactionCount) → Firestore hang → seluruh alur bayar freeze. Fix: guard `if (isDemoMode) { await localDb...; return }` di AWAL SEMUA fungsi write (create/update/delete), sama seperti list/get. Aturan mutlak: di service demo-mode, TIDAK ADA satupun fungsi (read maupun write) yang boleh menyentuh Firestore saat `isDemoMode` — audit file per file, satu fungsi kelewat = satu titik hang.

**Nuance ke-3 (muncul lagi di sesi lain — bikin "app MACET/freeze saat aksi tertentu"): file service yang KELEWAT belum di-guard `isDemoMode` bikin hang parah, bukan cuma senyap.** Gejala: sebagian alur lancar (nggak sentuh service itu), sebagian MACET total. Contoh nyata: checkout TANPA pelanggan lancar, tapi checkout DENGAN pelanggan freeze — karena `handlePaymentConfirm` manggil `updateCustomer()` (update total belanja) yang di `customers.ts` masih nyoba Firestore `updateDoc` dulu → retry/backoff hang. `createCustomer`/`updateCustomer`/`deleteCustomer` sering lupa di-guard karena perhatian ketuju ke transaksi/produk. **Aturan: SETIAP file service (products, categories, customers, transactions, inventory, shift, settings) harus punya guard `if (isDemoMode)` di SETIAP fungsi write & read.** Grep audit: `search_files pattern="setDoc|updateDoc|deleteDoc|getDocs|runTransaction"` lalu pastikan tiap fungsi yang muncul punya cabang `isDemoMode` SEBELUM baris Firestore itu. Diagnosis "macet cuma di alur X": telusuri service apa yang CUMA kepanggil di alur X (di sini: `updateCustomer`) — itu tersangka utama.

## BUG 5 — Layout mobile: dialog & panel numpuk, harus scroll cari tombol
**Gejala:** di HP, dialog muncul di tengah dengan konten kepanjangan → scroll naik-turun cari tombol aksi. Panel keranjang POS ketimpa di bawah produk.
**Fix A — Dialog jadi bottom-sheet di mobile, centered di desktop:**
```tsx
<div className="fixed inset-0 z-50 flex items-end justify-center sm:items-center sm:p-4">
  <div className="w-full glass flex flex-col max-h-[92vh] sm:max-h-[90vh] overflow-hidden
                  rounded-t-3xl sm:rounded-2xl max-w-lg
                  animate-in slide-in-from-bottom-4 sm:zoom-in-95">
    {/* header shrink-0 | content overflow-y-auto | footer shrink-0 */}
  </div>
</div>
```
Header & footer `shrink-0`, content `overflow-y-auto` → tombol aksi selalu keliatan tanpa scroll seluruh dialog.
**Close affordance WAJIB eksplisit (user komplain 2x "tidak bisa di-close"):** tiap dialog HARUS punya tombol **X di header** + tombol **"Tutup" full-width di footer**. Tap-backdrop saja TIDAK cukup — di mobile tidak discoverable, user kira dialog nyangkut. Pola konsisten: `DialogHeader` berisi `<flex justify-between>{title}{X-button}</flex>`, `DialogFooter` berisi `<Button variant="outline" className="w-full">Tutup</Button>`. Terapkan ke SEMUA dialog (detail transaksi, held, opname, dll), jangan cuma sebagian — user akan nemu yang kelewat.\n**Fix B — Panel keranjang: floating button + bottom-sheet (bukan stack di bawah):**
- Desktop: kolom kanan (`hidden lg:block`).
- Mobile: floating FAB (`lg:hidden fixed bottom-20 right-4`) dengan badge jumlah + total → tap buka bottom-sheet berisi `<CartPanel embedded />`.
- Prop `embedded` di panel buat sembunyikan header ganda.

## BUG 6 — `position: fixed` malah ikut scroll (bukan nempel viewport)
**Gejala:** elemen `fixed` (floating cart bar, FAB, sticky checkout) yang harusnya nempel ke layar malah ikut ter-scroll bareng konten — user harus scroll mentok bawah baru ketemu.
**Root cause:** ada ANCESTOR dengan `transform`, `filter`, `backdrop-filter`, `perspective`, `will-change`, atau `contain` → bikin *containing block* baru, jadi `fixed` jadi relatif ke ancestor itu, BUKAN viewport. Umum kejadian: elemen di dalam wrapper animasi (`.animate-slide-up`, `translateY`), atau di dalam `.glass` card yang pakai `backdrop-filter`, atau di `overflow-y:auto` container.
**Diagnosis:** telusuri parent chain elemen `fixed`; cari `transform`/`backdrop-filter`/`filter` yang bukan `none`.
**Fix:** render lewat React Portal ke `document.body` (di luar semua containing block bermasalah):
```tsx
import { createPortal } from 'react-dom'
{show && createPortal(
  <div className="lg:hidden fixed left-0 right-0 bottom-[68px] z-[60]">...</div>,
  document.body
)}
```
Bottom-sheet/overlay juga sebaiknya di-portal ke body agar `fixed inset-0` benar-benar full-viewport. Naikkan z-index (mis. `z-[60]` bar, `z-[70]` sheet) supaya di atas bottom-nav.

## BUG 7 — Nested overlays: dialog dibuka dari dalam bottom-sheet → klik mati / "tumpuk-tumpuk"
**Gejala:** buka dialog (mis. Pembayaran) dari dalam bottom-sheet lain (mis. keranjang) → dua layer `fixed` numpuk, backdrop dobel, klik ke-blok / "nggak respon", tampilan bertumpuk-blur ganda.
**Root cause:** dua overlay `fixed` aktif bersamaan; backdrop dobel intercept pointer-events + z-index perang.
**Fix:** (a) tutup sheet DULU sebelum buka dialog berikutnya — `onCheckout={() => { setCartOpen(false); setPaymentOpen(true) }}`; (b) render Dialog lewat Portal ke `document.body` dengan z-index lebih tinggi dari sheet (sheet `z-[70]`, dialog `z-[80]`). Prinsip: satu layer interaktif pada satu waktu.

## BUG 8 — `window.prompt()` / `confirm()` / `alert()` diblok di webview / in-app browser HP
**Gejala:** tombol yang manggil `prompt()` (mis. "Hold" minta catatan) keliatan error / hang di HP.
**Root cause:** banyak in-app browser & webview Android mem-block atau suppress dialog JS native → return `null` senyap atau lempar.
**Fix:** JANGAN pakai `prompt`/`confirm`/`alert` untuk UX inti. Ganti dialog in-app sendiri, atau buang input opsionalnya (mis. Hold langsung jalan tanpa minta catatan). Sejalan dengan pitfall cetak struk yang tidak boleh `window.open()`.

## BUG 9 — Mobile drawer sidebar slide dari sisi yang salah
**Gejala:** tombol hamburger ada di KIRI, tapi drawer sidebar malah masuk dari KANAN (lari ke kanan) — terasa tidak natural / non-native.
**Root cause:** CSS drawer di-set `right: -300px` + `.drawer-open { right: 0 }` padahal trigger di kiri. Arah slide harus match posisi tombol.
**Fix (index.css @media mobile):** pakai `left: -300px` + `transition: left` + `.drawer-open { left: 0 }`, dan balik juga `box-shadow` (`4px 0 ...`) + `border-right`. Aturan umum: drawer masuk dari sisi yang sama dengan tombol pemicunya.

## BUG 10 — Tabel `overflow-x-auto` bikin harus geser samping di HP (bukan native)
**Gejala:** halaman list (Transaksi, Pelanggan, Produk, Inventori) pakai `<table>` + wrapper `overflow-x-auto` → di HP kolom kepotong, user harus scroll horizontal buat lihat data lengkap. Terasa seperti web di-shrink, bukan app native.
**Root cause:** tabel multi-kolom tidak muat di lebar HP; `overflow-x-auto` cuma "menyembunyikan" masalah jadi scroll samping.
**Fix — dual render responsive (BUKAN scroll horizontal):**
```tsx
{/* Desktop: tabel penuh */}
<div className="overflow-x-auto hidden md:block"><table>...</table></div>
{/* Mobile: card list vertikal */}
<div className="md:hidden divide-y divide-[var(--glass-border)]">
  {items.map(x => (
    <div className="p-4 ...">{/* semua field ke bawah + tombol aksi */}</div>
  ))}
</div>
```
Tiap card muat semua info (yang di desktop jadi kolom) tersusun vertikal + tombol aksi full-width/inline. Nol scroll horizontal. Ini pola "responsive-table → cards" yang benar untuk POS/dashboard mobile-first; lebih eksplisit & kontrol penuh dibanding trik CSS `display:block td:before{content:attr(data-label)}`.

## BUG 11 — Laporan POS cuma hitung penjualan, lupa kas masuk non-penjualan
**Gejala:** user tanya "laporan uang masuk deposit & pembayaran hutang di mana?" — halaman Laporan cuma punya omzet/profit/transaksi dari penjualan langsung, padahal ada dua sumber kas masuk lain yang tidak tercatat: **topup deposit** pelanggan dan **pelunasan kasbon**.
**Root cause:** report engine cuma agregasi dari koleksi `transactions`. Deposit topup & kasbon paid tercatat di **ledger terpisah** (per-pelanggan), tidak pernah di-roll-up ke laporan global.
**Fix:** tambah query lintas-pelanggan `getLedgerInRange(startTs, endTs)` yang narik SEMUA entri ledger (bukan per-customer), filter by rentang waktu + dual-path demo-mode (localStorage) vs Firestore. Lalu di ReportsPage jumlahkan `deposit_topup` & `kasbon_paid` jadi kartu "Kas Masuk" + riwayatnya.
**Pelajaran domain (POS/retail):** kas toko = penjualan + topup deposit + pelunasan kasbon (− penarikan deposit). Saat bikin laporan keuangan POS, JANGAN cuma agregasi transaksi penjualan — audit semua sumber uang masuk/keluar (deposit, kasbon, refund, pengeluaran/kas keluar). Fitur ini sering kelewat sampai user menagih.

## BUG 12 — TanStack Query cache basi setelah write → "transaksi nggak masuk laporan / stok nggak berkurang" (padahal DATA TERSIMPAN)
**Gejala:** setelah checkout, notif "berhasil" muncul, TAPI: (a) stok produk di grid POS keliatan nggak berkurang; (b) transaksi baru nggak muncul di halaman Transaksi; (c) omzet di Laporan nggak naik. Kalau di-refresh manual (F5), semua data BENAR muncul.
**Root cause:** BUKAN bug data — write ke IndexedDB sukses. Masalahnya `useQuery` masih nyajiin **cache lama** (`staleTime` 30-60 detik di `useProducts`/`useCategories`). Read fungsi nggak otomatis tau ada write di store lain. Ini gampang ketuker sama "data nggak tersimpan" → salah diagnosis.
**Fix:** setelah SETIAP operasi write yang efeknya lintas-view (checkout, adjust stok, topup deposit, dll), `invalidateQueries` semua queryKey yang kena:
```ts
// handlePaymentConfirm setelah checkout sukses:
queryClient.invalidateQueries({ queryKey: ['products'] })       // stok berkurang
queryClient.invalidateQueries({ queryKey: ['transactions-list'] }) // muncul di riwayat
queryClient.invalidateQueries({ queryKey: ['customers'] })      // total belanja update
queryClient.invalidateQueries({ queryKey: ['report'] })         // omzet naik
queryClient.invalidateQueries({ queryKey: ['dashboard'] })
```
**Pelajaran:** offline-first + cache = dua sumber "kebenaran" (IndexedDB vs React Query cache). Write cuma nyentuh IndexedDB; cache HARUS di-invalidate manual. Kalau user bilang "tersimpan tapi nggak muncul di view lain" → curigai cache basi DULUAN, bukan write gagal. Diagnosis cepat: minta user F5 — kalau habis refresh datanya muncul, itu cache invalidation yang kurang.

## BUG 13 — Seed data ber-timestamp masa depan → record baru "keselip" di tengah list, dikira nggak masuk
**Gejala (setelah BUG 12 sudah difix):** transaksi baru BENAR muncul di halaman Transaksi (cache sudah di-invalidate), TAPI user bilang "nggak masuk" karena posisinya nyelip di tengah daftar, bukan paling atas.
**Root cause:** seed/demo data bikin transaksi hari ini dengan **jam ACAK 08:00–20:00**. Kalau user transaksi jam 10 pagi, record dummy yang jam 14/17/20 (timestamp DI MASA DEPAN relatif `Date.now()`) sorting di ATAS record baru. Daftar sorted `createdAt desc` → record user ketimbun. Kesannya "nggak masuk", padahal cuma bukan di atas.
**Fix:** clamp timestamp seed untuk HARI INI biar nggak pernah > `Date.now()`:
```ts
let ts = dayBase.getTime() + rng(8,20)*3_600_000 + rng(0,59)*60_000
if (dayOffset === 0 && ts > Date.now()) ts = Date.now() - rng(1,120)*60_000
```
Data seed lama yang terlanjur ber-timestamp masa depan → re-seed (`?seed=1`) buat bersihin.
**Pelajaran:** dua trap "record baru nggak keliatan" berurutan & gampang ketuker: (1) BUG 12 cache basi (F5 → muncul), (2) BUG 13 ini timestamp seed di masa depan (record ADA di list, cuma keselip). Kalau user bilang "nggak masuk" tapi habis dicek record-nya SEBENARNYA ada di tengah daftar → ini BUG 13, bukan cache. Selalu pastikan dummy/seed data pakai timestamp masa lalu, jangan `rng` jam yang bisa lompat ke depan.

## BUG 14 — PWA "tidak bisa diinstal di HP" karena folder icons KOSONG (manifest nunjuk PNG 404)
**Gejala:** app punya `manifest.webmanifest` + service worker + registrasi SW lengkap, TAPI prompt "Add to Home Screen" tidak muncul di Chrome Android / install ditolak, atau ikon blank saat dipaksa install. User tanya "kok belum full PWA / belum ramah diinstal?".
**Root cause:** manifest mendaftarkan `/icons/icon-72x72.png` … `512x512.png`, tapi folder `public/icons/` KOSONG (cuma ada `favicon.svg`). Browser butuh PNG raster ukuran spesifik untuk installability — SVG favicon TIDAK cukup. Manifest yang nunjuk file 404 = kriteria installable gagal SENYAP (build tetap sukses).
**Diagnosis cepat:** `search_files pattern="icon-*.png" path=public/icons` → kosong. Atau serve + `curl -s -o /dev/null -w "%{http_code}" http://host/icons/icon-512x512.png` → 404.
**Fix — generate semua PNG dari 1 SVG master pakai cairosvg (Python, TANPA tool desain):**
```bash
pip install cairosvg
```
```python
import cairosvg
# icon-master.svg: full-bleed brand bg (gradient) + logo di zona tengah ~60%
for s in [72,96,128,144,152,192,384,512]:
    cairosvg.svg2png(url='public/icon-master.svg', write_to=f'public/icons/icon-{s}x{s}.png', output_width=s, output_height=s)
# MASKABLE (192,512): SVG TERPISAH, padding lebih besar (logo ~50%) — Android crop jadi
# lingkaran/rounded, full-bleed bakal kepotong. JANGAN gabung "any maskable" di 1 file.
cairosvg.svg2png(url='public/icon-maskable.svg', write_to='public/icons/maskable-512x512.png', output_width=512, output_height=512)
cairosvg.svg2png(url='public/icon-maskable.svg', write_to='public/icons/maskable-192x192.png', output_width=192, output_height=192)
# apple-touch-icon 180 dari master
cairosvg.svg2png(url='public/icon-master.svg', write_to='public/apple-touch-icon.png', output_width=180, output_height=180)
```
**Manifest wajib:** daftarkan 8 icon `purpose:"any"` + 2 icon `purpose:"maskable"` (dari SVG maskable terpisah). `theme_color`/`background_color` match brand, `scope:"/"`, `display:"standalone"`.
**index.html iOS meta** (biar installable + fullscreen di Safari): `<link rel="apple-touch-icon" href="/apple-touch-icon.png">`, `<meta name="mobile-web-app-capable" content="yes">`, `<meta name="apple-mobile-web-app-capable" content="yes">`, `apple-mobile-web-app-status-bar-style`, `apple-mobile-web-app-title`. Pastikan `<link rel="icon">` nunjuk file yang ADA (bukan `/vite.svg` yang sering kehapus → 404).
**SW precache:** tambah icon utama + offline.html ke PRECACHE, tapi pakai `Promise.allSettled(urls.map(u=>cache.add(u)))` BUKAN `cache.addAll()` — addAll gagal TOTAL kalau 1 file 404, allSettled toleran. Bump `CACHE_NAME` (v1→v2) tiap ubah daftar precache biar SW re-install.
**Verifikasi PNG bener tanpa vision tool** (vision_analyze/browser_vision bisa mati kalau provider belum di-setup) — cek pixel via PIL: corner harus warna brand, center harus putih/logo:
```python
from PIL import Image; im=Image.open('public/icons/icon-512x512.png').convert('RGBA'); px=im.load()
print('corner', px[5,5][:3], 'center', px[256,256][:3])  # corner=ungu, center=(255,255,255)
```
Lalu `curl` tiap asset → 200, dan `curl manifest → cek jumlah icons`.
**SYARAT TERAKHIR (sering bikin bingung, JELASKAN ke user): install PWA DIBLOK di HTTP.** Di `http://IP:port` browser TETAP tolak install walau manifest+icon+SW sempurna — itu batasan browser (butuh secure context), BUKAN bug app. Baru jalan penuh setelah deploy ke HTTPS (Firebase Hosting `*.web.app` otomatis HTTPS, sekalian ngilangin BUG 3 `crypto.randomUUID`). Jangan buang waktu debug installability di HTTP preview; cukup verifikasi asset (curl 200) + build, tes install nanti di HTTPS.

## BUG 16 — Dialog component API: no `title` prop, use children pattern
**Gejala:** Build error `Property 'title' does not exist on type 'IntrinsicAttributes & DialogProps'` saat pakai `<Dialog title="...">`.
**Root cause:** Dialog component di Omni POS pakai pattern `{children}` saja, bukan `<DialogTitle>` wrapper atau `title` prop.
**Fix:** Pakai children dengan heading di dalam:
```tsx
// SALAH
<Dialog open={open} onClose={onClose} title="Judul Dialog">
  <div>content</div>
</Dialog>

// BENAR
<Dialog open={open} onClose={onClose}>
  <div className="p-6">
    <h2 className="text-xl font-bold mb-4">Judul Dialog</h2>
    <div>content</div>
  </div>
</Dialog>
```

## BUG 17 — Card component tidak support onClick prop
**Gejala:** Build error `Property 'onClick' does not exist on type 'IntrinsicAttributes & CardProps'` saat bikin clickable card.
**Root cause:** Card component murni presentational, tidak forward event handlers.
**Fix:** Wrap Card dengan div yang punya onClick:
```tsx
// SALAH
<Card onClick={() => handleClick(item)} className="cursor-pointer">
  <CardContent>...</CardContent>
</Card>

// BENAR
<div onClick={() => handleClick(item)} className="cursor-pointer">
  <Card>
    <CardContent>...</CardContent>
  </Card>
</div>
```

## BUG 18 — TypeScript strict null check: deletedAt null vs undefined
**Gejala:** Build error `Type 'null' is not assignable to type 'number | undefined'` saat create record baru.
**Root cause:** Type definition pakai `deletedAt?: number` (optional number), tapi code set `deletedAt: null`.
**Fix:** Omit deletedAt saat create, atau gunakan explicit undefined:
```ts
// SALAH
const data = { ...fields, deletedAt: null }
return { id, ...data } as Account  // Error!

// BENAR
const data = { ...fields }  // deletedAt not set
return { id, ...data } as Account
```

## BUG 19 — Firestore setDoc tidak return DocumentReference
**Gejala:** Build error `Type 'void' is not assignable to type 'DocumentReference'`.
**Root cause:** `setDoc()` return `Promise<void>`, bukan DocumentReference seperti `addDoc()`.
**Fix:** Jangan assign return value setDoc:
```ts
// SALAH
const docRef = await setDoc(doc(firestore, 'accounts', id), data)

// BENAR
await setDoc(doc(firestore, 'accounts', id), data)
```

## BUG 20 — useMutation type inference gagal dengan complex function signature
**Gejala:** Build error `Argument of type 'Account' is not assignable to parameter of type 'void'`.
**Root cause:** React Query gagal infer type saat mutationFn punya multiple parameters.
**Fix:** Wrap dengan explicit arrow function:
```ts
// KURANG
const mutation = useMutation({
  mutationFn: updateAccount,  // (code: string, updates: Partial<Account>) => Promise<void>
})

// LEBIH BAIK
const mutation = useMutation({
  mutationFn: (data: Account) => updateAccount(data.code, data)
})
```

## BUG 21 — Property name inconsistency (parentId vs parentCode)
**Gejala:** Build error `Property 'parentCode' does not exist on type 'Account'`.
**Root cause:** Type definition pakai `parentId`, tapi UI code salah tulis `parentCode`.
**Fix:** Selalu cek type definition dulu, konsisten pakai satu nama.

## BUG 22 — JournalEntry pakai `number` bukan `journalNumber`
**Gejala:** Build error `Property 'journalNumber' does not exist on type 'JournalEntry'`.
**Fix:** Konsisten pakai `journal.number` bukan `journal.journalNumber`.

## BUG 23 — Unused imports cause strict mode build failure
**Gejala:** Build error `TS6133: 'X' is declared but its value is never read`.
**Fix:** Hapus atau prefix dengan underscore:
```ts
import { Button, Card } from '@/components/ui'  // hapus yang tidak dipakai
function handler(_event: Event, data: Data) {}  // prefix unused params
```

## BUG 24 — JSX structure must be balanced (opening/closing tags)
**Gejala:** Build error `Expected corresponding JSX closing tag for 'div'`.
**Fix:** Cek indentation dan pastikan setiap opening tag punya closing tag.

## BUG 25 — InventoryMovement function signature mismatch
**Gejala:** Build error `Module '"./inventory"' has no exported member 'addInventoryMovement'`.
**Fix:** Pakai `adjustStock` (actual function di inventory.ts):
```ts
import { adjustStock } from './inventory'
await adjustStock(productId, qty, notes, movementType, referenceType, referenceId)
```

## Domain: dokumen POS berlapis — nota vs surat jalan (multi print target)
POS toko/grosir sering butuh >1 jenis dokumen cetak dari SATU transaksi:
- **Nota/struk** — thermal 58/80mm, ADA harga, buat pelanggan bayar.
- **Surat jalan (delivery note)** — dokumen A4 lebar penuh, TANPA harga (cuma nama barang + qty + satuan), buat pengiriman/ekspedisi. Ada field penerima/alamat/ekspedisi/no.kendaraan + 3 kolom tanda tangan (penerima/pengirim/hormat kami). Nomor turunan invoice (`INV-…` → `SJ-…`).

**⚠️ PENDEKATAN DEFINITIF (pakai INI dari awal): cetak lewat HIDDEN IFRAME, BUKAN `@media print` pada DOM app.** Pendekatan `@media print` + `visibility:hidden` (terdokumentasi di bawah sebagai referensi sejarah) terbukti punya 3 kegagalan fatal yang bikin user komplain BERTURUT-TURUT lintas turn: (a) **muncul 10+ halaman kosong** — elemen yang di-`visibility:hidden` TETAP makan ruang layout, jadi seluruh app (sidebar, tabel 50+ baris) ikut ke-paginate; (b) **nggak bisa atur ukuran kertas per-dokumen** (nota kecil 58/80mm vs surat jalan A4) karena `@page` global; (c) di HP kadang buka tab baru / diblok popup. **Solusi yang menang: render dokumen ke `<iframe>` tersembunyi lalu `iframe.contentWindow.print()`.** Iframe isinya CUMA dokumen itu (HTML mandiri lengkap `<!DOCTYPE>` + `@page` sendiri) → nol halaman kosong, ukuran kertas per-dokumen, nggak buka tab, aman di HP (berasa native).
```ts
// lib/print.ts — helper reusable buat SEMUA cetak (nota, surat jalan, invoice, dll)
export function printHtml(html: string): void {
  const iframe = document.createElement('iframe')
  Object.assign(iframe.style, { position:'fixed', right:'0', bottom:'0', width:'0', height:'0', border:'0', visibility:'hidden' })
  document.body.appendChild(iframe)
  const cleanup = () => setTimeout(() => iframe.parentNode?.removeChild(iframe), 1000)
  const doc = iframe.contentWindow?.document
  if (!doc) return cleanup()
  doc.open(); doc.write(html); doc.close()
  let done = false
  const go = () => { if(done) return; done=true; try { iframe.contentWindow?.focus(); iframe.contentWindow?.print() } finally { cleanup() } }
  iframe.onload = () => setTimeout(go, 150)   // tunggu font/gambar render
  setTimeout(go, 500)                          // fallback kalau onload sudah lewat sebelum handler kepasang
}
```
```ts
// Builder balikin STRING dokumen lengkap dengan @page-nya sendiri:
// Nota thermal:   @page { size: 58mm auto; margin: 0; }   // ikut store.printerWidth (58/80)
// Surat jalan A4: @page { size: A4; margin: 12mm; }
// Handler: printHtml(buildReceiptHtml(tx, store, width))  /  printHtml(buildDeliveryNoteHtml(tx, store, data))
```
Ukuran nota ikut setting: `const width = store.printerWidth === 80 ? 80 : 58`. Blok `@media print` di `index.css` app DIKOSONGKAN (`@media print { body { visibility: visible; } }`) karena cetak nggak lewat DOM app lagi. Dialog preview in-app BOLEH tetap ada (buat lihat/edit field penerima-alamat sebelum cetak) — yang penting OUTPUT cetak lewat iframe. **WAJIB escape HTML** untuk field user-input (nama barang, alamat, dll) di builder: `s.replace(/[<>&]/g, c => ({'<':'&lt;','>':'&gt;','&':'&amp;'}[c]||c))` biar markup nggak rusak. Ini juga menggantikan larangan `window.open()` lama (popup diblok di HP) — iframe adalah pengganti yang benar.

---
**(REFERENSI SEJARAH — JANGAN dipakai lagi, terbukti gagal) Pola cetak multi-dokumen `@media print` scoped by body class:** tiap jenis dokumen punya class area cetak sendiri (`.receipt-print`, `.delivery-print`) DAN blok `@media print` yang di-scope ke class di `<body>`:
```css
@media print { /* struk: default */
  body * { visibility: hidden; }
  .receipt-print, .receipt-print * { visibility: visible; }
  .receipt-print { position:absolute; top:0; left:0; max-width:80mm; }
}
@media print { /* surat jalan: hanya saat body.printing-delivery */
  body.printing-delivery * { visibility: hidden; }
  body.printing-delivery .delivery-print,
  body.printing-delivery .delivery-print * { visibility: visible; }
  body.printing-delivery .delivery-print { position:absolute; top:0; left:0; max-width:100%; }
}
```
Handler: `document.body.classList.add('printing-delivery'); window.print(); setTimeout(()=>remove, 500)`. Tanpa scope body-class, dua blok print saling timpa dan salah dokumen ikut kecetak. Form edit (penerima/alamat) kasih `print:hidden` biar nggak ikut tercetak, cuma area preview `.delivery-print` yang keluar.

**PITFALL KRITIS (silent, ketemu di print preview): print cuma keluar HEADER, sisa dokumen (tabel barang, tanda tangan) kepotong/hilang.** Root cause: area cetak (`.receipt-print`/`.delivery-print`) berada di dalam **Dialog yang dirender via Portal** dengan ancestor `overflow:hidden` + `max-height: 90vh` (bottom-sheet/centered dialog dari BUG 5). Saat `window.print()`, ancestor itu tetap MOTONG konten yang lebih tinggi dari layar — jadi di kertas cuma kebagian bagian atas. Gejala: preview cetak nunjukin judul + no + tanggal doang, item ke bawah lenyap. Fix — unclip semua ancestor saat mode cetak:
```css
@media print {
  body.printing-receipt *,
  body.printing-delivery * {
    overflow: visible !important;
    max-height: none !important;
  }
}
```
Ini melengkapi trik `visibility` (yang cuma nyembunyiin elemen lain, TAPI tidak melepas clip/overflow ancestor). Selalu pasang bareng tiap kali area cetak ada di dalam dialog/portal ber-`overflow-hidden`. Verifikasi: bukan cukup lihat dialog on-screen keliatan penuh — cek DevTools print-emulation atau print-to-PDF beneran, karena clipping cuma kejadian di media print.

**PITFALL KRITIS LAPIS 2 (ketemu setelah unclip overflow masih kepotong): `position:fixed`/`absolute` ancestor bikin dokumen panjang cuma kecetak 1 halaman (header doang).** Unclip `overflow`+`max-height` SAJA TIDAK CUKUP kalau wrapper dialog pakai `position: fixed` (Dialog kita: `fixed inset-0`). Saat cetak, elemen `fixed`/`absolute` di-anchor ke halaman pertama & TIDAK ngalir ke halaman berikutnya — konten yang lebih tinggi dari 1 halaman kepotong (di preview keliatan cuma header + no + tanggal, tabel barang & tanda tangan hilang). Root cause beda dari clip overflow: ini soal flow/pagination, bukan clip. Fix — paksa SEMUA ancestor fixed/absolute jadi `static` saat mode cetak, dan set area cetak sendiri `position: static` (BUKAN `absolute`):
```css
@media print {
  html, body { height: auto !important; overflow: visible !important; }
  body.printing-receipt .fixed, body.printing-receipt .absolute,
  body.printing-delivery .fixed, body.printing-delivery .absolute {
    position: static !important;
    inset: auto !important; top: auto !important; left: auto !important;
    right: auto !important; bottom: auto !important; transform: none !important;
  }
  body.printing-delivery .delivery-print { position: static !important; /* JANGAN absolute */ }
}
```
Urutan diagnosis print-kepotong: (1) unclip `overflow`/`max-height` ancestor; (2) kalau MASIH cuma 1 halaman, curigai `position:fixed`/`absolute` ancestor → paksa `static` + `html,body{height:auto;overflow:visible}`. Dua-duanya wajib bareng untuk dialog/portal ber-`fixed` yang isinya bisa multi-halaman (surat jalan A4, nota panjang). Catatan alat: `vision_analyze`/`browser_vision` bisa mati kalau vision provider belum di-setup (`No LLM provider configured for task=vision`) — fallback: OCR screenshot via `pytesseract` (install `tesseract-ocr` + `pip pytesseract`), atau inspeksi DOM via `browser_console` (cek `scrollHeight` vs `clientHeight`, chain ancestor `position`/`overflow`/`maxHeight`).

## Domain: atribusi kasir + status cetak nota di riwayat transaksi
Dua fitur audit yang sering diminta setelah POS jalan:
- **Kasir per transaksi:** `Transaction` sudah simpan `cashierId`/`cashierName` (diisi dari `useAuth().user` saat checkout). Tampilkan kolom Kasir di tabel/card Transaksi, masukkan ke search, dan di Excel tambah kolom Kasir di sheet Riwayat + sheet baru **"Rekap per Kasir"** (agregasi count/item/omzet per `cashierName`).
- **Status cetak nota:** tambah field opsional `printed?/printCount?/printedAt?` di `Transaction`. Helper `markTransactionPrinted(id)` increment `printCount` + set `printed=true` (dual-path demo-mode: `localDb.transactions.update` + Firestore `updateDoc` kalau online). Panggil dari handler cetak (`ReceiptDialog` via prop `onPrinted` callback → `queryClient.invalidateQueries` biar badge refresh). Badge "Sudah cetak ×N" / "Belum cetak" di tiap baris + kolom "Status Nota" di Excel. Transaksi lama tampil "Belum cetak" (field baru) — normal, jelaskan ke user.

Pola reuse penting: `ReceiptDialog` yang sama dipakai di POS (cetak awal) DAN di halaman Transaksi (cetak ulang) — bikin prop opsional (`onPrinted?`) daripada duplikasi komponen. `getStoreConfig()` diambil sekali di page yang mau cetak.

## Verifikasi (WAJIB, jangan skip)
Deploy lewat HTTP IP → verifikasi via browser DI DALAM VPS (`vite preview --host 0.0.0.0`, lalu browser_navigate ke `http://127.0.0.1:PORT`). Tes alur nyata: login → tambah data → transaksi → cek tersimpan. Bug 3 & 4 CUMA muncul di runtime, bukan di build. Selalu:
```bash
npm run build   # cek zero TS errors
# lalu smoke test tiap route + 1 operasi write nyata
```

## Domain: POS pricing & quantity (multi-satuan, grosir, kiloan)
Pola fitur reusable untuk POS toko/grosir — input qty bebas, kilogram desimal,
tiered/grosir pricing (beli banyak → harga per-dus otomatis), override harga saat
checkout, dialog pilih satuan+qty. PENTING: pricing punya banyak varian, DISKUSIKAN
dulu dengan contoh angka sebelum implement (jangan asumsi cara hitung tiering).
Detail lengkap + kode di `references/pos-pricing-and-qty.md`.

## Domain: POS loyalty points (earn/burn/expiry)
Sistem poin pelanggan: earn saat belanja (dengan tier multiplier), burn untuk diskon
saat checkout, optional expiry. Arsitektur: LoyaltyConfig di StoreConfig, Customer.points
(balance), CustomerLedgerEntry (audit trail), Cart.pointsToBurn (UI state), calculateEarned/Burn
(pure functions), adjustPoints (atomic update). Urutan implementasi: types → default config
→ pure functions → adjustPoints → cart store → checkout → UI → build check.
Detail lengkap + pitfall + pola kode di `references/pos-loyalty-points.md`.

## Domain: POS akuntansi double-entry (PSAK)
Sistem akuntansi lengkap dengan Chart of Accounts, auto-journal dari transaksi, period closing (tutup buku bulanan), manual journal (jurnal penyesuaian), dan 4 laporan keuangan (Laba Rugi, Neraca, Arus Kas, Perubahan Modal). Detail di `references/pos-accounting-module.md`.

## Domain: Electron desktop conversion (PWA → .exe installer)
Convert Vite/React web app to Windows desktop installer using Electron. Preserves 95% code, adds system tray, hardware license binding, thermal printer native access, auto-updater. Full offline-first desktop app with NSIS installer.
Detail lengkap + Phase 1-8 timeline + pitfalls di `references/electron-desktop-conversion.md`.
Actual implementation code (Phase 1-3 completed) di `references/electron-implementation-patterns.md`.

## Domain: POS software licensing & pricing (Indonesian market)
Business model for selling POS software: perpetual vs subscription, hardware-bound licenses, tier pricing (Basic/Pro/Enterprise), Cloudflare Workers free license server, activation flow, grace periods, revenue projection. Covers why "data di komputer sendiri" still needs thin cloud for license validation.
Detail lengkap + pricing table + revenue streams di `references/pos-licensing-pricing.md`.

## Domain: Excel import & export (browser, no server)
Import produk massal dari Excel (+ template generator dengan satuan bertingkat) &
export laporan penjualan multi-sheet rapi. WAJIB pakai `exceljs`, JANGAN `xlsx`
(SheetJS sudah cabut dari npm). Preview validasi + pilihan Perbarui/Lewati untuk
SKU duplikat. Detail lengkap + pola kode di `references/excel-import-export.md`.

## Domain: Firestore free-tier (Spark) — sync incremental + agregat harian
POS/offline-first yang deploy ke Firestore GRATIS dengan data banyak butuh 3 pilar
biar tak jebol kuota: (1) sync incremental berbasis `updatedAt` (BUKAN full-fetch,
BUKAN `onSnapshot`) + soft delete + `lastSync` di localStorage; (2) agregat laporan
harian `reports_daily/{tanggal}` via `increment()` — laporan N hari = N read, BUKAN
scan ribuan transaksi; (3) batch write minimal (1 tx = 1 commit tx+stok+agregat,
jangan tulis inventory movement per-item). Plus pagination riwayat (limit+cursor),
dan `1 Firebase project per klien` → security rules single-tenant `if request.auth
!= null` (no storeId). Semua dual-path demo (localStorage) supaya kebangun & ketes
tanpa Firebase real; pas web config dateng tinggal colok ke `.env` + deploy. Detail
lengkap + estimasi kuota + model data + setup Vitest di
`references/firestore-freetier-optimization.md`.

## Domain: Dark glassmorphism theme conversion (Omni POS design system)

When converting pages from light theme to dark glassmorphism theme in Omni POS (or similar apps), follow this systematic class mapping strategy:

### Class mapping reference
**Typography & text colors:**
- `text-gray-900` → `text-[var(--foreground)]` (primary headings, main text)
- `text-gray-700`, `text-gray-600`, `text-gray-500`, `text-gray-400`, `text-gray-300` → `text-[var(--text-secondary)]` (labels, secondary text, muted content)
- `text-blue-600` → `text-[var(--primary)]` (links, active states, totals)
- `text-green-600` → `text-[var(--success)]` (positive values, balanced states)
- `text-red-600` → `text-[var(--danger)]` (negative values, errors, required markers)
- `text-yellow-600` → `text-[var(--warning)]` (alerts, caution states)

**Backgrounds:**
- `bg-gray-50`, `bg-white` → Remove (rely on `Card` component or use `bg-[var(--surface)]` for subtle elevation)
- `bg-blue-50` → `bg-[var(--primary)]/20` (active/selected states with opacity)
- `bg-green-50` → `bg-[var(--success)]/20`
- `bg-red-50` → `bg-[var(--danger)]/20`
- `bg-yellow-50` → `bg-[var(--surface)]` (info boxes, alerts)

**Borders:**
- `border-gray-200`, `border-gray-300`, `divide-gray-200` → `border-[var(--border)]` or `divide-[var(--border)]`
- `border-blue-600`, `border-blue-500` → `border-[var(--primary)]`
- `border-green-300`, `border-green-200` → `border-[var(--success)]`
- `border-red-200` → `border-[var(--danger)]`

**Interactive states:**
- `hover:bg-gray-50` → `hover:bg-[var(--surface-hover)]`
- `hover:border-gray-400` → `hover:border-[var(--surface-hover)]`

**Tables:**
- `<thead className="bg-gray-50">` → `<thead className="bg-[var(--surface)]">`
- `<tbody className="bg-white divide-y divide-gray-200">` → `<tbody className="divide-y divide-[var(--border)]">` (remove bg-white, rely on parent Card)
- Table headers: `text-xs font-medium text-gray-500 uppercase` → `text-xs font-medium text-[var(--text-secondary)] uppercase`

**Layout:**
- `container mx-auto px-4 py-8` → `space-y-6` (for main page wrappers, let Card components handle padding)

### Component behavior
- **Card component** already handles dark theme backgrounds and borders — avoid adding redundant `bg-*` classes to Cards
- **Button component** already supports dark theme — no changes needed
- **Input component** needs explicit dark theme classes when used as `<textarea>` or `<select>`: add `bg-[var(--background)] text-[var(--foreground)] border-[var(--border)]`

### Systematic conversion workflow
1. Read the entire file first to understand structure
2. Identify light theme classes using search: `text-gray-*`, `bg-gray-*`, `bg-white`, `border-gray-*`, `text-blue-*`
3. Apply class mappings systematically (don't mix old and new styles)
4. Update loading states: `border-b-2 border-blue-600` → `border-b-2 border-[var(--primary)]`
5. Update empty states: icons use `text-[var(--text-secondary)]` with `opacity-40`
6. Update alert/info boxes: `bg-blue-50 border-blue-200 text-blue-900` → `bg-[var(--surface)] border-[var(--primary)]` with text classes updated
7. Update badge colors: `bg-green-100 text-green-800` → `bg-[var(--success)]/20 text-[var(--success)]`
8. Test visually after each page to catch missed conversions

### Common pitfalls
- **Forgetting nested text colors:** `<p className="font-medium">` inside a dark container still needs `text-[var(--foreground)]` if parent doesn't set it
- **Select/textarea inputs:** These don't inherit from Input component — must add `bg-[var(--background)] text-[var(--foreground)]` explicitly
- **Loading spinners:** `border-blue-600` → `border-[var(--primary)]` (easy to miss)
- **Table footers:** `bg-gray-50 border-t-2` → `bg-[var(--surface)] border-t-2 border-[var(--border)]`
- **Conditional classes:** Update BOTH branches in ternaries (e.g., `isClosed ? 'border-green-300 bg-green-50' : 'border-gray-200'` → `isClosed ? 'border-[var(--success)] bg-[var(--surface)]' : 'border-[var(--border)]'`)

### CSS variables in use (src/index.css)
- `--foreground`: primary text color (white/light)
- `--text-secondary`: muted/secondary text (gray)
- `--background`: main background (dark)
- `--surface`: elevated surface (slightly lighter than background)
- `--surface-hover`: hover state for surfaces
- `--border`: subtle borders
- `--primary`: brand/accent color (purple/blue)
- `--success`: positive states (green)
- `--danger`: error states (red)
- `--warning`: caution states (yellow/orange)

## Domain: Type consistency & API patterns (field naming, function signatures)

When implementing new features (PO, Returns, etc.) that interact with existing types, watch for these consistency traps:

### Field naming mismatches
Common field name inconsistencies across modules:
- **Product info:** `name` vs `productName`, `sku` vs `productCode` vs `productSku`
- **Quantities:** `qty` vs `quantity`  
- **Prices:** `price` vs `unitPrice` vs `pricePerUnit`
- **Dates:** `date` vs `poDate` vs `receivedDate` vs `returnDate`
- **Quantities received:** `receivedQty` vs `receivedQuantity`

**Fix strategy:** Check the ACTUAL type definition first. For example:
```typescript
// TransactionItem uses: name, sku, pricePerUnit
// PurchaseOrderItem uses: productName, productSku, unitPrice, quantity
// GoodsReceiptItem uses: productName, productSku, orderedQuantity, receivedQuantity
```

When mapping between types, explicitly map fields:
```typescript
const newItem: SalesReturnItem = {
  productId: txItem.productId,
  productName: txItem.name,  // NOT txItem.productName
  productSku: txItem.sku,    // NOT txItem.productSku
  unitPrice: txItem.pricePerUnit,  // NOT txItem.unitPrice
  // ...
}
```

### Function signature mismatches
**adjustStock** - takes options object, NOT string:
```typescript
// WRONG
await adjustStock(productId, qty, 'Purchase return note')

// CORRECT  
await adjustStock(productId, qty, { notes: 'Purchase return note' })
```

**Journal entries** require full account info:
```typescript
// WRONG - missing accountCode and accountName
{ accountId: '4200', debit: 100, credit: 0 }

// CORRECT
{ 
  accountId: '4200',
  accountCode: '4200', 
  accountName: 'Sales Returns & Allowances',
  debit: 100, 
  credit: 0 
}
```

**Dialog component** - no `title` prop, use children:
```tsx
// WRONG
<Dialog open={open} onClose={onClose} title="My Dialog">

// CORRECT
<Dialog open={open} onClose={onClose}>
  <Card className="w-full max-w-2xl">
    <h2 className="text-xl font-bold mb-4">My Dialog</h2>
    {/* content */}
  </Card>
</Dialog>
```

### TypeScript strict mode patterns
**Unused imports** cause build failures - always clean up:
```typescript
import { Button, Card } from '@/components/ui'  // remove unused
function handler(_event: Event) {}  // prefix unused params
```

**Unused variables** in destructuring:
```typescript
// WRONG
const totalReceived = items.reduce(...)
const totalOrdered = items.reduce(...)  // TS6133 if not used

// CORRECT - remove if not needed
const totalReceived = items.reduce(...)
// delete totalOrdered line
```

**JSX structure balance** - every opening tag needs closing:
```tsx
// WRONG
<Card>
  <div className="p-4">
    content
  // missing </div>

// CORRECT
<Card>
  <div className="p-4">
    content
  </div>
</Card>
```

### API existence checks
Before using functions, verify they exist:
- `receiveGoods` doesn't exist in purchaseOrders.ts - use `createGoodsReceipt` instead
- `getTransaction` might not be exported - check the actual exports
- `addInventoryMovement` doesn't exist - use `adjustStock` instead

**Diagnosis:** When you see "Module has no exported member X", grep the actual file:
```bash
grep "export.*function" src/lib/module.ts
```

## Pitfall: STATE handoff file goes stale — always audit codebase first
When resuming via `OMNI_POS_STATE.md` (or any handoff document), the "BELUM dikerjakan" section is FREQUENTLY outdated — features get implemented but the STATE file doesn't get updated in the same session. Real case: STATE listed Akuntansi, PO/Supplier, Retur, Loyalty as "belum" when all were fully coded (109 source files, 18 feature modules). 

**Workflow at session start:**
1. Read `OMNI_POS_STATE.md` for context
2. Run a quick codebase audit via `delegate_task`: search for files/code matching each "belum" item (e.g. `search_files pattern="accounting|COA|journal" path="src"` for accounting, `search_files pattern="supplier|purchase" path="src"` for PO, etc.)
3. Update STATE file to match reality BEFORE doing anything else
4. Only then ask user what's next

This prevents wasting time on "should we build X?" when X already exists. The user expects you to know what's done — saying "STATE says belum" when the code is there is embarrassing and wastes a turn.

### Batch conversion script (use execute_code)
When multiple pages need dark theme conversion, use `execute_code` with a string replacement dictionary — much faster than patching one class at a time:
```python
from hermes_tools import read_file

replacements = [
    ('bg-gray-50', 'bg-white/5'),
    ('"bg-white ', '"bg-white/[0.03] '),
    ('bg-white divide', 'bg-white/[0.03] divide'),
    ('className="bg-white"', 'className="bg-white/[0.03]"'),
    ('text-gray-900', 'text-white'),
    ('text-gray-800', 'text-white/90'),
    ('text-gray-700', 'text-white/80'),
    ('text-gray-600', 'text-white/60'),
    ('text-gray-500', 'text-white/50'),
    ('text-gray-400', 'text-white/40'),
    ('divide-gray-200', 'divide-white/10'),
    ('border-gray-200', 'border-white/10'),
    ('border-gray-300', 'border-white/20'),
    ('hover:bg-gray-50', 'hover:bg-white/5'),
    ('text-blue-600', 'text-brand-300'),
    ('text-red-600', 'text-red-400'),
]
```
**Pitfall:** After batch replace, run `grep -c "bg-white\b\|bg-gray-50\|text-gray-900"` to verify remaining light-theme classes. Some patterns like standalone `className="bg-white"` need special handling — order matters: put `"bg-white "` (with trailing space) before `bg-white divide` before `className="bg-white"`.

### PO/Return workflow — status gating pitfall
When building Purchase Order or Return workflows with status-based button visibility (Draft → Submitted → Received), ensure ALL status transitions have explicit UI actions:
- PO created with `status: 'draft'` but "Receive Goods" button only shows when `status === 'submitted'` → user CANNOT receive goods without a Submit button
- "Buat Retur" button only shows when `status === 'received'` → user cannot return without completing full flow
- **Fix:** Add a `submitMutation` that calls `updatePurchaseOrder(id, { status: 'submitted' })` with a visible "Submit PO" button when status is draft
- **Rule:** Every status-gated action must have an explicit UI trigger for the preceding transition. Audit: for each `if (status === X)` button, check there's a button that transitions TO X from the previous state.

## Pitfalls tambahan
- **TypeScript syntax di JavaScript file (preload.js, main.js) → SyntaxError.** Electron preload & main files pakai `.js` (bukan `.ts`), tapi IDE/habit bikin pakai `(path?: string)` → error `Unexpected token ':'`. Fix: di file `.js`, JANGAN pakai type annotations. Preload API: `exportBackup: (path) => ipcRenderer.invoke(...)` BUKAN `(path?: string)`. Type annotations hanya di `.d.ts` file (mis `src/types/electron.d.ts`).

- **Dialog component API (no title prop, gunakan DialogHeader pattern).** Omni POS punya DialogHeader, DialogTitle, DialogContent, DialogFooter terpisah. JANGAN pakai `<Dialog title="...">`. Fix: `<Dialog open onClose><DialogHeader><DialogTitle>Judul</DialogTitle></DialogHeader><DialogContent>isi</DialogContent><DialogFooter>tombol</DialogFooter></Dialog>`.

- **Date type mismatch saat load dari IPC (IndexedDB → main process → renderer).** `createdAt` dari `listBackups()` bisa jadi Date object di main process tapi string di renderer (karena JSON serialization). Fix: selalu convert `const backupsWithStringDates = result.backups.map(b => ({ ...b, createdAt: b.createdAt instanceof Date ? b.createdAt.toISOString() : String(b.createdAt) }))`.

- **Dexie `.where(field).equals(x)` throw SchemaError di RUNTIME walau build sukses — kalau `field` BUKAN index di schema version.** Gejala: halaman nunjukin data kosong padahal data ada, dan query yang manggil `.where('referenceType').equals(...)` (atau field lain yang bukan index) lempar `SchemaError` yang di-catch diam-diam → fungsi capture oleh `try/catch`, hasilnya tak pernah kepakai. BUILD tetap hijau (error cuma runtime). Diagnosis: buka `src/lib/indexeddb.ts`, lihat baris `this.version(N).stores({ table: 'id, colA, colB, ...' })` — kalau field yang di-`.where()` nggak ada di daftar index tabel itu, itu biang keroknya. Fix: (a) tambah field itu ke index schema; (b) **bump version number** (v3→v4) — kalau tidak, migration nggak di-apply kalau user nggak re-seed; Dexie auto-migrate tapi WAJIB version baru. Contoh nyata: `journalEntries: 'id, number, date, type, postedAt, createdAt'` kurang `referenceType, referenceId` → `.where('referenceType')` rusak → jurnal/laporan kosong meski journal entries ADA di DB. Setelah bump version, tes dengan reload penuh (DB migrasi sekali) — flag `?seed=1` optional untuk ngebersihin data lama.
- **Seed/bulk-insert data referensial bypass service layer → fitur downstream (jurnal, agregat, rekap) tampil KOSONG padahal transaksi ada.** Gejala: data inti (produk/pelanggan/transaksi) muncul dan dashboard omzet terhitung, TAPI fitur turunan yang generate dari SERVICE LAYER (mis. jurnal akuntansi dari `createTransaction`, agregat harian) kosong / Rp 0 — karena seed pakai `localDb.transactions.bulkPut(...)` langsung ke IndexedDB, nggak lewat `createTransaction()` yang punya side-effect auto-journal. Build sukses, bukan error. Fix: bikin **idempotent backfill** — fungsi yang scan record yang belum punya artefak turunan (mis. cek `referenceId` sudah ada jurnal belum), lalu generate-mu pakai service function yang sama; panggil di `bootstrap()` setelah seed. Idempotent = guard `` if (exists) skip `` pakai `Set` dari `referenceId` yang udah ada, biar aman dipanggil tiap load. Diagnosis "fitur X kosong tapi data sumber ada": cek apakah data di-seed langsung ke IndexedDB (bypass service) — kalau iya, backfill.
- **Dialog detail/overlay di-render TANPA kondisi → layar HITAM mantul cuma header.** Gejala nyata (Sales Return list): halaman terbuka normal, tapi yang kelihatan cuma kotak hitam berjudul "Detail Sales Return" menutupi seluruh konten — isi detail nggak ada. Root cause: `<div className="fixed inset-0 bg-black bg-opacity-50 ...">` modal dirender TANPA guard `{selectedData && (...)}`, jadi overlay selalu muncul di atas halaman walau `selectedReturn` masih `null`. Karena data null, isi di dalamnya nggak render → user cuma lihat wrapper hitam + header. Fix: bungkus SELURUH dialog (overlay + Card + isi) dalam `{selected && ( ... )}` — overlay TIDAK BOLEH dirender saat tak ada data yang dipilih. Saat bungkus ulang, pastikan JSX balance (buka `{selected && (` lalu tutup `)}` MEMBELAKANGI `</div></Card>`; urutan penutup: `</div>` konten → `</Card>` → `</div>` overlay → `)}`). Auditori dialog detail di halaman list (Transaksi, Pelanggan, PO, Retur, notas): tiap dialog yang menampilkan entitas harus punya kondisi `selected` sebelum render overlay.
- **`lint` script manggil `eslint` padahal project pakai `oxlint` (tanpa `eslint.config.js`).** Gejala: `npm run lint` nyoba install `eslint@10` (muncul "package was not found and will be installed") lalu gagal `ESLint couldn't find an eslint.config.js`. cek `.oxlintrc.json` di root + `oxlint` di devDependencies. Fix: `"lint": "oxlint ."` di package.json scripts. Lesson: sebelum ngasih perintah lint, cek tool yang SEBENARNYA dikonfigurasi (ada `.oxlintrc.json` = pakai oxlint, bukan eslint), jangan andalkan nama script `lint` di package.json.
- **Dynamic import warnings:** Kalau Vite ngasih `[INEFFECTIVE_DYNAMIC_IMPORT]` warning karena module di-static import DI TEMPAT LAIN tapi di-dynamic import di file kamu → ganti dynamic import jadi static import biasa. Pola `await import('./customers')` bikin code-split tapi kalau module itu sudah di-import static di file lain (ExportPage, POSPage, dll), dynamic import jadi sia-sia. Fix: `import { getCustomer } from './customers'` di atas file, hapus dynamic import di tengah function.
- **TypeScript strict null checks di optional config:** Waktu akses nested property kayak `config.loyalty.tierMultiplier[tier]` di dalam blok `if (config.loyalty?.enabled)`, TypeScript tetap complain "possibly undefined" karena optional chaining di `if` TIDAK narrow type di dalam blok. Fix: pakai non-null assertion `config.loyalty!.tierMultiplier[tier]` saat kamu YAKIN properti ada (sudah di-check di atas). Alternatif: `const loyalty = config.loyalty!` di awal blok, lalu pakai `loyalty.tierMultiplier[tier]`.
- `vite preview` sering ninggal proses zombie saat restart berulang → `pkill -9 -f "vite preview"` sebelum start baru, verifikasi `ss -tlnp | grep PORT` bersih.
- Cetak struk/dokumen: JANGAN `window.open()` (diblok popup di HP) DAN JANGAN `window.print()` pada DOM app (bikin halaman kosong berlipat karena `visibility:hidden` tetap makan ruang → user lapor "sekali klik keluar 10 halaman"). **Pola terbaik: hidden iframe.** Buat `printHtml(html)` yang: bikin `<iframe>` invisible (`position:fixed; width/height:0; visibility:hidden`), `doc.write(html)` dokumen HTML MANDIRI lengkap (`<!DOCTYPE html>` + `@page` sendiri), `iframe.contentWindow.print()` on load (fallback timeout 500ms), cleanup iframe setelah ~1s. Keuntungan: (a) tidak buka tab baru (terasa native, aman di webview HP); (b) NOL halaman kosong karena app DOM tidak ikut; (c) ukuran kertas per-dokumen via `@page size:` — nota thermal `@page{size:58mm auto}` atau `80mm` (ikut `store.printerWidth`), surat jalan/invoice `@page{size:A4}`. Blok `@media print` di index.css app jadi tidak perlu lagi (kosongkan). Ini mengganti seluruh pendekatan `.receipt-print`/`.delivery-print` + body-class scope + unclip overflow/fixed — semua itu obsolete begitu pindah ke iframe.
- TanStack Query: setelah MUTASI yang mengubah data (checkout/simpan/hapus), WAJIB `queryClient.invalidateQueries` untuk semua queryKey terdampak, kalau tidak UI tampil data STALE meski IndexedDB sudah update. Gejala nyata POS: setelah bayar, stok produk "tidak berkurang", transaksi "tidak masuk daftar", laporan "tidak naik" — padahal data benar tersimpan, cuma cache lama. Fix di handler sukses checkout: invalidate `['products','transactions-list','customers','report','dashboard']`. Jangan andalkan `staleTime` untuk data transaksional.
- Seed dummy timestamp masa depan: kalau seed transaksi "hari ini" pakai jam ACAK (mis. `rng(8,20)*3600000`), sebagian bisa jatuh SETELAH `Date.now()`. Efek: transaksi BARU user (timestamp=now) keselip di TENGAH daftar (di bawah seed jam 20:00), user kira "transaksi tidak masuk". Fix: clamp `if (dayOffset===0 && ts>Date.now()) ts = Date.now()-rng(1,120)*60000`. Prinsip: seed hari ini tidak boleh > sekarang.
- Browser HP agresif cache SW/CSS → selalu ingatkan user hard-refresh (`Ctrl+Shift+R`) atau incognito setelah deploy ulang.

- **Pre-flight resource checks sebelum build** — build sering gagal/hang tanpa error jelas kalau server kehabisan disk atau CPU overload. WAJIB cek SEBELUM build: `df -h /` (disk <80%), `uptime` (load average <80% cores), `ps aux --sort=-%cpu | head -5` (cek zombie process). Common killers: runaway bash scripts (`notify.sh` recursive loop makan 96% CPU), zombie `vite preview`/`python3 -m http.server`, npm cache bloat. Quick fix: `pkill -9 -f "vite preview"; npm cache clean --force; rm -rf ~/.npm/_cacache`. Kalau disk >90%, build NSIS installer bisa gagal di tengah — output `.exe` corrupt/half-written.

- **Vite preview server management (port 4173/4174)** — untuk test PWA yang sudah di-build, pakai `npx vite preview --host 0.0.0.0 --port 4173`. Jalankan via `terminal(background=true)` (bukan `&` di foreground). SELALU verifikasi server jalan dengan `sleep 3 && curl -sI http://localhost:4173 | head -5` SEBELUM kasih link ke user. Kalau connection refused: cek `dist/` ada (`ls -la dist/`), kalau kosong → `npm run build` dulu. Kalau port occupied: `pkill -9 -f "vite preview"` + `ss -tlnp | grep 4173` buat cek. User OmniPOS prefer direct IP+port (`http://SERVER_IP:4173`) bukan domain/nginx routing untuk quick testing.

- **Blank page diagnosis workflow** — kalau user bilang "beberapa halaman blank putih" tanpa specify mana: (1) Grep semua feature files: `find src/features -name "*.tsx" | grep -iE "Create|List|Detail"`, (2) Batch-check via `execute_code`: baca tiap file, cek import count (0 imports = file incomplete), cek `placeholder`/`coming soon`/`TODO`, cek `export default` atau `export function` ada, (3) Kalau file keliatan complete → minta user buka F12 → Console → copy-paste error. Jangan tebak-nebak halaman mana yang blank, tanya spesifik atau minta console log. Common causes: `useQuery` return empty (render "no data" bukan blank), early return tanpa UI, dialog overlay tanpa guard condition.

- **User preference (OmniPOS):** Focus PWA web app DULUAN, .exe desktop secondary. User explicit: "bukan yang exe tapi yang web app pwa bos". Jangan habiskan waktu fix installer kalau web app masih ada bug. Prioritas: (1) web app features jalan & rapi, (2) baru desktop conversion.
- Close affordance PaymentDialog (dan SEMUA dialog full-screen alur kritis): dialog Pembayaran gampang kelupaan kasih jalan keluar — user stuck, tak bisa balik nambah barang. WAJIB: tombol X di header + tombol sekunder "← Kembali & Tambah Barang" full-width. `onClose` cukup tutup dialog TANPA clear cart (keranjang tetap utuh, tinggal tambah lagi). Sejalan BUG 5.
