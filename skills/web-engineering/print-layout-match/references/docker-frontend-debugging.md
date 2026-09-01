# Docker Frontend Deployment Debugging — When Changes Don't Appear

Root cause for "perbaikan tidak terdeploy": HTML files served from **inside Docker container**, NOT host filesystem.

## Quick Fix Pattern

1. **Check serve location inside container:**
```bash
docker exec <container_name> cat /app/public/dist/rapot.html | grep HEADER
```

2. **Compare with local edit:**
```bash
cat /path/to/frontend/rapot.html | grep HEADER
```

3. **Fix options:**
- Temporary: `docker cp ./rapot.html <container>:/app/public/dist/`
- Permanent: `docker compose build --no-cache && docker compose up -d app`

⚠️ Vite + Go backend workflow: Edit `/frontend/` → `npm run build` → Docker copies to image → Container serves from `/app/public/dist/`. Editing `/frontend/` alone doesn't work!

## Verification Script
```python
result = terminal(
    command="docker exec simmubtadiat-app-1 cat /app/public/dist/rapot.html | grep 'items-start'"
)
assert 'items-start' in result['output'], "Wrong version deployed!"
```

**Lesson**: Always verify actual serve location before assuming code change failed. (Source: SIM Mubtadiat 2026-08-25 session)