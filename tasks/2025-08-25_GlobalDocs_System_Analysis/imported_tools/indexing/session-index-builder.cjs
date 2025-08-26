#!/usr/bin/env node

/**
 * Session Index Builder - Enhanced version of build-index.cjs for OneShot sessions
 * Generates lightweight session indexes for intelligent context management
 * Based on existing build-index.cjs but optimized for session artifacts
 */

const fs = require('fs');
const path = require('path');

class SessionIndexBuilder {
    constructor(sessionPath = null) {
        this.documents = [];
        this.sessionPath = sessionPath || this.detectSessionPath();
        this.indexFile = path.join(this.sessionPath, 'SESSION_INDEX.md');
        this.metadataCache = new Map();
    }

    detectSessionPath() {
        // Auto-detect if running from a session directory
        const cwd = process.cwd();
        if (cwd.includes('artifacts') || cwd.includes('vault/sessions')) {
            return cwd;
        }
        // Default to artifacts if no session specified
        return path.join('artifacts', this.getLatestRunId());
    }

    getLatestRunId() {
        try {
            const artifactsDir = 'artifacts';
            if (!fs.existsSync(artifactsDir)) return 'default_session';
            
            const runDirs = fs.readdirSync(artifactsDir)
                .filter(dir => fs.statSync(path.join(artifactsDir, dir)).isDirectory())
                .sort((a, b) => b.localeCompare(a)); // Latest first
            
            return runDirs[0] || 'default_session';
        } catch (error) {
            return 'default_session';
        }
    }

    scanSessionDirectory() {
        if (!fs.existsSync(this.sessionPath)) {
            console.error(`❌ Session path does not exist: ${this.sessionPath}`);
            return;
        }

        const items = fs.readdirSync(this.sessionPath);
        for (const item of items) {
            const fullPath = path.join(this.sessionPath, item);
            const stat = fs.statSync(fullPath);
            
            if (stat.isFile() && path.extname(item) === '.md') {
                this.processMarkdownFile(fullPath);
            } else if (stat.isFile()) {
                this.processNonMarkdownFile(fullPath);
            }
        }
    }

    processMarkdownFile(filePath) {
        try {
            const content = fs.readFileSync(filePath, 'utf8');
            const frontMatterMatch = content.match(/^---\n([\s\S]*?)\n---/);
            const stats = fs.statSync(filePath);
            const fileName = path.basename(filePath);
            
            let frontMatter = {};
            if (frontMatterMatch) {
                frontMatter = this.parseFrontMatter(frontMatterMatch[1]);
            }

            // Extract content summary (first 200 chars after front matter)
            const contentWithoutFrontMatter = frontMatterMatch 
                ? content.replace(frontMatterMatch[0], '').trim()
                : content;
            const summary = this.extractContentSummary(contentWithoutFrontMatter);

            const document = {
                path: fileName,
                fullPath: filePath,
                title: frontMatter.title || frontMatter.name || fileName.replace('.md', ''),
                purpose: frontMatter.purpose || frontMatter.description || summary,
                type: frontMatter.type || this.inferFileType(fileName),
                priority: frontMatter.priority || this.inferPriority(fileName, frontMatter),
                tags: frontMatter.tags || [],
                created: frontMatter.created || stats.birthtime.toISOString(),
                modified: stats.mtime.toISOString(),
                size: stats.size,
                tokenEstimate: Math.ceil(content.length / 4), // Rough token estimate
                hasContent: contentWithoutFrontMatter.length > 100,
                status: frontMatter.status || 'unknown'
            };

            this.documents.push(document);
            this.metadataCache.set(filePath, document);
        } catch (error) {
            console.error(`❌ Error processing ${filePath}:`, error.message);
        }
    }

    processNonMarkdownFile(filePath) {
        try {
            const stats = fs.statSync(filePath);
            const fileName = path.basename(filePath);
            const ext = path.extname(fileName);

            const document = {
                path: fileName,
                fullPath: filePath,
                title: fileName,
                purpose: `${ext.substring(1).toUpperCase()} file`,
                type: this.inferFileTypeFromExtension(ext),
                priority: 'Low',
                tags: [ext.substring(1)],
                created: stats.birthtime.toISOString(),
                modified: stats.mtime.toISOString(),
                size: stats.size,
                tokenEstimate: 0, // Non-markdown files not directly tokenized
                hasContent: stats.size > 0,
                status: 'file'
            };

            this.documents.push(document);
        } catch (error) {
            console.error(`❌ Error processing ${filePath}:`, error.message);
        }
    }

    extractContentSummary(content) {
        // Extract first meaningful sentence or paragraph
        const lines = content.split('\n').filter(line => line.trim().length > 0);
        for (const line of lines) {
            if (!line.startsWith('#') && line.length > 20) {
                return line.substring(0, 200) + (line.length > 200 ? '...' : '');
            }
        }
        return 'No description available';
    }

    inferFileType(fileName) {
        const lowerName = fileName.toLowerCase();
        if (lowerName.includes('master') || lowerName.includes('architecture')) return 'architecture';
        if (lowerName.includes('test')) return 'test';
        if (lowerName.includes('readme')) return 'documentation';
        if (lowerName.includes('implementation') || lowerName.includes('plan')) return 'planning';
        if (lowerName.includes('troubleshooting') || lowerName.includes('debug')) return 'troubleshooting';
        if (lowerName.includes('progress') || lowerName.includes('tracker')) return 'tracking';
        return 'document';
    }

    inferFileTypeFromExtension(ext) {
        const typeMap = {
            '.py': 'code',
            '.js': 'code',
            '.ts': 'code',
            '.json': 'data',
            '.yaml': 'config',
            '.yml': 'config',
            '.txt': 'text',
            '.log': 'log',
            '.pdf': 'document',
            '.png': 'image',
            '.jpg': 'image',
            '.jpeg': 'image'
        };
        return typeMap[ext.toLowerCase()] || 'file';
    }

    inferPriority(fileName, frontMatter) {
        const lowerName = fileName.toLowerCase();
        if (frontMatter.priority) return frontMatter.priority;
        if (lowerName.includes('master') || lowerName.includes('final')) return 'High';
        if (lowerName.includes('temp') || lowerName.includes('debug') || lowerName.includes('test')) return 'Low';
        if (lowerName.includes('implementation') || lowerName.includes('architecture')) return 'High';
        return 'Medium';
    }

    parseFrontMatter(yamlContent) {
        const frontMatter = {};
        yamlContent.split('\n').forEach(line => {
            const match = line.match(/^(\w+):\s*(.*)$/);
            if (match) {
                const key = match[1];
                let value = match[2].trim();
                
                // Remove quotes
                if ((value.startsWith('"') && value.endsWith('"')) || 
                    (value.startsWith('\'') && value.endsWith('\''))) {
                    value = value.slice(1, -1);
                }
                
                // Parse arrays
                if (value.startsWith('[') && value.endsWith(']')) {
                    value = value.slice(1, -1).split(',')
                        .map(item => item.trim().replace(/["']/g, ''))
                        .filter(item => item.length > 0);
                }
                
                frontMatter[key] = value;
            }
        });
        return frontMatter;
    }

    generateSessionIndex() {
        // Sort documents by priority and type
        this.documents.sort((a, b) => {
            const priorityOrder = { 'High': 3, 'Medium': 2, 'Low': 1 };
            const aPriority = priorityOrder[a.priority] || 2;
            const bPriority = priorityOrder[b.priority] || 2;
            
            if (aPriority !== bPriority) return bPriority - aPriority;
            if (a.type !== b.type) return a.type.localeCompare(b.type);
            return a.title.localeCompare(b.title);
        });

        return this.buildSessionIndexMarkdown();
    }

    buildSessionIndexMarkdown() {
        const sessionId = path.basename(this.sessionPath);
        const now = new Date().toISOString();
        const totalTokens = this.documents.reduce((sum, doc) => sum + doc.tokenEstimate, 0);
        const totalFiles = this.documents.length;

        let markdown = `---
title: "Session Index - ${sessionId}"
generated: "${now}"
session_id: "${sessionId}"
type: "session_index"
total_files: ${totalFiles}
total_estimated_tokens: ${totalTokens}
context_strategy: "${totalFiles > 5 ? 'index_first' : 'full_content'}"
tags: ["session-index", "context-optimization"]
---

# Session Index: ${sessionId}

## 📊 Session Overview
- **Session ID**: \`${sessionId}\`
- **Total Files**: ${totalFiles}
- **Estimated Tokens**: ${totalTokens.toLocaleString()}
- **Context Strategy**: ${totalFiles > 5 ? '**Index-First** (Large session)' : '**Full Content** (Small session)'}
- **Generated**: ${now}

`;

        // Context strategy recommendation
        if (totalFiles > 5) {
            markdown += `## 🎯 Recommended Context Strategy

**Large Session Detected** - Use intelligent file selection:
1. **Review this index** to understand available files
2. **Select relevant files** based on current task requirements  
3. **Use \`read_file_contents\` tool** to load only 2-3 most relevant files
4. **Benefits**: 90%+ token reduction while maintaining intelligent access

`;
        } else {
            markdown += `## 📖 Small Session Strategy

**Small Session** - All files can be included in context efficiently.
Total estimated tokens (${totalTokens}) are within optimal range.

`;
        }

        // File metadata table
        markdown += this.buildFileMetadataTable();

        // Grouped by type and priority
        markdown += this.buildGroupedSections();

        // Usage instructions
        markdown += this.buildUsageInstructions();

        return markdown;
    }

    buildFileMetadataTable() {
        let table = `## 📋 File Metadata Summary

| Priority | File | Type | Purpose | Tokens |
|----------|------|------|---------|--------|
`;

        this.documents.forEach(doc => {
            const priority = doc.priority || 'Medium';
            const tokens = doc.tokenEstimate.toLocaleString();
            const purpose = (doc.purpose || '').substring(0, 50);
            const purposeDisplay = purpose.length === 50 ? purpose + '...' : purpose;
            
            table += `| ${priority} | \`${doc.path}\` | ${doc.type} | ${purposeDisplay} | ${tokens} |\n`;
        });

        table += '\n';
        return table;
    }

    buildGroupedSections() {
        const groups = this.groupDocumentsByType();
        let sections = `## 📂 Files by Type\n\n`;

        const typeOrder = ['architecture', 'planning', 'code', 'documentation', 'test', 'tracking', 'data', 'log', 'image', 'file'];
        
        for (const type of typeOrder) {
            if (groups[type] && groups[type].length > 0) {
                sections += this.buildTypeSection(type, groups[type]);
            }
        }

        return sections;
    }

    groupDocumentsByType() {
        const groups = {};
        this.documents.forEach(doc => {
            const type = doc.type || 'file';
            if (!groups[type]) groups[type] = [];
            groups[type].push(doc);
        });
        return groups;
    }

    buildTypeSection(type, documents) {
        const emoji = {
            'architecture': '🏗️',
            'planning': '📋',
            'code': '💻',
            'documentation': '📖',
            'test': '🧪',
            'tracking': '📊',
            'troubleshooting': '🔧',
            'data': '📄',
            'config': '⚙️',
            'log': '📝',
            'image': '🖼️',
            'file': '📄'
        }[type] || '📄';

        let section = `### ${emoji} ${type.charAt(0).toUpperCase() + type.slice(1)} Files\n\n`;
        
        documents.forEach(doc => {
            const statusBadge = doc.status !== 'unknown' ? ` (${doc.status})` : '';
            section += `- **\`${doc.path}\`**${statusBadge} - ${doc.purpose}\n`;
            section += `  - *Priority*: ${doc.priority} | *Tokens*: ${doc.tokenEstimate} | *Modified*: ${new Date(doc.modified).toLocaleDateString()}\n`;
        });
        
        return section + '\n';
    }

    buildUsageInstructions() {
        const totalFiles = this.documents.length;
        const sessionId = path.basename(this.sessionPath);

        return `## 🚀 Usage Instructions

### For Intelligent File Selection (Jinja2 Templates)

\`\`\`markdown
{% if provided_filepaths and provided_filepaths|length > 5 %}
## Session Index Available
**Files**: {{ provided_filepaths|length }}
**Strategy**: Use read_file_contents for selective loading

**High Priority Files**:
${this.documents.filter(d => d.priority === 'High').map(d => `- \`${d.path}\``).join('\n')}

{% else %}
## Small Session - Full Content Available
All files included in context.
{% endif %}
\`\`\`

### For Context-Optimized Agents

\`\`\`python
# Example usage in agents
session_files = ${JSON.stringify(this.documents.map(d => ({
    path: d.path,
    type: d.type,
    priority: d.priority,
    tokens: d.tokenEstimate
})), null, 2)}

# Smart selection logic
relevant_files = filter_by_task_relevance(session_files, current_task)
selected_files = select_top_priority(relevant_files, max_files=3)
\`\`\`

### Session Statistics
- **Total Token Budget**: ${this.documents.reduce((sum, doc) => sum + doc.tokenEstimate, 0).toLocaleString()}
- **High Priority Files**: ${this.documents.filter(d => d.priority === 'High').length}
- **Context Strategy**: ${totalFiles > 5 ? 'Index-first recommended' : 'Full content optimal'}
- **Estimated Context Reduction**: ${totalFiles > 5 ? '90%+' : 'N/A (small session)'}

---

*This index was automatically generated by session-index-builder.cjs*  
*Session: \`${sessionId}\` | Generated: ${new Date().toISOString()}*
`;
    }

    writeIndex() {
        const indexContent = this.generateSessionIndex();
        fs.writeFileSync(this.indexFile, indexContent, 'utf8');
        console.log(`✅ Session index generated: ${this.indexFile}`);
        console.log(`📊 Indexed ${this.documents.length} files`);
        console.log(`🎯 Context strategy: ${this.documents.length > 5 ? 'Index-first (large session)' : 'Full content (small session)'}`);
        
        // Output summary for immediate use
        const totalTokens = this.documents.reduce((sum, doc) => sum + doc.tokenEstimate, 0);
        console.log(`💾 Total estimated tokens: ${totalTokens.toLocaleString()}`);
        console.log(`🔍 High priority files: ${this.documents.filter(d => d.priority === 'High').length}`);
    }

    build() {
        console.log(`🔄 Building session index for: ${this.sessionPath}`);
        this.scanSessionDirectory();
        this.writeIndex();
    }
}

// CLI Usage
if (require.main === module) {
    const args = process.argv.slice(2);
    const sessionPath = args[0]; // Optional: specify session path
    
    const builder = new SessionIndexBuilder(sessionPath);
    builder.build();
}

module.exports = SessionIndexBuilder;
