# 6. Báo cáo giao diện và nghiệm thu hệ thống

> Ảnh chụp trực tiếp từ môi trường chạy thật (Vite dev server + mock backend), kích thước 1600×1000 px, mật độ 2×.

## 6.1. Trang chủ — vùng Hero

![Hình 1. Trang chủ PITECH LAB — vùng Hero với nền cảnh 3D, thông tin cá nhân và thẻ thống kê](../assets/screenshots/01_home_hero.png)

**Hình 1. Trang chủ PITECH LAB — vùng Hero với nền cảnh 3D, thông tin cá nhân và thẻ thống kê**

Vùng hero chiếm một màn hình đầy đủ (`min-h-screen`). Bên trái là ảnh đại diện bo tròn kèm huy hiệu trạng thái, bên phải là khối thông tin tên, chức danh tiếng Việt/Anh và mô tả ngắn. Dải thẻ thống kê đóng vai trò bảng tóm tắt nhanh.

## 6.2. Kinh nghiệm làm việc

![Hình 2. Khu vực Kinh nghiệm làm việc hiển thị dạng dòng thời gian (timeline)](../assets/screenshots/02_home_experience.png)

**Hình 2. Khu vực Kinh nghiệm làm việc hiển thị dạng dòng thời gian (timeline)**

Mỗi mục hiển thị tên công ty, vị trí, khoảng thời gian và mô tả công việc. Mục đang làm việc được đánh dấu bằng nhãn màu cam nổi bật.

## 6.3. Dự án và cửa sổ chi tiết

![Hình 3. Lưới thẻ dự án kèm công nghệ sử dụng](../assets/screenshots/03_home_projects.png)

**Hình 3. Lưới thẻ dự án kèm công nghệ sử dụng**

Mỗi thẻ gồm ảnh đại diện, tên dự án, mô tả ngắn, danh sách công nghệ và liên kết tới mã nguồn/demo.

![Hình 4. Cửa sổ modal chi tiết dự án](../assets/screenshots/09_home_project_modal.png)

**Hình 4. Cửa sổ modal chi tiết dự án**

Modal hiển thị đầy đủ: mô tả, vai trò, khách hàng, công nghệ, liên kết mã nguồn và demo, có nền tối phủ toàn màn hình.

## 6.4. Học vấn, kỹ năng, công bố và sự kiện

![Hình 5. Khu vực Học vấn — thẻ trường học, bậc học và thời gian đào tạo](../assets/screenshots/04_home_education.png)

**Hình 5. Khu vực Học vấn — thẻ trường học, bậc học và thời gian đào tạo**

![Hình 6. Khu vực Kỹ năng — thanh biểu diễn mức độ thành thạo theo nhóm](../assets/screenshots/05_home_skills.png)

**Hình 6. Khu vực Kỹ năng — thanh biểu diễn mức độ thành thạo theo nhóm**

![Hình 7. Khu vực Công bố khoa học — nền tối tương phản cao](../assets/screenshots/06_home_publications.png)

**Hình 7. Khu vực Công bố khoa học — nền tối tương phản cao**

![Hình 8. Khu vực Sự kiện — giải thưởng, hội thảo và chứng chỉ](../assets/screenshots/07_home_events.png)

**Hình 8. Khu vực Sự kiện — giải thưởng, hội thảo và chứng chỉ**

![Hình 9. Chân trang trang chủ — thông tin liên hệ và bản quyền](../assets/screenshots/08_home_footer.png)

**Hình 9. Chân trang trang chủ — thông tin liên hệ và bản quyền**

## 6.5. Trang đăng nhập

![Hình 10. Trang đăng nhập PITECH LAB](../assets/screenshots/10_login.png)

**Hình 10. Trang đăng nhập PITECH LAB**

Form gồm hai trường tài khoản và mật khẩu, nút đăng nhập và liên kết hỗ trợ.

## 6.6. Giao diện quản trị viên

![Hình 11. Hộp thư của quản trị viên — danh sách hội thoại và khung trò chuyện](../assets/screenshots/11_admin_chat_inbox.png)

**Hình 11. Hộp thư của quản trị viên — danh sách hội thoại và khung trò chuyện**

Chat dùng STOMP qua SockJS. Khách gửi tin từ widget góc phải trang chủ; quản trị viên nhận tin trong hộp thư, có bộ đếm tin chưa đọc và gọi video WebRTC.

![Hình 12. Danh sách hồ sơ nhân sự dạng thẻ, có phân trang](../assets/screenshots/12_admin_profile_list.png)

**Hình 12. Danh sách hồ sơ nhân sự dạng thẻ, có phân trang**

Dữ liệu lấy từ `GET /api/v1/admin/list` với tham số page/size, mặc định 6 bản ghi.

![Hình 13. Màn hình chỉnh sửa hồ sơ — thông tin cá nhân, liên hệ và phân bổ tổ chức](../assets/screenshots/13_admin_profile_edit.png)

**Hình 13. Màn hình chỉnh sửa hồ sơ — thông tin cá nhân, liên hệ và phân bổ tổ chức**

![Hình 14. Quản lý tài khoản — cấp tài khoản cho hồ sơ và kiểm tra trạng thái](../assets/screenshots/14_admin_account.png)

**Hình 14. Quản lý tài khoản — cấp tài khoản cho hồ sơ và kiểm tra trạng thái**

![Hình 15. Quản lý cây tổ chức — Vùng, Chi nhánh và Phòng ban](../assets/screenshots/15_admin_organization.png)

**Hình 15. Quản lý cây tổ chức — Vùng, Chi nhánh và Phòng ban**

Ba cấp độ độc lập: Vùng → Chi nhánh → Phòng ban, quyết định đường dẫn chia sẻ hồ sơ.

![Hình 16. Quản lý dự án — thêm, sửa, xóa và tải ảnh lên](../assets/screenshots/16_admin_projects.png)

**Hình 16. Quản lý dự án — thêm, sửa, xóa và tải ảnh lên**

![Hình 17. Quản lý kỹ năng theo nhóm và mức độ thành thạo](../assets/screenshots/17_admin_skills.png)

**Hình 17. Quản lý kỹ năng theo nhóm và mức độ thành thạo**

![Hình 18. Quản lý kinh nghiệm làm việc](../assets/screenshots/18_admin_experience.png)

**Hình 18. Quản lý kinh nghiệm làm việc**

![Hình 19. Quản lý học vấn](../assets/screenshots/19_admin_education.png)

**Hình 19. Quản lý học vấn**

![Hình 20. Quản lý công bố khoa học](../assets/screenshots/20_admin_publications.png)

**Hình 20. Quản lý công bố khoa học**

![Hình 21. Quản lý sự kiện, giải thưởng và chứng chỉ](../assets/screenshots/21_admin_events.png)

**Hình 21. Quản lý sự kiện, giải thưởng và chứng chỉ**

![Hình 22. Nhập CV từ tệp — nạp dữ liệu hồ sơ từ CV đã có](../assets/screenshots/22_admin_cv_import.png)

**Hình 22. Nhập CV từ tệp — nạp dữ liệu hồ sơ từ CV đã có**

## 6.7. Giao diện người dùng nội bộ

![Hình 23. Bảng điều khiển người dùng — thông tin tài khoản và lựa chọn nhanh](../assets/screenshots/23_user_dashboard.png)

**Hình 23. Bảng điều khiển người dùng — thông tin tài khoản và lựa chọn nhanh**

![Hình 24. Tự quản lý danh sách dự án của bản thân](../assets/screenshots/24_user_projects.png)

**Hình 24. Tự quản lý danh sách dự án của bản thân**

![Hình 25. Tự cập nhật kỹ năng và mức độ thành thạo](../assets/screenshots/25_user_skills.png)

**Hình 25. Tự cập nhật kỹ năng và mức độ thành thạo**

![Hình 26. Tự cập nhật kinh nghiệm làm việc](../assets/screenshots/26_user_experience.png)

**Hình 26. Tự cập nhật kinh nghiệm làm việc**

![Hình 27. Tự cập nhật thông tin học vấn](../assets/screenshots/27_user_education.png)

**Hình 27. Tự cập nhật thông tin học vấn**

![Hình 28. Tự cập nhật danh mục công bố](../assets/screenshots/28_user_publications.png)

**Hình 28. Tự cập nhật danh mục công bố**

![Hình 29. Tự cập nhật sự kiện và giải thưởng](../assets/screenshots/29_user_events.png)

**Hình 29. Tự cập nhật sự kiện và giải thưởng**

![Hình 30. Đổi mật khẩu — yêu cầu nhập mật khẩu cũ để xác nhận](../assets/screenshots/30_user_password.png)

**Hình 30. Đổi mật khẩu — yêu cầu nhập mật khẩu cũ để xác nhận**

## 6.9. Danh mục hình ảnh

| Ký hiệu | Nội dung | Tệp ảnh |
|---|---|---|
| Hình 1 | Trang chủ PITECH LAB — vùng Hero với nền cảnh 3D, thông tin cá nhân và thẻ thống kê | `01_home_hero.png` |
| Hình 2 | Khu vực Kinh nghiệm làm việc hiển thị dạng dòng thời gian (timeline) | `02_home_experience.png` |
| Hình 3 | Lưới thẻ dự án kèm công nghệ sử dụng | `03_home_projects.png` |
| Hình 4 | Cửa sổ modal chi tiết dự án | `09_home_project_modal.png` |
| Hình 5 | Khu vực Học vấn — thẻ trường học, bậc học và thời gian đào tạo | `04_home_education.png` |
| Hình 6 | Khu vực Kỹ năng — thanh biểu diễn mức độ thành thạo theo nhóm | `05_home_skills.png` |
| Hình 7 | Khu vực Công bố khoa học — nền tối tương phản cao | `06_home_publications.png` |
| Hình 8 | Khu vực Sự kiện — giải thưởng, hội thảo và chứng chỉ | `07_home_events.png` |
| Hình 9 | Chân trang trang chủ — thông tin liên hệ và bản quyền | `08_home_footer.png` |
| Hình 10 | Trang đăng nhập PITECH LAB | `10_login.png` |
| Hình 11 | Hộp thư của quản trị viên — danh sách hội thoại và khung trò chuyện | `11_admin_chat_inbox.png` |
| Hình 12 | Danh sách hồ sơ nhân sự dạng thẻ, có phân trang | `12_admin_profile_list.png` |
| Hình 13 | Màn hình chỉnh sửa hồ sơ — thông tin cá nhân, liên hệ và phân bổ tổ chức | `13_admin_profile_edit.png` |
| Hình 14 | Quản lý tài khoản — cấp tài khoản cho hồ sơ và kiểm tra trạng thái | `14_admin_account.png` |
| Hình 15 | Quản lý cây tổ chức — Vùng, Chi nhánh và Phòng ban | `15_admin_organization.png` |
| Hình 16 | Quản lý dự án — thêm, sửa, xóa và tải ảnh lên | `16_admin_projects.png` |
| Hình 17 | Quản lý kỹ năng theo nhóm và mức độ thành thạo | `17_admin_skills.png` |
| Hình 18 | Quản lý kinh nghiệm làm việc | `18_admin_experience.png` |
| Hình 19 | Quản lý học vấn | `19_admin_education.png` |
| Hình 20 | Quản lý công bố khoa học | `20_admin_publications.png` |
| Hình 21 | Quản lý sự kiện, giải thưởng và chứng chỉ | `21_admin_events.png` |
| Hình 22 | Nhập CV từ tệp — nạp dữ liệu hồ sơ từ CV đã có | `22_admin_cv_import.png` |
| Hình 23 | Bảng điều khiển người dùng — thông tin tài khoản và lựa chọn nhanh | `23_user_dashboard.png` |
| Hình 24 | Tự quản lý danh sách dự án của bản thân | `24_user_projects.png` |
| Hình 25 | Tự cập nhật kỹ năng và mức độ thành thạo | `25_user_skills.png` |
| Hình 26 | Tự cập nhật kinh nghiệm làm việc | `26_user_experience.png` |
| Hình 27 | Tự cập nhật thông tin học vấn | `27_user_education.png` |
| Hình 28 | Tự cập nhật danh mục công bố | `28_user_publications.png` |
| Hình 29 | Tự cập nhật sự kiện và giải thưởng | `29_user_events.png` |
| Hình 30 | Đổi mật khẩu — yêu cầu nhập mật khẩu cũ để xác nhận | `30_user_password.png` |
