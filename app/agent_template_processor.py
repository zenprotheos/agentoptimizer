#!/usr/bin/env python3
"""
Agent Template Processor - Handles agent template processing and file content injection
"""

import yaml
from pathlib import Path
from typing import Dict, Any, List, Tuple, Optional
from jinja2 import Environment, FileSystemLoader, TemplateNotFound, TemplateSyntaxError

from .agent_errors import TemplateProcessingError, YAMLFrontmatterError, AgentFileFormatError
from .agent_validation import validate_template_includes


class AgentTemplateProcessor:
    """
    Handles agent template processing, including:
    - Jinja2 template rendering
    - File content injection
    - Template context preparation
    - System prompt assembly
    """
    
    def __init__(self, project_root: Path, template_config: Dict[str, Any], tool_services):
        self.project_root = project_root
        self.template_config = template_config
        self.tool_services = tool_services
        self.enable_async = template_config.get('enable_async', False)
        self._setup_jinja_environment()
    
    def _setup_jinja_environment(self):
        """Setup Jinja2 environment for template rendering"""
        base_path = self.project_root / self.template_config.get('base_path', 'snippets')
        
        self.jinja_env = Environment(
            loader=FileSystemLoader([
                str(base_path),  # Primary snippets directory
                '/',  # Allow absolute paths
            ]),
            autoescape=self.template_config.get('autoescape', False),
            enable_async=self.enable_async
        )
        
        print(f"Template engine initialized with base path: {base_path}")
    
    async def process_agent_template(
        self, 
        agent_file: Path, 
        files: List[str] = None,
        additional_context: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """
        Complete template processing pipeline:
        1. Parse agent markdown file
        2. Extract YAML frontmatter and system prompt
        3. Process provided files into template context
        4. Render system prompt with full context
        5. Return processed configuration
        """
        # Parse agent file
        config_data, raw_system_prompt = self._parse_agent_file(agent_file)
        
        # Process files into template context
        file_context = self._process_files_context(files) if files else {}
        
        # Combine with additional context
        template_context = {**file_context}
        if additional_context:
            template_context.update(additional_context)
        
        # Render system prompt with full context
        rendered_system_prompt = await self._render_system_prompt(raw_system_prompt, template_context)
        
        # Add rendered system prompt to config
        config_data['system_prompt'] = rendered_system_prompt
        
        return {
            'config_data': config_data,
            'system_prompt': rendered_system_prompt,
            'file_context': file_context,
            'template_strategy': self._detect_template_strategy(raw_system_prompt)
        }
    
    def _parse_agent_file(self, agent_file: Path) -> Tuple[Dict[str, Any], str]:
        """Extract YAML frontmatter and raw system prompt with enhanced error handling"""
        try:
            content = agent_file.read_text(encoding='utf-8')
        except UnicodeDecodeError as e:
            raise AgentFileFormatError(
                f"File encoding error: {e}. Ensure file is saved as UTF-8.",
                agent_file
            )
        except FileNotFoundError:
            raise AgentFileFormatError(f"Agent file not found: {agent_file}", agent_file)
        
        # Check for frontmatter delimiters
        if not content.startswith('---'):
            raise AgentFileFormatError(
                "Agent file must start with YAML frontmatter delimiter '---'",
                agent_file
            )
        
        # Split on --- delimiters
        parts = content.split('---', 2)
        if len(parts) < 3:
            raise AgentFileFormatError(
                "Agent file must have YAML frontmatter enclosed in '---' delimiters",
                agent_file
            )
        
        yaml_content = parts[1].strip()
        raw_system_prompt = parts[2].strip()
        
        if not yaml_content:
            raise AgentFileFormatError(
                "YAML frontmatter section is empty",
                agent_file
            )
        
        if not raw_system_prompt:
            raise AgentFileFormatError(
                "System prompt section is empty",
                agent_file
            )
        
        # Parse YAML frontmatter with enhanced error handling
        try:
            config_data = yaml.safe_load(yaml_content)
        except yaml.scanner.ScannerError as e:
            line_number = getattr(e, 'problem_mark', None)
            line_num = line_number.line + 1 if line_number else None
            raise YAMLFrontmatterError(
                f"YAML syntax error: {e.problem}",
                agent_file,
                yaml_content,
                line_num
            )
        except yaml.parser.ParserError as e:
            line_number = getattr(e, 'problem_mark', None)
            line_num = line_number.line + 1 if line_number else None
            raise YAMLFrontmatterError(
                f"YAML parsing error: {e.problem}",
                agent_file,
                yaml_content,
                line_num
            )
        except Exception as e:
            raise YAMLFrontmatterError(
                f"Unexpected YAML error: {e}",
                agent_file,
                yaml_content
            )
        
        if not isinstance(config_data, dict):
            raise YAMLFrontmatterError(
                f"YAML frontmatter must be a dictionary/object, got {type(config_data).__name__}",
                agent_file,
                yaml_content
            )
        
        return config_data, raw_system_prompt
    
    def _process_files_context(self, files: List[str]) -> Dict[str, Any]:
        """Process files into template context variables"""
        if not files:
            return {}
        
        file_contents = {}
        file_paths = []
        
        for filepath in files:
            try:
                content = self.tool_services.read(filepath)
                file_contents[filepath] = content
                file_paths.append(filepath)
            except Exception as e:
                file_contents[filepath] = f"[ERROR READING FILE: {e}]"
                file_paths.append(filepath)
        
        # Generate AI summary of all files if we have content
        if file_contents and any(not content.startswith("[ERROR") for content in file_contents.values()):
            try:
                combined_content = "\n\n".join([
                    f"FILE: {fp}\n{content}" 
                    for fp, content in file_contents.items() 
                    if not content.startswith("[ERROR")
                ])
                # Use a simple concatenation for summary for now to avoid async issues
                summary = f"Files provided: {', '.join([fp for fp in file_contents.keys() if not file_contents[fp].startswith('[ERROR')])}"
            except Exception as e:
                summary = f"[ERROR GENERATING SUMMARY: {e}]"
        else:
            summary = "No readable files provided"
        
        return {
            'provided_files': file_contents,
            'provided_filepaths': file_paths,
            'provided_files_summary': summary
        }
    
    async def _render_system_prompt(self, raw_prompt: str, context: Dict[str, Any]) -> str:
        """Render system prompt with full template context and enhanced error handling"""
        try:
            # Pre-validate template includes
            snippets_dir = self.project_root / self.template_config.get('base_path', 'snippets')
            # Note: Skip validation here to avoid recursion issues - validation happens in agent_runner
            
            template = self.jinja_env.from_string(raw_prompt)
            if self.enable_async:
                return await template.render_async(**context)
            else:
                return template.render(**context)
        except TemplateNotFound as e:
            raise TemplateProcessingError(
                f"Template include file not found: {e}",
                include_file=str(e)
            )
        except TemplateSyntaxError as e:
            raise TemplateProcessingError(
                f"Template syntax error: {e.message}",
                template_line=e.lineno
            )
        except Exception as e:
            raise TemplateProcessingError(f"Template rendering error: {e}")
    
    def _detect_template_strategy(self, system_prompt: str) -> str:
        """Detect which file handling strategy to use based on template tags"""
        if '<$provided_files$>' in system_prompt:
            return 'full_content'
        elif '<$provided_filepaths$>' in system_prompt:
            return 'file_paths_only'
        elif '<$provided_files_summary$>' in system_prompt:
            return 'summary_only'
        elif 'provided_files' in system_prompt or 'provided_filepaths' in system_prompt:
            return 'template_variables'
        else:
            return 'message_append' 