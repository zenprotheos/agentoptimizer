#!/usr/bin/env node

/**
 * Intelligent Front-Matter Validator (VoiceScribeAI)
 */

const fs = require('fs');
const path = require('path');

class IntelligentFrontMatterValidator {
    constructor(options = {}) {
        this.baseDir = 'docs';
        this.errors = [];
        this.warnings = [];
        this.validFiles = [];
        this.duplicateFiles = [];
        this.placeholderFiles = [];
        this.useAI = options.useAI || false;

        this.requiredFields = ['title', 'summary', 'type', 'module'];
        this.validTypes = ['doc', 'working', 'troubleshooting', 'spec', 'test', 'rule', 'implementation', 'index', 'redirect', 'archive', 'completion'];
        // Accept modules used across the docs, including task-specific areas
        this.validModules = ['global', 'ui-ux', 'planning', 'implementation', 'docs'];
    }

    scanDirectory(dirPath) {
        const items = fs.readdirSync(dirPath);
        for (const item of items) {
            const fullPath = path.join(dirPath, item);
            const stat = fs.statSync(fullPath);
            if (stat.isDirectory()) {
                if (!item.startsWith('.') && item !== 'node_modules' && item !== 'ARCHIVED') {
                    this.scanDirectory(fullPath);
                }
            } else if (stat.isFile() && path.extname(item) === '.md') {
                this.analyzeMarkdownFile(fullPath);
            }
        }
    }

    analyzeMarkdownFile(filePath) {
        try {
            const content = fs.readFileSync(filePath, 'utf8');
            const relativePath = path.relative(this.baseDir, filePath).replace(/\\/g, '/');
            const frontMatterBlocks = this.detectFrontMatterBlocks(content);
            if (frontMatterBlocks.length === 0) {
                this.errors.push({ file: relativePath, type: 'missing_frontmatter', message: 'No front-matter found' });
                return;
            }
            if (frontMatterBlocks.length > 1) {
                this.duplicateFiles.push({ file: relativePath, blocks: frontMatterBlocks, content });
                this.warnings.push({ file: relativePath, type: 'duplicate_frontmatter', message: `Found ${frontMatterBlocks.length} front-matter blocks - duplicates detected` });
                return;
            }
            const frontMatter = this.parseFrontMatter(frontMatterBlocks[0].content);
            this.validateFrontMatter(relativePath, frontMatter);
            this.validFiles.push(relativePath);
        } catch (error) {
            this.errors.push({ file: path.relative(this.baseDir, filePath).replace(/\\/g, '/'), type: 'file_error', message: `Error reading file: ${error.message}` });
        }
    }

    detectFrontMatterBlocks(content) {
        const blocks = [];
        let currentPos = 0;
        while (currentPos < content.length) {
            const startMatch = content.indexOf('---', currentPos);
            if (startMatch === -1) break;
            if (startMatch > 0 && content[startMatch - 1] !== '\n' && startMatch !== 0) { currentPos = startMatch + 3; continue; }
            const endMatch = content.indexOf('\n---', startMatch + 3);
            if (endMatch === -1) break;
            const frontMatterContent = content.substring(startMatch + 3, endMatch).trim();
            if (this.looksLikeFrontMatter(frontMatterContent)) {
                blocks.push({ start: startMatch, end: endMatch + 4, content: frontMatterContent });
            }
            currentPos = endMatch + 4;
        }
        return blocks;
    }

    looksLikeFrontMatter(content) {
        const hasTitle = /^title:/m.test(content);
        const hasOtherFields = /^(summary|type|module|tags):/m.test(content);
        return hasTitle && hasOtherFields;
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

    validateFrontMatter(filePath, frontMatter) {
        for (const field of this.requiredFields) {
            if (!frontMatter[field] || frontMatter[field] === '') {
                this.errors.push({ file: filePath, type: 'missing_field', message: `Missing required field: ${field}` });
            }
        }
        if (frontMatter.type && !this.validTypes.includes(frontMatter.type)) {
            this.warnings.push({ file: filePath, type: 'invalid_type', message: `Invalid type '${frontMatter.type}'.` });
        }
        if (frontMatter.module && !this.validModules.includes(frontMatter.module)) {
            this.warnings.push({ file: filePath, type: 'invalid_module', message: `Invalid module '${frontMatter.module}'.` });
        }
    }

    printResults() {
        console.log('\n📋 Intelligent Front-Matter Analysis Results');
        console.log('=============================================');
        console.log(`\n✅ Valid files: ${this.validFiles.length}`);
        if (this.errors.length > 0) {
            console.log(`\n❌ Errors found: ${this.errors.length} files`);
            this.errors.forEach(error => { console.log(`   📄 ${error.file}: ${error.message}`); });
        }
        if (this.warnings.length > 0) {
            console.log(`\n⚠️  Warnings: ${this.warnings.length} files`);
            this.warnings.forEach(warning => { console.log(`   📄 ${warning.file}: ${warning.message}`); });
        }
        const totalFiles = this.validFiles.length + this.errors.length;
        const successRate = totalFiles > 0 ? ((this.validFiles.length / totalFiles) * 100).toFixed(1) : '0.0';
        console.log(`\n📊 Summary:`);
        console.log(`   📄 Total files analyzed: ${totalFiles}`);
        console.log(`   ✅ Valid files: ${this.validFiles.length} (${successRate}%)`);
    }

    async validate() {
        console.log('🔄 Running intelligent front-matter analysis...');
        this.scanDirectory(this.baseDir);
        this.printResults();
        return {
            valid: this.validFiles.length,
            errors: this.errors.length,
            warnings: this.warnings.length,
            successRate: this.errors.length === 0
        };
    }
}

if (require.main === module) {
    const validator = new IntelligentFrontMatterValidator();
    validator.validate().then(results => {
        process.exit(results.errors > 0 ? 1 : 0);
    }).catch(error => {
        console.error('Fatal error:', error);
        process.exit(1);
    });
}

module.exports = IntelligentFrontMatterValidator;


