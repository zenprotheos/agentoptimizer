---
name: "How to Setup"
purpose: "Read this step-by-step setup guide for helping a user get the oneshot system running with dependencies, environment configuration, API keys, and MCP server setup"
---

Your job is to help get the user setup with as little pain as possible.

# Step 1: Install dependencies

(The Cursor Agent should do this step for the user.)

```bash
   pip install -r requirements.txt
```

# Step 2: Set up your environment file

(The Cursor Agent should do this step for the user)

Find the .env_example file and rename it to .env
You will then need to add your keys for openrouter and logfire


# Step 3: Get your Openrouter key

(The user will need to do this)

Openrouter is a platform that offers a single API for accessing hundreds of Ai models from a single account. You will need an openrouter key to be able to use the AI models for this project.

1. If you don't already have a key, go to openrouter.ai and create an account. Put down some credit and get a key. 
2. Open the .env file and paste in the key

# Step 4: Get your logfire keys

(The user will need to do this)

Logfire is platform for saving and viewing logs and diagnostics for Python applications like oneshot. You need a free logfire account because this project sends logs there and the agent then uses those logs when it needs to sole problems or debug issues for you. Another prupose of the logfire integration is that it is a fantastic way of seeing an xray view of how an agent system works, with all of the tool calls, llm api calls etc.

1. Go to https://logfire.pydantic.dev/ and create a free account
2. Create a new project. you can call is `oneshot`. Then go to the settings for that project. On the left hand side of the settings screen you'll see "Write Tokens" and "Read Tokens". you will need to create one of each.

You can show/see a screenshot of this at app/guides/images/logfire_settings.jpg

3. Copy and paste the Write token you just created to the .env file where you see LOGFIRE_WRITE_TOKEN=
Paste it after the equals sign
1. Copy and paste the Read token you just created to the .env file where you see LOGFIRE_READ_TOKEN=
Paste it after the equals sign


## Step 5: Set up the MCP Servers

(The Cursor Agent should do this step for the user)

1. Look in the .cursor folder and find mcp_example.json. Rename it to mcp.json and open the file
2. The You Agent should see mcp server config details for the context7, logfire and the oneshot system.
3. Add the logfire READ token from the previous step to the part of the logfire mcp server config where it says PASTE_YOUR_LOGFIRE_READ_TOKEN_HERE

# Switch on MCP Servers

(The human will need to do this step)

1. Go to Cursor > Settings > Cursor Settings > Tools & Integrations
2. . Toggle on the following MCP Servers:
- Logfire
- Context 7
- oneshot
3. The You Agent should now see a green dot icon next to each server to show that they are configured and working
4. Ask cursor if it can see the logfire, context7 and oneshot mcp servers. If it says yes, then you are ready to roll

You can show/see a screenshot of this at app/guides/images/mcp_settings.jpg

# Run a test

Run the setup test to see if everything is working 
```python
python3 app/tests/test_system.py
```

We would like to see:

✅ PASS: Valid Agent Configuration
✅ PASS: Tool Functionality
✅ PASS: File Processing
✅ PASS: Template Includes
✅ PASS: Error Handling
✅ PASS: MCP Server Integration

Overall: 6/6 tests passed


# Get started

You can now start experimenting with agents and tools. You can now ask Cursor to start creating agents and tools for you.

