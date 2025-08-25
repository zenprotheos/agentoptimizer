# Cursor MCP Troubleshooting Guide - Windows 11

> **Purpose**: Resolve hangs, crashes, configuration errors, and performance issues when running Cursor with MCP servers on Windows 11. This is your comprehensive reference for diagnosing and fixing MCP problems.

## Quick Fixes for Common Issues

### 🔴 Red Dot / "No tools or prompts" Error

**Problem**: Server connects but shows red dot indicating no tools available.

**Root Causes & Solutions**:

1. **Wrong Python Environment**
   ```json
   // ❌ Wrong: System Python missing dependencies
   "oneshot": {
     "command": "C:\\Python312\\python.exe"
   }
   
   // ✅ Correct: Project virtual environment
   "oneshot": {
     "command": "C:\\path\\to\\project\\.venv\\Scripts\\python.exe"
   }
   ```

2. **Incorrect uv Command Format**
   ```json
   // ❌ Wrong: Missing 'tool' keyword
   "logfire": {
     "args": ["-m", "uv", "run", "logfire-mcp", "--read-token=..."]
   }
   
   // ✅ Correct: Use 'tool run'
   "logfire": {
     "args": ["-m", "uv", "tool", "run", "logfire-mcp", "--read-token=..."]
   }
   ```

### 🚫 Server Not Appearing (SSE Issues)

**Problem**: SSE servers don't show up in Cursor settings.

**Root Causes & Solutions**:

1. **SSE Format Issues**
   ```json
   // ❌ Wrong: Nested sse object
   "context7": {
     "sse": { "url": "https://mcp.context7.com/sse" }
   }
   
   // ✅ Correct: Direct url property
   "context7": {
     "url": "https://mcp.context7.com/sse"
   }
   ```

2. **Service Unavailable**
   - SSE endpoints only appear when actively running
   - External services may be down
   - Local SSE servers need manual startup

### 🛠️ Specific Server Issues

1. **Browser-Tools Fails to Connect**
   - **Cause**: Missing server or Chrome path
   - **Fix**: Ensure Chrome path in `BROWSER_EXECUTABLE_PATH` matches your installation
   - **Test**: Run server manually to verify it starts

2. **Context7 Not Responding**
   - **Cause**: Wrong URL or firewall blocks SSE
   - **Fix**: Use official hosted SSE: `https://mcp.context7.com/sse`
   - **Corporate Networks**: Allow outbound HTTPS if blocked by firewall

3. **Logfire MCP Doesn't Start**
   - **Cause**: `uv` not found or wrong command format
   - **Fix**: Install uv, ensure command uses `uv tool run` not just `uv run`
   - **Path**: Verify `C:\ProgramData\anaconda3\python.exe` exists

4. **OneShot Red Dot**
   - **Cause**: Wrong Python environment missing `fastmcp`
   - **Fix**: Use project's `.venv\Scripts\python.exe` not system Python
   - **Test**: Verify `fastmcp` is available in the environment

### ⚠️ Configuration Errors

**Problem**: "Server must have either a command or url" error.

**Solution**: Ensure each server has exactly one transport method:
```json
// ✅ stdio transport
"server1": {
  "command": "path/to/executable",
  "args": ["arg1", "arg2"]
}

// ✅ SSE transport  
"server2": {
  "url": "https://example.com/sse"
}

// ❌ Invalid: Missing both
"server3": {
  "env": { "VAR": "value" }
}
```

### 🐌 Windows Stalling Issues

**Problem**: Cursor hangs when starting MCP servers or becomes sluggish.

**Root Causes & Solutions**:

1. **npx Usage (Primary Stall Cause)**:
   ```bash
   # ❌ Avoid: npx causes Windows hanging
   "command": "npx"
   
   # ✅ Solution: Install globally, use absolute paths
   npm install -g puppeteer-mcp-server
   npm install -g @agentdeskai/browser-tools-mcp
   ```

2. **Relative Paths & PATH Dependencies**:
   ```json
   // ❌ Stall Risk: Relies on PATH
   "command": "python"
   
   // ✅ Reliable: Absolute paths
   "command": "C:\\Python312\\python.exe"
   ```

3. **Python Microsoft Store Alias**:
   - **Problem**: `python` opens Microsoft Store instead of running
   - **Fix**: Settings → Apps → App execution aliases → disable Python aliases

4. **stdio Buffer Hangs**:
   - **Problem**: Large MCP output causes Windows buffer hangs
   - **Fix**: Prefer SSE transport when available (Context7, Puppeteer)

5. **Popup Shell Windows**:
   - **Problem**: Cursor spawns PowerShell/cmd windows that close servers when closed
   - **Fix**: Leave shell windows open, or use SSE transport

## Diagnostic Workflow

### Step 1: Check MCP Logs First
1. **Open Cursor → Output → MCP Logs**
   - Look for `Spawning command:` or `Connecting to SSE:` lines
   - Errors here usually point directly to bad paths or missing executables
   - Note any connection failures or dependency errors

### Step 2: Validate Configuration
```powershell
# Test JSON validity
Get-Content "C:\Users\$env:USERNAME\.cursor\mcp.json" | ConvertFrom-Json

# Test individual executable paths
Test-Path "C:\Program Files\nodejs\node.exe"
Test-Path "C:\Python312\python.exe"
Test-Path "C:\Program Files\Google\Chrome Dev\Application\chrome.exe"
```

### Step 3: Manual Server Testing
```powershell
# Test Node.js MCP servers
& "C:\Program Files\nodejs\node.exe" "C:\path\to\server.js"

# Test Python MCP servers (use correct venv)
& "C:\path\to\.venv\Scripts\python.exe" "C:\path\to\server.py"

# Test uv commands
& "C:\ProgramData\anaconda3\python.exe" -m uv tool run logfire-mcp --help
```

### Step 4: Process Cleanup (If Needed)
```powershell
# Kill stray processes if servers hang
Get-Process node -ErrorAction SilentlyContinue | Stop-Process -Force
Get-Process python -ErrorAction SilentlyContinue | Stop-Process -Force
```

## Working Configuration Template

```json
{
  "mcpServers": {
    "puppeteer": {
      "command": "C:\\Program Files\\nodejs\\node.exe",
      "args": ["C:\\Users\\...\\node_modules\\puppeteer-mcp-server\\dist\\index.js"],
      "env": {
        "PUPPETEER_EXECUTABLE_PATH": "C:\\Program Files\\Google\\Chrome Dev\\Application\\chrome.exe"
      }
    },
    "browser-tools": {
      "command": "C:\\Program Files\\nodejs\\node.exe", 
      "args": ["C:\\Users\\...\\node_modules\\@agentdeskai\\browser-tools-mcp\\dist\\mcp-server.js"],
      "env": {
        "BROWSER_EXECUTABLE_PATH": "C:\\Program Files\\Google\\Chrome Dev\\Application\\chrome.exe",
        "BROWSER_TYPE": "chromium",
        "BROWSER_HEADLESS": "true",
        "BROWSER_DEFAULT_TIMEOUT": "30000"
      }
    },
    "context7": {
      "url": "https://mcp.context7.com/sse"
    },
    "logfire": {
      "command": "C:\\ProgramData\\anaconda3\\python.exe",
      "args": ["-m", "uv", "tool", "run", "logfire-mcp", "--read-token=YOUR_TOKEN"]
    },
    "oneshot": {
      "command": "C:\\path\\to\\project\\.venv\\Scripts\\python.exe",
      "args": ["C:\\path\\to\\project\\app\\oneshot_mcp.py"]
    }
  }
}
```

## Best Practices & Principles

### Configuration Best Practices
1. **Keep one global `mcp.json`** only - avoid project-specific configs
2. **Always use absolute paths** - never rely on PATH environment
3. **Avoid npx on Windows** - install globally and reference directly
4. **Use correct Python environments** - project venv, not system Python
5. **Prefer SSE when available** - less Windows shell fragility
6. **Pin absolute paths** for Node, Python, uvx executables
7. **Version pinning** - specify versions (`@1.2.0`) for reproducibility

### Testing Strategy
- **Test configurations incrementally** - add one server at a time
- **Check MCP logs immediately** after any configuration change
- **Focus on stdio servers first** - SSE servers are optional
- **Update dependencies periodically**: `npm install -g npm@latest`

### Windows-Specific Considerations
- Don't mix `npx` and absolute paths in the same config
- Cursor sometimes leaves orphan processes - manual cleanup may be needed
- stdio buffering can occasionally cause hangs under heavy load
- No system-wide override exists inside Cursor; config + scripts are the workaround

## Success Indicators

✅ **All Green Toggles**: Servers connect successfully  
✅ **Tool Counts Shown**: Each server displays "X tools enabled"  
✅ **No Red Dots**: All servers provide their tools  
✅ **No Error Messages**: Clean MCP configuration section  
✅ **Fast Startup**: No hanging or delays when Cursor starts  

## Emergency Recovery

### If Configuration Becomes Completely Broken:

1. **Backup current config**:
   ```powershell
   Copy-Item "C:\Users\$env:USERNAME\.cursor\mcp.json" "mcp.json.backup"
   ```

2. **Start with minimal working config**:
   ```json
   {
     "mcpServers": {
       "browser-tools": {
         "command": "C:\\Program Files\\nodejs\\node.exe",
         "args": ["C:\\Users\\CSJin\\AppData\\Roaming\\npm\\node_modules\\@agentdeskai\\browser-tools-mcp\\dist\\mcp-server.js"],
         "env": {
           "BROWSER_EXECUTABLE_PATH": "C:\\Program Files\\Google\\Chrome Dev\\Application\\chrome.exe"
         }
       }
     }
   }
   ```

3. **Add servers incrementally** until you identify the problematic configuration

### Quick Rescue Commands
```powershell
# Kill all stray Node processes
Get-Process node -ErrorAction SilentlyContinue | Stop-Process -Force

# Kill all stray Python processes  
Get-Process python -ErrorAction SilentlyContinue | Stop-Process -Force

# Reset to backup config
Copy-Item "mcp.json.backup" "C:\Users\$env:USERNAME\.cursor\mcp.json"
```

### Final Notes
Following this troubleshooting guide systematically will give you a stable, repeatable Cursor + MCP setup on Windows 11 with minimal hangs and maximum reliability.
