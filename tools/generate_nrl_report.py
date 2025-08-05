# tools/generate_nrl_report.py
"""
Tool: generate_nrl_report
Description: An example tool that shows an end to end process for creating a report artifact in a specific presentation template. The tool generate a comprehensive NRL match report by performing a search of live data, using openai/gpt-4o-mini-search-preview, returning a structured JSON response, populating a template HTML file, and generating a PDF.

CLI Test:
    cd /path/to/oneshot
    python3 -c "
from tools.generate_nrl_report import generate_nrl_report
result = generate_nrl_report('Cowboys vs Dragons, 25 July 2025')
print(result)
"
"""
from app.tool_services import *
import json
import shutil
import subprocess
import os
from pathlib import Path

TOOL_METADATA = {
    "type": "function",
    "function": {
        "name": "generate_nrl_report",
        "description": "Use this tool to generate a comprehensive NRL match report by researching live data and creating a PDF.",
        "parameters": {
            "type": "object",
            "properties": {
                "match_description": {
                    "type": "string", 
                    "description": "Use this to describe which match you want the match report generated for. This must be in the format: Team 1 vs Team 2 on date of the match (e.g. 'Cowboys vs Dragons, 25 July 2025')"
                },
                "model": {
                    "type": "string",
                    "description": "LLM model to use for research",
                    "default": "openai/gpt-4o-mini-search-preview"
                }
            },
            "required": ["match_description"]
        }
    }
}

def generate_nrl_report(match_description: str, model: str = "openai/gpt-4o-mini-search-preview") -> str:
    """Generate comprehensive NRL match report with web research and PDF creation"""
    
    try:
        run_id = get_run_id()
        # Get the project root directory dynamically
        project_root = Path(__file__).parent.parent
        artifacts_dir = project_root / "artifacts" / (run_id if run_id else "standalone")
        
        # Ensure artifacts directory exists
        os.makedirs(artifacts_dir, exist_ok=True)
        
        # Load the NRL match schema
        schema_content = read("snippets/nrl_match_jsonc.md")
        
        # Create the research prompt
        research_prompt = f"""You are an experienced and highly resourceful sports journalist and analyst. You have access to realtime sports data via web search. Your goal is to create a comprehensive match report for a recently played NRL rugby league game.

You first conceive of a plan to find the required information via web searches then you perform web research to curate the ingredient data that enables you to complete your match report. When you have completed the research, you produce the match report using JSON that conforms exactly to the provided MATCH REPORT SCHEMA. You ensure that you accurately populate as many of the fields in the schema as possible.

Remember, you are highly resourceful and work hard to complete this in detail using factual information from reliable web sources. Make sure to think step by step about the searches you should do to make this as complete as possible. Don't stop until you have completed.

--------

# MATCH TO REPORT ON

{match_description}

--------

{schema_content}

--------

Remember, You MUST reply in JSON format per the provided schema."""

        # Generate the match report JSON using web search
        print(f"🔍 Researching match: {match_description}")
        match_data_json = llm(
            research_prompt,
            model=model,
            system_prompt="You are a sports journalist with web search access. Research thoroughly and return only valid JSON matching the schema."
        )
        
        # Clean the JSON response (remove any markdown formatting)
        json_start = match_data_json.find('{')
        json_end = match_data_json.rfind('}') + 1
        if json_start != -1 and json_end != -1:
            clean_json = match_data_json[json_start:json_end]
        else:
            clean_json = match_data_json
            
        # Validate the JSON
        try:
            match_data = json.loads(clean_json)
        except json.JSONDecodeError as e:
            return json.dumps({
                "error": f"Invalid JSON generated: {str(e)}",
                "raw_response": match_data_json[:500] + "..."
            }, indent=2)
        
        # Save the JSON data as nrl.js
        nrl_js_content = f"const matchData = {json.dumps(match_data, indent=2)};"
        nrl_js_path = os.path.join(artifacts_dir, "nrl.js")
        with open(nrl_js_path, 'w') as f:
            f.write(nrl_js_content)
        
        # Copy the HTML template to artifacts directory
        html_template_path = "templates/nrl_match_report.html"
        html_output_path = os.path.join(artifacts_dir, "nrl_match_report.html")
        shutil.copy2(html_template_path, html_output_path)
        
        # Generate PDF using the pdf_from_html script
        print(f"📄 Generating PDF report...")
        pdf_script_path = os.path.join(os.getcwd(), "tools","bash_tools", "export_as_pdf_from_html")
        
        # Run the PDF generation script
        result = subprocess.run(
            [pdf_script_path, html_output_path],
            capture_output=True,
            text=True,
            cwd=os.getcwd()
        )
        
        if result.returncode != 0:
            return json.dumps({
                "error": f"PDF generation failed: {result.stderr}",
                "stdout": result.stdout
            }, indent=2)
        
        # Save the raw JSON data for reference
        json_file = save_json(match_data, f"NRL match data: {match_description}")
        
        # Get the PDF path
        pdf_path = html_output_path.replace('.html', '.pdf')
        
        return json.dumps({
            "success": True,
            "match_description": match_description,
            "artifacts_generated": {
                "json_data": nrl_js_path,
                "html_report": html_output_path,
                "pdf_report": pdf_path,
                "structured_data": json_file["filepath"]
            },
            "run_id": run_id,
            "artifacts_dir": str(artifacts_dir),
            "teams": f"{match_data.get('teams', {}).get('home', {}).get('name', 'Team 1')} vs {match_data.get('teams', {}).get('away', {}).get('name', 'Team 2')}",
            "final_score": f"{match_data.get('teams', {}).get('home', {}).get('score', 0)}-{match_data.get('teams', {}).get('away', {}).get('score', 0)}",
            "note": "PDF has been automatically opened. All artifacts are organized in the run directory."
        }, indent=2)
        
    except Exception as e:
        return json.dumps({
            "error": f"Report generation failed: {str(e)}",
            "match_description": match_description
        }, indent=2)


