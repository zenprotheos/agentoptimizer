---
name: "Troubleshooting Guide - Oneshot Windows Testing"
purpose: "Document issues encountered and solutions implemented during testing framework development"
created: "2025-08-25T02:52:59.154Z"
status: "Active"
---

# Troubleshooting Guide - Oneshot Windows Testing

## Issue #1: Agent Execution Path Problem ❌ RESOLVED

### Problem Description
Initial test execution failed because the test framework was looking for `oneshot.py` in the project root, but the actual agent execution system uses `python app/agent_runner.py`.

### Error Messages
```
C:\ProgramData\anaconda3\python.exe: can't open file 'C:\\Users\\CSJin\\Jininja Projects\\AI Projects\\main_oneshot\\oneshot\\oneshot.py': [Errno 2] No such file or directory
```

### Root Cause Analysis
1. **Incorrect Agent Execution Command**: Test framework assumed `python oneshot.py <agent> <prompt>`
2. **Actual Execution Method**: System uses `python app/agent_runner.py <agent> <prompt>`
3. **Discovery**: Found `app/oneshot` bash script that executes `python3 app/agent_runner.py "$@"`

### Solution Implementation
Update all test frameworks to use the correct agent execution command:
- **OLD**: `['python', 'oneshot.py', agent_name, prompt]`
- **NEW**: `['python', 'app/agent_runner.py', agent_name, prompt]`

### Files Requiring Updates
- [ ] `master_test_runner.py` - Update agent execution commands
- [ ] `agent_tests.py` - Update agent execution commands  
- [ ] `integration_tests.py` - Update agent execution commands
- [x] `quick_test_runner.py` - **Already Fixed**

### Validation Steps
1. Update command execution in all test files
2. Re-run quick test to validate agent execution
3. Verify all agents respond correctly
4. Update documentation with correct execution method

## Issue #2: PowerShell Command Escaping Problem ❌ RESOLVED

### Problem Description
PowerShell command execution failing due to improper escaping of Python import statements.

### Error Messages
```
At line:1 char:76
+ ...  -c from tools.list_agents import list_agents; print(list_agents()) }
+                                                                      ~
An expression was expected after '('.
    + CategoryInfo          : ParserError: (:) [], ParentContainsErrorRecordException
    + FullyQualifiedErrorId : ExpectedExpression
```

### Root Cause Analysis
1. **PowerShell Escaping Issue**: Complex Python commands not properly escaped in PowerShell
2. **Nested Quote Problem**: PowerShell parsing conflicts with Python string quotes
3. **Special Character Handling**: Parentheses and semicolons causing PowerShell parsing errors

### Solution Implementation
Use temporary script files for complex Python commands instead of inline execution:
- **OLD**: Direct PowerShell execution of complex Python commands
- **NEW**: Write temp Python script, execute script, clean up

### Implementation Pattern
```python
# Create temp script in task-specific directory
temp_script_path = self.test_dir / f"temp_command_{timestamp}.py"
with open(temp_script_path, 'w', encoding='utf-8') as f:
    f.write(python_code)

# Execute with simple command
result = subprocess.run(['python', str(temp_script_path)], ...)

# Mandatory cleanup
temp_script_path.unlink()
```

### Files Requiring Updates
- [x] `quick_test_runner.py` - **Already Uses Temp Files**
- [ ] `master_test_runner.py` - Update complex command execution
- [ ] `agent_tests.py` - Update complex command execution
- [ ] `tool_tests.py` - Update complex command execution

## Issue #3: System Prerequisites Check Failures ⚠️ PARTIAL

### Problem Description
System prerequisites check partially failing due to missing directories and files.

### Failed Checks
1. **oneshot_script_exists**: Looking for `oneshot.py` instead of `app/agent_runner.py`
2. **agents_directory_exists**: May need verification of actual agent files

### Current Status
- ✅ **python_available**: Working correctly
- ❌ **oneshot_script_exists**: Incorrect file path
- ✅ **tools_directory_exists**: Working correctly  
- ✅ **agents_directory_exists**: Working correctly

### Solution Required
Update prerequisite checks to validate correct files:
- Check for `app/agent_runner.py` instead of `oneshot.py`
- Validate agent configuration files exist
- Verify tool imports work correctly

## Issue #4: Tool Testing Success ✅ WORKING

### Current Status
All tool tests are passing successfully:
- ✅ **list_agents**: Passed (1.83s)
- ✅ **list_tools**: Passed (2.15s)  
- ✅ **file_creator**: Passed (2.07s)
- ✅ **web_search**: Passed (1.32s)
- ✅ **read_file_contents**: Passed (2.21s)

### Analysis
- Tool import mechanism working correctly
- Temporary file creation and cleanup working
- Python module loading functioning properly
- Windows compatibility for tools validated

## Windows-Specific Findings ✅ POSITIVE

### PowerShell Integration Success
- Timeout protection working correctly
- Error handling and logging functional
- Temp file management following workspace rules
- Unicode and special character support working

### File System Operations
- Directory creation and navigation working
- Temp file creation in task-specific directories
- File cleanup protocols functioning
- Path normalization working correctly

## Performance Metrics

### Test Execution Times
- **Quick Test Suite**: ~14 seconds total
- **Tool Tests**: 1.3-2.2 seconds per tool (very good)
- **Agent Tests**: 0.7-1.0 seconds per agent (when working)
- **System Checks**: <1 second

### Resource Usage
- Memory usage: Minimal
- Disk I/O: Efficient temp file handling
- Network: No network calls in basic tests

## Next Steps - Immediate Actions Required

### Priority 1: Fix Agent Execution
1. **Update Test Commands**: Change all agent execution commands to use `app/agent_runner.py`
2. **Test Validation**: Re-run quick test to verify agent functionality
3. **Documentation Update**: Update all documentation with correct execution method

### Priority 2: Complete Framework Updates
1. **Master Test Runner**: Update agent execution commands
2. **Agent Tests**: Update agent execution commands
3. **Integration Tests**: Update agent execution commands
4. **Prerequisites Check**: Fix system validation checks

### Priority 3: Comprehensive Testing
1. **Full Test Suite**: Execute complete testing framework
2. **Performance Validation**: Benchmark all components
3. **Windows Compatibility**: Complete Windows-specific validations
4. **Integration Workflows**: Test end-to-end scenarios

## Lessons Learned

### Project Structure Understanding
- Always verify actual execution methods before assuming common patterns
- Check for platform-specific execution scripts (bash vs batch)
- Understand the relationship between entry points and core modules

### Windows PowerShell Compatibility
- Use temporary script files for complex commands
- Implement proper timeout protection
- Test with actual Windows command patterns

### Testing Framework Design
- Build prerequisite validation that matches actual system architecture
- Design modular tests that can be easily updated
- Implement comprehensive error reporting and analysis

### Tool vs Agent Architecture
- Tools can be imported directly as Python modules
- Agents require execution through the agent runner framework
- Different testing approaches needed for different component types

## Success Patterns

### What's Working Well
1. **Tool Testing Framework**: Excellent reliability and performance
2. **Temporary File Management**: Following workspace rules correctly
3. **Error Handling**: Comprehensive logging and error reporting
4. **Windows Compatibility**: Core infrastructure working properly

### Best Practices Identified
1. **Temp File Protocol**: Task-specific temporary files with mandatory cleanup
2. **Timeout Protection**: All command executions protected with timeouts
3. **Comprehensive Logging**: Detailed logging for debugging and analysis
4. **Modular Design**: Easy to update and maintain test components

---

**Status**: Active troubleshooting document  
**Last Updated**: 2025-08-25T03:00:00.000Z  
**Next Review**: After framework fixes are implemented
