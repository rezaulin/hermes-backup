# RAPOT Header Layout Patterns - Reference

## Session: Aug 25, 2026 - Structure Debugging & Pattern Correction

### Problem Summary
Multiple attempts (v27-v33) using complex grid/flex layouts broke the visual flow of the raport header. User feedback: "Woi agenku, perbaikan malah makin berantakan" → Reset to simplest vertical stack pattern.

### The Anti-Pattern (v33 FAIL)

```html
<!-- ❌ Grid wrapper splits logo + text across 3 columns -->
<div class="header-grid" style="display: grid; grid-template-columns: 1fr auto 1fr;">
    <div class="student-data-left">Identitas Kiri</div>
    <div class="header-text">Logo + Teks Arab</div>
    <div class="student-data-right">Identitas Kanan</div>
</div>
```

**Visual Result**: Logo dan header text ter-split ke kolom berbeda → alignment mismatch

### The Solution Pattern (v34+ CORRECT)

Clear three-layer vertical stack: **Kop → HR Line → Identitas**

```html
<!-- ✅ Layer #1: Kop Surat (single balanced flex row) -->
<div class="kop-surat" style="display: flex; justify-content: space-between; align-items: center;">
    <div class="header-logo-img" style="width:60px;height:60px;">
        <img src="/logo-raport-bw-v5.png" alt="Logo">
    </div>
    <div class="header-text" style="text-align:center; flex:1; margin:0 20px;">
        <!-- Arabic text content -->
        <p class="hdr-1">كشف الدرجات الدراسية</p>
        <h1 data-field="semester-title">فصل الدراسة الأولى</h1>
        <h2 data-field="madrasah-line">المدرسة الابتدائية للبنات هداية المبتدئات كديري ليربيا</h2>
        <p class="hdr-tahun">سنة : <span data-field="tahun-ajaran">١٤٤٧ - ١٤٤٨ هـ / ٢٠٢٦ - ٢٠٢٧ م</span></p>
    </div>
    <div style="width:60px;"></div> <!-- Spacer to balance logo width -->
</div>

<!-- ✅ Layer #2: Horizontal separator line -->
<hr style="border:none;height:1px;background-color:#000;margin:6px auto;width:90%;">

<!-- ✅ Layer #3: Identitas Siswa (separate 2-col below line) -->
<div class="identitas-siswa" dir="ltr" style="display:flex;justify-content:space-between;gap:20px;margin-top:8px;">
    <div class="identitas-kiri" style="flex:1;">
        <p><span class="lbl">Nama</span><span class="colon">:</span><span class="val" data-field="nama">....................</span></p>
        <p><span class="lbl">No. Stambuk</span><span class="colon">:</span><span class="val" data-field="stambuk" style="white-space:nowrap;">....................</span></p>
        <p><span class="lbl">Kelas</span><span class="colon">:</span><span class="val" data-field="kelas">....................</span></p>
    </div>
    <div class="identitas-kanan" style="flex:1;">
        <p><span class="lbl">No. Tamrin</span><span class="colon">:</span><span class="val" data-field="tamrin">....................</span></p>
        <p><span class="lbl">Bagian</span><span class="colon">:</span><span class="val" data-field="bagian">....................</span></p>
    </div>
</div>
```

### Key Design Principles

1. **Three Distinct Layers**: Clear vertical hierarchy (Kop → HR → Identitas)
2. **No Mixed Layout Strategies**: Each section uses ONE approach (flex), not both grid and flex
3. **Spacer Balance**: Empty div on right balances logo width (60px)
4. **Separate Containers**: Don't try to do everything in one complex wrapper
5. **White-space: nowrap**: Critical for labels like "No. Stambuk" to prevent wrapping

### User Preference Learning

> **User Instruction**: "Urutan #1 (Kop), Urutan #2 (Garis), Urutan #3 (Identitas)"
>
> **Lesson**: When user explicitly describes structure with numbered steps, follow EXACTLY that order. Do NOT over-engineer with complex CSS layouts. Simpler is better.

> **Frustration Signal**: "Haduh semakin melenceng jauh... rasanya aku pengen nangis"
>
> **Action**: Immediately STOP and revert to simplest pattern matching user's explicit instruction. Verify visually before continuing.

### Signature Order Fix (v34)

```html
<div class="signature-box" style="margin-top:4px !important;">
    <!-- LEFT: المدير (Principal/Director) -->
    <div class="text-center">
        <p class="ft-uth-18">المدير</p>
        <div style="height:36px;"></div>
        <p class="ft-tnr">(<span data-field="sig-mudir-nama">.........................</span>)</p>
    </div>
    
    <!-- RIGHT: المدرس (Teacher/Mudarris) -->
    <div class="text-center" data-field="sig-mudarris-box">
        <p class="ft-uth-18">المدرس</p>
        <div style="height:36px;"></div>
        <p class="ft-tnr"><span data-field="sig-mudarris-nama">.........................</span></p>
    </div>
</div>
```

**User Requirement**: "Tukar posisi: المدير harus di KIRI, و المدرس di KANAN. Rapatkan jarak vertikal antara tabel dan tanda tangan."

### Table Width Optimization

```diff
- Old: width: 90%; margin: 0 auto; (still too wide visually)
+ New: width: 92%; margin: 0 auto; (narrower, centered, proper margins)
```

**Rationale**: 92% leaves more left/right margin space, creating "compact and centered" look matching reference photo.

---

## Related Source Files
- `/root/.hermes/cache/documents/doc_2fd6c11f3372_1 Aliyah A (2).docx` - Word source (GOLD STANDARD)
- `/root/.hermes/cache/images/img_02813cf7d4f2.jpg` - Photo reference (secondary due to distortion)

## v34 Build Checklist
- [ ] Header structure: kop → hr → identitas (vertical stack, NO grid/flex mix)
- [ ] Spacer div present (balances logo width)
- [ ] White-space: nowrap on label values (No.Stambuk = one line)
- [ ] Table width: 92%, margin: 0 auto (compact centered)
- [ ] Signature order: Mudir LEFT, Mudarris RIGHT
- [ ] Margin top signature: 4px from table
- [ ] Visual verification in browser screenshot (not just build green)
- [ ] Cache name bumped to v34+

## Version History
- v27: Original successful structure
- v28-v33: Over-engineered with grids/flex → broken layouts
- v34: Simplified back to vertical stack following user explicit instructions

## Pitfalls Discovered (DO NOT REPEAT)
1. **Grid wrapper for header** → Splits layout across columns, breaks flow
2. **Mixed flex/grid in same container** → Creates alignment mismatches  
3. **Horizontal-only header** → Missing clear stacking order
4. **Complex CSS abstraction** → User prefers simple, explicit structure
5. **Ignoring user's numbered instructions** → Always follow "Urutan #1,#2,#3" exactly

## Verification Protocol
Before deploying any change:
1. Check comparison screenshot - does it match reference photo?
2. Verify Arabic text against Word .docx source (NOT just text extraction)
3. Run Playwright render test - should be EXACTLY 2 pages for F4
4. Inspect DOM - header must have clean hierarchy: kop > hr > identitas
5. If user says "makin berantakan", immediately reset to v27 structure
