---
title: "Session Role Clarification: Roles vs Agents vs Templates"
created: "2025-08-27T05:42:12.332Z"
type: "brainstorm"
purpose: "Explore and clarify the distinctions between AI assistant roles, individual agents, and session templates; capture decision points and next steps for implementation"
status: "Active"
tags: ["roles","agents","templates","brainstorm"]
---

# Session Role Clarification — Brainstorm

This document explores the overlap and boundaries between the following concepts:

- Agent Roles: Orchestrator, Designer, Developer
- Individual Agents: research_agent, search_agent, vision_agent, web_agent, etc.
- Session Templates: coding, troubleshooting, research, checkpoints, snippets

## Problem Statement

Users are confused about when to treat an activity as a role-based action (Designer/Developer/Orchestrator) versus a session type (coding/troubleshooting/research). We need a clear decision matrix and practical rules so that the system behaves predictably.

## Key Questions to Resolve

- When should the assistant switch from Orchestrator to Developer or Designer?
- Are templates and checkpoints created by Designer or Developer flows?
- How do agent MD files (in `/agents`) determine agent capabilities and tool access?
- How should projects that include core-system work be handled (developer vs project session)?

## Proposed Decision Matrix (Draft)

- If the user explicitly asks to change the **oneshot system code**, take **Developer** role.
- If the user asks to **create or configure agents/tools/templates/checkpoints** that are *intended for reuse in the system*, take **Designer** role (must read how-to guides first).
- If the user asks for **general work, research, or project tasks** that do not modify oneshot internals, take **Orchestrator** role.
- If the user requests both (e.g., build an agent and also modify core behavior), default to **Designer** and ask clarification about whether core changes are required.

## Agent MD Files and Capabilities

- Agent definitions in `/agents/*.md` contain YAML frontmatter with model, tools, and system prompt.
- Designer role is responsible for editing/creating these files (after reading `how_to_create_agents.md`).
- Orchestrator uses `list_agents` to discover agents and delegates tasks; it does NOT modify agent MD files.

## Templates, Snippets, Checkpoints

- Templates and snippets used for session organization are managed by `TemplateManager`.
- Creation of new **system-wide templates/checkpoints** should be considered a Designer task.
- Ad-hoc templates or project-local templates may be created by Orchestrator on behalf of the user and stored under `vault/sessions/...`.

## Edge Cases and Clarifications

- "Create a dev project" can mean either creating a project using templates (Orchestrator) or changing the system to add new development workflows (Developer). Ask clarifying question when ambiguous.
- Designer must always run through guide checks before creating system-wide artifacts.

## Next Steps (Actionable)

- Add this note to the brainstorm folder (done)
- Create a short checklist for the Assistant to ask clarifying questions when ambiguous
- Update `app/guides/how_oneshot_works.md` with a short section summarizing this decision matrix
- Update UML and architecture docs to link to this brainstorm decision matrix


<!-- EVALUATION & RECOMMENDATION APPENDIX -->

## Evaluation: pros / cons of the three-role model

### Current 3-role model (Orchestrator / Designer / Developer)

- **Pros**:
  - Simple and easy to reason about.
  - Clear separation of responsibilities: orchestration vs system extension vs core maintenance.
  - Enforces safety: Designer/Developer require guides/readme checks before making system changes.
  - Fits current repo organization (`/agents`, `/tools`, `app/guides`).

- **Cons**:
  - Ambiguity when a user request spans both system changes and project work (e.g., "build a dev project and change system hooks").
  - Overloading: "Developer" can mean both modify core system and run user’s development tasks if not scoped strictly.
  - Potential friction: users must understand subtle difference between creating system-wide templates (Designer) and ad-hoc project templates (Orchestrator).

### Alternatives considered

1. **Role-per-action (fine-grained capabilities)**
   - Each assistant response declares a capability vector (e.g., {orchestrate:yes, modify_core:no, create_agent:yes}).
   - **Pros**: Very flexible, less binary switching.
   - **Cons**: More complex; increases cognitive load and makes permissions/policies harder to enforce.

2. **Two-tier model: Operator vs Builder**
   - `Operator` (orchestrator-like) for external tasks; `Builder` (designer+developer) for any system/agent/tool work.
   - **Pros**: Simpler than 3 roles; reduces confusion between Designer/Developer.
   - **Cons**: Loses the explicit separation between making agents (Designer) and changing core system (Developer); may be less safe.

3. **Contextual subroles (primary + scope flag)**
   - Keep 3 primary roles, but attach a `scope` flag: `scope:system|project|session`. The role + scope together determine permissions.
   - **Pros**: Preserves current model, adds clarity on whether actions affect system vs project vs session.
   - **Cons**: Slightly more complex, but much clearer for ambiguous cases.

## Recommendation (concise)

- **Keep the three roles** (Orchestrator, Designer, Developer) for clarity and safety **but add a `scope` flag** to disambiguate intent: `system`, `project`, or `session`.
  - Examples:
    - Designer + scope:system → creates system-wide agents/templates (modify `/agents`, `/snippets`)
    - Designer + scope:project → creates reusable agents/templates but stored under a project namespace or vault project (less privileged)
    - Orchestrator + scope:session → ad-hoc templates and files under `vault/sessions/` only
    - Developer + scope:system → modify core `app/` code or core pipeline

- **Behavior rules**:
  - If role is Designer/Developer with `scope:system`, require mandatory guide/readme verification before changes (existing rule).
  - If ambiguous, ask 2 clarifying questions (see checklist below). Default to Designer+scope:project rather than making system changes.

- **Why**: preserves safety and the current mental model but solves the ambiguous "dev project vs core dev" case without removing useful distinctions.

## Assistant clarifying-question checklist (use when ambiguous)

1. "Do you want this change to affect the oneshot system code or only your project files?"
2. "Should the agent/template be reusable system-wide (yes) or private to this project/session (no)?"
3. If user answers both/uncertain: "I can either (A) make a project-local version now, or (B) make a system-wide change but I must first read the onboarding/how-to guides — which do you prefer?"

## Example flows

- User: "Create a research agent that can fetch papers and summarize"
  - Assistant: Designer + scope:project (asks whether to make it system-wide). If user says system-wide, run guides and proceed.

- User: "Set up a dev project to track feature work"
  - Assistant: Orchestrator + scope:project — create `vault/projects/<name>/` and apply coding template.

- User: "Add a new CI hook to oneshot to run tests"
  - Assistant: Developer + scope:system — require onboarding read and confirm before edits.


---

*Appended recommendations and clarifying prompts.*
