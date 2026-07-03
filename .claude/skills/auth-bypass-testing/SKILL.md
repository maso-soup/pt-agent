---
name: auth-bypass-testing
description: Test authentication, session management, and access-control logic for bypass vulnerabilities (broken auth, IDOR, privilege escalation via role/ID manipulation) as an initial foothold or account-takeover path. Use when webapp-recon maps login flows, session tokens, or multi-tenant/role boundaries.
---

## Purpose

Broken authentication and access control let an attacker act as another user
(or a higher-privileged one) without needing to exploit a technical
vulnerability like injection — often the highest business-impact class of web
app finding because it directly demonstrates account/data compromise.

## When to use

After [webapp-recon](../webapp-recon/SKILL.md) maps login flows, session
tokens, password reset flows, or any endpoint that takes a user/object ID as a
parameter.

## Methodology

1. **Session token analysis**: check token generation for predictability, and
   token handling for missing expiration, lack of invalidation on logout, or
   acceptance across unrelated sessions.
2. **IDOR / broken object-level access**: for any endpoint taking a
   user/object ID, test whether changing the ID grants access to another
   user's data while authenticated as a low-privilege account.
3. **Privilege escalation via role manipulation**: test whether client-side
   role/permission fields (hidden form fields, JWT claims, manipulable
   parameters) are trusted without server-side re-validation.
4. **Password reset / account recovery flow**: test for host-header injection
   into reset links, predictable reset tokens, or missing rate limiting
   enabling token brute force.
5. **Multi-tenancy boundary testing**: in multi-tenant apps, confirm one
   tenant's authenticated session cannot reach another tenant's data via
   direct object reference or API parameter manipulation.

## Tools

- Burp Suite (Repeater/Intruder) for manual and semi-automated parameter
  manipulation across two authenticated sessions (low-priv and victim/higher-
  priv) side by side.
- JWT-focused tooling (e.g. `jwt_tool`) for token structure and signature
  validation testing.
- Two or more test accounts at different privilege levels — this class of bug
  is very hard to find with only one account.

## Output

Confirmed bypass(es) with the exact request demonstrating access to another
user's data or elevated privilege, and which control (missing server-side
check, predictable ID, trusted client-side field) failed.

## Safety notes

- Testing with real other users' accounts/data is out of scope by default —
  use dedicated test accounts created for the engagement, not live customer
  accounts, unless the RoE explicitly provides for it.
- Stop at proving access is possible (e.g. viewing one other test account's
  data) rather than broadly harvesting data across many accounts.
