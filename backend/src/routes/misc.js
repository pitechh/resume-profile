/**
 * routes/misc.js — health, danh sách collection, đọc _index.json
 */
import { Router } from 'express';
import { promises as fs } from 'node:fs';
import path from 'node:path';
import { MAX_BYTES, MAX_FILES, STORAGE_ROOT } from '../lib/store.js';

const router = Router();

router.get('/health', (_req, res) => {
  res.json({
    status: 'UP',
    service: 'pitechlab-backend',
    root: STORAGE_ROOT,
    maxBytes: MAX_BYTES,
    maxFilesPerCollection: MAX_FILES,
    time: new Date().toISOString(),
  });
});

router.get('/', async (_req, res, next) => {
  try {
    let collections = [];
    try {
      const entries = await fs.readdir(STORAGE_ROOT, { withFileTypes: true });
      for (const e of entries) {
        if (!e.isDirectory()) continue;
        const dir = path.join(STORAGE_ROOT, e.name);
        // eslint-disable-next-line no-await-in-loop
        const files = (await fs.readdir(dir)).filter((f) => f.endsWith('.json'));
        let totalSize = 0;
        for (const f of files) {
          // eslint-disable-next-line no-await-in-loop
          totalSize += (await fs.stat(path.join(dir, f))).size;
        }
        // eslint-disable-next-line no-await-in-loop
        const stat = await fs.stat(dir);
        collections.push({
          name: e.name,
          count: files.length,
          totalSize,
          updatedAt: stat.mtime.toISOString(),
        });
      }
      collections.sort((a, b) => a.name.localeCompare(b.name));
    } catch {
      collections = [];
    }
    res.json({ root: STORAGE_ROOT, collections });
  } catch (e) {
    next(e);
  }
});

router.get('/_index', async (_req, res) => {
  try {
    const raw = await fs.readFile(path.join(STORAGE_ROOT, '_index.json'), 'utf8');
    res.json(JSON.parse(raw));
  } catch {
    res.json([]);
  }
});

export default router;
