---
name: large-file-write
description: Write large files (HTML/JS/CSS) when write_file and execute_code fail silently due to content size. Uses bash heredocs in parts with escaping fixes.
triggers:
  - writing files over 5KB
  - write_file content parameter not included
  - execute_code "No code provided" error
  - single-file web app deployment
---

# Large File Write via Bash Heredoc

## Problem
`write_file` and `execute_code` tools silently fail when content is very large — the content/code parameter gets dropped entirely, resulting in empty files or "No code provided" errors.

## Solution: Bash Heredoc in Parts

### Step 1: Write file in parts using `cat >` (first part) and `cat >>` (append)

```bash
# First part (overwrites)
cat > /path/to/file << 'EOF'
content here
EOF

# Subsequent parts (appends)
cat >> /path/to/file << 'EOF'
more content
EOF
```

### Step 2: CRITICAL — Escape JavaScript strings carefully

**Heredoc pitfall:** Backslash escaping behaves differently inside heredocs vs JavaScript strings.

Rules:
- Inside heredoc with `'EOF'` (quoted): NO variable expansion, backslashes are literal
- For JS strings containing single quotes inside HTML onclick handlers, use `\\'` (double backslash + quote)
- **WRONG:** `\\\\\\'` (triple backslash) — this breaks JavaScript parsing
- **RIGHT:** `\\'` inside the heredoc → becomes `\'` in the file → valid JS escape

Example for generating HTML with JS onclick:
```bash
cat >> file << 'EOF'
<div onclick="handleClick(\\'myId\\')">Click</div>
EOF
```

### Step 3: Verify with Node.js syntax check

```bash
# Extract JS from HTML and check syntax
node -e "
const fs=require('fs');
const html=fs.readFileSync('/path/to/file','utf8');
const m=html.match(/<script>([\s\S]*?)<\/script>/);
if(m){try{new Function(m[1]);console.log('OK')}catch(e){console.log('Error:',e.message)}}
"
```

Or write JS to temp file and use `node --check`:
```bash
node --check /path/to/extracted.js
```

### Step 4: Fix escaping issues with Python

If `node --check` reports errors on lines with escaped quotes:
```python
with open('file.html', 'r') as f:
    content = f.read()
# Fix double-escaped backslashes: \\\\' → \\'
content = content.replace("\\\\'", "\\'")
with open('file.html', 'w') as f:
    f.write(content)
```

## Verification Checklist
1. `wc -l` and `wc -c` confirm file size matches expectations
2. `node --check` passes on extracted JavaScript
3. No JS errors in browser console after deployment
4. `pm2 restart <app>` to reload changes

## Common Pitfalls
- Don't use unquoted heredoc delimiter (`<< EOF`) when content has `$` or backticks — use `<< 'EOF'`
- Emoji with ZWJ (zero-width joiner) characters like 👨‍🎓 are fine in JS but may trigger security scanners
- Always restart the Node.js server after modifying static files served by Express
