#!/usr/bin/env node

/**
 * Date Current Generator
 * Provides current date in formats useful for task workspace creation
 * Compatible with VoiceScribeAI documentation standards
 */

function getCurrentDate() {
    const now = new Date();
    
    const formats = {
        // Primary format for task folder naming: YYYY-MM-DD
        taskFolder: now.toISOString().split('T')[0],
        
        // ISO format for front-matter timestamps
        iso: now.toISOString(),
        
        // Human readable format
        readable: now.toLocaleDateString('en-US', {
            year: 'numeric',
            month: 'long', 
            day: 'numeric'
        }),
        
        // Short format for quick reference
        short: now.toLocaleDateString('en-US', {
            year: 'numeric',
            month: 'short',
            day: 'numeric'
        })
    };
    
    return formats;
}

// Command line usage
if (require.main === module) {
    const dates = getCurrentDate();
    
    const args = process.argv.slice(2);
    const format = args[0] || 'taskFolder';
    
    if (dates[format]) {
        console.log(dates[format]);
    } else {
        console.error(`Unknown format: ${format}`);
        console.error('Available formats:', Object.keys(dates).join(', '));
        process.exit(1);
    }
}

module.exports = { getCurrentDate };


