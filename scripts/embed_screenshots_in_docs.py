#!/usr/bin/env python3
"""
Chèn ảnh giao diện vào các tài liệu Markdown trong docs/.

Mục đích: bổ sung "hình minh hoạ" cho tài liệu hướng dẫn và đặc tả, để người
đọc có thể đối chiếu trực quan với mô tả màn hình.

Cách dùng:
    python3 scripts/embed_screenshots_in_docs.py
"""
import re
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
DOCS = REPO / "docs"
SHOTS = "assets/screenshots"

# (file tài liệu, marker đặt ảnh, ảnh, tiêu đề, mô tả)
INJECTIONS = [
    # ------------------------------------------------ 01 Tổng quan
    ("01-TONG-QUAN-HET-THONG.md", "<!--SHOT:home-hero-->", "01_home_hero.png",
     "Trang chủ công khai của hồ sơ năng lực",
     "Bố cục trang chủ: vùng Hero chiếm một màn hình đầy đủ với nền cảnh 3D "
     "(three.js), khối thông tin cá nhân và dải thẻ thống kê. Bên dưới lần lượt là "
     "các section Kinh nghiệm, Dự án, Học vấn, Kỹ năng, Công bố, Sự kiện và Chân trang."),
    ("01-TONG-QUAN-HET-THONG.md", "<!--SHOT:admin-->", "11_admin_chat_inbox.png",
     "Bảng điều khiển quản trị — màn hình hộp thư chat",
     "Khung bên trái là 12 nhóm chức năng quản trị, khung bên phải hiển thị nội dung "
     "theo tab đang chọn (mặc định là Chat). Đây là nơi quản trị viên trả lời tin nhắn "
     "và tiếp nhận cuộc gọi video của khách truy cập."),
    ("01-TONG-QUAN-HET-THONG.md", "<!--SHOT:user-->", "23_user_dashboard.png",
     "Bảng điều khiển người dùng — trang tự quản lý hồ sơ",
     "Mỗi nhân sự có vùng quản lý riêng gồm 9 tab: hồ sơ, dự án, kỹ năng, kinh nghiệm, "
     "học vấn, công bố, sự kiện, đổi mật khẩu và đăng xuất."),

    # ------------------------------------------------ 02 Đặc tả chức năng
    ("02-DAC-TA-CHUC-NANG.md", "<!--SHOT:projects-->", "03_home_projects.png",
     "Section Dự án trên trang công khai",
     "Lưới thẻ dự án hiển thị ảnh đại diện, tên, mô tả rút gọn và danh sách công nghệ. "
     "Nhấn vào thẻ sẽ mở modal chi tiết."),
    ("02-DAC-TA-CHUC-NANG.md", "<!--SHOT:project-modal-->", "09_home_project_modal.png",
     "Modal chi tiết dự án",
     "Modal hiển thị đầy đủ mô tả, vai trò đảm nhiệm, khách hàng, công nghệ sử dụng và "
     "liên kết tới mã nguồn / bản demo. Đóng bằng phím Esc hoặc nút ×."),
    ("02-DAC-TA-CHUC-NANG.md", "<!--SHOT:login-->", "10_login.png",
     "Trang đăng nhập",
     "Form gồm tài khoản và mật khẩu. Phản hồi thành công lưu token/role/profileId vào "
     "localStorage rồi chuyển hướng theo vai trò (ADMIN → /admin, USER → /user)."),
    ("02-DAC-TA-CHUC-NANG.md", "<!--SHOT:admin-profile-list-->", "12_admin_profile_list.png",
     "Tab Profile List — danh sách hồ sơ nhân sự",
     "Quản trị viên công khai (Public) hoặc xóa (Del) hồ sơ; dữ liệu phân trang với "
     "tham số page/size, mặc định 6 bản ghi mỗi trang."),
    ("02-DAC-TA-CHUC-NANG.md", "<!--SHOT:admin-org-->", "15_admin_organization.png",
     "Tab Organization — cây tổ chức ba cấp",
     "Quản lý độc lập ba cấp: Vùng → Chi nhánh → Phòng ban. Khi gán hồ sơ vào phòng ban, "
     "ứng dụng sinh tự động đường dẫn chia sẻ theo mã vùng/mã chi nhánh/mã phòng ban."),
    ("02-DAC-TA-CHUC-NANG.md", "<!--SHOT:user-projects-->", "24_user_projects.png",
     "Tab Projects trong trang người dùng",
     "Nhân sự tự thêm, sửa, xóa dự án của mình mà không cần quản trị viên can thiệp."),

    # ------------------------------------------------ 03 Hướng dẫn
    ("03-HUONG-DAN-CAI-DAT-VA-SU-DUNG.md", "<!--SHOT:login-->", "10_login.png",
     "Trang đăng nhập — bước đăng nhập đầu tiên",
     "Mở `/login`, nhập tài khoản được cấp ở tab `account` của quản trị viên. "
     "Hệ thống tự chuyển hướng theo vai trò."),
    ("03-HUONG-DAN-CAI-DAT-VA-SU-DUNG.md", "<!--SHOT:admin-profile-list-->", "12_admin_profile_list.png",
     "Bảng điều khiển quản trị — bước kiểm tra danh sách hồ sơ",
     "Sau khi đăng nhập bằng tài khoản ADMIN, bạn sẽ thấy bảng điều khiển này. "
     "Danh sách hồ sơ nằm ở tab `profile-list`."),
    ("03-HUONG-DAN-CAI-DAT-VA-SU-DUNG.md", "<!--SHOT:admin-org-->", "15_admin_organization.png",
     "Gán tổ chức và lấy link chia sẻ",
     "Tại tab `organization`, chọn Phòng ban cho hồ sơ rồi bấm nút copy để lấy đường dẫn "
     "chia sẻ dạng `/#/view/{mã vùng}/{mã chi nhánh}/{mã phòng ban}/{profileId}`."),
    ("03-HUONG-DAN-CAI-DAT-VA-SU-DUNG.md", "<!--SHOT:admin-chat-->", "11_admin_chat_inbox.png",
     "Trả lời tin nhắn của khách truy cập",
     "Khách gửi tin từ widget chat góc phải trang chủ. Tin hiển thị ở đây kèm bộ đếm "
     "tin chưa đọc; nút camera cho phép gọi video WebRTC trực tiếp."),
    ("03-HUONG-DAN-CAI-DAT-VA-SU-DUNG.md", "<!--SHOT:user-password-->", "30_user_password.png",
     "Đổi mật khẩu ở trang người dùng",
     "Tab `change-password` yêu cầu nhập mật khẩu hiện tại trước khi đặt mật khẩu mới."),
    ("03-HUONG-DAN-CAI-DAT-VA-SU-DUNG.md", "<!--SHOT:home-footer-->", "08_home_footer.png",
     "Chân trang trang chủ — nơi đặt thông tin liên hệ",
     "Chân trang chứa thông tin liên hệ (email, GitHub, LinkedIn) và nút tải CV."),

    # ------------------------------------------------ 04 Kiểm tra & bàn giao
    ("04-KIEM-TRA-VA-BAN-GIAO.md", "<!--SHOT:admin-profile-list-->", "12_admin_profile_list.png",
     "Hiện thực chức năng công khai / xóa hồ sơ",
     "Kiểm chứng mục A-05: nút Public trong tab `profile-list` đưa hồ sơ sang trạng "
     "thái công khai, nút Del xóa hồ sơ kèm hộp thoại xác nhận."),
    ("04-KIEM-TRA-VA-BAN-GIAO.md", "<!--SHOT:user-projects-->", "24_user_projects.png",
     "Hiện thực chức năng người dùng tự quản lý dự án",
     "Kiểm chứng mục U-03: thêm / sửa / xóa dự án trong tab `projects` của trang `/user`."),

    # ------------------------------------------------ 05 Phụ lục kỹ thuật
    ("05-PHU-LUC-KY-THUAT.md", "<!--SHOT:home-hero-->", "01_home_hero.png",
     "Giao diện trang công khai — tham chiếu cho mô hình dữ liệu",
     "Dữ liệu hiển thị trên trang này ánh xạ trực tiếp từ payload `GET /api/v1/portfolio` "
     "qua hàm `mapBackendToFrontend` trong `services/api.ts`."),
]


def inject():
    changed = []
    for doc_name, marker, img, title, desc in INJECTIONS:
        path = DOCS / doc_name
        if not path.exists():
            print("  !! không có tài liệu:", doc_name)
            continue
        text = path.read_text(encoding="utf-8")
        if marker not in text:
            print(f"  – marker {marker} không có trong {doc_name} (bỏ qua)")
            continue
        if f"<!--SHOT-DONE:{marker}" in text:
            continue

        block = (
            f"\n<!--SHOT-DONE:{marker}-->\n"
            f"![{title}](../{SHOTS}/{img})\n\n"
            f"**{title}**\n\n"
            f"> {desc}\n"
        )
        text = text.replace(marker, block, 1)
        path.write_text(text, encoding="utf-8")
        changed.append(f"{doc_name} ← {img}")
    for c in changed:
        print("  ✓", c)
    print(f"\nĐã chèn {len(changed)} ảnh vào {len(set(c.split(' ← ')[0] for c in changed))} tài liệu.")


if __name__ == "__main__":
    inject()
