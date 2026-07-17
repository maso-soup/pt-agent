# PT Agent

An AI framework for penetration testing, built on Claude Code's agent/skills
architecture. A single agent drives every engagement — scoping, tool selection,
execution, and reporting — using [AGENTS.md](AGENTS.md) as its operating manual
and a library of 16 tool categories, 16 scenario playbooks, and 270+ individual
tool references under `.claude/skills/`.

**Authorized use only.** Every workflow in this repo assumes confirmed written
authorization for an explicitly in-scope target. `AGENTS.md`'s Security
Constraints section — never scan without authorization, scope is binding, High/
Critical operations require explicit approval — is the baseline every playbook
and skill builds on top of.

## How it works

There is no per-domain subagent; one generalist agent reads `AGENTS.md` at the
start of every task and follows its 4-step lifecycle:

1. **Plan** — confirm scope and authorization, pick a depth (Quick/Standard/Deep),
   and select a playbook from `skills/playbooks/SKILL.md`'s decision tree.
2. **Execute** — read the playbook for the workflow, the category `SKILL.md` for
   tool selection, and the individual tool doc only for the tool about to run.
   Playbooks hand off to each other as new signals appear (e.g. an AD domain
   found mid-scan switches to the Active Directory playbook).
3. **Analyze and iterate** — chain findings into the next action, cross-validate
   before reporting anything confirmed, and stop for explicit user confirmation
   on any Critical/High finding.
4. **Report** — follow the 8-step reporting workflow and the standard report
   template; nothing gets skipped to reporting with known coverage gaps.

This reading order is deliberately lazy: only the playbook and tool docs for the
current phase get loaded, so the size of the tool library doesn't bloat context
on a task that only needs a handful of tools.

Progress is tracked outside the conversation so it survives context compression:
state files (`todo.txt`, `findings.txt`, `cred_matrix.txt`, etc. — see
[skills/state-files/SKILL.md](.claude/skills/state-files/SKILL.md)) live at
`~/pt-agent-state/<target>/`, and raw tool output lives at
`~/pt-agent-output/<target>/`.

## Structure

```
pt-agent/
├── AGENTS.md                # operating manual — read this first
├── CLAUDE.md                 # imports AGENTS.md + Claude-specific notes
└── .claude/
    ├── settings.json         # project-wide permissions
    └── skills/
        ├── playbooks/         # scenario workflows (select first, per SKILL.md's decision tree)
        ├── state-files/       # state/output directory conventions
        ├── reporting/         # report template, severity framework, doc tooling
        └── <category>/        # one directory per tool category
            ├── SKILL.md        # Golden Path + Decision Tree for that category
            └── tools/          # one reference file per tool
```

## Playbooks

Playbooks are workflow guides, not parameter references — they decide phases,
stopping points, risk gates, and expected artifacts, then point into the tool
categories below for the actual commands. Select one via
[skills/playbooks/SKILL.md](.claude/skills/playbooks/SKILL.md)'s decision tree;
`internal-network.md` is the default when nothing else matches.

| Playbook | Use for |
|---|---|
| `internal-network` | IP/CIDR/internal network, or the default when nothing else fits |
| `internal-network-protocols` | SMB, MSRPC, SNMP, SMTP, DNS, database, RDP enumeration |
| `external-attack-surface` | Domain names, company name, public IPs — OSINT and subdomain discovery |
| `web-application` | Web app or URL target |
| `api-security` | GraphQL, OpenAPI/REST, gRPC, WebSocket APIs |
| `active-directory` | AD domain / DC / Windows domain |
| `password-audit` | Hash files, credential lists, service logins |
| `wireless-assessment` | Wi-Fi, Bluetooth/BLE |
| `cloud-native-assessment` | Cloud accounts, Kubernetes, container registries, Docker hosts |
| `mobile-application` | APK/IPA / mobile app runtime |
| `rfid-nfc` | RFID/NFC, smart cards, embedded device firmware |
| `voip-ics` | SIP/IAX/VoIP, ICS/OT, PLCs, Modbus, IPMI |
| `post-exploitation` | Existing shell / authorized initial access |
| `forensics-triage` | Disk images, memory dumps, pcaps, logs |
| `source-code-audit` | Source repos, dependency manifests, CI artifacts |
| `reporting-workflow` | Testing complete, need to produce a report |

## Tool categories

| Category | Covers |
|---|---|
| `information-gathering` | Host/port/subdomain discovery, OSINT |
| `vulnerability` | Service enumeration, vulnerability scanning |
| `sniffing-spoofing` | ARP/DNS spoofing, MITM, credential sniffing, packet crafting |
| `web` | Web apps, GraphQL/REST/gRPC/WebSocket APIs |
| `exploitation` | Confirmed-vulnerability exploitation, pivoting/tunneling, phishing |
| `password` | Online brute-forcing, offline hash cracking |
| `wireless` | Wi-Fi and Bluetooth |
| `cloud-native` | Cloud accounts, Kubernetes, containers, registries, Docker hosts |
| `rfid-nfc` | RFID/NFC, Proxmark3, smart cards, physical credentials |
| `voip-ics` | VoIP, SIP/IAX, ICS/OT, PLCs, Modbus |
| `reverse-engineering` | Binary analysis, disassembly, firmware, mobile decompilation |
| `forensics` | Disk/memory/traffic/log analysis |
| `post-exploitation` | Privilege escalation, persistence, lateral movement, AD analysis |
| `reporting` | Report templates, severity framework, document conversion |

Each category's `SKILL.md` leads with a Golden Path (default tool per scenario)
and a Decision Tree (what to do when the Golden Path doesn't fit), then links out
to `tools/<name>.md` for exact flags and example commands.

## Prerequisites

Engagements run natively on Kali (or a Kali-equivalent toolset) — there is no
MCP server layer or remote VM wrapper. `AGENTS.md`'s Execution Standards cover
tool availability checks (`which {tool} || apt-get install -y {tool}`,
falling back to `go install`/`pip install` for tools outside the apt repos).

## Adding a new tool or category

1. New tool in an existing category: add `.claude/skills/<category>/tools/<name>.md`
   following the existing format (Category/Risk Level header, Description,
   Installation, Parameter Reference, Common Commands, Notes & Tips, Official
   References), then link it from that category's `SKILL.md`.
2. New category: add `.claude/skills/<category>/SKILL.md` (Golden Path +
   Decision Tree) and a `tools/` subdirectory, then add it to the Tool
   Categories table in `AGENTS.md` and to this README.
3. New scenario: add `.claude/skills/playbooks/<name>.md` and register it in
   `skills/playbooks/SKILL.md`'s decision tree and cross-reference map.

## Credits and License

This project began as a fork of [x-glacier/kali-pentest](https://github.com/x-glacier/kali-pentest)
and is licensed under the [Apache License 2.0](LICENSE). Large portions of the
original have been added, removed, and substantially modified, and the project
continues to diverge from upstream over time.

Attribution for the original work is recorded in [NOTICE](NOTICE), as required by
the Apache License. See [LICENSE](LICENSE) for the full terms.
