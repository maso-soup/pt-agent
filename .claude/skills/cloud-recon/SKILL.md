---
name: cloud-recon
description: Map an organization's cloud footprint across AWS/Azure/GCP — accounts/subscriptions/projects, exposed services, storage, and subdomains pointing at cloud infrastructure — as the first phase of an authorized cloud penetration test. Use when starting a new cloud engagement or asked to enumerate what an organization runs in the cloud.
---

## Purpose

Cloud attack surface is often wider than what's in the client's own asset
inventory (shadow IT buckets, forgotten dev accounts, subdomains pointing at
decommissioned services). Recon here means finding the real footprint before
looking for misconfigurations in it.

## When to use

Start of any cloud engagement, once the specific accounts/subscriptions/
projects (or the domains to discover them from) are confirmed in scope.

## Methodology

1. Confirm scope: exact AWS account IDs / Azure subscription IDs / GCP project
   IDs, or the domains/org name to discover them from if not directly provided.
2. **Subdomain & DNS enumeration** — find hostnames pointing at cloud-hosted
   infrastructure (S3 website endpoints, Azure blob/app service domains, GCP
   equivalents) via passive sources and DNS brute forcing.
3. **Storage discovery** — enumerate likely bucket/container names (company
   name, product name, common suffixes like `-backup`, `-dev`, `-logs`) across
   all three providers regardless of which one is "primary" — orgs frequently
   have stray resources in a secondary provider.
4. **Service inventory** — where credentials or a read-only role are provided,
   enumerate compute, storage, IAM, and network resources directly via
   provider APIs/CLIs rather than guessing from outside.
5. Consolidate into an asset inventory: what's public and reachable
   unauthenticated vs. what requires the provided access level.

## Tools

- `cloud_enum` / `CloudRecon`-style multi-provider bucket & subdomain brute
  forcing tools.
- Provider CLIs (`aws`, `az`, `gcloud`) for authenticated inventory once
  credentials/roles are provided.
- Passive subdomain sources (certificate transparency logs, public DNS
  datasets) before any active brute forcing.

## Output

Inventory of in-scope accounts/projects, discovered public-facing cloud
assets (buckets, subdomains, exposed services), and a flagged list of
anything that looks immediately misconfigured (public bucket listing,
unauthenticated management endpoint) for handoff to the matching foothold
skill.

## Safety notes

- Bucket/subdomain brute forcing generates a lot of requests against
  provider-owned infrastructure (not just the client's) — keep volume
  reasonable and stop if a provider abuse warning appears.
- Only enumerate accounts/projects explicitly named in scope, even if a
  discovered resource hints at a related, unlisted account.
