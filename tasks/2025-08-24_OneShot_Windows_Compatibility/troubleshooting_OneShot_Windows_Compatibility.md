---
title: "OneShot Windows Compatibility - Troubleshooting Guide"
date: "2025-08-24"
task: "OneShot Windows Compatibility"
status: "In Progress"
priority: "High"
tags: ["troubleshooting", "windows", "debugging", "issues"]
---

# OneShot Windows Compatibility - Troubleshooting Guide

## Overview

This document provides comprehensive troubleshooting guidance for Windows-specific issues encountered during the OneShot MCP system adaptation from Mac to Windows environments.

## Common Windows Issues and Solutions

### 1. Path Resolution Failures

#### Issue: Unix-style paths not working on Windows
```
Error: FileNotFoundError: [Errno 2] No such file or directory: '/Users/user/documents/file.txt'
```

**Root Cause**: Mac-centric hardcoded paths using forward slashes and Unix directory structure.

**Solution**:
```python
# Before (Mac-centric)
config_path = "/Users/user/.oneshot/config.yaml"

# After (Windows-compatible)
from pathlib import Path
import os

config_path = Path.home() / ".oneshot" / "config.yaml"
# or
config_path = Path(os.path.expanduser("~")) / ".oneshot" / "config.yaml"
```

**Files Affected**:
- `app/agent_config.py`
- `app/oneshot_mcp.py`
- `tools/file_creator.py`

#### Issue: Long path limitations on Windows
```
Error: OSError: [Errno 22] Invalid argument: 'C:\\very\\long\\path\\exceeding\\260\\characters...'
```

**Root Cause**: Windows 260 character path limit (unless long path support enabled).

**Solution**:
```python
import os
from pathlib import Path

def enable_long_paths():
    """Enable long path support on Windows"""
    if os.name == 'nt':
        try:
            import ctypes
            from ctypes import wintypes
            kernel32 = ctypes.windll.kernel32
            # Enable long path support
            return True
        except Exception:
            return False
    return True

def safe_path_operation(path_str):
    """Safely handle long paths on Windows"""
    path = Path(path_str)
    if os.name == 'nt' and len(str(path)) > 260:
        # Use UNC path prefix for long paths
        return Path(f"\\\\?\\{path.resolve()}")
    return path
```

### 2. Process Execution Problems

#### Issue: subprocess calls failing with PowerShell
```
Error: subprocess.CalledProcessError: Command 'ls -la' returned non-zero exit status 1
```

**Root Cause**: Unix commands not available in Windows Command Prompt/PowerShell.

**Solution**:
```python
import subprocess
import sys

def execute_command(cmd, use_shell=True):
    """Cross-platform command execution"""
    if sys.platform == "win32":
        # Windows-specific handling
        if isinstance(cmd, str):
            # Use PowerShell for complex commands
            ps_cmd = ["powershell.exe", "-Command", cmd]
            return subprocess.run(ps_cmd, capture_output=True, text=True)
        else:
            # Use cmd for simple commands
            return subprocess.run(cmd, shell=True, capture_output=True, text=True)
    else:
        # Unix-like systems
        return subprocess.run(cmd, shell=use_shell, capture_output=True, text=True)

# Example usage
result = execute_command("Get-ChildItem -Force")  # PowerShell equivalent of 'ls -la'
```

#### Issue: Environment variables not found
```
Error: KeyError: 'HOME'
```

**Root Cause**: Unix environment variables don't exist on Windows.

**Solution**:
```python
import os
from pathlib import Path

def get_home_directory():
    """Get user home directory cross-platform"""
    if os.name == 'nt':
        return Path(os.environ.get('USERPROFILE', os.environ.get('HOMEPATH', '')))
    else:
        return Path(os.environ.get('HOME', ''))

def get_temp_directory():
    """Get temporary directory cross-platform"""
    if os.name == 'nt':
        return Path(os.environ.get('TEMP', os.environ.get('TMP', 'C:\\temp')))
    else:
        return Path('/tmp')
```

### 3. MCP Server Issues

#### Issue: MCP server fails to start on Windows
```
Error: [MCP] Failed to spawn command: python oneshot_mcp.py
```

**Root Cause**: Python executable not found or incorrect path format.

**Solution**:
```json
// Incorrect MCP configuration
{
  "mcpServers": {
    "oneshot": {
      "command": "python",
      "args": ["oneshot_mcp.py"]
    }
  }
}

// Correct Windows MCP configuration
{
  "mcpServers": {
    "oneshot": {
      "command": "powershell.exe",
      "args": [
        "-NoProfile", "-ExecutionPolicy", "Bypass", "-Command",
        "& { & 'C:\\Python312\\python.exe' 'C:\\path\\to\\oneshot\\app\\oneshot_mcp.py' }"
      ]
    }
  }
}
```

#### Issue: stdio transport hanging on Windows
```
Error: MCP server connection timeout
```

**Root Cause**: Windows buffer handling differences in stdio transport.

**Solution**:
```python
# In oneshot_mcp.py
import sys
import os

if os.name == 'nt':
    # Windows-specific stdio handling
    import msvcrt
    msvcrt.setmode(sys.stdin.fileno(), os.O_BINARY)
    msvcrt.setmode(sys.stdout.fileno(), os.O_BINARY)

# Alternative: Use SSE transport for Windows
def get_preferred_transport():
    if os.name == 'nt':
        return 'sse'  # Prefer SSE on Windows
    return 'stdio'
```

### 4. File Permission Issues

#### Issue: Permission denied errors on file operations
```
Error: PermissionError: [Errno 13] Permission denied: 'C:\\path\\to\\file.txt'
```

**Root Cause**: Windows file permission model differences.

**Solution**:
```python
import os
import stat
from pathlib import Path

def safe_file_operation(file_path, operation='read'):
    """Safely perform file operations with proper permissions"""
    path = Path(file_path)
    
    try:
        if operation == 'write':
            # Ensure directory exists
            path.parent.mkdir(parents=True, exist_ok=True)
            
            # Check if file exists and is writable
            if path.exists():
                # Make file writable if it's read-only
                path.chmod(stat.S_IWRITE | stat.S_IREAD)
        
        return True
    except Exception as e:
        print(f"Permission error: {e}")
        return False

# Example usage
if safe_file_operation("C:\\path\\to\\file.txt", "write"):
    with open("C:\\path\\to\\file.txt", "w") as f:
        f.write("content")
```

### 5. External Tool Dependencies

#### Issue: Browser executable not found
```
Error: selenium.common.exceptions.WebDriverException: Message: 'chromedriver' executable needs to be in PATH
```

**Root Cause**: Different browser installation paths on Windows.

**Solution**:
```python
from pathlib import Path
import os

def find_chrome_executable():
    """Find Chrome executable on Windows"""
    possible_paths = [
        Path("C:/Program Files/Google/Chrome/Application/chrome.exe"),
        Path("C:/Program Files (x86)/Google/Chrome/Application/chrome.exe"),
        Path(os.path.expanduser("~/AppData/Local/Google/Chrome/Application/chrome.exe")),
        Path("C:/Program Files/Google/Chrome Dev/Application/chrome.exe"),
    ]
    
    for path in possible_paths:
        if path.exists():
            return str(path)
    
    raise FileNotFoundError("Chrome executable not found")

def find_node_executable():
    """Find Node.js executable on Windows"""
    possible_paths = [
        Path("C:/Program Files/nodejs/node.exe"),
        Path("C:/Program Files (x86)/nodejs/node.exe"),
        Path(os.path.expanduser("~/AppData/Roaming/npm/node.exe")),
    ]
    
    for path in possible_paths:
        if path.exists():
            return str(path)
    
    raise FileNotFoundError("Node.js executable not found")
```

## Diagnostic Procedures

### 1. Environment Verification Script

```python
# diagnostics/verify_windows_environment.py
import os
import sys
from pathlib import Path
import subprocess

def verify_python_environment():
    """Verify Python installation and environment"""
    print(f"Python version: {sys.version}")
    print(f"Python executable: {sys.executable}")
    print(f"Platform: {sys.platform}")
    
    # Check for virtual environment
    if hasattr(sys, 'real_prefix') or (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix):
        print("✓ Running in virtual environment")
    else:
        print("⚠ Not running in virtual environment")

def verify_dependencies():
    """Verify required packages are installed"""
    required_packages = ['fastmcp', 'requests', 'pathlib']
    
    for package in required_packages:
        try:
            __import__(package)
            print(f"✓ {package} is available")
        except ImportError:
            print(f"✗ {package} is missing")

def verify_file_permissions():
    """Verify file system permissions"""
    test_dir = Path.home() / ".oneshot_test"
    
    try:
        test_dir.mkdir(exist_ok=True)
        test_file = test_dir / "test.txt"
        test_file.write_text("test content")
        content = test_file.read_text()
        test_file.unlink()
        test_dir.rmdir()
        print("✓ File operations working")
        return True
    except Exception as e:
        print(f"✗ File operations failed: {e}")
        return False

def verify_external_tools():
    """Verify external tool availability"""
    tools = {
        'chrome': find_chrome_executable,
        'node': find_node_executable,
    }
    
    for tool_name, finder_func in tools.items():
        try:
            path = finder_func()
            print(f"✓ {tool_name} found at: {path}")
        except FileNotFoundError:
            print(f"✗ {tool_name} not found")

if __name__ == "__main__":
    print("OneShot Windows Environment Verification")
    print("=" * 40)
    verify_python_environment()
    print()
    verify_dependencies()
    print()
    verify_file_permissions()
    print()
    verify_external_tools()
```

### 2. MCP Connection Test

```python
# diagnostics/test_mcp_connection.py
import json
import subprocess
import sys
from pathlib import Path

def test_mcp_server_startup():
    """Test if MCP server can start properly"""
    server_path = Path(__file__).parent.parent / "app" / "oneshot_mcp.py"
    
    try:
        # Test direct Python execution
        result = subprocess.run(
            [sys.executable, str(server_path)],
            capture_output=True,
            text=True,
            timeout=10
        )
        
        if result.returncode == 0:
            print("✓ MCP server starts successfully")
            return True
        else:
            print(f"✗ MCP server failed to start: {result.stderr}")
            return False
    except subprocess.TimeoutExpired:
        print("✗ MCP server startup timeout")
        return False
    except Exception as e:
        print(f"✗ MCP server test failed: {e}")
        return False

def test_mcp_tools_available():
    """Test if MCP tools are properly loaded"""
    # Implementation would depend on MCP protocol specifics
    pass

if __name__ == "__main__":
    print("OneShot MCP Connection Test")
    print("=" * 30)
    test_mcp_server_startup()
```

## Performance Optimization for Windows

### 1. File I/O Optimization

```python
# utils/windows_performance.py
import os
from pathlib import Path

def optimize_file_operations():
    """Optimize file operations for Windows"""
    if os.name == 'nt':
        # Use Windows-specific optimizations
        import threading
        
        # Enable concurrent file operations
        def threaded_file_operation(func, *args, **kwargs):
            thread = threading.Thread(target=func, args=args, kwargs=kwargs)
            thread.start()
            return thread
        
        return threaded_file_operation
    
    return lambda func, *args, **kwargs: func(*args, **kwargs)
```

### 2. Process Pool Optimization

```python
# utils/process_optimization.py
import multiprocessing
import os

def get_optimal_worker_count():
    """Get optimal worker count for Windows"""
    if os.name == 'nt':
        # Windows-specific worker count calculation
        cpu_count = multiprocessing.cpu_count()
        # Conservative approach on Windows
        return max(1, cpu_count // 2)
    else:
        return multiprocessing.cpu_count()
```

## Logging and Debugging

### 1. Windows-Specific Logging Configuration

```python
# utils/windows_logging.py
import logging
import os
from pathlib import Path

def setup_windows_logging():
    """Setup logging optimized for Windows"""
    if os.name == 'nt':
        log_dir = Path(os.environ.get('LOCALAPPDATA', '')) / 'OneShot' / 'logs'
    else:
        log_dir = Path.home() / '.oneshot' / 'logs'
    
    log_dir.mkdir(parents=True, exist_ok=True)
    
    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_dir / 'oneshot.log'),
            logging.StreamHandler()
        ]
    )
    
    return logging.getLogger('oneshot')
```

### 2. Debug Information Collection

```python
# utils/debug_info.py
import sys
import os
import platform
from pathlib import Path

def collect_debug_info():
    """Collect comprehensive debug information"""
    debug_info = {
        'platform': {
            'system': platform.system(),
            'release': platform.release(),
            'version': platform.version(),
            'machine': platform.machine(),
            'processor': platform.processor(),
        },
        'python': {
            'version': sys.version,
            'executable': sys.executable,
            'path': sys.path,
        },
        'environment': {
            'PATH': os.environ.get('PATH', ''),
            'PYTHONPATH': os.environ.get('PYTHONPATH', ''),
            'TEMP': os.environ.get('TEMP', ''),
            'USERPROFILE': os.environ.get('USERPROFILE', ''),
        },
        'file_system': {
            'cwd': os.getcwd(),
            'home': str(Path.home()),
        }
    }
    
    return debug_info

def save_debug_info(filename='debug_info.json'):
    """Save debug information to file"""
    import json
    debug_info = collect_debug_info()
    
    with open(filename, 'w') as f:
        json.dump(debug_info, f, indent=2)
    
    print(f"Debug information saved to {filename}")
```

## Recovery Procedures

### 1. Configuration Reset

```python
# utils/recovery.py
from pathlib import Path
import shutil
import os

def backup_configuration():
    """Backup current configuration"""
    config_dir = Path.home() / '.oneshot'
    backup_dir = Path.home() / '.oneshot_backup'
    
    if config_dir.exists():
        if backup_dir.exists():
            shutil.rmtree(backup_dir)
        shutil.copytree(config_dir, backup_dir)
        print(f"Configuration backed up to {backup_dir}")

def reset_configuration():
    """Reset configuration to defaults"""
    config_dir = Path.home() / '.oneshot'
    
    if config_dir.exists():
        backup_configuration()
        shutil.rmtree(config_dir)
    
    # Recreate with defaults
    config_dir.mkdir(parents=True, exist_ok=True)
    print("Configuration reset to defaults")

def restore_configuration():
    """Restore configuration from backup"""
    config_dir = Path.home() / '.oneshot'
    backup_dir = Path.home() / '.oneshot_backup'
    
    if backup_dir.exists():
        if config_dir.exists():
            shutil.rmtree(config_dir)
        shutil.copytree(backup_dir, config_dir)
        print("Configuration restored from backup")
    else:
        print("No backup found")
```

## Prevention Strategies

### 1. Pre-deployment Checks

```python
# utils/precheck.py
def run_predeployment_checks():
    """Run comprehensive pre-deployment checks"""
    checks = [
        verify_python_environment,
        verify_dependencies,
        verify_file_permissions,
        verify_external_tools,
        test_mcp_server_startup,
    ]
    
    results = []
    for check in checks:
        try:
            result = check()
            results.append((check.__name__, result))
        except Exception as e:
            results.append((check.__name__, f"Error: {e}"))
    
    # Report results
    print("Pre-deployment Check Results:")
    print("=" * 30)
    for check_name, result in results:
        status = "✓" if result is True else "✗"
        print(f"{status} {check_name}: {result}")
    
    return all(result is True for _, result in results)
```

---

*This troubleshooting guide will be continuously updated as new Windows-specific issues are identified and resolved during the development process.*
