#!/usr/bin/env python3
"""
Run Persistence System for PydanticAI Agent Conversations

This module handles storing and retrieving agent conversation runs as JSON files
in a structured directory format: /runs/{run_id}/

Each run directory contains:
- run.json: Complete run data including metadata and message history
"""

import json
import uuid
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple
from pydantic_core import to_jsonable_python
from pydantic_ai.messages import ModelMessagesTypeAdapter, ModelMessage


class RunPersistence:
    """Manages persistent storage of agent conversation runs"""
    
    def __init__(self, base_dir: Path = None):
        """Initialize run persistence with base directory"""
        if base_dir is None:
            # Default to /runs in project root
            base_dir = Path(__file__).parent.parent / "runs"
        
        self.base_dir = Path(base_dir)
        self.base_dir.mkdir(exist_ok=True)
    
    def generate_run_id(self) -> str:
        """Generate a unique run ID with timestamp for chronological ordering"""
        timestamp = datetime.now().strftime("%m%d_%H%M%S")
        short_uuid = str(uuid.uuid4())[:4]  # Shorter UUID for uniqueness
        return f"{timestamp}_{short_uuid}"
    
    def get_run_dir(self, run_id: str) -> Path:
        """Get the directory path for a specific run"""
        return self.base_dir / run_id
    
    def run_exists(self, run_id: str) -> bool:
        """Check if a run exists"""
        run_dir = self.get_run_dir(run_id)
        return run_dir.exists() and (run_dir / "run.json").exists()
    
    def create_run(self, run_id: str, agent_name: str, initial_message: str) -> Dict[str, Any]:
        """Create a new run with initial metadata"""
        run_dir = self.get_run_dir(run_id)
        run_dir.mkdir(exist_ok=True)
        
        run_data = {
            "run_id": run_id,
            "agent_name": agent_name,
            "created_at": datetime.utcnow().isoformat(),
            "updated_at": datetime.utcnow().isoformat(),
            "initial_message": initial_message,
            "message_history": [],
            "total_usage": {
                "requests": 0,
                "request_tokens": 0,
                "response_tokens": 0,
                "total_tokens": 0
            },
            "run_count": 0
        }
        
        # Save initial run data
        self._save_run_data(run_id, run_data)
        return run_data
    
    def load_run(self, run_id: str) -> Optional[Dict[str, Any]]:
        """Load run data from disk"""
        if not self.run_exists(run_id):
            return None
        
        run_file = self.get_run_dir(run_id) / "run.json"
        try:
            with open(run_file, 'r') as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading run {run_id}: {e}")
            return None
    
    def get_message_history(self, run_id: str) -> List[ModelMessage]:
        """Get the message history for a run as ModelMessage objects"""
        run_data = self.load_run(run_id)
        if not run_data or not run_data.get("message_history"):
            return []
        
        # Check if messages contain fallback structures (binary content handling)
        messages = run_data["message_history"]
        if messages and isinstance(messages[0], dict) and ("type" in messages[0] or "original_type" in messages[0]):
            # These are fallback messages from binary content handling
            # Cannot convert back to proper ModelMessage objects
            print(f"Warning: Run {run_id} contains processed messages that cannot be restored to original format")
            return []
        
        try:
            # Convert JSON back to ModelMessage objects (original format)
            return ModelMessagesTypeAdapter.validate_python(run_data["message_history"])
        except Exception as e:
            print(f"Error deserializing message history for run {run_id}: {e}")
            return []
    
    def update_run(self, run_id: str, result: Dict[str, Any], new_messages: List[ModelMessage]) -> Dict[str, Any]:
        """Update run with new result and messages"""
        run_data = self.load_run(run_id)
        if not run_data:
            raise ValueError(f"Run {run_id} does not exist")
        
        # Try to serialize messages, handling binary content gracefully
        try:
            # First attempt: try to serialize as-is
            serializable_messages = to_jsonable_python(new_messages)
            run_data["message_history"].extend(serializable_messages)
        except (UnicodeDecodeError, UnicodeError) as e:
            # Handle UTF-8 decoding errors (binary content) by creating text-only versions
            try:
                safe_messages = []
                for msg in new_messages:
                    safe_msg = self._create_text_only_message(msg)
                    safe_messages.append(safe_msg)
                
                serializable_messages = to_jsonable_python(safe_messages)
                run_data["message_history"].extend(serializable_messages)
            except Exception as fallback_error:
                # Final fallback
                placeholder_messages = [{
                    "type": "message_with_binary_content",
                    "count": len(new_messages),
                    "error": f"Could not serialize messages containing binary content: {str(e)[:100]}",
                    "timestamp": datetime.utcnow().isoformat()
                }]
                run_data["message_history"].extend(placeholder_messages)
        except Exception as e:
            # Other serialization errors
            placeholder_messages = [{
                "type": "message_serialization_error",
                "count": len(new_messages),
                "error": f"Could not serialize messages: {str(e)[:100]}",
                "timestamp": datetime.utcnow().isoformat()
            }]
            run_data["message_history"].extend(placeholder_messages)
        
        # Update usage statistics
        if result.get("usage"):
            usage = result["usage"]
            total_usage = run_data["total_usage"]
            total_usage["requests"] += usage.get("requests", 0)
            total_usage["request_tokens"] += usage.get("request_tokens", 0)
            total_usage["response_tokens"] += usage.get("response_tokens", 0)
            total_usage["total_tokens"] += usage.get("total_tokens", 0)
        
        # Update metadata
        run_data["updated_at"] = datetime.utcnow().isoformat()
        run_data["run_count"] += 1
        run_data["last_message"] = result.get("output", "")[:100] + "..." if len(result.get("output", "")) > 100 else result.get("output", "")
        
        # Save updated run data
        self._save_run_data(run_id, run_data)
        return run_data
    
    def _create_safe_message_copies(self, messages: List[ModelMessage]) -> List[ModelMessage]:
        """Create safe copies of messages by replacing binary content with text placeholders"""
        from copy import deepcopy
        
        safe_messages = []
        for msg in messages:
            try:
                # Try to create a safe copy by replacing binary content in parts
                safe_msg = self._make_message_safe_copy(msg)
                safe_messages.append(safe_msg)
            except Exception as e:
                print(f"Warning: Could not create safe copy of message: {e}")
                # Skip problematic messages rather than breaking the entire save
                continue
        
        return safe_messages
    
    def _create_text_only_message(self, msg):
        """Create a text-only version of a message, preserving PydanticAI structure but replacing binary content"""
        import json
        
        # Convert message to dict first to inspect structure
        try:
            msg_dict = to_jsonable_python(msg)
            return msg  # If this works, no binary content
        except:
            pass
        
        # Create a simplified version that preserves the key structure
        if hasattr(msg, 'parts'):
            text_parts = []
            for part in msg.parts:
                if hasattr(part, 'content'):
                    if isinstance(part.content, str):
                        # Keep text content as-is
                        text_parts.append(part)
                    elif isinstance(part.content, list):
                        # Handle mixed content lists
                        text_items = []
                        for item in part.content:
                            if isinstance(item, str):
                                text_items.append(item)
                            else:
                                text_items.append(f"[Binary content: {type(item).__name__}]")
                        
                        # Create new part with safe content
                        safe_part = type(part)(
                            content=text_items,
                            **{k: v for k, v in part.__dict__.items() if k != 'content'}
                        )
                        text_parts.append(safe_part)
                    else:
                        # Non-string, non-list content
                        safe_part = type(part)(
                            content=f"[Non-text content: {type(part.content).__name__}]",
                            **{k: v for k, v in part.__dict__.items() if k != 'content'}
                        )
                        text_parts.append(safe_part)
                else:
                    # Part without content (might have data/binary)
                    text_parts.append(type(part)(
                        content=f"[Binary content: {type(part).__name__}]",
                        part_kind="text"
                    ))
            
            # Create new message with text-only parts
            return type(msg)(parts=text_parts, **{k: v for k, v in msg.__dict__.items() if k != 'parts'})
        
        else:
            # Message without parts
            return str(msg)
    
    def _make_message_safe_copy(self, msg):
        """Create a safe copy of a message by replacing binary content in parts"""
        from copy import deepcopy
        
        # Try deepcopy first - if this works, no binary content
        try:
            return deepcopy(msg)
        except Exception:
            pass
        
        # Binary content detected, need to create safe version
        if hasattr(msg, 'parts') and hasattr(msg, '__class__'):
            # Create new message with safe parts
            safe_parts = []
            
            for part in msg.parts:
                safe_part = self._make_part_safe_copy(part)
                safe_parts.append(safe_part)
            
            # Try to create new message with same type but safe parts
            try:
                # Get all attributes from original message
                msg_attrs = {}
                for attr in dir(msg):
                    if not attr.startswith('_') and attr != 'parts':
                        try:
                            value = getattr(msg, attr)
                            if not callable(value):
                                msg_attrs[attr] = value
                        except:
                            pass
                
                # Create new instance with safe parts
                return msg.__class__(parts=safe_parts, **msg_attrs)
            except Exception:
                # If we can't recreate the exact type, create a basic structure
                return type('SafeMessage', (), {
                    'parts': safe_parts,
                    'kind': getattr(msg, 'kind', 'unknown'),
                    '__class__': msg.__class__
                })()
        
        else:
            # Message without parts - convert to string representation
            return str(msg)
    
    def _make_part_safe_copy(self, part):
        """Create a safe copy of a message part by replacing binary content"""
        from copy import deepcopy
        
        # Try deepcopy first
        try:
            return deepcopy(part)
        except Exception:
            pass
        
        # Create safe version
        if hasattr(part, 'content'):
            safe_content = self._make_content_safe_copy(part.content)
            
            # Try to create new part with safe content
            try:
                part_attrs = {}
                for attr in dir(part):
                    if not attr.startswith('_') and attr != 'content':
                        try:
                            value = getattr(part, attr)
                            if not callable(value):
                                part_attrs[attr] = value
                        except:
                            pass
                
                return part.__class__(content=safe_content, **part_attrs)
            except Exception:
                # Fallback: create basic structure
                return type('SafePart', (), {
                    'content': safe_content,
                    'part_kind': getattr(part, 'part_kind', 'unknown'),
                    '__class__': part.__class__
                })()
        
        elif hasattr(part, 'data'):
            # Binary content part - replace with text placeholder
            try:
                part_attrs = {}
                for attr in dir(part):
                    if not attr.startswith('_') and attr != 'data':
                        try:
                            value = getattr(part, attr)
                            if not callable(value):
                                part_attrs[attr] = value
                        except:
                            pass
                
                # Replace data with placeholder text
                return type('SafePart', (), {
                    'content': f"[Binary content: {type(part).__name__}]",
                    'part_kind': 'text',  # Change to text type
                    **part_attrs
                })()
            except Exception:
                return f"[Binary content: {type(part).__name__}]"
        
        else:
            # Unknown part structure
            return f"[{type(part).__name__}]"
    
    def _make_content_safe_copy(self, content):
        """Create a safe copy of content by replacing binary parts"""
        if isinstance(content, str):
            return content
        elif isinstance(content, list):
            safe_items = []
            for item in content:
                if isinstance(item, str):
                    safe_items.append(item)
                else:
                    # Try to serialize individual items
                    try:
                        to_jsonable_python(item)
                        safe_items.append(item)
                    except Exception:
                        # Replace binary/complex items with placeholder
                        safe_items.append(f"[Binary content: {type(item).__name__}]")
            return safe_items
        else:
            # Try to serialize to test if it's safe
            try:
                to_jsonable_python(content)
                return content
            except Exception:
                return f"[Non-serializable content: {type(content).__name__}]"
    
    def _save_run_data(self, run_id: str, run_data: Dict[str, Any]):
        """Save run data to disk"""
        run_dir = self.get_run_dir(run_id)
        
        # Save complete run data (only file needed)
        with open(run_dir / "run.json", 'w') as f:
            json.dump(run_data, f, indent=2, default=str)
    

    
    def delete_run(self, run_id: str) -> bool:
        """Delete a run and all its files"""
        run_dir = self.get_run_dir(run_id)
        if not run_dir.exists():
            return False
        
        try:
            # Remove all files in the run directory
            for file in run_dir.iterdir():
                file.unlink()
            run_dir.rmdir()
            return True
        except Exception as e:
            print(f"Error deleting run {run_id}: {e}")
            return False
    
    def get_run_summary(self, run_id: str) -> Optional[Dict[str, Any]]:
        """Get a human-readable summary of a run"""
        if not self.run_exists(run_id):
            return None
        
        metadata_file = self.get_run_dir(run_id) / "metadata.json"
        try:
            with open(metadata_file, 'r') as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading run summary for {run_id}: {e}")
            return None 