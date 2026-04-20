---
name: tech-news-fb-writer
description: Scrape tech news from trusted sources, write engaging Facebook articles with strong hooks, real data, and source links. Also finds eye-catching images for posts.
category: social-media
version: 1.0
---

# Tech News Facebook Writer

Scrape berita teknologi terbaru dari sumber terpercaya, tulis artikel Facebook yang engaging dengan hook kuat, data real, link sumber, dan gambar menarik.

## Trigger
User minta artikel Facebook tentang berita tech terbaru, review gadget, atau konten teknologi.

## Workflow

### Step 1: Cari Berita Terbaru
Scrape dari salah satu sumber ini:
- **The Verge** — `https://www.theverge.com/tech` (paling update)
- **Tom's Guide** — `https://www.tomsguide.com` (review detail + data)
- **Android Authority** — `https://www.androidauthority.com`
- **Notebookcheck** — `https://www.notebookcheck.net` (benchmark data)

Gunakan `browser_navigate` lalu `browser_console` untuk extract headlines:
```javascript
// Get article headlines
const links = Array.from(document.querySelectorAll('a'));
const articles = links
    .filter(a => a.href && (a.href.includes('/2025/') || a.href.includes('/2026/')))
    .map(a => ({title: a.textContent.trim().substring(0, 100), url: a.href}))
    .filter(a => a.title.length > 15 && a.title.length < 150);
```

### Step 2: Ambil Detail Artikel
Buka artikel terpilih, extract konten:
```javascript
const article = document.querySelector('article') || document.querySelector('main');
article.innerText.substring(0, 4000);
```

Cari data spesifik:
- **Spek** — resolusi, chipset, RAM, dll
- **Benchmark** — Geekbench, 3DMark, skor DxOMark
- **Harga** — MSRP / harga resmi
- **Perbandingan** — tabel data head-to-head
- **Verdict reviewer** — skor dan opini

### Step 3: Tulis Artikel Facebook

#### Aturan Penulisan:
1. **Hook = provokatif + penasaran + angka**
   - ❌ "MacBook Neo review"
   - ✅ "Laptop 6 Jutaan Ini Bikin Microsoft Panik"
   - ✅ "⚠️ JANGAN BELI HP INI SEBELUM BACA!"
   - ✅ "😱 5 HP INI BIKIN IPHONE KELIHATAN MAHAL"

2. **Gaya bervariasi** (rotate tiap artikel):
   - 🅰️ **Kontroversi/Opini** — "STOP! Jangan beli dulu!"
   - 🅱️ **Storytelling** — cerita dampak/efek industri
   - 🅲️ **Review santai** — kayak YouTuber, ada plus minus
   - 🅳️ **Data-driven** — fokus angka dan benchmark

3. **JANGAN pakai "pengalaman pribadi"** — Netizen ga percaya. Posisikan sebagai:
   - "Kompilasi dari 15+ review"
   - "Reviewer besar bilang..."
   - "Dari data yang diambil di..."

4. **Format artikel:**
   - Hook kuat (1-2 baris)
   - Isi dengan data spesifik (angka, perbandingan)
   - Verdict/opini berdasarkan data
   - CTA (comment, share, tag)
   - Sumber review (link)
   - Harga (user kasih dari Shopee/Tokopedia)

5. **Bahasa:**
   - Casual, kayak ngobrol
   - Emoji secukupnya (ga berlebih)
   - Kalimat pendek-pendek buat ritme cepat
   - Bahasa Indonesia

### Step 4: Cari Gambar Eye-catching
Dari artikel sumber, extract gambar:
```javascript
// Get images from article
const images = Array.from(document.querySelectorAll('img'))
    .filter(img => img.src && img.alt && img.alt.length > 5)
    .map(img => ({src: img.src, alt: img.alt}))
    .filter(img => !img.src.includes('logo') && !img.src.includes('svg'));
```

Download gambar terbaik:
```bash
curl -sL -o nama-file.jpg "url-gambar"
```

Kirim ke user via `MEDIA:/path/to/image`

**Rekomendasi gambar:**
- Warna terang = scroll-stopper di feed
- Perbandingan side-by-side = netizen suka
- Warna-warni / unik = eye-catching

### Step 5: Format Final

```
[Artikel dengan hook kuat + data real + CTA]

📚 SUMBER:
- [link review 1]
- [link review 2]

💰 HARGA:
- Shopee: Rp xxx (user kasih link)
- Tokopedia: Rp xxx (user kasih link)
```

### Step 6: Kirim Gambar
Pilih 2-3 gambar terbaik, kirim ke user via Telegram:
- `MEDIA:/root/.hermes/macbook-neo-images/nama.jpg`

## Sumber Gambar Alternatif
Jika artikel tidak punya gambar bagus:
- **Unsplash** — `https://unsplash.com/s/photos/keyword`
- **Pexels** — `https://pexels.com/search/keyword`
- **Official press kit** — biasanya ada di brand website

## Gaya Artikel (Rotate)
| # | Gaya | Hook Style | Contoh |
|---|------|-----------|--------|
| 1 | Kontroversi | ⚠️ PROVOKATIF | "JANGAN BELI sebelum baca!" |
| 2 | Storytelling | 😶 Cerita dampak | "Microsoft panik gara-gara ini" |
| 3 | Review santai | 📱 Analisis | "Dari 15+ review, ini hasilnya" |
| 4 | Data-driven | 📊 Angka | "Benchmark: 1707 vs 3328" |

## Pitfalls
- **JANGAN** klaim pengalaman pribadi — netizen ga percaya
- **JANGAN** tanpa sumber link — kurang kredibel
- **JANGAN** hook lemah — "Review MacBook Neo" bukan hook
- **JANGAN** semua CAPS di hook — 1-2 kata cukup
- **JANGAN** gambar gelap/kecil — feed Facebook butuh visual kuat
- **Harga** selalu dari user (Shopee/Tokopedia) — bukan dari artikel luar

## Contoh Artikel

### Style Kontroversi:
```
⚠️ STOP! JANGAN BELI HP DULU!

Gw baru riset 3 hari nonstop. Hasilnya? 90% orang SALAH BELI.
...
[isi dengan data real]

📚 SUMBER: https://...
💰 HARGA: Shopee Rp xxx
```

### Style Storytelling:
```
🍎💻 Laptop 6 Jutaan Ini Bikin Microsoft Panik

Dalam 2 MINGGU setelah pengumuman MacBook Neo,
Microsoft langsung umumkan perbaikan besar Windows 11.
...
[isi dengan data real]

📚 SUMBER: https://...
💰 HARGA: Shopee Rp xxx
```
