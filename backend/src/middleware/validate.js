/** validate.js — middleware kiểm tra JSON body + giới hạn kích thước. */
import { MAX_BYTES } from '../lib/store.js';

/** Express 5 đã có sẵn express.json(); middleware này chỉ chuẩn hoá lỗi. */
export function jsonErrorHandler(err, _req, res, _next) {
  if (err?.type === 'entity.parse.failed' || err instanceof SyntaxError) {
    return res.status(400).json({ message: 'Body không phải JSON hợp lệ' });
  }
  if (err?.type === 'entity.too.large') {
    return res.status(413).json({ message: 'Body vượt quá kích thước cho phép' });
  }
  return res.status(err?.status ?? 500).json({ message: err?.message ?? 'Lỗi máy chủ' });
}

/** Bắt lỗi HttpError ném từ store/routes → trả đúng status code. */
export function httpErrorHandler(err, _req, res, _next) {
  if (err && typeof err.status === 'number') {
    return res.status(err.status).json({ message: err.message });
  }
  // eslint-disable-next-line no-console
  console.error('[backend]', err);
  return res.status(500).json({ message: 'Lỗi máy chủ nội bộ' });
}

export const JSON_LIMIT = `${Math.max(1, Math.round(MAX_BYTES / 1024 / 1024))}mb`;
