---
name: credential-spraying
description: Perform low-and-slow password spraying against exposed authentication services (SSH, RDP, WinRM, web logins) to gain an initial foothold without triggering account lockouts. Use when network-recon finds exposed login services and default/weak credentials are a plausible path in.
---

## Purpose

A small number of common/seasonal passwords sprayed across many accounts (rather
than many passwords against one account) is often faster and stealthier than
brute force, and is one of the most common real-world initial-access techniques.

## When to use

After recon identifies exposed SSH/RDP/WinRM/web-login services and a valid
username list exists or can be derived (e.g. from OSINT, email format
conventions, or prior enumeration).

If the login belongs to a fingerprinted, versioned, open-source product
(rather than a generic OS-level login), exhaust
[vulnerable-service-exploitation](../vulnerable-service-exploitation/SKILL.md)'s
CVE/advisory-research workflow first — including that skill's full
advisory-list check, not just an initial search. A known misconfiguration or
credential-disclosure vector on well-known software is often faster to find
and far less noisy than spraying, and spraying a login form should be a
fallback once the CVE angle is genuinely exhausted, not the default first
move just because a valid username was confirmed.

## Methodology

1. Build a username list (from OSINT, LinkedIn/company naming convention,
   or prior AD/LDAP enumeration).
2. Build a small, high-signal password list (season+year, company name
   variants, "Password1!"-style patterns, previously breached passwords for
   this org if legitimately available) — not a giant dictionary.
3. **Spray one password across all usernames**, then wait out the account
   lockout window before trying the next password. Never do the reverse
   (many passwords per user) — that's what triggers lockouts.
4. Validate any hit against a second, low-privilege action to confirm it's a
   real credential, not a false positive.
5. Document exactly which account/password/service/timestamp succeeded.

## Tools

- `hydra` with a single password and full
  user list, `-t` kept low for stealth, against `ssh`, `rdp`, `winrm` modules.
- `kerbrute` for AD environments — validates usernames and sprays against
  Kerberos pre-auth without generating Windows event log noise the same way
  interactive logon attempts do.

## Output

Confirmed valid credential pairs, the service/host they work against, and what
level of access they grant.

## Safety notes

- Always confirm the account lockout threshold and window from the RoE/client
  before spraying — get this wrong and you lock out real users, potentially
  including the ones who authorized the test.
- Prefer a single password per user per lockout window; never spray faster than
  the documented safe rate.
- Stop immediately and report if you see signs of monitoring/alerting firing —
  that's useful detection-capability information for the client either way.
