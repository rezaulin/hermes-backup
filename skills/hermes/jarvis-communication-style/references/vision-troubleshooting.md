# Vision Provider Troubleshooting Reference

## Error Symptoms & Diagnoses

### Symptom: 429 "No active credentials for provider: openai"

**Root cause:** Vision tool using misconfigured custom provider override instead of user's expected model.

**Diagnostic commands:**
```bash
# Check vision override configuration
hermes config show | grep -A2 "Vision"

# Verify API key status
hermes status | grep -A30 "API Keys"

# Test underlying HTTP connectivity (if known endpoint)
curl -I https://rkdeqfz.abc-tunnel.us
```

**Typical mismatch scenario:**
- User activates Opus 4.8 via `gorouter` or similar
- Config has stale/incorrect override: `Vision provider=custom:rkdeqfz.abc-tunnel.us, model=qmodel_38max`
- Actual endpoint returns expired credentials error (429)

## Fix Patterns

### Option A: Redirect to correct provider
```bash
hermes config set vision.provider custom:gorouter
```

### Option B: Set specific model (keeps existing provider)
```bash
hermes config set vision.model opus-4.8
```

### Option C: Remove override (use default model)
```bash
hermes config unset vision.provider
```

### Option D: Disable auxiliary vision override entirely
Check if global fallback chain should handle vision — remove line from config.yaml:
```yaml
auxiliary_models:
  # vision: ...  # Remove or comment out this line
```

## Verification Steps

After applying fix:
```bash
# Re-check config
hermes config show | grep -A2 "Vision"

# Verify model resolves correctly
hermes status | grep -A5 "Model:"

# Test with actual image
vision_analyze(image_url="/path/to/image.jpg", question="What is this?")
```

## Related Commands

- `hermes config edit` - Manual YAML editing
- `hermes config set <key> <value>` - Key-value config updates
- `hermes config unset <key>` - Remove config entry
- `hermes doctor` - Full system health check

## Notes

- Custom provider overrides are **per-session dangerous** — can silently fail
- Always verify before assuming provider is working
- abc-tunnel.us endpoints appear in some hermes installations — verify availability
- OpenRouter credentials may expire; refresh via `hermes login openrouter`
