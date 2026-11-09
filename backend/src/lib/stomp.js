/**
 * stomp.js — Broker STOMP tối giản trên SockJS cho chat & tín hiệu video.
 *
 * Tương thích @stomp/stompjs phía FE (giống mock_backend.py cũ):
 *   SEND /app/chat.sendToAdmin  → relay /topic/admin/messages + /topic/private/{senderId}
 *   SEND /app/chat.replyToUser  → relay /topic/admin/messages + /topic/private/{recipientId}
 *   SEND /app/video.request     → relay /topic/call-requests (+ /topic/private/1, + topic đích nếu body có profileId/recipientId)
 *   SEND /app/video.signal      → relay /topic/video/{roomId}
 *   SEND tới /topic/*           → relay trực tiếp (generic)
 *
 * FE dùng:  new SockJS(VITE_WS_URL)  với VITE_WS_URL = http://host:8080/ws
 * SockJS frame qua websocket transport: client gửi '["<STOMP frame>"]',
 * server trả 'a["<STOMP frame>"]' — sockjs package lo phần vỏ, ở đây chỉ
 * xử lý STOMP frame thô (kết thúc bằng \0).
 */
import sockjs from 'sockjs';

let seq = 0;

/** destination -> Set<{ conn, subId }> */
const subs = new Map();

const unescapeHeader = (s) =>
  String(s).replace(/\\r/g, '\r').replace(/\\n/g, '\n').replace(/\\c/g, ':').replace(/\\\\/g, '\\');

function parseStomp(raw) {
  const frames = [];
  for (const chunk of String(raw).split('\0')) {
    if (!chunk) continue;
    const idx = chunk.indexOf('\n\n');
    let head, body;
    if (idx === -1) {
      head = chunk;
      body = '';
    } else {
      head = chunk.slice(0, idx);
      body = chunk.slice(idx + 2);
    }
    const lines = head.split('\n');
    const command = (lines.shift() || '').replace(/\r$/, '');
    if (!command) continue;
    const headers = {};
    for (const line of lines) {
      const clean = line.replace(/\r$/, '');
      if (!clean) continue;
      const ci = clean.indexOf(':');
      if (ci === -1) continue;
      headers[clean.slice(0, ci)] = unescapeHeader(clean.slice(ci + 1));
    }
    frames.push({ command, headers, body });
  }
  return frames;
}

function sendFrame(conn, ...parts) {
  try {
    conn.write(`${parts.join('')}\x00`);
  } catch {
    /* kết nối đã chết — dọn ở sự kiện close */
  }
}

/** Gửi object (JSON) hoặc chuỗi thô tới mọi subscriber của destination. */
export function relay(destination, body) {
  const targets = subs.get(destination);
  if (!targets || targets.size === 0) return 0;
  const payload = typeof body === 'string' ? body : JSON.stringify(body);
  const len = Buffer.byteLength(payload, 'utf8');
  let n = 0;
  for (const { conn, subId } of [...targets]) {
    try {
      conn.write(
        `MESSAGE\nsubscription:${subId}\nmessage-id:msg-${++seq}\n` +
          `destination:${destination}\ncontent-type:application/json\ncontent-length:${len}\n\n${payload}\x00`,
      );
      n++;
    } catch {
      /* bỏ qua kết nối hỏng */
    }
  }
  return n;
}

function removeConn(conn, state) {
  for (const [subId, dest] of state.subs) {
    const set = subs.get(dest);
    if (set) {
      for (const e of set) {
        if (e.conn === conn && e.subId === subId) set.delete(e);
      }
      if (set.size === 0) subs.delete(dest);
    }
  }
  state.subs.clear();
}

function routeSend(frame) {
  const dest = frame.headers.destination || '';
  let parsed = frame.body;
  try {
    parsed = JSON.parse(frame.body);
  } catch {
    /* giữ nguyên chuỗi thô (vd 'PROFILE_UPDATED') */
  }
  const out = parsed !== undefined ? parsed : '';
  const b = out && typeof out === 'object' ? out : {};

  if (dest === '/app/chat.sendToAdmin') {
    relay('/topic/admin/messages', out);
    if (b.senderId) relay(`/topic/private/${b.senderId}`, out);
  } else if (dest === '/app/chat.replyToUser') {
    relay('/topic/admin/messages', out);
    if (b.recipientId) relay(`/topic/private/${b.recipientId}`, out);
  } else if (dest === '/app/video.request') {
    relay('/topic/call-requests', out);
    relay('/topic/private/1', out);
    if (b.profileId) relay(`/topic/call-requests/${b.profileId}`, out);
    if (b.recipientId) relay(`/topic/private/${b.recipientId}`, out);
  } else if (dest === '/app/video.signal') {
    if (b.roomId) relay(`/topic/video/${b.roomId}`, out);
  } else if (dest.startsWith('/topic/')) {
    relay(dest, out);
  }
  // destination lạ → bỏ qua (giống mock backend cũ)
}

function handleFrame(conn, state, frame) {
  const { command, headers } = frame;
  if (command === 'CONNECT' || command === 'STOMP') {
    sendFrame(conn, 'CONNECTED\nversion:1.2\nheart-beat:0,0\n\n');
    if (headers.receipt) sendFrame(conn, `RECEIPT\nreceipt-id:${headers.receipt}\n\n`);
  } else if (command === 'SUBSCRIBE') {
    const subId = headers.id ?? `sub-${state.subs.size}`;
    const dest = headers.destination || '';
    state.subs.set(subId, dest);
    if (!subs.has(dest)) subs.set(dest, new Set());
    subs.get(dest).add({ conn, subId });
    if (headers.receipt) sendFrame(conn, `RECEIPT\nreceipt-id:${headers.receipt}\n\n`);
  } else if (command === 'UNSUBSCRIBE') {
    const subId = headers.id;
    const dest = subId !== undefined ? state.subs.get(subId) : headers.destination;
    if (dest) {
      const set = subs.get(dest);
      if (set) {
        for (const e of set) {
          if (e.conn === conn && (subId === undefined || e.subId === subId)) set.delete(e);
        }
        if (set.size === 0) subs.delete(dest);
      }
    }
    if (subId !== undefined) state.subs.delete(subId);
  } else if (command === 'SEND') {
    routeSend(frame);
  } else if (command === 'DISCONNECT') {
    removeConn(conn, state);
    try {
      conn.close();
    } catch {
      /* kệ */
    }
  }
}

/** Gắn SockJS endpoint /ws vào http server đã có. */
export function attachStomp(httpServer) {
  const service = sockjs.createServer({
    prefix: '/ws',
    // eslint-disable-next-line no-console
    log: () => {},
  });
  service.on('connection', (conn) => {
    const state = { subs: new Map() };
    conn.on('data', (raw) => {
      try {
        for (const frame of parseStomp(raw)) handleFrame(conn, state, frame);
      } catch {
        /* frame lỗi → bỏ qua */
      }
    });
    conn.on('close', () => removeConn(conn, state));
  });
  service.installHandlers(httpServer, { prefix: '/ws' });
}
