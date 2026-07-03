---
name: ssrf-to-metadata
description: Chain a server-side request forgery vulnerability in a cloud-hosted application into instance metadata service access to steal cloud credentials, as an initial cloud foothold. Use when a web app pentest finds SSRF and the target runs on AWS/Azure/GCP compute.
---

## Purpose

Instance metadata services (IMDS) hand out temporary cloud credentials to
anything running on the instance, on the assumption that only the instance
itself can reach that address. An SSRF vulnerability breaks that assumption,
letting an external attacker pull those credentials through the vulnerable
app — one of the most common web-to-cloud foothold chains in real breaches.

## When to use

An SSRF finding (see the web application domain's
[ssrf-exploitation](../ssrf-exploitation/SKILL.md) skill) exists in an app
confirmed or suspected to run on cloud compute (AWS EC2/ECS/Lambda, Azure VM/
App Service, GCP Compute Engine/Cloud Run).

## Methodology

1. Confirm the SSRF can reach the provider's metadata IP
   (`169.254.169.254` for AWS/Azure/GCP's legacy endpoint, or provider-specific
   equivalents) and isn't blocked by network policy.
2. Identify the provider from response format — each has a distinct metadata
   API shape (AWS IMDSv1/v2 path structure, Azure `Metadata: true` header
   requirement, GCP `Metadata-Flavor: Google` header requirement).
3. **Check for IMDSv2 (AWS) or equivalent hardening** — session-oriented
   metadata access requires a PUT-based token request first; a pure SSRF that
   can only do simple GETs may not be able to reach hardened IMDSv2 endpoints,
   which is itself worth reporting as effective mitigation.
4. If reachable, retrieve the attached instance role's temporary credentials
   from the metadata path.
5. Immediately test what those credentials can actually do — feed them into
   [iam-misconfig-enum](../iam-misconfig-enum/SKILL.md) rather than assuming
   impact from possession alone.

## Tools

- The SSRF vulnerability itself (via `curl`/Burp Repeater through the
  vulnerable parameter) pointed at the metadata IP/path.
- `ssrfmap` for automating common metadata-path payloads once SSRF is
  confirmed.
- Provider CLIs, once credentials are retrieved, to test their actual scope.

## Output

Confirmation of metadata reachability, the retrieved role name and temporary
credentials (redacted in the report), and the permission scope those
credentials actually grant.

## Safety notes

- Retrieved credentials are live and time-limited — use them only long enough
  to confirm scope (e.g. `sts get-caller-identity` / an equivalent read-only
  call), then stop; don't use them to browse broadly.
- Report and follow the client's rotation process for any credentials
  retrieved this way rather than holding onto them.
