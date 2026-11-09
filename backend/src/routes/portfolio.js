/**
 * routes/portfolio.js — Tiện ích "lưu hồ sơ": snapshot có version.
 *
 *   POST /api/v1/storage/portfolio/:profileId  → lưu snapshot mới
 *   GET  /api/v1/storage/portfolio/:profileId  → lấy bản mới nhất (__current)
 *   GET  /api/v1/storage/portfolio/:profileId/versions → lịch sử các bản
 */
import { Router } from 'express';
import {
  getPortfolioSnapshot,
  listPortfolioVersions,
  savePortfolioSnapshot,
} from '../lib/store.js';

const router = Router();

router.post('/:profileId', async (req, res, next) => {
  try {
    const result = await savePortfolioSnapshot(req.params.profileId, req.body ?? {});
    res.status(201).json(result);
  } catch (e) {
    next(e);
  }
});

router.get('/:profileId/versions', async (req, res, next) => {
  try {
    res.json(await listPortfolioVersions(req.params.profileId));
  } catch (e) {
    next(e);
  }
});

router.get('/:profileId', async (req, res, next) => {
  try {
    res.json(await getPortfolioSnapshot(req.params.profileId));
  } catch (e) {
    next(e);
  }
});

export default router;
