#!/usr/bin/env python3
"""
Sinh bản Markdown của báo cáo giao diện (để lưu trong repo / dán vào hệ quản lý).

Cách dùng:
    python3 scripts/build_screenshot_report_md.py
"""
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SHOTS = ROOT / "assets" / "screenshots"
OUT_MD = ROOT / "docs" / "06-BAO-CAO-GIAO-DIEN.md"

FIG = 0


def fig(file, caption, desc=""):
    global FIG
    FIG += 1
    rel = f"../assets/screenshots/{file}"
    out = [f"![Hình {FIG}. {caption}]({rel})", "", f"**Hình {FIG}. {caption}**"]
    if desc:
        out += ["", desc]
    out.append("")
    return "\n".join(out)


SECTIONS = [
    ("Trang chủ — vùng Hero", [
        ("01_home_hero.png",
         "Trang chủ PITECH LAB — vùng Hero với nền cảnh 3D, thông tin cá nhân và thẻ thống kê",
         "Vùng hero chiếm một màn hình đầy đủ (`min-h-screen`). Bên trái là ảnh đại diện bo "
         "tròn kèm huy hiệu trạng thái, bên phải là khối thông tin tên, chức danh tiếng "
         "Việt/Anh và mô tả ngắn. Dải thẻ thống kê đóng vai trò bảng tóm tắt nhanh."),
    ]),
    ("Kinh nghiệm làm việc", [
        ("02_home_experience.png",
         "Khu vực Kinh nghiệm làm việc hiển thị dạng dòng thời gian (timeline)",
         "Mỗi mục hiển thị tên công ty, vị trí, khoảng thời gian và mô tả công việc. "
         "Mục đang làm việc được đánh dấu bằng nhãn màu cam nổi bật."),
    ]),
    ("Dự án và cửa sổ chi tiết", [
        ("03_home_projects.png", "Lưới thẻ dự án kèm công nghệ sử dụng",
         "Mỗi thẻ gồm ảnh đại diện, tên dự án, mô tả ngắn, danh sách công nghệ và liên kết "
         "tới mã nguồn/demo."),
        ("09_home_project_modal.png", "Cửa sổ modal chi tiết dự án",
         "Modal hiển thị đầy đủ: mô tả, vai trò, khách hàng, công nghệ, liên kết mã nguồn "
         "và demo, có nền tối phủ toàn màn hình."),
    ]),
    ("Học vấn, kỹ năng, công bố và sự kiện", [
        ("04_home_education.png", "Khu vực Học vấn — thẻ trường học, bậc học và thời gian đào tạo", ""),
        ("05_home_skills.png", "Khu vực Kỹ năng — thanh biểu diễn mức độ thành thạo theo nhóm", ""),
        ("06_home_publications.png", "Khu vực Công bố khoa học — nền tối tương phản cao", ""),
        ("07_home_events.png", "Khu vực Sự kiện — giải thưởng, hội thảo và chứng chỉ", ""),
        ("08_home_footer.png", "Chân trang trang chủ — thông tin liên hệ và bản quyền", ""),
    ]),
    ("Trang đăng nhập", [
        ("10_login.png", "Trang đăng nhập PITECH LAB",
         "Form gồm hai trường tài khoản và mật khẩu, nút đăng nhập và liên kết hỗ trợ."),
    ]),
    ("Giao diện quản trị viên", [
        ("11_admin_chat_inbox.png",
         "Hộp thư của quản trị viên — danh sách hội thoại và khung trò chuyện",
         "Chat dùng STOMP qua SockJS. Khách gửi tin từ widget góc phải trang chủ; quản trị "
         "viên nhận tin trong hộp thư, có bộ đếm tin chưa đọc và gọi video WebRTC."),
        ("12_admin_profile_list.png", "Danh sách hồ sơ nhân sự dạng thẻ, có phân trang",
         "Dữ liệu lấy từ `GET /api/v1/admin/list` với tham số page/size, mặc định 6 bản ghi."),
        ("13_admin_profile_edit.png", "Màn hình chỉnh sửa hồ sơ — thông tin cá nhân, liên hệ và phân bổ tổ chức", ""),
        ("14_admin_account.png", "Quản lý tài khoản — cấp tài khoản cho hồ sơ và kiểm tra trạng thái", ""),
        ("15_admin_organization.png", "Quản lý cây tổ chức — Vùng, Chi nhánh và Phòng ban",
         "Ba cấp độ độc lập: Vùng → Chi nhánh → Phòng ban, quyết định đường dẫn chia sẻ hồ sơ."),
        ("16_admin_projects.png", "Quản lý dự án — thêm, sửa, xóa và tải ảnh lên", ""),
        ("17_admin_skills.png", "Quản lý kỹ năng theo nhóm và mức độ thành thạo", ""),
        ("18_admin_experience.png", "Quản lý kinh nghiệm làm việc", ""),
        ("19_admin_education.png", "Quản lý học vấn", ""),
        ("20_admin_publications.png", "Quản lý công bố khoa học", ""),
        ("21_admin_events.png", "Quản lý sự kiện, giải thưởng và chứng chỉ", ""),
        ("22_admin_cv_import.png", "Nhập CV từ tệp — nạp dữ liệu hồ sơ từ CV đã có", ""),
    ]),
    ("Giao diện người dùng nội bộ", [
        ("23_user_dashboard.png", "Bảng điều khiển người dùng — thông tin tài khoản và lựa chọn nhanh", ""),
        ("24_user_projects.png", "Tự quản lý danh sách dự án của bản thân", ""),
        ("25_user_skills.png", "Tự cập nhật kỹ năng và mức độ thành thạo", ""),
        ("26_user_experience.png", "Tự cập nhật kinh nghiệm làm việc", ""),
        ("27_user_education.png", "Tự cập nhật thông tin học vấn", ""),
        ("28_user_publications.png", "Tự cập nhật danh mục công bố", ""),
        ("29_user_events.png", "Tự cập nhật sự kiện và giải thưởng", ""),
        ("30_user_password.png", "Đổi mật khẩu — yêu cầu nhập mật khẩu cũ để xác nhận", ""),
    ]),
]


def main():
    parts = [
        "# 6. Báo cáo giao diện và nghiệm thu hệ thống",
        "",
        "> Ảnh chụp trực tiếp từ môi trường chạy thật (Vite dev server + mock backend), "
        "kích thước 1600×1000 px, mật độ 2×.",
        "",
    ]
    n = 0
    for title, items in SECTIONS:
        n += 1
        parts += [f"## 6.{n}. {title}", ""]
        for f, cap, desc in items:
            parts.append(fig(f, cap, desc))
    parts += [
        "## 6.9. Danh mục hình ảnh",
        "",
        "| Ký hiệu | Nội dung | Tệp ảnh |",
        "|---|---|---|",
    ]
    for i, (title, items) in enumerate(SECTIONS):
        for f, cap, _ in items:
            pass
    # dựng lại danh sách theo đúng thứ tự đã sinh
    idx = 1
    for title, items in SECTIONS:
        for f, cap, _ in items:
            parts.append(f"| Hình {idx} | {cap} | `{f}` |")
            idx += 1
    parts.append("")
    OUT_MD.write_text("\n".join(parts), encoding="utf-8")
    print("✓ Đã tạo:", OUT_MD.name, f"({FIG} hình)")


if __name__ == "__main__":
    main()
