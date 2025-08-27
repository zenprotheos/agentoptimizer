#!/usr/bin/env node

/**
 * Front-Matter Validator for OneShot Documentation
 * Simple, dependency-free validation and fixing of front-matter
 */

const fs = require('fs');
const path = require('path');

class FrontMatterValidator {
    constructor() {
        this.requiredFields = [
            'title',
            'created', 
            'type',
            'purpose',
            'status',
            'tags'
        ];
        
        this.validTypes = [
            'architecture',
            'planning', 
            'analysis',
            'example',
            'test',
            'index',
            'audit_plan',
            'integration_summary',
            'persona_config',
            'template',
            'tool',
            'document'
        ];
        
        this.validStatuses = [
            'Active',
            'Complete', 
            'Legacy',
            'Deprecated',
            'In-Progress',
            'Pending'
        ];
    }

    parseSimpleYAML(yamlContent) {
        const result = {};
        const lines = yamlContent.split(/\r?\n/);
        
        for (const line of lines) {
            const trimmed = line.trim();
            if (!trimmed || trimmed.startsWith('#')) continue;
            
            const colonIndex = trimmed.indexOf(':');
            if (colonIndex === -1) continue;
            
            const key = trimmed.substring(0, colonIndex).trim();
            let value = trimmed.substring(colonIndex + 1).trim();
            
            // Remove quotes
            if ((value.startsWith('"') && value.endsWith('"')) || 
                (value.startsWith("'") && value.endsWith("'"))) {
                value = value.slice(1, -1);
            }
            
            // Handle arrays (simple format)
            if (value.startsWith('[') && value.endsWith(']')) {
                const arrayContent = value.slice(1, -1);
                result[key] = arrayContent.split(',').map(item => 
                    item.trim().replace(/["']/g, '')
                ).filter(item => item);
            } else {
                result[key] = value;
            }
        }
        
        return result;
    }

    validateFile(filePath) {
        try {
            const content = fs.readFileSync(filePath, 'utf8');
            const frontMatterMatch = content.match(/^---\r?\n([\s\S]*?)\r?\n---/);
            
            if (!frontMatterMatch) {
                return {
                    valid: false,
                    errors: ['No front-matter found'],
                    filePath
                };
            }

            const frontMatter = this.parseSimpleYAML(frontMatterMatch[1]);
            return this.validateFrontMatter(frontMatter, filePath);
            
        } catch (error) {
            return {
                valid: false,
                errors: [`Error reading file: ${error.message}`],
                filePath
            };
        }
    }

    validateFrontMatter(frontMatter, filePath) {
        const errors = [];
        const warnings = [];

        // Check required fields
        for (const field of this.requiredFields) {
            if (!frontMatter[field]) {
                errors.push(`Missing required field: ${field}`);
            }
        }

        // Validate field values
        if (frontMatter.type && !this.validTypes.includes(frontMatter.type)) {
            errors.push(`Invalid type: ${frontMatter.type}. Must be one of: ${this.validTypes.join(', ')}`);
        }

        if (frontMatter.status && !this.validStatuses.includes(frontMatter.status)) {
            errors.push(`Invalid status: ${frontMatter.status}. Must be one of: ${this.validStatuses.join(', ')}`);
        }

        // Check purpose description quality
        if (frontMatter.purpose) {
            if (frontMatter.purpose.length < 20) {
                warnings.push('Purpose description is too short (minimum 20 characters for good indexing)');
            }
            if (frontMatter.purpose.length > 200) {
                warnings.push('Purpose description is too long (maximum 200 characters recommended)');
            }
        }

        return {
            valid: errors.length === 0,
            errors,
            warnings,
            filePath,
            frontMatter
        };
    }

    scanDirectory(dirPath) {
        const results = {
            totalFiles: 0,
            validFiles: 0,
            invalidFiles: [],
            warnings: []
        };

        this.scanDirectoryRecursive(dirPath, results);
        return results;
    }

    scanDirectoryRecursive(dirPath, results) {
        try {
            const items = fs.readdirSync(dirPath);
            
            for (const item of items) {
                const fullPath = path.join(dirPath, item);
                const stat = fs.statSync(fullPath);
                
                if (stat.isDirectory()) {
                    if (!this.shouldSkipDirectory(item)) {
                        this.scanDirectoryRecursive(fullPath, results);
                    }
                } else if (path.extname(item) === '.md') {
                    results.totalFiles++;
                    const validation = this.validateFile(fullPath);
                    
                    if (validation.valid) {
                        results.validFiles++;
                    } else {
                        results.invalidFiles.push(validation);
                    }
                    
                    if (validation.warnings) {
                        results.warnings.push(...validation.warnings.map(w => ({
                            file: fullPath,
                            warning: w
                        })));
                    }
                }
            }
        } catch (error) {
            console.error(`Error scanning directory ${dirPath}:`, error.message);
        }
    }

    shouldSkipDirectory(dirName) {
        const skipDirs = [
            'node_modules',
            '.git',
            '__pycache__',
            '.obsidian',
            '.vscode',
            '.cursor'
        ];
        return skipDirs.includes(dirName) || dirName.startsWith('.');
    }

    generateReport(results) {
        const total = results.totalFiles;
        const valid = results.validFiles;
        const invalid = results.invalidFiles.length;
        const percentage = Math.round((valid / total) * 100);

        let report = `# Front-Matter Validation Report\n\n`;
        report += `## Summary\n`;
        report += `- **Total Files**: ${total}\n`;
        report += `- **Valid**: ${valid} (${percentage}%)\n`;
        report += `- **Invalid**: ${invalid}\n`;
        report += `- **Warnings**: ${results.warnings.length}\n\n`;

        if (invalid > 0) {
            report += `## Invalid Files\n\n`;
            for (const file of results.invalidFiles) {
                report += `### ${path.relative('.', file.filePath)}\n`;
                for (const error of file.errors) {
                    report += `- ❌ ${error}\n`;
                }
                report += '\n';
            }
        }

        if (results.warnings.length > 0) {
            report += `## Warnings\n\n`;
            for (const warning of results.warnings) {
                report += `- ⚠️ **${path.relative('.', warning.file)}**: ${warning.warning}\n`;
            }
            report += '\n';
        }

        return report;
    }

    generateTemplate(fileName, type = 'document') {
        const now = new Date().toISOString();
        const title = fileName
            .replace(/\.md$/, '')
            .replace(/[_-]/g, ' ')
            .replace(/\b\w/g, l => l.toUpperCase());

        return `---
title: "${title}"
created: "${now}"
type: "${type}"
purpose: "Detailed description of this document's purpose and scope"
status: "Active"
tags: ["documentation"]
---

# ${title}

## Purpose

[Describe the purpose and scope of this document]

## Content

[Document content goes here]
`;
    }
}

// CLI Usage
if (require.main === module) {
    const args = process.argv.slice(2);
    const command = args[0];
    const targetPath = args[1] || '.';
    
    const validator = new FrontMatterValidator();
    
    switch (command) {
        case 'validate':
            console.log('🔍 Validating front-matter...');
            const results = validator.scanDirectory(targetPath);
            console.log(validator.generateReport(results));
            process.exit(results.invalidFiles.length > 0 ? 1 : 0);
            break;
            
        case 'template':
            const fileName = args[2] || 'new-document.md';
            const type = args[3] || 'document';
            console.log(validator.generateTemplate(fileName, type));
            break;
            
        default:
            console.log(`
Front-Matter Validator for OneShot

Usage:
  node frontmatter_validator.cjs validate [directory]
  node frontmatter_validator.cjs template [filename] [type]

Commands:
  validate  - Check all .md files for front-matter compliance
  template  - Generate front-matter template for new files
            `);
    }
}

module.exports = FrontMatterValidator;
