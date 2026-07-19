# Playbook Selection

Scenario playbooks describe how an agent should combine tools across categories. They are workflow guides, not parameter references. Each playbook lives under `.claude/skills/<name>/SKILL.md` — **enter** it once selected below rather than treating it as a plain reference. Entering means invoking `Skill(skill: "<name>")` when the Skill tool is available (the default in the Claude Code harness), or reading `.claude/skills/<name>/SKILL.md` directly when it is not (e.g. Continue CLI). Both satisfy the PreToolUse playbook gate.

Use in this order:

1. Select the playbook that matches the authorized task using the Decision Tree below.
2. Enter it (`Skill(skill: "<name>")`, or read `.claude/skills/<name>/SKILL.md`) — it decides phases, stopping points, risk gates, and expected artifacts.
3. Read `<category>/INDEX.md` files under `.claude/reference/` — use Golden Path and Decision Tree to select suitable tools.
4. Read `<category>/tools/<name>.md` only when running that tool.

Do not rely on automatic Skill-description matching alone to pick between playbooks — engagements need the branching and combination logic below (multi-playbook sequencing, cross-reference triggers) that competing one-line Skill descriptions can't express.

## Decision Tree

Match the authorized target type to the correct playbook:

| Authorized Target | Playbook |
|-------------------|----------|
| IP range / CIDR / internal network | `internal-network` |
| Domain names / company name / public IPs | `external-attack-surface` |
| Web URL / web app | `web-application` |
| GraphQL / OpenAPI / gRPC / WebSocket API | `api-security` |
| Pure API endpoint (HTTP/HTTPS only, no other services) / user provides API docs, Swagger, or Postman collection | `api-security` |
| Active Directory domain / DC / Windows domain | `active-directory` |
| Hash file / credential list / service login | `password-audit` |
| Wi-Fi SSID / BSSID / wireless channel | `wireless-assessment` |
| Bluetooth / BLE target | `wireless-assessment` + `wireless/INDEX.md` |
| Cloud account / Kubernetes / container registry / Docker host | `cloud-native-assessment` |
| APK / IPA / mobile app runtime | `mobile-application` |
| RFID / NFC / smart card / physical credential / embedded device firmware | `rfid-nfc` |
| SIP / IAX / VoIP / ICS / OT / PLC / Modbus / IPMI / BMC | `voip-ics` |
| Existing shell / authorized initial access | `post-exploitation` |
| Disk image / memory dump / pcap / log files | `forensics-triage` |
| Source code repo / dependency manifests / CI artifacts | `source-code-audit` |
| Testing complete, need to produce a report | `reporting` |
| No match above / general pentest / unclear target type | `internal-network` (default) |

`internal-network` is the default playbook. When the target does not clearly match any specialized scenario above, start with `internal-network` — its host discovery, port scanning, and per-service testing workflow will reveal which specialized playbooks to switch to.

**Multi-playbook sequencing:** When a target matches multiple playbooks (e.g., an IP with web services matches both `internal-network` and `web-application`), start with `internal-network` for host and service discovery. Complete the per-service test matrix for all discovered services, then switch to specialized playbooks for deep testing. After completing a specialized playbook, return to the next unfinished phase of the originating playbook.

Cross-reference triggers during internal network testing:

- Discovered AD domain during internal network scan → switch to `active-directory`
- Discovered web app on enumerated host → switch to `web-application`
- Discovered API-heavy app or API schema → switch to `api-security`
- Target exposes only HTTP/HTTPS API (no other services) or user provides API documentation → switch to `api-security`
- Discovered Kubernetes, Docker API, registry, or cloud assets → switch to `cloud-native-assessment`
- Discovered VoIP or ICS/OT services → switch to `voip-ics`
- Gained initial access → switch to `post-exploitation`
- Discovered evidence of compromise (malware, unauthorized access, data exfiltration indicators) → switch to `forensics-triage`
- Captured hashes during AD enumeration → switch to `password-audit`

## Available Playbooks

| Scenario | Skill | Coverage |
|----------|------|----------|
| Internal network or full pentest | `internal-network` | Host discovery, port scanning, service enumeration, vulnerability validation, credential testing, and pivot to specialized playbooks |
| Internal network protocols | `internal-network-protocols` | SMB, MSRPC, SNMP, SMTP, DNS, database, and RDP protocol-specific enumeration and testing |
| External attack surface | `external-attack-surface` | OSINT, subdomain enumeration, port/service discovery, web fingerprinting, and handoff to web/API playbooks |
| Web application | `web-application` | Crawling, DAST scanning, authentication testing, injection, CMS-specific checks, and manual validation |
| API security | `api-security` | Schema recovery, endpoint discovery, auth/authorization testing (BOLA, JWT), fuzzing, rate limiting, and business logic |
| Active Directory | `active-directory` | AD enumeration, Kerberoasting, AS-REP roasting, relay attacks, ACL abuse, AD CS, credential extraction, and domain escalation |
| Password audit | `password-audit` | Hash identification, offline cracking (hashcat/john), password spraying, default credentials, and credential reuse |
| Wireless assessment | `wireless-assessment` | Adapter setup, WiFi reconnaissance, handshake capture, WPS attacks, evil twin, Bluetooth/BLE enumeration, and post-authentication |
| Cloud-native assessment | `cloud-native-assessment` | Multi-cloud posture, provider-specific audits (AWS/Azure/GCP), Kubernetes security, container/registry scanning, and serverless review |
| Mobile application assessment | `mobile-application` | Static analysis, data storage review, network security, runtime instrumentation, and binary protection |
| RFID/NFC assessment | `rfid-nfc` | Card identification, RFID/NFC assessment, smart-card testing, embedded device checks, and firmware analysis |
| VoIP/ICS protocols | `voip-ics` | VoIP/SIP enumeration, ICS/OT discovery, IPMI/BMC checks, SNMP testing, and protocol-specific read-only validation |
| Post-exploitation | `post-exploitation` | Privilege escalation, credential harvesting, lateral movement, persistence, tunneling, and C2/adversary emulation |
| Forensics triage | `forensics-triage` | Evidence handling, memory/disk/network analysis, timeline construction, log analysis, and artifact extraction |
| Source code & dependency audit | `source-code-audit` | SAST, secret scanning, dependency/SCA analysis, IaC scanning, and CI/CD pipeline review |
| Reporting | `reporting` | Finding organization, severity scoring (CVSS), evidence packaging, report generation, and delivery |

## Cross-Reference Map

Playbooks frequently hand off to each other as new signals emerge during testing:

| Source Playbook | Target Playbook | Trigger |
|----------------|-----------------|---------|
| `internal-network` | `internal-network-protocols` | Protocol-specific testing needed |
| `internal-network` | `active-directory` | AD domain discovered |
| `internal-network` | `web-application` | HTTP service found |
| `internal-network` | `api-security` | API endpoints found |
| `internal-network` | `cloud-native-assessment` | Kubernetes/Docker/cloud metadata |
| `internal-network` | `voip-ics` | VoIP/ICS/OT services |
| `internal-network` | `password-audit` | hashes captured |
| `internal-network` | `post-exploitation` | initial access gained |
| `external-attack-surface` | `web-application` | web app discovered |
| `external-attack-surface` | `api-security` | API endpoint discovered |
| `external-attack-surface` | `reporting` | findings ready |
| `active-directory` | `password-audit` | hashes for cracking |
| `active-directory` | `post-exploitation` | domain compromised |
| `cloud-native-assessment` | `internal-network` | VPC network testing |
| `cloud-native-assessment` | `post-exploitation` | container escape |
| `cloud-native-assessment` | `source-code-audit` | CI/CD pipeline review |
| `cloud-native-assessment` | `reporting` | findings ready |
| `forensics-triage` | `password-audit` | encrypted evidence |
| `forensics-triage` | `reporting` | documentation |
| `rfid-nfc` | `wireless-assessment` | Bluetooth proximity |
| `rfid-nfc` | `reporting` | evidence packaging |
| `api-security` | `web-application` | general web testing |
| All playbooks | `reporting` | final deliverable |

## Category References

After selecting a playbook, read the category `INDEX.md` to choose suitable tools:

| Scope | Reference |
|-------|-----------|
| Information gathering & OSINT | `information-gathering/INDEX.md` |
| Vulnerability analysis | `vulnerability/INDEX.md` |
| Sniffing & spoofing | `sniffing-spoofing/INDEX.md` |
| Web application and API testing | `web/INDEX.md` |
| Exploitation & pivoting | `exploitation/INDEX.md` |
| Password attacks & cracking | `password/INDEX.md` |
| Wireless & Bluetooth | `wireless/INDEX.md` |
| Cloud-native security | `cloud-native/INDEX.md` |
| Reverse engineering | `reverse-engineering/INDEX.md` |
| RFID/NFC | `rfid-nfc/INDEX.md` |
| VoIP/ICS protocols | `voip-ics/INDEX.md` |
| Forensics & triage | `forensics/INDEX.md` |
| Post-exploitation tools | `post-exploitation/INDEX.md` |
| Reporting | `reporting/INDEX.md` |
