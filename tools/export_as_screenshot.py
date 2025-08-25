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
        
        # Determine file type
        file_extension = input_path.suffix.lower()
        
        if file_extension not in ['.md', '.html']:
            return json.dumps({
                "error": f"Unsupported file type: {file_extension}. Only .md and .html files are supported."
            }, indent=2)
        
        # Windows-compatible screenshot generation using Python
        project_root = Path(__file__).parent.parent
        
        # Determine output path
        if visible_only:
            png_path = input_path.parent / f"{input_path.stem}-viewport.png"
        else:
            png_path = input_path.parent / f"{input_path.stem}-fullpage.png"
        
        try:
            # Try Windows-optimized selenium with webdriver-manager first
            success = _generate_screenshot_selenium_auto(input_path, png_path, file_extension, visible_only)
            if success:
                method = "selenium_auto"
            else:
                # Fallback to playwright
                success = _generate_screenshot_playwright(input_path, png_path, file_extension, visible_only)
                if success:
                    method = "playwright"
                else:
                    # Final fallback - simple image
                    success = _generate_simple_screenshot(input_path, png_path, file_extension)
                    method = "simple_image" if success else "failed"
        except Exception as e:
            # Emergency fallback - create a simple image with text
            success = _generate_simple_screenshot(input_path, png_path, file_extension)
            method = "simple_image_emergency" if success else "failed"
        
        if success:
            # Success - save the process output for reference
            process_log = f"Screenshot Generation Log\n{'='*50}\n\nInput File: {file_path}\nMethod Used: {method}\nOutput Path: {png_path}\nVisible Only: {visible_only}\n\nStatus: Success"
            
            saved_file = save(process_log, f"Screenshot generation log for {input_path.name}")
            
            return json.dumps({
                "success": True,
                "input_file": str(input_path.absolute()),
                "output_screenshot": str(png_path),
                "file_type": file_extension[1:],  # Remove the dot
                "method_used": method,
                "visible_only": visible_only,
                "screenshot_type": "viewport" if visible_only else "fullpage",
                "process_log": saved_file["filepath"],
                "run_id": saved_file["run_id"],
                "summary": f"Successfully generated {'viewport' if visible_only else 'fullpage'} screenshot from {file_extension[1:].upper()} file using {method}"
            }, indent=2)
        else:
            # Error occurred
            error_log = f"Screenshot Generation Error\n{'='*50}\n\nInput File: {file_path}\nMethod Attempted: {method}\nVisible Only: {visible_only}\n\nStatus: Failed - unable to generate screenshot with any available method"
            
            saved_file = save(error_log, f"Screenshot generation error log for {input_path.name}")
            
            return json.dumps({
                "error": "Screenshot generation failed - no available screenshot generation methods worked",
                "input_file": str(input_path.absolute()),
                "file_type": file_extension[1:],
                "method_attempted": method,
                "visible_only": visible_only,
                "error_log": saved_file["filepath"],
                "suggestions": [
                    "Install playwright: pip install playwright",
                    "Install selenium: pip install selenium",
                    "Install Pillow: pip install Pillow",
                    "Ensure Chrome/Edge browser is available"
                ]
            }, indent=2)
            
    except Exception as e:
        return json.dumps({
            "error": f"Failed to generate screenshot: {str(e)}",
            "file_path": file_path
        }, indent=2)

def _generate_screenshot_playwright(input_path: Path, png_path: Path, file_extension: str, visible_only: bool) -> bool:
    """Try to generate screenshot using playwright library"""
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
            page.set_viewport_size({"width": 1920, "height": 1080})
            page.goto(file_url)
            
            if visible_only:
                page.screenshot(path=str(png_path), clip={"x": 0, "y": 0, "width": 1920, "height": 1080})
            else:
                page.screenshot(path=str(png_path), full_page=True)
            
            browser.close()
        
        # Clean up temp file if created
        if file_extension == '.md' and temp_html.exists():
            temp_html.unlink()
        
        return png_path.exists()
    except ImportError:
        return False
    except Exception:
        return False

def _generate_screenshot_selenium_auto(input_path: Path, png_path: Path, file_extension: str, visible_only: bool) -> bool:
    """Try to generate screenshot using selenium with automatic Windows webdriver management"""
    try:
        from selenium import webdriver
        from selenium.webdriver.chrome.options import Options
        from webdriver_manager.chrome import ChromeDriverManager
        from selenium.webdriver.chrome.service import Service
        
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--window-size=1920,1080")
        
        if file_extension == '.md':
            # Convert markdown to HTML first
            html_content = _markdown_to_html(input_path)
            # Create temporary HTML file
            temp_html = input_path.parent / f"{input_path.stem}_temp.html"
            temp_html.write_text(html_content, encoding='utf-8')
            file_url = f"file:///{temp_html.absolute().as_posix()}"
        else:
            file_url = f"file:///{input_path.absolute().as_posix()}"
        
        # Auto-download and manage Chrome driver for Windows
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=chrome_options)
        
        driver.get(file_url)
        
        if visible_only:
            driver.set_window_size(1920, 1080)
        
        driver.save_screenshot(str(png_path))
        driver.quit()
        
        # Clean up temp file if created
        if file_extension == '.md' and temp_html.exists():
            temp_html.unlink()
        
        return png_path.exists()
    except ImportError:
        return False
    except Exception:
        return False

def _generate_screenshot_selenium(input_path: Path, png_path: Path, file_extension: str, visible_only: bool) -> bool:
    """Try to generate screenshot using selenium library"""
    try:
        from selenium import webdriver
        from selenium.webdriver.chrome.options import Options
        
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--window-size=1920,1080")
        
        if file_extension == '.md':
            # Convert markdown to HTML first
            html_content = _markdown_to_html(input_path)
            # Create temporary HTML file
            temp_html = input_path.parent / f"{input_path.stem}_temp.html"
            temp_html.write_text(html_content, encoding='utf-8')
            file_url = f"file:///{temp_html.absolute().as_posix()}"
        else:
            file_url = f"file:///{input_path.absolute().as_posix()}"
        
        driver = webdriver.Chrome(options=chrome_options)
        driver.get(file_url)
        
        if visible_only:
            driver.set_window_size(1920, 1080)
        
        driver.save_screenshot(str(png_path))
        driver.quit()
        
        # Clean up temp file if created
        if file_extension == '.md' and temp_html.exists():
            temp_html.unlink()
        
        return png_path.exists()
    except ImportError:
        return False
    except Exception:
        return False

def _generate_simple_screenshot(input_path: Path, png_path: Path, file_extension: str) -> bool:
    """Generate a simple image with text as fallback"""
    try:
        from PIL import Image, ImageDraw, ImageFont
        
        # Read content
        if file_extension == '.md':
            content = _markdown_to_text(input_path)
        else:
            content = _html_to_text(input_path)
        
        # Create image
        img = Image.new('RGB', (1920, 1080), color='white')
        draw = ImageDraw.Draw(img)
        
        try:
            font = ImageFont.truetype("arial.ttf", 16)
        except:
            font = ImageFont.load_default()
        
        # Add title
        draw.text((50, 50), f"Screenshot from {input_path.name}", fill='black', font=font)
        
        # Add content (word wrap)
        y_position = 100
        words = content.split()
        line = ""
        max_width = 1800
        
        for word in words[:500]:  # Limit to first 500 words
            test_line = line + word + " "
            bbox = draw.textbbox((0, 0), test_line, font=font)
            if bbox[2] <= max_width:
                line = test_line
            else:
                if line:
                    draw.text((50, y_position), line.strip(), fill='black', font=font)
                    y_position += 25
                    line = word + " "
                    
                    if y_position > 1000:  # Stop if we're near the bottom
                        break
        
        # Draw remaining line
        if line and y_position <= 1000:
            draw.text((50, y_position), line.strip(), fill='black', font=font)
        
        img.save(str(png_path), 'PNG')
        return png_path.exists()
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
        body {{ font-family: Arial, sans-serif; max-width: 800px; margin: 0 auto; padding: 20px; background: white; }}
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
        return f"<html><body style='background:white; padding:20px;'><pre>{content}</pre></body></html>"

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