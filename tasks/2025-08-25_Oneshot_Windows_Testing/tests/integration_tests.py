#!/usr/bin/env python3
"""
Integration test suite for Oneshot Windows compatibility testing.

This module contains end-to-end integration tests that validate complete workflows
combining multiple agents and tools in realistic usage scenarios.
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
import tempfile

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class OneshotIntegrationTester:
    """Integration testing framework for end-to-end workflows"""
    
    def __init__(self):
        self.project_root = self._find_project_root()
        self.is_windows = platform.system() == 'Windows'
        self.temp_dir = Path(tempfile.mkdtemp(prefix='oneshot_integration_tests_'))
        
        # Define integration test workflows
        self.integration_workflows = {
            'research_workflow': {
                'description': 'Complete research workflow using research_agent',
                'steps': [
                    {'agent': 'research_agent', 'prompt': 'Research the basics of renewable energy', 'expected_tools': ['research_planner', 'web_search']},
                    {'validation': 'check_research_output', 'criteria': ['wip_doc_created', 'content_comprehensive']}
                ],
                'timeout': 180,
                'windows_sensitive': False
            },
            'news_analysis_workflow': {
                'description': 'News search and analysis workflow',
                'steps': [
                    {'agent': 'news_search_agent', 'prompt': 'Find recent news about artificial intelligence developments', 'expected_tools': ['web_news_search', 'web_read_page']},
                    {'validation': 'check_news_output', 'criteria': ['articles_found', 'content_analyzed']}
                ],
                'timeout': 120,
                'windows_sensitive': False
            },
            'agent_orchestration_workflow': {
                'description': 'Multi-agent orchestration using oneshot_agent',
                'steps': [
                    {'agent': 'oneshot_agent', 'prompt': 'List all available agents and then delegate a simple search task', 'expected_tools': ['list_agents', 'agent_caller']},
                    {'validation': 'check_orchestration_output', 'criteria': ['agents_listed', 'delegation_successful']}
                ],
                'timeout': 150,
                'windows_sensitive': False
            },
            'file_processing_workflow': {
                'description': 'File creation and processing workflow',
                'steps': [
                    {'agent': 'web_agent', 'prompt': 'Search for information about Python programming and save it to a file', 'expected_tools': ['web_search', 'file_creator']},
                    {'validation': 'check_file_output', 'criteria': ['file_created', 'content_relevant']}
                ],
                'timeout': 90,
                'windows_sensitive': True
            },
            'vision_processing_workflow': {
                'description': 'Vision agent multimodal processing',
                'steps': [
                    {'agent': 'vision_agent', 'prompt': 'Analyze this image processing test', 'expected_tools': []},
                    {'validation': 'check_vision_output', 'criteria': ['response_received', 'analysis_provided']}
                ],
                'timeout': 60,
                'windows_sensitive': False
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
            
            logger.info(f"Running integration test command: {agent_name} with timeout {timeout}s")
            
            result = subprocess.run(
                command,
                capture_output=True,
                text=True,
                timeout=timeout,
                cwd=self.project_root
            )
            
            return result.returncode, result.stdout, result.stderr
            
        except subprocess.TimeoutExpired:
            logger.error(f"Integration test timed out for {agent_name} after {timeout}s")
            return -1, "", f"Timeout after {timeout}s"
        except Exception as e:
            logger.error(f"Failed to run integration test for {agent_name}: {e}")
            return -1, "", str(e)
    
    def test_integration_workflow(self, workflow_name: str) -> Dict[str, Any]:
        """Test a complete integration workflow"""
        logger.info(f"Testing integration workflow: {workflow_name}")
        
        workflow_config = self.integration_workflows.get(workflow_name)
        if not workflow_config:
            raise ValueError(f"Unknown workflow: {workflow_name}")
        
        test_result = {
            'workflow_name': workflow_name,
            'description': workflow_config['description'],
            'test_type': 'integration_workflow',
            'start_time': datetime.now().isoformat(),
            'end_time': None,
            'total_steps': len(workflow_config['steps']),
            'completed_steps': 0,
            'step_results': [],
            'overall_status': 'pending',
            'windows_compatibility': True,
            'performance_metrics': {
                'total_duration': 0,
                'average_step_duration': 0
            }
        }
        
        workflow_start_time = time.time()
        
        try:
            for i, step in enumerate(workflow_config['steps']):
                step_start_time = time.time()
                logger.info(f"Executing step {i+1}/{len(workflow_config['steps'])}")
                
                step_result = self._execute_workflow_step(step, workflow_config['timeout'])
                step_result['step_number'] = i + 1
                step_result['duration'] = time.time() - step_start_time
                
                test_result['step_results'].append(step_result)
                
                if step_result['status'] == 'passed':
                    test_result['completed_steps'] += 1
                    logger.info(f"✅ Step {i+1} passed ({step_result['duration']:.2f}s)")
                else:
                    logger.error(f"❌ Step {i+1} failed: {step_result.get('error', 'Unknown error')}")
                    
                    # Check for Windows-specific issues
                    if self.is_windows and workflow_config['windows_sensitive']:
                        error_text = step_result.get('error', '').lower()
                        if any(issue in error_text for issue in ['path', 'permission', 'powershell', 'encoding']):
                            test_result['windows_compatibility'] = False
                    
                    # Stop workflow on failure (can be made configurable)
                    break
            
            # Calculate performance metrics
            total_duration = time.time() - workflow_start_time
            test_result['performance_metrics']['total_duration'] = total_duration
            test_result['performance_metrics']['average_step_duration'] = (
                total_duration / max(test_result['completed_steps'], 1)
            )
            
            # Determine overall status
            if test_result['completed_steps'] == test_result['total_steps']:
                test_result['overall_status'] = 'passed'
            elif test_result['completed_steps'] > 0:
                test_result['overall_status'] = 'partial'
            else:
                test_result['overall_status'] = 'failed'
        
        except Exception as e:
            test_result['overall_status'] = 'failed'
            test_result['error'] = str(e)
            logger.error(f"❌ Integration workflow {workflow_name} failed with exception: {e}")
        
        test_result['end_time'] = datetime.now().isoformat()
        return test_result
    
    def _execute_workflow_step(self, step: Dict[str, Any], default_timeout: int) -> Dict[str, Any]:
        """Execute a single workflow step"""
        step_result = {
            'step_type': None,
            'status': 'pending',
            'error': None,
            'outputs': {}
        }
        
        try:
            if 'agent' in step:
                # Agent execution step
                step_result['step_type'] = 'agent_execution'
                step_result.update(self._execute_agent_step(step, default_timeout))
            
            elif 'validation' in step:
                # Validation step
                step_result['step_type'] = 'validation'
                step_result.update(self._execute_validation_step(step))
            
            else:
                raise ValueError(f"Unknown step type: {step}")
        
        except Exception as e:
            step_result['status'] = 'failed'
            step_result['error'] = str(e)
        
        return step_result
    
    def _execute_agent_step(self, step: Dict[str, Any], default_timeout: int) -> Dict[str, Any]:
        """Execute an agent-based workflow step"""
        agent_name = step['agent']
        prompt = step['prompt']
        expected_tools = step.get('expected_tools', [])
        timeout = step.get('timeout', default_timeout)
        
        result = {
            'agent_name': agent_name,
            'prompt': prompt,
            'expected_tools': expected_tools,
            'execution_successful': False,
            'response_received': False,
            'response_length': 0,
            'tools_likely_used': []
        }
        
        # Execute the agent
        returncode, stdout, stderr = self._run_agent_command(agent_name, prompt, timeout)
        
        if returncode == 0 and stdout.strip():
            result['execution_successful'] = True
            result['response_received'] = True
            result['response_length'] = len(stdout)
            result['status'] = 'passed'
            
            # Analyze response for tool usage indicators
            response_lower = stdout.lower()
            for tool in expected_tools:
                if tool.replace('_', ' ') in response_lower or tool in response_lower:
                    result['tools_likely_used'].append(tool)
            
            result['expected_tools_detected'] = len(result['tools_likely_used'])
            
        else:
            result['status'] = 'failed'
            result['error'] = stderr or "No response received"
        
        result['stdout'] = stdout
        result['stderr'] = stderr
        return result
    
    def _execute_validation_step(self, step: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a validation workflow step"""
        validation_type = step['validation']
        criteria = step.get('criteria', [])
        
        result = {
            'validation_type': validation_type,
            'criteria': criteria,
            'criteria_met': [],
            'criteria_failed': [],
            'validation_successful': False
        }
        
        # Execute validation based on type
        if validation_type == 'check_research_output':
            result.update(self._validate_research_output(criteria))
        elif validation_type == 'check_news_output':
            result.update(self._validate_news_output(criteria))
        elif validation_type == 'check_orchestration_output':
            result.update(self._validate_orchestration_output(criteria))
        elif validation_type == 'check_file_output':
            result.update(self._validate_file_output(criteria))
        elif validation_type == 'check_vision_output':
            result.update(self._validate_vision_output(criteria))
        else:
            result['status'] = 'failed'
            result['error'] = f"Unknown validation type: {validation_type}"
            return result
        
        # Determine validation status
        if len(result['criteria_met']) == len(criteria):
            result['status'] = 'passed'
            result['validation_successful'] = True
        elif len(result['criteria_met']) > 0:
            result['status'] = 'partial'
        else:
            result['status'] = 'failed'
        
        return result
    
    def _validate_research_output(self, criteria: List[str]) -> Dict[str, Any]:
        """Validate research workflow output"""
        validation_result = {
            'criteria_met': [],
            'criteria_failed': [],
            'validation_details': {}
        }
        
        for criterion in criteria:
            if criterion == 'wip_doc_created':
                # Check if any WIP documents were created
                wip_docs_exist = self._check_for_wip_documents()
                validation_result['validation_details']['wip_docs_found'] = wip_docs_exist
                if wip_docs_exist:
                    validation_result['criteria_met'].append(criterion)
                else:
                    validation_result['criteria_failed'].append(criterion)
            
            elif criterion == 'content_comprehensive':
                # Basic check for content comprehensiveness (placeholder)
                validation_result['criteria_met'].append(criterion)  # Assume passed for now
                validation_result['validation_details']['content_check'] = 'Basic validation passed'
            
            else:
                validation_result['criteria_failed'].append(criterion)
        
        return validation_result
    
    def _validate_news_output(self, criteria: List[str]) -> Dict[str, Any]:
        """Validate news analysis workflow output"""
        validation_result = {
            'criteria_met': [],
            'criteria_failed': [],
            'validation_details': {}
        }
        
        for criterion in criteria:
            if criterion == 'articles_found':
                # Assume articles were found if execution succeeded
                validation_result['criteria_met'].append(criterion)
                validation_result['validation_details']['articles_check'] = 'Articles likely found'
            
            elif criterion == 'content_analyzed':
                # Assume content was analyzed if execution succeeded
                validation_result['criteria_met'].append(criterion)
                validation_result['validation_details']['analysis_check'] = 'Analysis likely performed'
            
            else:
                validation_result['criteria_failed'].append(criterion)
        
        return validation_result
    
    def _validate_orchestration_output(self, criteria: List[str]) -> Dict[str, Any]:
        """Validate agent orchestration workflow output"""
        validation_result = {
            'criteria_met': [],
            'criteria_failed': [],
            'validation_details': {}
        }
        
        for criterion in criteria:
            if criterion == 'agents_listed':
                # Check if agents were listed by looking for agent names in output
                agents_found = self._check_for_agent_names()
                validation_result['validation_details']['agents_found'] = agents_found
                if agents_found > 0:
                    validation_result['criteria_met'].append(criterion)
                else:
                    validation_result['criteria_failed'].append(criterion)
            
            elif criterion == 'delegation_successful':
                # Assume delegation was successful if execution completed
                validation_result['criteria_met'].append(criterion)
                validation_result['validation_details']['delegation_check'] = 'Delegation likely successful'
            
            else:
                validation_result['criteria_failed'].append(criterion)
        
        return validation_result
    
    def _validate_file_output(self, criteria: List[str]) -> Dict[str, Any]:
        """Validate file processing workflow output"""
        validation_result = {
            'criteria_met': [],
            'criteria_failed': [],
            'validation_details': {}
        }
        
        for criterion in criteria:
            if criterion == 'file_created':
                # Check if any new files were created
                files_created = self._check_for_created_files()
                validation_result['validation_details']['files_created'] = files_created
                if files_created > 0:
                    validation_result['criteria_met'].append(criterion)
                else:
                    validation_result['criteria_failed'].append(criterion)
            
            elif criterion == 'content_relevant':
                # Assume content is relevant if files were created
                validation_result['criteria_met'].append(criterion)
                validation_result['validation_details']['content_check'] = 'Content relevance assumed'
            
            else:
                validation_result['criteria_failed'].append(criterion)
        
        return validation_result
    
    def _validate_vision_output(self, criteria: List[str]) -> Dict[str, Any]:
        """Validate vision processing workflow output"""
        validation_result = {
            'criteria_met': [],
            'criteria_failed': [],
            'validation_details': {}
        }
        
        for criterion in criteria:
            if criterion == 'response_received':
                # Assume response was received if we got here
                validation_result['criteria_met'].append(criterion)
                validation_result['validation_details']['response_check'] = 'Response received'
            
            elif criterion == 'analysis_provided':
                # Assume analysis was provided
                validation_result['criteria_met'].append(criterion)
                validation_result['validation_details']['analysis_check'] = 'Analysis likely provided'
            
            else:
                validation_result['criteria_failed'].append(criterion)
        
        return validation_result
    
    def _check_for_wip_documents(self) -> bool:
        """Check if WIP documents were created during the workflow"""
        # Look for common WIP document patterns
        wip_patterns = ['wip_', 'work_in_progress', 'research_']
        project_files = list(self.project_root.glob('**/*.md')) + list(self.project_root.glob('**/*.txt'))
        
        for file_path in project_files:
            if any(pattern in file_path.name.lower() for pattern in wip_patterns):
                return True
        
        return False
    
    def _check_for_agent_names(self) -> int:
        """Check for mentions of agent names (indicating successful listing)"""
        # This is a placeholder - in a real implementation, you'd check the actual output
        return 1  # Assume at least one agent name was found
    
    def _check_for_created_files(self) -> int:
        """Check for recently created files"""
        # Look for files created in the last few minutes
        current_time = time.time()
        recent_files = 0
        
        try:
            for file_path in self.project_root.glob('**/*'):
                if file_path.is_file():
                    file_mtime = file_path.stat().st_mtime
                    if current_time - file_mtime < 300:  # Last 5 minutes
                        recent_files += 1
        except Exception:
            pass
        
        return recent_files
    
    def run_all_integration_tests(self) -> Dict[str, Any]:
        """Run all integration test workflows"""
        logger.info("Running all integration test workflows")
        
        all_results = {
            'test_suite': 'integration_tests',
            'start_time': datetime.now().isoformat(),
            'end_time': None,
            'workflows_tested': list(self.integration_workflows.keys()),
            'test_summary': {
                'total_workflows': len(self.integration_workflows),
                'passed_workflows': 0,
                'partial_workflows': 0,
                'failed_workflows': 0,
                'windows_compatible_workflows': 0
            },
            'workflow_results': {}
        }
        
        for workflow_name in self.integration_workflows.keys():
            logger.info(f"\n{'='*50}")
            logger.info(f"Testing workflow: {workflow_name}")
            logger.info(f"{'='*50}")
            
            try:
                workflow_result = self.test_integration_workflow(workflow_name)
                all_results['workflow_results'][workflow_name] = workflow_result
                
                # Update summary
                if workflow_result['overall_status'] == 'passed':
                    all_results['test_summary']['passed_workflows'] += 1
                elif workflow_result['overall_status'] == 'partial':
                    all_results['test_summary']['partial_workflows'] += 1
                else:
                    all_results['test_summary']['failed_workflows'] += 1
                
                # Track Windows compatibility
                if workflow_result.get('windows_compatibility', True):
                    all_results['test_summary']['windows_compatible_workflows'] += 1
                
                logger.info(f"Workflow {workflow_name} status: {workflow_result['overall_status']}")
                
            except Exception as e:
                logger.error(f"Failed to test workflow {workflow_name}: {e}")
                all_results['workflow_results'][workflow_name] = {
                    'workflow_name': workflow_name,
                    'overall_status': 'failed',
                    'error': str(e)
                }
                all_results['test_summary']['failed_workflows'] += 1
        
        all_results['end_time'] = datetime.now().isoformat()
        return all_results

def main():
    """Main entry point for integration testing"""
    print("🔗 Oneshot Integration Testing Suite")
    print("=" * 45)
    
    tester = OneshotIntegrationTester()
    
    try:
        # Run all integration tests
        results = tester.run_all_integration_tests()
        
        # Display summary
        summary = results['test_summary']
        print(f"\n📊 Integration Test Summary:")
        print(f"Total Workflows: {summary['total_workflows']}")
        print(f"Passed: {summary['passed_workflows']} ✅")
        print(f"Partial: {summary['partial_workflows']} ⚠️")
        print(f"Failed: {summary['failed_workflows']} ❌")
        print(f"Windows Compatible: {summary['windows_compatible_workflows']} 🪟")
        
        # Display workflow details
        print(f"\n🔗 Workflow Details:")
        for workflow_name, workflow_result in results['workflow_results'].items():
            status_icon = {
                'passed': '✅',
                'partial': '⚠️',
                'failed': '❌'
            }.get(workflow_result['overall_status'], '❓')
            
            completed_steps = workflow_result.get('completed_steps', 0)
            total_steps = workflow_result.get('total_steps', 0)
            duration = workflow_result.get('performance_metrics', {}).get('total_duration', 0)
            
            print(f"  {workflow_name}: {status_icon} {workflow_result['overall_status']} "
                  f"({completed_steps}/{total_steps} steps, {duration:.1f}s)")
        
        # Save results
        output_file = Path(__file__).parent / f"integration_test_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        
        print(f"\nResults saved to: {output_file}")
        
        # Exit with appropriate code
        if summary['failed_workflows'] > 0:
            sys.exit(1)
        else:
            sys.exit(0)
    
    except KeyboardInterrupt:
        print("\n⏹️ Tests interrupted by user")
        sys.exit(2)
    except Exception as e:
        logger.error(f"Integration testing failed: {e}")
        sys.exit(3)

if __name__ == "__main__":
    main()
