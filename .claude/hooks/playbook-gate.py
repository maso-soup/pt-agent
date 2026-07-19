#!/usr/bin/env python3
"""Playbook engagement gate for pt-agent (PreToolUse hook).

Enforces the AGENTS.md rule that a scenario playbook Skill must be invoked
before any recon/attack tooling runs against a target.

Registered on PreToolUse for Skill, Read, and Bash:
  - Skill(<playbook>)              -> record a per-session marker ("entered")
  - Read(.../.claude/skills/<pb>/SKILL.md) -> same marker (harness-neutral
        entry for harnesses without a Skill tool, e.g. Continue CLI)
  - Bash(<recon tool>)             -> block (exit 2) unless the marker exists

Both playbook-entry methods (Skill tool or reading the SKILL.md file) are
treated as equivalent so a single instruction set works across harnesses.
Keep the Skill|Read|Bash matcher in settings.json in sync with this.

Reads the hook input JSON from stdin. Fails open on any error so a bug here
never bricks tool use. Depends only on python3 (already in the environment);
jq is intentionally not required.
"""
import sys
import os
import re
import json
import tempfile

PLAYBOOKS = {
    "active-directory", "api-security", "cloud-native-assessment",
    "external-attack-surface", "forensics-triage", "internal-network",
    "internal-network-protocols", "mobile-application", "password-audit",
    "post-exploitation", "rfid-nfc", "source-code-audit", "voip-ics",
    "web-application", "wireless-assessment", "reporting",
}

# Recon / attack tools whose use signals we are engaging a target.
RECON_TOOLS = (
    "nmap", "masscan", "rustscan", "naabu", "ffuf", "gobuster", "feroxbuster",
    "dirb", "dirbuster", "wfuzz", "nikto", "whatweb", "nuclei", "katana",
    "httpx", "hydra", "medusa", "crackmapexec", "nxc", "netexec", "sqlmap",
    "wpscan", "enum4linux", "enum4linux-ng", "smbclient", "smbmap",
    "onesixtyone", "snmpwalk", "dnsenum", "dnsrecon", "sublist3r", "amass",
    "msfconsole", "searchsploit", "evil-winrm", "responder",
)
RECON_RE = re.compile(
    r"(?<![A-Za-z0-9_.-])(?:" + "|".join(re.escape(t) for t in RECON_TOOLS) +
    r"|impacket-[A-Za-z0-9_]+)(?![A-Za-z0-9_-])"
)

# A Read of one of these paths counts as entering that playbook, for harnesses
# that load SKILL.md by reading the file instead of via a Skill tool.
SKILL_PATH_RE = re.compile(
    r"\.claude/skills/(" + "|".join(re.escape(p) for p in PLAYBOOKS) +
    r")/SKILL\.md$"
)


def marker_path(session_id):
    safe = re.sub(r"[^A-Za-z0-9_.-]", "_", str(session_id)) or "nosession"
    return os.path.join(tempfile.gettempdir(), "pt-agent-playbook-active-" + safe)


def main():
    try:
        data = json.load(sys.stdin)
    except Exception:
        return 0  # fail open

    tool = data.get("tool_name", "")
    marker = marker_path(data.get("session_id", "nosession"))
    tool_input = data.get("tool_input") or {}

    if tool == "Skill":
        if tool_input.get("skill", "") in PLAYBOOKS:
            try:
                open(marker, "w").close()
            except Exception:
                pass
        return 0

    if tool == "Read":
        path = tool_input.get("file_path", "") or ""
        if SKILL_PATH_RE.search(path):
            try:
                open(marker, "w").close()
            except Exception:
                pass
        return 0

    if tool == "Bash":
        if os.path.exists(marker):
            return 0
        cmd = tool_input.get("command", "") or ""
        if RECON_RE.search(cmd):
            sys.stderr.write(
                "BLOCKED by playbook gate: no scenario playbook Skill has been "
                "invoked this session.\n"
                "Per AGENTS.md, before running recon/attack tooling you must: "
                "(1) read .claude/reference/playbook-selection.md, then "
                "(2) invoke the matched Skill(skill: \"<name>\"). Recon is NOT "
                "exempt — \"it's just an nmap\" is the rationalization this gate "
                "exists to stop. Invoke the playbook Skill, then re-run this "
                "command.\n"
            )
            return 2
        return 0

    return 0


if __name__ == "__main__":
    sys.exit(main())
