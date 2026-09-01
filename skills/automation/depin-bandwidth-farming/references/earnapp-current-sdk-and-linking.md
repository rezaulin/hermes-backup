# EarnApp Node SDK: current version, install flow, linking, cert fix — verified 2026-08-30

The old images (`fazalfarhan01/earnapp:lite` etc.) ship **SDK v1.294.218 (2022)** which is now **BROKEN**:
- Its hardcoded `restricted_domain` allowlist only has old AWS us-east-1 IPs. The backend now resolves `proxyjs.luminatinet.com` / `proxyjs.lum-sdk.io` to AWS **Global Accelerator** IPs (`15.197.193.114`, `3.33.193.183`) that are NOT in the old allowlist → `ERR: restricted_domain: ... failed 15.197.193.114` → node never connects.
- Since the node never connects/registers, dashboard linking returns **"The device is not found"**. (It is NOT an Incus/container problem.)

## Use the OFFICIAL install.sh (current SDK = 1.651.510)

The official installer is the source of truth and pulls the current build:

```bash
wget -qO- https://brightdata.com/static/earnapp/install.sh > /tmp/earnapp.sh
echo yes | bash /tmp/earnapp.sh     # 'yes' auto-accepts terms
```

Details learned from reading install.sh:
- Downloads from `https://cdn-earnapp.b-cdn.net/static/<PRODUCT><SSL_SUFFIX>-x64-<VERSION>`
- `PRODUCT=earnapp`, `VERSION="1.651.510"` (as of 2026-08-30), `SSL_SUFFIX=-ssl3` when openssl 3.x
- Direct URL: `https://cdn-earnapp.b-cdn.net/static/earnapp-ssl3-x64-1.651.510`
- It runs `earnapp finish_install` (a hidden subcommand) which creates systemd services, registers the device, and **prints the `/r/<uuid>` link**. This is the register step — running bare `earnapp start` is NOT enough.

`earnapp` is actually a **packaged Node.js binary** (installer.js). Subcommands: `start`, `stop`, `status`, `register`, `showid`, `uninstall`, plus hidden `install` / `finish_install`.

## Critical: Node SDK self-signed cert failure (register/connect)

Even with current SDK, `finish_install` / connection fails with:
```
AxiosError: self-signed certificate in certificate chain  (code SELF_SIGNED_CERT_IN_CHAIN)
Failed registration: check internet connection and try again
```
Root cause: the SDK's bundled CA store is missing the **SSL.com intermediate / root**. `curl -v` to the same endpoint verifies fine (system ca-certificates has `SSL.com_*`), but the Node VM used by the SDK does not. **Fix:**
```bash
export NODE_EXTRA_CA_CERTS=/etc/ssl/certs/ca-certificates.crt
```
With that env set, `earnapp finish_install` → `✔ Registered` → prints the link. Without it → cert error → device never registers → `/r/` says "device not found".

## Linking (account uses Google SSO)

- Login is Google-SSO only — no password can be entered in CLI. That's fine: the device link is **browser-side**, not CLI.
- Flow: device must successfully `Register` (via `finish_install` with `NODE_EXTRA_CA_CERTS` set, or manually + node connected) → THEN open `https://earnapp.com/r/<uuid>` in a browser **already logged into the EarnApp account** (Google SSO).
- The old claim "1 akun cukup, node di-link via UUID link" still holds, but the node must reach `perr_connected` first. Grep the SDK log for `perr_connected_<ver>.sent` (a marker file written to `/etc/earnapp/`) to prove it connected. Newer SDK writes binary/obfuscated `brd_sdk3.log` — use the `perr_*.sent` marker files instead as the health signal.
- `is_ip_blocked?uuid=` returning `{"ip_blocked":false}` does NOT mean registered/linkable — it never did.

## Headless multi-device: per-container flow that WORKS

For an Incus/container farm, per device:
1. Push official 1.651.510 binary (`/usr/bin/earnapp`).
2. Write unique UUID: `printf 'sdk-node-<32hex>' > /etc/earnapp/uuid`
3. `export NODE_EXTRA_CA_CERTS=/etc/ssl/certs/ca-certificates.crt` (MUST be set in the process env that runs `earnapp`).
4. `earnapp finish_install` → should print `✔ Registered` + the link URL.
5. Open each `/r/<uuid>` in the logged-in (Google SSO) browser to bind to account.
