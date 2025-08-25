# tools/export_as_pdf.py
"""
Tool: export_as_pdf
Description: Use this tool to export a markdown (.md) or HTML (.html) file as a PDF. The PDF will be created in the same artifacts directory as the input file and automatically opened for the user to view.

CLI Test:
    cd /path/to/oneshot
    python3 -c "
from tools.export_as_pdf import export_as_pdf
result = export_as_pdf('test_data/sample.md')
print(result)
"
"""

from app.tool_services import *
import subprocess

TOOL_METADATA = {
    "type": "function",
    "function": {
        "name": "export_as_pdf",
        "description": "Use this tool to generate a PDF from a markdown (.md) or HTML (.html) file. The PDF will be created in the same artifacts directory as the input file and automatically opened for the user to view.",
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

def export_as_pdf(file_path: str) -> str:
    """Use this tool to export a markdown (.md) or HTML (.html) file as a PDF. The PDF will be created in the same artifacts directory as the input file and automatically opened for the user to view."""
    
    try:
        # Validate file path
        input_path = Path(file_path)
        if not input_path.exists():
            return json.dumps({
                "error": f"File not found: {file_path}"
            }, indent=2)
        
        # Determine file type
        file_extension = input_path.suffix.lower()
        
        if file_extension not in ['.md', '.html']:
            return json.dumps({
                "error": f"Unsupported file type: {file_extension}. Only .md and .html files are supported."
            }, indent=2)
        
        # Windows-compatible PDF generation using Python
        project_root = Path(__file__).parent.parent
        pdf_path = input_path.parent / f"{input_path.stem}.pdf"
        
        try:
            # Try to generate PDF using weasyprint (if available)
            success = _generate_pdf_weasyprint(input_path, pdf_path, file_extension)
            if success:
                method = "weasyprint"
            else:
                # Fallback to playwright/puppeteer approach
                success = _generate_pdf_playwright(input_path, pdf_path, file_extension)
                method = "playwright" if success else "failed"
        except Exception as e:
            # Final fallback - create a simple PDF with the text content
            success = _generate_simple_pdf(input_path, pdf_path, file_extension)
            method = "simple_pdf" if success else "failed"
        
        if success:
            # Success - save the process output for reference
            process_log = f"PDF Generation Log\n{'='*50}\n\nInput File: {file_path}\nMethod Used: {method}\nOutput Path: {pdf_path}\n\nStatus: Success"
            
            saved_file = save(process_log, f"PDF generation log for {input_path.name}")
            
            return json.dumps({
                "success": True,
                "input_file": str(input_path.absolute()),
                "output_pdf": str(pdf_path),
                "file_type": file_extension[1:],  # Remove the dot
                "method_used": method,
                "process_log": saved_file["filepath"],
                "run_id": saved_file["run_id"],
                "summary": f"Successfully generated PDF from {file_extension[1:].upper()} file using {method}"
            }, indent=2)
        else:
            # Error occurred
            error_log = f"PDF Generation Error\n{'='*50}\n\nInput File: {file_path}\nMethod Attempted: {method}\n\nStatus: Failed - unable to generate PDF with any available method"
            
            saved_file = save(error_log, f"PDF generation error log for {input_path.name}")
            
            return json.dumps({
                "error": "PDF generation failed - no available PDF generation methods worked",
                "input_file": str(input_path.absolute()),
                "file_type": file_extension[1:],
                "method_attempted": method,
                "error_log": saved_file["filepath"],
                "suggestions": [
                    "Install weasyprint: pip install weasyprint",
                    "Install playwright: pip install playwright",
                    "Ensure system dependencies are available"
                ]
            }, indent=2)
            
    except Exception as e:
        return json.dumps({
            "error": f"Failed to generate PDF: {str(e)}",
            "file_path": file_path
        }, indent=2)

def _generate_pdf_weasyprint(input_path: Path, pdf_path: Path, file_extension: str) -> bool:
    """Try to generate PDF using weasyprint library"""
    try:
        import weasyprint
        
        if file_extension == '.md':
            # Convert markdown to HTML first
            html_content = _markdown_to_html(input_path)
        else:
            html_content = input_path.read_text(encoding='utf-8')
        
        # Generate PDF
        weasyprint.HTML(string=html_content).write_pdf(str(pdf_path))
        return pdf_path.exists()
    except ImportError:
        return False
    except Exception:
        return False

def _generate_pdf_playwright(input_path: Path, pdf_path: Path, file_extension: str) -> bool:
    """Try to generate PDF using playwright library"""
    try:
        from playwright.sync_api import sync_playwright
        
        if file_extension == '.md':
            # Convert markdown to HTML first
            html_content = _markdown_to_html(input_path)
            # Create temporary HTML file
            temp_html = input_path.parent / f"{input_path.stem}_temp.html"
            temp_html.write_text(html_content, encoding='utf-8')
            file_url = f"file:///{temp_html.absolute().as_posix()}"
        else:
            file_url = f"file:///{input_path.absolute().as_posix()}"
        
        with sync_playwright() as p:
            browser = p.chromium.launch()
            page = browser.new_page()
            page.goto(file_url)
            page.pdf(path=str(pdf_path))
            browser.close()
        
        # Clean up temp file if created
        if file_extension == '.md' and temp_html.exists():
            temp_html.unlink()
        
        return pdf_path.exists()
    except ImportError:
        return False
    except Exception:
        return False

def _generate_simple_pdf(input_path: Path, pdf_path: Path, file_extension: str) -> bool:
    """Generate a simple PDF using reportlab as fallback"""
    try:
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
        from reportlab.lib.styles import getSampleStyleSheet
        from reportlab.lib.pagesizes import letter
        
        # Read content
        if file_extension == '.md':
            content = _markdown_to_text(input_path)
        else:
            content = _html_to_text(input_path)
        
        # Create PDF
        doc = SimpleDocTemplate(str(pdf_path), pagesize=letter)
        styles = getSampleStyleSheet()
        story = []
        
        # Add title
        title = Paragraph(f"Exported from {input_path.name}", styles['Title'])
        story.append(title)
        story.append(Spacer(1, 12))
        
        # Add content paragraphs
        for line in content.split('\n'):
            if line.strip():
                para = Paragraph(line.strip(), styles['Normal'])
                story.append(para)
                story.append(Spacer(1, 6))
        
        doc.build(story)
        return pdf_path.exists()
    except ImportError:
        return False
    except Exception:
        return False

def _markdown_to_html(md_path: Path) -> str:
    """Convert markdown to HTML"""
    try:
        import markdown
        content = md_path.read_text(encoding='utf-8')
        
        # Strip frontmatter if present
        if content.startswith('---'):
            parts = content.split('---', 2)
            if len(parts) >= 3:
                content = parts[2].strip()
        
        # Convert to HTML with basic styling
        html = markdown.markdown(content)
        
        # Wrap in complete HTML document
        return f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <style>
        body {{ font-family: Arial, sans-serif; max-width: 800px; margin: 0 auto; padding: 20px; }}
        h1, h2, h3 {{ color: #333; }}
        pre {{ background: #f5f5f5; padding: 10px; }}
    </style>
</head>
<body>
{html}
</body>
</html>"""
    except ImportError:
        # Fallback without markdown processing
        content = md_path.read_text(encoding='utf-8')
        return f"<html><body><pre>{content}</pre></body></html>"

def _markdown_to_text(md_path: Path) -> str:
    """Convert markdown to plain text"""
    content = md_path.read_text(encoding='utf-8')
    # Strip frontmatter if present
    if content.startswith('---'):
        parts = content.split('---', 2)
        if len(parts) >= 3:
            content = parts[2].strip()
    return content

def _html_to_text(html_path: Path) -> str:
    """Extract text from HTML"""
    try:
        from bs4 import BeautifulSoup
        content = html_path.read_text(encoding='utf-8')
        soup = BeautifulSoup(content, 'html.parser')
        return soup.get_text()
    except ImportError:
        # Fallback without HTML parsing
        content = html_path.read_text(encoding='utf-8')
        # Basic HTML tag removal
        import re
        return re.sub(r'<[^>]+>', '', content) 