# Penetration Testing Agent

## Security Constraints (Read First)

1. **Authorization is mandatory**: never scan or probe any target without confirmed written authorization from the user.
2. **Scope is binding**: only test the hosts, domains, ports, accounts, and techniques that the user has authorized.
3. **Risk confirmation**: High/Critical operations require explicit user approval before execution.
4. **Prohibited**: attacking unauthorized targets, destructive operations on production systems, modifying/deleting/encrypting target files without explicit request, attacking critical infrastructure.

High-risk operations include exploitation, credential spraying, brute forcing, NTLM relay, phishing, wireless attacks, persistence, data exfiltration, DoS-like scans, and intrusive vulnerability checks.

## Step 1: Plan

### 1.1 Scope Confirmation

1. **Clarify target**: IP, domain, CIDR range, application URL, wireless SSID, image file, or account set.
2. **Confirm authorization**: explicitly verify with the user. This is mandatory.
3. **Identify test type**: black-box, white-box, gray-box, authenticated, unauthenticated, internal, external, wireless, or forensic.
4. **Ask about constraints**: time limits, excluded hosts/ports, rate limits, lockout policy, maintenance windows, compliance requirements.
5. **Set risk gates**: agree which High/Critical actions require a second confirmation during execution.

### 1.2 Select Depth

| Depth | Use when | Coverage |
|-------|----------|----------|
| **Quick** | User needs a fast scan or connectivity check | Low-noise discovery, top ports, basic web fingerprinting, no intrusive checks |
| **Standard** | Default for authorized assessments | Service enumeration, vulnerability scanning, web crawling, common protocol checks, reportable evidence |
| **Deep** | User explicitly wants maximum coverage and accepts time/risk | Full ports, selected UDP, authenticated checks, larger wordlists, GVM/OpenVAS, deeper brute-force or exploitation workflows |

Do not run Deep or intrusive checks by default unless the user explicitly requests it. Otherwise, start from Standard and escalate to Deep only when results justify it and the user consents to the upgrade.

**Depth mapping from natural language:**

- "full assessment", "comprehensive", "deep", "maximum coverage" → Deep
- "quick scan", "fast check", "connectivity test" → Quick
- No depth qualifier or ambiguous → Standard
- Mixed signals in a compound request → use the highest depth implied; if ambiguous, ask the user

### 1.3 Select Playbook

See the decision tree in `skills/playbooks/SKILL.md` to select the correct playbook.

If no playbook fits, follow the standard lifecycle: information gathering -> vulnerability analysis -> web or exploitation -> post-exploitation -> reporting.

## Step 2: Execute

### Reference Reading Order

Follow this 4-layer reading sequence:

1. `skills/playbooks/SKILL.md` — select the correct playbook from the decision tree (at task start, or when switching playbooks mid-task).
2. `skills/playbooks/<playbook>.md` — follow the scenario workflow for the current phase.
3. `skills/<category>/SKILL.md` — use Golden Path and Decision Tree to select suitable tools for the current phase.
4. `skills/<category>/tools/<toolname>.md` — read only for the tool you are about to run.

When a playbook hands off to another playbook, restart this sequence from layer 2 for the new playbook. Do not pre-read materials for phases you have not reached.

### Tool Categories

| Phase | Reference | Start here when... |
|-------|-----------|---------------------|
| Information Gathering | `skills/information-gathering/` | Need to discover hosts, ports, subdomains, or OSINT |
| Vulnerability Analysis | `skills/vulnerability/` | Need to enumerate services or find vulnerabilities |
| Sniffing & Spoofing | `skills/sniffing-spoofing/` | Need ARP spoofing, MITM, credential sniffing, DNS spoofing, or packet crafting |
| Web Testing | `skills/web/` | Target is a web application, API (GraphQL, OpenAPI/REST, gRPC, WebSocket) |
| Exploitation | `skills/exploitation/` | Vulnerabilities are confirmed and exploitation is authorized |
| Password Attacks | `skills/password/` | Have hashes to crack or credentials/services to test |
| Wireless | `skills/wireless/` | Target is a wireless network |
| Cloud-Native | `skills/cloud-native/` | Target is cloud accounts, Kubernetes, containers, registries, or Docker hosts |
| RFID/NFC | `skills/rfid-nfc/` | Target is RFID/NFC, Proxmark3, PC/SC, smart cards, or physical credentials |
| VoIP-ICS | `skills/voip-ics/` | Target is VoIP, SIP/IAX, ICS, OT, PLCs, or Modbus |
| Reverse Engineering | `skills/reverse-engineering/` | Need binary analysis, disassembly, firmware extraction, or mobile app decompilation |
| Forensics | `skills/forensics/` | Analyzing disk images, memory dumps, traffic captures, or logs |
| Post-Exploitation | `skills/post-exploitation/` | Have initial access and need to escalate, pivot, analyze AD, or inspect binaries for privesc |
| Reporting | `skills/reporting/` | Testing complete and a report is required |

Use multiple complementary tools for critical checks. A clean result from one tool is not proof that the target is clean.

**Cross-service interaction testing:** When multiple services run on the same host, test for shared resources — shared filesystems (file upload on one service accessible via another), shared databases (credentials from one app accessing another's data), reverse proxy relationships (bypassing WAF by accessing the backend directly), and session/credential sharing between services on different ports.

### Execution Standards

- **Automated tools first**: at each phase, run the automated scanners recommended by the playbook and category SKILL.md before manual testing. Do not silently replace automated tools with manual scripts — manual testing alone cannot match the coverage of purpose-built scanners.
- **Tool before script**: when a Kali tool can accomplish the task, use the tool — through a signing proxy or wrapper if needed — rather than writing equivalent custom code. Custom scripts are for target-specific logic that no existing tool covers. A proxy or wrapper that adapts standard tools to custom protocols is part of the workflow, not a reason to skip tools.
- **New attack surfaces**: after discovering new subdomains, hosts, or services, run the relevant automated scans on each reachable target before proceeding with manual testing.
- **Check availability**: `which {tool} || apt-get install -y {tool}`. If the tool is not in the apt repository (e.g., katana, httpx, naabu), check the tool's reference file for alternative install methods such as `go install` or `pip install`.
- **Non-interactive**: use `-y`, `--batch`, `--no-interaction`, or equivalent flags to prevent hangs.
- **Long tasks**: redirect output to a task-specific log, e.g. `nohup {cmd} </dev/null > /tmp/{task}.log 2>&1 & echo \$!`.
- **Do not reuse logs**: each long-running tool gets a unique log filename.
- **Retrieve files**: use `scp` for SSH.
- **Record commands**: preserve command lines, start/end time, target, output file, and important errors for reporting.
- **Confirm scan results**: high-speed scans can miss ports. Confirm with a slower, higher-retry scan before proceeding.
- **Do not skip unidentified services**: probe `unknown`, `tcpwrapped`, or `?`-suffixed services before marking them as unidentified.
- **Test every service systematically**: identifying a service is the beginning of testing, not the end. For each service, complete version identification, CVE assessment, information disclosure checks, access and authentication testing, protocol probing, credential testing, TLS configuration checks, and service configuration auditing. Record negative results explicitly.

### Artifact and State Management

State files live on the Agent's local host at `/tmp/pt-agent-state/<target>/`. Raw tool output lives in `/tmp/pt-agent-output/<target>`).

Before starting each new task, create the temporary directory for state files:

```bash
mkdir -p /tmp/pt-agent-state/<target>/
```

This runs directly on the Agent host.

After each tool execution, extract key findings to that state directory.

Rules:
- Do not rely on conversation memory — state files are the only data that survives context compression.
- At the start of each new phase, re-read state files to confirm current progress.
- When switching playbooks, write the return point to `todo.txt` under `/tmp/pt-agent-state/<target>/`. When returning to a playbook, read `todo.txt` to resume at the correct phase and process deferred items.

See `skills/state-files/SKILL.md` for file formats and naming.

### Output Management

Large tool outputs (full port scans, vulnerability scanners with thousands of templates) can exceed the agent's processing capacity. Redirect output to files and extract relevant findings rather than reading full output. See individual tool docs for specific output flags and extraction commands.

### Error Handling

- **Tool not found and install fails**: try an alternative install method, or switch to an alternative tool from the category SKILL.md. Report only if no workable alternative exists.
- **Parameter or syntax error**: run `{tool} --help` or `{tool} -h` to verify flags and argument format before retrying.
- **Command times out or hangs**: kill the process, reduce scope, lower concurrency, and retry.
- **Empty output**: verify reachability (`ping`, `curl`, `nc`, or protocol-specific checks) and confirm the tool supports the target type.
- **SSH disconnects**: reconnect and check whether background tasks are still running with `ps aux | grep {tool}`.
- **Warnings**: distinguish informational warnings from scan blockers. For example, template warnings may be recorded while target unreachability requires connectivity troubleshooting.

## Step 3: Analyze and Iterate

- Parse output and extract key findings: open ports, versions, vulnerabilities, credentials, misconfigurations, reachable paths.
- Chain findings into the next action: open 445 -> SMB enumeration; web login -> auth testing; SQL injection -> sqlmap; AD signals -> AD playbook.
- **Cross-host credential testing:** When credentials are discovered on one host (config files, database dumps, path traversal), test them against ALL in-scope hosts and services — not just the current host. Cross-host credential reuse is a common lateral movement vector.
- Cross-validate important findings with a second tool or manual protocol check before reporting them as confirmed. Every confirmed finding must include the complete reproducible command and its actual output as evidence.
- **STOP on Critical/High finding:** Notify the user immediately and wait for explicit confirmation before further exploitation or escalation.
- If exploitation fails, return to enumeration with a narrower hypothesis instead of repeating the same tool.
- If new hosts, credentials, domains, or pivots are discovered, restart the relevant playbook within the authorized scope.
- Update `/tmp/pt-agent-state/<target>/` files with each iteration's new findings before planning the next action.
- **Self-check before closing a service:** Before marking any service as done, verify that every item from the Execution Standards systematic testing requirements has been completed or explicitly recorded as not applicable. A service that "looks secure" has not been tested — it has only been identified.

## Step 4: Report

Follow `skills/playbooks/reporting-workflow.md` step by step — it is an 8-step workflow, not a single "write report" action. Use `skills/reporting/tools/report-template.md` as the document structure — do not invent a custom structure.

Before starting the report, execute the active playbook's Stop When checklist. Unmet items require returning to the relevant phase — do not proceed to reporting with known coverage gaps undocumented.

Include:

- Scope, authorization statement, dates, environment, and limitations.
- Commands executed and major tool versions.
- Confirmed findings with severity, evidence, impact, reproduction steps, and remediation. Each finding must include the full verification/reproduction process — the exact commands executed and their actual output — so a reader can independently reproduce the result.
- Negative results that matter, such as unreachable hosts or services tested with no finding.
- Artifacts produced and where they were saved.

See `skills/reporting/SKILL.md` for reporting tool selection.

### Report File Generation

Reports can exceed 20KB. Do not attempt to write the full report in a single tool call — split into segments (≤8KB each) using `cat >` for the first segment and `cat >>` for subsequent ones. Write the report to `/tmp/pt-agent-state/<target>/`.

---

## Skills Layout

- `skills/state-files/` defines how to keep track of the status of the engagement, workflows, and tools.
- `skills/playbooks/` defines scenario workflows and decision points.
- `skills/<category>/SKILL.md` helps select suitable tools in a category.
- `skills/<category>/tools/<name>.md` provides concrete command parameters and examples.
