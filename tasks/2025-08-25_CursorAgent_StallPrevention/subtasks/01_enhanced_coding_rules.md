---
title: "Enhanced Coding Rules - Anti-Stall Protocols"
date: "2025-08-25T10:15:48.914Z"
parent_task: "CursorAgent_StallPrevention"
priority: "Critical"
status: "In Progress"
assigned: ""
estimated_effort: "2-3 hours"
tags: ["coding-rules", "anti-stall", "timeout", "auto-recovery"]
---

# Enhanced Coding Rules - Anti-Stall Protocols

## Overview
Define mandatory anti-stall protocols to be added to `coding-tasks.mdc` to eliminate manual Ctrl+Enter intervention requirements.

## Problem Statement
Current coding rules lack comprehensive anti-stall mechanisms, resulting in:
- Manual intervention required when commands hang
- Inconsistent timeout handling across different command types
- No automatic recovery mechanisms
- Poor user experience with frequent stalls

## Enhanced Rule Additions

### 1. MANDATORY COMMAND TIMEOUT PROTOCOL

#### Rule: ALL Commands Must Have Timeouts
```markdown
#### 🚨 MANDATORY COMMAND TIMEOUT PROTOCOL 🚨

**CRITICAL**: ALL command executions MUST include timeout protection to prevent stalls requiring manual intervention.

**Command Timeout Requirements by Type:**
- **Simple Commands** (file ops, basic tools): 30 seconds maximum
- **MCP Operations** (agent calls, tool execution): 60 seconds maximum  
- **Heavy Operations** (builds, downloads, processing): 90 seconds maximum
- **Network Operations** (API calls, web requests): 45 seconds maximum
- **Interactive Commands**: FORBIDDEN - use non-interactive alternatives

**Implementation Templates:**

**PowerShell Job Pattern (Recommended):**
```powershell
$job = Start-Job -ScriptBlock { <YOUR_COMMAND> }
if (Wait-Job $job -Timeout <TIMEOUT_SECONDS>) {
    $result = Receive-Job $job
    Remove-Job $job
    return $result
} else {
    Stop-Job $job -Force
    Remove-Job $job
    Write-Host "⚠️ Command timed out after <TIMEOUT_SECONDS>s - continuing automatically"
    # Continue execution - no manual intervention required
}
```

**Process Timeout Pattern:**
```powershell
$psi = New-Object System.Diagnostics.ProcessStartInfo
$psi.FileName = '<EXECUTABLE>'
$psi.Arguments = '<ARGS>'
$psi.UseShellExecute = $false
$psi.RedirectStandardOutput = $true
$psi.RedirectStandardError = $true
$p = [System.Diagnostics.Process]::Start($psi)
if (!$p.WaitForExit(<TIMEOUT_MILLISECONDS>)) {
    $p.Kill()
    Write-Host "⚠️ Process timeout - auto-recovery triggered"
    # Continue execution
} else {
    $output = $p.StandardOutput.ReadToEnd()
}
```

**Background Execution Pattern:**
```powershell
# For non-critical or long-running commands
Start-Process -NoNewWindow -PassThru '<COMMAND>' 
# Monitor and timeout if needed, but don't block main execution
```
```

### 2. AUTO-RECOVERY MECHANISMS

```markdown
#### 🔄 AUTOMATIC RECOVERY PROTOCOLS

**MANDATORY**: When commands timeout or stall, agents MUST automatically recover without human intervention.

**Recovery Actions Hierarchy:**
1. **Graceful Termination**: Send SIGTERM, wait 5 seconds
2. **Force Termination**: Send SIGKILL/Process.Kill()
3. **Context Preservation**: Maintain execution state
4. **Continuation Logic**: Resume task execution automatically
5. **Error Logging**: Log timeout event without stopping workflow

**Auto-Recovery Template:**
```powershell
function Invoke-CommandWithAutoRecovery {
    param([string]$Command, [int]$TimeoutSec = 30)
    
    try {
        $job = Start-Job -ScriptBlock { Invoke-Expression $using:Command }
        if (Wait-Job $job -Timeout $TimeoutSec) {
            $result = Receive-Job $job
            Remove-Job $job
            return $result
        } else {
            # AUTO-RECOVERY: Simulate Ctrl+Enter
            Stop-Job $job -Force
            Remove-Job $job
            Write-Host "🔄 Auto-recovery: Command timeout, continuing execution..."
            return "TIMEOUT_RECOVERED"
        }
    } catch {
        Write-Host "🔄 Auto-recovery: Error occurred, continuing execution..."
        return "ERROR_RECOVERED"
    }
}
```
```

### 3. ENHANCED RUN_TERMINAL_CMD REQUIREMENTS

```markdown
#### 🛡️ ENHANCED TERMINAL COMMAND EXECUTION

**MANDATORY**: All `run_terminal_cmd` calls MUST include anti-stall protection.

**Required Parameters:**
- `timeout`: Maximum execution time (default: 30s)
- `auto_recover`: Enable automatic recovery (default: true)
- `kill_on_timeout`: Force termination on timeout (default: true)
- `background`: Run in background for non-critical ops (default: false)

**Enhanced Usage Pattern:**
```python
# CORRECT: With anti-stall protection
run_terminal_cmd(
    command="your-command",
    timeout=30,  # Mandatory timeout
    auto_recover=True,  # Enable auto-recovery
    explanation="Running command with timeout protection"
)

# WRONG: No timeout protection (FORBIDDEN)
run_terminal_cmd(
    command="your-command",
    explanation="Command without timeout"  # ❌ Missing timeout
)
```

**Implementation Requirements:**
- Commands MUST NOT hang indefinitely
- Timeouts MUST be enforced at multiple layers
- Auto-recovery MUST be triggered on timeout
- Manual intervention MUST NEVER be required
- Execution MUST continue after timeout events
```

### 4. STALL DETECTION AND PREVENTION

```markdown
#### 🔍 STALL DETECTION AND PREVENTION

**Proactive Stall Prevention:**
- **Command Analysis**: Pre-screen commands for stall risk patterns
- **Resource Monitoring**: Monitor CPU, memory, I/O during execution
- **Progress Tracking**: Detect commands with no output/progress
- **Pattern Recognition**: Identify known problematic command signatures

**High-Risk Command Patterns (Require Extra Protection):**
- Interactive commands waiting for input
- Network operations without explicit timeouts
- Large file operations without progress indicators
- Subprocess calls without timeout controls
- Commands with complex PowerShell escaping

**Prevention Strategies:**
```powershell
# 1. Pre-flight Command Validation
function Test-CommandStallRisk {
    param([string]$Command)
    $riskPatterns = @(
        "Read-Host",           # Interactive input
        "pause",               # Waiting for keypress
        "Invoke-WebRequest",   # Network without timeout
        "Start-Process.*-Wait" # Blocking process waits
    )
    foreach ($pattern in $riskPatterns) {
        if ($Command -match $pattern) {
            return $true  # High stall risk
        }
    }
    return $false
}

# 2. Safe Command Alternatives
# Replace: Read-Host with default values
# Replace: Invoke-WebRequest with timeout
# Replace: interactive commands with non-interactive variants
```
```

### 5. COMPREHENSIVE ERROR HANDLING

```markdown
#### ⚡ COMPREHENSIVE ERROR HANDLING WITH AUTO-CONTINUE

**Error Recovery Protocol:**
```powershell
function Invoke-ResilientCommand {
    param([string]$Command, [int]$MaxRetries = 3, [int]$TimeoutSec = 30)
    
    for ($attempt = 1; $attempt -le $MaxRetries; $attempt++) {
        try {
            $result = Invoke-CommandWithAutoRecovery -Command $Command -TimeoutSec $TimeoutSec
            if ($result -ne "TIMEOUT_RECOVERED" -and $result -ne "ERROR_RECOVERED") {
                return $result  # Success
            }
            
            # Auto-recovery occurred, try alternative or continue
            if ($attempt -lt $MaxRetries) {
                Write-Host "🔄 Attempt $attempt failed, retrying with exponential backoff..."
                Start-Sleep -Seconds ([math]::Pow(2, $attempt))
            }
        } catch {
            Write-Host "🔄 Exception in attempt $attempt, auto-recovering..."
            if ($attempt -eq $MaxRetries) {
                Write-Host "🔄 Max retries reached, continuing with graceful degradation"
                return "GRACEFUL_FAILURE"
            }
        }
    }
}
```

**Graceful Degradation:**
- Non-critical command failures MUST NOT stop task execution
- Alternative approaches MUST be attempted automatically
- Task progress MUST continue despite individual command failures
- User notification MUST occur without requiring intervention
```

## Implementation Checklist

### Phase 1: Rule Integration
- [ ] Add mandatory timeout protocols to coding-tasks.mdc
- [ ] Include auto-recovery mechanisms in standard patterns
- [ ] Define enhanced run_terminal_cmd requirements
- [ ] Add stall detection and prevention guidelines

### Phase 2: Template Creation
- [ ] Create PowerShell job timeout templates
- [ ] Design process timeout templates  
- [ ] Build auto-recovery function templates
- [ ] Develop error handling patterns

### Phase 3: Validation
- [ ] Test timeout enforcement across command types
- [ ] Validate auto-recovery mechanisms
- [ ] Verify graceful degradation behavior
- [ ] Ensure backward compatibility

### Phase 4: Documentation
- [ ] Update coding-tasks.mdc with complete protocols
- [ ] Create usage examples and best practices
- [ ] Document common stall patterns and solutions
- [ ] Provide troubleshooting guides

## Integration with Existing Rules

### Compatibility Requirements
- [ ] Maintain existing Windows PowerShell execution patterns
- [ ] Preserve temp file management protocols ([[memory:7091255]])
- [ ] Keep test location requirements ([[memory:7091258]])
- [ ] Integrate with progress tracking requirements ([[memory:7088653]])

### Enhancement Areas
- [ ] Extend existing timeout mechanisms in cursor-windows-rule.mdc
- [ ] Enhance error handling beyond current patterns
- [ ] Add proactive stall prevention to reactive timeout handling
- [ ] Improve user experience with automatic recovery

## Success Criteria

### Primary Objectives
- [ ] **Zero Manual Intervention**: No Ctrl+Enter required for any command
- [ ] **Universal Timeout Coverage**: ALL commands have timeout protection
- [ ] **Automatic Recovery**: 100% auto-recovery from timeout events
- [ ] **Seamless Integration**: No disruption to existing workflows

### Performance Targets
- [ ] **Command Completion Rate**: > 95% within timeout limits
- [ ] **Auto-Recovery Success**: > 98% successful recovery events
- [ ] **False Positive Rate**: < 1% unnecessary timeouts
- [ ] **User Experience**: Zero frustration from manual intervention

---

*This subtask will be marked complete when all enhanced protocols are successfully integrated into coding-tasks.mdc and validated through testing.*
