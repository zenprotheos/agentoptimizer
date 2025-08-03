


## Managing Token Costs

Use Cursor on Auto mode for free to do your agent orchestration. Use cheap models like gpt-4.1-mini to do the work
Keep your Cursor/Claude credits for coding tasks

## Learn how to build agents

Quickly create new agents just with markdown files
Try out different models via built in openrouter integration
Inspect and observe agent runs via Logfire
Cookbook with examples

## Learn about Context Management

Lots of advanced prompt examples
Use of files to pass context between agents 
Supports orchestrator -> sub agent pattern out of the box

## Learn about MCP servers

The system can be used as an MCP server
The system is also an MCP client supporting any MCP servers
The system knows how to build mcp servers for you
Connect your agents to Zapier/N8N, etc mcp servers
Lots of examples included

## Collaboration

Easily share tools and agents by copy and paste from a gist
Run the system in the cloud as a fastapi app

## Self-aware system

Knows how to onboard itself
Knows how to set you up
Knows how to build agents and tools for you
Knows how to troubleshoot

## All about Artifacts

The system is built to create useful artifacts for you
Easily create agents that have multi-step workflows with tools to generate useful artifacts

## Use the stack that openai uses

PydanticAI
Openrouter
Logfire
Fastapi

# Context management features

Rules: The rules in the `/.cursor/rules` directory tell the main orchestrator agent (ie the Cursor agent) how to behave.

Snippets: save bits of reusable text in md files in the `/snippets` directory for use in prompts, agents and tools

Artifacts: the tool system is designed to create useful artifacts (ie files), in the `/artifacts` directory. Eg reports, email drafts, posts, etc

Templates: html and other templates get used by tools for generating finished artifacts. They get stored in the `/templates` directory.

Runs: the state of a given agent session is stored in the `/runs` directory and allows for run continuation and multi-agent collaboration.