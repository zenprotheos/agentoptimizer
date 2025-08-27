#!/usr/bin/env node

/**
 * Drift Check
 * - Flags duplicate filenames across docs
 * - Runs docs maintenance pipeline
 */

const fs = require('fs');
const path = require('path');
const { execSync } = require('child_process');

function listMarkdownFiles(baseDir) {
  const results = [];
  const walk = (dirPath) => {
    const entries = fs.readdirSync(dirPath, { withFileTypes: true });
    for (const entry of entries) {
      if (entry.name.startsWith('.') || entry.name === 'node_modules') continue;
      const full = path.join(dirPath, entry.name);
      if (entry.isDirectory()) {
        if (entry.name !== 'tasks') walk(full);
      } else if (entry.isFile() && entry.name.toLowerCase().endsWith('.md')) {
        results.push(full.replace(/\\/g, '/'));
      }
    }
  };
  walk(baseDir);
  return results;
}

function findDuplicateFilenames(files) {
  const nameMap = new Map();
  for (const file of files) {
    const name = path.basename(file).toLowerCase();
    const arr = nameMap.get(name) || [];
    arr.push(file);
    nameMap.set(name, arr);
  }
  const dups = [];
  for (const [name, arr] of nameMap.entries()) {
    if (arr.length > 1) dups.push({ name, files: arr });
  }
  return dups;
}

function runMaintenance() {
  execSync('node tools/automation/docs-maintenance.cjs', { stdio: 'inherit' });
}

function main() {
  console.log('🔎 Running drift check...');
  const files = listMarkdownFiles('docs');
  const dups = findDuplicateFilenames(files);
  if (dups.length > 0) {
    console.log(`\n⚠️  Duplicate filenames detected (${dups.length}):`);
    for (const dup of dups) {
      console.log(`- ${dup.name}`);
      dup.files.forEach(f => console.log(`   • ${f}`));
    }
    console.log('\n💡 Consider consolidating duplicates to a single canonical file.');
  } else {
    console.log('\n✅ No duplicate filenames detected.');
  }

  console.log('\n🔧 Running docs maintenance...');
  runMaintenance();
}

try {
  main();
} catch (e) {
  console.error('❌ Drift check failed:', e.message);
  process.exit(1);
}


