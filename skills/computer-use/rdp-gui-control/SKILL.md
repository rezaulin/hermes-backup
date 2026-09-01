---
name: rdp-gui-control
description: "Kontrol GUI desktop remote (Windows/Linux) via RDP dari Hermes — setup Xvnc backend di VM headless, SSH tunnel ke port RDP, lancarkan xfreerdp di Xvfb virtual display, driver dengan xdotool (klik/kety/scroll), verifikasi end-to-end. Untuk mengontrol GUI VM remote yang IPv6-only atau dari background tanpa kursor fisik."
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [rdp, gui, remote-desktop, xfreerdp, xvnc, xvfb, xdotool, freestyle, computer-use, automation]
    related_skills: [computer-use, freestyle-vms, depin-bandwidth-farming]
---

# Kontrol GUI Remote via RDP

Remote-desktop GUI yang bisa kamu **kontrol keyboard + mouse-nya dari background** (gak rebut kursor fisik, jalan di machine headless). Pola: `SSH tunnel → xfreerdp → Xvfb virtual display → xdotool input → verifikasi`.

> Trigger: user mau "kontrol GUI" VM RDP, mau klik/ngetik di desktop remote, VM-nya headless/IPv6-only, atau perlu buka app GUI di cloud VM.

## Kenapa pola ini (bukan cara lain)

| Opsi | Verdict |
|---|---|
| **SSH tunnel → xfreerdp → Xvfb → xdotool** | ✅ **INi yang terbukti.** RDP client jalan di virtual display, kamu tunjuk driver input. |
| RDP langsung ke IPv6 publik | 🚫 gagal kalau host kamu gak punya route IPv6 |
| `computer_use` (cua-driver) langsung | ⚠️ cua-driver biasanya menunjuk DISPLAY yang beda; pecahin dengan pakai xdotool ke window FreeRDP |
| noVNC | alternatif browser-only buat manusia (IPv4 jalan), bukan buat kontrol agent input |

## Arsitektur target

```
Host (Hermes)                             VM remote (headless)
┌─────────────────────────────┐            ┌─────────────────────────┐
│ xdotool (click/key/type)    │            │ xrdp ── Xvnc :10        │
│   └▶ window FreeRDP         │            │   └▶ XFCE desktop       │
│        ▼                    │  SSH tunnel│                          │
│   xfreerdp ────127.0.0.1:13389──▶ beta-ssh:22 ──▶ 127.0.0.1:3389  │
│   (render di Xvfb :99)      │            └─────────────────────────┘
└─────────────────────────────┘
```

**Kunci:** xfreerdp render ke display `:99` (Xvfb) → yang "nyekel" layar visual; xdotool kirim input ke **window FreeRDP yang sama** → event masuk ke sesi RDP → diteruskan ke desktop remote. Input arahnya ke setiap client mana pun yang fokus di window itu.

## Step-by-step

### 0. Prereq di host
```bash
apt-get install -y freerdp2-x11 xdotool x11-apps imagemagick   # xfreerdp, xdotool, xwd, convert
# pastikan Xvfb display :99 ada & pakai XAUTHORITY
ps aux | grep "[X]vfb"          # biasanya sudah jalan (Hermes spawn Xvfb)
XAUTH=$(ls /tmp/xvfb-run.*/Xauthority 2>/dev/null | head -1)   # ambil path auth
export DISPLAY=:99 XAUTHORITY="$XAUTH"
```

### 1. Buka SSH tunnel ke port RDP (bypass IPv6-only / NAT)
```bash
ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null \
    -o ServerAliveInterval=30 -o ServerAliveCountMax=3 -o ExitOnForwardFailure=yes \
    -N -L 13389:127.0.0.1:3389 \
    "<user>@<ssh-host>" &
# verifikasi
ss -tlnp | grep 13389 && echo PORT UP
```
Untuk VM Freestyle: user-nya `rena+root:<TOKEN>@beta-ssh.freestyle.sh` (token di username, lihat skill `freestyle-vms`).

> Jalankan tunnel sebagai background process Hermes (`terminal background=true`), bukan `nohup &`.

### 2. Launch xfreerdp ke display virtual
```bash
export DISPLAY=:99 XAUTHORITY="$XAUTH"
xfreerdp /v:127.0.0.1:13389 /u:<user> /p:<pass> /size:1280x700 \
    +clipboard /cert-ignore /log-level:INFO &
sleep 15   # biar koneksi + render
# verifikasi window ada
xdotool search --name "FreeRDP" | head -1    # → WID
```

### 3. Verifikasi GUI hidup (screenshot + diff)
```bash
xwd -root -display :99 -silent -out /tmp/s.xwd
convert /tmp/s.xwd /tmp/s.png
stat -c%s /tmp/s.png        # >10KB + mean>0 = ADA konten GUI (bukan hitam 446B)
convert /tmp/s.png -format '%[fx:mean]' info:   # >0.05 = desktop render
```
Screenshot 446 byte / mean 0 = layar hitam (belum render).

### 4. Kirim input (keyboard + mouse)
```bash
WID=$(xdotool search --name "FreeRDP" | head -1)
xdotool key --window "$WID" ctrl+alt+t            # kombinasi tombol
xdotool type --window "$WID" --delay 40 'command' # ketik teks
xdotool key --window "$WID" Return                # enter
xdotool mousemove --window "$WID" X Y             # pindah mouse (relatif window)
xdotool click --window "$WID" 1                   # klik kiri; 2=mid,3=right
xdotool mousemove_relative 20 0                    # gerak relatif (scroll area)
```
Window freeerdp gak butuh WM untuk nerima input — `windowfocus` mungkin gagal ("no _NET_ACTIVE_WINDOW") tapi `xdotool key/type/click --window` tetap jalan.

### 5. Verifikasi input beneran nyampe (bukti end-to-end)
Cara TERPERCAYA (tanpa butuh vision model):
- Buka terminal (ctrl+alt+t) → ketik perintah yang efeknya bisa dicek dari luar → Enter:
  ```bash
  xdotool type --window "$WID" 'echo PROOF_$(date +%s) > /tmp/proof.txt'
  xdotool key --window "$WID" Return
  # lalu dari SSH ke VM:
  ssh <...> 'cat /tmp/proof.txt'
  ```
  Kalau file muncul = **keyboard control terbukti 100%** sampai shell remote.
- Mouse click: screenshot sebelum → klik → screenshot sesudah → hitung persen pixel berubah (2-35% = klik berhasil, mis. menu/panel terbuka).

## Pitfall utama (semua teruji)

1. **VM headless TANPA GPU → Xorg gagal.** Log: `Xvnc`-lah jawabannya, bukan Xorg:
   ```
   (EE) open /dev/dri/card0: No such file or directory
   (EE) No devices detected.  →  no screens found  → exit 1
   ```
   Fix: `apt-get install -y tigervnc-standalone-server` → `which Xvnc` → set sesi default xrdp:
   ```bash
   sed -i 's/^autorun=.*/autorun=Xvnc/' /etc/xrdp/xrdp.ini
   systemctl restart xrdp
   ```
2. **`startwm.sh` harus FOREGROUND**, bukan `startxfce4 &` + `exit 0`. Kalau background+exit, sesman kira WM langsung mati → sesi terminate (log: `Window manager exited quickly (N secs)`). Tulisan benar:
   ```bash
   #!/bin/sh
   [ -r /etc/profile ] && . /etc/profile
   [ -r ~/.profile ] && . ~/.profile
   startxfce4            # FOREGROUND, tanpa &, tanpa exit
   ```
   Fix via SSH langsung: `cat > /etc/xrdp/startwm.sh <<EOF ... EOF`.
3. **Screenshot hitam padahal session jalan:** tunggu 15s+ setelah connect; RDP negotiate dulu baru render. Kalau tetap hitam cek `journalctl`/`/var/log/xrdp-sesman.log` di VM: `No X server active` = Xorg died (pitfall 1); `exited quickly` = startwm (pitfall 2).
4. **Vision model bisa down** (`No active credentials for provider`). Jangan ketergantungan — pakai bukti fungsional (kirim perintah → verifikasi file/efek dari SSH) + diff screenshot.
5. **Apt error "Couldn't create temporary file /tmp/apt.conf.X"** di host (env terlindung): `export TMPDIR=/var/tmp` dulu sebelum `apt-get`.
6. **Repo pihak ketiga (docker/google/nodesource) nge-block `apt-get update`** → matikan file `.sources`/`.list` dulu (mv `.disabled`), lalu update.
7. **Ipv4-only host ke VM IPv6-only:** tunnel SSH adalah dua arah jalan (auto-forward via proxy). RDP langsung ke IPv6 publik gagal (`Network is unreachable`).

## Verification checklist

```bash
# 1. Tunnel
ss -tlnp | grep 13389 && echo tunnel-OK
# 2. Window FreeRDP
xdotool search --name "FreeRDP" | head -1 || echo NO-WINDOW
# 3. GUI render
convert /tmp/s.png -format '%[fx:mean]' info:   # >0.05
# 4. Keyboard (bukti fungsional)
ssh <vm> 'test -f /tmp/proof.txt && echo KEYBOARD-PROOF-OK'
# 5. Mouse (diff screenshot)
python3 - <<'EOF'
from PIL import Image, ImageChops; import numpy as np
a=np.array(Image.open('a.png').convert('L')); b=np.array(Image.open('b.png').convert('L'))
print(f"changed={(np.abs(a.astype(int)-b)>10).sum()/a.size*100:.2f}%")
EOF
```

## Catatan

- Script tunnel & launcher buat VM Freestyle `rena` ada di `/root/freestyle-check/` (`tunnel-rena.sh`, `mint-tunnel-token.mjs`).
- Sesi Idle → VM Freestyle auto-pause → RDP putus; `freestyle vm start` buat resume.
- RDP login butuh password root di VM (default Ubuntu root gak punya) — `echo 'root:TAU' | chpasswd`. `PermitRootLogin prohibit-password` cuma memengaruhi SSH, xrdp tetap jalan.
