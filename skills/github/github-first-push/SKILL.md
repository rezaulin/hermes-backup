---
name: github-first-push
description: "Back up / publish an existing local or server codebase to a new GitHub repo — preflight checks, auth capability matrix, .gitignore review, first commit & push, PAT safety when user pastes a token."
tags: [github, backup, git, push, repository, source-code]
triggers:
  - backup ke github
  - backup source code
  - push ke github
  - simpan kode ke github
  - buat repo dari project
  - upload project ke github
---

# GitHub First Push (Back Up an Existing Codebase)

The user has working code somewhere (their server, a VPS, a local dir) and wants it on GitHub — usually before adding features. This skill covers the preflight → create → push sequence safely.

Note: overlaps with the bundled `github-repo-management` skill, which covers CRUD on repos that already exist. This one covers the "nothing exists yet on GitHub" path and its traps.

## Preflight (run BEFORE git init / commit)

0. **Ownership mismatch** — on servers the agent runs as `root` but projects are often owned by another user (e.g. `ubuntu`). Git then refuses everything with `fatal: detected dubious ownership in repository`. Fix once: `git config --global --add safe.directory /path/to/repo`. Do this FIRST or every git command below fails confusingly.
1. **Git state** — `git status`. If "not a git repository" but a `.git/` dir exists: `ls -la .git/`. Server projects often have an EMPTY `.git` (an init that never completed). Empty = safe to `git init` fresh; non-empty = investigate (there may be unpushed commits or a detached remote).
2. **Identity** — `git config user.name; git config user.email` (global or repo-level). Set them if empty or the first commit fails.
3. **Auth transport** — `ssh -T git@github.com` for SSH; check `gh auth status` / `GITHUB_TOKEN` for HTTPS. `~/.ssh/config` often pins a specific IdentityFile — check it if the default key isn't the right account.
4. **Does the target repo already exist?** — `git ls-remote git@github.com:OWNER/REPO.git`. "Repository not found" → doesn't exist. Never assume.
5. **Review `.gitignore` BEFORE `git add .`** — verify `.env`, compiled binaries (`.exe`, Go `main`), archives (`*.tar.gz`/`.zip`), build output (`public/dist/`), DB dumps (`*.db`, `*.sql` backups), and logs are excluded. Author a `.gitignore` first if missing. Big binaries blow up the repo forever once committed.

## Auth capability matrix (key decision point)

| Have | Can clone/push | Can CREATE repo |
|---|---|---|
| SSH key only | ✅ | ❌ |
| `gh` CLI logged in | ✅ | ✅ `gh repo create` |
| PAT (scope `repo`) | ✅ (HTTPS) | ✅ `POST https://api.github.com/user/repos` |

**SSH alone cannot create repos.** When only SSH works, offer the user the choice:
- Create an EMPTY repo manually at github.com/new (no README/.gitignore — or the first push conflicts), then agent pushes. Simplest; no secret shared.
- Paste a PAT so the agent creates the repo via API.

## Push sequence

```bash
git init -b main
git add . && git status   # eyeball the list — catch secrets/binaries before commit
git commit -m "Initial commit"
git remote add origin git@github.com:OWNER/REPO.git
git push -u origin main
```

## Handling a user-pasted PAT

- ⚠️ **Check history BEFORE asking for credentials.** Users hate re-providing secrets: "kan sudah aku kasih pat" (I already gave you the PAT). If the user implies they shared a token before, `session_search` for it (query: PAT github token + account name, sort=newest) before offering manual-repo fallbacks. Old tokens are usually expired/revoked — validate first (`GET /user`) and only then ask for a fresh one.
- The token is now in chat history — tell the user, and remind them to **revoke it when done** (GitHub Settings → Developer settings → Personal access tokens). Recommend a single-use classic PAT with only `repo` scope.
- Don't echo the token back, don't write it into files, shell history, or persistent env — use it inline for the API call(s), then let it expire/be revoked.
- Create call: `curl -s -X POST -H "Authorization: token $TOKEN" https://api.github.com/user/repos -d '{"name":"REPO","private":true}'` — default to **private** for personal codebases unless the user says otherwise.

## Rebrand / clean-slate push (new repo name, fresh history)

When the user wants the same codebase pushed under a NEW name (rebranded product, e.g. "smart-lms" → "digitalsekolah") and the old repo history is polluted with committed binaries/DBs, do NOT push the old history into the new repo. Build a fresh orphan commit:

```bash
git checkout --orphan fresh-start     # keeps working tree, discards history
git rm -r --cached . -q               # clear index completely
# write .gitignore FIRST (binaries, *.exe, *.db, .env, auth/ dirs, node_modules, dist/, *.zip, *.tar.gz)
git add -A
# MANDATORY sweeps before commit:
git diff --cached --name-only | grep -E "\.exe$|\.db$|tar\.gz|\.zip$|auth/|\.env|ecosystem\.config\.js$"
git diff --cached --name-only | while read f; do [ -f "$f" ] && echo "$(du -b "$f"|cut -f1) $f"; done | sort -rn | head -10
git rm --cached <anything bad>        # then re-run the grep sweep
git commit -m "feat: <Brand> — initial release"
git remote add origin git@github.com:OWNER/NEWNAME.git && git push -u origin main
```

- Do NOT `git stash` before the orphan checkout — the stash-pop dance conflicts with the orphan index. Go straight to `checkout --orphan` from the dirty tree.
- Old history stays in the old repo; the new repo starts at one clean commit. Tell the user this tradeoff.
- Files already TRACKED by the old HEAD leak into the new staging even with a perfect .gitignore. After `git rm -r --cached . && git add -A` always run the suspects grep + size-sorted `du -b` sweep; never commit on `git add -A` alone for server projects.

### Scrub secrets from tracked config files, don't just delete them
Server projects often track `ecosystem.config.js` / `.env.example` with real secrets baked in. Pattern: commit a sanitized `ecosystem.config.js.example` with `YOUR_*` placeholders, add the real file to .gitignore. Also scan all staged files: `grep -lE "PRIVATE_KEY|sk-[a-zA-Z0-9]{20}|BEGIN OPENSSH" $(git diff --cached --name-only)` (expect false positives on placeholder templates — check by eye).

### Go: multiple `package main` files in one dir
Server Go projects accumulate one-off scripts (`add_bendahara.go`, `seed_soal.go`…) in the root, each with its own `func main`. If all must stay tracked, prepend to each utility file:
```go
//go:build ignore
```
Then `go build ./...` works and the scripts still run via `go run file.go`. Verify with a real `go build -o /tmp/buildtest ./...` BEFORE committing — a broken build in the first commit is embarrassing and hard to undo in a clean-slate repo.

## Pitfalls

- ⚠️ **Stale duplicate directory trees silently inflate the commit.** Server projects often accumulate `tmp_extract/`, `backup/`, `old_version/`, or other full copies of the source tree alongside the real code. The `.gitignore` may cover `tmp/` but NOT `tmp_extract/`. Before committing, ALWAYS review the staged top-level: `git diff --cached --name-only | sed 's|/.*||' | sort -u` and check total: `git diff --cached --stat | tail -3`. If you see the same handler/model/frontend structure duplicated under another folder, `git rm --cached -r <dir>` it, add to `.gitignore`, and `git commit --amend`.
- ⚠️ **PAT expired or revoked on first try** — the first token a user pastes may return `401 Bad credentials`. Verify immediately before proceeding: `curl -s -H "Authorization: token $TOKEN" https://api.github.com/user`. If 401, ask user to generate a fresh classic PAT with `repo` scope at github.com/settings/tokens. Don't guess at causes — just ask for a new one. Never store the token in files or persistent env vars.
- ⚠️ **PAT redaction breaks `$(...)` token reuse in shell.** The terminal security scanner redacts anything matching a PAT pattern — including `$(cat /tmp/token.txt)` inside a command — producing broken shell like `TOKEN=*** /tmp/token.txt)` → syntax error. If a token must be reused across several commands, do it in `execute_code`: `tok = open("/tmp/token.txt").read().strip()` then build the curl command string in Python. Don't fight the redactor with creative quoting.
- ⚠️ Pushing to a repo created with a README/LICENSE → rejected (non-fast-forward). Tell user: create it truly empty, or agent must pull --rebase first.
- ⚠️ Default branch mismatch: modern git uses `main`; some old configs still create `master`. Push with `-u origin main` explicitly.
- ⚠️ If the project dir has huge untracked artifacts (Docker images, node_modules, dumps), `git add .` without a proper `.gitignore` can hang or produce GB-scale commits. Always `git status` review first.
