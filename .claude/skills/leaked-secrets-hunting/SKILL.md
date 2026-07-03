---
name: leaked-secrets-hunting
description: Search public and semi-public sources (source repos, CI/CD configs, build artifacts, container images) for leaked cloud credentials and API keys as an initial cloud foothold. Use during OSINT/recon when the target has public repos, public CI logs, or publicly pushed container images.
---

## Purpose

Developers routinely commit cloud keys, hardcode them in CI configs, or bake
them into container images — these leaks give direct, working credentials
without needing to exploit anything, making this one of the fastest paths to
an initial cloud foothold when it applies.

## When to use

Target organization has public GitHub/GitLab repos, public CI build logs,
publicly pushed container images (Docker Hub, public ECR/GCR), or an
externally-facing developer-adjacent surface (Jenkins, exposed `.git`
directories on web servers).

## Methodology

1. Enumerate public repos belonging to the org and its known
   employees/contractors (via org membership, commit email domains).
2. Search commit history — not just current file contents — for credential
   patterns; secrets are frequently added and then "removed" in a later commit
   while remaining in history.
3. Check CI/CD configs and their public logs for hardcoded secrets or secrets
   accidentally echoed to build output.
4. Check publicly accessible container images for baked-in credentials,
   `.env` files, or cloud config files left in image layers.
5. For any exposed `.git` directory found on a live web server during
   [webapp-recon](../webapp-recon/SKILL.md), reconstruct history the same way.
6. Validate any found credential is live before reporting it as a finding
   (a single read-only API call), and immediately note it for rotation.

## Tools

- `trufflehog` / `gitleaks` — pattern and entropy-based secret scanning across
  repo history.
- `git-dumper` for reconstructing exposed `.git` directories found on live
  servers.
- `docker history` / `dive` for inspecting container image layers for baked-in
  secrets.

## Output

Each leaked secret's location (repo/commit/file or image layer), a redacted
confirmation it's live, and its scope (what it authenticates to and what
permissions it carries, via
[iam-misconfig-enum](../iam-misconfig-enum/SKILL.md)).

## Safety notes

- Validate with the single least-invasive call possible — this is still
  credential use against a real account and should be treated with the same
  care as any other credential-based access.
- Never post-process or persist harvested secrets beyond what the report
  needs; flag for immediate rotation per the RoE's handling process.
