---
id: global-index
owner: oneshot-system
last_updated: 2025-08-25
status: active
summary: Central index and quick reference for the oneshot specialist agent orchestration framework
---

# TL;DR (for agents)

- **Project**: Oneshot — Specialist AI agent orchestration framework for knowledge work
- **Source of truth**: `/global/*` overrides all other documentation
- **Before coding, always**:
  1) Check invariants in ARCHITECTURE.md
  2) Check acceptance criteria in SPEC.md  
  3) Check public surfaces in API.md
  4) Obey RULES.md (enforced via Cursor)

## Repo Map

- **Layout**: Monorepo with agents, tools, tasks, and global documentation
- **Build**: Python/PydanticAI with pip install -r requirements.txt
- **Environments**: Development (local), Production (user systems)
- **Entry Points**: CLI (`./oneshot`), MCP Server (Cursor integration)

## Invariants (non-negotiable)

- **Agent Specialization**: Each agent has focused expertise and specific tools
- **Artifact-First Design**: Agents produce files that are passed between workflows
- **Tool Services Usage**: All tools must use `from app.tool_services import *`
- **Run ID Persistence**: All operations maintain conversation continuity via run IDs
- **Windows Compatibility**: All code must work cross-platform (Windows/Mac/Linux)
- **Testing Requirements**: All task completions require passing automated tests
- **Git Workflow**: All task completions require automated commit/push

## System Components

- **8 Specialist Agents**: research, vision, web, nrl, news_search, search, search_analyst, oneshot
- **25 Core Tools**: File ops, web search, research, export, todo management, agent coordination
- **Task Management**: 7-step SOP workflow for complex development tasks  
- **Global Rules**: Cross-system enforcement of coding standards and protocols

## Current Architecture

```
oneshot/
├── agents/          # AI agents (markdown files with YAML frontmatter)
├── tools/           # Python tools agents can use  
├── app/             # Core system (agent runner, MCP server, tool services)
├── tasks/           # Task management workspace (timestamped folders)
├── global/          # Global documentation (this directory)
├── artifacts/       # Agent-generated files organized by run ID
├── runs/            # Conversation histories  
├── config.yaml      # System configuration and model defaults
└── .cursor/rules/   # Cursor IDE integration rules
```

## Pointers

- **Architecture** → ./ARCHITECTURE.md
- **Spec** → ./SPEC.md  
- **APIs** → ./API.md
- **Rules** → ./RULES.md
- **Onboarding** → app/guides/onboarding.md
- **System Details** → app/guides/how_oneshot_works.md

## Changelog (last 5)

- 2025-08-25 — Created global documentation system with architecture analysis ([this task](tasks/2025-08-25_GlobalDocs_System_Analysis/))
- 2025-08-25 — Enhanced anti-stall protocols and buffer reset mechanisms ([stall prevention task](tasks/2025-08-25_CursorAgent_StallPrevention/))
- 2025-08-25 — Completed comprehensive Windows testing framework ([windows testing](tasks/2025-08-25_Oneshot_Windows_Testing/))  
- 2025-08-24 — Resolved critical Windows compatibility issues in MCP server ([windows compatibility](tasks/2025-08-24_OneShot_Windows_Compatibility/))
- 2025-08-24 — Standardized date tooling across all task workflows ([date standardization](tasks/2025-08-24_GlobalRules_DateStandardization/))
