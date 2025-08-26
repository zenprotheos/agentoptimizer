---
title: "Detailed File Organization Logic & Cross-Linking Strategy"
date: "2025-08-25T23:59:59.999Z"
task: "GlobalDocs_System_Analysis"
status: "Specification"
priority: "High"
tags: ["file-organization", "frontmatter", "cross-linking", "obsidian", "detailed-logic"]
---

# Detailed File Organization Logic & Cross-Linking Strategy

## File Organization Intelligence

### Session Organization Logic

#### 1. Session Creation
```python
# When a conversation starts - Updated with human-readable naming
def generate_session_name(run_id: str, context: str = None) -> str:
    """Generate human-readable session name using topic extraction"""
    if context:
        topic_keywords = extract_topic_keywords_heuristic(context)
        if topic_keywords:
            timestamp = datetime.now().strftime("%Y_%m%d_%H%M%S")
            return f"{topic_keywords}_{timestamp}"
    return run_id

def extract_topic_keywords_heuristic(content: str) -> str:
    """Extract topic keywords using simple heuristics"""
    content_words = content.lower().split()
    stop_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by'}
    meaningful_words = [word for word in content_words[:10] if word not in stop_words and len(word) > 2]
    return '_'.join(meaningful_words[:3]) if meaningful_words else None

def create_session_workspace(run_id: str, context: str = None) -> Path:
    # Generate human-readable session name using topic extraction
    session_name = generate_session_name(run_id, context)
    session_dir = vault_manager.sessions_path / session_name
    
    # AUTOMATIC: Create session structure
    structure = {
        "README.md": "session_overview_template",
        "artifacts/": "directory",
        "context/": "directory",  # For conversation context
        "temp/": "directory"      # For working files
    }
    
    # INTELLIGENT: Analyze initial context for smart organization
    session_type = detect_session_type(context)
    if session_type == "research":
        structure["research/"] = "directory"
        structure["sources/"] = "directory"
    elif session_type == "development":
        structure["code/"] = "directory"
        structure["docs/"] = "directory"
        structure["tests/"] = "directory"
    elif session_type == "analysis":
        structure["data/"] = "directory"
        structure["reports/"] = "directory"
```

#### 2. Dynamic Subfolder Creation
```python
class SessionOrganizer:
    def __init__(self, session_dir: Path):
        self.session_dir = session_dir
        self.organization_rules = {
            "code_files": ["code/", "src/"],
            "documentation": ["docs/", "documentation/"],
            "diagrams": ["diagrams/", "charts/"],
            "data_files": ["data/", "datasets/"],
            "images": ["images/", "assets/"],
            "research": ["research/", "references/"],
            "temp_files": ["temp/", "working/"]
        }
    
    def organize_file(self, filename: str, content: str) -> Path:
        """Intelligently organize file based on content and type"""
        
        # 1. ANALYZE FILE TYPE
        file_type = self._analyze_file_type(filename, content)
        
        # 2. ANALYZE CONTENT CONTEXT
        content_context = self._analyze_content_context(content)
        
        # 3. DETERMINE OPTIMAL LOCATION
        target_dir = self._get_target_directory(file_type, content_context)
        
        # 4. CREATE DIRECTORY IF NEEDED
        full_path = self.session_dir / target_dir
        full_path.mkdir(parents=True, exist_ok=True)
        
        return full_path / filename
    
    def _analyze_file_type(self, filename: str, content: str) -> str:
        """Determine file type from extension and content"""
        extension = Path(filename).suffix.lower()
        
        type_mapping = {
            '.py': 'code',
            '.js': 'code', 
            '.ts': 'code',
            '.md': self._analyze_markdown_type(content),
            '.json': self._analyze_json_type(content),
            '.png': 'image',
            '.jpg': 'image',
            '.pdf': 'document',
            '.csv': 'data',
            '.xlsx': 'data'
        }
        
        return type_mapping.get(extension, 'general')
    
    def _analyze_markdown_type(self, content: str) -> str:
        """Analyze markdown content to determine specific type"""
        if "```mermaid" in content:
            return "diagram"
        elif content.startswith("# ") and "## Analysis" in content:
            return "analysis"
        elif "## Test" in content or "test" in content.lower():
            return "test_doc"
        elif "```python" in content or "```javascript" in content:
            return "code_doc"
        else:
            return "documentation"
    
    def _get_target_directory(self, file_type: str, content_context: str) -> str:
        """Get target directory based on file type and context"""
        
        directory_logic = {
            "code": "code/",
            "documentation": "docs/",
            "diagram": "diagrams/",
            "analysis": "analysis/",
            "test_doc": "tests/",
            "code_doc": "docs/code/",
            "data": "data/",
            "image": "assets/images/",
            "document": "documents/",
            "general": "artifacts/"
        }
        
        base_dir = directory_logic.get(file_type, "artifacts/")
        
        # CONTEXT-SPECIFIC SUBDIRECTORIES
        if content_context and content_context != "general":
            return f"{base_dir}{content_context}/"
        
        return base_dir
```

### Project Organization Logic

#### 1. Project Structure Creation
```python
def create_project_structure(project_name: str, project_type: str = None) -> Dict:
    """Create intelligent project structure based on detected type"""
    
    # ANALYZE PROJECT TYPE from promoted session content
    if not project_type:
        project_type = detect_project_type(session_content)
    
    structures = {
        "software_development": {
            "docs/": {
                "README.md": "project_overview_template",
                "architecture/": "directory",
                "api/": "directory",
                "user_guides/": "directory"
            },
            "artifacts/": {
                "code/": "directory",
                "designs/": "directory", 
                "specifications/": "directory"
            },
            "sessions/": "directory",  # Links to contributing sessions
            "resources/": {
                "references/": "directory",
                "examples/": "directory"
            }
        },
        
        "research_project": {
            "docs/": {
                "README.md": "research_overview_template",
                "methodology/": "directory",
                "findings/": "directory",
                "literature_review/": "directory"
            },
            "artifacts/": {
                "data/": "directory",
                "analysis/": "directory",
                "reports/": "directory",
                "visualizations/": "directory"
            },
            "sessions/": "directory",
            "resources/": {
                "sources/": "directory",
                "datasets/": "directory"
            }
        },
        
        "documentation_project": {
            "docs/": {
                "README.md": "documentation_overview_template",
                "content/": "directory",
                "guides/": "directory",
                "references/": "directory"
            },
            "artifacts/": {
                "diagrams/": "directory",
                "examples/": "directory",
                "templates/": "directory"
            },
            "sessions/": "directory",
            "resources/": "directory"
        }
    }
    
    return structures.get(project_type, structures["software_development"])

def detect_project_type(session_artifacts: List[Path]) -> str:
    """Analyze session content to determine project type"""
    
    code_files = sum(1 for f in session_artifacts if f.suffix in ['.py', '.js', '.ts'])
    data_files = sum(1 for f in session_artifacts if f.suffix in ['.csv', '.json', '.xlsx'])
    doc_files = sum(1 for f in session_artifacts if f.suffix in ['.md'])
    
    # SCORING SYSTEM
    scores = {
        "software_development": code_files * 3 + (doc_files * 1),
        "research_project": data_files * 3 + (doc_files * 2),
        "documentation_project": doc_files * 3 + (code_files * 0.5)
    }
    
    return max(scores, key=scores.get)
```

## Frontmatter System

### Universal Frontmatter Strategy
Every file gets intelligent frontmatter for both oneshot tracking and Obsidian compatibility:

```python
def generate_frontmatter(file_path: Path, content: str, context: Dict) -> str:
    """Generate comprehensive frontmatter for Obsidian + oneshot compatibility"""
    
    # BASE METADATA (Always present)
    frontmatter = {
        # ONESHOT TRACKING
        "created": datetime.now().isoformat(),
        "run_id": context.get("run_id"),
        "session_id": context.get("session_id"),
        
        # OBSIDIAN COMPATIBILITY  
        "tags": generate_smart_tags(file_path, content, context),
        "type": determine_content_type(content),
        
        # CROSS-REFERENCING
        "related_files": find_related_files(content),
        "project": context.get("project_name"),
        "session": context.get("session_id")
    }
    
    # CONTENT-SPECIFIC METADATA
    if is_diagram(content):
        frontmatter.update({
            "diagram_type": detect_diagram_type(content),
            "mermaid_validated": validate_mermaid_syntax(content),
            "dependencies": extract_diagram_dependencies(content)
        })
    
    if is_code_file(file_path):
        frontmatter.update({
            "language": detect_language(file_path),
            "functions": extract_function_names(content),
            "imports": extract_imports(content)
        })
    
    if is_analysis(content):
        frontmatter.update({
            "analysis_type": detect_analysis_type(content),
            "data_sources": extract_data_sources(content),
            "conclusions": extract_key_conclusions(content)
        })
    
    return yaml.dump(frontmatter, default_flow_style=False)

def generate_smart_tags(file_path: Path, content: str, context: Dict) -> List[str]:
    """Generate intelligent tags for Obsidian filtering"""
    
    base_tags = ["oneshot"]
    
    # PROJECT/SESSION TAGS
    if context.get("project_name"):
        base_tags.append(f"project/{context['project_name']}")
    if context.get("session_id"):
        base_tags.append(f"session/{context['session_id']}")
    
    # CONTENT TYPE TAGS
    content_tags = {
        "mermaid": "diagram",
        "```python": "code/python", 
        "```javascript": "code/javascript",
        "## Analysis": "analysis",
        "## Test": "testing",
        "# Architecture": "architecture",
        "flowchart": "diagram/flowchart",
        "classDiagram": "diagram/class"
    }
    
    for pattern, tag in content_tags.items():
        if pattern in content:
            base_tags.append(tag)
    
    # DOMAIN-SPECIFIC TAGS
    domain_keywords = {
        "authentication": "security",
        "database": "data",
        "API": "api",
        "frontend": "ui",
        "backend": "server",
        "testing": "qa",
        "deployment": "devops"
    }
    
    content_lower = content.lower()
    for keyword, tag in domain_keywords.items():
        if keyword in content_lower:
            base_tags.append(f"domain/{tag}")
    
    return base_tags
```

## Cross-Linking Strategy

### Obsidian-Compatible Linking
```python
class ObsidianLinker:
    def __init__(self, vault_manager: VaultManager):
        self.vault_manager = vault_manager
        self.link_patterns = {
            "file_reference": r'\[\[([^\]]+)\]\]',          # [[filename]]
            "section_reference": r'\[\[([^\]]+)#([^\]]+)\]\]', # [[file#section]]
            "alias_reference": r'\[\[([^\]]+)\|([^\]]+)\]\]'   # [[file|alias]]
        }
    
    def create_cross_references(self, file_path: Path, content: str) -> str:
        """Automatically create Obsidian-style cross-references"""
        
        enhanced_content = content
        
        # 1. DETECT REFERENCES TO OTHER FILES
        file_references = self._detect_file_references(content)
        for ref in file_references:
            if self._file_exists_in_vault(ref):
                # Convert to Obsidian link: filename.md → [[filename]]
                obsidian_link = f"[[{ref}]]"
                enhanced_content = enhanced_content.replace(ref, obsidian_link)
        
        # 2. DETECT PROJECT REFERENCES
        project_references = self._detect_project_references(content)
        for project in project_references:
            project_link = f"[[projects/{project}]]"
            enhanced_content = enhanced_content.replace(project, project_link)
        
        # 3. DETECT SESSION REFERENCES  
        session_references = self._detect_session_references(content)
        for session in session_references:
            session_link = f"[[sessions/{session}]]"
            enhanced_content = enhanced_content.replace(session, session_link)
        
        # 4. ADD AUTOMATIC BACKLINKS SECTION
        backlinks_section = self._generate_backlinks_section(file_path)
        if backlinks_section:
            enhanced_content += f"\n\n## Related\n{backlinks_section}"
        
        return enhanced_content
    
    def _generate_backlinks_section(self, file_path: Path) -> str:
        """Generate automatic backlinks section"""
        
        backlinks = []
        
        # Find files that reference this file
        referencing_files = self._find_referencing_files(file_path)
        for ref_file in referencing_files:
            rel_path = ref_file.relative_to(self.vault_manager.vault_path)
            backlinks.append(f"- [[{rel_path.with_suffix('').as_posix()}]]")
        
        # Add session/project relationships
        if "sessions" in str(file_path):
            # Link to related project if promoted
            related_project = self._find_related_project(file_path)
            if related_project:
                backlinks.append(f"- Related Project: [[projects/{related_project}]]")
        
        elif "projects" in str(file_path):
            # Link to contributing sessions
            contributing_sessions = self._find_contributing_sessions(file_path)
            for session in contributing_sessions:
                backlinks.append(f"- Contributing Session: [[sessions/{session}]]")
        
        return "\n".join(backlinks) if backlinks else ""

def update_file_with_obsidian_features(file_path: Path, content: str, context: Dict) -> str:
    """Enhance file with full Obsidian compatibility"""
    
    # 1. ADD FRONTMATTER
    frontmatter = generate_frontmatter(file_path, content, context)
    
    # 2. PROCESS CROSS-LINKS
    linker = ObsidianLinker(vault_manager)
    linked_content = linker.create_cross_references(file_path, content)
    
    # 3. ADD OBSIDIAN-SPECIFIC FEATURES
    enhanced_content = add_obsidian_features(linked_content, context)
    
    # 4. COMBINE ALL ELEMENTS
    final_content = f"---\n{frontmatter}---\n\n{enhanced_content}"
    
    return final_content

def add_obsidian_features(content: str, context: Dict) -> str:
    """Add Obsidian-specific enhancements"""
    
    enhanced = content
    
    # ADD QUERY BLOCKS for dynamic content
    if context.get("project_name"):
        query_block = f'''
## Related Sessions
```query
path:"sessions/" AND tag:"project/{context['project_name']}"
```

## Project Files
```query
path:"projects/{context['project_name']}/"
```
'''
        enhanced += query_block
    
    # ADD DATAVIEW TABLES for structured data
    if "analysis" in context.get("tags", []):
        dataview_table = '''
## Analysis Overview
```dataview
TABLE file.ctime as "Created", tags as "Tags", type as "Type"
FROM "analysis"
SORT file.ctime DESC
```
'''
        enhanced += dataview_table
    
    return enhanced
```

## Implementation Example

### Session Creation Flow
```python
# Example: User starts conversation about "API authentication system"
run_id = "1225_143521_8492"
context = "Designing API authentication system with JWT tokens"

# 1. GENERATE HUMAN-READABLE SESSION NAME
session_name = generate_session_name(run_id, context)  # → "designing_api_authentication_2025_1225_143521"

# 2. DETECT SESSION TYPE
session_type = detect_session_type(context)  # → "development"

# 3. CREATE INTELLIGENT STRUCTURE
session_dir = create_session_workspace(run_id, context)
# Creates:
# vault/sessions/designing_api_authentication_2025_1225_143521/
# ├── README.md (with smart frontmatter)
# ├── code/          (auto-created for development type)
# ├── docs/
# ├── tests/
# └── artifacts/

# 3. FIRST FILE GENERATED: "JWT implementation guide"
content = """# JWT Authentication Implementation

## Overview
This guide covers implementing JWT authentication...

## Code Example
```python
def generate_jwt_token(user_id):
    payload = {'user_id': user_id, 'exp': datetime.utcnow()}
    return jwt.encode(payload, secret_key)
```
"""

# 4. INTELLIGENT FILE PLACEMENT
organizer = SessionOrganizer(session_dir)
file_path = organizer.organize_file("jwt_guide.md", content)
# → vault/sessions/designing_api_authentication_2025_1225_143521/docs/jwt_guide.md

# 5. ENHANCED WITH FRONTMATTER & LINKS
final_content = update_file_with_obsidian_features(file_path, content, {
    "run_id": run_id,
    "session_id": session_name,  # Human-readable session identifier
    "tags": ["development", "authentication", "jwt", "api"]
})

# RESULT:
"""
---
created: 2025-12-25T14:35:21.849Z
run_id: 1225_143521_8492
session_id: designing_api_authentication_2025_1225_143521
tags: [oneshot, session/designing_api_authentication_2025_1225_143521, code/python, domain/security]
type: documentation
related_files: []
---

# JWT Authentication Implementation

## Overview
This guide covers implementing JWT authentication...

## Code Example
```python
def generate_jwt_token(user_id):
    payload = {'user_id': user_id, 'exp': datetime.utcnow()}
    return jwt.encode(payload, secret_key)
```

## Related
- [[sessions/designing_api_authentication_2025_1225_143521]] - Parent Session
"""
```

### Project Promotion Flow
```python
# When session meets promotion criteria
project_name = "API_Authentication_System"
project_type = detect_project_type(session_artifacts)  # → "software_development"

# 1. CREATE PROJECT STRUCTURE
project_structure = create_project_structure(project_name, project_type)
# Creates:
# vault/projects/API_Authentication_System/
# ├── README.md
# ├── docs/
# │   ├── architecture/
# │   ├── api/
# │   └── user_guides/
# ├── artifacts/
# │   ├── code/
# │   ├── designs/
# │   └── specifications/
# ├── sessions/
# └── resources/

# 2. COPY & ORGANIZE SESSION ARTIFACTS
copy_with_intelligent_organization(session_dir, project_dir)
# JWT guide → vault/projects/API_Authentication_System/docs/api/jwt_guide.md
# Code files → vault/projects/API_Authentication_System/artifacts/code/
# Tests → vault/projects/API_Authentication_System/artifacts/tests/

# 3. CREATE CROSS-REFERENCES
create_bidirectional_links(session_name, project_name)
# Updates session README with: "Promoted to: [[projects/API_Authentication_System]]"
# Updates project README with: "Originated from: [[sessions/designing_api_authentication_2025_1225_143521]]"
```

This system provides intelligent, context-aware organization while maintaining full Obsidian compatibility through native linking and frontmatter systems.
