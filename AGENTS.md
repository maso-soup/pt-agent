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

Read the decision tree in `.claude/reference/playbook-selection.md` to select the correct playbook, then **enter** it rather than reading it as a plain reference. Do not rely on automatic Skill-description matching alone — the routing doc's branching and cross-reference rules (multi-playbook sequencing, mid-engagement handoffs) are needed to pick correctly.

> **Entering a playbook** means loading its scenario workflow so the harness can apply its risk gates. Do it whichever way your harness supports:
> - **Skill tool available (default in the Claude Code harness):** invoke `Skill(skill: "<name>")`.
> - **No Skill tool (e.g. Continue CLI or other harnesses):** read `.claude/skills/<name>/SKILL.md` directly.
>
> Both satisfy the PreToolUse playbook gate. The rest of this document says "enter the playbook" to mean either method.

If no playbook fits, follow the standard lifecycle: information gathering -> vulnerability analysis -> web or exploitation -> post-exploitation -> reporting.

## Step 2: Execute

### Reference Reading Order

Follow this 4-layer reading sequence:

1. `.claude/reference/playbook-selection.md` — select the correct playbook from the decision tree (at task start, or when switching playbooks mid-task).
2. **Enter the matched playbook** (`Skill(skill: "<playbook>")`, or read `.claude/skills/<playbook>/SKILL.md` if the Skill tool is unavailable) — follow its scenario workflow for the current phase.
3. `.claude/reference/<category>/INDEX.md` — use Golden Path and Decision Tree to select suitable tools for the current phase.
4. `.claude/reference/<category>/tools/<toolname>.md` — read only for the tool you are about to run.

When a playbook hands off to another playbook, restart this sequence from layer 2 for the new playbook. Do not pre-read materials for phases you have not reached.

**Switch-trigger self-check (mandatory):** A cross-reference trigger fires the moment you discover a new attack surface that maps to a different playbook — a web app or API on an enumerated host, an AD domain, a cloud/Kubernetes/registry asset, VoIP/ICS services, captured hashes, or newly gained initial access (see the full trigger list in `.claude/reference/playbook-selection.md`). When one fires, **enter the matched playbook BEFORE running any tool against that new surface** — not after you have already started poking at it. Before firing recon or exploitation at a newly discovered surface, stop and ask yourself: *"Does this surface map to a playbook I have not entered this engagement?"* If yes, enter that playbook first. Prior knowledge of the target's software or a known CVE is never a reason to skip this — "I already know the exploit" is exactly the rationalization that leads to unstructured, incomplete testing. Entering the playbook is what guarantees the per-surface test matrix, risk gates, and stop conditions are applied. (A PreToolUse hook enforces this at the tool level, but the self-check is your responsibility — the hook only checks that *a* playbook was entered, not that you switched to the *right* one for the current surface.)

### Tool Categories

| Phase | Reference | Start here when... |
|-------|-----------|---------------------|
| Information Gathering | `.claude/reference/information-gathering/` | Need to discover hosts, ports, subdomains, or OSINT |
| Vulnerability Analysis | `.claude/reference/vulnerability/` | Need to enumerate services or find vulnerabilities |
| Sniffing & Spoofing | `.claude/reference/sniffing-spoofing/` | Need ARP spoofing, MITM, credential sniffing, DNS spoofing, or packet crafting |
| Web Testing | `.claude/reference/web/` | Target is a web application, API (GraphQL, OpenAPI/REST, gRPC, WebSocket) |
| Exploitation | `.claude/reference/exploitation/` | Vulnerabilities are confirmed and exploitation is authorized |
| Password Attacks | `.claude/reference/password/` | Have hashes to crack or credentials/services to test |
| Wireless | `.claude/reference/wireless/` | Target is a wireless network |
| Cloud-Native | `.claude/reference/cloud-native/` | Target is cloud accounts, Kubernetes, containers, registries, or Docker hosts |
| RFID/NFC | `.claude/reference/rfid-nfc/` | Target is RFID/NFC, Proxmark3, PC/SC, smart cards, or physical credentials |
| VoIP-ICS | `.claude/reference/voip-ics/` | Target is VoIP, SIP/IAX, ICS, OT, PLCs, or Modbus |
| Reverse Engineering | `.claude/reference/reverse-engineering/` | Need binary analysis, disassembly, firmware extraction, or mobile app decompilation |
| Forensics | `.claude/reference/forensics/` | Analyzing disk images, memory dumps, traffic captures, or logs |
| Post-Exploitation | `.claude/reference/post-exploitation/` | Have initial access and need to escalate, pivot, analyze AD, or inspect binaries for privesc |
| Reporting | `.claude/reference/reporting/` | Testing complete and a report is required |

Use multiple complementary tools for critical checks. A clean result from one tool is not proof that the target is clean.

**Cross-service interaction testing:** When multiple services run on the same host, test for shared resources — shared filesystems (file upload on one service accessible via another), shared databases (credentials from one app accessing another's data), reverse proxy relationships (bypassing WAF by accessing the backend directly), and session/credential sharing between services on different ports.

### Execution Standards

- **Automated tools first**: at each phase, run the automated scanners recommended by the playbook and category INDEX.md before manual testing. Do not silently replace automated tools with manual scripts — manual testing alone cannot match the coverage of purpose-built scanners.
- **Tool before script**: when a Kali tool can accomplish the task, use the tool — through a signing proxy or wrapper if needed — rather than writing equivalent custom code. Custom scripts are for target-specific logic that no existing tool covers. A proxy or wrapper that adapts standard tools to custom protocols is part of the workflow, not a reason to skip tools.
- **New attack surfaces**: after discovering new subdomains, hosts, or services, run the relevant automated scans on each reachable target before proceeding with manual testing.
- **Check availability**: `which {tool} || apt-get install -y {tool}`. If the tool is not in the apt repository (e.g., katana, httpx, naabu), check the tool's reference file for alternative install methods such as `go install` or `pip install`.
- **Non-interactive**: use `-y`, `--batch`, `--no-interaction`, or equivalent flags to prevent hangs.
- **Interactive shells**: the agent drives via stateless tool calls and has no controlling terminal, so a bare backgrounded `nc` cannot be typed into. When you obtain an interactive shell, handle it per `.claude/reference/exploitation/interactive-shell-handling.md` — prefer an exec primitive or SSH-with-key, and broker any genuinely interactive session through tmux (`send-keys`/`capture-pane`), never a raw `nc </dev/null &`.
- **Long tasks**: redirect output to a task-specific log, e.g. `nohup {cmd} </dev/null > /tmp/{task}.log 2>&1 & echo \$!`.
- **Do not reuse logs**: each long-running tool gets a unique log filename.
- **Retrieve files**: use `scp` for SSH.
- **Record commands**: preserve command lines, start/end time, target, output file, and important errors for reporting.
- **Confirm scan results**: high-speed scans can miss ports. Confirm with a slower, higher-retry scan before proceeding.
- **Do not skip unidentified services**: probe `unknown`, `tcpwrapped`, or `?`-suffixed services before marking them as unidentified.
- **Test every service systematically**: identifying a service is the beginning of testing, not the end. For each service, complete version identification, CVE assessment, information disclosure checks, access and authentication testing, protocol probing, credential testing, TLS configuration checks, and service configuration auditing. Record negative results explicitly.

### Artifact and State Management

State files live on the Agent's local host at `~/pt-agent-state/<target>/`. Raw tool output lives in `~/pt-agent-output/<target>`.

Before starting each new task, create the directories for state and output files:

```bash
mkdir -p ~/pt-agent-state/<target>/
mkdir -p ~/pt-agent-output/<target>/
```

After each tool execution, extract key findings to the relevant directory.

Rules:
- Do not rely on conversation memory — state files are the only data that survives context compression.
- At the start of each new phase, re-read state files to confirm current progress.
- When switching playbooks, write the return point to `todo.txt` under `~/pt-agent-state/<target>/`. When returning to a playbook, read `todo.txt` to resume at the correct phase and process deferred items.

See `.claude/skills/state-files/SKILL.md` for file formats and naming.

### Output Management

Large tool outputs (full port scans, vulnerability scanners with thousands of templates) can exceed the agent's processing capacity. Redirect output to files and extract relevant findings rather than reading full output. See individual tool docs for specific output flags and extraction commands.

### Error Handling

- **Tool not found and install fails**: try an alternative install method, or switch to an alternative tool from the category INDEX.md. Report only if no workable alternative exists.
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
- Update `~/pt-agent-state/<target>/` files with each iteration's new findings before planning the next action.
- **Self-check before closing a service:** Before marking any service as done, verify that every item from the Execution Standards systematic testing requirements has been completed or explicitly recorded as not applicable. A service that "looks secure" has not been tested — it has only been identified.

## Step 4: Report

Enter the reporting playbook (`Skill(skill: "reporting")`, or read `.claude/skills/reporting/SKILL.md`) and follow it step by step — it is an 8-step workflow, not a single "write report" action. Use `.claude/reference/reporting/tools/report-template.md` as the document structure — do not invent a custom structure.

Before starting the report, execute the active playbook's Stop When checklist. Unmet items require returning to the relevant phase — do not proceed to reporting with known coverage gaps undocumented. If any coverage gaps remain after that and cannot be reconciled, ask the user for relevant information or to make a decision. 

Include:

- Scope, authorization statement, dates, environment, and limitations.
- Commands executed and major tool versions.
- Confirmed findings with severity, evidence, impact, reproduction steps, and remediation. Each finding must include the full verification/reproduction process — the exact commands executed and their actual output — so a reader can independently reproduce the result.
- Negative results that matter, such as unreachable hosts or services tested with no finding.
- Artifacts produced and where they were saved.

See `.claude/reference/reporting/INDEX.md` for reporting tool selection.

### Report File Generation

Reports can exceed 20KB. Do not attempt to write the full report in a single tool call — split into segments (≤8KB each) using `cat >` for the first segment and `cat >>` for subsequent ones. Write the report to `~/pt-agent-state/<target>/`.

---

## Skills Layout

- `.claude/skills/state-files/` defines how to keep track of the status of the engagement, workflows, and tools.
- `.claude/skills/<playbook>/SKILL.md` defines a scenario workflow — enter it once selected (via the Skill tool, or by reading the file directly if that tool is unavailable).
- `.claude/reference/playbook-selection.md` holds the decision tree and cross-reference map used to pick a playbook.
- `.claude/reference/<category>/INDEX.md` helps select suitable tools in a category.
- `.claude/reference/<category>/tools/<name>.md` provides concrete command parameters and examples.
