#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AUTO-GENERATED from Cybermes skill: claude-bughunter/hunt-shadow-api

Skill: Path-based versioning
Desc : Hunt shadow / zombie / undocumented API surface (OWASP API9 Improper Inventory Management) — enumerate the full API version history (v1/v2/beta/legacy paths, header- and subdomain-based versioning), pull and diff every reachable OpenAPI/Swagger spec (including ones only findable via the Wayback Machine), and behaviorally diff old vs. current versions for auth/rate-limit/validation regressions rather than just response-shape differences. Distinct from hunt-api-misconfig, which owns exploitation once you have a spec or endpoint (mass assignment, JWT, OData, Swagger-chain attacks); distinct from hunt-subdomain, which owns host-level discovery. This skill owns the version-inventory and behavioral-diff workflow itself. Use when the target has versioned API paths, multiple specs, a changelog referencing deprecated endpoints, or a mobile app whose hardcoded backend calls look older than the current web app's.

Run:  python claude-bughunter-hunt-shadow-api.py --help
      python claude-bughunter-hunt-shadow-api.py --list
      python claude-bughunter-hunt-shadow-api.py --dump <section>
"""
import sys, json, argparse

NAME = 'claude-bughunter/hunt-shadow-api'
TITLE = 'Path-based versioning'
DESCRIPTION = "Hunt shadow / zombie / undocumented API surface (OWASP API9 Improper Inventory Management) — enumerate the full API version history (v1/v2/beta/legacy paths, header- and subdomain-based versioning), pull and diff every reachable OpenAPI/Swagger spec (including ones only findable via the Wayback Machine), and behaviorally diff old vs. current versions for auth/rate-limit/validation regressions rather than just response-shape differences. Distinct from hunt-api-misconfig, which owns exploitation once you have a spec or endpoint (mass assignment, JWT, OData, Swagger-chain attacks); distinct from hunt-subdomain, which owns host-level discovery. This skill owns the version-inventory and behavioral-diff workflow itself. Use when the target has versioned API paths, multiple specs, a changelog referencing deprecated endpoints, or a mobile app whose hardcoded backend calls look older than the current web app's."

PAYLOADS = {
    'main': ["name: hunt-shadow-api", "description: \"Hunt shadow / zombie / undocumented API surface (OWASP API9 Improper Inventory Management) \u2014 enumerate the full API version history (v1/v2/beta/legacy paths, header- and subdomain-based versioning), pull and diff every reachable OpenAPI/Swagger spec (including ones only findable via the Wayback Machine), and behaviorally diff old vs. current versions for auth/rate-limit/validation regressions rather than just response-shape differences. Distinct from hunt-api-misconfig, which owns exploitation once you have a spec or endpoint (mass assignment, JWT, OData, Swagger-chain attacks); distinct from hunt-subdomain, which owns host-level discovery. This skill owns the version-inventory and behavioral-diff workflow itself. Use when the target has versioned API paths, multiple specs, a changelog referencing deprecated endpoints, or a mobile app whose hardcoded backend calls look older than the current web app's.\"", "sources: owasp_api_top10_2023, portswigger_research, public_research", "report_count: 0"],
    'owasp-api9-improper-inventory-management-shadow-zombie-apis': ["As an API evolves, old versions and internal/staging routes routinely stay reachable without", "receiving the same security fixes as the current version \u2014 because nobody tracks that they", "still exist. The bug is rarely in one endpoint; it's in the **delta** between what an old", "version enforces and what the current version enforces on the same operation."],
    'when-to-use': ["Trigger when:", "- Versioned paths are visible (`/v1/`, `/v2/`, `/api/2023-01-01/`) or `Accept`/`X-API-Version`", "headers are in play.", "- A changelog, release notes, or deprecation notice references removed/old API behavior.", "- A mobile APK/IPA (via `apk-redteam-pipeline` / `ios-redteam-pipeline`) hardcodes endpoints", "that look like an older backend version than the current web app calls.", "- Multiple OpenAPI/Swagger specs are discoverable, or `info.version` in one spec implies others", "exist.", "DO NOT use for single-version APIs with no version history \u2014 there's nothing to diff; go", "straight to `hunt-api-misconfig` for direct exploitation of the one surface that exists."],
    'stage-1-enumerate-the-full-version-surface': ["```bash"],
    'path-based-versioning': ["for v in v1 v2 v3 v4 beta alpha internal legacy old 2022-01-01 2023-01-01 2024-01-01; do", "curl -s -o /dev/null -w \"%{http_code} /api/$v/\\n\" \"https://$TARGET/api/$v/\""],
    'header-based-versioning': ["curl -s -H \"X-API-Version: 1\" https://$TARGET/api/users", "curl -s -H \"Accept: application/vnd.company.v1+json\" https://$TARGET/api/users"],
    'subdomain-based-versioning': ["for sub in api api-v1 api-v2 apiv1 apiv2 legacy-api old-api internal-api staging-api; do", "curl -s -o /dev/null -w \"%{http_code} $sub\\n\" \"https://$sub.$TARGET/\"", "A `200`/`401`/`403` on an old version path (anything but `404`/connection-refused) means the", "version is still live and worth carrying into Stage 3, even if it demands auth."],
    'stage-2-pull-every-reachable-spec-not-just-the-linked-one': ["```bash", "for path in openapi.json swagger.json v1/swagger.json v2/swagger.json v3/api-docs \\", "api-docs.json swagger/v1/swagger.json .well-known/openapi.json; do", "curl -s -o /dev/null -w \"%{http_code} /$path\\n\" \"https://$TARGET/$path\""],
    'wayback-machine-a-deprecated-version-s-spec-often-stays-indexed-after-the-live-link-is-removed': ["curl -s \"http://web.archive.org/cdx/search/cdx?url=$TARGET/*swagger*&output=json&collapse=urlkey\"", "curl -s \"http://web.archive.org/cdx/search/cdx?url=$TARGET/*openapi*&output=json&collapse=urlkey\"", "When more than one spec resolves (a current one and an archived/old one), diff the endpoint", "inventories directly:", "```bash", "jq -r '.paths | keys[]' v1-swagger.json | sort > /tmp/v1_paths.txt", "jq -r '.paths | keys[]' v2-swagger.json | sort > /tmp/v2_paths.txt", "comm -23 /tmp/v1_paths.txt /tmp/v2_paths.txt   # in v1 only \u2014 candidates for \"still live but forgotten\"", "For every path in that diff, confirm it's still reachable against the v1 base URL. A route", "documented only in the old spec that still returns something other than `404` is a zombie-", "endpoint candidate \u2014 carry it into Stage 3."],
    'stage-3-behavioral-diff-between-old-and-current-version': ["For each operation that exists in **both** versions, compare security-relevant behavior, not", "response shape. Response shape differences are Informational; behavioral security regressions", "are the finding.", "- **Auth strength.** Does the old version accept no token, an expired token, or a lower-", "privilege token that the current version rejects?", "```bash", "curl -s -H \"Authorization: Bearer $EXPIRED_TOKEN\" https://$TARGET/api/v1/users/me -w '\\n%{http_code}\\n'", "curl -s -H \"Authorization: Bearer $EXPIRED_TOKEN\" https://$TARGET/api/v2/users/me -w '\\n%{http_code}\\n'", "- **Rate limiting.** Burst the same number of requests against both versions' equivalent", "endpoint; a missing `429` on the old version means rate-limiting was added later and never", "backported.", "- **Input validation.** Send the identical injection/oversized/malformed payload to both; the", "old version accepting what the new one rejects means hardening happened forward-only \u2014", "chain into whichever injection class the payload targets (`hunt-sqli`, `hunt-idor`, etc.).", "- **Field exposure.** Does the old version's response body include fields \u2014 internal IDs, other", "users' data, internal notes, PII \u2014 that the current version has since redacted?"],
    'stage-4-deprecated-internal-routes-never-referenced-by-the-current-ui': ["- Grep JS bundles for API calls no visible UI flow triggers (`/internal/`, `/admin/`, `/debug/`,", "`/_internal/`, `/test/`, `/staging/`) \u2014 reuse `hunt-source-leak`'s JS-bundle grep patterns for", "this specifically.", "- Check `robots.txt` / `sitemap.xml` for disallowed API paths \u2014 a self-inflicted disclosure.", "- Mobile-app endpoint inventories (via `apk-redteam-pipeline` / `ios-redteam-pipeline`) very", "often reference an older backend version than the current web app calls. Treat every", "APK/IPA-sourced endpoint as a version-diff candidate against the live web API."],
    'false-positive-gate': ["- A version difference alone (different response shape, cosmetic field renaming) is", "Informational. The finding is a **security-relevant regression** \u2014 auth, rate-limit, or", "validation that got weaker going backward in version history.", "- Confirm the old endpoint is not simply an alias/proxy to the current implementation before", "claiming a behavioral difference \u2014 send a payload that would actually behave differently", "under old vs. new logic, not just compare a version string in the response body.", "- A `200` on a path that just serves a static \"this API version is deprecated, use v2\" message", "is not a finding \u2014 confirm the underlying operation still executes."],
    'severity-table': [],
    'related-skills-chains': ["- **`hunt-api-misconfig`** \u2014 owns exploitation once a spec or endpoint is in hand (mass", "assignment, JWT attacks, OData, Swagger-chain attacks). This skill hands it a sharper target:", "\"here's a zombie endpoint with weaker validation than the current one.\"", "- **`hunt-subdomain`** \u2014 owns host/subdomain-level discovery (`api-v1.target.com` as its own", "host, potential takeover). This skill owns what happens once you're inside a given host's", "version surface.", "- **`hunt-source-leak`** \u2014 JS-bundle grep for internal/undocumented calls; reused here", "specifically for version-diffing rather than secret extraction.", "- **`apk-redteam-pipeline`** / **`ios-redteam-pipeline`** \u2014 mobile builds routinely hardcode an", "older API version; every mobile-sourced endpoint is a version-diff candidate.", "- **`hunt-brute-force`** \u2014 a rate-limit regression found here is only a complete finding once", "chained to actual brute-forceable impact (login, OTP, enumeration)."],
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