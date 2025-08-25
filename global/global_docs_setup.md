# Global Docs Template — Starter (No CI, Cursor‑Integrated)

> Purpose: a minimal, low‑friction set of global docs that coding agents (Cursor, VS Code assistants) can rely on as the single source of truth. Optimized for frequent edits; expandable later.

## Folder Layout (repo root)

```
/global
  ├─ GLOBAL_INDEX.md     # One‑pager TL;DR + invariants + pointers + mini‑changelog
  ├─ ARCHITECTURE.md     # Boundaries, flows, invariants, SLOs (short)
  ├─ SPEC.md             # Behaviors + acceptance criteria (executable style)
  ├─ API.md              # Public surfaces (HTTP/RPC, events, CLI, DB contracts)
  └─ RULES.md            # Agent/global rules map; referenced by Cursor global rules
# Optional later:
#  ├─ GLOSSARY.md        # Only if domain language grows
#  └─ CHANGELOG.md       # Otherwise keep “last 5” in GLOBAL_INDEX.md
```

---

## 0) Principles

* **Zero friction**: No CI checks, no doc linters. Edit code and docs together.
* **Single source**: `/global` wins over README or comments if conflicts.
* **Small + sharp**: Each required doc ≤ \~2 pages; begin with a TL;DR.
* **Links over prose**: Prefer permalinks to code/tests over long descriptions.
* **Cursor integration**: RULES live in Cursor’s global rules; `/global/RULES.md` documents the process.

Front‑matter (optional but helpful):

```yaml
---
id: <stable-slug>
owner: <team-or-handle>
last_updated: <YYYY-MM-DD>
status: active|draft|deprecated
summary: Short one‑liner for agents.
---
```

---

## 1) GLOBAL\_INDEX.md (Template)

```markdown
# TL;DR (for agents)
- Project: <name> — <1 line goal>.
- Source of truth: `/global/*` overrides all.
- Before coding, always:
  1) Check invariants in ARCHITECTURE.md
  2) Check acceptance criteria in SPEC.md
  3) Check public surfaces in API.md
  4) Obey RULES.md (enforced via Cursor)

## Repo Map
- Layout: <monorepo/services/apps>
- Build: <tool>
- Environments: <dev/stage/prod>

## Invariants (non‑negotiable)
- <Invariant 1>
- <Invariant 2>

## Pointers
- Architecture → ./ARCHITECTURE.md
- Spec → ./SPEC.md
- APIs → ./API.md
- Rules → ./RULES.md

## Changelog (last 5)
- YYYY‑MM‑DD — <what changed> (<commit/PR link>)
```

---

## 2) ARCHITECTURE.md (Template)

```markdown
# System Overview
- Context: <1 paragraph>
- Diagram: <Mermaid or image link>

# Boundaries & Ownership
- <Context A>: owns <capabilities>. Path: <dir>. Owner: <handle>.
- <Context B>: …

# Data Flow (happy path)
1) … → 2) … → 3) …

# Critical Invariants (do not break)
- IDs are <ULID/UUID>
- Timestamps are UTC ISO‑8601
- Retries are idempotent; timeouts: client 5s, upstream 2s

# Failure & Recovery
- Circuit breakers, queues, fallbacks (1–3 bullets)

# Performance Targets (SLOs)
- p95 <X> ms for <endpoint>; throughput <N>/s

# Security
- AuthN/AuthZ model; PII locations (fields only)
```

---

## 3) SPEC.md (Template)

```markdown
# Scope & Non‑Goals
- In: …
- Out: …

# Functional Requirements
- FR‑1: <behavior>. Rationale: <why>.
- FR‑2: …

# Acceptance Criteria (executable style)
- Given <context>, when <action>, then <observable result>.
- Golden cases: <test links>

# Edge Cases & Constraints
- <rate limits, timezones, unusual inputs>

# Telemetry
- Events: <name + schema link>
- Metrics: <name + unit>
```

---

## 4) API.md (Template)

```markdown
# Versioning
- Policy: <semver/date>. Deprecation window: <N days>.

# HTTP / RPC
- `GET /v1/things/{id}` — Returns Thing. SLA: <p95>.
  - Request: <schema link>
  - Response: <schema link>
  - Errors: <codes>

# Events / Queues
- `thing.created` — <schema link>. Consumers: <services>

# CLI / SDK
- `thingctl sync --since=<ts>`

# Database Contract (if shared)
- Exposed tables/views and write rules.

# Examples
- Curl + client snippets.
```

---

## 5) RULES.md (Template)

```markdown
# Agent & Contributor Rules
- Always read `/global/GLOBAL_INDEX.md` and `/global/ARCHITECTURE.md` before coding.
- Implement only what’s in `/global/SPEC.md`. If missing, open an RfC and update the doc.
- Don’t change public surfaces without updating `/global/API.md`.
- Never violate invariants without updating ARCHITECTURE.md first.
- After behavior changes, add a one‑liner in GLOBAL_INDEX.md → Changelog (last 5).
```

---

## Maintenance Rhythm (Lightweight)

* **On change:** Update the relevant `/global` doc alongside the code.
* **Casual pass:** Periodically prune verbose sections and fix dead links.
* **Expand later:** Add `GLOSSARY.md`, `CHANGELOG.md`, or automation only when needed.

---

## Cursor Global Rules — Paste This (Reference)

```
Before coding:
- Read /global/GLOBAL_INDEX.md and /global/ARCHITECTURE.md.
- Respect invariants under “Critical Invariants.”
- Only implement behaviors defined in /global/SPEC.md.
- If touching public surfaces, update /global/API.md in the same PR.
- After changes, append one line to the mini‑changelog in GLOBAL_INDEX.md.

Never:
- Introduce new endpoints/events without documenting them in /global/API.md.
- Violate invariants without updating ARCHITECTURE.md.
```

---

## Minimal Checklist

* [ ] Create the 4 required docs + RULES.md
* [ ] Fill TL;DR + invariants
* [ ] Reference RULES.md from Cursor’s global rules
