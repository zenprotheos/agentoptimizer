# tools/export_as_screenshot.py
"""
Tool: export_as_screenshot
Description: Generate a PNG screenshot from a markdown (.md) or HTML (.html) file using Puppeteer-based bash scripts.

CLI Test:
    cd /path/to/oneshot
    python3 -c "
from tools.export_as_screenshot import export_as_screenshot
result = export_as_screenshot('test_data/sample.md', visible_only=False)
print(result)
"
"""
from app.tool_services import *
import subprocess

TOOL_METADATA = {
    "type": "function",
    "function": {
        "name": "generate_screenshot",
        "description": "Use this tool to generate a PNG screenshot from a markdown (.md) or HTML (.html) file. The screenshot will be created in the same artifacts directory as the input file and automatically opened for the user to view.",
        "parameters": {
            "type": "object",
            "properties": {
                "file_path": {
                    "type": "string",
                    "description": "Path to the markdown (.md) or HTML (.html) file to convert to screenshot"
                },
                "visible_only": {
                    "type": "boolean",
                    "description": "If true, capture only the visible viewport (100vh). If false, capture the entire page length. Default: false",
                    "default": False
                }
            },
            "required": ["file_path"]
        }
    }
}

def export_as_screenshot(file_path: str, visible_only: bool = False) -> str:
    """Use this tool to generate a PNG screenshot from a markdown (.md) or HTML (.html) file. The screenshot will be created in the same artifacts directory as the input file and automatically opened for the user to view."""
    
    try:
        # Validate file path
        input_path = Path(file_path)
        if not input_path.exists():
            return json.dumps({
                "error": f"File not found: {file_path}"
            }, indent=2)
        
        # Determine file type and script to use
        file_extension = input_path.suffix.lower()
        
        if file_extension == '.md':
            script_name = "export_as_screenshot_from_markdown"
        elif file_extension == '.html':
            script_name = "export_as_screenshot_from_html"
        else:
            return json.dumps({
                "error": f"Unsupported file type: {file_extension}. Only .md and .html files are supported."
            }, indent=2)
        
        # Get absolute path to the bash script
        project_root = Path(__file__).parent.parent
        script_path = project_root / "tools" / "bash_tools" / script_name
        
        if not script_path.exists():
            return json.dumps({
                "error": f"Script not found: {script_path}"
            }, indent=2)
        
        # Make script executable
        script_path.chmod(0o755)
        
        # Prepare command arguments
        cmd_args = [str(script_path), str(input_path.absolute())]
        if visible_only:
            cmd_args.append("--visible-only")
        
        # Run the bash script
        result = subprocess.run(
            cmd_args,
            capture_output=True,
            text=True,
            cwd=str(project_root)
        )
        
        # Determine expected output PNG path
        if visible_only:
            png_path = input_path.parent / f"{input_path.stem}-viewport.png"
        else:
            png_path = input_path.parent / f"{input_path.stem}-fullpage.png"
        
        if result.returncode == 0:
            # Success - save the process output for reference
            process_log = f"Screenshot Generation Log\n{'='*50}\n\nInput File: {file_path}\nScript Used: {script_name}\nOutput Path: {png_path}\nVisible Only: {visible_only}\n\nScript Output:\n{result.stdout}\n\nScript Errors (if any):\n{result.stderr}"
            
            saved_file = save(process_log, f"Screenshot generation log for {input_path.name}")
            
            return json.dumps({
                "success": True,
                "input_file": str(input_path.absolute()),
                "output_screenshot": str(png_path),
                "file_type": file_extension[1:],  # Remove the dot
                "script_used": script_name,
                "visible_only": visible_only,
                "screenshot_type": "viewport" if visible_only else "fullpage",
                "process_log": saved_file["filepath"],
                "run_id": saved_file["run_id"],
                "summary": f"Successfully generated {'viewport' if visible_only else 'fullpage'} screenshot from {file_extension[1:].upper()} file"
            }, indent=2)
        else:
            # Error occurred
            error_log = f"Screenshot Generation Error\n{'='*50}\n\nInput File: {file_path}\nScript Used: {script_name}\nVisible Only: {visible_only}\nReturn Code: {result.returncode}\n\nScript Output:\n{result.stdout}\n\nScript Errors:\n{result.stderr}"
            
            saved_file = save(error_log, f"Screenshot generation error log for {input_path.name}")
            
            return json.dumps({
                "error": "Screenshot generation failed",
                "input_file": str(input_path.absolute()),
                "file_type": file_extension[1:],
                "script_used": script_name,
                "visible_only": visible_only,
                "return_code": result.returncode,
                "error_log": saved_file["filepath"],
                "stdout": result.stdout,
                "stderr": result.stderr
            }, indent=2)
            
    except Exception as e:
        return json.dumps({
            "error": f"Failed to generate screenshot: {str(e)}",
            "file_path": file_path
        }, indent=2) 