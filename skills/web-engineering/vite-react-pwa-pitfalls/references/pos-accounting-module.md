# POS Accounting Module — Double-Entry (PSAK Standard)

Modul akuntansi untuk Omni POS yang generate jurnal otomatis dari transaksi, deposit, kasbon, dan stock adjustment.

## Arsitektur

### Data Model
- **Account** (`types/accounting.ts`): Chart of Accounts (COA) standar PSAK
  - `id` = `code` (stabil untuk referensi, e.g. "1110", "4100")
  - `type`: asset | liability | equity | revenue | expense
  - `normalBalance`: debit | credit
  - `parentId`: hierarki (e.g. 1110 Kas → parent 1100 Aset Lancar)
  - `isCash`, `isBank`: flag untuk cash flow statement
  
- **JournalEntry** (`types/accounting.ts`): Jurnal double-entry
  - `number`: "JRN-YYYYMMDD-NNNN" (auto-generated)
  - `date`: ISO date string
  - `type`: auto | manual | adjustment | closing | opening
  - `lines[]`: array of { accountId, accountCode, accountName, debit, credit }
  - `totalDebit`, `totalCredit`: HARUS sama (balanced)
  - `referenceType`, `referenceId`: link ke transaksi/customer/etc

- **JournalLine**: per-baris entry
  - `accountId`, `accountCode`, `accountName` (denormalized untuk speed)
  - `debit`, `credit`: salah satu harus 0, tidak boleh dua-duanya > 0
  - `description`: opsional

- **PeriodClose** (`types/accounting.ts`): Tracking period closure
  - `id`: UUID
  - `period`: "YYYY-MM" format
  - `closedAt`: timestamp
  - `closedBy`: user email
  - `totalRevenue`, `totalExpenses`: summary untuk periode
  - `netIncome`: profit/loss
  - `totalDebit`, `totalCredit`: harus balance
  - `isActive`: status aktif/tidak

### Default COA (46 akun)
Tersimpan di `lib/accounting/coa.ts` sebagai `DEFAULT_COA`. Struktur:
- **1xxx Aset**: Kas (1110), Bank (1120), Piutang (1130), Persediaan (1140), Peralatan (1210), Kendaraan (1220)
- **2xxx Utang**: Utang Usaha (2110), Utang Pajak (2120), PPN Keluaran (2121), PPN Masukan (2122), Deposit Pelanggan (2130)
- **3xxx Modal**: Modal Pemilik (3100), Prive (3200), Laba Ditahan (3300), Laba Berjalan (3400)
- **4xxx Pendapatan**: Penjualan (4100), Diskon Penjualan (4110), Retur (4120)
- **5xxx HPP**: Harga Pokok Penjualan (5100), Beban Pengiriman (5200)
- **6xxx Beban Ops**: Gaji (6100), Sewa (6200), Listrik (6300), Penyusutan (6400)
- **7xxx Pendapatan Lain**: Bunga (7100)
- **8xxx Beban Lain**: Bunga (8100), Selisih Stok (8200)

Seed function: `seedDefaultCOA()` — pakai `account.id = account.code` (bukan UUID) untuk stabilitas referensi.

### Auto-Journal Logic

**Transaksi penjualan (checkout):**
```
D Kas/Bank/Piutang    = total per payment method
K Penjualan           = subtotal
D Diskon Penjualan    = itemDiscount + globalDiscount (jika > 0)
K PPN Keluaran        = tax (jika > 0)
```

**HPP (setelah transaksi):**
```
D HPP                 = sum(costPrice * baseQty) per item
K Persediaan          = same amount
```

**Deposit topup:**
```
D Kas                 = amount
K Deposit Pelanggan   = amount
```

**Pembayaran kasbon:**
```
D Kas                 = amount
K Piutang Usaha       = amount
```

**Mapping payment method → account:**
- cash → 1110 (Kas)
- qris/card/transfer → 1120 (Bank)
- kasbon → 1130 (Piutang Usaha)
- deposit → 2130 (Deposit Pelanggan)

### Financial Reports (`lib/accounting/reports.ts`)
- **AccountLedger** (Buku Besar): per-akun, running balance, filter periode
- **TrialBalance** (Neraca Saldo): semua akun + total debit/credit, validasi balanced
- **IncomeStatement** (Laba Rugi): revenue - COGS = gross profit - operating expenses = operating income ± other = net income
- **BalanceSheet** (Neraca): assets = liabilities + equity
- **CashFlowStatement** (Arus Kas): operating + investing + financing = net change

## Period Closing (`lib/accounting/periodClosing.ts`)

Fitur untuk menutup periode akuntansi (biasanya bulanan) dan mencegah perubahan data historis.

### Flow Period Closing
1. User pilih periode (YYYY-MM)
2. Validasi belum ada closing journal untuk periode itu
3. Generate closing journal entries:
   - Close semua revenue accounts (debit revenue, credit income summary)
   - Close semua expense accounts (credit expense, debit income summary)
   - Transfer net income ke Laba Ditahan (3300)
4. Simpan PeriodClose record dengan summary (revenue, expenses, net income)
5. Lock periode (prevent new journals di masa lalu)

### Implementation Pattern
```typescript
// Check if period is closed
export async function isPeriodClosed(period: string): Promise<boolean>

// Close period with closing journals
export async function closePeriod(
  period: string,
  closedBy: string,
  notes?: string
): Promise<PeriodClose>

// Reopen closed period (with audit trail)
export async function reopenPeriod(
  period: string,
  reopenedBy: string,
  reason: string
): Promise<void>

// Get all period closes
export async function getAllPeriodCloses(): Promise<PeriodClose[]>
```

### UI Pattern (PeriodClosingPage.tsx)
- Card-based period selection (12 bulan terakhir)
- Green badge untuk periode yang sudah ditutup
- Confirmation dialog dengan warning
- History table dengan details (revenue, expenses, net income, closed by)

### Pitfalls
- **Period format**: Selalu pakai "YYYY-MM" (bukan "YYYYMM") untuk konsistensi dengan date parsing
- **Closing journal detection**: Cek existence dengan query `where('number', '==', 'CLOSING-' + period)`
- **Reopening**: Harus delete closing journals DULU sebelum hapus PeriodClose record
- **Audit trail**: Simpan reason untuk reopening (required field)

## Manual Journal (`lib/accounting/journal.ts`)

Fitur untuk input jurnal manual (penyesuaian, koreksi, dll).

### Features
- Dynamic form dengan multiple debit/credit lines
- Real-time balance validation (total debit = total credit)
- Journal number auto-generation: "MJ-YYYYMMDD-NNNN"
- Period locking integration (tidak bisa create di closed period)
- History view dalam modal

### Implementation Pattern
```typescript
// Create manual journal
export async function createManualJournal(data: {
  date: string
  description: string
  lines: Array<{
    accountId: string
    debit: number
    credit: number
    description?: string
  }>
  createdBy: string
}): Promise<JournalEntry>

// Validation rules:
// 1. Minimal 2 lines (1 debit, 1 credit)
// 2. Total debit MUST equal total credit
// 3. Each line must have either debit OR credit (not both, not neither)
// 4. Cannot create in closed period
```

### UI Pattern (ManualJournalPage.tsx)
```tsx
// Dynamic lines dengan add/remove
const [lines, setLines] = useState([
  { accountId: '', debit: 0, credit: 0 },
  { accountId: '', debit: 0, credit: 0 }
])

// Real-time validation
const totalDebit = lines.reduce((sum, l) => sum + l.debit, 0)
const totalCredit = lines.reduce((sum, l) => sum + l.credit, 0)
const isBalanced = Math.abs(totalDebit - totalCredit) < 0.01

// Account selector dengan search
<Select>
  {accounts.map(acc => (
    <option value={acc.id}>
      {acc.code} - {acc.name}
    </option>
  ))}
</Select>
```

### Pitfalls
- **Balance validation**: Gunakan tolerance 0.01 untuk floating point comparison
- **Minimum lines**: Enforce minimal 2 lines (tidak bisa delete kalau cuma 2)
- **Period check**: Validasi `isDateInClosedPeriod(date)` SEBELUM create
- **Journal number prefix**: Pakai "MJ-" untuk manual journal (beda dari "JRN-" auto journal)

## File Structure
```
src/
├── types/accounting.ts          # Account, JournalEntry, JournalLine, PeriodClose types
├── lib/accounting/
│   ├── coa.ts                   # DEFAULT_COA, seedDefaultCOA, getAccounts, CRUD
│   ├── journal.ts               # createJournalEntry, createManualJournal, auto-journal functions
│   ├── periodClosing.ts         # closePeriod, reopenPeriod, isPeriodClosed
│   └── reports.ts               # getAccountLedger, getTrialBalance, getIncomeStatement, etc.
├── features/accounting/
│   ├── JournalListPage.tsx      # List jurnal + filter tanggal + detail dialog
│   ├── COAManagementPage.tsx    # CRUD akun + tree view hierarki
│   ├── PeriodClosingPage.tsx    # Period closing UI + history
│   ├── ManualJournalPage.tsx    # Manual journal form + validation
│   └── FinancialReportsPage.tsx # Laporan keuangan (4 tabs)
├── hooks/useAccounting.ts       # useJournalEntries, useJournalsByReference
└── App.tsx                      # Routes: /accounting/*
```

## IndexedDB Schema (Dexie)
```ts
accounts: 'id, code, type, parentId, isActive'
journalEntries: 'id, number, date, type, postedAt, createdAt'
periodCloses: 'id, period, closedAt'
```

## Permissions
- Permission: `'accounting'`
- Role: owner only (di `lib/permissions.ts`)
- Routes di-guard dengan `<RequirePermission perm="accounting">`

## Routes
```typescript
/accounting/coa              // Chart of Accounts management
/accounting/journals         // Journal entries list
/accounting/period-closing   // Period closing UI
/accounting/manual-journal   // Manual journal entry
/accounting/reports          // Financial reports (4 tabs)
```

## Urutan Implementasi (Pattern Reusable)

Saat menambah **modul fitur baru** ke codebase Omni POS:

1. **Types** (`types/namaFitur.ts`) — definisi interface/type
2. **IndexedDB schema** (`lib/indexeddb.ts`) — tambah table di Dexie + index
3. **Library functions** (`lib/namaFitur/`) — business logic + dual-path demo/Firestore
4. **Seed data** (opsional) — `seedDefaultX()` untuk data awal
5. **Integration** — panggil dari existing flows (checkout, etc.)
6. **Hooks** (`hooks/useX.ts`) — React Query wrappers
7. **UI Pages** (`features/namaFitur/`) — halaman + komponen
8. **Routes** (`App.tsx`) — tambah route + permission guard
9. **Permissions** (`lib/permissions.ts`) — tambah permission type + role mapping
10. **Build check** — `npm run build` wajib zero error

## Pitfalls Spesifik

### Dialog component tidak punya prop `title`
`Dialog` di project ini pakai pattern `<Dialog>{children}</Dialog>` tanpa prop `title`. Untuk header judul, pakai children biasa:
```tsx
<Dialog open={open} onClose={onClose}>
  <div className="p-6">
    <h2 className="text-xl font-bold mb-4">Judul</h2>
    {/* content */}
  </div>
</Dialog>
```

### TypeScript `as Type` gagal dengan `deletedAt: null` vs `deletedAt?: number`
Saat create record baru, jangan set `deletedAt: null` karena type expect `number | undefined`:
```ts
// SALAH
const accountData = { ...data, deletedAt: null }
const account = { id: data.code, ...accountData } as Account  // TS error!

// BENAR
const accountData = { ...data }  // omit deletedAt
const account = { id: data.code, ...accountData } as Account  // OK
```

### setDoc tidak return doc ref seperti addDoc
```ts
// SALAH — setDoc return void, bukan DocumentReference
const docRef = await setDoc(doc(firestore, 'accounts', id), data)

// BENAR — langsung await tanpa assign
await setDoc(doc(firestore, 'accounts', id), data)
```

### useMutation type inference lemah untuk complex signatures
Kalau mutation function punya parameter kompleks, wrap dengan explicit arrow function:
```ts
// KURANG — type inference bisa gagal
const mutation = useMutation({ mutationFn: updateAccount })

// LEBIH BAIK — explicit type
const mutation = useMutation({
  mutationFn: (data: any) => updateAccount(data.code, data)
})
```

### Property name mismatch (parentId vs parentCode)
Type `Account` pakai `parentId`, tapi UI code kadang salah tulis `parentCode`. Selalu cek type definition dulu, jangan asumsi nama property.

### JournalEntry pakai `number` bukan `journalNumber`
Property di type `JournalEntry` adalah `number`, bukan `journalNumber`. Konsisten dengan `Transaction.number`.

### Card component tidak support onClick prop
`Card` component di project ini tidak menerima `onClick` prop. Kalau butuh clickable card, wrap dengan `<div>`:
```tsx
// SALAH
<Card onClick={handleClick}>...</Card>

// BENAR
<div onClick={handleClick} className="cursor-pointer">
  <Card>...</Card>
</div>
```

### Unused imports bikin build fail
TypeScript strict mode akan fail kalau ada unused imports. Selalu hapus import yang tidak dipakai:
```ts
// Sebelum build, cek dan hapus:
// - import yang tidak dipakai di code
// - variable yang di-declare tapi tidak dipakai
// - parameter function yang tidak dipakai (prefix dengan _)
```

### JSX structure harus balanced
Pastikan setiap opening tag punya closing tag yang match, terutama saat refactor Dialog content:
```tsx
// Cek indentation dan nesting
<Dialog>
  <div className="p-6">
    <h2>Title</h2>
    <div className="content">
      {/* content here */}
    </div>  {/* ← jangan lupa close */}
  </div>  {/* ← jangan lupa close */}
</Dialog>
```
