---
name: default-creds-admin-panels
description: Identify exposed admin/management interfaces and test default or weak credentials for direct administrative access, as an initial foothold. Use when webapp-recon discovers admin panels, CMS dashboards, or management interfaces (e.g. via content discovery or known default paths).
---

## Purpose

Admin panels reachable from the internet with default or weak vendor
credentials still turn up regularly, and grant immediate high-privilege
access — no injection or logic bug required, just an unchanged default
password.

## When to use

After [webapp-recon](../webapp-recon/SKILL.md) discovers admin/login panels —
CMS dashboards (WordPress `/wp-admin`, etc.), framework admin interfaces,
device/appliance web management UIs fronted by the same web stack, or
vendor-specific product admin consoles.

## Methodology

1. Identify the exact product/platform and version powering the admin panel
   (via headers, login page branding, static asset paths).
2. Check for the platform's documented default credentials first — many
   products ship with a known default admin account that's frequently left
   unchanged.
3. If no known default applies, try a short, targeted list of common weak
   credentials (`admin`/`admin`, company-name-based guesses) — not a large
   generic wordlist; this should be fast and low-noise.
4. Respect any account lockout policy — space attempts to avoid locking out
   legitimate admin users.
5. On success, confirm access level and stop — document what the panel
   controls rather than using it to make changes.

## Tools

- `wpscan` for WordPress-specific
  credential and plugin/theme vulnerability checks.
- `hydra` for a small, targeted
  credential list against the login form.
- Vendor default-credential references kept in engagement notes.

## Output

Confirmed admin panel, the credential that worked, and what level of control
it grants (content management vs. full server/plugin code execution
capability, e.g. via theme/plugin editors).

## Safety notes

- Many CMS admin panels allow theme/plugin editing that leads directly to
  code execution — treat successful admin login as a potential escalation to
  full RCE and confirm that's in scope before going further than logging in.
- Avoid making persistent changes (new users, modified content, installed
  plugins) beyond what's needed to prove access; revert anything necessarily
  changed during testing.
