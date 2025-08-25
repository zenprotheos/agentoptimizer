#!/usr/bin/env python3
"""
Agent-specific test suite for Oneshot Windows compatibility testing.

This module contains comprehensive tests for all 8 agents in the Oneshot system,
validating their functionality, Windows compatibility, and error handling.
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
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class OneshotAgentTester:
    """Comprehensive agent testing framework"""
    
    def __init__(self):
        self.project_root = self._find_project_root()
        self.is_windows = platform.system() == 'Windows'
        self.test_results = {}
        
        # Agent configurations with specific test scenarios
        self.agent_configs = {
            'news_search_agent': {
                'test_prompts': [
                    'Search for recent news about artificial intelligence',
                    'Find news about climate change from the last week',
                ],
                'expected_tools': ['web_news_search', 'web_read_page', 'file_creator', 'read_file_contents'],
                'timeout': 90
            },
            'nrl_agent': {
                'test_prompts': [
                    'Generate a sample NRL match report',
                ],
                'expected_tools': ['generate_nrl_report', 'web_news_search', 'web_read_page'],
                'timeout': 60
            },
            'oneshot_agent': {
                'test_prompts': [
                    'List available agents in the system',
                    'Coordinate a simple task using multiple agents',
                ],
                'expected_tools': ['list_agents', 'agent_caller', 'read_file_metadata', 'read_file_contents', 'file_creator'],
                'timeout': 120
            },
            'research_agent': {
                'test_prompts': [
                    'Research the basics of machine learning',
                    'Create a research plan for studying renewable energy',
                ],
                'expected_tools': ['research_planner', 'web_search', 'web_read_page', 'wip_doc_create', 'wip_doc_edit'],
                'timeout': 120
            },
            'search_agent': {
                'test_prompts': [
                    'Search for information about Python programming',
                    'Find recent articles about space exploration',
                ],
                'expected_tools': ['web_search', 'web_read_page'],
                'timeout': 60
            },
            'search_analyst': {
                'test_prompts': [
                    'Analyze search trends for electric vehicles',
                    'Research market data for renewable energy',
                ],
                'expected_tools': ['web_search', 'web_read_page', 'web_news_search', 'web_image_search', 'wip_doc_create'],
                'timeout': 90
            },
            'vision_agent': {
                'test_prompts': [
                    'Analyze this test: Vision agent functionality test',
                ],
                'expected_tools': [],  # Vision agent uses no tools currently
                'timeout': 45,
                'special_requirements': 'multimodal'
            },
            'web_agent': {
                'test_prompts': [
                    'Search the web for information about Python',
                    'Read a webpage and summarize its content',
                ],
                'expected_tools': ['structured_search', 'web_search', 'web_read_page'],
                'timeout': 75
            }
        }
    
    def _find_project_root(self) -> Path:
        """Find the Oneshot project root directory"""
        current = Path(__file__).parent
        while current.parent != current:
            if (current / 'oneshot.py').exists() or (current / 'app').exists():
                return current
            current = current.parent
        return Path.cwd()
    
    def _run_agent_command(self, agent_name: str, prompt: str, timeout: int = 60) -> Tuple[int, str, str]:
        """Run an agent command with proper Windows handling"""
        try:
            if self.is_windows:
                # Use PowerShell for better Windows compatibility
                command = [
                    'powershell', '-NoProfile', '-ExecutionPolicy', 'Bypass', '-Command',
                    f'python app/agent_runner.py {agent_name} "{prompt}"'
                ]
            else:
                command = ['python', 'app/agent_runner.py', agent_name, prompt]
            
            logger.info(f"Running: {' '.join(command)}")
            
            result = subprocess.run(
                command,
                capture_output=True,
                text=True,
                timeout=timeout,
                cwd=self.project_root
            )
            
            return result.returncode, result.stdout, result.stderr
            
        except subprocess.TimeoutExpired:
            logger.error(f"Agent {agent_name} timed out after {timeout}s")
            return -1, "", f"Timeout after {timeout}s"
        except Exception as e:
            logger.error(f"Failed to run agent {agent_name}: {e}")
            return -1, "", str(e)
    
    def test_agent_basic_functionality(self, agent_name: str) -> Dict[str, Any]:
        """Test basic agent functionality with multiple prompts"""
        logger.info(f"Testing basic functionality for {agent_name}")
        
        config = self.agent_configs.get(agent_name, {})
        test_prompts = config.get('test_prompts', ['Hello, this is a test'])
        timeout = config.get('timeout', 60)
        
        test_result = {
            'agent_name': agent_name,
            'test_type': 'basic_functionality',
            'start_time': datetime.now().isoformat(),
            'end_time': None,
            'total_prompts': len(test_prompts),
            'successful_prompts': 0,
            'failed_prompts': 0,
            'prompt_results': [],
            'overall_status': 'pending',
            'windows_compatible': True,
            'error_summary': []
        }
        
        for i, prompt in enumerate(test_prompts):
            logger.info(f"Testing prompt {i+1}/{len(test_prompts)}: {prompt[:50]}...")
            
            prompt_start = time.time()
            returncode, stdout, stderr = self._run_agent_command(agent_name, prompt, timeout)
            prompt_duration = time.time() - prompt_start
            
            prompt_result = {
                'prompt_number': i + 1,
                'prompt': prompt,
                'duration_seconds': prompt_duration,
                'returncode': returncode,
                'response_length': len(stdout) if stdout else 0,
                'has_response': bool(stdout and stdout.strip()),
                'status': 'passed' if returncode == 0 and stdout.strip() else 'failed',
                'error_message': stderr if stderr else None,
                'windows_issues': []
            }
            
            # Check for Windows-specific issues
            if self.is_windows and stderr:
                error_lower = stderr.lower()
                windows_indicators = ['path', 'permission', 'powershell', 'encoding', 'drive', 'access denied']
                for indicator in windows_indicators:
                    if indicator in error_lower:
                        prompt_result['windows_issues'].append(f"Windows-specific issue detected: {indicator}")
                        test_result['windows_compatible'] = False
            
            test_result['prompt_results'].append(prompt_result)
            
            if prompt_result['status'] == 'passed':
                test_result['successful_prompts'] += 1
                logger.info(f"✅ Prompt {i+1} passed ({prompt_duration:.2f}s)")
            else:
                test_result['failed_prompts'] += 1
                test_result['error_summary'].append(f"Prompt {i+1}: {stderr or 'No response'}")
                logger.error(f"❌ Prompt {i+1} failed: {stderr or 'No response'}")
        
        # Determine overall status
        if test_result['successful_prompts'] == test_result['total_prompts']:
            test_result['overall_status'] = 'passed'
        elif test_result['successful_prompts'] > 0:
            test_result['overall_status'] = 'partial'
        else:
            test_result['overall_status'] = 'failed'
        
        test_result['end_time'] = datetime.now().isoformat()
        return test_result
    
    def test_agent_tool_integration(self, agent_name: str) -> Dict[str, Any]:
        """Test agent's integration with its expected tools"""
        logger.info(f"Testing tool integration for {agent_name}")
        
        config = self.agent_configs.get(agent_name, {})
        expected_tools = config.get('expected_tools', [])
        
        test_result = {
            'agent_name': agent_name,
            'test_type': 'tool_integration',
            'start_time': datetime.now().isoformat(),
            'end_time': None,
            'expected_tools': expected_tools,
            'tools_available': [],
            'tools_missing': [],
            'tool_accessibility': {},
            'overall_status': 'pending'
        }
        
        # Check if expected tools exist and are accessible
        for tool_name in expected_tools:
            tool_path = self.project_root / 'tools' / f'{tool_name}.py'
            is_available = tool_path.exists()
            
            test_result['tool_accessibility'][tool_name] = {
                'exists': is_available,
                'path': str(tool_path),
                'accessible': False
            }
            
            if is_available:
                test_result['tools_available'].append(tool_name)
                
                # Try to import the tool to verify accessibility
                try:
                    import importlib.util
                    spec = importlib.util.spec_from_file_location(tool_name, tool_path)
                    module = importlib.util.module_from_spec(spec)
                    spec.loader.exec_module(module)
                    test_result['tool_accessibility'][tool_name]['accessible'] = True
                    logger.info(f"✅ Tool {tool_name} is accessible")
                except Exception as e:
                    logger.error(f"❌ Tool {tool_name} import failed: {e}")
                    test_result['tool_accessibility'][tool_name]['import_error'] = str(e)
            else:
                test_result['tools_missing'].append(tool_name)
                logger.warning(f"⚠️ Tool {tool_name} not found at {tool_path}")
        
        # Determine overall status
        available_count = len(test_result['tools_available'])
        total_expected = len(expected_tools)
        
        if available_count == total_expected:
            test_result['overall_status'] = 'passed'
        elif available_count > 0:
            test_result['overall_status'] = 'partial'
        else:
            test_result['overall_status'] = 'failed'
        
        test_result['end_time'] = datetime.now().isoformat()
        return test_result
    
    def test_agent_error_handling(self, agent_name: str) -> Dict[str, Any]:
        """Test agent's error handling capabilities"""
        logger.info(f"Testing error handling for {agent_name}")
        
        test_result = {
            'agent_name': agent_name,
            'test_type': 'error_handling',
            'start_time': datetime.now().isoformat(),
            'end_time': None,
            'error_scenarios': [],
            'graceful_failures': 0,
            'harsh_failures': 0,
            'overall_status': 'pending'
        }
        
        # Test various error scenarios
        error_scenarios = [
            ('empty_prompt', ''),
            ('very_long_prompt', 'x' * 10000),
            ('invalid_characters', '\\invalid\\path\\with\\special\\chars\\<>|'),
            ('null_prompt', None),
        ]
        
        for scenario_name, prompt in error_scenarios:
            logger.info(f"Testing error scenario: {scenario_name}")
            
            try:
                # Convert None to empty string for subprocess
                test_prompt = prompt if prompt is not None else ''
                
                returncode, stdout, stderr = self._run_agent_command(
                    agent_name, test_prompt, timeout=30
                )
                
                scenario_result = {
                    'scenario': scenario_name,
                    'prompt': prompt,
                    'returncode': returncode,
                    'has_error_message': bool(stderr),
                    'graceful_failure': returncode != 0 and bool(stderr),
                    'harsh_failure': returncode != 0 and not stderr,
                    'response_provided': bool(stdout and stdout.strip())
                }
                
                if scenario_result['graceful_failure']:
                    test_result['graceful_failures'] += 1
                    logger.info(f"✅ Graceful failure for {scenario_name}")
                elif scenario_result['harsh_failure']:
                    test_result['harsh_failures'] += 1
                    logger.warning(f"⚠️ Harsh failure for {scenario_name}")
                else:
                    logger.info(f"✅ Handled {scenario_name} appropriately")
                
                test_result['error_scenarios'].append(scenario_result)
                
            except Exception as e:
                logger.error(f"❌ Error testing scenario {scenario_name}: {e}")
                test_result['error_scenarios'].append({
                    'scenario': scenario_name,
                    'prompt': prompt,
                    'exception': str(e),
                    'harsh_failure': True
                })
                test_result['harsh_failures'] += 1
        
        # Determine overall status
        total_scenarios = len(test_result['error_scenarios'])
        if test_result['harsh_failures'] == 0:
            test_result['overall_status'] = 'passed'
        elif test_result['graceful_failures'] > test_result['harsh_failures']:
            test_result['overall_status'] = 'partial'
        else:
            test_result['overall_status'] = 'failed'
        
        test_result['end_time'] = datetime.now().isoformat()
        return test_result
    
    def test_agent_windows_compatibility(self, agent_name: str) -> Dict[str, Any]:
        """Test Windows-specific compatibility for the agent"""
        logger.info(f"Testing Windows compatibility for {agent_name}")
        
        test_result = {
            'agent_name': agent_name,
            'test_type': 'windows_compatibility',
            'start_time': datetime.now().isoformat(),
            'end_time': None,
            'is_windows': self.is_windows,
            'compatibility_tests': {},
            'overall_status': 'pending'
        }
        
        if not self.is_windows:
            test_result['overall_status'] = 'skipped'
            test_result['end_time'] = datetime.now().isoformat()
            logger.info("⏭️ Windows compatibility test skipped (not on Windows)")
            return test_result
        
        # Windows-specific test scenarios
        windows_tests = {
            'powershell_execution': 'Test PowerShell command execution compatibility',
            'path_handling': 'Test with Windows-style paths: C:\\Users\\Test\\file.txt',
            'environment_variables': 'Test environment variable: %USERPROFILE%',
            'unicode_support': 'Test Unicode: 測試 файл тест',
            'long_paths': 'Test long path: ' + 'C:\\' + 'very_long_directory_name\\' * 5 + 'test.txt'
        }
        
        for test_name, test_prompt in windows_tests.items():
            logger.info(f"Running Windows test: {test_name}")
            
            try:
                returncode, stdout, stderr = self._run_agent_command(
                    agent_name, test_prompt, timeout=45
                )
                
                test_result['compatibility_tests'][test_name] = {
                    'prompt': test_prompt,
                    'returncode': returncode,
                    'success': returncode == 0,
                    'has_output': bool(stdout and stdout.strip()),
                    'error_message': stderr if stderr else None,
                    'windows_specific_error': self._detect_windows_error(stderr) if stderr else False
                }
                
                if returncode == 0:
                    logger.info(f"✅ Windows test {test_name} passed")
                else:
                    logger.error(f"❌ Windows test {test_name} failed: {stderr}")
                    
            except Exception as e:
                logger.error(f"❌ Windows test {test_name} exception: {e}")
                test_result['compatibility_tests'][test_name] = {
                    'prompt': test_prompt,
                    'exception': str(e),
                    'success': False,
                    'windows_specific_error': True
                }
        
        # Determine overall status
        successful_tests = sum(1 for test in test_result['compatibility_tests'].values() if test.get('success', False))
        total_tests = len(test_result['compatibility_tests'])
        
        if successful_tests == total_tests:
            test_result['overall_status'] = 'passed'
        elif successful_tests > total_tests // 2:
            test_result['overall_status'] = 'partial'
        else:
            test_result['overall_status'] = 'failed'
        
        test_result['end_time'] = datetime.now().isoformat()
        return test_result
    
    def _detect_windows_error(self, error_message: str) -> bool:
        """Detect if an error message indicates Windows-specific issues"""
        if not error_message:
            return False
        
        error_lower = error_message.lower()
        windows_indicators = [
            'access denied', 'permission denied', 'path not found',
            'invalid path', 'powershell', 'execution policy',
            'drive not found', 'unc path', 'long path'
        ]
        
        return any(indicator in error_lower for indicator in windows_indicators)
    
    def run_comprehensive_agent_tests(self, agent_names: Optional[List[str]] = None) -> Dict[str, Any]:
        """Run comprehensive tests for specified agents or all agents"""
        if agent_names is None:
            agent_names = list(self.agent_configs.keys())
        
        logger.info(f"Running comprehensive tests for agents: {agent_names}")
        
        all_results = {
            'test_suite': 'comprehensive_agent_tests',
            'start_time': datetime.now().isoformat(),
            'end_time': None,
            'agents_tested': agent_names,
            'test_summary': {
                'total_agents': len(agent_names),
                'passed_agents': 0,
                'partial_agents': 0,
                'failed_agents': 0
            },
            'agent_results': {}
        }
        
        for agent_name in agent_names:
            logger.info(f"\n{'='*50}")
            logger.info(f"Testing agent: {agent_name}")
            logger.info(f"{'='*50}")
            
            agent_results = {
                'agent_name': agent_name,
                'basic_functionality': None,
                'tool_integration': None,
                'error_handling': None,
                'windows_compatibility': None,
                'overall_status': 'pending'
            }
            
            try:
                # Run all test types for this agent
                agent_results['basic_functionality'] = self.test_agent_basic_functionality(agent_name)
                agent_results['tool_integration'] = self.test_agent_tool_integration(agent_name)
                agent_results['error_handling'] = self.test_agent_error_handling(agent_name)
                agent_results['windows_compatibility'] = self.test_agent_windows_compatibility(agent_name)
                
                # Determine overall status for the agent
                test_statuses = [
                    agent_results['basic_functionality']['overall_status'],
                    agent_results['tool_integration']['overall_status'],
                    agent_results['error_handling']['overall_status'],
                    agent_results['windows_compatibility']['overall_status']
                ]
                
                # Filter out 'skipped' status for overall calculation
                relevant_statuses = [s for s in test_statuses if s != 'skipped']
                
                if all(s == 'passed' for s in relevant_statuses):
                    agent_results['overall_status'] = 'passed'
                    all_results['test_summary']['passed_agents'] += 1
                elif any(s == 'passed' for s in relevant_statuses):
                    agent_results['overall_status'] = 'partial'
                    all_results['test_summary']['partial_agents'] += 1
                else:
                    agent_results['overall_status'] = 'failed'
                    all_results['test_summary']['failed_agents'] += 1
                
                logger.info(f"Agent {agent_name} overall status: {agent_results['overall_status']}")
                
            except Exception as e:
                logger.error(f"Failed to test agent {agent_name}: {e}")
                agent_results['overall_status'] = 'failed'
                agent_results['error'] = str(e)
                all_results['test_summary']['failed_agents'] += 1
            
            all_results['agent_results'][agent_name] = agent_results
        
        all_results['end_time'] = datetime.now().isoformat()
        return all_results

def main():
    """Main entry point for agent testing"""
    print("🤖 Oneshot Agent Testing Suite")
    print("=" * 40)
    
    tester = OneshotAgentTester()
    
    try:
        # Run comprehensive tests for all agents
        results = tester.run_comprehensive_agent_tests()
        
        # Display summary
        summary = results['test_summary']
        print(f"\n📊 Test Summary:")
        print(f"Total Agents: {summary['total_agents']}")
        print(f"Passed: {summary['passed_agents']} ✅")
        print(f"Partial: {summary['partial_agents']} ⚠️")
        print(f"Failed: {summary['failed_agents']} ❌")
        
        # Save results
        output_file = Path(__file__).parent / f"agent_test_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        
        print(f"\nResults saved to: {output_file}")
        
        # Exit with appropriate code
        if summary['failed_agents'] > 0:
            sys.exit(1)
        else:
            sys.exit(0)
            
    except KeyboardInterrupt:
        print("\n⏹️ Tests interrupted by user")
        sys.exit(2)
    except Exception as e:
        logger.error(f"Agent testing failed: {e}")
        sys.exit(3)

if __name__ == "__main__":
    main()
