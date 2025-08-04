# Oneshot Setup Guide

This guide will help you get the oneshot agent framework running on your machine.

## Prerequisites

- Python 3.11 or higher
- Git

## Quick Start

1. **Clone the repository:**
   ```bash
   git clone <repository-url>
   cd oneshot
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment variables:**
   ```bash
   cp .env_template .env
   ```
   
   Edit `.env` and add your API keys:
   - **Required:** `OPENROUTER_API_KEY` - Get from [OpenRouter](https://openrouter.ai/keys)
   - **Optional:** Other API keys for additional functionality

4. **Make the oneshot script executable:**
   ```bash
   chmod +x oneshot
   ```

5. **Test the installation:**
   ```bash
   ./oneshot --help
   ```

## MCP Server Setup (for Cursor/Claude)

If you want to use the MCP server with Cursor or other MCP-compatible tools:

1. **Update the MCP configuration:**
   - Edit `.cursor/mcp.json` 
   - The paths should already use `${workspaceFolder}` variables
   - Make sure your `LOGFIRE_READ_TOKEN` is set in your environment if using Logfire

2. **Test the MCP server:**
   ```bash
   python3 app/oneshot_mcp.py --help
   ```

## Usage

Once set up, you can use oneshot to orchestrate AI agents:

```bash
./oneshot research_agent "Research the latest developments in AI"
./oneshot writing_agent "Write a summary of this research" --files research_output.md
```

For more detailed usage instructions, run:
```bash
./oneshot --help
```

## Troubleshooting

- **Import errors:** Make sure you're running from the project root directory
- **API key errors:** Check that your `.env` file has the correct API keys
- **Permission errors:** Make sure the `oneshot` script is executable (`chmod +x oneshot`)

## Directory Structure

- `agents/` - Agent configuration files
- `app/` - Core application code
- `tools/` - Custom tools for agents
- `artifacts/` - Generated outputs
- `config.yaml` - Main configuration file