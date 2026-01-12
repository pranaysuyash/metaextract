/**
 * Metadata Routes Module
 *
 * Handles metadata-related endpoints:
 * - Search and storage
 * - History
 * - Favorites
 * - Similar file finding
 */

import { spawn } from 'child_process';

import type { Express } from 'express';
import type { AuthRequest } from '../auth';
import { requireAuth } from '../auth';
import path from 'path';

// Get the routes directory - compatible with both ESM and CommonJS
const projectRoot = process.cwd();
const currentDirPath = path.join(projectRoot, 'server', 'routes');

// ============================================================================
// Helper Functions
// ============================================================================

async function runMetadataDbCli(args: string[]): Promise<any> {
  return new Promise((resolve, reject) => {
    const pythonScript = path.join(
      currentDirPath,
      '..',
      'extractor',
      'metadata_db_cli.py'
    );

    // Prefer a configured Python executable (e.g., project's venv) when available
    const configuredPython = process.env.PYTHON_EXECUTABLE;
    const venvPython = path.join(
      currentDirPath,
      '..',
      '.venv',
      'bin',
      'python'
    );
    const pythonExec =
      configuredPython ||
      (require('fs').existsSync(venvPython) ? venvPython : 'python3');

    const python = spawn(pythonExec, [pythonScript, ...args]);

    let stdout = '';
    let stderr = '';

    python.stdout.on('data', data => {
      stdout += data.toString();
    });

    python.stderr.on('data', data => {
      stderr += data.toString();
    });

    python.on('close', code => {
      if (code !== 0) {
        console.error('metadata_db_cli stderr:', stderr);
        reject(new Error(stderr || 'metadata db cli failed'));
        return;
      }
      try {
        resolve(JSON.parse(stdout));
      } catch (_error) {
        console.error('metadata_db_cli stdout (raw):', stdout);
        reject(new Error('failed to parse metadata db cli output'));
      }
    });

    python.on('error', err => {
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
    } catch (_error) {
      res.status(500).json({ error: 'metadata search failed' });
    }
  });

  // History endpoint
  app.get(
    '/api/metadata/history',
    requireAuth,
    async (req: AuthRequest, res) => {
      try {
        // Verify user is authenticated and get their ID
        if (!req.user?.id) {
          return res.status(401).json({ error: 'Authentication required' });
        }

        // Use Python script to get metadata history for this user
        const pythonProcess = spawn('python3', [
          path.join(currentDirPath, 'metadata-history.py'),
          '--user-id',
          req.user.id,
          '--limit',
          '50',
        ]);

        let data = '';
        pythonProcess.stdout.on('data', chunk => {
          data += chunk.toString();
        });

        pythonProcess.on('close', code => {
          if (code !== 0) {
            return res
              .status(500)
              .json({ error: 'Failed to get metadata history' });
          }

          try {
            const history = JSON.parse(data);
            res.json({ history });
          } catch (error) {
            console.error('Failed to parse metadata history:', error);
            res.status(500).json({ error: 'Failed to parse metadata history' });
          }
        });
      } catch (error) {
        console.error('Error getting metadata history:', error);
        res.status(500).json({ error: 'Internal server error' });
      }
    }
  );

  // Stats endpoint
  app.get('/api/metadata/stats', async (req, res) => {
    try {
      const stats = await runMetadataDbCli(['stats']);
      res.json(stats);
    } catch (_error) {
      res.status(500).json({ error: 'metadata stats failed' });
    }
  });

  // Favorites list endpoint
  app.get(
    '/api/metadata/favorites',
    requireAuth,
    async (req: AuthRequest, res) => {
      try {
        // Verify user is authenticated and get their ID
        if (!req.user?.id) {
          return res.status(401).json({ error: 'Authentication required' });
        }

        // Use Python script to get favorites for this user
        const pythonProcess = spawn('python3', [
          path.join(currentDirPath, 'metadata-favorites.py'),
          '--user-id',
          req.user.id,
          '--action',
          'list',
        ]);

        let data = '';
        pythonProcess.stdout.on('data', chunk => {
          data += chunk.toString();
        });

        pythonProcess.on('close', code => {
          if (code !== 0) {
            return res.status(500).json({ error: 'Failed to get favorites' });
          }

          try {
            const favorites = JSON.parse(data);
            res.json({ favorites });
          } catch (error) {
            console.error('Failed to parse favorites:', error);
            res.status(500).json({ error: 'Failed to parse favorites' });
          }
        });
      } catch (error) {
        console.error('Error getting favorites:', error);
        res.status(500).json({ error: 'Internal server error' });
      }
    }
  );

  // Favorites toggle endpoint
  app.post(
    '/api/metadata/favorites',
    requireAuth,
    async (req: AuthRequest, res) => {
      try {
        // Verify user is authenticated and get their ID
        if (!req.user?.id) {
          return res.status(401).json({ error: 'Authentication required' });
        }

        const { fileId, action } = req.body;

        if (!fileId || !action) {
          return res
            .status(400)
            .json({ error: 'fileId and action are required' });
        }

        // Use Python script to manage favorites for this user
        const pythonProcess = spawn('python3', [
          path.join(currentDirPath, 'metadata-favorites.py'),
          '--user-id',
          req.user.id,
          '--action',
          action,
          '--file-id',
          fileId,
        ]);

        let data = '';
        pythonProcess.stdout.on('data', chunk => {
          data += chunk.toString();
        });

        pythonProcess.on('close', code => {
          if (code !== 0) {
            return res
              .status(500)
              .json({ error: 'Failed to manage favorites' });
          }

          try {
            const result = JSON.parse(data);
            res.json(result);
          } catch (error) {
            console.error('Failed to parse result:', error);
            res.status(500).json({ error: 'Failed to parse result' });
          }
        });
      } catch (error) {
        console.error('Error managing favorites:', error);
        res.status(500).json({ error: 'Internal server error' });
      }
    }
  );

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
    } catch (_error) {
      res.status(500).json({ error: 'similarity search failed' });
    }
  });
}
