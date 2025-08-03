import os
import sys
from pathlib import Path
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import Optional
import json

# Add the project root to the Python path to import the AgentRunner
sys.path.insert(0, str(Path(__file__).parent.parent))
from app.agent_runner import AgentRunner

app = FastAPI()

# --- Configuration ---
# Get the absolute path of the parent directory (oneshot repo root)
# The script is in /baby-cursor, so .. is the root
PROJECT_ROOT = Path(__file__).parent.parent.resolve()

# --- Pydantic Models ---
class FileContent(BaseModel):
    content: str

class ChatRequest(BaseModel):
    message: str
    agent_name: Optional[str] = None
    run_id: Optional[str] = None
    
    class Config:
        # Allow None values to be passed as null in JSON
        validate_assignment = True

# --- Agent Runner Initialization ---
runner = AgentRunner(debug=True)

# --- Helper Functions ---
def get_file_tree(dir_path: Path, root_path: Path, max_depth=3, current_depth=0):
    """Recursively builds a file tree for the sidebar with depth limits."""
    if current_depth >= max_depth:
        return []
    
    tree = []
    try:
        items = list(os.scandir(dir_path))
        # Limit number of items to prevent performance issues
        items = sorted(items, key=lambda e: (e.is_file(), e.name.lower()))[:50]
        
        for item in items:
            # Exclude hidden files/dirs, binary files, and problematic directories
            if (item.name.startswith('.') or 
                item.name in ['baby-cursor', '__pycache__', 'node_modules', '.git', 'runs', 'artifacts'] or
                (item.is_file() and item.name.endswith(('.pyc', '.pyo', '.so', '.dylib', '.dll')))):
                continue

            item_path = Path(item.path)
            try:
                relative_path = item_path.relative_to(root_path)
            except ValueError:
                continue  # Skip if path is outside root
            
            entry = {
                "id": str(relative_path),
                "name": item.name,
            }
            
            if item.is_dir():
                entry["type"] = "folder"
                # Only recurse into folders if we haven't hit depth limit
                if current_depth < max_depth - 1:
                    entry["children"] = get_file_tree(item_path, root_path, max_depth, current_depth + 1)
                else:
                    entry["children"] = []
            else:
                entry["type"] = "file"
                # Skip very large files
                try:
                    if item.stat().st_size > 1024 * 1024:  # Skip files > 1MB
                        continue
                except:
                    continue
                    
            tree.append(entry)
            
    except (FileNotFoundError, PermissionError):
        return []
    return tree

def is_safe_path(path: str) -> bool:
    """Ensure the path is within the project directory."""
    abs_path = (PROJECT_ROOT / path).resolve()
    return abs_path.is_relative_to(PROJECT_ROOT)

# --- FastAPI Endpoints ---
app.mount("/static", StaticFiles(directory=str(Path(__file__).parent / "static")), name="static")

@app.get("/")
async def read_index():
    return FileResponse(str(Path(__file__).parent / "static/index.html"))

@app.get("/api/files")
async def list_files_endpoint():
    """List all files in the repository, structured for the file explorer."""
    file_tree = get_file_tree(PROJECT_ROOT, PROJECT_ROOT)
    return JSONResponse(content=[
        {
            "id": "oneshot",
            "name": "oneshot",
            "type": "folder",
            "children": file_tree
        }
    ])

@app.get("/api/files/{file_path:path}")
async def read_file_content(file_path: str):
    """Read the content of a specific file, with security checks."""
    if not is_safe_path(file_path):
        raise HTTPException(status_code=403, detail="Access denied: Path is outside the project directory.")
    
    try:
        abs_path = (PROJECT_ROOT / file_path).resolve()
        with open(abs_path, "r", encoding="utf-8") as f:
            content = f.read()
        return JSONResponse(content={"content": content})
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail=f"File not found: {file_path}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error reading file: {str(e)}")

@app.post("/api/files/{file_path:path}")
async def write_file_content_endpoint(file_path: str, file_content: FileContent):
    """Write content to a specific file, with security checks."""
    if not is_safe_path(file_path):
        raise HTTPException(status_code=403, detail="Access denied: Path is outside the project directory.")
        
    try:
        abs_path = (PROJECT_ROOT / file_path).resolve()
        with open(abs_path, "w", encoding="utf-8") as f:
            f.write(file_content.content)
        return JSONResponse(content={"message": "File saved successfully"})
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error writing file: {str(e)}")

@app.get("/api/agents")
async def get_agents():
    """Get list of available agents."""
    try:
        # Get list of agent files from the agents directory
        agents_dir = PROJECT_ROOT / "agents"
        agents = []
        
        if agents_dir.exists():
            for agent_file in agents_dir.glob("*.md"):
                agent_name = agent_file.stem
                # Skip template files or non-agent files
                if agent_name not in ['template', 'example']:
                    # Create display name with emoji
                    display_name = agent_name.replace('_', ' ').title()
                    
                    # Add emoji based on agent type
                    emoji = {
                        'oneshot': '🤖',
                        'web': '🌐', 
                        'research': '🔍',
                        'writing': '✍️',
                        'vision': '👁️',
                        'search': '🔎',
                        'nrl': '🏉'
                    }.get(agent_name.split('_')[0], '🤖')
                    
                    agents.append({
                        'value': agent_name,
                        'label': f"{emoji} {display_name}",
                        'name': display_name
                    })
        
        # Sort agents by name
        agents.sort(key=lambda x: x['name'])
        
        # Ensure oneshot_agent is first if it exists
        oneshot_agent = next((a for a in agents if a['value'] == 'oneshot_agent'), None)
        if oneshot_agent:
            agents.remove(oneshot_agent)
            agents.insert(0, oneshot_agent)
        
        return JSONResponse(content=agents)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting agents: {str(e)}")

@app.post("/api/chat")
async def chat(request: ChatRequest):
    """Handle chat requests to the agent runner."""
    try:
        response = await runner.run_agent_async(
            agent_name=request.agent_name,  # Use the selected agent or defaults to oneshot_agent
            message=request.message,
            run_id=request.run_id
        )
        # Ensure the response is JSON serializable
        return JSONResponse(content=json.loads(json.dumps(response, default=str)))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)