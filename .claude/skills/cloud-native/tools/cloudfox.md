# CloudFox

- **Category**: Cloud-Native / Cloud Situational Awareness
- **Risk Level**: 🟡 Medium

---

## Description

CloudFox (Bishop Fox) helps gain situational awareness in unfamiliar cloud environments by enumerating resources and surfacing exploitable attack paths from an existing set of credentials. Strongest for AWS, with growing Azure and GCP support. Read-only enumeration — use it after obtaining cloud credentials (or an assumed role) to quickly map inventory, permissions, exposed secrets, and public endpoints before deciding where to focus exploitation.

## Installation

```bash
go install github.com/BishopFox/cloudfox@latest
```

Alternative (prebuilt binary):

```bash
wget https://github.com/BishopFox/cloudfox/releases/latest/download/cloudfox-linux-arm64.zip
unzip cloudfox-linux-arm64.zip
chmod +x cloudfox
sudo mv cloudfox /usr/local/bin/
```

## Parameter Reference

### Global Flags

| Parameter | Description |
|-----------|-------------|
| `-p, --profile <name>` | AWS CLI profile to use |
| `-a, --profile-all` | Run against all profiles in the AWS credentials file |
| `-r, --region <region>` | Limit to a specific AWS region |
| `-t, --account-id <id>` | Target account ID (multi-account setups) |
| `-o, --output <format>` | Output format: `table`, `csv`, or `json` |
| `--outputdirectory <dir>` | Output directory for results |
| `--wrap` | Wrap long table output instead of truncating |
| `-v, --verbosity <int>` | Verbosity level (0-2) |

### Key AWS Subcommands

| Subcommand | Description |
|-----------|-------------|
| `all-checks` | Run all AWS recon modules against the account |
| `inventory` | Inventory of resources per region |
| `permissions` | Enumerate IAM permissions for the current principal |
| `role-trusts` | Map IAM role trust relationships (cross-account/privesc paths) |
| `principals` | List all IAM users and roles in the account |
| `access-keys` | List active IAM access keys |
| `instances` | EC2 instance inventory with roles and public IPs |
| `buckets` | S3 bucket inventory |
| `secrets` | Secrets Manager and SSM Parameter Store secrets |
| `env-vars` | Environment variables from Lambda, ECS, and EC2 (common secret leak point) |
| `endpoints` | Public-facing endpoints (ALB, API Gateway, CloudFront, etc.) |
| `network-ports` | Security group rules mapped to exposed ports |
| `inbound-assumed-roles` / `outbound-assumed-roles` | Cross-account role assumption paths |
| `organizations` | AWS Organizations structure, if accessible |

### Azure Subcommands

| Subcommand | Description |
|-----------|-------------|
| `whoami` | Show enumerated Azure identity/subscription context |
| `rbac` | Enumerate Azure RBAC role assignments |
| `vms` | Azure VM inventory |
| `storage` | Azure Storage account inventory |

## Common Commands

```bash
# Run all AWS recon modules using a named profile
cloudfox aws --profile <profile> all-checks

# Quick permissions check for the current identity
cloudfox aws --profile <profile> permissions

# Look for exposed secrets in env vars, Secrets Manager, and SSM
cloudfox aws --profile <profile> secrets
cloudfox aws --profile <profile> env-vars

# Map role trust relationships for privilege escalation / lateral movement
cloudfox aws --profile <profile> role-trusts

# Enumerate public-facing endpoints
cloudfox aws --profile <profile> endpoints

# Run against every profile in the credentials file
cloudfox aws --profile-all all-checks

# Azure identity and RBAC enumeration
cloudfox azure whoami
cloudfox azure rbac
```

## Notes & Tips

1. Run `permissions` first to confirm what the current principal can actually enumerate before running `all-checks` — avoids wasted calls against denied services.
2. `role-trusts` and `inbound-assumed-roles`/`outbound-assumed-roles` are the fastest way to spot cross-account privilege escalation paths; pivot to `pacu`'s `iam__privesc_scan` to confirm exploitability.
3. `secrets` and `env-vars` frequently surface hardcoded credentials in Lambda/ECS/EC2 configuration — treat any hits as sensitive findings requiring cross-host credential testing.
4. Results are stored locally under `~/.cloudfox/` by default in addition to any `--outputdirectory` — clean up or secure this path after the engagement.
5. CloudFox is read-only enumeration (API `Describe`/`List`/`Get` calls) but still generates CloudTrail activity — coordinate with the engagement scope like any other AWS API activity.
6. Use CloudFox for fast attack-surface discovery from credentials already obtained; use `prowler`/`scoutsuite` for compliance-oriented configuration audits, and `pacu` once a specific exploitation path is identified.

---

## Official References

- [CloudFox GitHub](https://github.com/BishopFox/cloudfox)
- [CloudFox Documentation](https://github.com/BishopFox/cloudfox/wiki)
