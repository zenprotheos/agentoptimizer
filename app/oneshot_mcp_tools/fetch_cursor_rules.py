#!/usr/bin/env python3
"""
Fetch Cursor rules from .cursor/rules directory
"""

import os
import json
from pathlib import Path

def fetch_cursor_rules(rule_names: list, project_root: str = ".") -> str:
    """Fetch Cursor rules from .cursor/rules directory
    
    Args:
        rule_names: List of rule names to fetch (without .mdc extension)
        project_root: Root directory of the project
        
    Returns:
        str: Contents of the requested rules
    """
    rules_dir = Path(project_root) / ".cursor" / "rules"
    
    if not rules_dir.exists():
        return json.dumps({
            "error": "Cursor rules directory not found",
            "expected_path": str(rules_dir)
        })
    
    fetched_rules = {}
    errors = []
    
    for rule_name in rule_names:
        rule_file = rules_dir / f"{rule_name}.mdc"
        
        if not rule_file.exists():
            # List available rules
            available_rules = [f.stem for f in rules_dir.glob("*.mdc")]
            errors.append(f"Rule '{rule_name}' not found. Available rules: {', '.join(available_rules)}")
            continue
        
        try:
            with open(rule_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Parse frontmatter if present
            frontmatter = {}
            rule_content = content
            
            if content.startswith('---'):
                parts = content.split('---', 2)
                if len(parts) >= 3:
                    import yaml
                    try:
                        frontmatter = yaml.safe_load(parts[1]) or {}
                        rule_content = parts[2].strip()
                    except yaml.YAMLError:
                        pass  # Keep original content if YAML parsing fails
            
            fetched_rules[rule_name] = {
                "content": rule_content,
                "frontmatter": frontmatter,
                "file_path": str(rule_file)
            }
            
        except Exception as e:
            errors.append(f"Error reading rule '{rule_name}': {str(e)}")
    
    return json.dumps({
        "success": len(fetched_rules) > 0,
        "rules": fetched_rules,
        "errors": errors,
        "total_fetched": len(fetched_rules),
        "total_requested": len(rule_names)
    }, indent=2)

def list_available_cursor_rules(project_root: str = ".") -> str:
    """List all available Cursor rules
    
    Args:
        project_root: Root directory of the project
        
    Returns:
        str: JSON string with available rule information
    """
    rules_dir = Path(project_root) / ".cursor" / "rules"
    
    if not rules_dir.exists():
        return json.dumps({
            "error": "Cursor rules directory not found",
            "expected_path": str(rules_dir)
        })
    
    rules_info = []
    
    for rule_file in rules_dir.glob("*.mdc"):
        try:
            with open(rule_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Parse frontmatter for metadata
            frontmatter = {}
            if content.startswith('---'):
                parts = content.split('---', 2)
                if len(parts) >= 3:
                    import yaml
                    try:
                        frontmatter = yaml.safe_load(parts[1]) or {}
                    except yaml.YAMLError:
                        pass
            
            # Extract first line as description if available
            lines = content.strip().split('\n')
            description = ""
            for line in lines:
                line = line.strip()
                if line and not line.startswith('#') and not line.startswith('---'):
                    description = line
                    break
            
            rules_info.append({
                "name": rule_file.stem,
                "filename": rule_file.name,
                "description": description[:100] + "..." if len(description) > 100 else description,
                "frontmatter": frontmatter,
                "always_apply": frontmatter.get("alwaysApply", False)
            })
            
        except Exception as e:
            rules_info.append({
                "name": rule_file.stem,
                "filename": rule_file.name,
                "error": f"Could not read file: {str(e)}"
            })
    
    return json.dumps({
        "rules": rules_info,
        "total": len(rules_info),
        "rules_directory": str(rules_dir)
    }, indent=2)
