#!/usr/bin/env python3
"""
Quick Test Runner for Oneshot Windows Compatibility Testing

This script provides a fast validation of the most critical agents and tools
to quickly verify system functionality during development and troubleshooting.
"""

import os
import sys
import json
import time
import subprocess
import platform
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class QuickTestRunner:
    """Fast validation runner for critical system components"""
    
    def __init__(self):
        self.project_root = self._find_project_root()
        self.is_windows = platform.system() == 'Windows'
        self.test_dir = Path(__file__).parent
        
        # Quick test configuration - subset of most critical components
        self.quick_agents = [
            'web_agent',      # Most commonly used
            'search_agent',   # Core search functionality  
            'oneshot_agent',  # Agent orchestration
            'list_agents'     # Basic system validation
        ]
        
        self.quick_tools = [
            'list_agents',          # System validation
            'list_tools',           # System validation
            'file_creator',         # File operations
            'web_search',           # Web operations
            'read_file_contents'    # File reading
        ]
        
        self.results = {
            'test_type': 'quick_validation',
            'start_time': datetime.now().isoformat(),
            'end_time': None,
            'system_info': {
                'platform': platform.system(),
                'python_version': sys.version,
                'project_root': str(self.project_root)
            },
            'agent_tests': {},
            'tool_tests': {},
            'system_checks': {},
            'summary': {
                'total_tests': 0,
                'passed_tests': 0,
                'failed_tests': 0,
                'critical_failures': []
            }
        }
        
        logger.info(f"Quick Test Runner initialized on {platform.system()}")
    
    def _find_project_root(self) -> Path:
        """Find the Oneshot project root directory"""
        current = Path(__file__).parent
        while current.parent != current:
            if (current / 'oneshot.py').exists() or (current / 'app').exists():
                return current
            current = current.parent
        return Path.cwd()
    
    def _run_command_with_timeout(self, command: List[str], timeout: int = 30) -> Tuple[int, str, str]:
        """Run command with Windows-compatible timeout handling"""
        try:
            logger.debug(f"Running: {' '.join(command)}")
            
            if self.is_windows:
                # Use PowerShell wrapper for better Windows compatibility
                ps_command = [
                    'powershell', '-NoProfile', '-ExecutionPolicy', 'Bypass', '-Command',
                    f"& {{ {' '.join(command)} }}"
                ]
                result = subprocess.run(
                    ps_command,
                    capture_output=True,
                    text=True,
                    timeout=timeout,
                    cwd=self.project_root
                )
            else:
                result = subprocess.run(
                    command,
                    capture_output=True,
                    text=True,
                    timeout=timeout,
                    cwd=self.project_root
                )
            
            return result.returncode, result.stdout, result.stderr
            
        except subprocess.TimeoutExpired:
            logger.error(f"Command timed out after {timeout}s: {' '.join(command)}")
            return -1, "", f"Timeout after {timeout}s"
        except Exception as e:
            logger.error(f"Command execution failed: {e}")
            return -1, "", str(e)
    
    def test_system_prerequisites(self) -> Dict[str, Any]:
        """Test basic system prerequisites"""
        logger.info("Testing system prerequisites...")
        
        prereq_result = {
            'test_name': 'system_prerequisites',
            'start_time': datetime.now().isoformat(),
            'checks': {},
            'status': 'pending'
        }
        
        checks = [
            ('python_available', ['python', '--version']),
            ('oneshot_script_exists', None),  # File check
            ('tools_directory_exists', None), # Directory check
            ('agents_directory_exists', None) # Directory check
        ]
        
        passed_checks = 0
        
        for check_name, command in checks:
            try:
                if command is None:
                    # File/directory existence checks
                    if check_name == 'oneshot_script_exists':
                        exists = (self.project_root / 'app' / 'agent_runner.py').exists()
                    elif check_name == 'tools_directory_exists':
                        exists = (self.project_root / 'tools').exists()
                    elif check_name == 'agents_directory_exists':
                        exists = (self.project_root / 'agents').exists()
                    else:
                        exists = False
                    
                    prereq_result['checks'][check_name] = {
                        'type': 'file_check',
                        'passed': exists,
                        'details': 'File/directory exists' if exists else 'File/directory missing'
                    }
                    
                    if exists:
                        passed_checks += 1
                else:
                    # Command execution checks
                    returncode, stdout, stderr = self._run_command_with_timeout(command, 10)
                    
                    prereq_result['checks'][check_name] = {
                        'type': 'command_check',
                        'command': ' '.join(command),
                        'returncode': returncode,
                        'passed': returncode == 0,
                        'stdout': stdout[:200] if stdout else '',  # Limit output
                        'stderr': stderr[:200] if stderr else ''
                    }
                    
                    if returncode == 0:
                        passed_checks += 1
                        logger.info(f"✅ {check_name} passed")
                    else:
                        logger.error(f"❌ {check_name} failed: {stderr}")
                        
            except Exception as e:
                prereq_result['checks'][check_name] = {
                    'type': 'exception',
                    'passed': False,
                    'error': str(e)
                }
                logger.error(f"❌ {check_name} exception: {e}")
        
        prereq_result['passed_checks'] = passed_checks
        prereq_result['total_checks'] = len(checks)
        prereq_result['status'] = 'passed' if passed_checks == len(checks) else 'failed'
        prereq_result['end_time'] = datetime.now().isoformat()
        
        return prereq_result
    
    def test_agent_quick(self, agent_name: str) -> Dict[str, Any]:
        """Quick test of a single agent"""
        logger.info(f"Quick testing agent: {agent_name}")
        
        test_result = {
            'agent_name': agent_name,
            'test_type': 'quick_agent_test',
            'start_time': datetime.now().isoformat(),
            'status': 'pending'
        }
        
        try:
            # Use a simple, fast test prompt
            test_prompt = "Hello, this is a quick system test"
            
            if agent_name == 'list_agents':
                # Special case - this is actually a tool, not an agent
                command = ['python', 'app/agent_runner.py', 'list_agents', test_prompt]
            else:
                command = ['python', 'app/agent_runner.py', agent_name, test_prompt]
            
            start_time = time.time()
            returncode, stdout, stderr = self._run_command_with_timeout(command, 45)
            duration = time.time() - start_time
            
            test_result.update({
                'duration': duration,
                'returncode': returncode,
                'has_output': bool(stdout and stdout.strip()),
                'output_length': len(stdout) if stdout else 0,
                'error_message': stderr if stderr else None
            })
            
            if returncode == 0 and stdout.strip():
                test_result['status'] = 'passed'
                logger.info(f"✅ Agent {agent_name} quick test passed ({duration:.2f}s)")
            else:
                test_result['status'] = 'failed'
                logger.error(f"❌ Agent {agent_name} quick test failed: {stderr or 'No output'}")
                
        except Exception as e:
            test_result['status'] = 'failed'
            test_result['error'] = str(e)
            logger.error(f"❌ Agent {agent_name} quick test exception: {e}")
        
        test_result['end_time'] = datetime.now().isoformat()
        return test_result
    
    def test_tool_quick(self, tool_name: str) -> Dict[str, Any]:
        """Quick test of a single tool"""
        logger.info(f"Quick testing tool: {tool_name}")
        
        test_result = {
            'tool_name': tool_name,
            'test_type': 'quick_tool_test',
            'start_time': datetime.now().isoformat(),
            'status': 'pending'
        }
        
        try:
            # Create a simple import test in a temp script
            temp_script_content = f"""
import sys
sys.path.append('.')
try:
    from tools.{tool_name} import *
    print(f"✅ Tool {tool_name} imported successfully")
    print(f"Available functions: {{[attr for attr in dir() if not attr.startswith('_')]}}")
except ImportError as e:
    print(f"❌ Import failed: {{e}}")
    sys.exit(1)
except Exception as e:
    print(f"❌ Tool error: {{e}}")
    sys.exit(1)
"""
            
            # Write to task-specific temp file (following workspace rules)
            temp_script_path = self.test_dir / f"temp_quick_test_{tool_name}.py"
            
            with open(temp_script_path, 'w', encoding='utf-8') as f:
                f.write(temp_script_content)
            
            try:
                start_time = time.time()
                returncode, stdout, stderr = self._run_command_with_timeout(
                    ['python', str(temp_script_path)], 20
                )
                duration = time.time() - start_time
                
                test_result.update({
                    'duration': duration,
                    'returncode': returncode,
                    'import_successful': returncode == 0,
                    'output': stdout,
                    'error_message': stderr if stderr else None
                })
                
                if returncode == 0:
                    test_result['status'] = 'passed'
                    logger.info(f"✅ Tool {tool_name} quick test passed ({duration:.2f}s)")
                else:
                    test_result['status'] = 'failed'
                    logger.error(f"❌ Tool {tool_name} quick test failed: {stderr}")
                    
            finally:
                # MANDATORY: Clean up temp file (following workspace rules)
                if temp_script_path.exists():
                    temp_script_path.unlink()
                    
        except Exception as e:
            test_result['status'] = 'failed'
            test_result['error'] = str(e)
            logger.error(f"❌ Tool {tool_name} quick test exception: {e}")
        
        test_result['end_time'] = datetime.now().isoformat()
        return test_result
    
    def run_quick_tests(self) -> Dict[str, Any]:
        """Run the complete quick test suite"""
        logger.info("🚀 Starting Quick Test Suite for Oneshot System")
        
        # Test system prerequisites first
        prereq_test = self.test_system_prerequisites()
        self.results['system_checks']['prerequisites'] = prereq_test
        self.results['summary']['total_tests'] += 1
        
        if prereq_test['status'] == 'passed':
            self.results['summary']['passed_tests'] += 1
            logger.info("✅ System prerequisites check passed")
        else:
            self.results['summary']['failed_tests'] += 1
            self.results['summary']['critical_failures'].append('System prerequisites failed')
            logger.error("❌ System prerequisites check failed - continuing anyway")
        
        # Test critical agents
        for agent_name in self.quick_agents:
            try:
                agent_result = self.test_agent_quick(agent_name)
                self.results['agent_tests'][agent_name] = agent_result
                self.results['summary']['total_tests'] += 1
                
                if agent_result['status'] == 'passed':
                    self.results['summary']['passed_tests'] += 1
                else:
                    self.results['summary']['failed_tests'] += 1
                    if agent_name in ['oneshot_agent', 'web_agent']:
                        self.results['summary']['critical_failures'].append(f'Critical agent {agent_name} failed')
                        
            except Exception as e:
                logger.error(f"Failed to test agent {agent_name}: {e}")
                self.results['summary']['failed_tests'] += 1
                self.results['summary']['critical_failures'].append(f'Agent {agent_name} test crashed')
        
        # Test critical tools  
        for tool_name in self.quick_tools:
            try:
                tool_result = self.test_tool_quick(tool_name)
                self.results['tool_tests'][tool_name] = tool_result
                self.results['summary']['total_tests'] += 1
                
                if tool_result['status'] == 'passed':
                    self.results['summary']['passed_tests'] += 1
                else:
                    self.results['summary']['failed_tests'] += 1
                    if tool_name in ['list_agents', 'list_tools']:
                        self.results['summary']['critical_failures'].append(f'Critical tool {tool_name} failed')
                        
            except Exception as e:
                logger.error(f"Failed to test tool {tool_name}: {e}")
                self.results['summary']['failed_tests'] += 1
                self.results['summary']['critical_failures'].append(f'Tool {tool_name} test crashed')
        
        self.results['end_time'] = datetime.now().isoformat()
        return self.results
    
    def generate_quick_report(self) -> str:
        """Generate a concise test report"""
        summary = self.results['summary']
        
        # Calculate pass rate
        pass_rate = (summary['passed_tests'] / max(summary['total_tests'], 1)) * 100
        
        report = f"""
# Quick Test Report - Oneshot System

## Summary
- **Total Tests:** {summary['total_tests']}
- **Passed:** {summary['passed_tests']} ✅
- **Failed:** {summary['failed_tests']} ❌
- **Pass Rate:** {pass_rate:.1f}%
- **Platform:** {self.results['system_info']['platform']}

## Critical Status
"""
        
        if len(summary['critical_failures']) == 0:
            report += "✅ **No critical failures detected**\n"
        else:
            report += "❌ **Critical failures detected:**\n"
            for failure in summary['critical_failures']:
                report += f"  - {failure}\n"
        
        report += "\n## Quick Test Results\n\n### System Checks\n"
        prereq = self.results['system_checks'].get('prerequisites', {})
        if prereq:
            status_icon = "✅" if prereq['status'] == 'passed' else "❌"
            report += f"- **Prerequisites:** {status_icon} {prereq['status']} ({prereq.get('passed_checks', 0)}/{prereq.get('total_checks', 0)})\n"
        
        report += "\n### Agent Tests\n"
        for agent, result in self.results['agent_tests'].items():
            status_icon = "✅" if result['status'] == 'passed' else "❌"
            duration = result.get('duration', 0)
            report += f"- **{agent}:** {status_icon} {result['status']} ({duration:.2f}s)\n"
        
        report += "\n### Tool Tests\n"
        for tool, result in self.results['tool_tests'].items():
            status_icon = "✅" if result['status'] == 'passed' else "❌"
            duration = result.get('duration', 0)
            report += f"- **{tool}:** {status_icon} {result['status']} ({duration:.2f}s)\n"
        
        if summary['failed_tests'] > 0:
            report += "\n## ⚠️ Next Steps\n"
            report += "- Run full test suite: `python master_test_runner.py`\n"
            report += "- Check detailed logs for failure analysis\n"
            report += "- Verify Windows environment configuration\n"
        else:
            report += "\n## ✅ System Ready\n"
            report += "- Basic functionality validated\n"
            report += "- Ready for production use\n"
            report += "- Consider running full test suite for comprehensive validation\n"
        
        return report
    
    def save_results(self) -> Path:
        """Save test results and generate report"""
        # Save JSON results
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        json_file = self.test_dir / f"quick_test_results_{timestamp}.json"
        
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump(self.results, f, indent=2, ensure_ascii=False)
        
        # Save markdown report
        report_file = self.test_dir / f"quick_test_report_{timestamp}.md"
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write(self.generate_quick_report())
        
        logger.info(f"Quick test results saved to: {json_file}")
        logger.info(f"Quick test report saved to: {report_file}")
        
        return report_file

def main():
    """Main entry point for quick testing"""
    print("⚡ Oneshot Quick Test Runner")
    print("=" * 35)
    
    runner = QuickTestRunner()
    
    try:
        # Run quick tests
        results = runner.run_quick_tests()
        
        # Generate and display report
        report = runner.generate_quick_report()
        print(report)
        
        # Save results
        report_file = runner.save_results()
        
        # Determine exit code
        summary = results['summary']
        
        if len(summary['critical_failures']) > 0:
            print("\n❌ Critical failures detected!")
            print("Run full test suite for detailed analysis.")
            sys.exit(2)
        elif summary['failed_tests'] > 0:
            print("\n⚠️ Some tests failed, but no critical issues.")
            sys.exit(1)
        else:
            print("\n✅ All quick tests passed!")
            sys.exit(0)
            
    except KeyboardInterrupt:
        print("\n⏹️ Quick tests interrupted by user")
        sys.exit(2)
    except Exception as e:
        logger.error(f"Quick test runner failed: {e}")
        sys.exit(3)

if __name__ == "__main__":
    main()
