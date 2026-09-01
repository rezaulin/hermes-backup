---
name: llm-proxy-gateway
description: "Call operator's custom OpenAI-compatible LLM proxy gateways: auth discovery, capability probing, model fallback roulette, vision analysis, streaming-response parsing. Load when hitting 401/412 on a custom endpoint, when vision_analyze has no provider, or when any task needs an LLM/vision call through a non-standard base URL."
---

# LLM Proxy Gateway Ops

Operator runs custom OpenAI-compatible gateways that aggregate many upstream
providers (Fireworks, Anthropic-likes, GPT-likes, Grok) behind one base URL.
Upstreams rotate, run out of quota, and get suspended — treat EVERY model as
possibly broken and probe, don't assume.

## When to load
- Any curl/SDK call to a custom base URL returns 401/412/empty.
- `vision_analyze` says "no provider configured" or times out.
- Need vision analysis of an image/video frame via the operator's proxy.
- A model that worked yesterday returns errors today.

## 1. Auth discovery (do this FIRST on 401)
Gateways differ per deployment. Test header variants against `/v1/models`
(cheap, no tokens) before anything else:

```bash
K="<key>"; B="<base_url>"   # e.g. http://host:20128/v1
curl -s -H "Authorization: Bearer $K"  "$B/models" | head -c 120
curl -s -H "X-API-Key: $K"             "$B/models" | head -c 120
curl -s -H "api-key: $K"               "$B/models" | head -c 120
```

Pitfall discovered 2026-08: one gateway required BOTH
`Authorization: Bearer $K` AND `X-API-Key: $K` simultaneously — each alone
401'd. If single-header calls 401, send both.

OpenAI SDK equivalent — needed for any Python-side call (e.g. godmode
auto_jailbreak against the proxy). The SDK sends only `Authorization: Bearer`
by default; `default_headers` adds the second header the gateway demands:

```python
from openai import OpenAI
client = OpenAI(api_key=K, base_url=B, default_headers={"X-API-Key": K})
```

Two more gotchas seen when driving the proxy from Python (2026-08):

- The gateway may inject its own large system prompt (a trivial query came
  back with ~2k prompt tokens). That permissive framing is the gateway's, not
  yours — it makes models appear more compliant on gray-area prompts while
  still hard-refusing clearly harmful ones.
- Scripts that auto-detect the model from `config.yaml` (godmode's
  auto_jailbreak reads `model.name` / `model.base_url`) break on this
  profile, which uses `model.default` + `model.provider` + a
  `custom_providers` list. Pass `model` / `base_url` / `api_key` explicitly
  instead of relying on auto-detection.

## 2. Capability probing
`GET /v1/models` returns `capabilities.vision` etc. Filter:

```bash
curl -s -H "X-API-Key: $K" "$B/models" | python3 -c "
import sys,json
for m in json.load(sys.stdin).get('data',[]):
    if m.get('capabilities',{}).get('vision'): print(m['id'])"
```

## 3. Model fallback roulette (the core loop)
Upstream states seen: `401 credentials expired`, `412 Precondition Failed`
(often image too large OR rate limit — error text may say "reset after Ns"),
empty body (model dead), quota-exhausted messages with dollar amounts,
`HTTP 200 with a JSON error body` (e.g. qoder code-112 paywall — body reads
`[qoder error 403: {"code":"112","message":{"pricingUrl":"…qoder.com/pricing…"}}]`)
which masquerades as a normal completion and fools a naive refusal-scorer into
"COMPLY" when it's really an error. Grep the body for `error`/`403`/`pricing`
before judging compliance; a suspiciously short identical response across many
models = the same error body, not real output.
Strategy: iterate candidate models, ONE cheap test call each, keep the first
that returns content. For vision, known-good fallback (2026-08):
`fireworks/accounts/fireworks/models/kimi-k3` survived when gcli/grok-build,
oc-prod/claude-*, bb/gpt-5.* all failed.

```bash
curl -s -m 90 -H "Authorization: Bearer $K" -H "X-API-Key: $K" \
  -H "Content-Type: application/json" "$B/chat/completions" \
  -d '{"model":"<M>","messages":[{"role":"user","content":[
    {"type":"text","text":"<prompt>"},
    {"type":"image_url","image_url":{"url":"data:image/jpeg;base64,<B64>"}}
  ]}],"max_tokens":500}'
```

## 4. Image payloads
- Downscale before base64: `PIL thumbnail((900,900))`, quality 82-90.
  Full-res frames got 412; ~384-900px worked. Keep base64 under ~150KB.
- For crops: upscale 2-4x + Contrast 1.5-2.0 before sending (handwritten
  Arabic reads much better enlarged).
- 412 with "reset after Ns" text = upstream rate limit; sleep and retry the
  SAME model before switching.

## 5. Response parsing pitfalls
- Gateway may stream MULTIPLE JSON objects in one body (chunked objects, not
  SSE). `json.loads` raises; use incremental decode:
  ```python
  dec = json.JSONDecoder()
  try: d = json.loads(raw)
  except json.JSONDecodeError: d, _ = dec.raw_decode(raw)
  content = d['choices'][0]['message']['content']
  ```
- Empty `content` with no error = model dead; move to next candidate.
- Verbose chain-of-thought often leaks into content; extract the LAST
  concrete answer or re-prompt with "jawab singkat per nomor".

## 6. Hermes vision_analyze integration
`hermes config set auxiliary.vision.provider custom:<name>` +
`auxiliary.vision.model <vision-capable model>` — but ONLY if the model is
genuinely vision-capable; a text-only model makes vision_analyze fail.
If flaky, bypass vision_analyze: curl the proxy directly with base64 image
(sections 3-5). This was the reliable path in practice.

## Support files
- `references/operator-gateways.md` — operator's actual gateway endpoints,
  header combos, and model status notes (keys redacted — read from env/config).

## Hygiene
- NEVER print API keys in output; reference env vars. Redact in any log or
  message to the operator (`sk-...[REDACTED]`).
- Save `-o /tmp/resp.json` then parse — don't pipe huge base64 bodies
  through shell variables twice (command-length limits).
