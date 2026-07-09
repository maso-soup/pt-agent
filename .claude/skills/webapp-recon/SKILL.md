---
name: webapp-recon
description: Perform web application reconnaissance — content/endpoint discovery, technology fingerprinting, and attack surface mapping — as the first phase of an authorized web app penetration test. Use when starting a new web/API engagement or asked to map an application's structure and tech stack.
---

## Purpose

Build a complete map of the application's attack surface — endpoints, forms,
APIs, technology stack, and exposed but forgotten content — before any
exploitation attempt. This determines which foothold skills are relevant.

## When to use

Start of any web application or API pentest engagement, once the target
hostname(s)/URL(s) are confirmed in scope.

## Methodology

1. **Technology fingerprinting** — server, framework, language, and known
   library versions from headers, error pages, and static asset paths.
2. **Content/endpoint discovery** — directory and file brute forcing plus
   crawling to find pages, forms, and API routes not linked from the visible
   UI (admin panels, backup files, debug endpoints, old API versions).
3. **API surface mapping** — for REST/GraphQL APIs, enumerate
   routes/operations, including introspection queries for GraphQL and
   spec files (`openapi.json`, `swagger.json`) if exposed.
4. **Authentication/session mapping** — identify login flows, session token
   mechanism (cookie/JWT/etc.), and any multi-tenancy or role boundaries.
5. Consolidate into an attack-surface map: endpoint, method, auth requirement,
   parameters, and technology involved — flag anything unusual (exposed
   `.git`, backup files, verbose error pages, outdated library versions with
   known CVEs) for immediate follow-up.

## Tools

- `gobuster` / `dirb` / `feroxbuster` for content/directory discovery against a
  curated wordlist.
- `nikto` for known-vulnerability and misconfiguration checks.
- `wpscan` when the target is WordPress.
- Browser dev tools / JS bundle review for client-side-referenced API
  endpoints not otherwise discoverable.
- A large-wordlist `gobuster`/`dirb` run can be slow — give it a generous
  timeout, or run it in the background and poll the output file.

## Output

Attack-surface map (endpoints, parameters, auth requirements, technology
versions) plus a shortlist of high-signal findings (exposed `.git`,
debug/admin endpoints, outdated components) to route into the matching
foothold skill.

## Safety notes

- Content discovery brute forcing generates significant request volume —
  respect rate limits, especially on shared/production infrastructure, and
  stop if the app shows signs of degradation.
- Don't test any linked third-party domain (analytics, payment processor, SSO
  provider) unless it's explicitly in scope.
