const http = require('node:http');
const fs = require('node:fs');
const path = require('node:path');
const root = path.resolve(__dirname, '..');
const mime = { '.html': 'text/html; charset=utf-8', '.js': 'text/javascript; charset=utf-8', '.css': 'text/css; charset=utf-8', '.json': 'application/json; charset=utf-8', '.png': 'image/png' };
const server = http.createServer((req, res) => {
  try {
    const name = decodeURIComponent(new URL(req.url, 'http://localhost').pathname);
    const target = path.resolve(root, '.' + (name === '/' ? '/index.html' : name));
    const relative = path.relative(root, target).replaceAll('\\', '/');
    if (relative.startsWith('..') || !/^(index\.html|cat_sectional_practice\.html|app\/[^/]+\.(js|css)|samples\/[^/]+\.json)$/.test(relative)) { res.writeHead(404); res.end('Not found'); return; }
    const body = fs.readFileSync(target);
    res.writeHead(200, { 'Content-Type': mime[path.extname(target)] || 'application/octet-stream', 'Cache-Control': 'no-store', 'X-Content-Type-Options': 'nosniff' }); res.end(body);
  } catch { res.writeHead(404); res.end('Not found'); }
});
function openBrowser() {
  if (process.argv.includes('--open') && process.platform === 'win32') {
    require('node:child_process').execFile('cmd.exe', ['/c', 'start', '', 'http://localhost:4173'], { windowsHide: true }, error => {
      if (error) console.log('Open http://localhost:4173 in your browser.');
    });
  }
}
server.on('error', error => {
  if (error.code === 'EADDRINUSE') {
    console.log('Port 4173 is already in use. If CAT Studio is running, open http://localhost:4173.');
    openBrowser();
  } else { console.error(error.message); process.exitCode = 1; }
});
server.listen(4173, '127.0.0.1', () => { console.log('CAT Studio: http://localhost:4173'); openBrowser(); });
