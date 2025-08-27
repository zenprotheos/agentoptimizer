#!/usr/bin/env node

/**
 * Global Indexer for OneShot Documentation
 * Simple, dependency-free hierarchical indexing
 */

const fs = require('fs');
const path = require('path');
const crypto = require('crypto');

class GlobalIndexer {
    constructor(rootPath = '.') {
        this.rootPath = path.resolve(rootPath);
        this.fileHashes = new Map();
        this.cacheFile = path.join(this.rootPath, '.indexer-cache.json');
        this.loadCache();
    }

    loadCache() {
        try {
            if (fs.existsSync(this.cacheFile)) {
                const cache = JSON.parse(fs.readFileSync(this.cacheFile, 'utf8'));
                this.fileHashes = new Map(cache.fileHashes || []);
            }
        } catch (error) {
            this.fileHashes = new Map();
        }
    }

    saveCache() {
        try {
            const cache = {
                fileHashes: Array.from(this.fileHashes.entries()),
                lastUpdated: new Date().toISOString()
            };
            fs.writeFileSync(this.cacheFile, JSON.stringify(cache, null, 2));
        } catch (error) {
            console.warn('Failed to save cache:', error.message);
        }
    }

    calculateFileHash(filePath) {
        try {
            const content = fs.readFileSync(filePath, 'utf8');
            // Hash only front-matter for efficiency
            const frontMatterMatch = content.match(/^---\r?\n([\s\S]*?)\r?\n---/);
            const hashableContent = frontMatterMatch ? frontMatterMatch[1] : path.basename(filePath);
            return crypto.createHash('md5').update(hashableContent).digest('hex');
        } catch {
            return null;
        }
    }

    detectChanges(directory) {
        const changes = {
            added: [],
            modified: [],
            deleted: []
        };

        const currentFiles = this.scanMarkdownFiles(directory);
        const currentFilePaths = new Set(currentFiles.map(f => f.path));
        
        // Check for new and modified files
        for (const file of currentFiles) {
            const currentHash = this.calculateFileHash(file.path);
            const cachedHash = this.fileHashes.get(file.path);
            
            if (!cachedHash) {
                changes.added.push(file.path);
            } else if (currentHash !== cachedHash) {
                changes.modified.push(file.path);
            }
            
            this.fileHashes.set(file.path, currentHash);
        }

        // Check for deleted files
        for (const [cachedPath] of this.fileHashes) {
            if (cachedPath.startsWith(directory) && !currentFilePaths.has(cachedPath)) {
                changes.deleted.push(cachedPath);
                this.fileHashes.delete(cachedPath);
            }
        }

        return changes;
    }

    shouldUpdateIndex(changes) {
        return changes.added.length > 0 || 
               changes.deleted.length > 0 || 
               changes.modified.length > 0;
    }

    scanMarkdownFiles(directory) {
        const files = [];
        
        try {
            const items = fs.readdirSync(directory);
            
            for (const item of items) {
                const fullPath = path.join(directory, item);
                const stat = fs.statSync(fullPath);
                
                if (stat.isDirectory() && !this.shouldSkipDirectory(item)) {
                    files.push(...this.scanMarkdownFiles(fullPath));
                } else if (path.extname(item) === '.md') {
                    const fileInfo = this.extractFileInfo(fullPath);
                    if (fileInfo) {
                        files.push(fileInfo);
                    }
                }
            }
        } catch (error) {
            console.warn(`Error scanning directory ${directory}:`, error.message);
        }
        
        return files;
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

    parseSimpleFrontMatter(content) {
        const frontMatterMatch = content.match(/^---\r?\n([\s\S]*?)\r?\n---/);
        if (!frontMatterMatch) return {};
        
        const result = {};
        const lines = frontMatterMatch[1].split(/\r?\n/);
        
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
            
            result[key] = value;
        }
        
        return result;
    }

    extractFileInfo(filePath) {
        try {
            const content = fs.readFileSync(filePath, 'utf8');
            const frontMatter = this.parseSimpleFrontMatter(content);
            const stats = fs.statSync(filePath);
            const relativePath = path.relative(this.rootPath, filePath);
            
            return {
                path: filePath,
                relativePath: relativePath,
                title: frontMatter.title || this.generateTitleFromPath(relativePath),
                purpose: frontMatter.purpose || 'No description available',
                type: frontMatter.type || 'document',
                status: frontMatter.status || 'Active',
                created: frontMatter.created || stats.birthtime.toISOString(),
                lastUpdated: frontMatter.last_updated || stats.mtime.toISOString(),
                size: stats.size,
                directory: path.dirname(relativePath)
            };
        } catch (error) {
            console.warn(`Error extracting info from ${filePath}:`, error.message);
            return null;
        }
    }

    generateTitleFromPath(relativePath) {
        const fileName = path.basename(relativePath, '.md');
        return fileName
            .replace(/[_-]/g, ' ')
            .replace(/\b\w/g, l => l.toUpperCase());
    }

    generateDirectoryIndex(directory) {
        const files = this.scanMarkdownFiles(directory).filter(f => 
            path.dirname(f.path) === directory
        );
        
        if (files.length === 0) return;

        const relativePath = path.relative(this.rootPath, directory);
        const indexPath = path.join(directory, 'INDEX.md');
        const dirName = path.basename(directory) || 'Root';
        
        let indexContent = this.generateIndexHeader(dirName, relativePath, files.length);
        indexContent += this.generateFileList(files);
        indexContent += this.generateStatistics(files);

        fs.writeFileSync(indexPath, indexContent);
        console.log(`📋 Generated index: ${path.relative(this.rootPath, indexPath)}`);
    }

    generateIndexHeader(dirName, relativePath, fileCount) {
        const now = new Date().toISOString();
        
        return `---
title: "Index - ${dirName}"
type: "index"
purpose: "Auto-generated index for ${dirName} directory with ${fileCount} files"
status: "Active"
generated: "${now}"
auto_generated: true
tags: ["index", "navigation"]
---

# Index: ${dirName}

**Path**: ${relativePath || 'Root'}  
**Files**: ${fileCount}  
**Generated**: ${now}  

---

## 📄 Files

`;
    }

    generateFileList(files) {
        let content = '';
        
        // Sort by type then by title
        files.sort((a, b) => {
            if (a.type !== b.type) {
                return a.type.localeCompare(b.type);
            }
            return a.title.localeCompare(b.title);
        });

        for (const file of files) {
            const fileName = path.basename(file.relativePath);
            const emoji = this.getEmojiForType(file.type);
            
            content += `### ${emoji} [${file.title}](./${fileName})\n`;
            content += `**Type**: ${file.type} | **Status**: ${file.status}\n`;
            content += `**Purpose**: ${file.purpose}\n`;
            content += `**Updated**: ${new Date(file.lastUpdated).toLocaleDateString()}\n\n`;
        }

        return content;
    }

    getEmojiForType(type) {
        const emoji = {
            'architecture': '🏗️',
            'planning': '📋',
            'analysis': '📊',
            'index': '📇',
            'integration_summary': '🔗',
            'audit_plan': '🔍',
            'persona_config': '👤',
            'template': '📄',
            'example': '💡',
            'test': '🧪',
            'tool': '🔧',
            'document': '📖'
        };
        return emoji[type] || '📄';
    }

    generateStatistics(files) {
        const stats = {
            total: files.length,
            byType: {},
            byStatus: {}
        };

        for (const file of files) {
            stats.byType[file.type] = (stats.byType[file.type] || 0) + 1;
            stats.byStatus[file.status] = (stats.byStatus[file.status] || 0) + 1;
        }

        let statsSection = `## 📊 Statistics\n\n`;
        statsSection += `- **Total Files**: ${stats.total}\n`;
        statsSection += `- **By Type**: ${Object.entries(stats.byType)
            .map(([type, count]) => `${type}(${count})`)
            .join(', ')}\n`;
        statsSection += `- **By Status**: ${Object.entries(stats.byStatus)
            .map(([status, count]) => `${status}(${count})`)
            .join(', ')}\n\n`;

        statsSection += `---\n\n*Auto-generated by Global Indexer*\n`;

        return statsSection;
    }

    generateHierarchicalIndexes(directory = this.rootPath) {
        console.log('🔄 Generating hierarchical indexes...');
        
        const changes = this.detectChanges(directory);
        
        if (!this.shouldUpdateIndex(changes)) {
            console.log('✅ No changes detected, indexes are current');
            return { updated: false, reason: 'No changes' };
        }

        console.log(`📊 Changes detected:`, {
            added: changes.added.length,
            modified: changes.modified.length,
            deleted: changes.deleted.length
        });

        const indexedDirectories = this.generateIndexesRecursive(directory);
        this.saveCache();
        
        return {
            updated: true,
            changes,
            indexedDirectories
        };
    }

    generateIndexesRecursive(directory) {
        const indexedDirs = [];
        
        try {
            const items = fs.readdirSync(directory);
            const hasMarkdownFiles = items.some(item => path.extname(item) === '.md');

            // Generate index for current directory if it has markdown files
            if (hasMarkdownFiles) {
                this.generateDirectoryIndex(directory);
                indexedDirs.push(directory);
            }

            // Recursively process subdirectories
            for (const item of items) {
                const fullPath = path.join(directory, item);
                const stat = fs.statSync(fullPath);
                
                if (stat.isDirectory() && !this.shouldSkipDirectory(item)) {
                    const subIndexes = this.generateIndexesRecursive(fullPath);
                    indexedDirs.push(...subIndexes);
                }
            }
        } catch (error) {
            console.warn(`Error processing directory ${directory}:`, error.message);
        }

        return indexedDirs;
    }
}

// CLI Usage
if (require.main === module) {
    const args = process.argv.slice(2);
    const command = args[0] || 'generate';
    const targetPath = args[1] || '.';
    
    const indexer = new GlobalIndexer(targetPath);
    
    switch (command) {
        case 'generate':
            console.log('🚀 Starting hierarchical indexing...');
            const result = indexer.generateHierarchicalIndexes();
            
            if (result.updated) {
                console.log(`\n✅ Generated indexes for ${result.indexedDirectories.length} directories`);
            } else {
                console.log(`\n✅ ${result.reason}`);
            }
            break;
            
        case 'check':
            const changes = indexer.detectChanges(targetPath);
            console.log('📊 Change Detection Results:');
            console.log(`- Added: ${changes.added.length}`);
            console.log(`- Modified: ${changes.modified.length}`);
            console.log(`- Deleted: ${changes.deleted.length}`);
            break;
            
        default:
            console.log(`
Global Indexer for OneShot

Usage:
  node global_indexer.cjs generate [directory]
  node global_indexer.cjs check [directory]

Features:
  - Hierarchical indexing
  - Change detection
  - Auto-generated navigation
            `);
    }
}

module.exports = GlobalIndexer;
