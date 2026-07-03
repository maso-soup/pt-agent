---
name: kerberos-attacks
description: Perform Kerberoasting and AS-REP roasting against Active Directory to obtain crackable credential hashes for an initial foothold. Use when the target is a domain-joined Windows environment and valid (even low-privileged) domain credentials, or unauthenticated LDAP/Kerberos access, are available.
---

## Purpose

Kerberos ticket-based attacks let you turn a single low-privileged domain
account (or in some cases zero credentials) into crackable password hashes for
service accounts or misconfigured user accounts — a very common real-world path
from "domain user" to "domain foothold with a better account."

## When to use

- Domain-joined environment confirmed during recon (DNS/LDAP/Kerberos ports
  open, domain controller identified).
- Any valid domain credential is available (even a low-privilege one obtained
  via [credential-spraying](../credential-spraying/SKILL.md)), or AS-REP roasting
  candidates exist (accounts with Kerberos pre-authentication disabled).

## Methodology

1. **Enumerate SPNs**: query the domain for service accounts with a Service
   Principal Name set — these are Kerberoastable.
2. **Kerberoasting**: request a service ticket (TGS) for each SPN account using
   any valid domain credential; the ticket is encrypted with the service
   account's password hash and can be cracked offline.
3. **AS-REP roasting**: identify accounts with "Do not require Kerberos
   preauthentication" set; request their AS-REP without any credential at all
   and crack the returned hash offline.
4. **Offline cracking**: run recovered hashes through a cracker with a
   targeted wordlist (company-specific terms first, then a general list).
5. Validate any cracked credential against a benign action before treating it
   as a foothold.

## Tools

- `GetUserSPNs.py` / `GetNPUsers.py` (Impacket) for Kerberoasting and AS-REP
  roasting requests respectively.
- `john` or the Kali MCP `john_crack` tool for offline hash cracking
  (`krb5tgs`/`krb5asrep` formats).

## Output

List of Kerberoastable/AS-REP-roastable accounts, which hashes were recovered,
which were cracked, and the resulting credential's privilege level.

## Safety notes

- Requesting service tickets is itself low-risk/low-noise, but cracking
  attempts and any resulting credential use should be logged just as carefully
  as any other credential-based access.
- Service accounts are often highly privileged (SQL, backup, scheduled task
  accounts) — treat a cracked service account credential as a potential
  escalation path and confirm scope before using it further.
