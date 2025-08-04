#!/usr/bin/env python3
"""
Tool: todo_write
Description: Update the todo list for the current session

CLI Test:
    cd /path/to/oneshot
    python3 -c "
from tools.todo_write import todo_write
result = todo_write([
    {'content': 'Test task', 'status': 'pending', 'id': 'test1', 'priority': 'medium'}
], merge=True)
print(result)
"
"""

from app.tool_services import *
import uuid

# OpenAI tools spec compliant metadata
TOOL_METADATA = {
    "type": "function",
    "function": {
        "name": "todo_write",
        "description": "Use this tool to update your to-do list for the current session. This tool should be used proactively as often as possible to track progress, and to ensure that any new tasks or ideas are captured appropriately. Err towards using this tool more often than less. Add todos for your own planned actions. Update todos as you make progress. Mark todos as in_progress when you start working on them. Ideally you should only have one todo as in_progress at a time. Complete existing tasks before starting new ones. Mark todos as completed when finished. Cancel todos that are no longer relevant",
        "parameters": {
            "type": "object",
            "properties": {
                "merge": {
                    "type": "boolean",
                    "description": "Whether to merge the todos with existing todos. If true, todos are merged based on id field. If false, new todos replace existing ones.",
                    "default": True
                },
                "todos": {
                    "type": "array",
                    "description": "Array of TODO items to write to the workspace",
                    "items": {
                        "type": "object",
                        "properties": {
                            "content": {
                                "type": "string",
                                "description": "The description/content of the TODO item"
                            },
                            "status": {
                                "type": "string",
                                "enum": ["pending", "in_progress", "completed", "cancelled"],
                                "description": "The current status of the TODO item"
                            },
                            "id": {
                                "type": "string",
                                "description": "Unique identifier for the TODO item. If not provided, one will be generated."
                            },
                            "priority": {
                                "type": "string",
                                "enum": ["low", "medium", "high"],
                                "description": "Priority level of the TODO item",
                                "default": "medium"
                            }
                        },
                        "required": ["content", "status"]
                    },
                    "minItems": 1
                }
            },
            "required": ["todos"]
        }
    }
}


def todo_write(todos: List[Dict[str, Any]], merge: bool = True) -> str:
    """
    Update the todo list for the current session
    
    Args:
        todos: List of todo items with content, status, id (optional), and priority (optional)
        merge: Whether to merge with existing todos (True) or replace them (False)
    
    Returns:
        JSON string confirming the update and showing the current todo list
    """
    try:
        # Get the current run ID from tool_services
        run_id = get_run_id()
        if not run_id:
            return json.dumps({
                "error": "No active run session found. Todo lists are session-specific.",
                "success": False
            }, indent=2)
        
        # Path to the todo file for this run
        runs_dir = Path("runs")
        run_dir = runs_dir / run_id
        todo_file = run_dir / "todos.json"
        
        # Ensure run directory exists
        run_dir.mkdir(parents=True, exist_ok=True)
        
        # Load existing todos if merging
        existing_todos = []
        if merge and todo_file.exists():
            try:
                # Use tool_services read function
                todo_content = read(str(todo_file))
                existing_todos = json.loads(todo_content)
            except (json.JSONDecodeError, FileNotFoundError):
                existing_todos = []
        
        # Process new todos - generate IDs if missing and set default priority
        processed_todos = []
        for todo in todos:
            processed_todo = todo.copy()
            
            # Generate ID if not provided
            if 'id' not in processed_todo or not processed_todo['id']:
                processed_todo['id'] = str(uuid.uuid4())[:8]  # Use UUID for better uniqueness
            
            # Set default priority if not provided
            if 'priority' not in processed_todo:
                processed_todo['priority'] = 'medium'
            
            processed_todos.append(processed_todo)
        
        # Merge or replace todos
        if merge:
            # Create a map of existing todos by ID for efficient lookup
            existing_map = {todo['id']: todo for todo in existing_todos}
            
            # Update existing todos or add new ones
            for todo in processed_todos:
                existing_map[todo['id']] = todo
            
            final_todos = list(existing_map.values())
        else:
            final_todos = processed_todos
        
        # Sort todos by status priority (in_progress, pending, completed, cancelled)
        status_priority = {'in_progress': 0, 'pending': 1, 'completed': 2, 'cancelled': 3}
        final_todos.sort(key=lambda x: (status_priority.get(x['status'], 4), x['id']))
        
        # Use tool_services to save the todo list as JSON
        saved_file = save_json(final_todos, f"Todo list for run {run_id}", f"todos.json")
        
        # Count todos by status
        status_counts = {}
        for todo in final_todos:
            status = todo['status']
            status_counts[status] = status_counts.get(status, 0) + 1
        
        return json.dumps({
            "success": True,
            "message": f"Todo list updated successfully. {len(processed_todos)} item(s) {'merged' if merge else 'added'}.",
            "status_summary": status_counts,
            "total_todos": len(final_todos),
            "run_id": run_id,
            "filepath": saved_file["filepath"]
        }, indent=2)
        
    except Exception as e:
        return json.dumps({
            "error": f"Failed to update todo list: {str(e)}",
            "success": False
        }, indent=2)


if __name__ == "__main__":
    # Test the function
    test_todos = [
        {
            "content": "Test todo item",
            "status": "pending",
            "priority": "high"
        }
    ]
    print(todo_write(test_todos)) 