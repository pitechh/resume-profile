/**
 * store.js — Tầng lưu trữ JSON trên filesystem (KHÔNG dùng database).
 *
 * Quy ước thư mục (mặc định: <backend>/storage):
 *
 *   storage/
 *     <collection>/
 *       <docId>.json            ← 1 document = 1 file JSON
 *     portfolio/
 *       <profileId>/
 *         __current.json        ← bản snapshot mới nhất
 *         <stamp>__<id>.json    ← các bản có version
 *     _index.json               ← metadata best-effort (không bắt buộc)
 *
 * Ghi file an toàn: ghi ra file .tmp rồi rename (tránh file hỏng khi crash).
 */
import { promises as fs } from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const __dirname = path.dirname(fileURLToPath(import.meta.url));

export const STORAGE_ROOT =
  process.env.STORAGE_ROOT
    ? path.resolve(process.env.STORAGE_ROOT)
    : path.resolve(__dirname, '..', '..', 'storage');

export const MAX_BYTES = Number(process.env.STORAGE_MAX_BYTES ?? 5 * 1024 * 1024); // 5 MB
export const MAX_FILES = Number(process.env.STORAGE_MAX_FILES ?? 1000);

const COLLECTION_RE = /^[A-Za-z0-9_.-]{1,64}$/;
const DOC_ID_RE = /^[A-Za-z0-9_.:-]{1,128}$/;

/** Collection dành riêng cho router khác — router files generic phải từ chối. */
export const RESERVED = new Set(['import', 'export', 'download', 'portfolio', 'health']);

export class HttpError extends Error {
  constructor(status, message) {
    super(message);
    this.status = status;
  }
}

export const nowIso = () => new Date().toISOString();

/** Biến chuỗi tự do thành doc_id an toàn cho filesystem. */
export function slug(text) {
  const s = String(text ?? '')
    .normalize('NFC')
    .replace(/[^\w\-. ]+/gu, '')
    .replace(/[\s_]+/g, '-')
    .replace(/^[.-]+|[.-]+$/g, '')
    .slice(0, 120);
  return s || `${Date.now().toString(36)}${Math.floor(Math.random() * 0xffff).toString(36)}`;
}

export function assertCollection(name) {
  if (!COLLECTION_RE.test(name ?? '') || RESERVED.has(name)) {
    throw new HttpError(400, `Tên collection không hợp lệ: ${JSON.stringify(name)}`);
  }
}

export function assertDocId(id) {
  if (!DOC_ID_RE.test(id ?? '')) {
    throw new HttpError(400, `doc_id không hợp lệ: ${JSON.stringify(id)}`);
  }
}

export const collectionDir = (collection) => path.join(STORAGE_ROOT, collection);
export const docPath = (collection, docId) => path.join(collectionDir(collection), `${docId}.json`);

export async function ensureDir(dir) {
  await fs.mkdir(dir, { recursive: true });
  return dir;
}

/** Ghi JSON nguyên tử: .tmp → rename. */
export async function atomicWrite(filePath, payload) {
  await ensureDir(path.dirname(filePath));
  const tmp = `${filePath}.tmp${process.pid}`;
  await fs.writeFile(tmp, JSON.stringify(payload, null, 2) + '\n', 'utf8');
  await fs.rename(tmp, filePath);
}

export async function readJson(filePath) {
  let raw;
  try {
    raw = await fs.readFile(filePath, 'utf8');
  } catch {
    throw new HttpError(404, `Không tìm thấy file: ${path.basename(filePath)}`);
  }
  if (Buffer.byteLength(raw, 'utf8') > MAX_BYTES) {
    throw new HttpError(413, 'File vượt quá kích thước cho phép');
  }
  try {
    return JSON.parse(raw);
  } catch (e) {
    throw new HttpError(500, `File JSON không hợp lệ: ${e.message}`);
  }
}

function withMeta(payload, collection, docId, createdAt) {
  const stamp = nowIso();
  return {
    ...(payload && typeof payload === 'object' && !Array.isArray(payload) ? payload : { value: payload }),
    _meta: {
      id: docId,
      collection,
      createdAt: createdAt ?? stamp,
      updatedAt: stamp,
    },
  };
}

/** Liệt kê document (metadata nhẹ + vài field phổ biến nếu có). */
export async function listDocuments(collection) {
  assertCollection(collection);
  const dir = collectionDir(collection);
  try {
    await fs.access(dir);
  } catch {
    return [];
  }
  const files = (await fs.readdir(dir)).filter((f) => f.endsWith('.json')).sort();
  const items = [];
  for (const file of files) {
    const full = path.join(dir, file);
    const stat = await fs.stat(full);
    const meta = {
      id: path.basename(file, '.json'),
      size: stat.size,
      updatedAt: stat.mtime.toISOString(),
    };
    try {
      const data = JSON.parse(await fs.readFile(full, 'utf8'));
      if (data && typeof data === 'object' && !Array.isArray(data)) {
        for (const key of ['title', 'name', 'label', 'version', 'profileId']) {
          if (['string', 'number'].includes(typeof data[key])) meta[key] = data[key];
        }
      }
    } catch { /* bỏ qua file lỗi khi liệt kê */ }
    items.push(meta);
  }
  return items;
}

/** Ghi metadata vào _index.json (best-effort). */
export async function writeIndex(entry) {
  try {
    const indexPath = path.join(STORAGE_ROOT, '_index.json');
    let index = [];
    try {
      const parsed = JSON.parse(await fs.readFile(indexPath, 'utf8'));
      if (Array.isArray(parsed)) index = parsed;
    } catch { /* file chưa có */ }
    index = [...index.filter((e) => e?.key !== entry.key), entry].slice(-500);
    await atomicWrite(indexPath, index);
  } catch { /* không làm hỏng request chính */ }
}

async function enforceLimit(collection) {
  const dir = collectionDir(collection);
  try {
    const files = (await fs.readdir(dir)).filter((f) => f.endsWith('.json'));
    if (files.length >= MAX_FILES) {
      throw new HttpError(507, `Collection ${JSON.stringify(collection)} đã đạt giới hạn ${MAX_FILES} file`);
    }
  } catch (e) {
    if (e instanceof HttpError) throw e;
    // thư mục chưa tồn tại → chưa vượt giới hạn
  }
}

/** Sinh id tự tăng dạng số ("1", "2", ...) để dễ đọc. */
export async function nextNumericId(collection) {
  const dir = collectionDir(collection);
  try {
    const files = await fs.readdir(dir);
    let max = 0;
    for (const f of files) {
      const stem = path.basename(f, '.json');
      if (/^\d+$/.test(stem)) max = Math.max(max, Number(stem));
    }
    return String(max + 1);
  } catch {
    return '1';
  }
}

export async function createDocument(collection, { id, data, title }) {
  assertCollection(collection);
  const docId = id ? slug(id) : await nextNumericId(collection);
  assertDocId(docId);
  const filePath = docPath(collection, docId);
  try {
    await fs.access(filePath);
    throw new HttpError(409, `Document ${JSON.stringify(docId)} đã tồn tại trong ${JSON.stringify(collection)}`);
  } catch (e) {
    if (e instanceof HttpError) throw e;
  }
  await enforceLimit(collection);
  const payload = withMeta(data ?? {}, collection, docId);
  await atomicWrite(filePath, payload);
  await writeIndex({ key: `${collection}/${docId}`, collection, id: docId, title, updatedAt: nowIso() });
  return { status: 'created', id: docId, collection, path: path.relative(STORAGE_ROOT, filePath) };
}

export async function getDocument(collection, docId) {
  assertCollection(collection);
  assertDocId(docId);
  return readJson(docPath(collection, docId));
}

export async function putDocument(collection, docId, { data, title }) {
  assertCollection(collection);
  assertDocId(docId);
  const filePath = docPath(collection, docId);
  let existed = true;
  let createdAt;
  try {
    const current = await readJson(filePath);
    createdAt = current?._meta?.createdAt;
  } catch (e) {
    if (e instanceof HttpError && e.status === 404) existed = false;
    else throw e;
  }
  const payload = withMeta(data ?? {}, collection, docId, createdAt);
  await atomicWrite(filePath, payload);
  await writeIndex({ key: `${collection}/${docId}`, collection, id: docId, title, updatedAt: nowIso() });
  return { status: existed ? 'updated' : 'created', id: docId, collection };
}

/** Merge nông 1 cấp (object con được merge, các kiểu khác ghi đè). */
export async function patchDocument(collection, docId, { data }) {
  assertCollection(collection);
  assertDocId(docId);
  const filePath = docPath(collection, docId);
  const current = await readJson(filePath); // 404 nếu chưa có
  const incoming = data ?? {};
  let next;
  if (typeof current !== 'object' || current === null || Array.isArray(current) ||
      typeof incoming !== 'object' || incoming === null || Array.isArray(incoming)) {
    next = withMeta(incoming, collection, docId, current?._meta?.createdAt);
  } else {
    next = { ...current };
    for (const [key, value] of Object.entries(incoming)) {
      if (key === '_meta') continue;
      if (value && typeof value === 'object' && !Array.isArray(value) &&
          next[key] && typeof next[key] === 'object' && !Array.isArray(next[key])) {
        next[key] = { ...next[key], ...value };
      } else {
        next[key] = value;
      }
    }
    next._meta = { ...current._meta, id: docId, collection, updatedAt: nowIso() };
  }
  await atomicWrite(filePath, next);
  return { status: 'patched', id: docId, collection };
}

export async function deleteDocument(collection, docId) {
  assertCollection(collection);
  assertDocId(docId);
  const filePath = docPath(collection, docId);
  try {
    await fs.unlink(filePath);
  } catch {
    throw new HttpError(404, `Không tìm thấy document ${JSON.stringify(docId)}`);
  }
  return { status: 'deleted', id: docId, collection };
}

export async function importDocuments(collection, { items = [], overwrite = false }) {
  assertCollection(collection);
  const created = [];
  const skipped = [];
  for (const item of items) {
    const docId = item?.id ? slug(item.id) : await nextNumericId(collection);
    const filePath = docPath(collection, docId);
    try {
      await fs.access(filePath);
      if (!overwrite) {
        skipped.push(docId);
        continue;
      }
    } catch { /* chưa có → tạo mới */ }
    await atomicWrite(filePath, withMeta(item?.data ?? {}, collection, docId));
    created.push(docId);
  }
  return { status: 'imported', collection, created, skipped };
}

/* ------------------------------------------------- portfolio snapshots */

const stampOf = () => {
  const d = new Date();
  const p = (n) => String(n).padStart(2, '0');
  return `${d.getFullYear()}-${p(d.getMonth() + 1)}-${p(d.getDate())}T${p(d.getHours())}-${p(d.getMinutes())}-${p(d.getSeconds())}`;
};

export async function savePortfolioSnapshot(profileId, body) {
  const pid = String(profileId);
  if (!/^\d{1,10}$/.test(pid)) throw new HttpError(400, 'profileId phải là số');
  const folder = path.join(collectionDir('portfolio'), pid);
  await ensureDir(folder);
  const version = stampOf();
  const payload = {
    ...(body ?? {}),
    _meta: { id: `${version}__${pid}`, collection: 'portfolio', profileId: Number(pid), version, ...{ createdAt: nowIso(), updatedAt: nowIso() } },
  };
  await atomicWrite(path.join(folder, `${version}__${pid}.json`), payload);
  await atomicWrite(path.join(folder, '__current.json'), payload);
  return { status: 'saved', profileId: Number(pid), version, path: `portfolio/${pid}/${version}__${pid}.json` };
}

export async function getPortfolioSnapshot(profileId) {
  const filePath = path.join(collectionDir('portfolio'), String(profileId), '__current.json');
  try {
    return await readJson(filePath);
  } catch (e) {
    if (e instanceof HttpError && e.status === 404) {
      throw new HttpError(404, `Chưa có bản lưu nào cho profile ${profileId}`);
    }
    throw e;
  }
}

export async function listPortfolioVersions(profileId) {
  const folder = path.join(collectionDir('portfolio'), String(profileId));
  try {
    await fs.access(folder);
  } catch {
    return { profileId: Number(profileId), count: 0, versions: [] };
  }
  const files = (await fs.readdir(folder)).filter((f) => f.endsWith('.json') && f !== '__current.json').sort();
  const versions = [];
  for (const f of files) {
    const stat = await fs.stat(path.join(folder, f));
    versions.push({ id: path.basename(f, '.json'), updatedAt: stat.mtime.toISOString() });
  }
  return { profileId: Number(profileId), count: versions.length, versions };
}
