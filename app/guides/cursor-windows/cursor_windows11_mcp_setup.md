# Core Windows 11 Cursor + MCP Setup Guide

> Purpose: make **MCP servers** work reliably on **Windows 11** in Cursor **and** reduce general Cursor “hangs” when the agent runs commands. This guide consolidates everything into a single global config, prefers SSE when available, and gives repeatable steps.

---

## What this fixes (Windows 11)

* StdIO servers spawning flaky shells (PowerShell/cmd pop‑ups, PATH/npx issues)
* Relative paths breaking when Cursor launches tools headlessly
* Python Store alias hijacking `python`
* Browser MCPs needing Chrome paths and a sidecar server (port 3025)
* Confusion from split configs (global vs project) and hanging when tools don’t start

---

## Prerequisites (install/verify)

**You need these once; Doc 2’s script can auto‑detect and suggest paths.**

* **Node.js LTS** (for Node‑based MCPs)
* **Python 3.x** (for your `oneshot` server)
* **Chrome/Chromium** (for Browser‑Tools / Puppeteer)
* **uvx (uv)** only if you use **Logfire MCP**

Quick checks in PowerShell:

```
where node
python --version   # if this opens Microsoft Store, use absolute python.exe or disable alias
"$env:LOCALAPPDATA\Programs\uv\uvx.exe" -V  # if using Logfire
```

**Disable Python Store alias** (if needed): Settings → Apps → Advanced app settings → App execution aliases → turn off **Python**.

---

## One global config (recommended)

Cursor reads both **global** and **project** configs. For stability, keep **everything** in **global** and remove/empty per‑project files.

* Global: `C:\Users\CSJin\.cursor\mcp.json`
* Project: `<project>\.cursor\mcp.json` (avoid using this unless absolutely required)

---

## Transports: SSE vs StdIO (plain‑English)

* **SSE (Server‑Sent Events)**: Cursor connects to a **URL** (e.g., `http://127.0.0.1:3000/sse`) and listens; no shell quirks. Use when the server offers it.
* **StdIO**: Cursor **spawns a process** (node/python). More moving parts on Windows; use absolute paths to executables to avoid hangs.

```
Before (StdIO): Cursor ──spawns──> powershell/cmd ──runs──> server.js / server.py
After  (SSE) : Cursor ──HTTP──> http://127.0.0.1:PORT/sse (no shell pop‑ups)
```

---

## Your servers and recommended transport

* **Context7** — **SSE (hosted)**: `https://mcp.context7.com/sse`
* **Browser‑Tools (@agentdeskai/browser-tools-mcp)** — **StdIO** (plus a sidecar **browser‑tools‑server** on port 3025)
* **Logfire (logfire-mcp)** — **StdIO** via `uvx`
* **Oneshot (chrisboden/oneshot)** — **StdIO** (your Python script)
* *(Puppeteer MCP)* — if you use it: prefer **SSE** **if the server exposes `/sse`**; otherwise use StdIO with absolute paths

---

## Global `mcp.json` — two ready‑to‑use variants

> Use **Variant A** now (zero path edits). After you run Doc 2’s script, switch to **Variant B** for maximum stability.

### Variant A — Minimal edits (works today)

```json
{
  "mcpServers": {
    "context7": { "sse": { "url": "https://mcp.context7.com/sse" } },

    "browser-tools": {
      "command": "npx",
      "args": ["@agentdeskai/browser-tools-mcp@1.2.0"],
      "env": {
        "BROWSER_TYPE": "chromium",
        "BROWSER_EXECUTABLE_PATH": "C:\\Program Files\\Google\\Chrome Dev\\Application\\chrome.exe",
        "BROWSER_HEADLESS": "true",
        "BROWSER_DEFAULT_TIMEOUT": "30000"
      }
    },

    "logfire": {
      "command": "uvx",
      "args": ["logfire-mcp", "--read-token=<<<YOUR_LOGFIRE_READ_TOKEN>>>"]
    },

    "oneshot": {
      "command": "powershell.exe",
      "args": [
        "-NoProfile","-ExecutionPolicy","Bypass","-Command",
        "& { & 'python' 'C:\\Users\\CSJin\\Jininja Projects\\AI Projects\\main_oneshot\\oneshot\\app\\oneshot_mcp.py' }"
      ]
    }
  }
}
```

**Notes:**

* This keeps **npx/uvx/python** without absolute paths to get you moving. If `python` opens the Store, run Doc 2 and it will rewrite to an absolute `python.exe`.
* For Browser‑Tools you must also run the **sidecar server** (see below).

### Variant B — Stable Windows paths (after running Doc 2 script)

```json
{
  "mcpServers": {
    "context7": { "sse": { "url": "https://mcp.context7.com/sse" } },

    "browser-tools": {
      "command": "C:\\Program Files\\nodejs\\node.exe",
      "args": ["C:\\Tools\\mcp\\browser-tools-mcp\\dist\\index.js"],
      "env": {
        "BROWSER_TYPE": "chromium",
        "BROWSER_EXECUTABLE_PATH": "C:\\Program Files\\Google\\Chrome Dev\\Application\\chrome.exe",
        "BROWSER_HEADLESS": "true",
        "BROWSER_DEFAULT_TIMEOUT": "30000"
      }
    },

    "logfire": {
      "command": "C:\\Users\\CSJin\\AppData\\Local\\Programs\\uv\\uvx.exe",
      "args": ["logfire-mcp", "--read-token=<<<YOUR_LOGFIRE_READ_TOKEN>>>"]
    },

    "oneshot": {
      "command": "powershell.exe",
      "args": [
        "-NoProfile","-ExecutionPolicy","Bypass","-Command",
        "& { & 'C:\\Users\\CSJin\\Jininja Projects\\AI Projects\\main_oneshot\\oneshot\\venv\\Scripts\\python.exe' 'C:\\Users\\CSJin\\Jininja Projects\\AI Projects\\main_oneshot\\oneshot\\app\\oneshot_mcp.py' }"
      ]
    }
  }
}
```

**Notes:**

* Absolute executables end most Windows hangs.
* Keep tokens only in `args` (Cursor may not read `env` for secrets consistently).

---

## Server‑specific steps

### Context7 (SSE)

* No local process needed if you use the hosted endpoint.
* Put the SSE URL in `mcp.json` (as above).

### Browser‑Tools (StdIO + sidecar)

1. Add the MCP server (Variant A or B above).
2. Start the **sidecar** in a separate terminal (required):

```
npx @agentdeskai/browser-tools-server@1.2.0   # listens on port 3025
```

3. Load the BrowserTools Chrome extension (unpacked) and open DevTools on the page you care about.

### Logfire (StdIO)

* Create a **read token** in Logfire.
* Use the `uvx` entry shown above (Variant A or B). Nothing else to run; Cursor spawns it on demand.

### Oneshot (StdIO, Python)

* Create/activate a **venv** for oneshot and install its requirements.
* Use the PowerShell command wrapper shown above; Doc 2 will fill the absolute `python.exe` path.

### Puppeteer (optional)

* If your Puppeteer MCP server exposes `/sse`, prefer an SSE entry.
* If not, use StdIO with absolute `node.exe` and the path to the server’s entry script.

---

## Windows 11 tips that stop hangs

* **Absolute paths** for `node.exe`, `python.exe`, `uvx.exe` (Variant B)
* **ExecutionPolicy**: always spawn via `powershell.exe -ExecutionPolicy Bypass` for Python servers
* **Don’t close** any popup shell windows that Cursor spawns for StdIO servers; closing them kills the tool
* **MCP Logs**: in Cursor, open **Output → MCP Logs** to see exactly what started/failed
* **Firewall**: if you self‑host SSE servers on `127.0.0.1:<port>`, allow those inbound loopback ports if blocked
* **WSL**: if you run servers in WSL, either connect via SSE (URL) or launch with `wsl.exe bash -lc "…"`

---

## Validate the setup (quick checks)

1. Save `C:\Users\CSJin\.cursor\mcp.json` (Variant A first).
2. Launch Cursor → **Output → MCP Logs**. Confirm each server registers.
3. Try a simple tool from each server (e.g., list tools/commands).
4. If something doesn’t start: run the auto‑check script from Doc 2; it will locate executables and suggest the stable Variant B edits.

---

## Ask Cursor to self‑lint the config

Prompt (copy/paste into Cursor Agent):

> “Open `C:\\Users\\CSJin\\.cursor\\mcp.json`. Validate JSON and MCP schema (servers are either `{command,args,env}` or `{sse:{url}}`). Convert any relative paths to absolute Windows paths, replace bare `node`/`python` with absolute paths, prefer SSE where available, and output the corrected JSON plus a short changelog.”

---

### That’s it

This gives you a **Windows‑11‑first**, repeatable, low‑hang setup. Next up, Doc 2 (Automation & Verification) will generate the stable paths for Variant B and sanity‑check SSE endpoints automatically.
