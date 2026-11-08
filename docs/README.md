# TÀI LIỆU BÀN GIAO HỆ THỐNG

## PITECH LAB — Dynamic Portfolio (CV Profile Platform)

| Mục | Nội dung |
|---|---|
| **Tên dự án** | Dynamic Portfolio / PITECH LAB CV Profile Platform |
| **Mã nguồn** | `https://github.com/dao24092004/pitechlab-cv-profile.git` |
| **Nhánh chính** | `main` (commit `886de4b` — *Merge pull request #5 from dao24092004/Update-UI*) |
| **Phạm vi tài liệu** | **Frontend (React + Vite)** — toàn bộ 4.807 dòng mã nguồn, 4 trang, 18 component |
| **Ngoài phạm vi** | Backend Spring Boot (repo riêng), hạ tầng triển khai, quản trị CSDL |
| **Ngày bàn giao** | 08/11/2026 |

---

## 1. Mục đích tài liệu

Bộ tài liệu này dùng cho **hai mục tiêu tách biệt**:

1. **Đặc tả (Specification)** — mô tả *hệ thống này làm gì, dữ liệu nào đi qua đâu, hành vi từng tác vụ như thế nào*. Dùng để đối chiếu khi nghiệm thu, và làm đầu vào cho việc phát triển tiếp.
2. **Hướng dẫn (Guide)** — mô tả *cài đặt, chạy, vận hành, xử lý sự cố*. Dùng để người mới tiếp nhận có thể dựng và sửa hệ thống mà không cần đọc mã nguồn.

> **Lưu ý về phạm vi.** Repo này **chỉ chứa frontend**. Toàn bộ dữ liệu đều đến từ backend qua REST API và STOMP/WebSocket. Tài liệu này **ghi nhận các điểm tích hợp (endpoint, topic, header) mà frontend đang sử dụng** như một *danh mục phụ thuộc* để bên backend đối chiếu — **không** đặc tả thiết kế backend, không định nghĩa lại schema dữ liệu, không quy định nghiệp vụ phía server.

---

## 2. Cấu trúc bộ tài liệu

| # | Tài liệu | Nội dung | Đối tượng |
|---|---|---|---|
| 01 | [Tổng quan hệ thống](./01-TONG-QUAN-HET-THONG.md) | Kiến trúc, công nghệ, cấu trúc mã nguồn, luồng dữ liệu, mô hình phân quyền | Tất cả |
| 02 | [Đặc tả chức năng](./02-DAC-TA-CHUC-NANG.md) | Đặc tả chi tiết từng màn hình, từng tác vụ người dùng, quy tắc nghiệp vụ, xử lý lỗi | Người nghiệm thu, dev |
| 03 | [Hướng dẫn cài đặt & sử dụng](./03-HUONG-DAN-CAI-DAT-VA-SU-DUNG.md) | Cài đặt, cấu hình môi trường, build, deploy, hướng dẫn dùng từng vai trò, xử lý sự cố | Người vận hành, dev mới |
| 04 | [Kiểm tra & bàn giao](./04-KIEM-TRA-VA-BAN-GIAO.md) | Checklist nghiệm thu theo vai trò, danh sách khiếm khuyết đã biết, kế hoạch khắc phục | Người nghiệm thu, quản lý dự án |
| 05 | [Phụ lục kỹ thuật](./05-PHU-LUC-KY-THUAT.md) | Danh mục phụ thuộc, endpoint REST, topic STOMP, biến môi trường, quy ước mã nguồn | Dev |
| 06 | [Báo cáo giao diện](./06-BAO-CAO-GIAO-DIEN.md) | 30 ảnh chụp màn hình thật của cả 3 vai trò + nhận xét nghiệm thu | Người nghiệm thu, GV |
| — | [README.md](../README.md) | Hướng dẫn chạy nhanh 5 phút | Tất cả |

### Báo cáo Word/PDF (để nộp)

| Tệp | Mô tả |
|---|---|
| [`Bao-cao-giao-dien-PITECHLAB-Dynamic-Portfolio.docx`](../Bao-cao-giao-dien-PITECHLAB-Dynamic-Portfolio.docx) | Báo cáo 27 trang A4, 30 hình, mục lục có số trang thật + phụ lục danh mục hình |
| [`Bao-cao-giao-dien-PITECHLAB-Dynamic-Portfolio.pdf`](../Bao-cao-giao-dien-PITECHLAB-Dynamic-Portfolio.pdf) | Bản PDF để in/đọc nhanh |
| [`Tai-lieu-ban-giao-PITECHLAB-Dynamic-Portfolio.docx`](../Tai-lieu-ban-giao-PITECHLAB-Dynamic-Portfolio.docx) | Bộ tài liệu đặc tả & bàn giao gộp (69 trang) |

---

## 3. Tóm tắt hệ thống trong 60 giây

Hệ thống là một **nền tảng portfolio động (CV Profile Platform)** cho tổ chức **PITECH LAB / INNOTECH SOLUTIONS**, cho phép:

- **Công khai** — mỗi nhân sự có một trang portfolio riêng, truy cập bằng đường dẫn phân cấp tổ chức (`/#/view/MB/HN/IT/12`), hiển thị đa ngôn ngữ Việt/Anh, có nút tải CV in ra PDF.
- **Quản trị (Admin)** — quản lý hồ sơ nhân sự, dữ liệu tổ chức 3 cấp (Vùng → Chi nhánh → Phòng ban), nhập CV tự động bằng AI, hội thoại chat trực tiếp và gọi video WebRTC với khách truy cập.
- **Cá nhân (User)** — mỗi nhân sự tự quản lý hồ sơ của mình (dự án, kỹ năng, kinh nghiệm, học vấn, công bố, thành tựu), xem liên kết chia sẻ, đổi mật khẩu.

Hai trụ cột kỹ thuật nổi bật:

1. **Realtime bằng STOMP over SockJS** — chat và tín hiệu gọi video đi qua WebSocket.
2. **WebRTC peer-to-peer** — gọi video trực tiếp giữa trình duyệt khách và trình duyệt quản trị, STOMP chỉ đóng vai trò kênh báo hiệu (signaling).

---

## 4. Bản đồ tài liệu ↔ mã nguồn

| Nhóm tài liệu | File mã nguồn tương ứng |
|---|---|
| Định tuyến, bảo vệ route | `App.tsx` |
| Trang công khai | `pages/Home.tsx`, `components/ZigZagSection.tsx`, `components/ProjectModal.tsx`, `components/PortfolioPrintTemplate.tsx` |
| Trang đăng nhập | `pages/Login.tsx` |
| Bảng điều khiển Admin | `pages/Admin.tsx` |
| Bảng điều khiển User | `pages/User.tsx` |
| Lớp giao tiếp API | `services/api.ts` |
| Kiểu dữ liệu | `types/index.ts` |
| Đa ngôn ngữ | `utils/translations.ts` |
| Chat & video call | `components/ChatWidget.tsx`, `components/VideoCallInterface.tsx` |
| Giao diện & hiệu ứng | `components/Header.tsx`, `DarkModeSwitch.tsx`, `MagneticWrapper.tsx`, `TextReveal.tsx`, `SkillFlipCard.tsx`, `ProjectCarousel.tsx`, `ImageViewer.tsx`, `CustomCursor.tsx`, `Avatar3D.tsx`, `AvatarBox.tsx`, `TechScene.tsx`, `ThreeScene.tsx`, `LanguageSwitcher.tsx` |
| Cấu hình build | `vite.config.ts`, `tsconfig.json`, `tailwind.config.js`, `index.html`, `index.css`, `index.tsx`, `package.json` |
