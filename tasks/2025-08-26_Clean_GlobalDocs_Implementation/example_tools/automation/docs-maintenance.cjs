#!/usr/bin/env node

/**
 * Docs Maintenance Wrapper
 * Rebuilds index, refreshes TOCs, and validates front-matter.
 */

const { execSync } = require('child_process');

function run(cmd) {
  console.log(`\n$ ${cmd}`);
  execSync(cmd, { stdio: 'inherit' });
}

try {
  run('node tools/indexing/build-index.cjs');
  run('node tools/automation/enhanced-toc-updater.cjs --all --verbose');
  run('node tools/automation/intelligent-front-matter-validator.cjs --fix');
  console.log('\n✅ Docs maintenance completed');
} catch (e) {
  console.error('\n❌ Docs maintenance failed:', e.message);
  process.exit(1);
}


