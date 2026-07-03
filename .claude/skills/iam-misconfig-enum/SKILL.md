---
name: iam-misconfig-enum
description: Enumerate IAM roles, users, policies, and trust relationships across AWS/Azure/GCP to find over-permissioned identities and privilege escalation paths. Use once initial cloud credentials or a role are available (from a foothold, a provided test account, or leaked keys) and the goal is to map what access they actually grant.
---

## Purpose

Cloud breaches are rarely "the storage bucket was public" alone — they're
usually a foothold identity with far more IAM permission than intended,
letting an attacker pivot from "one leaked key" to "account admin." This skill
maps that blast radius.

## When to use

Any time a credential, access key, or assumable role becomes available —
whether from [leaked-secrets-hunting](../leaked-secrets-hunting/SKILL.md),
[ssrf-to-metadata](../ssrf-to-metadata/SKILL.md), or a client-provided starting
credential for an authenticated assessment.

## Methodology

1. Identify the current identity's own attached and inherited permissions
   (direct policies, group memberships, role assumptions).
2. Enumerate **what that identity can do to IAM itself** — create/attach
   policies, create access keys for other users, modify trust policies. These
   are the highest-value escalation paths.
3. Enumerate cross-account/cross-project trust relationships — roles that can
   be assumed from other accounts, federated identity providers, overly broad
   `AssumeRole`/`iam.serviceAccounts.actAs`-style permissions.
4. Look for common misconfiguration patterns: wildcard resource/action grants
   (`"Action": "*"`, `"Resource": "*"`), passable roles with high privilege
   (`iam:PassRole` to an admin role), and unused/stale keys with broad access.
5. Build a privilege-escalation graph: starting identity → reachable
   permissions → highest privilege obtainable, with the specific policy
   statements that make each step possible.

## Tools

- `pacu` (AWS) — automated IAM privilege escalation path enumeration.
- `ScoutSuite` — cross-provider configuration auditing including IAM.
- `cloudfox` — fast, read-only AWS permission and attack-surface enumeration.
- Provider CLIs directly (`aws iam simulate-principal-policy`, `az role
  assignment list`, `gcloud projects get-iam-policy`) for precise policy
  inspection.

## Output

A privilege-escalation path (or confirmation none exists) from the starting
identity to a higher-privilege one, citing the exact policy statements
involved — this is what makes the finding fixable rather than just alarming.

## Safety notes

- Enumeration (`list`/`get`/`simulate` calls) is read-only and low-risk;
  actually exercising an escalation path (creating a new access key, assuming
  a role) is a more invasive step — confirm it's in scope before doing more
  than proving the path exists on paper.
- Clean up any test principals/keys created to prove an escalation path.
