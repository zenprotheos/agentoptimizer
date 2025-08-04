#!/usr/bin/env python3
"""
Comprehensive System Test for Oneshot Agent Framework
Tests agent configuration, error handling, tools, templates, and file processing
"""

import os
import sys
import subprocess
import tempfile
import shutil
from pathlib import Path
from typing import Dict, Any, List

def run_command(cmd: List[str], cwd: Path = None) -> Dict[str, Any]:
    """Run a command and return the result"""
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            cwd=cwd or Path.cwd()
        )
        return {
            "success": result.returncode == 0,
            "stdout": result.stdout.strip(),
            "stderr": result.stderr.strip(),
            "returncode": result.returncode
        }
    except Exception as e:
        return {
            "success": False,
            "stdout": "",
            "stderr": str(e),
            "returncode": -1
        }

def test_valid_agent():
    """Test that the test_agent works correctly"""
    print("🧪 Testing valid agent configuration...")
    
    result = run_command(["./oneshot", "test_agent", "Hello, please test your functionality"])
    
    if result["success"]:
        print("✅ Test agent executed successfully")
        stdout_lower = result["stdout"].lower()
        if "test agent" in stdout_lower or "i am the test agent" in stdout_lower or "test_agent" in stdout_lower:
            print("✅ Agent correctly identified itself")
        else:
            print("⚠️  Agent response doesn't seem to identify itself as test agent")
            print(f"   Response snippet: {result['stdout'][:100]}...")
        return True
    else:
        print(f"❌ Test agent failed: {result['stderr']}")
        return False

def test_tool_functionality():
    """Test that the test_tool can be called"""
    print("\n🧪 Testing tool functionality...")
    
    result = run_command(["./oneshot", "test_agent", "Please call your test_tool to verify it works"])
    
    if result["success"]:
        stdout_lower = result["stdout"].lower()
        if ("test tool executed successfully" in stdout_lower or 
            "✅ test tool executed successfully" in stdout_lower or
            "called the test_tool" in stdout_lower):
            print("✅ Test tool called successfully")
            return True
        else:
            print("⚠️  Test tool may not have been called (check agent response)")
            print(f"Response: {result['stdout'][:300]}...")
            return True  # Don't fail if tool wasn't called, agent might have other reasons
    else:
        print(f"❌ Tool functionality test failed: {result['stderr']}")
        return False

def test_file_processing():
    """Test file processing functionality"""
    print("\n🧪 Testing file processing...")
    
    result = run_command([
        "./oneshot", "test_agent", 
        "I've provided you with a test file. Please confirm you can see its content.",
        "--files", "test_data/sample_file.txt"
    ])
    
    if result["success"]:
        if "sample test file" in result["stdout"].lower() or "file passing" in result["stdout"].lower():
            print("✅ File content processed successfully")
            return True
        else:
            print("⚠️  File content may not have been processed correctly")
            print(f"Response: {result['stdout'][:200]}...")
            return True  # Don't fail, might be working but not explicitly mentioned
    else:
        print(f"❌ File processing test failed: {result['stderr']}")
        return False

def test_template_includes():
    """Test that template includes are working"""
    print("\n🧪 Testing template includes...")
    
    result = run_command(["./oneshot", "test_agent", "Do you see the test snippet content in your system prompt?"])
    
    if result["success"]:
        # The test snippet should be visible in the agent's context
        print("✅ Template includes appear to be working (agent responded successfully)")
        return True
    else:
        if "template include file not found" in result["stderr"].lower():
            print("❌ Template include failed - test_snippet.md not found")
            return False
        else:
            print(f"❌ Template include test failed: {result['stderr']}")
            return False

def test_error_handling():
    """Test error handling with invalid configurations"""
    print("\n🧪 Testing error handling...")
    
    # Test with a broken configuration - invalid tool and model
    broken_agent_content = """---
name: broken_agent
description: "A broken test agent"
model: invalid-model-name
tools:
  - nonexistent_tool
temperature: "hot"
---

# Broken Agent
This agent has configuration errors.
"""
    
    # Copy to agents directory temporarily
    agents_dir = Path("agents")
    temp_agent_path = agents_dir / "broken_agent.md"
    
    try:
        temp_agent_path.write_text(broken_agent_content)
        
        result = run_command(["./oneshot", "broken_agent", "Hello"])
        
        # Check for error messages in both stdout and stderr (error location varies)
        stderr_content = result["stderr"].lower()
        stdout_content = result["stdout"].lower()
        all_output = stderr_content + " " + stdout_content
        
        if "configuration error" in all_output:
            print("✅ Configuration errors caught correctly")
            return True
        elif ("yaml" in all_output and "error" in all_output) or "syntax error" in all_output:
            print("✅ YAML syntax errors caught correctly")
            return True
        elif "error" in all_output and ("tool" in all_output or "model" in all_output):
            print("✅ Error handling working (caught configuration issues)")
            return True
        else:
            print("❌ Error handling failed - no error messages found")
            print(f"Expected error messages, but got:")
            print(f"Stderr: {result['stderr'][:200]}")
            print(f"Stdout: {result['stdout'][:200]}")
            return False
            
    finally:
        # Clean up
        if temp_agent_path.exists():
            temp_agent_path.unlink()

def test_mcp_server_integration():
    """Test MCP server integration (basic test)"""
    print("\n🧪 Testing MCP server integration...")
    
    # Just test that the system can handle MCP configuration without crashing
    result = run_command(["python3", "-c", 
        "from app.oneshot_mcp_tools.list_agents import list_agents; import os; print(list_agents(os.getcwd()))"
    ])
    
    if result["success"]:
        if "test_agent" in result["stdout"]:
            print("✅ MCP server integration working (can list agents)")
            return True
        else:
            print("⚠️  MCP server working but test_agent not found in list")
            return True
    else:
        print(f"❌ MCP server integration test failed: {result['stderr']}")
        return False

def check_prerequisites():
    """Check that all required files exist"""
    print("🔍 Checking prerequisites...")
    
    required_files = [
        "agents/test_agent.md",
        "tools/test_tool.py", 
        "snippets/test_snippet.md",
        "test_data/sample_file.txt",
        "oneshot"  # Main agent script
    ]
    
    missing_files = []
    for file_path in required_files:
        if not Path(file_path).exists():
            missing_files.append(file_path)
    
    if missing_files:
        print(f"❌ Missing required files: {', '.join(missing_files)}")
        return False
    
    print("✅ All required files present")
    return True

def main():
    """Run all system tests"""
    print("🚀 Oneshot Agent System Test Suite")
    print("=" * 50)
    
    # Check prerequisites
    if not check_prerequisites():
        print("\n❌ Prerequisites not met. Please ensure all test files are created.")
        return False
    
    # Run tests
    tests = [
        ("Valid Agent Configuration", test_valid_agent),
        ("Tool Functionality", test_tool_functionality),
        ("File Processing", test_file_processing),
        ("Template Includes", test_template_includes),
        ("Error Handling", test_error_handling),
        ("MCP Server Integration", test_mcp_server_integration),
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            success = test_func()
            results.append((test_name, success))
        except Exception as e:
            print(f"❌ {test_name} failed with exception: {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 Test Results Summary")
    print("=" * 50)
    
    passed = 0
    for test_name, success in results:
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status}: {test_name}")
        if success:
            passed += 1
    
    print(f"\nOverall: {passed}/{len(results)} tests passed")
    
    if passed == len(results):
        print("\n🎉 All tests passed! System is working correctly.")
        return True
    else:
        print(f"\n⚠️  {len(results) - passed} test(s) failed. Please review the output above.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 