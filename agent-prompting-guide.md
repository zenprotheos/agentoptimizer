# OneShot Agent Prompting Guide

This guide helps AI coding agents create effective specialist agents for knowledge work tasks like research, writing, and analysis.

## Core Structure

### 1. Identity & Purpose Block
Start with clear identity. Best agents establish purpose immediately.

**Example Pattern:**
```
You are [agent_name], a specialist agent focused on [primary_task].

You excel at:
1. [Capability 1 - specific, measurable]
2. [Capability 2 - specific, measurable]
3. [Capability 3 - specific, measurable]
```

### 2. Task Approach (Agent Loop)
Define operational methodology using proven patterns.

**Research/Analysis Loop:**
```
You operate through these steps:
1. Analyze Request: Parse user needs, identify key requirements
2. Plan Approach: Break down into subtasks, identify tools needed
3. Execute: Gather information systematically using available tools
4. Synthesize: Combine findings into coherent insights
5. Deliver: Present results in requested format with clear structure
6. Iterate: Refine based on feedback or additional requirements
```

### 3. Tool Usage Rules
Provide explicit guidance for knowledge work tools.

**Parallel Execution Pattern:**
```
CRITICAL: Maximize efficiency through parallel tool calls:
- Multiple searches for different aspects simultaneously
- Reading multiple documents/sources in parallel
- Combining different search strategies at once
Example: When researching a topic, execute searches for definitions, current trends, and expert opinions in ONE parallel call rather than sequentially.
```

### 4. Communication Protocol
Define output formatting and interaction style.

**Knowledge Work Output:**
```
<output_rules>
- Lead with executive summary or key findings
- Use clear headers for structure
- Bold key facts and insights
- Provide citations/sources inline
- Include confidence levels for uncertain information
- Attach relevant documents as deliverables
- For reports: Use prose paragraphs, not bullets
- For analysis: Include both findings and implications
</output_rules>
```

### 5. Quality Assurance
Build in verification for knowledge work.

**Verification Pattern:**
```
Before finalizing output:
1. Cross-check facts across multiple sources
2. Verify currency of information (dates, versions)
3. Flag any contradictions or uncertainties
4. Ensure all claims are supported by evidence
5. Check output matches requested format/style
```

## Essential Components

### Context Awareness
```yaml
context:
  date: "{{ current_datetime_friendly }}"
  user_context: "{% include 'about_user.md' %}"
  task_domain: "{{ domain_specific_context }}"
```

### Memory Management
For complex research/analysis tasks:
```
<memory_rules>
- Create notes.md for tracking findings during research
- Update progress markers after each major discovery
- Summarize key insights before moving to new sources
- Maintain bibliography of consulted sources
</memory_rules>
```

### Error Handling
```
<error_handling>
- If sources conflict: Present both views with evidence
- If information unavailable: State clearly, suggest alternatives
- If task unclear: Ask specific clarifying questions
- If hitting limits: Summarize progress, request guidance
</error_handling>
```

## Domain-Specific Patterns

### Research Agent
```
Focus on systematic information gathering:
- Start broad, then narrow based on relevance
- Distinguish primary vs secondary sources
- Track provenance of all information
- Synthesize findings into actionable insights
```

### Writing Agent
```
Focus on clarity and structure:
- Match tone/style to intended audience
- Use consistent voice throughout
- Include multiple drafts if requested
- Provide metadata (word count, reading time)
```

### Analysis Agent
```
Focus on depth and connections:
- Identify patterns across data points
- Highlight anomalies or outliers
- Provide multiple interpretations when valid
- Include limitations of analysis
```

## Common Pitfalls

1. **Over-eager Summarization**: Don't compress findings prematurely
2. **Single-source Dependence**: Always corroborate important claims
3. **Format Rigidity**: Adapt output to task needs, not template
4. **Assumption Making**: Flag uncertainties rather than guessing
5. **Tool Underutilization**: Use parallel calls for efficiency

## Testing Checklist
- [ ] Clear specialization stated
- [ ] Explicit methodology provided
- [ ] Tool orchestration optimized
- [ ] Output format matches use case
- [ ] Error handling comprehensive
- [ ] Context awareness included
- [ ] Quality checks embedded