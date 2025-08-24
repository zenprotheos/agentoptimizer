---
title: "OneShot Windows Compatibility - Implementation Plan"
date: "2025-08-24"
task: "OneShot Windows Compatibility"
status: "In Progress"
priority: "High"
tags: ["implementation", "planning", "windows", "compatibility"]
---

# OneShot Windows Compatibility - Implementation Plan

## Executive Summary

This document outlines the comprehensive implementation plan for making the OneShot MCP system fully compatible with Windows 11, addressing the Mac-centric design patterns identified in the original GitHub repository.

## Implementation Phases

### Phase 1: Core Infrastructure (Critical Priority)
**Timeline: Week 1-2**

#### 1.1 Path Handling Standardization
- **Target Files**: All Python modules with file/path operations
- **Implementation**:
  ```python
  # Replace Unix-specific paths with pathlib
  from pathlib import Path, PurePath
  import os
  
  # Windows-safe path operations
  def normalize_path(path_str: str) -> Path:
      """Convert any path format to Windows-compatible Path object"""
      return Path(path_str).resolve()
  ```

#### 1.2 Process Execution Wrapper
- **Target Files**: `tool_services.py`, `agent_executor.py`
- **Implementation**:
  ```python
  # Windows subprocess wrapper
  import subprocess
  import sys
  
  def safe_subprocess_run(cmd, **kwargs):
      """Windows-safe subprocess execution"""
      if sys.platform == "win32":
          # Windows-specific handling
          kwargs.setdefault('shell', True)
          kwargs.setdefault('creationflags', subprocess.CREATE_NO_WINDOW)
      return subprocess.run(cmd, **kwargs)
  ```

#### 1.3 Environment Detection
- **New Module**: `platform_utils.py`
- **Purpose**: Centralized platform detection and configuration

### Phase 2: Agent System Compatibility (High Priority)
**Timeline: Week 2-3**

#### 2.1 Agent Configuration Updates
- **Target Files**: `agent_config.py`, `agent_validation.py`
- **Changes**:
  - Windows path validation for agent definitions
  - Tool path resolution for Windows environments
  - Environment variable handling

#### 2.2 Tool Services Refactoring
- **Target Files**: All files in `/tools/` directory
- **Focus Areas**:
  - Web search tools (browser path handling)
  - File operation tools (Windows file handling)
  - Export tools (Windows executable paths)

### Phase 3: MCP Server Optimization (Medium Priority)
**Timeline: Week 3-4**

#### 3.1 MCP Communication Layer
- **Target Files**: `oneshot_mcp.py`, `mcp_config.py`
- **Enhancements**:
  - Windows-optimized MCP transport (SSE vs stdio)
  - Error handling for Windows-specific MCP issues
  - Configuration validation for Windows paths

#### 3.2 Logging and Monitoring
- **Target Files**: All modules with logging
- **Implementation**:
  - Windows-compatible log file paths
  - Logfire integration testing on Windows
  - Performance monitoring for Windows-specific bottlenecks

### Phase 4: Testing and Validation (Ongoing)
**Timeline: Throughout all phases**

#### 4.1 Automated Testing Suite
- **New Directory**: `/tests/windows_compatibility/`
- **Test Categories**:
  - Path handling tests
  - Process execution tests
  - MCP communication tests
  - Agent execution tests

## Detailed Implementation Strategy

### File-by-File Analysis and Modifications

#### Core System Files

1. **`app/oneshot_mcp.py`**
   - Issue: MCP server initialization and transport handling
   - Solution: Implement Windows-specific MCP server configuration
   - Priority: Critical

2. **`app/agent_runner.py`**
   - Issue: Agent execution and subprocess management
   - Solution: Windows subprocess wrapper implementation
   - Priority: Critical

3. **`app/tool_services.py`**
   - Issue: Tool discovery and execution
   - Solution: Windows executable path resolution
   - Priority: High

4. **`app/agent_config.py`**
   - Issue: Configuration file path handling
   - Solution: Pathlib integration for cross-platform paths
   - Priority: High

#### Tool Files Requiring Updates

1. **`tools/web_search.py`**
   - Issue: Browser executable paths
   - Solution: Windows Chrome/Edge path detection
   - Priority: Medium

2. **`tools/export_as_pdf.py`**
   - Issue: External tool dependencies
   - Solution: Windows PDF generation tool paths
   - Priority: Medium

3. **`tools/file_creator.py`**
   - Issue: File permission and path handling
   - Solution: Windows file operation wrapper
   - Priority: High

### Configuration Changes

#### 1. Windows-Specific Configuration Template
```yaml
# config_windows.yaml
platform:
  type: "windows"
  shell: "powershell"
  
paths:
  temp_dir: "${TEMP}"
  user_dir: "${USERPROFILE}"
  
executables:
  python: "C:\\Python312\\python.exe"
  node: "C:\\Program Files\\nodejs\\node.exe"
  chrome: "C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe"
```

#### 2. MCP Configuration Updates
```json
{
  "mcpServers": {
    "oneshot": {
      "command": "powershell.exe",
      "args": [
        "-NoProfile", "-ExecutionPolicy", "Bypass", "-Command",
        "& { & 'C:\\path\\to\\python.exe' 'C:\\path\\to\\oneshot_mcp.py' }"
      ]
    }
  }
}
```

### Error Handling Strategy

#### Windows-Specific Error Cases
1. **Path Resolution Errors**
   - Long path names (>260 characters)
   - Reserved file names (CON, PRN, AUX, etc.)
   - Case sensitivity differences

2. **Permission Errors**
   - UAC restrictions
   - Antivirus interference
   - File locking issues

3. **Process Execution Errors**
   - PowerShell execution policy
   - Environment variable differences
   - Shell command syntax variations

### Testing Strategy

#### Unit Tests
```python
# tests/windows_compatibility/test_path_handling.py
import unittest
from pathlib import Path
from app.platform_utils import normalize_path

class TestWindowsPathHandling(unittest.TestCase):
    def test_unix_to_windows_path_conversion(self):
        unix_path = "/Users/user/documents/file.txt"
        windows_path = normalize_path(unix_path)
        self.assertIsInstance(windows_path, Path)
    
    def test_long_path_handling(self):
        long_path = "C:\\" + "a" * 300 + "\\file.txt"
        result = normalize_path(long_path)
        self.assertTrue(result.is_absolute())
```

#### Integration Tests
```python
# tests/windows_compatibility/test_mcp_integration.py
import unittest
from app.oneshot_mcp import MCPServer

class TestWindowsMCPIntegration(unittest.TestCase):
    def test_mcp_server_startup_windows(self):
        server = MCPServer()
        self.assertTrue(server.start())
    
    def test_agent_execution_windows(self):
        # Test agent execution on Windows
        pass
```

## Risk Assessment and Mitigation

### High-Risk Areas
1. **MCP Transport Layer**
   - Risk: stdio transport instability on Windows
   - Mitigation: Implement SSE transport preference
   - Fallback: Robust stdio implementation with timeouts

2. **Subprocess Execution**
   - Risk: Shell command failures
   - Mitigation: PowerShell-specific command formatting
   - Fallback: Alternative execution methods

3. **File Path Handling**
   - Risk: Path resolution failures
   - Mitigation: Comprehensive pathlib usage
   - Fallback: Manual path normalization

### Medium-Risk Areas
1. **External Tool Dependencies**
   - Risk: Tool availability on Windows
   - Mitigation: Alternative tool discovery
   - Fallback: Graceful degradation

2. **Environment Variables**
   - Risk: Variable name/format differences
   - Mitigation: Platform-specific variable mapping
   - Fallback: Default value provision

## Success Metrics

### Functional Requirements
- [ ] All MCP tools function correctly on Windows 11
- [ ] Agent execution completes without path-related errors
- [ ] File operations work with Windows file system
- [ ] External tool integration functions properly

### Performance Requirements
- [ ] MCP server startup time < 5 seconds on Windows
- [ ] Agent execution time comparable to Mac performance
- [ ] Memory usage within acceptable limits
- [ ] No resource leaks in long-running sessions

### Reliability Requirements
- [ ] 99% success rate for basic operations
- [ ] Graceful error handling for Windows-specific issues
- [ ] Automatic recovery from transient failures
- [ ] Comprehensive logging for troubleshooting

## Timeline and Milestones

### Week 1
- [ ] Complete core infrastructure changes
- [ ] Implement path handling standardization
- [ ] Create Windows testing environment

### Week 2
- [ ] Refactor agent system for Windows compatibility
- [ ] Update tool services for Windows paths
- [ ] Begin integration testing

### Week 3
- [ ] Optimize MCP server for Windows
- [ ] Complete tool updates
- [ ] Comprehensive testing phase

### Week 4
- [ ] Final validation and bug fixes
- [ ] Documentation updates
- [ ] Release preparation

## Dependencies and Prerequisites

### Software Requirements
- Windows 11 (primary target)
- Python 3.8+ with pathlib support
- PowerShell 5.1 or PowerShell Core
- Cursor IDE with MCP support

### External Dependencies
- OpenRouter API access
- Brave Search API (optional)
- Chrome/Chromium browser
- Node.js (for Node-based tools)

## Rollback Strategy

### Immediate Rollback
- Maintain original Mac-compatible code in separate branch
- Use feature flags to toggle Windows-specific code
- Implement graceful degradation for unsupported features

### Long-term Support
- Maintain parallel codepaths for Mac and Windows
- Implement runtime platform detection
- Provide platform-specific installation instructions

---

*This implementation plan will be updated as development progresses and new requirements are identified.*
