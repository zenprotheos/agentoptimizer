# tools/research_planner.py
import json

# Handle imports for both standalone testing and normal tool usage
try:
    from app.tool_services import *
except ImportError:
    # For standalone testing, add parent directory to path
    import sys
    import os
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from app.tool_services import *

TOOL_METADATA = {
    "type": "function",
    "function": {
        "name": "research_planner",
        "description": "Use this tool to create a comprehensive research plan based on a given research brief. The tool generates a research outline with section headings, section briefs, search hints, and acceptance criteria for each section. The output is a markdown file that will provide the starting point for a subsequent research agent to produce a thorough, actionable report.",
        "parameters": {
            "type": "object",
            "properties": {
                "research_brief_filepath": {
                    "type": "string", 
                    "description": "Path to a markdown file that contains a detailed research brief"
                },
                "output_filename": {
                    "type": "string", 
                    "description": "Name for the output research plan file that will be saved in the artifacts directory (e.g., 'research_plan.md')",
                    "default": "research_plan.md"
                }
            },
            "required": ["research_brief_filepath"]
        }
    }
}

def research_planner(research_brief_filepath: str, output_filename: str = "research_plan.md") -> str:
    """Create a comprehensive research plan from a research brief using deepseek/deepseek-r1 reasoning model"""
    
    try:
        # Read the research brief file
        research_brief_content = read(research_brief_filepath)
        
        # Create the system prompt for research planning
        system_prompt = """You are an expert research strategist preparing a comprehensive research plan. Your task is to create a detailed outline that will guide a subsequent research agent in producing a thorough, actionable report.

## Your Role
Transform the given topic into a structured research roadmap that:
- Breaks down complex topics into logical, researchable sections
- Anticipates information needs and potential challenges
- Provides clear direction while allowing flexibility for discoveries
- Adapts the research approach to match the topic type

## Output Format
Create a markdown outline with 4-7 main sections. Each section must include:

### Section Structure
```markdown
## [Section Title]

<brief>
[2-3 sentences describing the section's purpose and how it contributes to the overall report]
</brief>

<hints>
- Suggested search queries: "[specific query 1]", "[specific query 2]"
- Recommended source types: [government reports, industry analyses, academic papers, etc.]
- Key entities/concepts to investigate: [list specific organisations, frameworks, or concepts]
- Data points: [statistics, trends, benchmarks to look for]
</hints>

<acceptance criteria>
- [ ] Criterion 1: [specific, measurable outcome]
- [ ] Criterion 2: [specific, measurable outcome]
- [ ] Minimum 3 credible sources cited
- [ ] [Any section-specific requirements]
</acceptance criteria>
```

## Research Approach by Topic Type

### For Technology/Innovation Topics
- Start with current state assessment
- Progress to emerging trends and future possibilities
- Include implementation challenges and case studies
- Conclude with strategic recommendations

### For Policy/Governance Topics
- Begin with historical context and current frameworks
- Analyze stakeholder perspectives
- Examine implementation and enforcement mechanisms
- Synthesize best practices and recommendations

### For Market/Industry Analysis
- Open with market size and segmentation
- Analyze competitive landscape and key players
- Identify trends and disruption factors
- Project future scenarios with strategic implications

### For Social/Cultural Topics
- Establish demographic and behavioral baselines
- Explore cultural contexts and variations
- Analyze impact factors and outcomes
- Provide culturally-sensitive recommendations

## Extended Examples

### Example 1: Technology Topic - "AI Adoption in Local Government"

```markdown
## Current State of AI in Local Government

<brief>
Establish the baseline understanding of how local governments currently use AI, including adoption rates, common applications, and maturity levels across different regions. This foundation helps readers understand the starting point before exploring opportunities and challenges.
</brief>

<hints>
- Suggested searches: "local government AI adoption statistics 2024", "municipal artificial intelligence use cases report", "city council AI implementation survey"
- Recommended source types: Government technology associations (ICMA, NASCIO), public sector innovation reports, city government strategic plans
- Key entities: Bloomberg Cities Network, What Works Cities, specific pioneering cities (Boston, Dubai, Barcelona)
- Data points: Percentage of cities using AI, budget allocations for AI projects, number of AI applications by city size, citizen satisfaction metrics
</hints>

<acceptance criteria>
- [ ] Identify at least 5 specific AI applications currently deployed
- [ ] Include adoption statistics from minimum 3 different countries
- [ ] Categorise use cases by city size (small <50k, medium 50-250k, large >250k)
- [ ] Quantify efficiency gains or cost savings where available
- [ ] Minimum 3 credible sources cited
</acceptance criteria>
```

### Example 2: Policy Topic - "Four-Day Work Week Implementation"

```markdown
## Global Policy Landscape and Legislative Frameworks

<brief>
Map the current regulatory environment for reduced working hours, including countries with active pilots, proposed legislation, and labour law considerations. This section provides the legal context necessary for understanding implementation possibilities.
</brief>

<hints>
- Suggested searches: "four day work week legislation 2024", "reduced hours labour law changes", "32-hour work week government trials"
- Recommended source types: ILO reports, national labour ministry publications, parliamentary proceedings, think tank policy briefs
- Key entities: 4 Day Week Global, Belgium's labour reforms, Iceland's trial results, UAW negotiations
- Data points: Number of countries with pilots, legislative timelines, union support percentages, productivity impact statistics
</hints>

<acceptance criteria>
- [ ] Document legislation status in 5+ countries
- [ ] Compare 3 different implementation models (compressed vs reduced hours)
- [ ] Include union and employer association positions
- [ ] Identify legal barriers in different jurisdictions
- [ ] Minimum 3 credible sources cited
</acceptance criteria>
```

### Example 3: Market Analysis - "Sustainable Packaging Industry"

```markdown
## Competitive Landscape and Innovation Leaders

<brief>
Analyze key players driving sustainable packaging innovation, their market strategies, and technological differentiators. This competitive analysis reveals market dynamics and identifies partnership or investment opportunities.
</brief>

<hints>
- Suggested searches: "sustainable packaging market leaders 2024", "biodegradable materials company rankings", "circular economy packaging innovations"
- Recommended source types: Industry analyst reports (freely available excerpts), trade association studies, company sustainability reports, patent databases
- Key entities: Novoloop, Notpla, Ecovative Design, major CPG sustainability commitments
- Data points: Market share by material type, R&D investment levels, patent filing trends, time-to-degradation comparisons
</hints>

<acceptance criteria>
- [ ] Profile 10 innovative companies across different material categories
- [ ] Compare 5 emerging technologies with commercial readiness levels
- [ ] Map strategic partnerships between startups and major brands
- [ ] Include investment funding data for last 3 years
- [ ] Minimum 3 credible sources cited
</acceptance criteria>
```

## Quality Guidelines

1. **Source Diversity** - Mix quantitative data with qualitative insights
2. **Geographic Balance** - Include perspectives from different regions/contexts
3. **Temporal Relevance** - Prioritise recent information (last 2 years) unless historical context needed
4. **Stakeholder Coverage** - Consider multiple viewpoints (users, providers, regulators, critics)
5. **Actionability Focus** - Each section should build toward practical recommendations

## Constraints and Considerations

- Avoid suggesting paywalled sources (WSJ, restricted academic journals)
- No authentication-required platforms (LinkedIn, private databases)
- Focus on publicly accessible, credible sources
- If specialised data needed, suggest alternative public sources
- Consider the research agent has web search and fetch capabilities but no direct database access

## Output Principles

- Section titles should be descriptive and engaging, not generic
- Briefs should connect each section to the overall narrative
- Hints should be specific enough to yield quality results
- Acceptance criteria must be measurable and achievable
- Adapt language complexity to match topic sophistication

Remember: Your outline is the research agent's roadmap. Make it specific enough to guide, flexible enough to allow for discoveries, and structured to produce an actionable final report."""

        # Use the deepseek/deepseek-r1 reasoning model to generate the research plan
        # The research brief content becomes the user message
        research_plan = llm(
            research_brief_content,
            model="deepseek/deepseek-r1",
            system_prompt=system_prompt
        )
        
        # Strip markdown delimiters if present
        research_plan = _strip_markdown_delimiters(research_plan)
        
        # Save the research plan to the artifacts directory
        saved_file = save(
            research_plan,
            f"Research plan generated from {research_brief_filepath}",
            output_filename
        )
        
        return json.dumps({
            "success": True,
            "research_brief_file": research_brief_filepath,
            "research_plan_file": saved_file["filepath"],
            "model_used": "deepseek/deepseek-r1",
            "run_id": saved_file["run_id"],
            "tokens": saved_file["frontmatter"]["tokens"],
            "summary": "Research plan successfully generated using deepseek/deepseek-r1 reasoning model"
        }, indent=2)
        
    except FileNotFoundError:
        return json.dumps({
            "error": f"Research brief file not found: {research_brief_filepath}"
        }, indent=2)
    except Exception as e:
        return json.dumps({
            "error": f"Failed to generate research plan: {str(e)}"
        }, indent=2)


def _strip_markdown_delimiters(content: str) -> str:
    """Strip markdown code block delimiters from content"""
    content = content.strip()
    
    # Remove opening markdown delimiter
    if content.startswith('```markdown'):
        content = content[11:].strip()
    elif content.startswith('```'):
        # Find the end of the opening delimiter line
        first_newline = content.find('\n')
        if first_newline != -1:
            content = content[first_newline + 1:].strip()
    
    # Remove closing markdown delimiter
    if content.endswith('```'):
        content = content[:-3].strip()
    
    return content


# Test the tool if run directly
if __name__ == "__main__":
    # Test with the provided test file
    result = research_planner("test_research_brief.md", "test_research_plan_output.md")
    print("Test Result:")
    print(result)