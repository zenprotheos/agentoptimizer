#!/usr/bin/env node
/**
 * Start a LocalTunnel for the Flask dev server and persist the public URL
 * to storage/LOCAL_TUNNEL_URL.txt
 */
const fs = require('fs');
const path = require('path');
const localtunnel = require('localtunnel');

(async () => {
  const port = parseInt(process.env.PORT || '5000', 10);
  const subdomain = process.env.LT_SUBDOMAIN || undefined; // optional
  const outfile = path.join(process.cwd(), 'storage', 'LOCAL_TUNNEL_URL.txt');

  // Ensure storage directory exists
  try {
    fs.mkdirSync(path.dirname(outfile), { recursive: true });
  } catch (_) {}

  const tunnel = await localtunnel({ port, subdomain });
  const url = tunnel.url;
  console.log(`[localtunnel] Public URL: ${url}`);
  fs.writeFileSync(outfile, url, 'utf8');

  tunnel.on('close', () => {
    try { fs.unlinkSync(outfile); } catch (_) {}
    process.exit(0);
  });
})();


