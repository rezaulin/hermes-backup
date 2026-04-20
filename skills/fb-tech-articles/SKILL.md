---
name: fb-tech-articles
description: Create engaging Facebook tech articles with strong hooks. Scrapes tech specs and writes casual Indonesian content optimized for engagement.
category: social-media
---

# Facebook Tech Article Generator

Create viral-ready Facebook articles about phones/gadgets from tech data.

## When to use
- User wants tech content for Facebook pages
- Need to write phone reviews, comparisons, or listicles
- Scraping GSMArena/TechRadar data and turning into social content

## Article Formats (rotate between these)

### 1. Kontroversi/Opini
**Hook pattern:** "⚠️ JANGAN BELI [produk] SEBELUM BACA INI!"
- Start with provocative statement
- Give honest pros/cons with strong opinions
- End with CTA: "Lo pake hp apa? Comment!"

### 2. Head-to-Head
**Hook pattern:** "🔥 [Produk A] VS [Produk B]: Siapa Raja [tahun]? (Hasil Mengejutkan!)"
- Side-by-side comparison with ✅/❌
- Personal verdict with reasoning
- End with: "Setuju atau ga? Debate di komentar!"

### 3. Listicle Viral
**Hook pattern:** "😱 [N] [KATEGORI] INI BIKIN [PRODUK MAHAL] KELIHATAN MAHAL!"
- Numbered list with emoji markers
- Each item: name + price + 1-line pros + unique angle
- End with: "Simpan post ini buat nanti! 📌"

## Writing Style Rules
- **Casual Indonesian** — pakai "lo/gw", bukan "anda/saya"
- **Short paragraphs** — max 2-3 baris per paragraf
- **Emoji** — tapi ga berlebihan (1-2 per paragraf)
- **Opini pribadi** — bukan cuma fakta, kasih pendapat
- **Provokatif tapi jujur** — hook kuat, konten tetep informatif
- **CTA di akhir** — comment, share, tag, atau simpan

## Hook Formula
- Pakai ANGKA: "5 HP...", "90% orang..."
- Pakai EMOJI warning: ⚠️🔥😱
- Pakai KATA provokatif: JANGAN, Mengejutkan, GILA, SALAH
- Pakai KURUNG: "(Hasil Mengejutkan!)"

## Additional Style: Review Santai (YouTuber Style)
**Hook pattern:** "[Produk]: Review Jujur dari Data, Bukan Opini Kosong"
- Open like a YouTuber: "Oke guys, jadi..."
- Present data first, opinion second
- Give scores per category (Kamera: 9/10, Charging: 4/10)
- Honest pros AND cons — not just promotion
- "Yang cocok / Yang ga cocok" section
- End with: "Kalo mau gw review hp lain, comment aja!"

## CRITICAL: No Fake Personal Experience ⚠️
**User explicitly stated:** "jangan pakai kata-kata pengalaman karena pasti netizen gak percaya"

DO NOT write "gw udah coba", "gw baru aja beli", or any fake personal claims.
Instead, use these credibility approaches:

1. **Kurator/Kompilator** — "Gw kompilasiin dari 15+ review reviewer besar"
2. **Data-driven** — pakai benchmark angka asli (Geekbench, 3DMark, DxOMark score)
3. **Sumber jelas** — "Menurut Tom's Guide...", "DxOMark labelin..."
4. **Community consensus** — "Banyak reviewer bilang...", "Komplain terbanyak di forum..."

Position as: **orang yang bantu ringkas info**, bukan "orang yang ngaku-ngaku udah coba"

## Data Sources (Updated)
- Tom's Guide ✅ — accessible, has detailed reviews with benchmarks
- DxOMark ✅ — camera rankings and scores
- Notebookcheck ✅ — detailed specs and comparisons
- Android Authority ✅ — reviews and news
- GSMArena ❌ — Cloudflare Turnstile (captcha blocked)
- PhoneArena ❌ — aggressive bot detection

### Tom's Guide Camera Data Extraction
Tom's Guide reviews contain real benchmark tables. Extract via:
```
document.querySelector('#section-[product]-review-cameras')?.parentElement?.innerText
```
This gives actual Geekbench scores, 3DMark results, and camera comparison data.

## Additional Style: Berita Teknologi Terbaru
**Hook pattern:** dampak/reaksi industri, bukan promosi produk
- Angle: efek berita ke konsumen/pasar, bukan "produk X bagus"
- Pakai data real: benchmark angka, perbandingan layar, harga
- Ada timeline: "Dalam 2 minggu setelah X, terjadi Y"
- Netral: kasih plus DAN minus

## Source & Pricing Format (Wajib di akhir artikel)
```
📚 SUMBER:
- [link review 1]
- [link review 2]

💰 HARGA:
- Shopee: Rp xxx (user provides link)
- Tokopedia: Rp xxx (user provides link)
```
User akan kasih harga Shopee/Tokopedia. Jangan bikin harga sendiri.

## Notes
- User prefers Indonesian language content
- Target audience: Indonesian Facebook users interested in budget phones
- User wants article styles to rotate (jangan monoton)
- Format: provokatif → storytelling → review santai → berita teknologi (cycle these)
- Always use real source links, not just source names
