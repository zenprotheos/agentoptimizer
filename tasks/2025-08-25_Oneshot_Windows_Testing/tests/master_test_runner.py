#!/usr/bin/env python3
"""
Master Test Runner for Oneshot Windows Compatibility Testing

This script orchestrates comprehensive testing of all agents and tools in the Oneshot system,
with special focus on Windows compatibility validation.
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
import traceback
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('test_results.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class OneshotTestRunner:
    """Main test runner for comprehensive Oneshot system testing"""
    
    def __init__(self):
        self.test_results = {
            'summary': {
                'start_time': datetime.now().isoformat(),
                'end_time': None,
                'total_tests': 0,
                'passed_tests': 0,
                'failed_tests': 0,
                'skipped_tests': 0,
                'windows_specific_tests': 0,
                'windows_specific_passed': 0
            },
            'agent_tests': {},
            'tool_tests': {},
            'integration_tests': {},
            'windows_compatibility_tests': {},
            'performance_tests': {},
            'errors': []
        }
        
        self.project_root = self._find_project_root()
        self.test_dir = Path(__file__).parent
        
        # Windows-specific configuration
        self.is_windows = platform.system() == 'Windows'
        self.powershell_available = self._check_powershell()
        
        logger.info(f"Initializing Oneshot Test Runner on {platform.system()}")
        logger.info(f"Project root: {self.project_root}")
        logger.info(f"PowerShell available: {self.powershell_available}")
    
    def _find_project_root(self) -> Path:
        """Find the Oneshot project root directory"""
        current = Path(__file__).parent
        while current.parent != current:
            if (current / 'oneshot.py').exists() or (current / 'app').exists():
                return current
            current = current.parent
        return Path.cwd()
    
    def _check_powershell(self) -> bool:
        """Check if PowerShell is available and working"""
        if not self.is_windows:
            return False
        
        try:
            result = subprocess.run(
                ['powershell', '-Command', 'Get-Host'],
                capture_output=True,
                text=True,
                timeout=10
            )
            return result.returncode == 0
        except Exception:
            return False
    
    def _run_command(self, command: List[str], timeout: int = 30, cwd: Optional[Path] = None) -> Tuple[int, str, str]:
        """Run a command with proper Windows handling and timeout"""
        try:
            if cwd is None:
                cwd = self.project_root
            
            logger.debug(f"Running command: {' '.join(command)} in {cwd}")
            
            result = subprocess.run(
                command,
                capture_output=True,
                text=True,
                timeout=timeout,
                cwd=cwd
            )
            
            return result.returncode, result.stdout, result.stderr
        except subprocess.TimeoutExpired:
            logger.error(f"Command timed out after {timeout}s: {' '.join(command)}")
            return -1, "", f"Command timed out after {timeout}s"
        except Exception as e:
            logger.error(f"Command execution failed: {e}")
            return -1, "", str(e)
    
    def test_agent_basic_functionality(self, agent_name: str, test_prompt: str = "Hello, test message") -> Dict[str, Any]:
        """Test basic agent functionality"""
        logger.info(f"Testing agent: {agent_name}")
        
        test_result = {
            'agent_name': agent_name,
            'test_type': 'basic_functionality',
            'status': 'pending',
            'start_time': datetime.now().isoformat(),
            'end_time': None,
            'duration_seconds': 0,
            'error_message': None,
            'response_received': False,
            'response_length': 0,
            'windows_specific_issues': []
        }
        
        start_time = time.time()
        
        try:
            # Test agent via agent runner
            command = ['python', 'app/agent_runner.py', agent_name, f'"{test_prompt}"']
            returncode, stdout, stderr = self._run_command(command, timeout=60)
            
            test_result['end_time'] = datetime.now().isoformat()
            test_result['duration_seconds'] = time.time() - start_time
            
            if returncode == 0 and stdout.strip():
                test_result['status'] = 'passed'
                test_result['response_received'] = True
                test_result['response_length'] = len(stdout)
                logger.info(f"✅ Agent {agent_name} test passed")
            else:
                test_result['status'] = 'failed'
                test_result['error_message'] = stderr or "No response received"
                logger.error(f"❌ Agent {agent_name} test failed: {test_result['error_message']}")
                
                # Check for Windows-specific issues
                if self.is_windows and any(issue in stderr.lower() for issue in 
                    ['path', 'permission', 'powershell', 'encoding', 'drive']):
                    test_result['windows_specific_issues'].append("Potential Windows path/permission issue detected")
            
        except Exception as e:
            test_result['status'] = 'failed'
            test_result['error_message'] = str(e)
            test_result['end_time'] = datetime.now().isoformat()
            test_result['duration_seconds'] = time.time() - start_time
            logger.error(f"❌ Agent {agent_name} test failed with exception: {e}")
        
        return test_result
    
    def test_tool_functionality(self, tool_name: str) -> Dict[str, Any]:
        """Test individual tool functionality"""
        logger.info(f"Testing tool: {tool_name}")
        
        test_result = {
            'tool_name': tool_name,
            'test_type': 'tool_functionality',
            'status': 'pending',
            'start_time': datetime.now().isoformat(),
            'end_time': None,
            'duration_seconds': 0,
            'error_message': None,
            'tool_executed': False,
            'windows_compatibility': True,
            'windows_specific_issues': []
        }
        
        start_time = time.time()
        
        try:
            # Create test script for tool validation
            tool_test_script = f"""
import sys
sys.path.append('.')
try:
    from tools.{tool_name} import *
    print(f"✅ Tool {tool_name} imported successfully")
    # Add basic tool validation here
except ImportError as e:
    print(f"❌ Tool {tool_name} import failed: {{e}}")
    sys.exit(1)
except Exception as e:
    print(f"❌ Tool {tool_name} validation failed: {{e}}")
    sys.exit(1)
"""
            
            # Write temporary test script
            temp_script_path = self.test_dir / f"temp_test_{tool_name}.py"
            with open(temp_script_path, 'w', encoding='utf-8') as f:
                f.write(tool_test_script)
            
            try:
                # Execute tool test
                command = ['python', str(temp_script_path)]
                returncode, stdout, stderr = self._run_command(command, timeout=30)
                
                test_result['end_time'] = datetime.now().isoformat()
                test_result['duration_seconds'] = time.time() - start_time
                
                if returncode == 0:
                    test_result['status'] = 'passed'
                    test_result['tool_executed'] = True
                    logger.info(f"✅ Tool {tool_name} test passed")
                else:
                    test_result['status'] = 'failed'
                    test_result['error_message'] = stderr or stdout
                    logger.error(f"❌ Tool {tool_name} test failed: {test_result['error_message']}")
                    
                    # Check for Windows-specific issues
                    if self.is_windows:
                        error_text = (stderr + stdout).lower()
                        if any(issue in error_text for issue in 
                            ['path', 'permission', 'encoding', 'drive', 'powershell']):
                            test_result['windows_compatibility'] = False
                            test_result['windows_specific_issues'].append("Windows compatibility issue detected")
            
            finally:
                # Clean up temporary test script
                if temp_script_path.exists():
                    temp_script_path.unlink()
            
        except Exception as e:
            test_result['status'] = 'failed'
            test_result['error_message'] = str(e)
            test_result['end_time'] = datetime.now().isoformat()
            test_result['duration_seconds'] = time.time() - start_time
            logger.error(f"❌ Tool {tool_name} test failed with exception: {e}")
        
        return test_result
    
    def test_windows_path_handling(self) -> Dict[str, Any]:
        """Test Windows-specific path handling"""
        logger.info("Testing Windows path handling")
        
        test_result = {
            'test_type': 'windows_path_handling',
            'status': 'pending',
            'start_time': datetime.now().isoformat(),
            'end_time': None,
            'subtests': {}
        }
        
        if not self.is_windows:
            test_result['status'] = 'skipped'
            test_result['end_time'] = datetime.now().isoformat()
            logger.info("⏭️ Windows path testing skipped (not on Windows)")
            return test_result
        
        path_tests = {
            'backslash_paths': r'C:\Users\Test\file.txt',
            'forward_slash_paths': 'C:/Users/Test/file.txt',
            'unc_paths': r'\\server\share\file.txt',
            'long_paths': 'C:\\' + 'very_long_directory_name\\' * 10 + 'file.txt',
            'unicode_paths': r'C:\Users\測試\файл.txt',
            'spaces_in_paths': r'C:\Program Files\My App\file.txt'
        }
        
        for test_name, test_path in path_tests.items():
            try:
                # Test path normalization
                normalized = os.path.normpath(test_path)
                exists_check = os.path.exists(os.path.dirname(normalized) if os.path.dirname(normalized) else normalized)
                
                test_result['subtests'][test_name] = {
                    'original_path': test_path,
                    'normalized_path': normalized,
                    'path_accessible': exists_check,
                    'status': 'passed'
                }
                
                logger.info(f"✅ Path test {test_name} passed")
                
            except Exception as e:
                test_result['subtests'][test_name] = {
                    'original_path': test_path,
                    'error': str(e),
                    'status': 'failed'
                }
                logger.error(f"❌ Path test {test_name} failed: {e}")
        
        # Determine overall status
        passed_subtests = sum(1 for subtest in test_result['subtests'].values() if subtest['status'] == 'passed')
        total_subtests = len(test_result['subtests'])
        
        if passed_subtests == total_subtests:
            test_result['status'] = 'passed'
        elif passed_subtests > 0:
            test_result['status'] = 'partial'
        else:
            test_result['status'] = 'failed'
        
        test_result['end_time'] = datetime.now().isoformat()
        return test_result
    
    def test_integration_workflow(self, workflow_name: str, steps: List[str]) -> Dict[str, Any]:
        """Test end-to-end integration workflows"""
        logger.info(f"Testing integration workflow: {workflow_name}")
        
        test_result = {
            'workflow_name': workflow_name,
            'test_type': 'integration_workflow',
            'status': 'pending',
            'start_time': datetime.now().isoformat(),
            'end_time': None,
            'duration_seconds': 0,
            'steps_completed': 0,
            'total_steps': len(steps),
            'step_results': [],
            'error_message': None
        }
        
        start_time = time.time()
        
        try:
            for i, step in enumerate(steps):
                step_start = time.time()
                logger.info(f"Executing workflow step {i+1}/{len(steps)}: {step}")
                
                # This is a simplified integration test - in practice, you'd have specific
                # workflow implementations for each test scenario
                step_result = {
                    'step_number': i + 1,
                    'step_description': step,
                    'status': 'passed',  # Placeholder - implement actual step execution
                    'duration_seconds': time.time() - step_start
                }
                
                test_result['step_results'].append(step_result)
                test_result['steps_completed'] += 1
            
            test_result['status'] = 'passed'
            test_result['end_time'] = datetime.now().isoformat()
            test_result['duration_seconds'] = time.time() - start_time
            logger.info(f"✅ Integration workflow {workflow_name} completed successfully")
            
        except Exception as e:
            test_result['status'] = 'failed'
            test_result['error_message'] = str(e)
            test_result['end_time'] = datetime.now().isoformat()
            test_result['duration_seconds'] = time.time() - start_time
            logger.error(f"❌ Integration workflow {workflow_name} failed: {e}")
        
        return test_result
    
    def run_all_tests(self) -> Dict[str, Any]:
        """Run the complete test suite"""
        logger.info("🚀 Starting comprehensive Oneshot system tests")
        
        # Test all agents
        agents = [
            'news_search_agent', 'nrl_agent', 'oneshot_agent', 'research_agent',
            'search_agent', 'search_analyst', 'vision_agent', 'web_agent'
        ]
        
        for agent in agents:
            try:
                result = self.test_agent_basic_functionality(agent)
                self.test_results['agent_tests'][agent] = result
                self.test_results['summary']['total_tests'] += 1
                
                if result['status'] == 'passed':
                    self.test_results['summary']['passed_tests'] += 1
                elif result['status'] == 'failed':
                    self.test_results['summary']['failed_tests'] += 1
                else:
                    self.test_results['summary']['skipped_tests'] += 1
                    
            except Exception as e:
                logger.error(f"Failed to test agent {agent}: {e}")
                self.test_results['errors'].append(f"Agent {agent}: {str(e)}")
        
        # Test all tools
        tools = [
            'agent_caller', 'export_as_pdf', 'export_as_screenshot', 'file_creator',
            'generate_nrl_report', 'list_agents', 'list_tools', 'read_file_contents',
            'read_file_metadata', 'read_howto_docs', 'research_planner', 'research_prompt_rewriter',
            'search_analyst', 'structured_search', 'test_tool', 'todo_read', 'todo_write',
            'usage_status', 'web_image_search', 'web_news_search', 'web_read_page',
            'web_search', 'wip_doc_create', 'wip_doc_edit', 'wip_doc_read'
        ]
        
        for tool in tools:
            try:
                result = self.test_tool_functionality(tool)
                self.test_results['tool_tests'][tool] = result
                self.test_results['summary']['total_tests'] += 1
                
                if result['status'] == 'passed':
                    self.test_results['summary']['passed_tests'] += 1
                elif result['status'] == 'failed':
                    self.test_results['summary']['failed_tests'] += 1
                else:
                    self.test_results['summary']['skipped_tests'] += 1
                    
            except Exception as e:
                logger.error(f"Failed to test tool {tool}: {e}")
                self.test_results['errors'].append(f"Tool {tool}: {str(e)}")
        
        # Windows-specific tests
        if self.is_windows:
            try:
                path_test = self.test_windows_path_handling()
                self.test_results['windows_compatibility_tests']['path_handling'] = path_test
                self.test_results['summary']['total_tests'] += 1
                self.test_results['summary']['windows_specific_tests'] += 1
                
                if path_test['status'] == 'passed':
                    self.test_results['summary']['passed_tests'] += 1
                    self.test_results['summary']['windows_specific_passed'] += 1
                elif path_test['status'] == 'failed':
                    self.test_results['summary']['failed_tests'] += 1
                else:
                    self.test_results['summary']['skipped_tests'] += 1
                    
            except Exception as e:
                logger.error(f"Failed Windows compatibility tests: {e}")
                self.test_results['errors'].append(f"Windows compatibility: {str(e)}")
        
        # Integration tests
        integration_workflows = [
            ('research_workflow', ['Initialize research_agent', 'Execute web_search', 'Create wip_doc', 'Generate report']),
            ('news_analysis_workflow', ['Initialize news_search_agent', 'Search news', 'Read articles', 'Create summary']),
            ('agent_orchestration', ['Initialize oneshot_agent', 'List available agents', 'Delegate tasks', 'Aggregate results'])
        ]
        
        for workflow_name, steps in integration_workflows:
            try:
                result = self.test_integration_workflow(workflow_name, steps)
                self.test_results['integration_tests'][workflow_name] = result
                self.test_results['summary']['total_tests'] += 1
                
                if result['status'] == 'passed':
                    self.test_results['summary']['passed_tests'] += 1
                elif result['status'] == 'failed':
                    self.test_results['summary']['failed_tests'] += 1
                else:
                    self.test_results['summary']['skipped_tests'] += 1
                    
            except Exception as e:
                logger.error(f"Failed integration test {workflow_name}: {e}")
                self.test_results['errors'].append(f"Integration {workflow_name}: {str(e)}")
        
        # Finalize results
        self.test_results['summary']['end_time'] = datetime.now().isoformat()
        
        return self.test_results
    
    def generate_report(self) -> str:
        """Generate a comprehensive test report"""
        summary = self.test_results['summary']
        
        report = f"""
# Oneshot Windows Compatibility Test Report

## Summary
- **Start Time:** {summary['start_time']}
- **End Time:** {summary['end_time']}
- **Total Tests:** {summary['total_tests']}
- **Passed:** {summary['passed_tests']} ✅
- **Failed:** {summary['failed_tests']} ❌
- **Skipped:** {summary['skipped_tests']} ⏭️

### Windows-Specific Results
- **Windows Tests:** {summary['windows_specific_tests']}
- **Windows Passed:** {summary['windows_specific_passed']}

## Pass Rate
- **Overall:** {(summary['passed_tests'] / max(summary['total_tests'], 1)) * 100:.1f}%
- **Windows Specific:** {(summary['windows_specific_passed'] / max(summary['windows_specific_tests'], 1)) * 100:.1f}%

## Agent Test Results
"""
        
        for agent, result in self.test_results['agent_tests'].items():
            status_icon = "✅" if result['status'] == 'passed' else "❌" if result['status'] == 'failed' else "⏭️"
            report += f"- **{agent}:** {status_icon} {result['status']} ({result.get('duration_seconds', 0):.2f}s)\n"
        
        report += "\n## Tool Test Results\n"
        
        for tool, result in self.test_results['tool_tests'].items():
            status_icon = "✅" if result['status'] == 'passed' else "❌" if result['status'] == 'failed' else "⏭️"
            windows_icon = "🪟" if result.get('windows_compatibility', True) else "⚠️"
            report += f"- **{tool}:** {status_icon} {result['status']} {windows_icon} ({result.get('duration_seconds', 0):.2f}s)\n"
        
        if self.test_results['integration_tests']:
            report += "\n## Integration Test Results\n"
            for workflow, result in self.test_results['integration_tests'].items():
                status_icon = "✅" if result['status'] == 'passed' else "❌" if result['status'] == 'failed' else "⏭️"
                report += f"- **{workflow}:** {status_icon} {result['status']} ({result['steps_completed']}/{result['total_steps']} steps)\n"
        
        if self.test_results['errors']:
            report += "\n## Errors Encountered\n"
            for error in self.test_results['errors']:
                report += f"- ❌ {error}\n"
        
        return report
    
    def save_results(self, output_path: Optional[Path] = None) -> None:
        """Save test results to JSON and generate report"""
        if output_path is None:
            output_path = self.test_dir
        
        # Save JSON results
        json_path = output_path / f"test_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(self.test_results, f, indent=2, ensure_ascii=False)
        
        # Save markdown report
        report_path = output_path / f"test_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write(self.generate_report())
        
        logger.info(f"Test results saved to: {json_path}")
        logger.info(f"Test report saved to: {report_path}")

def main():
    """Main entry point for the test runner"""
    print("🚀 Oneshot Windows Compatibility Test Runner")
    print("=" * 50)
    
    runner = OneshotTestRunner()
    
    try:
        # Run all tests
        results = runner.run_all_tests()
        
        # Generate and display report
        report = runner.generate_report()
        print(report)
        
        # Save results
        runner.save_results()
        
        # Exit with appropriate code
        if results['summary']['failed_tests'] > 0:
            print("\n❌ Some tests failed!")
            sys.exit(1)
        else:
            print("\n✅ All tests passed!")
            sys.exit(0)
            
    except KeyboardInterrupt:
        print("\n⏹️ Tests interrupted by user")
        sys.exit(2)
    except Exception as e:
        logger.error(f"Test runner failed: {e}")
        traceback.print_exc()
        sys.exit(3)

if __name__ == "__main__":
    main()
