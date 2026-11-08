#!/usr/bin/env node
/**
 * Chụp ảnh giao diện PITECH LAB Dynamic Portfolio.
 *
 * Dùng puppeteer-core + Google Chrome hệ thống (không tải Chromium).
 * - Mỗi vai trò dùng MỘT page riêng (vì điều hướng bằng hash không
 *   reload document nên localStorage không được seed lại).
 * - Chụp theo viewport và theo từng <section id> để có ảnh cắt gọn.
 * - Chụp ở deviceScaleFactor = 2 cho bản in sắc nét.
 */
const fs = require('fs');
const path = require('path');
const puppeteer = require('puppeteer-core');

const BASE = process.env.APP_URL || 'http://127.0.0.1:3011';
const OUT = path.resolve(__dirname, '../assets/screenshots');
const CHROME = '/usr/bin/google-chrome';

const sleep = (ms) => new Promise((r) => setTimeout(r, ms));

const ADMIN_AUTH = {
  token: 'mock-token-admin', role: 'ADMIN', profileId: '1',
  username: 'admin', fullName: 'Quản trị viên',
};
const USER_AUTH = {
  token: 'mock-token-user', role: 'USER', profileId: '1',
  username: 'minhdao', fullName: 'PHẠM MINH ĐÀO',
};

const errors = [];

async function newPage(browser, auth) {
  const page = await browser.newPage();
  await page.setViewport({ width: 1600, height: 1000, deviceScaleFactor: 2 });
  await page.evaluateOnNewDocument((a) => {
    localStorage.setItem('app_lang', 'vi');
    Object.entries(a).forEach(([k, v]) => localStorage.setItem(k, v));
  }, auth);
  page.on('console', (m) => { if (m.type() === 'error') errors.push(m.text()); });
  page.on('pageerror', (e) => errors.push(String(e)));
  return page;
}

async function goto(page, hash) {
  await page.goto(`${BASE}/${hash}`, { waitUntil: 'domcontentloaded', timeout: 30000 });
  await sleep(1500);
}

/** Chụp 1 element theo selector; trả về false nếu không tìm thấy. */
async function shotEl(page, selector, file, pad = 12) {
  const el = await page.$(selector);
  if (!el) { console.log('  – không có:', selector); return false; }
  const box = await el.boundingBox();
  if (!box || box.height < 20) { console.log('  – rỗng:', selector); return false; }
  await page.screenshot({
    path: path.join(OUT, file),
    clip: {
      x: Math.max(0, box.x - pad),
      y: Math.max(0, box.y - pad),
      width: Math.min(1600 - Math.max(0, box.x - pad), box.width + pad * 2),
      height: Math.min(2000, box.height + pad * 2),
    },
  });
  console.log('  ✓', file, `(${Math.round(box.width)}x${Math.round(box.height)})`);
  return true;
}

/** Click 1 tab trong sidebar admin / user theo nhãn hiển thị. */
async function clickTab(page, label) {
  return page.evaluate((l) => {
    const norm = (s) => s.replace(/\s+/g, ' ').trim().toLowerCase();
    const want = norm(l);
    const els = [...document.querySelectorAll('nav button, aside button, button')];
    const el = els.find((e) => norm(e.textContent || '') === want);
    if (el) { el.click(); return true; }
    return false;
  }, label);
}

async function shotPanel(page, file) {
  await page.screenshot({ path: path.join(OUT, file) });
  console.log('  ✓', file);
}

(async () => {
  fs.mkdirSync(OUT, { recursive: true });
  const browser = await puppeteer.launch({
    executablePath: CHROME,
    headless: 'new',
    args: [
      '--no-sandbox', '--disable-setuid-sandbox', '--disable-dev-shm-usage',
      '--hide-scrollbars', '--use-gl=swiftshader', '--enable-unsafe-swiftshader',
      '--enable-webgl', '--ignore-gpu-blocklist', '--font-render-hinting=none',
    ],
  });

  // =============================================================== HOME
  console.log('\n[1] Trang chủ (khách)');
  {
    const page = await newPage(browser, {});
    await goto(page, '#/');
    await sleep(4500);

    await page.screenshot({ path: path.join(OUT, '01_home_hero.png') });
    console.log('  ✓ 01_home_hero.png');

    await shotEl(page, '#experience', '02_home_experience.png');
    await shotEl(page, '#projects', '03_home_projects.png');
    await shotEl(page, '#education', '04_home_education.png');
    await shotEl(page, '#skills', '05_home_skills.png');
    await shotEl(page, '#publications', '06_home_publications.png');
    await shotEl(page, '#events', '07_home_events.png');

    await page.evaluate(() => window.scrollTo(0, document.body.scrollHeight));
    await sleep(1500);
    await page.screenshot({ path: path.join(OUT, '08_home_footer.png') });
    console.log('  ✓ 08_home_footer.png');

    // modal chi tiết dự án
    console.log('\n[2] Modal chi tiết dự án');
    await page.evaluate(() => window.scrollTo(0, 0));
    await sleep(800);
    const opened = await page.evaluate(() => {
      const btns = [...document.querySelectorAll('#projects button')];
      const b = btns.find((x) => /chi tiết|detail|xem|view/i.test(x.textContent)) || btns[0];
      if (b) { b.click(); return true; }
      return false;
    });
    if (opened) {
      await sleep(2500);
      await page.screenshot({ path: path.join(OUT, '09_home_project_modal.png') });
      console.log('  ✓ 09_home_project_modal.png');
    }
    await page.close();
  }

  // =============================================================== LOGIN
  console.log('\n[3] Trang đăng nhập');
  {
    const page = await newPage(browser, {});
    await goto(page, '#/login');
    await sleep(2500);
    await page.screenshot({ path: path.join(OUT, '10_login.png') });
    console.log('  ✓ 10_login.png');
    await page.close();
  }

  // =============================================================== ADMIN
  console.log('\n[4] Trang quản trị');
  {
    const page = await newPage(browser, ADMIN_AUTH);
    await goto(page, '#/admin');
    await sleep(4500);
    console.log('  URL:', page.url());
    await shotPanel(page, '11_admin_chat_inbox.png');

    const adminTabs = [
      ['profile list', '12_admin_profile_list.png'],
      ['profile', '13_admin_profile_edit.png'],
      ['account', '14_admin_account.png'],
      ['organization', '15_admin_organization.png'],
      ['projects', '16_admin_projects.png'],
      ['skills', '17_admin_skills.png'],
      ['experience', '18_admin_experience.png'],
      ['education', '19_admin_education.png'],
      ['publications', '20_admin_publications.png'],
      ['events', '21_admin_events.png'],
      ['cv import', '22_admin_cv_import.png'],
    ];
    for (const [label, file] of adminTabs) {
      const okClick = await clickTab(page, label);
      if (okClick) {
        await sleep(2200);
        await shotPanel(page, file);
      } else {
        console.log('  – không tìm thấy tab:', label);
      }
    }
    await page.close();
  }

  // =============================================================== USER
  console.log('\n[5] Trang người dùng');
  {
    const page = await newPage(browser, USER_AUTH);
    await goto(page, '#/user');
    await sleep(4500);
    console.log('  URL:', page.url());
    await shotPanel(page, '23_user_dashboard.png');

    const userTabs = [
      ['projects', '24_user_projects.png'],
      ['skills', '25_user_skills.png'],
      ['experience', '26_user_experience.png'],
      ['education', '27_user_education.png'],
      ['publications', '28_user_publications.png'],
      ['events', '29_user_events.png'],
      ['change password', '30_user_password.png'],
    ];
    for (const [label, file] of userTabs) {
      const okClick = await clickTab(page, label);
      if (okClick) {
        await sleep(2200);
        await shotPanel(page, file);
      } else {
        console.log('  – không tìm thấy tab:', label);
      }
    }
    await page.close();
  }

  await browser.close();
  if (errors.length) {
    console.log('\n⚠ LỖI CONSOLE (' + errors.length + '):');
    console.log([...new Set(errors)].slice(0, 12).join('\n'));
  } else {
    console.log('\n✓ Không có lỗi console.');
  }
})().catch((e) => { console.error('LỖI:', e); process.exit(1); });
