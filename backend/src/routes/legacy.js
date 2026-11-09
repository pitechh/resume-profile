/**
 * routes/legacy.js — Lớp tương thích mock backend cũ (scripts/mock_backend.py).
 *
 * FE hiện tại gọi các API nghiệp vụ: /portfolio, /admin/*, /user/*, /org/*,
 * /auth/*, /upload ... nhưng backend Node mới chỉ có /storage.
 * Router này cung cấp lại các endpoint đó (dữ liệu in-memory + seed mẫu)
 * để giao diện chạy ổn định trong lúc chờ backend Spring Boot thật.
 *
 * Mount tại: app.use('/api/v1', legacyRouter)
 */
import { Router } from 'express';
import { relay } from '../lib/stomp.js';

const router = Router();

const pick = (o, k, d = '') => (o?.[k] ?? d);

// ---------------------------------------------------------------- dữ liệu mẫu
const PROFILE = {
  id: 1,
  fullName: 'PHẠM MINH ĐÀO',
  userName: 'minhdao',
  titleVi: 'KỸ SƯ PHẦN MỀM | FULL-STACK DEVELOPER',
  titleEn: 'SOFTWARE ENGINEER | FULL-STACK DEVELOPER',
  jobTitle: 'Backend Developer / DevOps Engineer',
  bio: 'Kỹ sư phần mềm với hơn 3 năm kinh nghiệm thiết kế và vận hành hệ thống web phân tán.',
  avatarUrl: 'https://placehold.co/600x800/1F3B73/FFFFFF?text=MINH+DAO',
  strengths: 'Problem Solving',
  workStyle: 'Professional',
  regionName: 'Miền Bắc',
  localOrgName: 'Chi nhánh Hà Nội',
  departmentName: 'Phòng Công nghệ Phần mềm',
  departmentId: 3,
  contact: {
    email: 'minhdao.pitechlab@gmail.com',
    github: 'https://github.com/dao24092004',
    linkedin: 'https://www.linkedin.com/in/dao24092004',
    address: 'Hà Nội, Việt Nam',
    phone: '0904 140 022',
  },
  projects: [
    {
      id: 1,
      name: 'Hệ thống Quản lý Hồ sơ Năng lực (CV Profile Platform)',
      description: 'Nền tảng portfolio động cho tổ chức.',
      imageUrl: 'https://placehold.co/600x400/1F3B73/FFFFFF?text=Project+1',
      techStack: 'Spring Boot, React',
      sourceCodeUrl: 'https://github.com/dao24092004/pitechlab-cv-profile',
      role: 'Backend Lead',
      customer: 'Pet Project',
    },
  ],
  workHistory: [
    {
      id: 1,
      companyName: 'PITECH LAB',
      position: 'Backend Developer',
      startDate: '2022-01-01',
      endDate: '',
      isCurrent: true,
      description: 'Phát triển hệ thống portfolio động.',
    },
  ],
  skills: [{ id: 1, name: 'Java', proficiency: 90, category: 'Backend' }],
  education: [
    { id: 1, school: 'Đại học Bách Khoa', degree: 'Kỹ sư CNTT', period: '2018-2022', description: '' },
  ],
  publications: [],
  events: [],
};

const PROFILE_LIST = [
  { id: 1, fullName: 'PHẠM MINH ĐÀO', jobTitle: 'Backend Developer', avatarUrl: PROFILE.avatarUrl, userName: 'minhdao' },
  { id: 2, fullName: 'NGUYỄN THỊ BÍCH NGỌC', jobTitle: 'Frontend Developer', avatarUrl: 'https://placehold.co/300x300/1F3B73/FFFFFF?text=BICH+NGOC', userName: 'bichngoc' },
  { id: 3, fullName: 'TRẦN VĂN HÙNG', jobTitle: 'DevOps Engineer', avatarUrl: 'https://placehold.co/300x300/1F3B73/FFFFFF?text=VAN+HUNG', userName: 'vanhung' },
];

const REGIONS = [{ id: 1, name: 'Miền Bắc', code: 'MB' }];
const LOCALS = [{ id: 1, name: 'Chi nhánh Hà Nội', code: 'HN', regionId: 1, regionName: 'Miền Bắc' }];
const DEPARTMENTS = [{ id: 3, name: 'Phòng Công nghệ Phần mềm', code: 'IT', localOrgId: 1, localOrgName: 'Chi nhánh Hà Nội' }];

const USERS = {
  admin: { role: 'ADMIN', profileId: 1, username: 'admin', fullName: 'Quản trị viên' },
  minhdao: { role: 'USER', profileId: 1, username: 'minhdao', fullName: 'Phạm Minh Đào' },
};

const SUB = {
  projects: 'projects',
  skills: 'skills',
  experiences: 'workHistory',
  educations: 'education',
  publications: 'publications',
  events: 'events',
};

const findItem = (sub, sid) => (PROFILE[SUB[sub]] || []).find((x) => x.id === Number(sid));

const makeItem = (sub, body) => {
  const b = body || {};
  if (sub === 'projects') {
    return {
      id: b.id ?? 99, name: b.title ?? b.name, description: b.description ?? '',
      imageUrl: b.imageUrl ?? '', techStack: (b.technologies || []).join(', '),
      sourceCodeUrl: b.repoUrl ?? '', role: b.role ?? '', customer: b.customer ?? '',
    };
  }
  if (sub === 'skills') return { id: b.id ?? 99, name: b.name ?? '', proficiency: b.proficiency ?? 50, category: b.category ?? '' };
  if (sub === 'experiences') {
    return {
      id: b.id ?? 99, companyName: b.company ?? '', position: b.role ?? '',
      startDate: b.startDate ?? '', endDate: b.endDate ?? '',
      isCurrent: b.isCurrent ?? false, description: b.description ?? '',
    };
  }
  if (sub === 'educations') return { id: b.id ?? 99, school: b.school ?? '', degree: b.degree ?? '', period: b.year ?? '', description: b.description ?? '' };
  if (sub === 'publications') return { id: b.id ?? 99, title: b.title ?? '', publisher: b.publisher ?? '', releaseDate: b.releaseDate ?? '', link: b.url ?? '' };
  return { id: b.id ?? 99, name: b.name ?? '', role: b.role ?? '', date: b.date ?? '', description: b.description ?? '', imageUrl: b.imageUrl ?? '' };
};

// ---------------------------------------------------------------- portfolio
router.get('/portfolio', (_req, res) => res.json(PROFILE));
router.get('/admin/portfolio/:pid', (_req, res) => res.json(PROFILE));
router.get('/view/code/:r/:l/:d/:pid', (_req, res) => res.json(PROFILE));
router.get('/view/:r/:l/:pid', (_req, res) => res.json(PROFILE));
router.get('/view/:r/:pid', (_req, res) => res.json(PROFILE));
router.get('/user/profile', (_req, res) => res.json([PROFILE]));
router.get('/user/portfolio/:pid', (_req, res) => res.json(PROFILE));
router.put('/user/profile', (req, res) => {
  Object.assign(PROFILE, Object.fromEntries(Object.entries(req.body || {}).filter(([k]) => k in PROFILE)));
  relay('/topic/public/updates', 'PROFILE_UPDATED');
  res.json(PROFILE);
});
router.put('/admin/profile', (req, res) => {
  const body = req.body || {};
  for (const [k, v] of Object.entries(body)) if (k in PROFILE && k !== 'id') PROFILE[k] = v;
  relay('/topic/public/updates', 'PROFILE_UPDATED');
  res.json(PROFILE);
});
router.delete('/admin/profile/:pid', (_req, res) => res.json({ status: 'deleted' }));
router.post('/admin/profile/:pid/activate', (_req, res) => res.json({ status: 'active' }));
router.get('/admin/list', (req, res) => {
  const page = Number(req.query.page ?? 0);
  const size = Number(req.query.size ?? 6);
  const content = PROFILE_LIST.slice(page * size, page * size + size);
  res.json({ content, totalPages: Math.ceil(PROFILE_LIST.length / size), totalElements: PROFILE_LIST.length, number: page, size });
});

// ------------------------------------------------- CRUD thực thể con (mock)
const registerSub = (prefix) => {
  router.get(`/${prefix}/:sub`, (req, res) => res.json(PROFILE[SUB[req.params.sub]] ?? []));
  router.post(`/${prefix}/:sub`, (req, res) => {
    const item = makeItem(req.params.sub, req.body);
    (PROFILE[SUB[req.params.sub]] ??= []).push(item);
    res.json(item);
  });
  router.get(`/${prefix}/:sub/:sid`, (req, res) => res.json(findItem(req.params.sub, req.params.sid) || {}));
  router.put(`/${prefix}/:sub/:sid`, (req, res) => {
    const sid = Number(req.params.sid);
    const item = makeItem(req.params.sub, { ...(findItem(req.params.sub, sid) || {}), ...(req.body || {}) });
    item.id = sid;
    const lst = (PROFILE[SUB[req.params.sub]] ??= []);
    const i = lst.findIndex((x) => x.id === sid);
    if (i >= 0) lst[i] = item; else lst.push(item);
    res.json(item);
  });
  router.delete(`/${prefix}/:sub/:sid`, (req, res) => {
    const sid = Number(req.params.sid);
    PROFILE[SUB[req.params.sub]] = (PROFILE[SUB[req.params.sub]] || []).filter((x) => x.id !== sid);
    res.json({ status: 'deleted' });
  });
};
registerSub('admin');
registerSub('user');

// ------------------------------------------------------------------- org
router.get('/org/regions', (_req, res) => res.json(REGIONS));
router.post('/org/regions', (req, res) => {
  const body = { id: REGIONS.length + 1, ...(req.body || {}) };
  REGIONS.push(body);
  res.json(body);
});
router.put('/org/regions/:rid', (req, res) => {
  const i = REGIONS.findIndex((r) => r.id === Number(req.params.rid));
  if (i >= 0) REGIONS[i] = { ...REGIONS[i], ...(req.body || {}) };
  res.json(req.body || {});
});
router.delete('/org/regions/:rid', (req, res) => {
  const i = REGIONS.findIndex((r) => r.id === Number(req.params.rid));
  if (i >= 0) REGIONS.splice(i, 1);
  res.json({ status: 'deleted' });
});
router.get('/org/locals', (_req, res) => res.json(LOCALS));
router.post('/org/locals', (req, res) => {
  const body = { id: LOCALS.length + 1, ...(req.body || {}) };
  LOCALS.push(body);
  res.json(body);
});
router.put('/org/locals/:lid', (req, res) => {
  const i = LOCALS.findIndex((x) => x.id === Number(req.params.lid));
  if (i >= 0) LOCALS[i] = { ...LOCALS[i], ...(req.body || {}) };
  res.json(req.body || {});
});
router.delete('/org/locals/:lid', (req, res) => {
  const i = LOCALS.findIndex((x) => x.id === Number(req.params.lid));
  if (i >= 0) LOCALS.splice(i, 1);
  res.json({ status: 'deleted' });
});
router.get('/org/departments', (_req, res) => res.json(DEPARTMENTS));
router.post('/org/departments', (req, res) => {
  const body = { id: DEPARTMENTS.length + 1, ...(req.body || {}) };
  DEPARTMENTS.push(body);
  res.json(body);
});
router.put('/org/departments/:did', (req, res) => {
  const i = DEPARTMENTS.findIndex((x) => x.id === Number(req.params.did));
  if (i >= 0) DEPARTMENTS[i] = { ...DEPARTMENTS[i], ...(req.body || {}) };
  res.json(req.body || {});
});
router.delete('/org/departments/:did', (req, res) => {
  const i = DEPARTMENTS.findIndex((x) => x.id === Number(req.params.did));
  if (i >= 0) DEPARTMENTS.splice(i, 1);
  res.json({ status: 'deleted' });
});

// ------------------------------------------------------------------ auth
router.post('/auth/login', (req, res) => {
  const u = String(req.body?.username || '').trim();
  if (!USERS[u]) return res.status(401).json({ message: 'Tài khoản hoặc mật khẩu không đúng.' });
  res.json({ token: `mock-token-${Date.now().toString(36)}`, ...USERS[u] });
});
router.post('/auth/register', (req, res) => {
  const { username, profileId, fullName } = req.body || {};
  if (username) USERS[username] = { role: 'USER', profileId, username, fullName };
  res.json({ status: 'registered' });
});
router.post('/auth/change-password', (_req, res) => res.json({ status: 'changed' }));

// ------------------------------------------------------------------ khác
router.post('/upload', (req, res) => res.json(`/uploads/mock-${Date.now().toString(36)}.png`));
router.post('/admin/import-cv', (_req, res) => res.json({ status: 'imported' }));
router.post('/user/import-cv', (_req, res) => res.json({ status: 'imported' }));
router.get('/chat/history', (_req, res) => res.json([]));
router.get('/export/cv-data', (_req, res) => res.type('text/plain').send('CV export mock'));
router.get('/health', (_req, res) => res.json({ status: 'UP' }));

export default router;
