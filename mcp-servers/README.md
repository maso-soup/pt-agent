# MCP Servers

This directory holds custom Model Context Protocol servers built for this framework —
tool integrations that agents and skills call into (scanners, cloud APIs, credential
databases, reporting backends, etc.) beyond what a generic Bash/WebFetch toolset covers.

## Convention

Each server lives in its own subdirectory and is self-contained:

```
mcp-servers/
└── <server-name>/
    ├── README.md        # what it wraps, auth requirements, safety notes
    ├── package.json      # or pyproject.toml for Python servers
    └── src/
```

Register a server by adding it to the root [.mcp.json](../.mcp.json) `mcpServers` map.

## Planned servers

None are implemented yet — this is scaffolding to grow into. Candidates as the
framework matures:

- **nmap-mcp** — structured wrapper around nmap/masscan scan output
- **cloud-enum-mcp** — unified AWS/Azure/GCP recon (IAM, storage, compute inventory)
- **burp-mcp** — drive Burp Suite scans and pull findings programmatically
- **secrets-scan-mcp** — search public repos/CI artifacts for leaked credentials
- **reporting-mcp** — turn engagement notes into client-ready report drafts

If a general-purpose MCP already covers a need (e.g. the Kali toolkit's nmap/gobuster/
hydra/sqlmap/metasploit tools), prefer wiring skills to that instead of building a new
server here.
