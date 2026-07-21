---
name: reporting
description: Scenario workflow for producing the penetration test deliverable — finding organization, severity scoring, evidence packaging, report generation, and delivery. Use after testing completes, or throughout testing to keep evidence report-ready.
---

# Reporting Workflow Playbook

Use after testing, or throughout testing to keep evidence ready for a final report.

## Inputs

- Authorized scope and test dates.
- Confirmed findings, raw tool output, screenshots, requests/responses, and notes.
- Required report format and audience.

## Workflow

1. **Executive summary**
   - Cover: engagement scope, testing approach and methodology, key risk themes identified, count of critical and high findings, and overall risk posture assessment.
   - Keep language non-technical — frame risks in business impact terms (data exposure, service disruption, regulatory consequence).
   - This section is the first thing stakeholders read; ensure it stands alone as a meaningful summary.

2. **Normalize evidence**
   - Group evidence by finding, affected asset, severity, and proof.
   - Keep raw tool output separate from analyst conclusions.

   (See `../../reference/reporting/INDEX.md` for reporting tool selection.)

   ```bash
   mkdir -p /tmp/report/{evidence/{screenshots,scans,raw},findings}
   cat nuclei_findings.jsonl | jq -r '[.info.severity, .info.name, .host] | @tsv' > /tmp/report/finding_summary.tsv
   ```

3. **Validate findings**
   - Confirm each finding has reproducible evidence.
   - Remove duplicates and mark false positives clearly.
   - For tool-only findings, add manual or second-tool validation when feasible.

   **Finding completeness check:** Verify that every tested service and every tool run has at least one finding or an explicit negative-result entry. Do not leave tested services undocumented — negative results are evidence that testing was performed.

4. **Assign severity**
   - Rate impact and likelihood in context.
   - Note exploitability, authentication requirement, exposure, and compensating controls.
   - Apply Environmental and Temporal adjustments when the target environment context is known (e.g., compensating controls, defense-in-depth, exploit maturity).


5. **Write findings**
   - Include title, description, impact, likelihood, evidence, affected assets, reproduction steps, and remediation.
   - Avoid unsupported claims and clearly state limitations.

6. **Create supporting artifacts**
   - Before generating the report, copy all tool outputs and evidence files produced during the test from the remote environment to the host; report generation should run on the host.
   - Use `gowitness` for screenshots when needed (see `../../reference/information-gathering/tools/gowitness.md`).
   - Use `pandoc` for format conversion when requested (see `../../reference/reporting/tools/pandoc.md`).
   - Use `../../reference/reporting/tools/report-template.md` as the base structure.
   - Write long reports in sections rather than as a single operation to avoid write failures.

   ```bash
   # gowitness v3 syntax (Kali 2024+)
   gowitness scan file -f urls.txt --screenshot-path /tmp/report/evidence/screenshots/
   pandoc /tmp/report/report.md -o /tmp/report/report.pdf --pdf-engine=wkhtmltopdf
   ```

7. **Peer review**
   - Before final delivery, conduct a peer review covering:
     - Technical accuracy: are findings correctly described and categorized?
     - Reproducibility: can each finding be reproduced using the documented steps?
     - Sensitive data redaction: verify no client credentials, tokens, or PII appear in the report body or evidence.
     - Severity consistency: are similar findings rated at the same severity across the report?
     - Spelling and grammar check on all narrative sections.

8. **Final review**
   - Check scope alignment, sensitive data handling, command log accuracy, and artifact references.
   - Include important negative results and unreachable-target notes when they affect conclusions.

## Cross-References

- `../active-directory/SKILL.md` — final deliverable step after AD testing completes.
- `../api-security/SKILL.md` — final deliverable step after API testing completes.
- `../cloud-native-assessment/SKILL.md` — final deliverable step after cloud assessment completes.
- `../external-attack-surface/SKILL.md` — final deliverable step after external testing completes.
- `../forensics-triage/SKILL.md` — final deliverable step after forensic triage completes.
- `../internal-network/SKILL.md` — final deliverable step after internal network testing completes.
- `../mobile-application/SKILL.md` — final deliverable step after mobile testing completes.
- `../password-audit/SKILL.md` — final deliverable step after password audit completes.
- `../post-exploitation/SKILL.md` — final deliverable step after post-exploitation completes.
- `../rfid-nfc/SKILL.md` — final deliverable step after RFID/NFC testing completes.
- `../source-code-audit/SKILL.md` — final deliverable step after source code audit completes.
- `../voip-ics/SKILL.md` — final deliverable step after VoIP/ICS testing completes.
- `../web-application/SKILL.md` — final deliverable step after web application testing completes.
- `../wireless-assessment/SKILL.md` — final deliverable step after wireless assessment completes.

## Expected Artifacts

- Final report.
- Evidence bundle or artifact index.
- Command log summary.
- Remediation summary.

## Stop When

- Every confirmed finding has evidence and remediation.
- Scope, limitations, and residual risks are documented.
- Client has accepted the deliverable format.
- Retest plan is documented with timeline and responsible parties.
- All critical findings have been communicated via the agreed channel (e.g., immediate notification for critical/high severity).
