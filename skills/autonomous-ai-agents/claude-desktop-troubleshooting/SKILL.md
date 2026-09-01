---
name: claude-desktop-troubleshooting
description: "Troubleshoot Claude Desktop issues — UWP/Windows Store install, gateway configuration, missing Connection menu, MCP server errors. Covers Claude Desktop vs Claude Code CLI differences, config file locations, and workaround strategies."
version: 1.1.0
author: Hermes Agent
license: MIT
platforms: [windows, macos, linux]
metadata:
  hermes:
    tags: [Claude, Desktop, Troubleshooting, Gateway, UWP, Windows-Store, MCP]
    related_skills: [claude-code]
---

# Claude Desktop Troubleshooting

## When to Load
- User cannot find "Connection" menu in Claude Desktop settings
- Claude Desktop installed from Windows Store (UWP) has limited features
- Gateway/API configuration issues with Claude Desktop
- MCP server errors or disconnection issues
- User wants to use third-party gateway with Claude Desktop
- "Model discovery" or `/v1/models` 404 errors in Connection settings

## Critical Distinction: Connection vs MCP Servers

Claude Desktop has TWO separate concepts that are often confused:

| Setting | Location | Purpose |
|---------|----------|---------|
| **Connection** (inference gateway) | Settings → Connection | Routes LLM API calls (what model to talk to) |
| **MCP Servers** (tools/agents) | Settings → Developer / config file | Provides external tools to Claude |

**They do NOT interfere with each other.** A gateway in Connection is for inference (chatting with AI). MCP servers provide tools (delegation to specialist agents). Both can coexist.

## Claude Desktop vs Claude Code CLI — Key Differences

| Feature | Claude Desktop | Claude Code CLI |
|---------|---------------|-----------------|
| **Gateway support** | ✅ UI menu (Connection) | ✅ Full (env variables) |
| **Config file** | MCP servers only | Full config support |
| **Installation** | .exe installer or Windows Store | npm global install |
| **Plan requirement** | Any plan (Free works too) | Any plan with API key |

**Rule of thumb:** Claude Desktop Connection menu is available on all plans (including Free) when installed from the .exe installer.

## Installation Methods

### 1. Official Installer (.exe)
- Download from: https://claude.ai/download
- Install location: `%LOCALAPPDATA%\AnthropicClaude\`
- Features: Full feature set, including Connection menu

### 2. Windows Store (UWP)
- Install via Microsoft Store
- Install location: `C:\Users\[USER]\AppData\Local\Packages\Claude_[random]\`
- Config location: `C:\Users\[USER]\AppData\Local\Packages\Claude_[random]\LocalCache\Roaming\Claude\`
- **Limitations:** May lag behind .exe version in features

### How to Check Installation Type
```powershell
# Check if UWP install
Get-AppxPackage *Claude* | Select-Object Name, PackageFullName

# Check if .exe install
Get-ChildItem "$env:LOCALAPPDATA\AnthropicClaude" -ErrorAction SilentlyContinue
```

## Common Issues

### Issue 1: Missing "Connection" Menu

**Symptoms:**
- Settings menu shows: General, Account, Privacy, Billing, etc.
- No "Connection" or "Gateway" option visible

**Causes:**
1. **UWP version outdated** — Windows Store version may lag behind
2. **Outdated version** — Need to update to latest

**Diagnosis:**
```
Settings → Account → Check plan (Free/Pro/Team/Enterprise)
Settings → Check version number (if visible)
```

**Solutions:**

| Solution | When to Use |
|----------|-------------|
| **Reinstall from .exe** | If using UWP version — most common fix |
| **Update via Store** | If UWP version is outdated |
| **Use Claude Code CLI** | If user wants gateway without reinstalling |
| **Use Open WebUI** | If user wants GUI + gateway flexibility |

### Issue 2: Config File Only Supports MCP Servers

**Symptoms:**
- User edited `claude_desktop_config.json`
- Added `apiBaseUrl` or `gateway` fields
- Claude Desktop ignores these fields

**Root Cause:**
`claude_desktop_config.json` is ONLY for MCP server configuration:
```json
{
  "mcpServers": {
    "server-name": {
      "command": "npx",
      "args": ["..."],
      "env": { "KEY": "value" }
    }
  }
}
```

Gateway configuration must be done via UI (Settings → Connection), not config file.

### Issue 3: MCP Server Disconnected/Error

**Symptoms:**
- MCP server shows "Error" or "Server disconnected"
- Tools from MCP server not available

**Common Causes:**
1. **Wrong URL** — SSE endpoint incorrect or unreachable
2. **Auth issue** — API key invalid or expired
3. **Network/firewall** — Connection blocked
4. **Server down** — Remote MCP server offline

**Diagnosis:**
```
1. Click "Lihat Log" (View Log) in Claude Desktop
2. Check error message for clues
3. Test MCP endpoint manually:
   curl -v https://your-mcp-server.com/mcp/sse
```

**Fix Pattern:**
```json
{
  "mcpServers": {
    "my-server": {
      "command": "npx",
      "args": [
        "-y",
        "@modelcontextprotocol/client-sse",
        "https://your-server.com/mcp/sse"
      ],
      "env": {
        "API_KEY": "***"
      }
    }
  }
}
```

### Issue 4: "Model discovery — Gateway /v1/models returned HTTP 404"

**Symptoms:**
- Connection configured with gateway base URL
- Save Changes shows error: `Model discovery — Gateway /v1/models returned HTTP 404`
- Connection test fails

**Root Cause:**
The gateway does not expose a `/v1/models` endpoint for automatic model discovery. Some gateways (like Agent Router) don't implement this endpoint.

**Fix:**
Under the Connection settings, look for a "Models" section and **manually add model entries** to skip discovery:
```
Models:
  - claude-sonnet-4-20250514
  - claude-haiku-3-5-20241022
  (add whichever models the gateway supports)
```

Or fix the gateway URL — URL typos are the #1 cause of this error.

### Issue 5: Wrong Gateway URL Format

**Symptoms:**
- `/v1/models` returns 404
- Connection test fails
- Other users with the same gateway report it works

**Root Cause:**
URL format is critical — `www.`, dashes, and trailing slashes matter.

**Real-world example (Agent Router):**
| URL | Works? |
|-----|--------|
| `https://agentrouter.org` | ✅ Correct |
| `https://www.agent-router.org/` | ❌ 404 (docs site, not API) |
| `https://agent-router.org` | ❌ Wrong domain |

**Fix:** Always verify the exact URL from a working configuration (ask a friend, check official docs). Copy-paste, don't retype.

### Issue 6: "API Error: 400 content-blocked" When Using Gateway

**Symptoms:**
- Claude Desktop returns `API Error: 400 content-blocked` repeatedly
- Multiple requests fail with different request IDs
- Happens during code analysis or long conversations

**Root Cause:**
The gateway or upstream provider's content filter is rejecting the request. This is NOT a configuration error — the gateway is working, but the specific prompt/context triggers moderation filters.

**Common Triggers:**
1. **Large code analysis** — analyzing many files at once
2. **Sensitive keywords** — words like "admin", "bypass", "hack" in context
3. **Long context** — system prompt + conversation + code = filter overload
4. **Gateway-level filtering** — some gateways add their own content filters on top of the model provider's

**Solutions:**

| Approach | How |
|----------|-----|
| **Break down requests** | Ask for one small thing at a time instead of "analyze everything" |
| **Rephrase prompts** | Avoid security-sensitive keywords |
| **Clear context** | Start a new conversation/session |
| **Try different model** | `claude-sonnet-4-20250514` or older versions may have looser filters |
| **Switch gateway** | Different gateways have different filter layers |

**Note:** This is a provider-side issue, not a configuration problem. The gateway is correctly forwarding the request — the upstream API is blocking it.

## Gateway Configuration

### Connection Settings Fields

| Field | Purpose | Example |
|-------|---------|---------|
| **Gateway base URL** | Full URL of inference gateway endpoint | `https://agentrouter.org` |
| **Gateway API key** | Authentication credential | `a2a_...` or `sk-...` |
| **Gateway auth scheme** | How credential is sent | `Bearer` or `x-api-key` |
| **Gateway extra headers** | Additional headers (routing, tenant IDs) | `X-Header-Name: value` |
| **Artifact preview iframe origin** | HTTPS origin for artifact renderer | (leave default) |
| **Custom inference headers** | Extra headers on every request | (usually empty) |

### Auth Scheme Selection
- **Bearer (default)** — sends `Authorization: Bearer <key>` — use for most gateways
- **x-api-key** — sends `x-api-key: <key>` — auto-selected for Anthropic API directly

## Gateway Configuration Workarounds

### Option A: Claude Code CLI (Recommended for Power Users)
```bash
# Set gateway via environment variables
export ANTHROPIC_BASE_URL="https://your-gateway.com/v1"
export ANTHROPIC_API_KEY="***"

# Run Claude Code
claude
```

**Pros:**
- ✅ Works with any gateway
- ✅ No plan upgrade needed
- ✅ Full feature support

**Cons:**
- ❌ Terminal-based, no GUI
- ❌ Steeper learning curve

### Option B: Open WebUI (GUI Alternative)
```bash
docker run -d -p 3000:8080 \
  -e ANTHROPIC_API_KEY="***" \
  -e ANTHROPIC_API_BASE_URL="https://your-gateway.com/v1" \
  -v open-webui:/app/backend/data \
  ghcr.io/open-webui/open-webui:main
```

**Pros:**
- ✅ Beautiful GUI (similar to ChatGPT)
- ✅ Gateway support
- ✅ Can install as PWA on desktop
- ✅ Multi-model support

**Cons:**
- ❌ Requires Docker
- ❌ Separate from Claude Desktop

### Option C: Local Proxy (Advanced)
Run local proxy that intercepts Claude Desktop requests and forwards to gateway.

**Architecture:**
```
Claude Desktop → Local Proxy (port 443) → Your Gateway
```

**Complexity:** High (requires SSL cert, hosts file modification)
**Reliability:** Medium (fragile, breaks on updates)

**Not recommended** unless absolutely necessary.

## Recommended Gateways

| Gateway | URL | Pricing | Best For |
|---------|-----|---------|----------|
| **Agent Router** | https://agentrouter.org | Free tier available | Multi-agent platform + inference |
| **OpenRouter** | https://openrouter.ai/api/v1 | Pay per use ($0.001-$0.05/msg) | Multi-model access |
| **Anthropic Console** | https://console.anthropic.com/ | Pay per token | Official API |
| **Together AI** | https://api.together.ai/ | Cheap, many models | Budget option |
| **Groq** | https://console.groq.com/ | Free (rate limit) | Testing/learning |

### Agent Router Setup
```
1. Sign up at https://agentrouter.org
2. Get API key (starts with a2a_...)
3. In Claude Desktop → Settings → Connection:
   - Gateway base URL: https://agentrouter.org  (NOT www.agent-router.org!)
   - Gateway API key: ***
   - Auth scheme: Bearer
4. If /v1/models 404: manually add model names
```

**Note:** Agent Router is BOTH an MCP platform (tools/agents) AND an inference gateway. Use the same platform in two places:
- Settings → Connection → for inference
- Settings → Developer → MCP Servers → for agent tools

### OpenRouter Setup
```bash
# 1. Sign up at https://openrouter.ai/keys
# 2. Create API key (starts with sk-or-...)
# 3. Top up minimum $5

# 4. Use with Claude Code CLI
export ANTHROPIC_BASE_URL="https://openrouter.ai/api/v1"
export ANTHROPIC_API_KEY="***"
claude
```

## Pitfalls

### ⚠️ Don't try to hack config file for gateway
Editing `claude_desktop_config.json` to add `apiBaseUrl` or `gateway` fields will NOT work. Claude Desktop ignores these fields. Gateway must be configured via UI (Settings → Connection) or use alternative tools (Claude Code CLI, Open WebUI).

### ⚠️ UWP "Open file location" is grayed out
Windows Store apps (UWP) have restricted file access. Right-click → "Open file location" in Task Manager is disabled.

**Workaround:**
```powershell
# Find install location
Get-AppxPackage *Claude* | Select-Object InstallLocation

# Config files are in:
# %LOCALAPPDATA%\Packages\Claude_[random]\LocalCache\Roaming\Claude\
```

### ⚠️ URL format is extremely important
Gateway URLs are NOT interchangeable with their documentation URLs. Common mistakes:
- Adding `www.` prefix
- Adding dashes where none exist
- Using documentation domain instead of API domain
- Trailing slashes sometimes matter

**Always copy-paste the exact URL from working configuration.**

### ⚠️ MCP server errors don't affect gateway
MCP servers (Model Context Protocol) are for external tools, not for API routing. MCP errors won't prevent Claude Desktop from working with the gateway — they only disable external tool integrations.

### ⚠️ Connection vs MCP are independent
Do not confuse:
- **Connection** (Settings → Connection) = inference gateway, sends chat to LLM
- **MCP Servers** (Settings → Developer) = external tools that Claude can call

Both can be configured simultaneously and do not conflict.

## Decision Tree

```
User wants gateway in Claude Desktop
  ↓
Check installation type (UWP or .exe?)
  ↓
├─ UWP → Reinstall from .exe first (https://claude.ai/download)
│         ↓
│         Connection menu appears → Configure gateway
│
└─ .exe installer
    ↓
    Settings → Connection → Fill gateway fields
    ↓
    ├─ Works → Done!
    │
    └─ /v1/models 404 error
        ↓
        ├─ URL typo? → Fix URL (copy from working config)
        └─ Gateway lacks /v1/models? → Manually add model names
```

## Migration Path

If user is stuck with Claude Desktop limitations:

1. **Try reinstalling from .exe** (if using UWP)
   - Uninstall: `Get-AppxPackage *Claude* | Remove-AppxPackage`
   - Download: https://claude.ai/download
   - Install and check if Connection menu appears

2. **If still no Connection menu** → likely outdated version
   - Update or reinstall latest from https://claude.ai/download

3. **For maximum flexibility** → Claude Code CLI + Open WebUI combo
   - CLI for terminal work
   - Open WebUI for GUI tasks
   - Both support any gateway

## Related Skills
- `claude-code` — For Claude Code CLI usage and configuration