
# Background


## Purpose

Oneshot was built to give friends and people in the Peregian Digital Hub network a powerful but approachable way to "vibe code" their own AI agent system that can do useful knowledge work for them. 

There's something magical about creating your own specialised AI assistants, and we wanted to make that accessible to everyone - not just experienced developers.

## How it works

This framework lets you create and orchestrate specialist AI agents without needing to understand complex infrastructure. You write a simple markdown file, and you have a working agent. You issue instructions to Cursor or Claude Code and they will orchestrate those specialised agents, to perform useful work for you.

The Oneshot system is self-describing to the likes of Cursor and Claude Code, which means they know immediately how it works and can do things like create agents and tools, in oneshot, or troubleshoot when things go wrong.

## Why Oneshot

The term "one shot" refers to an AI getting the right outcome the first time. Eg from a single prompt, a coding agent creates perfect working software, in one shot, without the need for correction and further "shots" to get it working.

If you're working in AI, you're constantly in pursuit of a oneshot machine - a system that produces valuable outputs in one shot, every time. 

This project won't get it right in one shot every time but that's the inspiration for it. There are a lot of behind the scenes prompts and instructions that are intended to have the coding agents like Cursor/Claude Code etc be able to use this and build things with it for you, in one shot, without mistakes.

# Benefits of the Oneshot system

## Managing Token Costs

Tools like Cursor and Claude Code that use the Claude models, are getting expensive $200 is the new $20. What if we could use cheaper models to do useful work for us and save those expensive tokens for high value software dev tasks. 

Oneshot gives you access to pretty much all the models available, via the openrouter gateway. You can use workhorses like gpt-4.1-mini to do the grunt work and powerful models like gemini-2.5-pro , gpt-4.1 to do more complex agent work, and reasoning models from openai, deepseek and others for planning and other high-IQ steps.

Importantly, you can use Cursor on Auto mode **for free** to do your agent orchestration work. It very reliably figures out which of your agents to invoke and does a good job of passing around files etc. This lets you keep your Cursor/Claude credits for higher value coding tasks and use these cheap models for day to day knowledge work.

## Learn by building

The Oneshot system is intended to make building agents a breeze. Create a md file in /agents with some frontmatter to specify the model, allocate a few tools and give it a system instruction and you're off to the races. Beter still, you can ask Cursor or Claude code to create a new agent for you and they'll read the instructions and do that in one shot without you having to lift a finger.

This lets you quickly create new agents just with markdown files and try out different models via the built in openrouter integration. 

## Auto Tool Creation

The Oneshot project also teaches the Orchestrator agent (Claude Code/Cursor agent) how to make tools, in one shot. Vibe code new tools by telling them what you want the tool to do and they will read instructions on how to create a tool, and how to use the built-in tool_services module (to reduce boilerplate) and it will likely work in one shot. You may have to add an api key or token to the env file but that's about it.

Within a couple of hours you'll have built out multiple agents with a growing portfolio of tools at their disposal. 

## Learn about Context Management

An important aspect of Oneshot is to demystify agentic systems and expose what goes into building them. 

Agents are effectively LLM chat prompts (with tools) running in a loop. The LLM receives the prompt, determines whether to call a tool, we execute the tool locally and respond back with tool response and we do this in a loop until the LLM determines that the task has been completed.

Most AI systems are black boxes - you see the magic but not how it works. Oneshot is transparent:

- Watch agents make decisions in real-time
- See exactly which tools they use and why
- Understand the conversation flow
- Debug when things go sideways

Through the Logfire integration, you get a window into the agent's "thought process" - it's both educational and fascinating.

The Oneshot repo comes with some handy examples to get you started with and a few useful tools that will be helpful for your agents. You can read the agent prompts, tool descriptions etc to get good examples of how to provide the right context to agents. 

## Novel Context Engineering approach

Oneshot uses a novel context management approach whereby agents produce artifacts (files) and pass these files to each other to perform work on. This allows for more accurate agent orchestration because the context window does not get crowded with voluminous tool output responses. 

This lends itself to the orchestrator -> sub agent pattern, where an Orchestrator agent (eg Cursor agent, Claude code agent or other) delegates tasks to specialist agents. The specialist agents perform the detailed work, which may involve many tools calls and lots of context processing, but they respond back to the agent with only the artifact they produced from that process. This allows the main thread (ie, the Orchestrator's context window) to remain "clean". 

Oneshot is built on the open source PydanticAI library which has lots of extensibility and you are free to evolve this repo to try more optimised context management strategies.

## Learn about MCP servers

The system can be used as an MCP server
The system is also an MCP client supporting any MCP servers
The system knows how to build mcp servers for you
Connect your agents to Zapier/N8N, etc mcp servers
Lots of examples included

## Collaboration

One of the principles for the Oneshot system is to enable very lightweight collaboration. If you create a useful agent or tool, you can share it via gist and someone else using Oneshot can copy and paste it into a new markdown file in the /agents directory or a new python file in the /tools directory.


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


---------


# Oneshot: A Beginner-Friendly Framework for Building AI Agents

## Background

I built Oneshot to give friends and people in our hub network a powerful but approachable way to experiment with AI agents. There's something magical about creating your own specialised AI assistants, and I wanted to make that accessible to everyone - not just experienced developers.

This framework lets you create and orchestrate specialist AI agents without needing to understand complex infrastructure. You write a simple markdown file, and you have a working agent. It's that straightforward.

## Why Oneshot?

### Learn By Building

The best way to understand AI agents is to build them. Oneshot makes this incredibly simple:
1. Create a markdown file
2. Tell the agent what it should do
3. Give it some tools
4. Watch it work

No complex setup, no deep technical knowledge required. Just ideas and experimentation.

### See How Agents Actually Work

Most AI systems are black boxes - you see the magic but not how it works. Oneshot is transparent:
- Watch agents make decisions in real-time
- See exactly which tools they use and why
- Understand the conversation flow
- Debug when things go sideways

Through the Logfire integration, you get a window into the agent's "thought process" - it's both educational and fascinating.

### Build Real, Useful Things

These aren't toy examples. You can create agents that:
- Research topics and write comprehensive reports
- Analyze data and generate insights
- Create content based on your specifications
- Automate repetitive knowledge work
- Whatever you can imagine

### Start Simple, Grow Complex

Begin with a basic agent that does one thing well. As you get comfortable, you can:
- Create teams of specialised agents
- Build custom tools
- Design multi-step workflows
- Connect to external services

The system grows with your skills and ambitions.

## How It Works

### Creating Your First Agent

Here's a complete agent in just a few lines:

```markdown
# agents/research_assistant.md
---
name: research_assistant
description: "Researches topics and creates summaries"
model: openai/gpt-4o-mini
tools: [web_search, save_to_file]
---

You are Research Assistant, focused on finding accurate information
and creating clear, well-structured summaries.

When given a topic, you:
1. Search for relevant information
2. Verify facts from multiple sources
3. Create a comprehensive summary
4. Save it as a clean markdown file
```

That's it. Your agent is ready to use:
```bash
./oneshot research_assistant "Tell me about vertical farming"
```

### The Tool System

Agents become powerful when they can use tools. Oneshot includes tools for:
- Web searching and reading
- File operations
- Data analysis
- Document creation
- Much more

Want a custom tool? Just describe what you need:
> "Create a tool that gets weather forecasts"

The system will build it for you.

### Context Management Made Simple

One innovation in Oneshot is how agents share information. Instead of passing huge blocks of text back and forth (expensive and confusing), agents:
- Create files (artifacts) with their work
- Pass file references to each other
- Keep conversations focused and clear

This means you can chain agents together for complex tasks without things getting messy.

## Getting Started

### Quick Setup (5 minutes)

Create a new Cursor window 

```bash
# Clone the repository
git clone [repo-url]
cd oneshot

# Copy the example environment file
cp .env.example .env

# Add your OpenRouter API key (get one free at openrouter.ai)
# Optionally add a Logfire token for debugging (also free)

# Install dependencies
pip install -r requirements.txt

# Test with an example agent
./oneshot research_agent "What are the latest AI agent frameworks?"
```

### Your First Custom Agent

The easiest way? Just ask Cursor or Claude Code:
> "Create an agent that helps me write blog posts"

They'll read the system documentation and create a working agent instantly.

Or copy one of the examples in `/agents` and modify it for your needs.

## Project Structure

```
oneshot/
├── agents/          # Your AI agents (simple markdown files)
├── tools/           # Python tools agents can use
├── artifacts/       # Files created by agents (reports, analyses, etc.)
├── runs/            # Conversation history
├── snippets/        # Reusable text blocks
└── templates/       # Output templates
```

## Examples to Get You Started

Ask Cusor/Claude Code what agents are available and what they can do then give them a task. Example: ask Cursor to create a report on the latest NRL game involving the Broncos.

### Multi-Agent Workflows
The real power comes from combining agents:
- Research Agent gathers information
- Analyst processes and finds patterns
- Writer creates the final report
- Editor polishes the output

## Key Features for Experimenters

### Self-Documenting System
- The system knows how to explain itself
- It can create new agents for you
- It can troubleshoot problems
- Built-in examples show best practices


### Model Flexibility
Experiment with different AI models:
- GPT-4.1-mini for quick tasks
- Deepseek for reasoning
- Claude for nuanced writing
- Gemini for large documents
- Specialised models for specific needs

All through one simple configuration.

### Complete Visibility
With Logfire integration, you can:
- Watch agents think through problems
- See exact token usage
- Debug issues easily
- Learn how agents make decisions

## Tips for Getting Started

1. **Start with the examples** - Copy and modify existing agents
2. **Keep it simple** - Your first agent should do one thing well
3. **Use the orchestrator** - Let Cursor coordinate multiple agents
4. **Experiment freely** - You can't break anything
5. **Share your creations** - Others can learn from what you build

## Common Questions

**Q: Do I need to know Python?**
A: No! You can create agents with just markdown. If you want custom tools, the system can create them for you.

**Q: What models should I use?**
A: Start with GPT-4o-mini - it's capable and affordable. Experiment with others as you learn.

**Q: Can agents work together?**
A: Yes! That's where the magic happens. Each agent can specialize while working as a team.

**Q: Is this production-ready?**
A: It's perfect for experimentation and personal use. For production, you'd want additional safeguards.

## Next Steps

1. Create your first agent for something you do regularly
2. Watch it work using the debug flag: `--debug`
3. Check the Logfire dashboard to see what happened
4. Iterate and improve
5. Share what you build!

The goal is to demystify AI agents and make them accessible. Every agent you build teaches you something new about what's possible.

Questions? Issues? Cool agents to share? Let me know!

---

Built with Pydantic AI and designed for curious minds 🤖