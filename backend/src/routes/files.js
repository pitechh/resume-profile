/** routes/files.js — CRUD generic: 1 collection = 1 thư mục, 1 document = 1 file .json */
import { Router } from 'express';
import {
  createDocument,
  deleteDocument,
  docPath,
  getDocument,
  importDocuments,
  listDocuments,
  patchDocument,
  putDocument,
  collectionDir,
} from '../lib/store.js';
import { promises as fs } from 'node:fs';

const router = Router();

/** Liệt kê document trong collection */
router.get('/:collection', async (req, res, next) => {
  try {
    const { collection } = req.params;
    const items = await listDocuments(collection);
    res.json({ collection, count: items.length, items });
  } catch (e) {
    next(e);
  }
});

/** Tạo document mới (id tự sinh nếu không gửi) */
router.post('/:collection', async (req, res, next) => {
  try {
    const result = await createDocument(req.params.collection, req.body ?? {});
    res.status(201).json(result);
  } catch (e) {
    next(e);
  }
});

/** Tải file .json gốc về máy — đặt TRƯỚC route /:collection/:docId */
router.get('/:collection/download/:docId', async (req, res, next) => {
  try {
    const file = docPath(req.params.collection, req.params.docId);
    try {
      await fs.access(file);
    } catch {
      const err = new Error(`Không tìm thấy document ${JSON.stringify(req.params.docId)}`);
      err.status = 404;
      throw err;
    }
    res.download(file, `${req.params.docId}.json`);
  } catch (e) {
    next(e);
  }
});

/** Gộp toàn bộ collection thành 1 file JSON để tải — đặt TRƯỚC /:collection/:docId */
router.get('/:collection/export', async (req, res, next) => {
  try {
    const { collection } = req.params;
    const items = await listDocuments(collection);
    const out = [];
    for (const it of items) {
      try {
        // eslint-disable-next-line no-await-in-loop
        out.push(await getDocument(collection, it.id));
      } catch { /* bỏ qua file lỗi */ }
    }
    res.setHeader('Content-Disposition', `attachment; filename="${collection}.json"`);
    res.json(out);
  } catch (e) {
    next(e);
  }
});

/** Nạp hàng loạt document — đặt TRƯỚC /:collection/:docId */
router.post('/import/:collection', async (req, res, next) => {
  try {
    const result = await importDocuments(req.params.collection, req.body ?? {});
    res.status(201).json(result);
  } catch (e) {
    next(e);
  }
});

/** Lấy 1 document */
router.get('/:collection/:docId', async (req, res, next) => {
  try {
    res.json(await getDocument(req.params.collection, req.params.docId));
  } catch (e) {
    next(e);
  }
});

/** Ghi đè / upsert 1 document */
router.put('/:collection/:docId', async (req, res, next) => {
  try {
    const result = await putDocument(req.params.collection, req.params.docId, req.body ?? {});
    res.json(result);
  } catch (e) {
    next(e);
  }
});

/** Merge một phần field */
router.patch('/:collection/:docId', async (req, res, next) => {
  try {
    const result = await patchDocument(req.params.collection, req.params.docId, req.body ?? {});
    res.json(result);
  } catch (e) {
    next(e);
  }
});

/** Xoá document */
router.delete('/:collection/:docId', async (req, res, next) => {
  try {
    res.json(await deleteDocument(req.params.collection, req.params.docId));
  } catch (e) {
    next(e);
  }
});

export default router;
