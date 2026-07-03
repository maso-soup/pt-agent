---
name: linux-privilege-escalation
description: Systematically enumerate and exploit privilege escalation paths on a compromised Linux host — kernel/sudo CVEs, SUID/capabilities, credential reuse, and cron/incron-triggered scripts reachable by the current low-privileged account. Use once an initial foothold (shell) is established on a Linux target and further access (root) is the goal.
---

## Purpose

An initial foothold is rarely the objective — this skill turns a low-privileged
shell on a Linux host into root, working through the standard privesc surface
systematically (automated triage first, then the vectors automated tools
routinely miss) rather than jumping straight to the first CVE that looks
promising.

## When to use

After any foothold skill (in any domain — network, web application, etc.)
lands a shell on a Linux host and the RoE permits escalation. Pairs naturally
with [vulnerable-service-exploitation](../vulnerable-service-exploitation/SKILL.md)
for the CVE-research workflow once a specific kernel/sudo/package version is
identified.

## Methodology

1. **Baseline enumeration** — `id`/`groups`, `sudo -l`, `uname -a`,
   `/etc/os-release`, current user's writable paths, and any credentials
   already found during the foothold (config files, database credentials,
   API keys). Test credential/password reuse against `su` and SSH before
   anything else — it's often free and immediately conclusive.
2. **Automated triage** — run linPEAS against the session in **default mode
   (no flags), or `-s` for superfast/stealth**, and Metasploit's
   `post/multi/recon/local_exploit_suggester` (via the Metasploit MCP
   server's `run_post_module`, against the active session). **Never run
   linPEAS with `-a` (all checks)** — it adds a whole-filesystem password
   search, brute-force user enumeration, and a slow CVE-database check that
   together can run 10+ minutes for findings that mostly duplicate the
   default scan; the default invocation finds the large majority of wins in
   a fraction of the time. Treat both tools' output as a starting point, not
   a verdict: they produce false positives (flagging a CVE by version number
   alone when the distro backported a fix without bumping that version) and
   false negatives (custom/vendor-specific mechanisms they don't know to
   look for).
   - If an even faster first pass is useful before committing to linPEAS,
     [linux-smart-enumeration](https://github.com/diego-treitos/linux-smart-enumeration)
     (`lse.sh`) has explicit verbosity levels (`-l0`/`-l1`/`-l2`) and is
     usually quicker to a signal — escalate to linPEAS if it doesn't turn up
     a clear path.
   - For the cron/incron/scheduled-task vector specifically (step 4 below),
     `pspy` is often more direct than either enumeration tool: it passively
     watches process execution (no root required) and shows a cron/incron
     job firing in real time, rather than requiring you to spot a
     low-priv-writable watched path in a static file listing and infer that
     it's triggered by something root-owned.
3. For any suggested kernel/sudo/SUID-binary CVE, verify the *exact* package
   build string (not just the upstream version number) before attempting
   exploitation — e.g. a Red Hat/Debian errata suffix can indicate a
   backported fix the raw version number doesn't reflect.
4. Independently check the classic manual vectors even when automated tools
   don't flag them:
   - SUID/SGID binaries against [GTFOBins](https://gtfobins.github.io/),
     including less common ones not in the enumeration tool's default list
   - `sudo -l` output, including NOPASSWD entries — worth checking even if
     an initial non-interactive `sudo -n -l` fails, since that only proves
     no *passwordless* rule matched
   - Writable files/directories referenced by root-owned cron jobs, systemd
     timers, or **incron watches** (`/etc/cron.d/`, `/etc/incron.d/`,
     `/var/spool/incron/`, `/var/spool/cron/`) — a root-triggered action
     watching a path the current low-privileged account can write to is a
     common pattern that generic enumeration scripts often surface as raw
     data (a file listing) without connecting it to a root-owned trigger.
     Run `pspy` alongside the static enumeration to catch this class live
     instead of inferring it from a file listing.
   - Capabilities beyond the standard set (`getcap -r /`)
5. If a **custom or vendor-specific script/binary** turns out to be
   triggered by a root-owned cron/incron/systemd path that the current
   account can write to, read its full source before attempting
   exploitation (if it's a script — binaries need static/dynamic analysis
   instead). Specifically look for: unsanitized filename/argument handling,
   an incomplete shell-metacharacter blocklist (e.g. blocking quotes and `;`
   but not `|`), and any "alternate input" mechanism that bypasses the
   primary sanitization (e.g. reading parameters from a file's *contents*
   instead of its name, if the filename itself is restricted).
6. Confirm root access and capture the target flag/file. **Revert any
   persistence artifacts created during exploitation** (an added SUID bit,
   a written cron/incron trigger file, a modified sudoers-equivalent) once
   access is confirmed and documented — don't leave the target more
   exploitable than it was found.
7. Document the exact technique, file paths, and commands used — this is
   what the report's reproduction steps are built from.

## Tools

- linPEAS — upload and run via the active session, **default mode or `-s`
  only, never `-a`** (see Methodology step 2). Even in default mode, a scan
  can run long enough to exceed a single Kali MCP `execute_command` call's
  timeout on a busy host; use the `tmux-shell` MCP server for it, or launch
  it backgrounded with output redirected to a file and poll for completion
  rather than blocking a single call on it.
- [linux-smart-enumeration](https://github.com/diego-treitos/linux-smart-enumeration)
  (`lse.sh`) as a faster, leveled first pass before committing to a full
  linPEAS run.
- `pspy` for live process/cron/incron monitoring — the most direct way to
  catch a root-triggered scheduled job, faster and more conclusive than
  spotting the same thing in a static enumeration dump.
- Metasploit's `post/multi/recon/local_exploit_suggester`, run through the
  **Metasploit MCP server** (`run_post_module`) against the active session.
  Manage the session and follow-up commands with `list_active_sessions` /
  `send_session_command` rather than re-triggering the original foothold
  exploit for every check. This project denies the older
  `mcp__kali__metasploit_run` tool — use the Metasploit MCP server instead.
- [GTFOBins](https://gtfobins.github.io/) for known SUID/sudo/capability
  abuse recipes once a specific binary is identified.
- `searchsploit`/CVE research for kernel and sudo version-specific
  exploits — see [vulnerable-service-exploitation](../vulnerable-service-exploitation/SKILL.md)
  for the general CVE-research workflow (CISA KEV, vendor advisories,
  confirm-before-exploit probing); it applies here too.

## Output

Root access confirmed with the exact technique and reproduction steps
documented, or the specific vector identified and left unexploited pending
client authorization — either way, with exploitation artifacts (if any)
already cleaned up.

## Safety notes

- Kernel exploits are the least safe privesc vector — a mistimed race
  condition or a kernel build the exploit wasn't tested against can crash or
  corrupt the host. Prefer a userspace/misconfiguration vector (SUID, cron,
  credential reuse) whenever one exists, and get explicit sign-off before
  running a kernel exploit against a production host.
- Blind exploits that brute-force ASLR (e.g. CVE-2021-3156-style attacks)
  can take many minutes and repeatedly crash the target process during the
  attempt. Don't let a slow blind exploit block investigation of a faster,
  already-identified vector — run it in parallel or come back to it, and set
  expectations with the client if the RoE has a tight testing window.
- Clean up any SUID bits, written files, or added cron/incron/systemd
  entries created as part of exploitation once the finding is confirmed and
  documented.
