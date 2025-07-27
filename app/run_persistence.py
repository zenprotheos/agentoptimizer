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
from typing import Dict, Any, List, Optional
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
        """Generate a unique run ID"""
        return str(uuid.uuid4())[:8]  # Short UUID for readability
    
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
        
        try:
            # Convert JSON back to ModelMessage objects
            return ModelMessagesTypeAdapter.validate_python(run_data["message_history"])
        except Exception as e:
            print(f"Error deserializing message history for run {run_id}: {e}")
            return []
    
    def update_run(self, run_id: str, result: Dict[str, Any], new_messages: List[ModelMessage]) -> Dict[str, Any]:
        """Update run with new result and messages"""
        run_data = self.load_run(run_id)
        if not run_data:
            raise ValueError(f"Run {run_id} does not exist")
        
        # Try to serialize messages, but handle binary content gracefully
        try:
            serializable_messages = to_jsonable_python(new_messages)
            run_data["message_history"].extend(serializable_messages)
        except Exception as e:
            # If serialization fails (likely due to binary content), store a placeholder
            placeholder_messages = [{
                "type": "message_with_binary_content",
                "count": len(new_messages),
                "error": f"Could not serialize messages containing binary content: {str(e)[:100]}",
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