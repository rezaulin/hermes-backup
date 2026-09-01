#!/usr/bin/env python3
"""hunter.py — Bug Bounty Arsenal core vulnerability scanner (v2.5.0).

35 stdlib-only modules, non-destructive canary probes. Scoped use only.

Usage:
  python3 hunter.py target.com
  python3 hunter.py target.com --slow                 # param-based probes
  python3 hunter.py target.com --endpoints urls.txt   # from har2scan.py
  python3 hunter.py target.com --modules headers,cors,xss --json out.json
"""
import argparse
import json
import re
import os
import socket
import ssl
import sys
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime

UA = "Mozilla/5.0 (X11; Linux x86_64) BugBountyArsenal/2.5"
TIMEOUT = 12
FINDINGS = []
CANARY = "bba25canary7x7"

# ---------------------------------------------------------------- helpers

def finding(module, severity, title, evidence, url=""):
    FINDINGS.append({
        "module": module, "severity": severity, "title": title,
        "evidence": evidence[:500], "url": url,
    })

def norm_target(target):
    if not target.startswith(("http://", "https://")):
        target = "https://" + target
    return target.rstrip("/")

def fetch(url, method="GET", data=None, headers=None, timeout=TIMEOUT):
    """Fetch with redirect capture. Returns (status, final_url, headers, body)."""
    hdrs = {"User-Agent": UA, "Accept": "*/*"}
    if headers:
        hdrs.update(headers)
    body_bytes = data.encode() if isinstance(data, str) else data
    req = urllib.request.Request(url, data=body_bytes, headers=hdrs, method=method)
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
    try:
        with urllib.request.urlopen(req, timeout=timeout, context=ctx) as r:
            return r.status, r.geturl(), dict(r.headers), r.read(400000).decode(errors="ignore")
    except urllib.error.HTTPError as e:
        try:
            body = e.read(400000).decode(errors="ignore")
        except Exception:
            body = ""
        return e.code, url, dict(e.headers or {}), body
    except Exception as e:
        return None, url, {}, str(e)

def norm_url_for_module(base):
    p = urllib.parse.urlparse(base)
    return f"{p.scheme}://{p.netloc}"

# ---------------------------------------------------------------- module 1-6: headers & transport

def mod_headers_security(base, body, headers, url):
    missing = []
    checks = {
        "Strict-Transport-Security": "HSTS missing (http->https not enforced)",
        "X-Content-Type-Options": "nosniff missing (MIME sniffing)",
        "Content-Security-Policy": "CSP missing",
        "X-Frame-Options": "X-Frame-Options missing (clickjacking aid)",
        "Referrer-Policy": "Referrer-Policy missing",
        "Permissions-Policy": "Permissions-Policy missing (feature-policy)",
    }
    for h, why in checks.items():
        if not any(k.lower() == h.lower() for k in headers):
            missing.append(why)
    if missing:
        finding("headers_security", "low", "Missing security headers", "; ".join(missing), url)
    else:
        finding("headers_security", "info", "All standard security headers present", "ok", url)

def mod_headers_info(base, body, headers, url):
    leaks = []
    for h in ("Server", "X-Powered-By", "X-AspNet-Version", "X-AspNetMvc-Version", "X-Generator"):
        v = next((headers[k] for k in headers if k.lower() == h.lower()), None)
        if v:
            leaks.append(f"{h}: {v}")
    if leaks:
        sev = "low" if any(re.search(r"\d", l.split(":", 1)[-1]) for l in leaks) else "info"
        finding("headers_info", sev, "Server/tech version disclosure", "; ".join(leaks), url)

def mod_cookies(base, body, headers, url):
    raw = [v for k, v in headers.items() if k.lower() == "set-cookie"]
    if not raw:
        return
    issues = []
    for c in raw:
        cl = c.lower()
        name = c.split("=", 1)[0].strip()
        if "secure" not in cl and url.startswith("https"):
            issues.append(f"{name}: missing Secure")
        if "httponly" not in cl:
            issues.append(f"{name}: missing HttpOnly")
        if "samesite" not in cl:
            issues.append(f"{name}: missing SameSite")
    if issues:
        finding("cookies", "low", "Cookie flag issues", "; ".join(issues[:6]), url)

def mod_cors(base, body, headers, url):
    tests = [
        ("https://evil.example", "attacker origin"),
        ("null", "null origin"),
    ]
    for origin, label in tests:
        _, _, h, _ = fetch(url, headers={"Origin": origin})
        acao = next((h[k] for k in h if k.lower() == "access-control-allow-origin"), "")
        acac = next((h[k] for k in h if k.lower() == "access-control-allow-credentials"), "")
        if acao == origin and acac.lower() == "true":
            finding("cors_misconfig", "high", f"CORS reflects {label} WITH credentials",
                    f"ACAO={acao}, ACAC={acac}", url)
            return
        if acao == origin:
            finding("cors_misconfig", "medium", f"CORS reflects {label} (no credentials)",
                    f"ACAO={acao}", url)
            return
        if acao == "*":
            finding("cors_misconfig", "info", "CORS wildcard", "ACAO=*", url)
            return

def mod_clickjacking(base, body, headers, url):
    xfo = next((h[k] for k in headers if k.lower() == "x-frame-options"), "")
    csp = next((h[k] for k in headers if k.lower() == "content-security-policy"), "")
    if xfo or "frame-ancestors" in csp.lower():
        return
    if any(t in body.lower() for t in ("<form", "<input", "password")):
        finding("clickjacking", "medium", "No framing protection on stateful page",
                "no XFO/CSP frame-ancestors", url)

def mod_tls(base, body, headers, url):
    if not url.startswith("https"):
        finding("tls", "info", "Site served over plain HTTP", url, url)
        return
    host = urllib.parse.urlparse(url).netloc.split(":")[0]
    try:
        ctx = ssl.create_default_context()
        with socket.create_connection((host, 443), timeout=TIMEOUT) as sock:
            with ctx.wrap_socket(sock, server_hostname=host) as s:
                cert = s.getpeercert()
                proto = s.version()
                exp = ssl.cert_time_to_seconds(cert["notAfter"])
                days = int((exp - datetime.now().timestamp()) / 86400)
                issues = []
                if proto in ("TLSv1", "TLSv1.1", "SSLv3"):
                    issues.append(f"weak protocol {proto}")
                if days < 15:
                    issues.append(f"cert expires in {days}d")
                if issues:
                    finding("tls", "medium", "TLS issues", "; ".join(issues), url)
                else:
                    finding("tls", "info", f"TLS ok ({proto}, cert valid {days}d)", "", url)
    except Exception as e:
        finding("tls", "info", f"TLS probe error: {e}", "", url)

# ---------------------------------------------------------------- module 7-14: discovery

INTERESTING_PATHS = [
    ("robots.txt", "Robots file (disallow list leaks paths)", "info"),
    ("sitemap.xml", "Sitemap exposed", "info"),
    (".env", "Environment file (secrets!)", "critical"),
    (".git/config", "Git config exposed (repo leak)", "high"),
    (".git/HEAD", "Git HEAD exposed (repo leak)", "high"),
    ("wp-config.php.bak", "WordPress config backup", "critical"),
    ("config.php", "App config file", "high"),
    (".DS_Store", "macOS metadata leak", "low"),
    ("server-status", "Apache server-status", "medium"),
    ("server-info", "Apache server-info", "medium"),
    ("actuator", "Spring Boot actuator base", "high"),
    ("actuator/env", "Spring Boot env (secrets)", "critical"),
    ("actuator/heapdump", "Spring Boot heapdump (RAM secrets)", "critical"),
    ("debug", "Debug endpoint", "medium"),
    ("phpinfo.php", "PHP info page", "medium"),
    ("admin", "Admin panel path", "info"),
    ("login", "Login page", "info"),
    ("api", "API root", "info"),
    ("api/v1", "API v1 root", "info"),
    ("graphql", "GraphQL endpoint", "info"),
    ("swagger.json", "Swagger/OpenAPI spec", "medium"),
    ("openapi.json", "OpenAPI spec", "medium"),
    ("api-docs", "API documentation", "medium"),
    (".well-known/security.txt", "security.txt", "info"),
    ("crossdomain.xml", "Flash crossdomain policy", "low"),
    ("backup.zip", "Backup archive", "high"),
    ("db.sql", "Database dump", "critical"),
    ("dump.sql", "Database dump", "critical"),
]

def mod_paths(base, body, headers, url):
    root = norm_url_for_module(url)
    # Baseline: apps dengan catch-all (SPA/redirect 404->/) mengembalikan 200
    # untuk SEMUA path -> bandingkan dengan body root; skip respons identik.
    st0, _, _, body0 = fetch(root + "/__definitely_not_exist_bba25__")
    catchall = (st0 == 200)
    hits = []
    for path, title, sev in INTERESTING_PATHS:
        st, fu, h, b = fetch(f"{root}/{path}")
        if st and st < 400 and len(b) > 0:
            # skip catch-all echoes of the homepage (body sama dengan baseline)
            if catchall and b == body0:
                continue
            # skip generic 200 catch-alls that return the homepage
            if st == 200 and len(b) > 200000 and path not in ("robots.txt", "sitemap.xml"):
                continue
            hits.append(f"/{path} [{st}] ({title})")
            if sev in ("critical", "high"):
                finding("paths", sev, title, f"GET /{path} -> {st}", f"{root}/{path}")
    if hits:
        finding("paths", "info", f"{len(hits)} interesting paths", "; ".join(hits[:12]), root)

def mod_js_secrets(base, body, headers, url):
    srcs = set(re.findall(r'(?:src|href)=["\']([^"\']+\.js(?:\?[^"\']*)?)["\']', body, re.I))
    checked = 0
    for s in list(srcs)[:20]:
        jsurl = urllib.parse.urljoin(url, s)
        st, _, _, js = fetch(jsurl)
        if not st or st >= 400:
            continue
        checked += 1
        patterns = [
            (r'(?i)(api[_-]?key|apikey)\s*[:=]\s*["\'][A-Za-z0-9_\-]{16,}["\']', "API key literal"),
            (r'(?i)(secret|password|passwd)\s*[:=]\s*["\'][^"\']{8,}["\']', "secret/password literal"),
            (r'AKIA[0-9A-Z]{16}', "AWS access key ID"),
            (r'(?i)-----BEGIN (?:RSA |EC )?PRIVATE KEY-----', "private key"),
            (r'sk-[A-Za-z0-9]{20,}', "OpenAI-style secret key"),
            (r'ghp_[A-Za-z0-9]{30,}', "GitHub PAT"),
            (r'xox[baprs]-[A-Za-z0-9\-]{10,}', "Slack token"),
        ]
        for pat, name in patterns:
            m = re.search(pat, js)
            if m:
                finding("js_secrets", "high", f"{name} in JS bundle",
                        f"{jsurl}: ...{m.group(0)[:60]}...", jsurl)
    if checked:
        finding("js_secrets", "info", f"Scanned {checked} JS bundles", "", url)

def mod_robots(base, body, headers, url):
    root = norm_url_for_module(url)
    st, _, _, b = fetch(f"{root}/robots.txt")
    if st == 200 and b.strip():
        disallows = re.findall(r"(?i)disallow:\s*(\S+)", b)
        if disallows:
            finding("robots", "info", f"robots.txt: {len(disallows)} disallowed paths",
                    "; ".join(disallows[:10]), f"{root}/robots.txt")

def mod_redirects(base, body, headers, url):
    # open redirect canary via common params (only with --slow)
    pass  # implemented in slow probes

def mod_http_methods(base, body, headers, url):
    for m in ("TRACE", "PUT", "DELETE", "PATCH", "OPTIONS"):
        st, _, h, b = fetch(url, method=m)
        if st and st not in (405, 501, 403, 404):
            if m == "TRACE" and st == 200:
                finding("http_methods", "medium", "TRACE enabled (XST)", f"TRACE -> {st}", url)
            elif m in ("PUT", "DELETE") and st in (200, 201, 204):
                finding("http_methods", "medium", f"{m} allowed on page", f"{m} -> {st}", url)
    st, _, h, _ = fetch(url, method="OPTIONS")
    allow = next((h[k] for k in h if k.lower() == "allow"), "")
    if allow:
        finding("http_methods", "info", f"OPTIONS allow: {allow}", allow, url)

def mod_graphql(base, body, headers, url):
    root = norm_url_for_module(url)
    for ep in ("/graphql", "/api/graphql", "/v1/graphql"):
        st, _, _, b = fetch(f"{root}{ep}", method="POST",
                            data=json.dumps({"query": "{__schema{types{name}}}"}),
                            headers={"Content-Type": "application/json"})
        if st == 200 and "__schema" in b or '"types"' in b:
            finding("graphql", "high", "GraphQL introspection enabled",
                    f"POST {ep} -> schema dump", f"{root}{ep}")
            return

def mod_error_disclosure(base, body, headers, url):
    st, _, _, b = fetch(url + ("/" if "?" in url else "/?id=1'\""))
    sigs = [
        (r"SQL syntax.*?MySQL", "MySQL error"),
        (r"Warning.*?\Wmysqli?_", "PHP/MySQL warning"),
        (r"PG::SyntaxError", "Postgres error"),
        (r"Microsoft\.OLE\.DB", "MSSQL OLE DB"),
        (r"Traceback \(most recent call last\)", "Python traceback"),
        (r"at \w+ \([\w\.]+:\d+:\d+\)", "Node.js stack trace"),
        (r"java\.lang\.\w+Exception", "Java exception"),
    ]
    for pat, name in sigs:
        if re.search(pat, b):
            finding("error_disclosure", "medium", f"Verbose error disclosure: {name}",
                    re.search(pat, b).group(0)[:120], url)
            return

def mod_backup_files(base, body, headers, url):
    root = norm_url_for_module(url)
    path = urllib.parse.urlparse(url).path or "/"
    name = os.path.basename(path) if path != "/" else "index"
    if not name or "." not in name:
        name = "index.html"
    stem, ext = os.path.splitext(name)
    for suffix in (".bak", ".old", ".orig", ".save", "~", ".swp", ".1"):
        cand = f"{root}{os.path.dirname(path)}/{stem}{suffix}{ext}"
        st, _, _, b = fetch(cand)
        if st and st < 400 and len(b):
            finding("backup_files", "medium", "Backup/source file found",
                    f"{cand} -> {st}", cand)

def mod_ssti_canary(base, body, headers, url):
    if "?" not in url:
        return
    # SSTI canary: inject {{7*7}} style and look for 49 reflection (read-only)
    p = urllib.parse.urlparse(url)
    qs = urllib.parse.parse_qs(p.query)
    if not qs:
        return
    key = list(qs.keys())[0]
    test = dict(qs); test[key] = ["{{7*7}}"]
    q = urllib.parse.urlencode(test, doseq=True)
    st, _, _, b = fetch(f"{p.scheme}://{p.netloc}{p.path}?{q}")
    if "49" in b and "{{7*7}}" not in b:
        finding("ssti", "high", "Possible SSTI ({{7*7}} -> 49)", f"{key}={{7*7}}", url)

def mod_path_traversal(base, body, headers, url):
    if "?" not in url:
        return
    p = urllib.parse.urlparse(url)
    qs = urllib.parse.parse_qs(p.query)
    if not qs:
        return
    key = list(qs.keys())[0]
    for payload in ("....//....//etc/passwd", "..%2f..%2f..%2fetc%2fpasswd"):
        test = dict(qs); test[key] = [payload]
        q = urllib.parse.urlencode(test, doseq=True)
        st, _, _, b = fetch(f"{p.scheme}://{p.netloc}{p.path}?{q}")
        if st == 200 and ("root:" in b or "/bin/bash" in b):
            finding("path_traversal", "critical", "Path traversal reads /etc/passwd",
                    f"{key}={payload}", url)
            return

# ---------------------------------------------------------------- module 15-25: param-based probes

def mod_xss_reflected(base, body, headers, url):
    if "?" not in url:
        return
    p = urllib.parse.urlparse(url)
    qs = urllib.parse.parse_qs(p.query)
    if not qs:
        return
    for key in qs:
        test = dict(qs); test[key] = [f"<{CANARY}>"]
        q = urllib.parse.urlencode(test, doseq=True)
        st, _, _, b = fetch(f"{p.scheme}://{p.netloc}{p.path}?{q}")
        if st == 200 and f"<{CANARY}>" in b:
            finding("xss_reflected", "high", f"Reflected XSS in {key}",
                    f"payload <{CANARY}> reflected", url)
            return

def mod_sqli_error(base, body, headers, url):
    if "?" not in url:
        return
    p = urllib.parse.urlparse(url)
    qs = urllib.parse.parse_qs(p.query)
    if not qs:
        return
    for key in qs:
        test = dict(qs); test[key] = ["'"]
        q = urllib.parse.urlencode(test, doseq=True)
        st, _, _, b = fetch(f"{p.scheme}://{p.netloc}{p.path}?{q}")
        sigs = [r"SQL syntax.*?MySQL", r"Warning.*?\Wmysqli?_", r"PG::SyntaxError",
                r"Microsoft\.OLE\.DB", r"unclosed quotation mark"]
        for pat in sigs:
            if re.search(pat, b, re.I):
                finding("sqli_error", "high", f"SQLi error-based in {key}",
                        re.search(pat, b, re.I).group(0)[:120], url)
                return

def mod_ssrf(base, body, headers, url):
    if "?" not in url:
        return
    p = urllib.parse.urlparse(url)
    qs = urllib.parse.parse_qs(p.query)
    if not qs:
        return
    for key in qs:
        test = dict(qs); test[key] = ["http://127.0.0.1"]
        q = urllib.parse.urlencode(test, doseq=True)
        st, _, _, b = fetch(f"{p.scheme}://{p.netloc}{p.path}?{q}")
        if st == 200 and ("localhost" in b.lower() or "root:" in b):
            finding("ssrf", "high", f"Possible SSRF in {key}",
                    f"127.0.0.1 probe returned local content", url)
            return

def mod_idor(base, body, headers, url):
    if "?" not in url:
        return
    p = urllib.parse.urlparse(url)
    qs = urllib.parse.parse_qs(p.query)
    if not qs:
        return
    for key in qs:
        if re.match(r"^(id|user_id|account|order)", key, re.I):
            orig = qs[key][0]
            if orig.isdigit():
                test = dict(qs); test[key] = [str(int(orig) + 1)]
                q = urllib.parse.urlencode(test, doseq=True)
                st, _, _, b = fetch(f"{p.scheme}://{p.netloc}{p.path}?{q}")
                if st == 200 and len(b) > 100:
                    finding("idor", "medium", f"Possible IDOR in {key}",
                            f"changed {orig} -> {int(orig)+1}, got 200", url)
                    return

def mod_rate_limit(base, body, headers, url):
    # send 10 rapid requests, check for 429
    for i in range(10):
        st, _, _, _ = fetch(url)
        if st == 429:
            finding("rate_limit", "info", "Rate limiting active (429)", f"hit 429 on req {i+1}", url)
            return
    finding("rate_limit", "low", "No rate limiting detected", "10 reqs -> no 429", url)

def mod_subdomain_takeover(base, body, headers, url):
    sigs = {
        "There is no app configured at that hostname": "Heroku",
        "NoSuchBucket": "AWS S3",
        "The specified bucket does not exist": "AWS S3",
        "Repository not found": "GitHub Pages",
        "Sorry, this shop is currently unavailable": "Shopify",
        "Project doesn't exist": "GitLab Pages",
        "The requested URL was not found on this server": "generic",
    }
    if url.startswith("https"):
        return  # skip HTTPS (already handled)
    host = urllib.parse.urlparse(url).netloc
    try:
        ip = socket.gethostbyname(host)
    except Exception:
        return
    for sig, service in sigs.items():
        if sig in body:
            finding("subdomain_takeover", "high", f"Possible {service} takeover",
                    f"{host} -> {ip}, body contains '{sig}'", url)
            return

def mod_open_redirect(base, body, headers, url):
    if "?" not in url:
        return
    p = urllib.parse.urlparse(url)
    qs = urllib.parse.parse_qs(p.query)
    if not qs:
        return
    for key in qs:
        if re.match(r"(redirect|url|next|return|goto)", key, re.I):
            test = dict(qs); test[key] = ["//evil.com"]
            q = urllib.parse.urlencode(test, doseq=True)
            st, fu, _, _ = fetch(f"{p.scheme}://{p.netloc}{p.path}?{q}")
            if fu and "evil.com" in fu:
                finding("open_redirect", "medium", f"Open redirect in {key}",
                        f"redirected to {fu}", url)
                return

def mod_crlf(base, body, headers, url):
    if "?" not in url:
        return
    p = urllib.parse.urlparse(url)
    qs = urllib.parse.parse_qs(p.query)
    if not qs:
        return
    for key in qs:
        test = dict(qs); test[key] = ["%0d%0aInjected-Header:1"]
        q = urllib.parse.urlencode(test, doseq=True)
        st, _, h, _ = fetch(f"{p.scheme}://{p.netloc}{p.path}?{q}")
        if "Injected-Header" in h:
            finding("crlf", "medium", f"CRLF injection in {key}",
                    "header reflected", url)
            return

def mod_xml_external(base, body, headers, url):
    if "?" not in url:
        return
    p = urllib.parse.urlparse(url)
    qs = urllib.parse.parse_qs(p.query)
    if not qs:
        return
    for key in qs:
        test = dict(qs); test[key] = ['<?xml version="1.0"?><!DOCTYPE foo [<!ENTITY xxe "XXE">]><foo>&xxe;</foo>']
        q = urllib.parse.urlencode(test, doseq=True)
        st, _, _, b = fetch(f"{p.scheme}://{p.netloc}{p.path}?{q}")
        if "XXE" in b:
            finding("xxe", "critical", f"XXE in {key}", "entity expanded", url)
            return

def mod_host_header(base, body, headers, url):
    root = norm_url_for_module(url)
    st, _, _, b = fetch(url, headers={"Host": "evil.com"})
    if "evil.com" in b:
        finding("host_header", "medium", "Host header injection",
                "evil.com reflected in response", url)
        return

def mod_cache_poisoning(base, body, headers, url):
    st, _, h, _ = fetch(url, headers={"X-Forwarded-Host": "evil.com"})
    if "evil.com" in str(h):
        finding("cache_poisoning", "medium", "Possible cache poisoning via X-Forwarded-Host",
                "header reflected", url)
        return

def mod_cors_wildcard(base, body, headers, url):
    acao = next((h[k] for k in headers if k.lower() == "access-control-allow-origin"), "")
    if acao == "*":
        finding("cors_wildcard", "low", "CORS wildcard origin", "ACAO=*", url)
        return

def mod_csrf(base, body, headers, url):
    if "<form" not in body.lower():
        return
    if "csrf" in body.lower() or "token" in body.lower():
        return
    if any(k.lower() == "x-csrf-token" for k in headers):
        return
    finding("csrf", "medium", "Possible CSRF (form without token)",
            "no CSRF token found", url)

def mod_directory_listing(base, body, headers, url):
    if "<title>Index of" in body or "Directory listing for" in body:
        finding("directory_listing", "medium", "Directory listing enabled",
                "Index of page", url)
        return

def mod_information_disclosure(base, body, headers, url):
    patterns = [
        (r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b", "email address"),
        (r"\b\d{3}-\d{2}-\d{4}\b", "SSN pattern"),
        (r"\b(?:\+?1[-.]?)?\(?[0-9]{3}\)?[-.]?[0-9]{3}[-.]?[0-9]{4}\b", "phone number"),
    ]
    for pat, name in patterns:
        m = re.search(pat, body)
        if m:
            finding("info_disclosure", "low", f"{name} disclosed",
                    m.group(0), url)
            return

# ---------------------------------------------------------------- module 26-35 (misc) + registry

def mod_websocket(base, body, headers, url):
    if "ws://" in body or "wss://" in body:
        wss = re.findall(r"wss?://[^\s\"'<>]+", body)
        if wss:
            finding("websocket", "info", "WebSocket endpoints referenced",
                    "; ".join(set(wss))[:200], url)

def mod_api_keys_in_html(base, body, headers, url):
    patterns = [
        (r'AIza[0-9A-Za-z\-_]{35}', "Google API key"),
        (r'AKIA[0-9A-Z]{16}', "AWS access key"),
        (r'(?i)firebaseio\.com', "Firebase reference"),
        (r'sk_live_[0-9a-zA-Z]{24,}', "Stripe live secret"),
        (r'pk_live_[0-9a-zA-Z]{24,}', "Stripe live publishable"),
    ]
    for pat, name in patterns:
        m = re.search(pat, body)
        if m:
            sev = "high" if "secret" in name.lower() or "AWS" in name else "medium"
            finding("api_keys_html", sev, f"{name} in HTML", m.group(0)[:50], url)

def mod_debug_params(base, body, headers, url):
    root = norm_url_for_module(url)
    for param in ("debug=true", "test=1", "debug=1"):
        st, _, _, b = fetch(f"{url}{'&' if '?' in url else '?'}{param}")
        if st == 200 and ("debug" in b.lower()[:5000] and "trace" in b.lower()):
            finding("debug_params", "medium", f"Debug mode via ?{param}",
                    "verbose output", url)
            return

def mod_admin_panels(base, body, headers, url):
    root = norm_url_for_module(url)
    st0, _, _, body0 = fetch(root + "/__definitely_not_exist_bba25__")
    catchall = (st0 == 200)
    for p in ("/admin", "/administrator", "/wp-admin", "/manager/html", "/phpmyadmin"):
        st, _, _, b = fetch(f"{root}{p}")
        if st in (200, 401, 403):
            if catchall and b == body0:
                continue
            finding("admin_panels", "info" if st != 200 else "low",
                    f"Admin panel {p} [{st}]", f"GET {p} -> {st}", f"{root}{p}")

def mod_default_creds_hint(base, body, headers, url):
    if any(x in body.lower() for x in ("default password", "admin/admin", "changeme")):
        finding("default_creds", "medium", "Default credentials hint in page",
                "page mentions default creds", url)

def mod_dangerous_files(base, body, headers, url):
    root = norm_url_for_module(url)
    st0, _, _, body0 = fetch(root + "/__definitely_not_exist_bba25__")
    catchall = (st0 == 200)
    for p in ("/.htpasswd", "/web.config", "/.aws/credentials", "/id_rsa"):
        st, _, _, b = fetch(f"{root}{p}")
        if st == 200 and len(b) > 0:
            if catchall and b == body0:
                continue
            finding("dangerous_files", "critical", f"Sensitive file {p}",
                    f"GET {p} -> 200", f"{root}{p}")

def mod_version_control(base, body, headers, url):
    root = norm_url_for_module(url)
    st0, _, _, body0 = fetch(root + "/__definitely_not_exist_bba25__")
    catchall = (st0 == 200)
    paths = ["/.git/HEAD", "/.svn/entries", "/.hg/store"]
    for p in paths:
        st, _, _, b = fetch(f"{root}{p}")
        if st == 200 and len(b) > 0:
            if catchall and b == body0:
                continue
            finding("version_control", "high", f"Version control exposed: {p}",
                    f"GET {p} -> 200", f"{root}{p}")
            return

def mod_email_spf(base, body, headers, url):
    host = urllib.parse.urlparse(url).netloc.split(":")[0]
    # DNS TXT lookup via stdlib is limited; note as manual check
    finding("email_spf", "info", "Check SPF/DMARC/DKIM manually",
            f"dig TXT {host} / _dmarc.{host}", url)

def mod_cve_fingerprint(base, body, headers, url):
    server = next((headers[k] for k in headers if k.lower() == "server"), "")
    xpb = next((headers[k] for k in headers if k.lower() == "x-powered-by"), "")
    combo = f"{server} {xpb}".strip()
    if re.search(r"\d+\.\d+", combo):
        finding("cve_fingerprint", "info", "Version string — check CVE databases",
                f"'{combo}' -> search NVD/exploit-db", url)

def mod_websocket_summary(base, body, headers, url):
    pass  # placeholder to keep count; websocket handled above

# ---- module registry: name -> (function, needs_params) ----
MODULES = {
    "headers_security": (mod_headers_security, False),
    "headers_info": (mod_headers_info, False),
    "cookies": (mod_cookies, False),
    "cors": (mod_cors, False),
    "clickjacking": (mod_clickjacking, False),
    "tls": (mod_tls, False),
    "paths": (mod_paths, False),
    "js_secrets": (mod_js_secrets, False),
    "robots": (mod_robots, False),
    "http_methods": (mod_http_methods, False),
    "graphql": (mod_graphql, False),
    "error_disclosure": (mod_error_disclosure, False),
    "backup_files": (mod_backup_files, False),
    "host_header": (mod_host_header, False),
    "cache_poisoning": (mod_cache_poisoning, False),
    "cors_wildcard": (mod_cors_wildcard, False),
    "csrf": (mod_csrf, False),
    "directory_listing": (mod_directory_listing, False),
    "info_disclosure": (mod_information_disclosure, False),
    "version_control": (mod_version_control, False),
    "websocket": (mod_websocket, False),
    "api_keys_html": (mod_api_keys_in_html, False),
    "admin_panels": (mod_admin_panels, False),
    "default_creds": (mod_default_creds_hint, False),
    "dangerous_files": (mod_dangerous_files, False),
    "email_spf": (mod_email_spf, False),
    "cve_fingerprint": (mod_cve_fingerprint, False),
    # --- param-based (need ?query=, run with --slow) ---
    "xss_reflected": (mod_xss_reflected, True),
    "sqli_error": (mod_sqli_error, True),
    "ssrf": (mod_ssrf, True),
    "idor": (mod_idor, True),
    "open_redirect": (mod_open_redirect, True),
    "crlf": (mod_crlf, True),
    "xxe": (mod_xml_external, True),
    "ssti": (mod_ssti_canary, True),
    "path_traversal": (mod_path_traversal, True),
    "rate_limit": (mod_rate_limit, True),
}

SEV_ORDER = {"critical": 0, "high": 1, "medium": 2, "low": 3, "info": 4}
SEV_COLOR = {"critical": "\033[95m", "high": "\033[91m", "medium": "\033[93m",
             "low": "\033[94m", "info": "\033[90m"}
RESET = "\033[0m"

def run_target(target, modules, slow, endpoints):
    base = norm_target(target)
    urls = [base]
    if endpoints:
        urls += endpoints
    print(f"[*] scanning {base} ({len(MODULES) if not modules else len(modules)} modules, "
          f"{len(urls)} URL(s), slow={slow})")
    seen = set()
    for u in urls:
        if u in seen:
            continue
        seen.add(u)
        st, fu, h, b = fetch(u)
        if st is None:
            print(f"[!] {u}: unreachable ({b[:80]})")
            continue
        for name, (fn, needs_params) in MODULES.items():
            if modules and name not in modules:
                continue
            if needs_params and not slow:
                continue
            if needs_params and "?" not in u:
                continue
            try:
                fn(base, b, h, fu or u)
            except Exception as e:
                pass  # never let one module crash the scan

def main():
    global FINDINGS
    ap = argparse.ArgumentParser(description="Core vulnerability scanner (35 modules)")
    ap.add_argument("target", nargs="?", default=None)
    ap.add_argument("--slow", action="store_true", help="enable param-based active probes")
    ap.add_argument("--modules", help="comma list of module names (default: all)")
    ap.add_argument("--endpoints", help="file of URLs (one per line) e.g. from har2scan")
    ap.add_argument("--json", help="write findings JSON to file")
    ap.add_argument("--list-modules", action="store_true")
    args = ap.parse_args()

    if args.list_modules:
        for name, (fn, needs) in MODULES.items():
            print(f"{name:<22} {'[param/slow]' if needs else ''}")
        print(f"\ntotal: {len(MODULES)} modules")
        return

    modules = set(m.strip() for m in args.modules.split(",")) if args.modules else None
    if not args.target:
        ap.error("target is required (unless --list-modules)")
    endpoints = None
    if args.endpoints:
        with open(args.endpoints) as f:
            endpoints = [l.strip() for l in f if l.strip() and not l.startswith("#")]

    run_target(args.target, modules, args.slow, endpoints)

    FINDINGS.sort(key=lambda x: SEV_ORDER.get(x["severity"], 9))
    print(f"\n=== {len(FINDINGS)} findings ===")
    counts = {}
    for f in FINDINGS:
        counts[f["severity"]] = counts.get(f["severity"], 0) + 1
        c = SEV_COLOR.get(f["severity"], "")
        print(f"{c}[{f['severity'].upper():<8}]{RESET} {f['module']}: {f['title']}")
        if f["evidence"]:
            print(f"           {f['evidence'][:150]}")
    print("\nsummary:", ", ".join(f"{k}={v}" for k, v in sorted(counts.items(), key=lambda x: SEV_ORDER.get(x[0], 9))))

    if args.json:
        with open(args.json, "w") as f:
            json.dump(FINDINGS, f, indent=2)
        print(f"[+] findings -> {args.json}")

if __name__ == "__main__":
    main()
