#!/usr/bin/env node

const http = require('http');
const { spawn } = require('child_process');

const HOST = process.env.HOST || '127.0.0.1';
const PORT = process.env.PORT || 3000;
const HEALTH_PATH = '/api/extract/health';

function checkHealth() {
  return new Promise(resolve => {
    const req = http.request(
      {
        host: HOST,
        port: PORT,
        path: HEALTH_PATH,
        method: 'GET',
        timeout: 2000,
      },
      res => {
        resolve({ status: res.statusCode });
      }
    );
    req.on('error', () => resolve({ status: 0 }));
    req.on('timeout', () => {
      req.destroy();
      resolve({ status: 0 });
    });
    req.end();
  });
}

(async () => {
  const health = await checkHealth();
  if (health.status === 200) {
    console.log('Server already running and healthy.');
    process.exit(0);
  }

  console.log('Server not healthy; starting server...');
  const child = spawn('npm', ['run', 'dev:server'], {
    stdio: 'inherit',
    shell: true,
  });

  // Wait for up to 30s for health to succeed
  const start = Date.now();
  const timeout = 30000;
  const poll = async () => {
    while (Date.now() - start < timeout) {
      const h = await checkHealth();
      if (h.status === 200) {
        console.log('Server started and healthy.');
        process.exit(0);
      }
      await new Promise(r => setTimeout(r, 500));
    }
    console.error('Server failed to become healthy in time');
    child.kill();
    process.exit(1);
  };

  poll();
})();
