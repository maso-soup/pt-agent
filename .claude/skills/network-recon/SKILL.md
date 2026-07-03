---
name: network-recon
description: Perform network reconnaissance — host discovery, port scanning, and service/version fingerprinting — as the first phase of an authorized network penetration test. Use when starting a new network engagement or when asked to map hosts, open ports, or running services on a target network/range.
---

## Purpose

Establish an accurate map of live hosts, open ports, and running service
versions before any exploitation attempt. Every downstream foothold skill
depends on this being thorough and correct.

## When to use

- Start of any network/internal/external pentest engagement.
- When the user provides a CIDR range, host list, or single IP/hostname and asks
  "what's running here" or "map this network."

## Methodology

1. Confirm scope explicitly (CIDR ranges/host lists from the RoE) before sending
   a single packet.
2. **Host discovery** — identify live hosts in scope (ICMP/ARP/TCP ping sweeps as
   appropriate to the environment).
3. **Port scanning** — full TCP port sweep on live hosts, followed by targeted
   UDP scanning for common services (DNS, SNMP, NTP).
4. **Service/version fingerprinting** — banner grab and version-detect every open
   port; note anything unusual (non-standard ports, self-signed certs, custom
   banners).
5. **OS fingerprinting** — narrow down likely OS/patch level to help prioritize
   later exploit selection.
6. Consolidate into a host-by-host inventory (IP, hostname, open ports, service +
   version, OS guess) and hand off to the relevant foothold skill(s).

## Tools

- `nmap` — the primary tool. Typical flow: `-sn` for discovery, `-p-` full TCP
  sweep, `-sV -sC` for version/script detection on discovered ports, `-sU` for a
  top-N UDP scan. If the Kali MCP toolkit is available, use its `nmap_scan` tool
  rather than shelling out directly.
- `masscan` for very large ranges where nmap's full sweep would be too slow —
  follow up with nmap `-sV` on masscan's hits for accuracy.
- A full `-p-` sweep or a large `-sV -sC` run can exceed a single Kali MCP
  `execute_command` call's timeout. If that happens, use the `tmux-shell` MCP
  server (a persistent tmux session on the Kali host) to launch the scan and
  poll its output, rather than backgrounding it manually with `nohup`/`&` and
  polling via repeated `execute_command` calls.

## Output

A structured inventory (table or JSON) of hosts/ports/services/versions. Flag
anything that looks like a fast path to foothold (SMB, RDP, exposed admin
panels, default-looking banners) so the agent can route to the right skill next.

## Safety notes

- Stay within the authorized rate/timing window — aggressive timing templates
  (`-T4`/`-T5`) can trip IDS/IPS or destabilize fragile embedded devices (printers,
  OT/ICS gear). Default to `-T3` unless the RoE says otherwise.
- Never scan hosts discovered incidentally (neighboring subnets, gateways) that
  aren't in the signed scope.
