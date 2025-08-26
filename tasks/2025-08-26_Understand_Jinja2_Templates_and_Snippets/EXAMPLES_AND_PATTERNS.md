---
created: 2025-08-26T08:14:23.711Z
purpose: Practical examples and patterns for Jinja2 usage
---

# Jinja2 Examples & Patterns

## Dynamic Snippet Example

**File**: `snippets/dynamic_example.md`
```markdown
# User Info
Hello {{ username | default('Guest') }}!

{% if items %}
## Items:
{% for item in items %}
- {{ item }}
{% endfor %}
{% else %}
No items provided.
{% endif %}
```

**Usage in Agent**:
```markdown
---
name: test_agent
---

You are a test agent.

{% include "dynamic_example.md" %}
```

## Intelligent File Selection Agent

```markdown
---
name: file_selector_agent
tools:
  - read_file_contents
---

You intelligently select files from large sets.

{% if provided_filepaths %}
## Available Files:
{{ provided_filepaths | join(', ') }}

**Instructions:**
1. Analyze task requirements
2. Filter files by name/extension relevance
3. Read only the most relevant 2-3 files
4. Process efficiently
{% endif %}
```

## File Strategy Comparison

### Full Content (Small Files)
```markdown
{% if provided_files %}
## File Contents:
{% for filepath, content in provided_files.items() %}
### {{ filepath }}
```
{{ content }}
```
{% endfor %}
{% endif %}
```

### Path-Only (Large Sets)
```markdown
{% if provided_filepaths %}
## Files Available:
{% for filepath in provided_filepaths %}
- `{{ filepath }}`
{% endfor %}

Use tools to read selectively.
{% endif %}
```

### Mixed Strategy
```markdown
{% if provided_files_summary %}
## Overview:
{{ provided_files_summary }}
{% endif %}

{% if provided_filepaths %}
**Available**: {{ provided_filepaths | length }} files
Use read_file_contents for detailed analysis.
{% endif %}
```
