#!/usr/bin/env node

/**
 * Documentation Index Builder (VoiceScribeAI)
 * Generates docs/doc_index.md from front-matter in all .md files
 */

const fs = require('fs');
const path = require('path');

class DocumentationIndexBuilder {
    constructor() {
        this.documents = [];
        this.baseDir = 'docs';
        this.indexFile = path.join(this.baseDir, 'doc_index.md');
    }

    buildDirectoryTreeMarkdown() {
        const buildTree = (dir, depth = 0) => {
            const entries = fs.readdirSync(dir, { withFileTypes: true })
                .filter(d => !d.name.startsWith('.') && d.name !== 'node_modules')
                .sort((a, b) => a.name.localeCompare(b.name));
            let md = '';
            for (const entry of entries) {
                const fullPath = path.join(dir, entry.name);
                const rel = path.relative(this.baseDir, fullPath).replace(/\\/g, '/');
                const indent = '  '.repeat(depth);
                if (entry.isDirectory()) {
                    md += `${indent}- ${entry.name}/\n`;
                    md += buildTree(fullPath, depth + 1);
                } else if (entry.isFile() && path.extname(entry.name) === '.md') {
                    md += `${indent}- [${entry.name}](${rel})\n`;
                }
            }
            return md;
        };
        return `## 📁 Directory of docs/\n\n${buildTree(this.baseDir)}\n`;
    }

    scanDirectory(dirPath) {
        const items = fs.readdirSync(dirPath);
        for (const item of items) {
            const fullPath = path.join(dirPath, item);
            const stat = fs.statSync(fullPath);
            if (stat.isDirectory()) {
                if (!item.startsWith('.') && item !== 'node_modules' && item !== 'tasks') {
                    this.scanDirectory(fullPath);
                }
            } else if (stat.isFile() && path.extname(item) === '.md') {
                this.processMarkdownFile(fullPath);
            }
        }
    }

    processMarkdownFile(filePath) {
        try {
            const content = fs.readFileSync(filePath, 'utf8');
            const frontMatterMatch = content.match(/^---\n([\s\S]*?)\n---/);
            if (!frontMatterMatch) return;
            const frontMatter = this.parseFrontMatter(frontMatterMatch[1]);
            const stats = fs.statSync(filePath);
            const relativePath = path.relative(this.baseDir, filePath).replace(/\\/g, '/');
            const document = {
                path: relativePath,
                title: frontMatter.title || path.basename(filePath, '.md'),
                summary: frontMatter.summary || 'No description available',
                type: frontMatter.type || 'doc',
                module: frontMatter.module || 'global',
                tags: frontMatter.tags || [],
                created: stats.birthtime,
                modified: stats.mtime,
                size: stats.size
            };
            this.documents.push(document);
        } catch (error) {
            console.error(`❌ Error processing ${filePath}:`, error.message);
        }
    }

    parseFrontMatter(yamlContent) {
        const frontMatter = {};
        yamlContent.split('\n').forEach(line => {
            const match = line.match(/^(\w+):\s*(.*)$/);
            if (match) {
                const key = match[1];
                let value = match[2].trim();
                if ((value.startsWith('"') && value.endsWith('"')) || (value.startsWith('\'') && value.endsWith('\''))) {
                    value = value.slice(1, -1);
                }
                if (value.startsWith('[') && value.endsWith(']')) {
                    value = value.slice(1, -1).split(',').map(item => item.trim().replace(/["']/g, '')).filter(item => item.length > 0);
                }
                frontMatter[key] = value;
            }
        });
        return frontMatter;
    }

    generateMarkdownIndex() {
        this.documents.sort((a, b) => {
            if (a.type !== b.type) return a.type.localeCompare(b.type);
            if (a.module !== b.module) return a.module.localeCompare(b.module);
            return a.title.localeCompare(b.title);
        });
        return this.buildIndexMarkdown();
    }

    buildIndexMarkdown() {
        const now = new Date().toISOString().split('T')[0];
        let markdown = `---
title: "VoiceScribeAI Documentation Index"
summary: "Index of documentation with quick navigation and references"
type: "index"
module: "global"
tags: ["index", "navigation", "documentation"]
last_updated: "${now}"
---

# VoiceScribeAI Documentation Index

---
`;

        // Directory listing first
        markdown += this.buildDirectoryTreeMarkdown();

        const docsByType = this.groupDocumentsByType();
        const typeOrder = ['index', 'rule', 'doc', 'implementation', 'working', 'troubleshooting', 'test', 'spec', 'archive'];
        for (const type of typeOrder) {
            if (docsByType[type] && docsByType[type].length > 0) {
                markdown += this.buildTypeSection(type, docsByType[type]);
            }
        }

        markdown += this.buildQuickReference();
        return markdown;
    }

    groupDocumentsByType() {
        const groups = {};
        this.documents.forEach(doc => {
            const type = doc.type || 'doc';
            if (!groups[type]) groups[type] = [];
            groups[type].push(doc);
        });
        return groups;
    }

    buildTypeSection(type, documents) {
        const emoji = {
            'index': '📋',
            'rule': '📜',
            'doc': '📖',
            'implementation': '🚀',
            'working': '🔄',
            'troubleshooting': '🔧',
            'test': '🧪',
            'spec': '⚙️',
            'archive': '📁'
        }[type] || '📄';

        let section = `\n## ${emoji} ${type.charAt(0).toUpperCase() + type.slice(1)}\n\n`;
        documents.forEach(doc => {
            section += `- [\`${doc.path}\`](${doc.path}) - ${doc.summary}\n`;
        });
        return section + '\n';
    }

    buildQuickReference() {
        return `## ⚡ Quick Reference

### Common Commands
\`\`\`bash
# Get current date for task naming
node tools/automation/date-current.cjs

# Build documentation index
node tools/indexing/build-index.cjs

# Validate front-matter (safe to run anytime)
node tools/automation/intelligent-front-matter-validator.cjs --fix
 
# Auto-regenerate docs index (watch)
npm run docs:watch
\`\`\`

### Local App
- Run: \`python main.py\`
- URL: \`http://localhost:5000\`

`;
    }

    writeIndex() {
        const indexContent = this.generateMarkdownIndex();
        fs.writeFileSync(this.indexFile, indexContent, 'utf8');
        console.log(`✅ Documentation index generated: ${this.indexFile}`);
        console.log(`📊 Indexed ${this.documents.length} documents`);
    }

    build() {
        console.log('🔄 Building documentation index...');
        this.scanDirectory(this.baseDir);
        this.writeIndex();
    }
}

if (require.main === module) {
    const builder = new DocumentationIndexBuilder();
    builder.build();
}

module.exports = DocumentationIndexBuilder;


