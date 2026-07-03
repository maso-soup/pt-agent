# pt-agent

An AI framework for penetration testing, built on Claude Code's agents/skills/MCP
architecture. It packages domain-specific pentest agents, methodology-driven skills,
and tool integrations (MCP servers) so engagements follow a consistent, repeatable
process from recon through initial foothold.

**Authorized use only.** Every agent and skill in this repo assumes a signed
engagement letter / rules of engagement and an explicitly in-scope target. None of
this replaces the scoping, authorization, and reporting discipline in
[pentest-methodology](.claude/skills/pentest-methodology/SKILL.md) — treat that as
the baseline this framework builds on top of.

## Structure

```
pt-agent/
├── .claude/
│   ├── agents/            # domain specialist agents
│   │   ├── network-pentest-agent.md
│   │   ├── cloud-pentest-agent.md
│   │   └── webapp-pentest-agent.md
│   ├── settings.json       # project-wide permissions (e.g. denies legacy tools superseded by an MCP server)
│   └── skills/             # one directory per skill, each with a SKILL.md
│       ├── network-recon/
│       ├── smb-enum-exploitation/
│       ├── credential-spraying/
│       ├── kerberos-attacks/
│       ├── llmnr-nbns-poisoning/
│       ├── vulnerable-service-exploitation/
│       ├── default-creds-exploitation/
│       ├── cloud-recon/
│       ├── iam-misconfig-enum/
│       ├── public-storage-exploitation/
│       ├── ssrf-to-metadata/
│       ├── leaked-secrets-hunting/
│       ├── serverless-exploitation/
│       ├── k8s-container-misconfig/
│       ├── webapp-recon/
│       ├── sql-injection-exploitation/
│       ├── auth-bypass-testing/
│       ├── file-upload-exploitation/
│       ├── ssrf-exploitation/
│       ├── lfi-rfi-exploitation/
│       ├── default-creds-admin-panels/
│       ├── pentest-methodology/
│       ├── linux-privilege-escalation/
│       ├── windows-privilege-escalation/
│       └── pentest-reporting/
└── .mcp.json               # MCP server registry
```

This layout is deliberately flat and additive: new domains get a new agent plus a
new set of skill directories; new tool integrations get a new entry in
`.mcp.json`.

## Agents

| Agent | Domain |
|---|---|
| [network-pentest-agent](.claude/agents/network-pentest-agent.md) | Internal/external network & Active Directory assessments |
| [cloud-pentest-agent](.claude/agents/cloud-pentest-agent.md) | AWS/Azure/GCP infrastructure assessments |
| [webapp-pentest-agent](.claude/agents/webapp-pentest-agent.md) | Web application & API assessments |

Each agent owns a methodology (recon → enumeration → foothold → escalation →
reporting) and delegates the hands-on work to the skills below.

## Skills

Skills are organized by domain. Each domain has one **recon** skill (always run
first) and a set of **initial foothold** skills covering the most common ways
engagements actually get a first shell / first credential / first access.

### Network
- [network-recon](.claude/skills/network-recon/SKILL.md) — host discovery, port scanning, service fingerprinting
- [smb-enum-exploitation](.claude/skills/smb-enum-exploitation/SKILL.md) — SMB null sessions, share enumeration, EternalBlue-class checks
- [credential-spraying](.claude/skills/credential-spraying/SKILL.md) — low-and-slow spraying against SSH/RDP/WinRM/web logins
- [kerberos-attacks](.claude/skills/kerberos-attacks/SKILL.md) — Kerberoasting and AS-REP roasting for AD credential theft
- [llmnr-nbns-poisoning](.claude/skills/llmnr-nbns-poisoning/SKILL.md) — Responder-style poisoning and hash relay/cracking
- [vulnerable-service-exploitation](.claude/skills/vulnerable-service-exploitation/SKILL.md) — matching a fingerprinted version (network service or web app/CMS/platform) to known CVEs and exploiting with Metasploit; also used from the Web Application domain below
- [default-creds-exploitation](.claude/skills/default-creds-exploitation/SKILL.md) — default/weak creds on SNMP, routers, printers, IoT, and other exposed services

### Cloud
- [cloud-recon](.claude/skills/cloud-recon/SKILL.md) — asset/subdomain discovery, cloud footprint mapping across AWS/Azure/GCP
- [iam-misconfig-enum](.claude/skills/iam-misconfig-enum/SKILL.md) — over-permissioned roles, keys, and trust policies
- [public-storage-exploitation](.claude/skills/public-storage-exploitation/SKILL.md) — public S3/Blob/GCS buckets and their contents
- [ssrf-to-metadata](.claude/skills/ssrf-to-metadata/SKILL.md) — SSRF pivots into the instance metadata service for credential theft
- [leaked-secrets-hunting](.claude/skills/leaked-secrets-hunting/SKILL.md) — cloud keys/tokens leaked in repos, CI configs, and build artifacts
- [serverless-exploitation](.claude/skills/serverless-exploitation/SKILL.md) — misconfigured Lambda/Functions with excess permissions or exposed triggers
- [k8s-container-misconfig](.claude/skills/k8s-container-misconfig/SKILL.md) — exposed kubelet/dashboard APIs and container escapes

### Web Application
- [webapp-recon](.claude/skills/webapp-recon/SKILL.md) — subdomain/content discovery, tech stack fingerprinting, attack surface mapping
- [vulnerable-service-exploitation](.claude/skills/vulnerable-service-exploitation/SKILL.md) — check for a known, weaponized CVE against the fingerprinted app/CMS/platform version before assuming a custom exploitation path is needed (shared with the Network domain above)
- [sql-injection-exploitation](.claude/skills/sql-injection-exploitation/SKILL.md) — detecting and exploiting SQLi for data access or auth bypass
- [auth-bypass-testing](.claude/skills/auth-bypass-testing/SKILL.md) — broken authentication, session, and access-control flaws
- [file-upload-exploitation](.claude/skills/file-upload-exploitation/SKILL.md) — unrestricted upload to webshell/RCE
- [ssrf-exploitation](.claude/skills/ssrf-exploitation/SKILL.md) — server-side request forgery for internal pivoting
- [lfi-rfi-exploitation](.claude/skills/lfi-rfi-exploitation/SKILL.md) — local/remote file inclusion toward code execution
- [default-creds-admin-panels](.claude/skills/default-creds-admin-panels/SKILL.md) — default/weak credentials on exposed admin interfaces

### Shared
- [pentest-methodology](.claude/skills/pentest-methodology/SKILL.md) — scoping and rules-of-engagement gate every domain agent runs before touching a target
- [linux-privilege-escalation](.claude/skills/linux-privilege-escalation/SKILL.md) — turn a Linux foothold into root (kernel/sudo CVEs, SUID/capabilities, cron/incron-triggered scripts, credential reuse)
- [windows-privilege-escalation](.claude/skills/windows-privilege-escalation/SKILL.md) — turn a Windows foothold into SYSTEM (token privileges, service/task misconfigurations, stored credentials)
- [pentest-reporting](.claude/skills/pentest-reporting/SKILL.md) — consolidate findings from any domain into a CVSS-scored, evidence-backed client report

## MCP Servers

Two MCP servers are registered in [.mcp.json](.mcp.json), both running on the Kali
VM and reached over SSH-wrapped stdio (`ssh -i <key> kali@<host> <server-binary>`)
so their state — tmux sessions, Metasploit sessions — lives where the actual work
happens, not on the machine running Claude Code.

- **`tmux-shell`** ([persistent-shell-mcp](https://github.com/TNTisdial/persistent-shell-mcp))
  — persistent tmux-backed shell sessions on Kali. Use for anything without a
  structured API, and for long-running commands that would exceed a single Kali
  MCP `execute_command` call's timeout: full `-p-` nmap sweeps, large-wordlist
  `gobuster` runs, `linPEAS`, or driving `msfconsole` interactively for anything
  the Metasploit MCP server below doesn't cover.
- **`metasploit`** ([MetasploitMCP](https://github.com/fishke22/MetasploitMCP),
  installed via `apt install metasploitmcp` on Kali) — talks to `msfrpcd`
  (a loopback-only systemd service on Kali) over structured RPC instead of
  scraping `msfconsole`'s text output. Covers module search/execution, payload
  generation, and session/listener/job lifecycle (`list_active_sessions`,
  `send_session_command`, `terminate_session`, `start_listener`, `stop_job`).
  [.claude/settings.json](.claude/settings.json) denies the older
  `mcp__kali__metasploit_run` tool, so this server is the only path for
  Metasploit work in this project — see
  [vulnerable-service-exploitation](.claude/skills/vulnerable-service-exploitation/SKILL.md)
  for how a skill is expected to use it.

Credentials for both (the `msfrpcd` RPC password, the SSH private key) live only
on the Kali host or in `~/.ssh/` — never in `.mcp.json` itself, since that file is
git-tracked.

As further gaps show up, register the next server the same way: point a new
`.mcp.json` entry at wherever it needs to run.

## Adding a new domain

1. Add `.claude/agents/<domain>-pentest-agent.md`.
2. Add `.claude/skills/<domain>-recon/SKILL.md`.
3. Add 5-10 `.claude/skills/<foothold-skill>/SKILL.md` covering the domain's most
   common paths to an initial foothold.
4. Update this README's tables.
