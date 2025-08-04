# tools/research_prompt_rewriter.py
"""
Tool: research_prompt_rewriter
Description: Rewrite a user's initial research prompt into a detailed, comprehensive research brief and save it to the artifacts directory.

CLI Test:
    cd /path/to/oneshot
    python3 -c "
from tools.research_prompt_rewriter import research_prompt_rewriter
result = research_prompt_rewriter('Research the impact of AI on education')
print(result)
"
"""
from app.tool_services import *

TOOL_METADATA = {
    "type": "function",
    "function": {
        "name": "research_prompt_rewriter",
        "description": "Rewrite a user's initial research prompt into a detailed, comprehensive research brief which will be used to guide a subsequent research steps. The tool saves the research brief to the artifacts directory and returns the filepath so that it can be used in subsequent steps.",
        "parameters": {
            "type": "object",
            "properties": {
                "user_research_prompt": {
                    "type": "string", 
                    "description": "The user's initial research request or prompt that will be rewritten into a detailed research brief"
                },
                "filename": {
                    "type": "string", 
                    "description": "(Optional) The name that will be used for the output research brief file",
                    "default": "research_brief.md"
                }
            },
            "required": ["user_research_prompt"]
        }
    }
}

def research_prompt_rewriter(user_research_prompt: str, filename: str = "research_brief.md") -> str:
    """Rewrite a user's initial research prompt into a detailed research brief using openai/gpt-4o"""
    
    try:
        # Create the system prompt for research brief rewriting
        system_prompt = """You will be given a research task by a user. Your job is to produce a set of instructions for a researcher.

## GUIDELINES

### 1. **Maximise Specificity and Detail**

* Include all known user preferences and explicitly list key attributes or dimensions to consider.
* It is of utmost importance that all details from the user are included in the instructions.

### 2. **Fill in Unstated But Necessary Dimensions as Open-Ended**

* If certain attributes are essential for a meaningful output but the user has not provided them, add them as open-ended questions.

### 3. **Avoid Unwarranted Assumptions**

* If the user has not provided a particular detail, do not invent one.
* Instead, state the lack of specification and guide the researcher to treat it as flexible or ask the user to clarify.

### 4. **Use the First Person**

* Phrase the request from the perspective of the user.

### 5. **Tables**

* If you determine that including a table will help illustrate, organise, or enhance the information, request one.

**Examples:**

* **Product Comparison (Consumer):** When comparing different smartphone models, request a table listing key features, specs, and pricing.
* **Project Tracking (Work):** When outlining project deliverables, create a table showing tasks, deadlines, and responsibilities.
* **Budget Planning (Consumer):** When creating a personal or household budget, request a table detailing income and expenses.
* **Competitor Analysis (Work):** When evaluating competitor products, request a table with key metrics across each product.

### 6. **Headers and Formatting**

* You should include the expected output format in the prompt.
* If the user is asking for content that would be best returned in a structured format (e.g. a report, table, outline), specify this clearly.

### 7. **Language**

* If the user input is in a language other than English, tell the researcher to respond in this language.

### 8. **Sources**

* If specific sources should be prioritised, specify them in the prompt.

**Recommendations:**

* For product and travel research: Prefer linking directly to official or primary websites (e.g. manufacturer, hotel, airline).
* For academic or scientific queries: Prefer linking directly to the original paper or official journal site.
* For non-English queries: Prioritise sources published in that language.

Your output should be a comprehensive research brief written in markdown format that transforms the user's initial request into detailed instructions for a researcher."""

        # Use the openai/gpt-4o model to rewrite the research prompt
        research_brief = llm(
            user_research_prompt,
            model="openai/gpt-4o",
            system_prompt=system_prompt
        )
        
        # Save the research brief to the artifacts directory
        saved_file = save(
            research_brief,
            f"Research brief generated from user prompt",
            filename
        )
        
        return json.dumps({
            "success": True,
            "original_prompt": user_research_prompt,
            "research_brief_file": saved_file["filepath"],
            "model_used": "openai/gpt-4o",
            "run_id": saved_file["run_id"],
            "tokens": saved_file["frontmatter"]["tokens"],
            "summary": "User research prompt successfully rewritten into detailed research brief"
        }, indent=2)
        
    except Exception as e:
        return json.dumps({
            "error": f"Failed to rewrite research prompt: {str(e)}"
        }, indent=2)


# Test the tool if run directly
if __name__ == "__main__":
    # Test with a simple research prompt
    test_prompt = "I want to learn about AI adoption in small businesses in Australia"
    result = research_prompt_rewriter(test_prompt, "test_research_brief.md")
    print("Test Result:")
    print(result)
