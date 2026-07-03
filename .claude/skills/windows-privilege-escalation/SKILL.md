---
name: windows-privilege-escalation
description: Systematically enumerate and exploit privilege escalation paths on a compromised Windows host — impersonation-capable token privileges, service/scheduled-task misconfigurations, unquoted service paths, stored credentials, and AlwaysInstallElevated/kernel CVEs. Use once an initial foothold (shell) is established on a Windows target and further access (SYSTEM or a domain-relevant account) is the goal.
---

## Purpose

An initial foothold is rarely the objective — this skill turns a low-privileged
shell on a Windows host into SYSTEM (or another elevated/domain-relevant
account), working through the standard privesc surface systematically
(automated triage first, then the vectors automated tools routinely miss)
rather than jumping straight to the first CVE that looks promising.

## When to use

After any foothold skill (in any domain — network, web application, etc.)
lands a shell on a Windows host and the RoE permits escalation. Pairs
naturally with [kerberos-attacks](../kerberos-attacks/SKILL.md) and
[smb-enum-exploitation](../smb-enum-exploitation/SKILL.md) in AD
environments, and with [vulnerable-service-exploitation](../vulnerable-service-exploitation/SKILL.md)
for the CVE-research workflow once a specific OS build/patch level is
identified.

## Methodology

1. **Baseline enumeration** — `whoami /all` (user, groups, **and token
   privileges** — `SeImpersonatePrivilege`, `SeBackupPrivilege`,
   `SeDebugPrivilege`, and `SeTakeOwnershipPrivilege` are each direct
   escalation vectors on their own), `systeminfo` (OS build/patch level),
   and any credentials already captured during the foothold.
2. **Automated triage** — run WinPEAS (or PowerUp.ps1 / Seatbelt as
   alternatives) against the session, and Metasploit's
   `post/multi/recon/local_exploit_suggester` (via the Metasploit MCP
   server's `run_post_module`, against the active session). Same caveat as
   Linux: verify any build-number-based CVE suggestion against the actual
   patch level (installed KBs / Windows Update history), not just the
   marketing OS version — a suggester tool working off the OS version alone
   will false-positive on a patched build.
3. If an **impersonation-capable token privilege** is present (most
   commonly `SeImpersonatePrivilege`, held by many service accounts by
   default), that's usually the fastest path to SYSTEM — try a
   Potato-family exploit (JuicyPotato / PrintSpoofer / RoguePotato /
   GodPotato, whichever fits the OS build) before more time-consuming manual
   enumeration.
4. Independently check the classic manual vectors even when automated tools
   don't flag them:
   - Service binary/config permissions — `sc qc <service>` plus an ACL check
     (`icacls`) on the binary path and any DLLs it loads; unquoted service
     paths containing a space (e.g. `C:\Program Files\...`) where an
     earlier, writable path segment can hijack execution
   - Scheduled tasks running as SYSTEM/admin with a writable target
     script/binary
   - `AlwaysInstallElevated` registry keys (both HKLM and HKCU must be set)
     enabling arbitrary MSI-based SYSTEM execution
   - Stored/cached credentials — unattended install files
     (`unattend.xml`), web/app config files, PowerShell history, saved
     RDP/WinSCP/PuTTY sessions, and LSASS-accessible credentials if
     `SeDebugPrivilege` is present
   - Registry Run keys and startup-folder entries writable by the current
     user
5. If a **custom or vendor-specific service or scheduled-task binary** is
   found running as SYSTEM and reachable from a path the current account
   can write to, treat it the same way as the analogous Linux case (see
   [linux-privilege-escalation](../linux-privilege-escalation/SKILL.md)):
   identify the exact trigger condition and, if it's a script, read its
   source for injection points before attempting exploitation.
6. Confirm SYSTEM (or the relevant elevated account) and capture the target
   flag/file. **Revert any persistence artifacts created during
   exploitation** (added services, modified ACLs, dropped binaries) once
   access is confirmed and documented.
7. Document the exact technique, binary/registry paths, and commands used —
   this is what the report's reproduction steps are built from.

## Tools

- WinPEAS / PowerUp.ps1 / Seatbelt — upload and run via the active session
  (e.g. Meterpreter `upload`). For anything long-running, prefer the
  `tmux-shell` MCP server or a backgrounded run with output redirected to a
  file over blocking a single Kali MCP `execute_command` call on it.
- Metasploit's `post/multi/recon/local_exploit_suggester` and the
  Potato-family local exploits, run through the **Metasploit MCP server**
  (`run_post_module` / `run_exploit`) against the active session. Manage the
  session and follow-up commands with `list_active_sessions` /
  `send_session_command` rather than re-triggering the original foothold
  exploit for every check. This project denies the older
  `mcp__kali__metasploit_run` tool — use the Metasploit MCP server instead.
- `icacls` / Sysinternals `accesschk` for service, file, and registry ACL
  checks.
- [LOLBAS](https://lolbas-project.github.io/) (the Windows equivalent of
  GTFOBins) for living-off-the-land binary abuse once a specific
  binary/privilege is identified.

## Output

SYSTEM (or the relevant elevated account) confirmed with the exact technique
and reproduction steps documented, or the specific vector identified and
left unexploited pending client authorization — either way, with
exploitation artifacts (if any) already cleaned up.

## Safety notes

- Some Potato-family and kernel exploits can crash the target service or
  the whole host, especially against unusual or heavily-patched builds —
  verify the exact build number, prefer the least invasive variant
  available, and get explicit sign-off before running against production.
- Credential material found during enumeration (cached passwords, hashes,
  Kerberos tickets) is sensitive — handle it per the engagement's
  reporting/confidentiality requirements; never paste it into a report body
  unredacted.
- Clean up any added services, scheduled tasks, or ACL changes made during
  exploitation once the finding is confirmed and documented.
