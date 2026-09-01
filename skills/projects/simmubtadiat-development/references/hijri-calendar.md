# Hijri calendar handling in SIM Mubtadiat

## Canonical conversion: Hijri → Masehi (browser, WIB)

Tabular-estimate JD + Intl islamic-umalqura refinement. Source of truth for
the user is Umm al-Qura (matches dashboard clock in frontend/src/js/main.js
`formatHijri`). Verified test cases (must pass any rewrite):

| Hijri | Masehi |
|---|---|
| 1 Muharram 1447 | 2025-06-26 |
| 1 Ramadhan 1446 | 2025-03-01 |
| 1 Syawal 1446 | 2025-03-30 |
| 1 Muharram 1448 | 2026-06-16 |
| 30 Dzulhijjah 1446 | null (month has 29 days — correct rejection) |

```js
function jdToGregorian(jd) {
  const l = jd + 68569, n = Math.floor((4*l)/146097);
  const l2 = l - Math.floor((146097*n+3)/4);
  const i = Math.floor((4000*(l2+1))/1461001);
  const l3 = l2 - Math.floor((1461*i)/4) + 31;
  const j = Math.floor((80*l3)/2447);
  const day = l3 - Math.floor((2447*j)/80);
  const l4 = Math.floor(j/11);
  return { year: 100*(n-49)+i+l4, month: j+2-12*l4, day };
}
function gregorianToHijri(date) {
  const parts = new Intl.DateTimeFormat('en-US-u-ca-islamic-umalqura',
    { timeZone:'Asia/Jakarta', day:'numeric', month:'numeric', year:'numeric' }).formatToParts(date);
  let d=0,m=0,y=0;
  parts.forEach(p => { if(p.type==='day') d=+p.value; else if(p.type==='month') m=+p.value; else if(p.type==='year') y=+p.value; });
  return {d,m,y};
}
function hijriToMasehi(y,m,d) {
  const jd = d + Math.ceil(29.5*(m-1)) + (y-1)*354 + Math.floor((3+11*y)/30) + 1948439;
  const g = jdToGregorian(jd);
  for (let delta=-4; delta<=4; delta++) {
    const date = new Date(Date.UTC(g.year, g.month-1, g.day+delta, 12));
    const h = gregorianToHijri(date);
    if (h && h.y===y && h.m===m && h.d===d) {
      return `${date.getUTCFullYear()}-${String(date.getUTCMonth()+1).padStart(2,'0')}-${String(date.getUTCDate()).padStart(2,'0')}`;
    }
  }
  return null; // invalid Hijri date (e.g. day 30 in a 29-day month)
}
```

Go month names constant: Muharram, Safar, Rabiul Awal, Rabiul Akhir, Jumadil
Awal, Jumadil Akhir, Rajab, Sya'ban, Ramadhan, Syawal, Dzulqa'dah, Dzulhijjah
(index+1 = bulan_hijri).

## Semester resolution rules

- **Absensi manual bulanan** (santri & pengajar): a Hijri month belongs to the
  semester whose range contains the month's **day 15**. Backend:
  `SemesterDariBulanHijri(ctx, tahunAjaran, tahunHijri, bulanHijri)` in
  models/hijri_semester.go. Ordinal comparison: `tahun*360 + bulan*30 + tanggal`.
- **Absensi sesi** (per-date Masehi): unchanged legacy path — range lookup in
  `kalender_kuartal`, then `SemesterDariKuartal` (kwartal 1-2 → smt 1, 3-4 → smt 2).
- Backfill SQL for the manual tables (GROUP BY + MAX so a month matching
  multiple semester rows stays deterministic):

```sql
UPDATE absensi_manual_bulanan am SET semester = v.sem
  FROM (SELECT am2.id,
               MAX(CASE WHEN (ks.mulai_tahun_hijri*360 + ks.mulai_bulan_hijri*30 + ks.mulai_tanggal)
                             <= (am2.tahun_hijri*360 + am2.bulan_hijri*30 + 15)
                        AND  (ks.selesai_tahun_hijri*360 + ks.selesai_bulan_hijri*30 + ks.selesai_tanggal)
                             >= (am2.tahun_hijri*360 + am2.bulan_hijri*30 + 15)
                       THEN ks.semester END) AS sem
          FROM absensi_manual_bulanan am2
          LEFT JOIN kalender_semester_hijri ks ON ks.tahun_ajaran = am2.tahun_ajaran
         GROUP BY am2.id) v
 WHERE am.id = v.id AND am.semester IS DISTINCT FROM v.sem;
```

## Tables

- `kalender_semester_hijri` (PK tahun_ajaran, semester): Hijri start/end +
  nullable `masehi_mulai/selesai` DATE columns (written by frontend).
- `kalender_kuartal` (PK kuartal, tahun_ajaran): derived; each semester splits
  into two kwartals (tamrin half / ujian half) by halving the Gregorian span.
- `hijri_semester_map`: DROPPED in migration 047 — superseded, do not recreate.

## API

- `GET /api/kalender/hijri-semester?tahun_ajaran=X` — any logged role except wali_santri.
- `POST /api/kalender/hijri-semester` — pimpinan/admin only. Body: array of
  KalenderSemesterHijri; validates bulan 1-12, tanggal 1-30, mulai <= selesai,
  smt2 starts after smt1 ends; syncs kalender_kuartal + backfills absensi manual.

## Cross-year Hijri semesters

A semester routinely **spans two Hijri years** (pesantren pattern: year starts
~Syawal). Example TA 2026/2027: Smt 1 = 1 Syawal **1447** → 29 Rabiul Awal
**1448**; Smt 2 = 16 Rabiul Awal **1448** → 30 Sya'ban **1448**. Every Hijri
input field has its own year component, so the ordinal comparison
(`tahun*360 + bulan*30 + tanggal`) handles this correctly — never key
resolution on month number alone.

## Kalender_kuartal sync query (run before deploying — real 500 bug)

The semester-split uses a LATERAL value list; the columns belong to the `base`
subquery alias, NOT `k`:

```sql
INSERT INTO kalender_kuartal (kuartal, tahun_ajaran, tgl_mulai, tgl_selesai)
SELECT k.kuartal, base.tahun_ajaran,
       base.mulai + (k.idx - 1) * base.span,
       CASE WHEN k.idx = 1 THEN base.mulai + base.span - 1 ELSE base.selesai END
  FROM (
    SELECT semester, tahun_ajaran,
           masehi_mulai::DATE AS mulai, masehi_selesai::DATE AS selesai,
           GREATEST(((masehi_selesai::DATE - masehi_mulai::DATE + 1) / 2), 1) AS span
      FROM kalender_semester_hijri
     WHERE masehi_mulai IS NOT NULL AND masehi_selesai IS NOT NULL
  ) base,
  LATERAL (VALUES
    (CASE semester WHEN 1 THEN 1 ELSE 3 END, 1),
    (CASE semester WHEN 1 THEN 2 ELSE 4 END, 2)
  ) k(kuartal, idx)
ON CONFLICT (kuartal, tahun_ajaran)
DO UPDATE SET tgl_mulai = EXCLUDED.tgl_mulai, tgl_selesai = EXCLUDED.tgl_selesai;
```

Bug history: shipping `k.tahun_ajaran` (alias mixup) made every calendar POST
return 500 with no SQL text in app logs — caught by re-running the tx in psql.
