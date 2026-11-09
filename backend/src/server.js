/**
 * server.js — PITECH LAB Backend (Node.js + Express, KHÔNG database).
 *
 * Chạy:
 *   npm start            → http://localhost:8080
 *   npm run dev           → watch mode
 *   PORT=8081 npm start   → đổi cổng
 *   STORAGE_ROOT=./data npm start → đổi thư mục lưu trữ
 */
import express from 'express';
import cors from 'cors';
import morgan from 'morgan';

import http from 'node:http';

import filesRouter from './routes/files.js';
import portfolioRouter from './routes/portfolio.js';
import miscRouter from './routes/misc.js';
import legacyRouter from './routes/legacy.js';
import { attachStomp } from './lib/stomp.js';
import { JSON_LIMIT, httpErrorHandler, jsonErrorHandler } from './middleware/validate.js';
import { ensureDir, STORAGE_ROOT } from './lib/store.js';

const app = express();
const PORT = Number(process.env.PORT ?? 8080);

app.disable('x-powered-by');
app.use(cors());
app.use(morgan('tiny'));
app.use(express.json({ limit: JSON_LIMIT }));
app.use(jsonErrorHandler);

/* --- Thứ tự quan trọng: route cụ thể trước, generic sau --- */
app.use('/api/v1/storage/portfolio', portfolioRouter);
app.use('/api/v1/storage', miscRouter);   // /health, / , /_index
app.use('/api/v1/storage', filesRouter);  // /:collection[/:docId]
/* Lớp tương thích mock backend cũ (FE vẫn gọi /portfolio, /admin/*, /auth/*...) */
app.use('/api/v1', legacyRouter);

app.get('/api/v1/health', (_req, res) => res.json({ status: 'UP', time: new Date().toISOString() }));

app.use((_req, res) => res.status(404).json({ message: 'Không tìm thấy endpoint' }));
// eslint-disable-next-line no-unused-vars
app.use(httpErrorHandler);

await ensureDir(STORAGE_ROOT);

const httpServer = http.createServer(app);
attachStomp(httpServer);

httpServer.listen(PORT, () => {
  // eslint-disable-next-line no-console
  console.log(`[backend] listening on http://localhost:${PORT}`);
  // eslint-disable-next-line no-console
  console.log(`[backend] storage root: ${STORAGE_ROOT}`);
  // eslint-disable-next-line no-console
  console.log(`[backend] stomp/sockjs at ws://localhost:${PORT}/ws`);
});

export default app;
