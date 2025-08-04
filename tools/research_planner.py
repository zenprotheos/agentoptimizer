# tools/research_planner.py
"""
Tool: research_planner
Description: Create a structured XML research plan from a research brief.

CLI Test:
    cd /path/to/oneshot
    python3 -c "
from tools.research_planner import research_planner
result = research_planner('test_data/sample_brief.md')
print(result)
"
"""
from app.tool_services import *

TOOL_METADATA = {
    "type": "function",
    "function": {
        "name": "research_planner",
        "description": "Creates a structured XML research plan from a research brief. The plan includes sections with briefs, hints, and acceptance criteria that guide systematic research execution using the WIP document system.",
        "parameters": {
            "type": "object",
            "properties": {
                "research_brief_filepath": {
                    "type": "string", 
                    "description": "Path to a markdown file containing the research brief"
                },
                "output_filename": {
                    "type": "string", 
                    "description": "Name for the output research plan file.Keep it short & end with *_plan.xml (e.g., 'algae_bloom_research_plan.xml')",
                    "default": "research_plan.xml"
                }
            },
            "required": ["research_brief_filepath"]
        }
    }
}

def research_planner(research_brief_filepath: str, output_filename: str = "research_plan.xml") -> str:
    """Create an XML-structured research plan from a research brief"""
    
    try:
        # Read the research brief file
        research_brief_content = read(research_brief_filepath)
        
        # Create the system prompt for research planning
        system_prompt = """You are an expert research strategist working as part of a team of specialist AI agents who collaborate to produce deep research reports on any given subject. You perform the first step in the process,  creating structured research plans that downstream agents will use to guide their research activities. You do that by generating an XML research plan that guides systematic research execution.

## Your Task
Carefully consider the research brief you are provided with and then thoughtfully transform it into a detailed XML-structured plan with 5-8 main sections that will be systematically researched and written by downstream research agents.

## Required XML Structure

```xml
<research-document status="draft">
  <section id="executive-summary" status="empty">
    <brief>Synthesize all findings into strategic overview highlighting key insights and recommendations</brief>
    <content></content>
  </section>
  
  <section id="[section-id]" status="empty">
    <brief>[2-3 sentences describing section purpose and contribution to overall research]</brief>
    <hints>
      <search>[specific search query 1]</search>
      <search>[specific search query 2]</search>
      <source>[recommended source type]</source>
      <entity>[key organization or concept to investigate]</entity>
    </hints>
    <acceptance>
      <criterion>Minimum 5 credible sources cited</criterion>
      <criterion>[Specific measurable outcome]</criterion>
      <criterion>[Required data points or analysis]</criterion>
    </acceptance>
    <content></content>
  </section>
  
  <!-- Additional sections -->
</research-document>
```

## Section Design Principles

### Section IDs
- Use lowercase with hyphens: current-state, market-analysis, technical-assessment
- Make them descriptive and unique
- Avoid generic IDs like section-1 or part-a

### Section Order by Topic Type

**Technology/Innovation Topics:**
1. executive-summary (always first, complete last)
2. current-state (baseline understanding)
3. technical-analysis (deep dive into technology)
4. implementation-cases (real-world examples)
5. challenges-barriers (obstacles and limitations)
6. future-outlook (emerging trends)
7. recommendations (strategic guidance)

**Market/Industry Analysis:**
1. executive-summary
2. market-overview (size, segments, growth)
3. competitive-landscape (key players, positioning)
4. customer-analysis (needs, behaviors, trends)
5. technology-disruptions (innovations impacting market)
6. financial-analysis (economics, ROI, costs)
7. strategic-opportunities (recommendations)

**Policy/Governance Topics:**
1. executive-summary
2. regulatory-landscape (current frameworks)
3. stakeholder-analysis (perspectives, interests)
4. implementation-mechanisms (how policies work)
5. comparative-analysis (different approaches)
6. impact-assessment (outcomes, effectiveness)
7. policy-recommendations (improvements)

**Scientific/Technical Research:**
1. executive-summary
2. literature-review (existing knowledge)
3. methodology-comparison (different approaches)
4. technical-findings (core research results)
5. performance-analysis (metrics, benchmarks)
6. applications (practical uses)
7. future-research (gaps, opportunities)

### Brief Guidelines
- Clearly state what the section will investigate
- Connect to overall research objective
- Indicate why this section matters

### Hints Structure
- 3-5 specific search queries per section
- Mix broad and narrow searches
- Include recent date qualifiers (2023-2024)
- Suggest authoritative source types
- Name specific entities, reports, or databases

### Acceptance Criteria
- Always require minimum source count (5+ for main sections)
- Include specific data requirements
- Set quality thresholds (e.g., "Compare at least 3 approaches")
- Make criteria verifiable and measurable

## Example Section for Quality Reference

```xml
<section id="techno-economic-comparison" status="empty">
  <brief>Compare enzymatic and chemical depolymerization routes focusing on process efficiency, cost structures, scalability, and environmental impact for cosmetic-grade oligosaccharide production.</brief>
  <hints>
    <search>techno-economic analysis enzymatic vs chemical depolymerization algal EPS 2023</search>
    <search>cost comparison oligosaccharides production enzymatic chemical route</search>
    <search>life cycle assessment algal polysaccharide processing cosmetics</search>
    <source>Bioprocess Engineering journals</source>
    <source>ACS Sustainable Chemistry reports</source>
    <entity>Novozymes enzyme technology</entity>
    <entity>BASF chemical processing</entity>
  </hints>
  <acceptance>
    <criterion>Minimum 5 peer-reviewed sources comparing both routes</criterion>
    <criterion>Include quantitative cost data ($/kg production)</criterion>
    <criterion>Compare at least 3 process parameters (yield, purity, time)</criterion>
    <criterion>Address environmental impact with LCA data</criterion>
  </acceptance>
  <content></content>
</section>
```

## Quality Requirements

1. **Section ids** - must use this naming convention: lowercase with hyphens
**Comprehensive Coverage** - Sections should collectively address all aspects of the research brief
2. **Logical Flow** - Order sections to build understanding progressively
3. **Research Depth** - Each section should require substantial investigation
4. **Actionable Outcomes** - Plan should lead to practical insights and recommendations
5. **Executive Summary** - Always include as first section, to be completed last

## Output Format
- Generate valid XML only
- No markdown formatting or code blocks
- Include 5-8 research sections plus executive summary
- All sections start with status="empty"
- All content tags should be empty (no placeholder text)
4. **Actionable Outcomes** - Plan should lead to practical insights and recommendations
5. **Executive Summary** - Always include as first section, to be completed last

## Output Format
- Generate valid XML only
- No markdown formatting or code blocks
- Include 5-8 research sections plus executive summary
- All sections start with status="empty"
- All content tags should be empty (no placeholder text)

Remember: This plan will guide systematic research execution. Make it specific enough to ensure comprehensive coverage while allowing flexibility for discoveries during research."""

        # Use the reasoning model to generate the research plan
        research_plan_xml = llm(
            research_brief_content,
            model="deepseek/deepseek-r1",
            system_prompt=system_prompt
        )
        
        # Clean up any markdown formatting if present
        research_plan_xml = _clean_xml_output(research_plan_xml)
        
        # Save the research plan
        saved_file = save(
            research_plan_xml,
            f"Research plan generated from {research_brief_filepath}",
            output_filename
        )
        
        return json.dumps({
            "success": True,
            "research_brief_file": research_brief_filepath,
            "research_plan_file": saved_file["filepath"],
            "format": "XML",
            "model_used": "deepseek/deepseek-r1",
            "run_id": saved_file["run_id"],
            "summary": "XML research plan generated for WIP document system"
        }, indent=2)
        
    except FileNotFoundError:
        return json.dumps({
            "error": f"Research brief file not found: {research_brief_filepath}"
        }, indent=2)
    except Exception as e:
        return json.dumps({
            "error": f"Failed to generate research plan: {str(e)}"
        }, indent=2)


def _clean_xml_output(content: str) -> str:
    """Remove any markdown formatting from XML output"""
    content = content.strip()
    
    # Remove markdown code blocks
    if content.startswith('```xml'):
        content = content[6:].strip()
    elif content.startswith('```'):
        first_newline = content.find('\n')
        if first_newline != -1:
            content = content[first_newline + 1:].strip()
    
    if content.endswith('```'):
        content = content[:-3].strip()
    
    return content


# Test the tool if run directly
if __name__ == "__main__":
    result = research_planner("test_research_brief.md", "test_research_plan.xml")
    print("Test Result:")
    print(result)