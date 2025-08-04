# Oneshot: Vibe Code Your Own AI Agent System

Create powerful, specialised AI agents with just markdown files. No complex infrastructure, no deep technical knowledge—just ideas and experimentation.

<div>
    <a href="https://www.loom.com/share/b434737c295c4b2483b375217d051339">
      <p>Creating a News Agent from Scratch - Watch Video</p>
    </a>
    <a href="https://www.loom.com/share/b434737c295c4b2483b375217d051339">
      <img style="max-width:300px;" src="https://cdn.loom.com/sessions/thumbnails/b434737c295c4b2483b375217d051339-12a0ff783b72514f-full-play.gif">
    </a>
</div>

## Quick Start

### Setup (2 minutes)
1. Clone this repo in Cursor: `https://github.com/chrisboden/oneshot`
2. Rename `.env_example` to `.env`
3. Add your [OpenRouter API key](https://openrouter.ai/keys)

### Your First Agent

Simply ask your AI assistant (Cursor/Claude) to delegate tasks to one of the example agents provided:

**"Research the latest developments in vertical farming"** → Your assistant will use the research_agent

**"Describe this screenshot in detail (provide filepath)"** → Your assistant will use the vision_agent  

**"Create a match report for the latest Broncos game"** → Your assistant will use the nrl_agent

**"Create an agent that summarises YouTube videos"** → Your assistant will build a custom agent for you


## Create your own agents

Write a markdown file, get a working agent:

```markdown
# agents/my_agent.md
---
name: content_creator
model: openai/gpt-4o-mini
tools: 
  - web_search
  - save_to_file
  - etc
---

You create engaging blog posts about tech trends.
Research the topic thoroughly, then write in a conversational tone.
```

That's it. Your agent is ready.

## Why Oneshot?

### Transparent AI
Most AI systems are black boxes. Oneshot shows you everything:
- Watch agents make decisions in real-time
- See exactly which tools they use and why
- Debug when things go sideways
- Learn by observing the "thought process"

### Cost-Effective
Use Cursor on Auto mode **for free** to orchestrate your agents, while running specialist work on cheaper models. Save your expensive Claude/GPT-4 tokens for high-value coding tasks.

### Learn by Building
The best way to understand AI agents is to build them. Start simple, grow complex:
- Basic agents → multi-agent workflows
- Built-in tools → custom integrations
- Single tasks → complex automation

### Novel Context Management
Agents create and pass files (artifacts) instead of cramming everything into chat. This keeps conversations focused and enables clean agent-to-agent collaboration without context window chaos.

## Key Features

### Self-Describing System
Oneshot teaches Cursor and Claude Code how to work with it. They can:
- Create new agents for you
- Build custom tools on demand
- Troubleshoot problems
- Extend the system intelligently

### Model Flexibility
Access hundreds of models through OpenRouter:
- **GPT-4o-mini**: Reliable workhorse for most tasks
- **Gemini-2.0-flash**: Fast and capable for general work
- **DeepSeek-R1**: Advanced reasoning for complex problems
- **Claude-3.5-Sonnet**: Nuanced writing and analysis
- Plus many specialized models

### MCP Integration
- **Use as MCP Server**: Other agents can call Oneshot agents
- **Use MCP Clients**: Agents can call your existing MCP servers
- **Build MCP Servers**: System creates new integrations on demand

### Complete Visibility
With Logfire integration:
- Real-time agent decision tracking
- Token usage monitoring
- Performance optimization insights
- Educational debugging experience

## Project Structure

```
oneshot/
├── agents/          # AI agents (markdown files)
├── tools/           # Python tools agents can use
├── artifacts/       # Agent-generated files
├── runs/            # Conversation histories
├── templates/       # Output templates
└── snippets/        # Reusable text blocks
```

## Advanced Patterns

### Multi-Agent Workflows
Chain specialists for complex tasks:
```
Research Agent → Data Analyst → Report Writer → Editor
```

Each agent focuses on what it does best, passing clean artifacts forward.

### Artifact-First Design
Unlike code-focused tools, Oneshot creates knowledge work artifacts:
- Reports in your company template
- Emails in your voice
- Presentations with your branding
- Analysis with your methodology

### Lightweight Collaboration
Share agents and tools via simple file sharing. Copy-paste a markdown file, and someone else has your agent working in their system.

## Examples in Action

**Research Pipeline**
```bash
# Deep research with citations
./oneshot research_agent "Competitive landscape for AI coding tools"

# Generate executive summary
./oneshot summary_agent "Summarize research_output.md for C-suite audience"
```

**Content Creation**
```bash
# Create blog post
./oneshot content_creator "Write about the future of remote work"

# Generate social media variants  
./oneshot social_agent "Create LinkedIn and Twitter versions of blog_post.md"
```

**Data Analysis**
```bash
# Process dataset
./oneshot data_analyst "Analyze trends in sales_data.csv"

# Create presentation
./oneshot presenter "Turn analysis into executive slides"
```

## Built on Proven Stack

- **PydanticAI**: LLM integration and context management
- **OpenRouter**: Access to 200+ models through unified API
- **Logfire**: Real-time observability and debugging
- **MCP Protocol**: Interoperability with other AI tools

## Philosophy

Oneshot was built for the Peregian Digital Hub community—a place where people experiment with emerging technologies. The core principles:

1. **Accessibility**: You shouldn't need a CS degree to build useful AI
2. **Transparency**: See how agents actually work, don't just use them
3. **Experimentation**: Fast iteration cycles, low barrier to trying new ideas
4. **Collaboration**: Easy sharing of agents and tools
5. **Practical Value**: Build things that solve real problems

The name "oneshot" reflects the goal: AI that gets it right the first time. While we're not there yet, the system includes extensive prompting and context management designed to help Cursor and Claude Code work with it effectively—often succeeding in one attempt.

## Getting Deeper

### Creating Custom Tools
Need something specific? Describe it to Cursor:
> "Create a tool that extracts data from PDFs and formats it as structured JSON"

The system will build it, often in one shot.

### Advanced Agent Design
Study the included examples to learn patterns:
- **Vision Agent**: Image analysis workflows
- **Research Agent**: Multi-source fact-checking
- **NRL Agent**: Structured report generation

### Context Engineering
Learn how different prompt patterns affect agent behavior. The system exposes everything, making it an excellent learning environment.

### MCP Server Development
Build integrations with your existing tools and services. The system can generate MCP servers from API documentation.

## Community

This isn't just an open source project—it's a learning environment. Built for people who want to understand AI agents by building them, not just using them.

Share your agents, tools, and discoveries. Every experiment teaches us something new about what's possible when AI becomes truly accessible.

---

Ready to build your first agent? Start with the examples, then let your imagination run wild.