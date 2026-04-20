---
name: simple-web-app
description: Build a zero-dependency-nonsense web app with Express + JSON file storage + JWT auth + single-file HTML frontend. Use when you need a working web app fast without database setup, native compilation, or build tools.
category: software-development
---

# Simple Web App (Express + JSON + JWT + SPA)

Build a complete web app in 3 files: `server.js`, `public/index.html`, `package.json`.

## When to Use

- Quick internal tools, admin panels, attendance apps
- User wants "something that just works" with `node server.js`
- No database server available or desired
- Native SQLite compilation fails (better-sqlite3 node-gyp issues)

## Dependencies (only 3)

```json
{
  "dependencies": {
    "express": "^4.18.2",
    "jsonwebtoken": "^9.0.2",
    "bcryptjs": "^2.4.3"
  }
}
```

No native compilation needed. `npm install` always works.

## Database Pattern: JSON File

Replace `better-sqlite3` with a simple JSON file helper:

```js
const DB_FILE = path.join(__dirname, 'data.json');

const db = {
  baca() {
    if (fs.existsSync(DB_FILE)) return JSON.parse(fs.readFileSync(DB_FILE, 'utf-8'));
    return { users: [], /* other tables */ };
  },
  simpan(data) { fs.writeFileSync(DB_FILE, JSON.stringify(data, null, 2)); },
  nextId(arr) { return arr.length ? Math.max(...arr.map(x => x.id)) + 1 : 1; },
};
```

## Auth Pattern: JWT + bcrypt

```js
// Login
const token = jwt.sign({ id, username, role, nama }, SECRET, { expiresIn: '24h' });

// Middleware
function auth(req, res, next) {
  const token = (req.headers.authorization || '').replace('Bearer ', '');
  if (!token) return res.status(401).json({ message: 'Login dulu' });
  try { req.user = jwt.verify(token, SECRET); next(); }
  catch { res.status(401).json({ message: 'Token invalid' }); }
}

function adminOnly(req, res, next) {
  if (req.user.role !== 'admin') return res.status(403).json({ message: 'Hanya admin' });
  next();
}
```

## Default Admin Seed

On first run, create default admin if not exists:

```js
let db = loadDB();
if (!db.users.find(u => u.username === 'admin')) {
  db.users.push({ id: 1, username: 'admin', password_hash: bcrypt.hashSync('admin123', 10), role: 'admin', nama: 'Administrator', created_at: new Date().toISOString() });
  saveDB(db);
}
```

## Frontend: Single HTML File

Put everything in `public/index.html`:
- Inline CSS (no build step)
- Inline JS (vanilla, no framework)
- SPA routing via showing/hiding divs
- `fetch()` calls with Bearer token header
- Mobile-friendly with responsive CSS

Key pattern for API calls:

```js
async function api(path, opts = {}) {
  const res = await fetch(path, {
    ...opts,
    headers: { 'Content-Type': 'application/json', 'Authorization': 'Bearer ' + token, ...(opts.headers || {}) }
  });
  if (res.status === 401) { logout(); return; }
  return res.json();
}
```

## Pitfalls

- **JSON file locking**: Not safe for concurrent writes. Fine for <100 users.
- **No data relations**: Use manual "joins" by looking up IDs in other arrays.
- **No migrations**: To change schema, delete data.json and restart.
- **Token in localStorage**: Acceptable for internal tools, not for public-facing apps with sensitive data.
- **Single HTML file size**: Can get large (20KB+). Still works fine, just keep it organized with comments.

## .gitignore

```
node_modules/
data.json
```

## Deployment

### Local / VPS
```bash
npm install
node server.js
# Or with pm2: pm2 start server.js --name app
```

### Quick Public Access (Cloudflare Tunnel)
Expose local server to internet instantly with HTTPS — no port opening, no config, no domain needed:

```bash
# Install cloudflared
curl -L https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64 -o /usr/local/bin/cloudflared
chmod +x /usr/local/bin/cloudflared

# Start quick tunnel (gives random *.trycloudflare.com URL)
cloudflared tunnel --url http://localhost:3000
```

Output gives a public HTTPS URL like: `https://adding-below-microwave-submitting.trycloudflare.com`

**Caveats:**
- URL changes every restart (it's a "quick" tunnel, not named)
- For permanent URL: create a named tunnel via Cloudflare dashboard
- Works great for demos, testing, showing client progress
- All CRUD/database works normally — tunnel is just a reverse proxy

### SQLite Pitfall (avoid)
`better-sqlite3` requires native compilation (node-gyp, python, build-essentials). On many VPS/sandboxes it fails. If you hit this:
- Don't waste time debugging node-gyp
- Switch immediately to JSON file storage (pattern above)
- Or use `sql.js` (SQLite compiled to WASM, no native deps) — but JSON file is simpler for most cases
