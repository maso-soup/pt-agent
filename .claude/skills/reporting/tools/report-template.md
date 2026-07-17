# Penetration Test Report Template

- **Category**: Reporting / Template
- **Risk Level**: 🟢 Low

---

## Description

Reusable penetration test report template for final deliverables. Use this file to structure executive summaries, scope, findings, evidence, remediation guidance, and appendices.

## Installation

Not applicable. This is a reusable documentation template, not an installable command-line tool.

## Parameter Reference

| Parameter | Description |
|-----------------------|-------------|
| `{Client Name}` | Client or engagement name |
| `{IP/Domain}` | Authorized test scope |
| `{Start Date} ~ {End Date}` | Testing period |
| `{Vulnerability Name}` | Finding title |
| `{System/Location}` | Affected system, endpoint, or asset |
| `{impact description}` | Business or technical impact summary |
| `F-###` | Finding identifier format |

## Common Commands

### Complete Report Structure

````markdown
# Penetration Test Report
**Client**: {Client Name}
**Scope**: {IP/Domain}  
**Test Period**: {Start Date} ~ {End Date}  
**Test Type**: Black-box / Grey-box / White-box  
**Report Date**: {Date}  
**Report Version**: v1.0  
**Confidentiality**: Confidential

---

## Executive Summary

This should be a succinct paragraph very briefly describing that the penetration test was performed and a brief recap of the type of testing and intention with this testing. Do not include any technical details or finding specifics, as this is more an introduction paragraph than a discussion. 

---

## Improvement Opportunities

These should be single sentence, high-level versions of the vulnerability descriptions for each of the findings. These should be in a bulleted list. 

---

## Key Strengths

These should be a few different single sentence, high level versions of any secure parts of the system or security controls that were noted to be in place during the testing. These should be in a bulleted list. 

---

## High Level Recommendations

These should be single sentence, high level versions of the Remediations for each of the findings. These should be in a bulleted list.

---

## Test Objectives

These are a few very high level test objectives that were used as guidance for engagement. These should be in a bulleted list.

---

## Test Actions

These are few single sentence descriptors of high level discrete actions taken throughout the test. These should be in a bulleted list. 

---

## Attack Narrative

This is a section where a few succinct paragraphs should follow the general narrative of the testing, including what types of vulnerabilities were tested for and components of the system were targeted. 

---

## Vulnerability Details

### F-001: SQL Injection

**Description**:
Insert a succinct description of the vulnerability. 

**Impact Description**:

Insert a succinct paragraph describing the possible impact of the vulnerability in the organization. 

**Likelihood Description**:

Insert a succinct paragraph describing the possible likelihood of the exploitation of the vulnerability in the organization. 

**Evidence**:

Insert evidence of the vulnerability here. This can include tools used, commands, reproduction steps, screenshots, etc.

Reproduction Steps:
1. Navigate to `http://target.com/login`
2. Enter in the username field: `admin' OR '1'='1`
3. Enter any value in the password field and click Login
4. Successfully log in as an administrator

```
$ sqlmap -u "http://target.com/api/login" --data="username=test&password=test" --batch
[INFO] Parameter 'username' is vulnerable
[INFO] the back-end DBMS is MySQL
[INFO] retrieved: admin, password_hash, email from users table
```

**Remediation**:

Insert a brief description of possible remediation recommendations. 

---

(Fill in remaining findings using the same format)

````

### Impact and Likelihood Level Definitions

**Impact Level Definitions**

Critical - The vulnerability has proven to be exploitable and could be expected to have multiple severe or catastrophic adverse effects on the organization. 

High - The vulnerability could be expected to have a severe or catastrophic adverse effect on the organization. 

Medium - The vulnerability could be expected to have a serious adverse effect on the organization. 

Low - The vulnerability could be expected to have a limited adverse effect on the organization. 

Very Low - Observation means that no action is required. This value is selected when the organization should maintain awareness of a security best practice or guideline.

**Likelihood Definitions**

Critical - Adversary is almost certain to initiate the threat event.

High - Adversary is highly likely to initiate the threat event.

Medium - Adversary is somewhat likely to initiate the threat event.

Low - Adversary is unlikely to initiate the threat event.

Very Low - Adversary is highly unlikely to initiate the threat event.

### Placeholder Rules

Use these rules to populate placeholders automatically:

| Placeholder | Source |
|-------------|--------|
| `{Client Name}` | Extract from user message — look after "client:", "target:", "assessment:", "company:" |
| `{IP/Domain}` | Collect from authorized scope confirmation at the start of the engagement |
| `{Start Date} ~ {End Date}` | Timestamp of the first command run and the last command run; use `date -I` format |
| `{Vulnerability Name}` | From nuclei `info.name`, sqlmap result, or manual finding title |
| `{System/Location}` | From nuclei `host` field, `matched-at` URL, or nmap target |
| `{impact description}` | Infer from vulnerability type: SQLi → "unauthorized database access", RCE → "full system compromise" |
| `F-###` | Auto-number: sort findings by severity (Critical→High→Medium→Low), assign F-001, F-002, ... |
| Tools Used table | Extract tool names and versions from `{tool} --version 2>&1` or `{tool} -h` output during testing |

### Data Extraction Commands

```bash
# 1. Extract severity, name, and host from nuclei JSONL
cat nuclei_findings.jsonl | jq -r '[.info.severity, .info.name, .host] | @tsv' | sort -k1,1 | nl -ba -nrz -w3 | awk -F'\t' '{printf "F-%s\t%s\t%s\t%s\n", $1, $2, $3, $4}' > findings.tsv

# 2. Extract SQL injection results
grep -E "Parameter|vulnerable|back-end" /tmp/sqlmap/*/log | sed 's/^/F-SQL-/'

# 3. Extract open ports from nmap XML
grep '<port protocol="tcp".*state="open"' scan.xml | grep -oP 'portid="\K[^"]+' | sort -n | paste -sd ','
```

## Notes & Tips

1. Keep the executive summary non-technical and focused on business impact.
2. Every finding should include affected assets, reproducible evidence, impact, and remediation guidance.
3. Preserve authorization scope and testing constraints in the final report.
4. Before the final report is generated, if there are any major questions about what has or hasn't been tested, ask the user and wait for the response. This can help ensure full coverage. During the assessment the user may perform checks, tests, or actions outside of the session that you might not be aware of.
5. When determining impact and likelihood, ask for the user for any extra details that may be relevant to determining the accurate ratings for impact and likelihood. 