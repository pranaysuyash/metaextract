/**
 * Metadata Routes Module
 *
 * Handles metadata-related endpoints:
 * - Search and storage
 * - History
 * - Favorites
 * - Similar file finding
 */

import type { Express, Response } from 'express';
import path from 'path';
import { spawn } from 'child_process';

// ============================================================================
// Helper Functions
// ============================================================================

async function runMetadataDbCli(args: string[]): Promise<any> {
  return new Promise((resolve, reject) => {
    const pythonScript = path.join(
      __dirname,
      '..',
      'extractor',
      'metadata_db_cli.py'
    );

    // Prefer a configured Python executable (e.g., project's venv) when available
    const configuredPython = process.env.PYTHON_EXECUTABLE;
    const venvPython = path.join(__dirname, '..', '.venv', 'bin', 'python');
    const pythonExec =
      configuredPython ||
      (require('fs').existsSync(venvPython) ? venvPython : 'python3');

    const python = spawn(pythonExec, [pythonScript, ...args]);

    let stdout = '';
    let stderr = '';

    python.stdout.on('data', (data) => {
      stdout += data.toString();
    });

    python.stderr.on('data', (data) => {
      stderr += data.toString();
    });

    python.on('close', (code) => {
      if (code !== 0) {
        console.error('metadata_db_cli stderr:', stderr);
        reject(new Error(stderr || 'metadata db cli failed'));
        return;
      }
      try {
        resolve(JSON.parse(stdout));
      } catch (error) {
        console.error('metadata_db_cli stdout (raw):', stdout);
        reject(new Error('failed to parse metadata db cli output'));
      }
    });

    python.on('error', (err) => {
      reject(new Error(`failed to start metadata db cli: ${err.message}`));
    });

    setTimeout(() => {
      python.kill();
      reject(new Error('metadata db cli timed out'));
    }, 15000);
  });
}

// ============================================================================
// Route Registration
// ============================================================================

export function registerMetadataRoutes(app: Express): void {
  // Metadata search endpoint
  app.get('/api/metadata/search', async (req, res) => {
    try {
      const query = (req.query.q || req.query.query) as string | undefined;
      if (!query) {
        return res.status(400).json({ error: 'query required' });
      }
      const limit = req.query.limit ? Number(req.query.limit) : 100;
      const offset = req.query.offset ? Number(req.query.offset) : 0;
      const results = await runMetadataDbCli([
        'search',
        '--query',
        query,
        '--limit',
        String(limit),
        '--offset',
        String(offset),
      ]);
      res.json(results);
    } catch (error) {
      res.status(500).json({ error: 'metadata search failed' });
    }
  });

  // History endpoint
  app.get('/api/metadata/history', async (req, res) => {
    try {
      const fileId = req.query.file_id as string | undefined;
      const filePath = req.query.file_path as string | undefined;
      if (!fileId && !filePath) {
        return res.status(400).json({ error: 'file_id or file_path required' });
      }
      const args = ['history'];
      if (fileId) {
        args.push('--file-id', fileId);
      } else if (filePath) {
        args.push('--file-path', filePath);
      }
      const history = await runMetadataDbCli(args);
      res.json(history);
    } catch (error) {
      res.status(500).json({ error: 'history lookup failed' });
    }
  });

  // Stats endpoint
  app.get('/api/metadata/stats', async (req, res) => {
    try {
      const stats = await runMetadataDbCli(['stats']);
      res.json(stats);
    } catch (error) {
      res.status(500).json({ error: 'metadata stats failed' });
    }
  });

  // Favorites list endpoint
  app.get('/api/metadata/favorites', async (req, res) => {
    try {
      const favorites = await runMetadataDbCli(['favorites', '--list']);
      res.json(favorites);
    } catch (error) {
      res.status(500).json({ error: 'favorites lookup failed' });
    }
  });

  // Favorites toggle endpoint
  app.post('/api/metadata/favorites', async (req, res) => {
    try {
      const { file_id, notes, tags } = req.body || {};
      if (!file_id) {
        return res.status(400).json({ error: 'file_id required' });
      }
      const args = ['favorites', '--toggle', '--file-id', String(file_id)];
      if (notes) {
        args.push('--notes', String(notes));
      }
      if (tags && Array.isArray(tags)) {
        args.push('--tags', tags.join(','));
      } else if (typeof tags === 'string') {
        args.push('--tags', tags);
      }
      const result = await runMetadataDbCli(args);
      res.json(result);
    } catch (error) {
      res.status(500).json({ error: 'favorites toggle failed' });
    }
  });

  // Similar files endpoint
  app.get('/api/metadata/similar', async (req, res) => {
    try {
      const phash = req.query.phash as string | undefined;
      if (!phash) {
        return res.status(400).json({ error: 'phash required' });
      }
      const threshold = req.query.threshold ? Number(req.query.threshold) : 5;
      const limit = req.query.limit ? Number(req.query.limit) : 20;
      const result = await runMetadataDbCli([
        'similar',
        '--phash',
        phash,
        '--threshold',
        String(threshold),
        '--limit',
        String(limit),
      ]);
      res.json(result);
    } catch (error) {
      res.status(500).json({ error: 'similarity search failed' });
    }
  });
}
