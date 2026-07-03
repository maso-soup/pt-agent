---
name: llmnr-nbns-poisoning
description: Poison LLMNR/NBT-NS/mDNS broadcast name resolution to capture NTLM authentication hashes for offline cracking or relay, as an initial foothold technique on Windows networks. Use when network-recon shows a Windows-heavy internal network with these legacy protocols still enabled.
---

## Purpose

Windows falls back to broadcast name resolution (LLMNR/NBT-NS) when DNS fails.
An on-path attacker can answer those broadcast queries directly, tricking
clients into authenticating to it and handing over an NTLMv2 hash — one of the
most reliable initial-foothold techniques on internal Windows networks that
haven't hardened these legacy protocols.

## When to use

Internal, on-network engagements (this requires L2 network access, not
internet-facing) where recon shows a Windows-dominant environment. Confirm the
RoE explicitly authorizes active on-path attacks, not just passive scanning —
this technique intercepts other users' authentication traffic.

## Methodology

1. Confirm you're positioned on the same broadcast domain as target hosts.
2. Run a listener that answers LLMNR/NBT-NS/mDNS queries, optionally combined
   with SMB/HTTP signing-disabled relay if the environment allows it.
3. Let it run passively for a representative window (not just a few minutes —
   broadcast queries are often triggered by mistyped share paths or periodic
   client behavior).
4. Take captured NetNTLMv2 hashes offline for cracking, or relay live
   authentication attempts (if SMB signing is disabled) directly to another
   host for immediate access without cracking.
5. Document which hosts/users authenticated and by what mechanism.

## Tools

- `Responder` — the standard tool for LLMNR/NBT-NS/mDNS poisoning and hash
  capture.
- `ntlmrelayx` (Impacket) — relay captured authentication to a target with SMB
  signing disabled, for direct access instead of offline cracking.
- `john`/`hashcat` for offline NetNTLMv2 cracking.

## Output

Captured hashes (or successful relay sessions) with source host/user, and
either the cracked plaintext or the access obtained via relay.

## Safety notes

- This intercepts real users' authentication traffic — make sure the RoE
  explicitly covers on-path/MITM-style techniques, not just passive scanning.
- Relaying to a target other than the one the credential owner intended is a
  more invasive action than passive capture; confirm this is in scope before
  relaying rather than just capturing for offline cracking.
- Run for a bounded, agreed-upon window and stop — don't leave a poisoner
  running unattended for the whole engagement.
