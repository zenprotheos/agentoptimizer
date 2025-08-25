# Automation & Verification (PowerShell Script Guide)

> Purpose: automate the **checking, verifying, and identifying** of everything Cursor needs on **Windows 11**. This script inspects your environment, validates your `mcp.json`, and outputs clear warnings/fixes. It eliminates manual path editing (except for API keys).

---

## What this script does

* Detects installed runtimes: Node.js, Python, Chrome/Chromium, `uvx` (Logfire)
* Reads your global config `C:\Users\CSJin\.cursor\mcp.json`
* For **StdIO servers**: checks that the executable paths exist (or if they’re relative)
* For **SSE servers**: probes the endpoint and validates it returns `text/event-stream`
* Flags risky patterns: bare `python` (Store alias), `node` without absolute path, missing Chrome path
* Suggests stable rewrites (Variant B from Doc 1)

---

## The PowerShell Script

Save as `Check-Cursor-MCP.ps1` and run in a normal PowerShell terminal (no admin required).

```powershell
# === Cursor MCP Auto-Check Script ===
$McpPath = "C:\\Users\\CSJin\\.cursor\\mcp.json"

$NodeCandidates = @(
  "C:\\Program Files\\nodejs\\node.exe",
  "$env:LOCALAPPDATA\\Programs\\nodejs\\node.exe"
)
$PythonCandidates = @(
  "C:\\Python312\\python.exe",
  "$env:LOCALAPPDATA\\Programs\\Python\\Python312\\python.exe"
)
$ChromeCandidates = @(
  "C:\\Program Files\\Google\\Chrome Dev\\Application\\chrome.exe",
  "C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe",
  "$env:LOCALAPPDATA\\Google\\Chrome\\Application\\chrome.exe"
)
$UvxCandidates = @(
  "$env:LOCALAPPDATA\\Programs\\uv\\uvx.exe",
  "C:\\Program Files\\uv\\uvx.exe"
)

function Test-FirstExisting([string[]]$paths) {
  foreach ($p in $paths) { if (Test-Path $p) { return $p } }
  return $null
}

$nodeExe   = Test-FirstExisting $NodeCandidates
$pythonExe = Test-FirstExisting $PythonCandidates
$chromeExe = Test-FirstExisting $ChromeCandidates
$uvxExe    = Test-FirstExisting $UvxCandidates

Write-Host "=== Runtime discovery ==="
Write-Host ("Node:   " + ($nodeExe   ?? "NOT FOUND"))
Write-Host ("Python: " + ($pythonExe ?? "NOT FOUND"))
Write-Host ("Chrome: " + ($chromeExe ?? "NOT FOUND"))
Write-Host ("uvx:    " + ($uvxExe    ?? "NOT FOUND"))
Write-Host ""

if (!(Test-Path $McpPath)) {
  Write-Warning "Cannot find $McpPath"
  exit 1
}

try {
  $json = Get-Content $McpPath -Raw | ConvertFrom-Json -ErrorAction Stop
} catch {
  Write-Error "Invalid JSON in $McpPath: $($_.Exception.Message)"
  exit 1
}

if (!$json.mcpServers) {
  Write-Host "No mcpServers defined in $McpPath."
  exit 0
}

Write-Host "=== MCP server checks ==="
foreach ($name in $json.mcpServers.PSObject.Properties.Name) {
  $srv = $json.mcpServers.$name
  Write-Host "`n[$name]"
  if ($srv.sse -and $srv.sse.url) {
    $url = $srv.sse.url
    Write-Host "  Transport: SSE -> $url"
    try {
      $resp = Invoke-WebRequest -Uri $url -Method GET -Headers @{Accept="text/event-stream"} -UseBasicParsing -TimeoutSec 5
      $ct = $resp.Headers["Content-Type"]
      if ($ct -and $ct -like "*text/event-stream*") {
        Write-Host "  OK: SSE endpoint responded with Content-Type: $ct"
      } else {
        Write-Warning "  WARN: Endpoint responded but not as text/event-stream (Content-Type: $ct)"
      }
    } catch {
      Write-Warning "  FAIL: Could not connect to SSE endpoint: $($_.Exception.Message)"
    }
  } elseif ($srv.command) {
    $cmd = $srv.command
    $args = ($srv.args -join " ")
    Write-Host "  Transport: stdio -> $cmd $args"
    if ($cmd -match "^(node|node.exe)$" -and -not $cmd -match ":\\") {
      Write-Warning "  HINT: Use absolute path to node.exe for stability on Windows."
      if ($nodeExe) { Write-Host "        Suggested: $nodeExe" }
    }
    if ($cmd -match "^(python|python.exe)$" -and -not $cmd -match ":\\") {
      Write-Warning "  HINT: Use absolute path to python.exe to avoid Store alias issues."
      if ($pythonExe) { Write-Host "        Suggested: $pythonExe" }
    }
    if ($srv.env) {
      foreach ($k in $srv.env.PSObject.Properties.Name) {
        $v = $srv.env.$k
        if ($k -match "EXECUTABLE_PATH" -and $v -and -not (Test-Path $v)) {
          Write-Warning "  WARN: $k points to missing path: $v"
        }
      }
    }
    if ($cmd -match ":\\" -and -not (Test-Path $cmd)) {
      Write-Warning "  WARN: command path does not exist: $cmd"
    }
  } else {
    Write-Warning "  Unknown server shape (no sse.url and no command)."
  }
}

Write-Host "`n=== Summary ==="
if (!$nodeExe)   { Write-Host "Install Node.js LTS (Windows) and note the path to node.exe" }
if (!$pythonExe) { Write-Host "Install Python 3.x and use absolute path to python.exe (avoid Store alias)" }
if (!$chromeExe) { Write-Host "Install Chrome/Chromium (needed by Puppeteer/BrowserTools) or update EXECUTABLE_PATH" }
if (!$uvxExe)    { Write-Host "Install uv (for Logfire MCP) so uvx.exe is available" }
Write-Host "Check Cursor → Output → MCP Logs after fixes."
```

---

## How to run

1. Save script as `Check-Cursor-MCP.ps1`
2. Right‑click → “Run with PowerShell”
3. Or in a terminal: `powershell -ExecutionPolicy Bypass -File .\Check-Cursor-MCP.ps1`
4. Read the output:

   * **OK** → server ready
   * **WARN/FAIL/HINT** → adjust `mcp.json` or install missing runtime

---

## Next step

After running this:

* If all is **OK**, switch your config to **Variant B (absolute paths)** from Doc 1.
* If warnings appear, copy the “Suggested” absolute paths into `mcp.json`.
* Run Cursor → **Output → MCP Logs** to confirm.

Doc 3 will cover **Troubleshooting & Best Practices** (handling hangs, common errors, debugging logs).
