---
title: "Modular Programmatic Checkpoint System"
date: "2025-08-25T23:59:59.999Z"
task: "GlobalDocs_System_Analysis"
status: "Specification"
priority: "High"
tags: ["checkpoints", "validation", "modular", "extensible", "sop"]
---

# Modular Programmatic Checkpoint System

## Overview

A flexible, easily modifiable checkpoint system that allows you to add, remove, or reorder validation steps in the SOP workflow. Each checkpoint is a modular component that can be configured independently.

## Architecture Design

### Core Checkpoint Framework
```python
# NEW: app/checkpoint_system.py
from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional
from pathlib import Path
import yaml
import json

class CheckpointResult:
    def __init__(self, passed: bool, message: str, details: Dict = None):
        self.passed = passed
        self.message = message
        self.details = details or {}
        self.timestamp = datetime.now().isoformat()

class BaseCheckpoint(ABC):
    """Base class for all checkpoint validations"""
    
    def __init__(self, config: Dict = None):
        self.config = config or {}
        self.name = self.__class__.__name__
        self.enabled = self.config.get("enabled", True)
        self.critical = self.config.get("critical", True)  # Stop on failure?
        self.order = self.config.get("order", 100)
    
    @abstractmethod
    def validate(self, context: Dict) -> CheckpointResult:
        """Perform the validation check"""
        pass
    
    def get_description(self) -> str:
        """Return human-readable description of this checkpoint"""
        return getattr(self, 'description', f"Validation: {self.name}")

class CheckpointManager:
    """Manages and executes checkpoint validations"""
    
    def __init__(self, config_path: str = "config/checkpoints.yaml"):
        self.config_path = Path(config_path)
        self.checkpoints: List[BaseCheckpoint] = []
        self.load_configuration()
        self.register_checkpoints()
    
    def load_configuration(self):
        """Load checkpoint configuration from YAML"""
        if self.config_path.exists():
            with open(self.config_path, 'r') as f:
                self.config = yaml.safe_load(f)
        else:
            # Default configuration
            self.config = {
                "enabled": True,
                "stop_on_critical_failure": True,
                "checkpoints": {
                    "mermaid_syntax": {"enabled": True, "critical": True, "order": 10},
                    "frontmatter_validation": {"enabled": True, "critical": False, "order": 20},
                    "cross_reference_validation": {"enabled": True, "critical": False, "order": 30},
                    "file_organization": {"enabled": True, "critical": False, "order": 40},
                    "obsidian_compatibility": {"enabled": True, "critical": False, "order": 50}
                }
            }
            self.save_configuration()
    
    def save_configuration(self):
        """Save current configuration to YAML"""
        self.config_path.parent.mkdir(parents=True, exist_ok=True)
        with open(self.config_path, 'w') as f:
            yaml.dump(self.config, f, default_flow_style=False)
    
    def register_checkpoints(self):
        """Register all available checkpoints"""
        checkpoint_classes = [
            MermaidSyntaxCheckpoint,
            FrontmatterValidationCheckpoint,
            CrossReferenceValidationCheckpoint,
            FileOrganizationCheckpoint,
            ObsidianCompatibilityCheckpoint,
            RuleComplianceCheckpoint,
            GitWorkflowCheckpoint,
            TestValidationCheckpoint
        ]
        
        for checkpoint_class in checkpoint_classes:
            checkpoint_name = checkpoint_class.__name__.replace("Checkpoint", "").lower()
            checkpoint_config = self.config["checkpoints"].get(checkpoint_name, {})
            
            if checkpoint_config.get("enabled", True):
                checkpoint = checkpoint_class(checkpoint_config)
                self.checkpoints.append(checkpoint)
        
        # Sort by order
        self.checkpoints.sort(key=lambda x: x.order)
    
    def run_checkpoints(self, context: Dict) -> Dict[str, Any]:
        """Execute all enabled checkpoints"""
        results = {
            "overall_passed": True,
            "critical_failures": [],
            "warnings": [],
            "checkpoint_results": [],
            "summary": {}
        }
        
        for checkpoint in self.checkpoints:
            if not checkpoint.enabled:
                continue
            
            try:
                result = checkpoint.validate(context)
                
                checkpoint_data = {
                    "name": checkpoint.name,
                    "description": checkpoint.get_description(),
                    "passed": result.passed,
                    "message": result.message,
                    "details": result.details,
                    "critical": checkpoint.critical,
                    "timestamp": result.timestamp
                }
                
                results["checkpoint_results"].append(checkpoint_data)
                
                if not result.passed:
                    if checkpoint.critical:
                        results["critical_failures"].append(checkpoint_data)
                        results["overall_passed"] = False
                        
                        if self.config.get("stop_on_critical_failure", True):
                            break
                    else:
                        results["warnings"].append(checkpoint_data)
                
            except Exception as e:
                error_data = {
                    "name": checkpoint.name,
                    "passed": False,
                    "message": f"Checkpoint execution failed: {str(e)}",
                    "critical": checkpoint.critical,
                    "error": True
                }
                
                results["checkpoint_results"].append(error_data)
                if checkpoint.critical:
                    results["critical_failures"].append(error_data)
                    results["overall_passed"] = False
        
        # Generate summary
        results["summary"] = {
            "total_checkpoints": len([c for c in self.checkpoints if c.enabled]),
            "passed": len([r for r in results["checkpoint_results"] if r["passed"]]),
            "failed": len([r for r in results["checkpoint_results"] if not r["passed"]]),
            "critical_failures": len(results["critical_failures"]),
            "warnings": len(results["warnings"])
        }
        
        return results
    
    def add_checkpoint(self, checkpoint_name: str, checkpoint_class: type, 
                      config: Dict = None, order: int = None):
        """Dynamically add a new checkpoint"""
        if order is None:
            order = max([c.order for c in self.checkpoints], default=0) + 10
        
        checkpoint_config = config or {"enabled": True, "critical": False, "order": order}
        checkpoint_config["order"] = order
        
        # Update configuration
        self.config["checkpoints"][checkpoint_name] = checkpoint_config
        self.save_configuration()
        
        # Register the checkpoint
        checkpoint = checkpoint_class(checkpoint_config)
        self.checkpoints.append(checkpoint)
        self.checkpoints.sort(key=lambda x: x.order)
    
    def remove_checkpoint(self, checkpoint_name: str):
        """Remove a checkpoint"""
        self.checkpoints = [c for c in self.checkpoints if c.name != checkpoint_name]
        if checkpoint_name in self.config["checkpoints"]:
            del self.config["checkpoints"][checkpoint_name]
            self.save_configuration()
    
    def reorder_checkpoints(self, new_order: Dict[str, int]):
        """Reorder checkpoints by updating their order values"""
        for checkpoint_name, order in new_order.items():
            if checkpoint_name in self.config["checkpoints"]:
                self.config["checkpoints"][checkpoint_name]["order"] = order
        
        self.save_configuration()
        self.register_checkpoints()  # Reload with new order
```

### Specific Checkpoint Implementations

#### 1. Mermaid Syntax Validation
```python
class MermaidSyntaxCheckpoint(BaseCheckpoint):
    description = "Validate Mermaid diagram syntax against established rules"
    
    def validate(self, context: Dict) -> CheckpointResult:
        """Check all Mermaid diagrams for syntax errors"""
        
        issues = []
        files_checked = 0
        
        # Find all files with Mermaid content
        for file_path in context.get("generated_files", []):
            if file_path.suffix == ".md":
                content = file_path.read_text()
                mermaid_blocks = self._extract_mermaid_blocks(content)
                
                if mermaid_blocks:
                    files_checked += 1
                    for i, block in enumerate(mermaid_blocks):
                        block_issues = self._validate_mermaid_block(block, file_path, i)
                        issues.extend(block_issues)
        
        if issues:
            return CheckpointResult(
                passed=False,
                message=f"Found {len(issues)} Mermaid syntax issues in {files_checked} files",
                details={
                    "issues": issues,
                    "files_checked": files_checked,
                    "validation_rules": self._get_validation_rules()
                }
            )
        
        return CheckpointResult(
            passed=True,
            message=f"All Mermaid diagrams validated successfully ({files_checked} files checked)",
            details={"files_checked": files_checked}
        )
    
    def _validate_mermaid_block(self, mermaid_code: str, file_path: Path, block_index: int) -> List[Dict]:
        """Validate individual Mermaid block against rules"""
        issues = []
        
        # Load Mermaid validation rules
        validation_rules = self._get_validation_rules()
        
        for rule_name, rule_config in validation_rules.items():
            if rule_config.get("enabled", True):
                violation = self._check_rule_violation(mermaid_code, rule_name, rule_config)
                if violation:
                    issues.append({
                        "file": str(file_path),
                        "block_index": block_index,
                        "rule": rule_name,
                        "severity": rule_config.get("severity", "error"),
                        "message": violation,
                        "line_number": self._find_violation_line(mermaid_code, rule_name)
                    })
        
        return issues
    
    def _get_validation_rules(self) -> Dict:
        """Load Mermaid validation rules from mermaid-rule.mdc"""
        return {
            "no_html_tags": {
                "enabled": True,
                "severity": "error",
                "pattern": r"<br/?>|<b>|<i>|<div>|<span>",
                "message": "HTML tags not allowed in Mermaid diagrams. Use pipe | for line breaks."
            },
            "quoted_special_chars": {
                "enabled": True,
                "severity": "error",
                "check": "unquoted_special_chars",
                "message": "Special characters must be quoted. Use [\"text with/special chars\"]"
            },
            "standard_arrows": {
                "enabled": True,
                "severity": "warning",
                "pattern": r"\|\|--\|\|",
                "message": "Use standard arrow syntax: -->, --o, --|>, --*"
            },
            "defined_participants": {
                "enabled": True,
                "severity": "error",
                "check": "sequence_participants",
                "message": "All sequence diagram participants must be defined before use"
            }
        }
    
    def _check_rule_violation(self, mermaid_code: str, rule_name: str, rule_config: Dict) -> Optional[str]:
        """Check specific rule violation"""
        
        if "pattern" in rule_config:
            import re
            if re.search(rule_config["pattern"], mermaid_code):
                return rule_config["message"]
        
        elif rule_config.get("check") == "unquoted_special_chars":
            # Check for unquoted special characters
            lines = mermaid_code.split('\n')
            for line in lines:
                if self._has_unquoted_special_chars(line):
                    return rule_config["message"]
        
        elif rule_config.get("check") == "sequence_participants":
            # Check sequence diagram participants
            if "sequenceDiagram" in mermaid_code:
                if self._has_undefined_participants(mermaid_code):
                    return rule_config["message"]
        
        return None
```

#### 2. Rule Compliance Checkpoint
```python
class RuleComplianceCheckpoint(BaseCheckpoint):
    description = "Validate compliance with all applicable coding-tasks rules"
    
    def validate(self, context: Dict) -> CheckpointResult:
        """Check compliance with SOP steps and rules"""
        
        compliance_issues = []
        
        # Check each SOP step completion
        sop_steps = {
            "step_1_workspace": self._check_workspace_creation(context),
            "step_2_architecture": self._check_architecture_docs(context),
            "step_3_testing": self._check_automated_testing(context),
            "step_4_master_test": self._check_master_test(context),
            "step_5_git_workflow": self._check_git_workflow(context),
            "step_6_lessons_learned": self._check_lessons_learned(context),
            "step_7_compliance": True  # This IS the compliance check
        }
        
        failed_steps = [step for step, passed in sop_steps.items() if not passed]
        
        if failed_steps:
            return CheckpointResult(
                passed=False,
                message=f"SOP compliance failures in steps: {', '.join(failed_steps)}",
                details={
                    "failed_steps": failed_steps,
                    "step_details": sop_steps,
                    "compliance_requirements": self._get_compliance_requirements()
                }
            )
        
        return CheckpointResult(
            passed=True,
            message="All SOP steps completed successfully",
            details={"completed_steps": list(sop_steps.keys())}
        )
    
    def _check_automated_testing(self, context: Dict) -> bool:
        """Verify automated tests exist and pass"""
        test_dir = Path(context.get("task_dir", "")) / "tests"
        
        if not test_dir.exists():
            return False
        
        test_files = list(test_dir.glob("*.py"))
        if not test_files:
            return False
        
        # Check if tests have been executed recently
        for test_file in test_files:
            if self._has_recent_execution_evidence(test_file):
                return True
        
        return False
    
    def _check_git_workflow(self, context: Dict) -> bool:
        """Verify git commit and push completed"""
        # Check git status and recent commits
        try:
            result = subprocess.run(["git", "status", "--porcelain"], 
                                  capture_output=True, text=True)
            
            # Should have clean working directory after commit
            if result.stdout.strip():
                return False  # Uncommitted changes
            
            # Check for recent commits
            recent_commits = subprocess.run(
                ["git", "log", "--oneline", "-n", "5"], 
                capture_output=True, text=True
            )
            
            # Look for task-related commit in recent history
            task_name = context.get("task_name", "")
            return task_name in recent_commits.stdout
            
        except subprocess.CalledProcessError:
            return False
```

### Configuration Management

#### Checkpoint Configuration File
```yaml
# config/checkpoints.yaml
enabled: true
stop_on_critical_failure: true

checkpoints:
  mermaid_syntax:
    enabled: true
    critical: true
    order: 10
    config:
      validate_html_tags: true
      validate_quotes: true
      validate_arrows: true
      validate_participants: true
  
  frontmatter_validation:
    enabled: true
    critical: false
    order: 20
    config:
      required_fields: ["created", "tags", "type"]
      validate_yaml_syntax: true
  
  cross_reference_validation:
    enabled: true
    critical: false
    order: 30
    config:
      check_broken_links: true
      validate_obsidian_syntax: true
  
  file_organization:
    enabled: true
    critical: false
    order: 40
    config:
      check_vault_structure: true
      validate_naming_conventions: true
  
  obsidian_compatibility:
    enabled: true
    critical: false
    order: 50
    config:
      test_vault_loading: true
      validate_plugins: false
  
  rule_compliance:
    enabled: true
    critical: true
    order: 60
    config:
      check_sop_steps: true
      validate_completeness: true
  
  git_workflow:
    enabled: true
    critical: true
    order: 70
    config:
      require_commit: true
      require_push: true
      check_commit_message: true
  
  test_validation:
    enabled: true
    critical: true
    order: 80
    config:
      require_passing_tests: true
      check_coverage: false

# Custom checkpoint definitions
custom_checkpoints:
  documentation_quality:
    enabled: false
    critical: false
    order: 90
    class: "DocumentationQualityCheckpoint"
    config:
      min_words: 100
      check_spelling: true
      validate_structure: true
```

### Easy Modification Interface

#### CLI Tool for Checkpoint Management
```python
# tools/manage_checkpoints.py
from app.tool_services import *

TOOL_METADATA = {
    "type": "function",
    "function": {
        "name": "manage_checkpoints",
        "description": "Add, remove, or modify checkpoint validations in the SOP workflow",
        "parameters": {
            "type": "object",
            "properties": {
                "action": {
                    "type": "string",
                    "enum": ["list", "add", "remove", "enable", "disable", "reorder", "configure"],
                    "description": "Action to perform on checkpoints"
                },
                "checkpoint_name": {
                    "type": "string",
                    "description": "Name of the checkpoint to modify"
                },
                "config": {
                    "type": "object",
                    "description": "Configuration for the checkpoint"
                },
                "order": {
                    "type": "integer", 
                    "description": "Execution order for the checkpoint"
                }
            },
            "required": ["action"]
        }
    }
}

def manage_checkpoints(action: str, checkpoint_name: str = None, 
                      config: dict = None, order: int = None) -> str:
    """Manage checkpoint system configuration"""
    
    try:
        checkpoint_manager = CheckpointManager()
        
        if action == "list":
            checkpoints = []
            for cp in checkpoint_manager.checkpoints:
                checkpoints.append({
                    "name": cp.name,
                    "description": cp.get_description(),
                    "enabled": cp.enabled,
                    "critical": cp.critical,
                    "order": cp.order
                })
            
            return json.dumps({
                "success": True,
                "checkpoints": checkpoints,
                "total": len(checkpoints)
            }, indent=2)
        
        elif action == "add":
            if not checkpoint_name:
                return json.dumps({"error": "checkpoint_name required for add action"})
            
            # Example of adding a custom checkpoint
            class CustomCheckpoint(BaseCheckpoint):
                description = config.get("description", f"Custom checkpoint: {checkpoint_name}")
                
                def validate(self, context):
                    # Custom validation logic based on config
                    return CheckpointResult(True, "Custom validation passed")
            
            checkpoint_manager.add_checkpoint(checkpoint_name, CustomCheckpoint, config, order)
            
            return json.dumps({
                "success": True,
                "message": f"Added checkpoint: {checkpoint_name}",
                "config": config
            }, indent=2)
        
        elif action == "enable" or action == "disable":
            enabled = action == "enable"
            checkpoint_manager.config["checkpoints"][checkpoint_name]["enabled"] = enabled
            checkpoint_manager.save_configuration()
            
            return json.dumps({
                "success": True,
                "message": f"Checkpoint {checkpoint_name} {'enabled' if enabled else 'disabled'}"
            }, indent=2)
        
        elif action == "reorder":
            if not config:
                return json.dumps({"error": "config with new order mapping required"})
            
            checkpoint_manager.reorder_checkpoints(config)
            
            return json.dumps({
                "success": True,
                "message": "Checkpoints reordered",
                "new_order": config
            }, indent=2)
        
    except Exception as e:
        return json.dumps({
            "error": f"Failed to {action} checkpoint: {str(e)}"
        }, indent=2)

# Example usage commands:
# manage_checkpoints("list")
# manage_checkpoints("add", "my_custom_check", {"critical": True, "description": "My validation"}, 25)
# manage_checkpoints("disable", "frontmatter_validation")  
# manage_checkpoints("reorder", {"mermaid_syntax": 5, "rule_compliance": 10})
```

### Integration with Tool Services

```python
# Enhanced app/tool_services.py
class ToolHelper:
    def __init__(self):
        # Existing initialization...
        self.checkpoint_manager = CheckpointManager()
    
    def save(self, content: str, description: str = "", 
             filename: str = None, add_frontmatter: bool = True,
             run_checkpoints: bool = True) -> Dict[str, Any]:
        """Enhanced save with automatic checkpoint validation"""
        
        # Normal save process
        result = self._original_save(content, description, filename, add_frontmatter)
        
        # Run checkpoints if enabled
        if run_checkpoints and self.checkpoint_manager.config.get("enabled", True):
            checkpoint_context = {
                "generated_files": [Path(result["filepath"])],
                "task_dir": Path(result["artifacts_dir"]).parent,
                "run_id": result["run_id"],
                "content": content,
                "file_type": Path(result["filepath"]).suffix
            }
            
            checkpoint_results = self.checkpoint_manager.run_checkpoints(checkpoint_context)
            
            # Add checkpoint results to response
            result["checkpoint_validation"] = {
                "passed": checkpoint_results["overall_passed"],
                "summary": checkpoint_results["summary"],
                "issues": checkpoint_results["critical_failures"] + checkpoint_results["warnings"]
            }
            
            # If critical failures, include details
            if not checkpoint_results["overall_passed"]:
                result["validation_errors"] = checkpoint_results["critical_failures"]
        
        return result
```

## Usage Examples

### Adding a Custom Checkpoint
```python
# Example: Add spell-check validation
manage_checkpoints("add", "spell_check", {
    "critical": False,
    "description": "Validate spelling in documentation files",
    "config": {
        "dictionaries": ["en_US", "technical_terms"],
        "ignore_code_blocks": True,
        "max_errors": 5
    }
}, 35)
```

### Reordering Checkpoints
```python
# Move Mermaid validation to run earlier
manage_checkpoints("reorder", config={
    "mermaid_syntax": 5,
    "frontmatter_validation": 15,
    "rule_compliance": 65
})
```

### Configuring Checkpoint Sensitivity
```yaml
# Modify config/checkpoints.yaml for different environments
development:
  checkpoints:
    mermaid_syntax:
      critical: false  # Don't stop on Mermaid errors during development
      
production:
  checkpoints:
    mermaid_syntax:
      critical: true   # Strict validation for production
```

This modular system makes it trivial to add new validation steps, modify existing ones, or change the order of execution, giving you complete control over the quality assurance process.
