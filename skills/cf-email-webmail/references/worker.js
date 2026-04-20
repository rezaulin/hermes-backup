// ============================================
// SIMPLE WEBMAIL WORKER
// Cloudflare Workers + D1 + Email Routing
// ============================================

export default {
  // Handle incoming emails (Cloudflare Email Routing)
  async email(message, env, ctx) {
    const to = message.to;
    const from = message.from;
    const subject = message.headers.get('subject') || '(no subject)';

    // Read raw email from stream
    const reader = message.raw.getReader();
    const chunks = [];
    while (true) {
      const { done, value } = await reader.read();
      if (done) break;
      chunks.push(value);
    }
    const rawBytes = new Uint8Array(chunks.reduce((acc, c) => acc + c.length, 0));
    let offset = 0;
    for (const chunk of chunks) {
      rawBytes.set(chunk, offset);
      offset += chunk.length;
    }
    const rawText = new TextDecoder().decode(rawBytes);

    // Extract body
    let bodyText = '';
    let bodyHtml = '';
    try {
      const parsed = parseEmailBody(rawText);
      bodyText = parsed.text;
      bodyHtml = parsed.html;
    } catch (e) {
      bodyText = rawText.slice(0, 5000);
    }

    // Save to D1
    await env.DB.prepare(
      `INSERT INTO emails (to_addr, from_addr, subject, body_text, body_html, raw_email)
       VALUES (?, ?, ?, ?, ?, ?)`
    ).bind(to, from, subject, bodyText || '', bodyHtml || '', rawText.slice(0, 50000)).run();
  },

  // Handle HTTP requests (web UI + API)
  async fetch(request, env, ctx) {
    const url = new URL(request.url);
    const path = url.pathname;

    // CORS preflight
    if (request.method === 'OPTIONS') {
      return new Response(null, {
        headers: {
          'Access-Control-Allow-Origin': '*',
          'Access-Control-Allow-Methods': 'GET, POST, OPTIONS',
          'Access-Control-Allow-Headers': 'Content-Type, Authorization'
        }
      });
    }

    // API routes
    if (path === '/api/login' && request.method === 'POST') return handleLogin(request, env);
    if (path === '/api/inbox') return handleInbox(request, env);
    if (path === '/api/email') return handleEmailDetail(request, env);
    if (path === '/api/delete' && request.method === 'POST') return handleDelete(request, env);

    // Serve web UI
    return new Response(HTML, {
      headers: { 'content-type': 'text/html; charset=utf-8' }
    });
  }
};

// ===== API HANDLERS =====

async function handleLogin(request, env) {
  const { email, password } = await request.json();

  // Must be @reviewtechno.me domain (customize per deployment)
  if (!email.endsWith('@reviewtechno.me')) {
    return json({ error: 'Hanya email @reviewtechno.me' }, 401);
  }

  // Check if user exists
  let user = await env.DB.prepare('SELECT * FROM users WHERE email = ?').bind(email).first();

  // Auto-create if not exists
  if (!user) {
    await env.DB.prepare('INSERT INTO users (email, password) VALUES (?, ?)').bind(email, password).run();
    user = { email, password };
  }

  // Verify password
  if (user.password !== password) {
    return json({ error: 'Password salah' }, 401);
  }

  const token = btoa(`${email}:${password}`);
  return json({ token, email });
}

async function handleInbox(request, env) {
  const auth = checkAuth(request);
  if (!auth) return json({ error: 'Unauthorized' }, 401);

  const url = new URL(request.url);
  const page = parseInt(url.searchParams.get('page') || '1');
  const limit = 20;
  const offset = (page - 1) * limit;

  const emails = await env.DB.prepare(
    `SELECT id, to_addr, from_addr, subject, created_at
     FROM emails WHERE to_addr = ?
     ORDER BY created_at DESC LIMIT ? OFFSET ?`
  ).bind(auth.email, limit, offset).all();

  const count = await env.DB.prepare('SELECT COUNT(*) as total FROM emails WHERE to_addr = ?').bind(auth.email).first();

  return json({ emails: emails.results, total: count.total, page, pages: Math.ceil(count.total / limit) });
}

async function handleEmailDetail(request, env) {
  const auth = checkAuth(request);
  if (!auth) return json({ error: 'Unauthorized' }, 401);

  const url = new URL(request.url);
  const id = url.searchParams.get('id');
  if (!id) return json({ error: 'Missing id' }, 400);

  const email = await env.DB.prepare('SELECT * FROM emails WHERE id = ? AND to_addr = ?').bind(id, auth.email).first();
  if (!email) return json({ error: 'Not found' }, 404);

  return json(email);
}

async function handleDelete(request, env) {
  const auth = checkAuth(request);
  if (!auth) return json({ error: 'Unauthorized' }, 401);

  const { id } = await request.json();
  await env.DB.prepare('DELETE FROM emails WHERE id = ? AND to_addr = ?').bind(id, auth.email).run();
  return json({ ok: true });
}

// ===== HELPERS =====

function checkAuth(request) {
  const authHeader = request.headers.get('Authorization');
  if (!authHeader || !authHeader.startsWith('Basic ')) return null;
  try {
    const decoded = atob(authHeader.slice(6));
    const [email, password] = decoded.split(':');
    if (!email || !password) return null;
    return { email, password };
  } catch { return null; }
}

function json(data, status = 200) {
  return new Response(JSON.stringify(data), {
    status,
    headers: { 'content-type': 'application/json', 'access-control-allow-origin': '*' }
  });
}

// ===== EMAIL PARSER =====

function parseEmailBody(rawEmail) {
  let text = '', html = '';
  const headerEnd = rawEmail.indexOf('\r\n\r\n');
  const bodyStart = headerEnd >= 0 ? headerEnd + 4 : (rawEmail.indexOf('\n\n') >= 0 ? rawEmail.indexOf('\n\n') + 2 : 0);
  if (bodyStart <= 1) return { text: rawEmail.slice(0, 5000), html: '' };

  const headers = rawEmail.slice(0, bodyStart);
  const body = rawEmail.slice(bodyStart);
  const boundaryMatch = headers.match(/boundary="?([^";\s\r\n]+)"?/i);
  const contentType = headers.match(/content-type:\s*([^\s;]+)/i);

  if (boundaryMatch) {
    const parts = body.split('--' + boundaryMatch[1]);
    for (const part of parts) {
      if (part.trim() === '' || part.trim() === '--' || part.trim().startsWith('--')) continue;
      const pHeaderEnd = part.indexOf('\r\n\r\n');
      const pBodyStart = pHeaderEnd >= 0 ? pHeaderEnd + 4 : (part.indexOf('\n\n') >= 0 ? part.indexOf('\n\n') + 2 : 0);
      if (pBodyStart <= 1) continue;
      const pHeaders = part.slice(0, pBodyStart);
      let pBody = part.slice(pBodyStart).replace(/--\s*$/, '').trim();
      const pType = pHeaders.match(/content-type:\s*([^\s;]+)/i);
      const pEnc = pHeaders.match(/content-transfer-encoding:\s*(\S+)/i);
      if (pEnc && /base64/i.test(pEnc[1])) { try { pBody = atob(pBody.replace(/\s/g, '')); } catch (e) {} }
      if (pEnc && /quoted-printable/i.test(pEnc[1])) {
        pBody = pBody.replace(/=\r?\n/g, '').replace(/=([0-9A-Fa-f]{2})/g, (_, h) => String.fromCharCode(parseInt(h, 16)));
      }
      if (pType) {
        const t = pType[1].toLowerCase();
        if (t === 'text/plain' && !text) text = pBody;
        else if (t === 'text/html' && !html) html = pBody;
      }
    }
  } else {
    const enc = headers.match(/content-transfer-encoding:\s*(\S+)/i);
    let decoded = body.trim();
    if (enc && /base64/i.test(enc[1])) { try { decoded = atob(decoded.replace(/\s/g, '')); } catch (e) {} }
    if (enc && /quoted-printable/i.test(enc[1])) {
      decoded = decoded.replace(/=\r?\n/g, '').replace(/=([0-9A-Fa-f]{2})/g, (_, h) => String.fromCharCode(parseInt(h, 16)));
    }
    const type = contentType ? contentType[1].toLowerCase() : 'text/plain';
    if (type === 'text/html') html = decoded; else text = decoded;
  }
  return { text: text.trim().slice(0, 10000), html: html.trim().slice(0, 50000) };
}

// ===== HTML UI =====
// (See SKILL.md for full HTML — includes login, inbox list, email detail with
//  auto-extract verification codes, HTML preview, auto-refresh every 15s)
const HTML = `<!DOCTYPE html>
<html lang="id">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Webmail</title>
  <style>
    * { margin: 0; padding: 0; box-sizing: border-box; }
    body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; background: #0f0f1a; color: #e0e0e0; min-height: 100vh; }
    .login-wrap { display: flex; align-items: center; justify-content: center; min-height: 100vh; padding: 1rem; }
    .login-box { background: #1a1a2e; border: 1px solid #2a2a4a; border-radius: 16px; padding: 2rem; width: 100%; max-width: 380px; }
    .login-box h1 { text-align: center; margin-bottom: 1.5rem; font-size: 1.5rem; }
    .login-box input { width: 100%; padding: 0.8rem 1rem; background: #12121f; border: 1px solid #2a2a4a; border-radius: 8px; color: #e0e0e0; font-size: 0.95rem; margin-bottom: 0.8rem; }
    .login-box button { width: 100%; padding: 0.8rem; background: #6c63ff; color: #fff; border: none; border-radius: 8px; font-size: 1rem; cursor: pointer; font-weight: 600; }
    .app { display: none; } .app.active { display: block; }
    .header { background: #1a1a2e; border-bottom: 1px solid #2a2a4a; padding: 1rem 1.5rem; display: flex; justify-content: space-between; align-items: center; position: sticky; top: 0; z-index: 10; }
    .email-list { max-width: 900px; margin: 0 auto; padding: 0.5rem; }
    .email-item { display: flex; align-items: center; padding: 1rem 1.2rem; border-bottom: 1px solid #1f1f35; cursor: pointer; gap: 1rem; }
    .email-item:hover { background: #1a1a2e; }
    .email-from { font-weight: 600; font-size: 0.9rem; min-width: 140px; }
    .email-subject { flex: 1; font-size: 0.85rem; color: #aaa; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
    .email-date { font-size: 0.75rem; color: #666; }
    .detail-overlay { display: none; position: fixed; inset: 0; background: rgba(0,0,0,0.7); z-index: 50; justify-content: center; padding: 2rem; overflow-y: auto; }
    .detail-overlay.active { display: flex; }
    .detail-box { background: #1a1a2e; border: 1px solid #2a2a4a; border-radius: 16px; padding: 2rem; width: 100%; max-width: 700px; margin-top: 2rem; position: relative; }
    .code-extract { background: #6c63ff22; border: 1px solid #6c63ff; border-radius: 8px; padding: 1rem; margin-bottom: 1rem; font-size: 1.2rem; text-align: center; font-family: monospace; letter-spacing: 4px; cursor: pointer; }
  </style>
</head>
<body>
  <div class="login-wrap" id="loginPage">
    <div class="login-box">
      <h1><span>📬</span> Webmail</h1>
      <div id="loginError" style="color:#ff6b6b;text-align:center;margin-bottom:0.8rem;font-size:0.85rem;"></div>
      <input type="email" id="loginEmail" placeholder="nama@reviewtechno.me" autofocus>
      <input type="password" id="loginPass" placeholder="Password">
      <button onclick="doLogin()">Login</button>
    </div>
  </div>
  <div class="app" id="app">
    <div class="header">
      <h1><span>📬</span> Inbox — <span id="userEmail"></span></h1>
      <div><button onclick="loadInbox()" style="background:#6c63ff;border:none;color:#fff;padding:0.4rem 0.8rem;border-radius:6px;cursor:pointer;">🔄</button> <button onclick="logout()" style="background:none;border:1px solid #2a2a4a;color:#888;padding:0.4rem 0.8rem;border-radius:6px;cursor:pointer;">Logout</button></div>
    </div>
    <div class="email-list" id="emailList"></div>
  </div>
  <div class="detail-overlay" id="detailOverlay" onclick="if(event.target===this)closeDetail()">
    <div class="detail-box">
      <button onclick="closeDetail()" style="position:absolute;top:1rem;right:1rem;background:none;border:none;color:#888;font-size:1.5rem;cursor:pointer;">×</button>
      <div id="detailMeta"></div>
      <div class="code-extract" id="codeExtract" style="display:none" onclick="navigator.clipboard.writeText(this.textContent);this.style.borderColor='#2ecc71'"></div>
      <div id="detailBody" style="max-height:60vh;overflow-y:auto;"></div>
    </div>
  </div>
<script>
let token=localStorage.getItem('wm_token'),currentEmail=localStorage.getItem('wm_email');
if(token)showApp();
async function doLogin(){const e=document.getElementById('loginEmail').value.trim(),p=document.getElementById('loginPass').value;if(!e||!p)return;const r=await fetch('/api/login',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({email:e,password:p})});const d=await r.json();if(d.error){document.getElementById('loginError').textContent=d.error;return;}token=d.token;currentEmail=d.email;localStorage.setItem('wm_token',token);localStorage.setItem('wm_email',currentEmail);showApp();}
function logout(){token=null;currentEmail=null;localStorage.removeItem('wm_token');localStorage.removeItem('wm_email');document.getElementById('app').classList.remove('active');document.getElementById('loginPage').style.display='flex';}
function showApp(){document.getElementById('loginPage').style.display='none';document.getElementById('app').classList.add('active');document.getElementById('userEmail').textContent=currentEmail;loadInbox();}
async function loadInbox(page=1){const r=await fetch('/api/inbox?page='+page,{headers:{'Authorization':'Basic '+token}});const d=await r.json();if(d.error){logout();return;}const list=document.getElementById('emailList');if(!d.emails.length){list.innerHTML='<div style="text-align:center;padding:3rem;color:#555;">📭 Inbox kosong</div>';return;}list.innerHTML=d.emails.map(e=>{const dt=new Date(e.created_at+'Z');return '<div class="email-item" onclick="openEmail('+e.id+')"><div class="email-from">'+esc(e.from_addr||'?')+'</div><div class="email-subject">'+esc(e.subject||'(no subject)')+'</div><div class="email-date">'+dt.toLocaleString('id-ID',{day:'2-digit',month:'short',hour:'2-digit',minute:'2-digit'})+'</div></div>';}).join('');}
async function openEmail(id){const r=await fetch('/api/email?id='+id,{headers:{'Authorization':'Basic '+token}});const d=await r.json();if(d.error)return;const dt=new Date(d.created_at+'Z');document.getElementById('detailMeta').innerHTML='<div><b>Dari:</b> '+esc(d.from_addr)+'</div><div><b>Subjek:</b> '+esc(d.subject)+'</div><div><b>Waktu:</b> '+dt.toLocaleString('id-ID')+'</div>';const ce=document.getElementById('codeExtract');const m=(d.body_text||'').match(/\b(\d{4,8})\b/);if(m){ce.textContent=m[1];ce.style.display='block';}else{ce.style.display='none';}document.getElementById('detailBody').innerHTML='<pre style="white-space:pre-wrap;">'+esc(d.body_text||'(empty)')+'</pre>';document.getElementById('detailOverlay').classList.add('active');}
function closeDetail(){document.getElementById('detailOverlay').classList.remove('active');}
function esc(s){const d=document.createElement('div');d.textContent=s||'';return d.innerHTML;}
setInterval(()=>{if(token&&!document.getElementById('detailOverlay').classList.contains('active'))loadInbox();},15000);
document.getElementById('loginPass').addEventListener('keydown',e=>{if(e.key==='Enter')doLogin();});
</script>
</body>
</html>`;
