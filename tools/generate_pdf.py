# tools/generate_pdf.py
from app.tool_services import *
import subprocess

TOOL_METADATA = {
    "type": "function",
    "function": {
        "name": "generate_pdf",
        "description": "Generate a PDF from a markdown (.md) or HTML (.html) file. The PDF will be created in the same directory as the input file and automatically opened.",
        "parameters": {
            "type": "object",
            "properties": {
                "file_path": {
                    "type": "string",
                    "description": "Path to the markdown (.md) or HTML (.html) file to convert to PDF"
                }
            },
            "required": ["file_path"]
        }
    }
}

def generate_pdf(file_path: str) -> str:
    """Generate a PDF from a markdown or HTML file using the existing bash scripts"""
    
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
            script_name = "generate_pdf_from_markdown"
        elif file_extension == '.html':
            script_name = "generate_pdf_from_html"
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
        
        # Run the bash script
        result = subprocess.run(
            [str(script_path), str(input_path.absolute())],
            capture_output=True,
            text=True,
            cwd=str(project_root)
        )
        
        # Determine expected output PDF path
        pdf_path = input_path.parent / f"{input_path.stem}.pdf"
        
        if result.returncode == 0:
            # Success - save the process output for reference
            process_log = f"PDF Generation Log\n{'='*50}\n\nInput File: {file_path}\nScript Used: {script_name}\nOutput Path: {pdf_path}\n\nScript Output:\n{result.stdout}\n\nScript Errors (if any):\n{result.stderr}"
            
            saved_file = save(process_log, f"PDF generation log for {input_path.name}")
            
            return json.dumps({
                "success": True,
                "input_file": str(input_path.absolute()),
                "output_pdf": str(pdf_path),
                "file_type": file_extension[1:],  # Remove the dot
                "script_used": script_name,
                "process_log": saved_file["filepath"],
                "run_id": saved_file["run_id"],
                "summary": f"Successfully generated PDF from {file_extension[1:].upper()} file"
            }, indent=2)
        else:
            # Error occurred
            error_log = f"PDF Generation Error\n{'='*50}\n\nInput File: {file_path}\nScript Used: {script_name}\nReturn Code: {result.returncode}\n\nScript Output:\n{result.stdout}\n\nScript Errors:\n{result.stderr}"
            
            saved_file = save(error_log, f"PDF generation error log for {input_path.name}")
            
            return json.dumps({
                "error": "PDF generation failed",
                "input_file": str(input_path.absolute()),
                "file_type": file_extension[1:],
                "script_used": script_name,
                "return_code": result.returncode,
                "error_log": saved_file["filepath"],
                "stdout": result.stdout,
                "stderr": result.stderr
            }, indent=2)
            
    except Exception as e:
        return json.dumps({
            "error": f"Failed to generate PDF: {str(e)}",
            "file_path": file_path
        }, indent=2) 