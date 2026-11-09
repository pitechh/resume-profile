/**
 * seed.js — Tạo dữ liệu mẫu vào storage/ để test ngay.
 *
 *   npm run seed
 */
import { createDocument, savePortfolioSnapshot, STORAGE_ROOT, ensureDir } from './lib/store.js';

await ensureDir(STORAGE_ROOT);

const profile = {
  id: 1,
  fullName: 'PHẠM MINH ĐÀO',
  jobTitle: 'Backend Developer / DevOps Engineer',
  bio: 'Kỹ sư phần mềm, chuyên Java/Spring Boot, React, DevSecOps.',
  contact: { email: 'minhdao.pitechlab@gmail.com', phone: '0904 140 022', location: 'Hà Nội, Việt Nam' },
  projects: [
    { title: 'CV Profile Platform', role: 'Backend Lead', technologies: ['Spring Boot', 'React'] },
  ],
  skills: [{ name: 'Java', proficiency: 90 }],
};

await savePortfolioSnapshot(1, profile);
console.log('seeded: portfolio/1');

for (const note of [
  { title: 'Ghi chú onboard', body: 'Checklist khi thêm nhân sự mới vào hệ thống.' },
  { title: 'Lịch backup', body: 'Copy thư mục storage/ mỗi tuần.' },
]) {
  try {
    const r = await createDocument('notes', { data: note, title: note.title });
    console.log('seeded: notes/%s', r.id);
  } catch (e) {
    if (e?.status !== 409) throw e;
    console.log('skip (đã có):', note.title);
  }
}

console.log('Xong. Storage:', STORAGE_ROOT);
