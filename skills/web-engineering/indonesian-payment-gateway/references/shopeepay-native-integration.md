# ShopeePay Partner — native Go integration spec (proven 2026-08 in Digital Sekolah)

Working implementation: `/home/ubuntu/smart-lms/backend/internal/shopeepay/` (repo rezaulin/digitalsekolah). All of the below was exercised against the REAL ShopeePay API with a test token.

## Token acquisition (tenant does this once, re-does on expiry)

partner.shopee.co.id → F12 → Network → Fetch/XHR → refresh transactions page → click `get-transaction-list` → Payload → `data.metadata.token` (starts `B:`). Session-bound: dies on logout/rotation → admin UI must support re-paste + show test status.

## API endpoints (POST, JSON body wrapped in `data`)

Base `https://shopeepay.shopee.co.id`, required headers: `Origin: https://partner.shopee.co.id`, `Referer: https://partner.shopee.co.id/`, `X-Timestamp-Ms: <now-ms>`, browser User-Agent (rotate), Content-Type/Accept json. Timeout 20s.

1. `/merchant/v1/partner-web/get-transaction-list`
   Body: `{data:{metadata:{token,language:"id",timezone:"Asia/Jakarta"},pageSize:N,filter:{startTime:<epoch SEC>,endTime:<epoch SEC>,serviceList:[1,3]},sorter:{field:"createTime",order:"descend"}}}`
   Resp: `{code:0,msg,data:{list:[{transactionId,displayTransactionId,amount:"50.000",status:3,createTime:<epoch sec>}],next_position,totalNetSales}}`. code≠0 → `msg` (e.g. "invalid token, err "). status: 1 pending, 2 failed, **3 success**, 4 refunded, 5 expired.
2. `/merchant/v1/partner-web/get-transaction-detail`
   Body: `{data:{metadata:{token,...},order_sn:<displayTransactionId>}}` → `data.issuer` = source wallet ("OVO","DANA","BCA","SeaBank"...). Use displayTransactionId (or transactionId fallback).

`startTime`/`endTime` are epoch SECONDS — passing milliseconds silently produces garbage ranges (the audited gateway had exactly this bug: year-58609 dates in logs).

## Dynamic QRIS generation (EMVCo TLV, no provider needed)

```go
// Parse: walk string; tag=payload[i:i+2], len=atoi(payload[i+2:i+4]), value=next len chars
// Build: tag + %02d(len) + value concatenated
// Inject: drop tag 63; replace tag 54 with amount (or insert 54 right after 53 if absent)
// Final: body + "6304" + CRC16-CCITT(body)  [poly 0x1021, init 0xFFFF, uppercase hex, pad4]
```
Validate a tenant-pasted static QRIS before storing: must parse, contain tag 00, and its trailing 4 chars must equal CRC16 of the rest — catches bad copies early with a friendly error.

Amount matching: provider `amount` is a formatted string ("25.016") — strip `.` and `,` then compare to exact final (requested + unique code 1–99).

## QR rendering — local only

Go: `github.com/skip2/go-qrcode` → `qrcode.WriteFile(qrisString, qrcode.High, 350, path)` into `qris_codes/qr_<id>.png`, serve via authed endpoint, delete PNG on paid/expired. Never redirect buyers to api.qrserver.com (leaks QRIS content to a third party).

## Verification loop (backend, driven by frontend poll)

```
GET status per poll:
  pending && now > expiresAt → mark expired, delete PNG
  else query get-transaction-list [createdAt-10m, now], pageSize 50
    for tx: status==3 AND amount==AmountFinal AND createTime>=start
      AND ShopeeTXID not in DB (dedupe vs OTHER invoices) →
      BEGIN; INSERT pembayaran (metode qris, nominal=requested, NOT amount_final);
      recalcTagihan; COMMIT; link PaymentID; mark paid; notify lunas
```
Double dedupe is mandatory: provider txId unique-check in DB (survives restart) + amount uniqueness via random code. `NominalBayar` records the REQUESTED amount; the unique code is gateway noise, not revenue.

## Sandbox test recipe (no real merchant)

1. Build a valid static QRIS programmatically with the same BuildTLV+CRC16 (hand-crafted strings fail TLV validation — e.g. wrong length fields).
2. Save config with token `B:test` → `pg/test` must return `invalid token` from the REAL API (proves wiring; unreachable vs invalid distinguishes network vs auth failures).
3. `qris/create` works without a valid token (QRIS gen is local) → decode the returned PNG with pyzbar and assert tag 54 == amount_final. This is the end-to-end proof.
4. Cleanup: DELETE config + qris rows, rm PNGs, drop temp `tmp_genqris.go` helper.

## Tenant-facing setup copy (used in the admin UI accordion)

1. Daftar ShopeePay Partner (partner.shopee.co.id, KTP+usaha, gratis) → dapat QRIS statis merchant. Personal ShopeePay cannot: no static QRIS, no mutasi API.
2. Salin string QRIS statis (`000201...`).
3. Ambil token via DevTools (above).
4. Paste keduanya di form → Test Koneksi → aktifkan toggle.
5. Dana 100% masuk saldo ShopeePay merchant sekolah; token read-only (can't move funds); token bisa kedaluwarsa → paste ulang.
