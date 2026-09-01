---
name: earnapp-ip-tester
description: "Pre-test 9Proxy IP quality BEFORE mounting an EarnApp device — forward with state/city filter, verify org/region/latency, reject datacenter+flagged regions, so IPs aren't burned on dead devices. Use when deploying or swapping EarnApp farm devices, or when a device is 'green but not earning'."
version: 1.0.0
author: Hermes Agent
license: MIT
platforms: [linux]
metadata:
  hermes:
    tags: [earnapp, 9proxy, proxy, ip-quality, farming, depin]
    related_skills: [depin-bandwidth-farming]
---

# EarnApp IP Tester — pre-test sebelum bakar IP

Tiap `9proxy proxy -c US -p <port>` = **1 IP hangus permanen** (By-IPs one-way). Skill ini memastikan IP yang dibakar itu kemungkinan besar earning — dengan **filter state/city + pre-check quality SEBELUM device dipasang**.

## When to Use

- Deploy device baru di farm EarnApp
- Swap device "hijau tapi gak earning" (abu-abu / $0 berjam-jam)
- Setelah top-up 9Proxy pool — biar IP langsung target region bagus
- Kapan pun mau cek: IP ini layak gak buat EarnApp?

## Senjata utama: 9Proxy filter (verified 2026-08-31)

```bash
# ✅ WAJIB nama lengkap state + quotes — dua-huruf ("NY") GAGAL dengan "no proxy found"
9proxy proxy -c US -s "New York" -p 60000   # filter STATE: New York
9proxy proxy -c US -t "New York" -p 60000   # filter CITY (quotes wajib)
9proxy proxy -c US -z 10001 -p 60000        # filter ZIP
```

**Kenapa penting:** forward random `-c US` dapet ~80% region jelek → bakar IP percuma. Dengan `-s "New York"` langsung target state yang terbukti earning.

**⚠️ Syntax pitfall (verified 2026-08-31):** `-s` menerima NAMA LENGKAP (`"New York"`, `"Florida"`, `"Texas"`), BUKAN kode dua-huruf. `-s NY` / `-s ny` / `-s FL` → `✗ Forwarding failed: no proxy found` (kelihatan kayak stok habis, padahal formatnya salah). Kalau forward state gagal, cek dulu format sebelum asumsi pool kosong.

## Known GOOD vs BAD (dari observasi real, 2026-08-31)

### ✅ GOOD states/cities (target dengan -s/-t)
| State/City | ISP | Bukti |
|:--|:--|:--|
| **New York, NY** | Verizon | 🏆 $0.083/6jam (tertinggi) |
| **New York, NY** | T-Mobile | $0.04/3jam |
| **Mount Vernon, NY** | Verizon | earning |
| **Miami, FL** | Comcast | awet 4.5h+ |
| **Houston / Denver, TX/CO** | Comcast | awet 4.5h+ |
| **Gibsonville, NC** | Charter | awet 4.5h+ |
| **Jackson, MS** | Starlink | awet 4.5h+ |

### ❌ BAD (reject langsung, jangan pakai)
| Region | Alasan |
|:--|:--|
| **California** (Monterey Park, Millbrae, Stockton, dst) | Flagged "Low quality IP" |
| **Datacenter ASN** (Tier.Net AS397423, dll) | Flagged "VPN" |
| **T-Mobile East Providence RI** | 5h hijau tapi $0 |
| **Verizon Westbury NY / Richmond VA** | cepet mati 1-2h |

## Workflow (5 langkah, ~30 detik per port)

```bash
# 1. FORWARD dengan filter state (target NY, fallback TX/FL kalau kosong)
9proxy proxy -c US -s "New York" -p 60000
#    kalau error/Empty: 9proxy proxy -c US -s "Texas" -p 60000
#    atau:             9proxy proxy -c US -s "Florida" -p 60000

# 2. DAPAT IP publiknya (kolom ke-4 tabel 9proxy port -s)
IP=$(9proxy port -s | grep ":60000 " | awk -F"│" '{gsub(/ /,"",$4); print $4}')
echo "IP: $IP"

# 3. PRE-CHECK: org / region / latency (jalankan scripts/check-ip.sh)
bash scripts/check-ip.sh "$IP"

# 4. KALAU LOLOS → pasang device (restart earnapp)
# 5. KALAU GAGAL → kill + forward ulang (bakar 1 IP, tapi gak buang 6 jam)
9proxy port -k 60000
```

## check-ip.sh — kriteria LOLOS

| Cek | LOLOS kalau | GAGAL kalau |
|:--|:--|:--|
| **Org/ASN** | ISP residential (Comcast, Charter, Verizon, T-Mobile, Cox, AT&T, Mediacom, Starlink) | Datacenter ASN: Tier.Net, AMAZON, DIGITALOCEAN, HETZNER, OVH, VULTR, GOOGLE, AZURE, HOSTING, CLOUD, COLO, RACKSPACE, LINODE, ORACLE, IBM, COGENT |
| **Region** | Bukan California | California (semua kota) |
| **Latency** | < 1500ms | ≥ 1500ms |
| **IP unik** | belum pernah dipakai/burned di sesi ini | pernah di-blacklist |

Script: `scripts/check-ip.sh` (stdlib curl + grep, jalan di VPS farm).

## Pitfalls

1. **Test = bakar IP.** Setiap forward menghabiskan 1 IP permanen. Filter state bukan buat nol-in bakar — tapi buat bakar IP yang PROBABILITAS BAGUSNYA TINGGI. 1 IP untuk NY yang earning >> 5 IP untuk region random.
2. **`-t "New York"` butuh quotes** — spasi di city name. Tanpa quotes = parse error.
3. **Filter kota bisa kosong** — kalau 9Proxy gak punya stok di state itu, forward gagal/Empty. Fallback: coba state GOOD lain (TX, FL, NC) atau kota besar (Miami, Houston).
4. **IP 9Proxy bisa beda dari egress** — cek `incus exec <container> -- curl -s https://api.ipify.org` untuk IP yang BENERAN keluar, bukan cuma yang ada di tabel `9proxy port -s`.
5. **Jangan swap IP yang udah earning** — kalau device dapet $, jangan disentuh walau region-nya "kurang favorit". Earning > teori.
6. **Setelah top-up pool, target state GOOD dulu** — jangan habiskan pool baru ke random US.
7. **Watchdog auto-swap bisa dinyalakan kembali** setelah IP di pre-test — cuma swap yang butuh state-aware (pakai filter, bukan random).

## Related

- `depin-bandwidth-farming` — full farm operation (deploy, watchdog, ekonomi)
- Region durability data juga tersimpan di `region-durability.csv` di tiap farm VPS
