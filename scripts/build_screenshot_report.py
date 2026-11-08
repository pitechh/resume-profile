#!/usr/bin/env python3
"""
Sinh báo cáo Word (.docx) cho dự án PITECH LAB Dynamic Portfolio,
đính kèm toàn bộ ảnh giao diện đã chụp.

Cấu trúc:
  Phần A — Trang bìa
  Phần B — Mục lục
  Phần C — Tổng quan hệ thống
  Phần D — Giao diện người dùng (ảnh chụp)
  Phần E — Giao diện quản trị
  Phần F — Giao diện người dùng nội bộ (self-service)
  Phần G — Kết luận

Cách dùng:
    python3 scripts/build_screenshot_report.py
"""
import re
import subprocess
from pathlib import Path

from docx import Document
from docx.enum.section import WD_SECTION
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_BREAK
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Cm, Pt, RGBColor

ROOT = Path(__file__).resolve().parent.parent
SHOTS = ROOT / "assets" / "screenshots"
OUT_DOCX = ROOT / "Bao-cao-giao-dien-PITECHLAB-Dynamic-Portfolio.docx"

ACCENT = RGBColor(0x1F, 0x3B, 0x73)
ORANGE = RGBColor(0xEA, 0x58, 0x0C)
GREY = RGBColor(0x55, 0x5F, 0x6D)

FIG_NO = 0
TOC_ENTRIES: list[tuple[str, int]] = []


# ----------------------------------------------------------------- helpers
def set_cell_bg(cell, hex_color):
    tcPr = cell._tc.get_or_add_tcPr()
    shd = OxmlElement("w:shd")
    shd.set(qn("w:val"), "clear")
    shd.set(qn("w:color"), "auto")
    shd.set(qn("w:fill"), hex_color)
    tcPr.append(shd)


def set_repeat_header(row):
    trPr = row._tr.get_or_add_trPr()
    el = OxmlElement("w:tblHeader")
    el.set(qn("w:val"), "true")
    trPr.append(el)


def add_page_number_footer(section):
    footer = section.footer
    p = footer.paragraphs[0]
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER

    def field(instr, size=9):
        """w:fldSimple phải là con trực tiếp của w:p (không bọc trong w:r)."""
        fld = OxmlElement("w:fldSimple")
        fld.set(qn("w:instr"), instr)
        r = OxmlElement("w:r")
        rPr = OxmlElement("w:rPr")
        sz = OxmlElement("w:sz")
        sz.set(qn("w:val"), str(size * 2))
        color = OxmlElement("w:color")
        color.set(qn("w:val"), "555F6D")
        rPr.append(sz)
        rPr.append(color)
        t = OxmlElement("w:t")
        t.text = "1"
        r.append(rPr)
        r.append(t)
        fld.append(r)
        return fld

    p._p.append(field("PAGE"))
    sep = p.add_run(" / ")
    sep.font.size = Pt(9)
    sep.font.color.rgb = GREY
    p._p.append(field("NUMPAGES"))


def style_document(doc):
    st = doc.styles["Normal"]
    st.font.name = "Times New Roman"
    st.font.size = Pt(12)
    st.element.rPr.rFonts.set(qn("w:eastAsia"), "Times New Roman")
    pf = st.paragraph_format
    pf.line_spacing = 1.4
    pf.space_after = Pt(6)

    for name, size, color, bold in (
        ("Heading 1", 18, ACCENT, True),
        ("Heading 2", 15, ACCENT, True),
        ("Heading 3", 13, ORANGE, True),
    ):
        s = doc.styles[name]
        s.font.name = "Times New Roman"
        s.font.size = Pt(size)
        s.font.color.rgb = color
        s.font.bold = bold
        s.paragraph_format.space_before = Pt(14)
        s.paragraph_format.space_after = Pt(8)
        s.paragraph_format.keep_with_next = True


def heading(doc, text, level=1, toc=True):
    h = doc.add_heading(text, level=level)
    if toc:
        TOC_ENTRIES.append((text, level))
    return h


def measure_pages(docx_path: Path, titles: list[str]) -> dict:
    """Đo số trang thật của từng tiêu đề bằng cách chuyển sang PDF rồi trích text."""
    import subprocess
    import tempfile

    with tempfile.TemporaryDirectory() as td:
        subprocess.run(
            ["soffice", "--headless", "--convert-to", "pdf", str(docx_path),
             "--outdir", td],
            capture_output=True, timeout=600,
        )
        pdfs = list(Path(td).glob("*.pdf"))
        if not pdfs:
            return {}
        txt = subprocess.run(
            ["pdftotext", "-layout", str(pdfs[0]), "-"],
            capture_output=True, text=True,
        ).stdout
        pages = txt.split("\f")

    # trang bìa + trang mục lục không chứa nội dung thật
    body_start = 0
    for i, p in enumerate(pages):
        if "MỤC LỤC" in re.sub(r"\s+", " ", p):
            body_start = i + 1
            break
    mapping = {}
    for title in titles:
        needle = re.sub(r"\s+", " ", title).strip()
        for i in range(body_start, len(pages)):
            flat = re.sub(r"\s+", " ", pages[i])
            if needle in flat:
                mapping[title] = i + 1
                break
    return mapping


def para(doc, text, italic=False, size=12, align=None, bold=False, color=None):
    p = doc.add_paragraph()
    r = p.add_run(text)
    r.font.size = Pt(size)
    r.italic = italic
    r.bold = bold
    if color:
        r.font.color.rgb = color
    if align:
        p.alignment = align
    p.alignment = align or WD_ALIGN_PARAGRAPH.JUSTIFY
    return p


def bullet(doc, text, level=0):
    p = doc.add_paragraph(style="List Bullet")
    p.paragraph_format.left_indent = Cm(0.8 + 0.6 * level)
    r = p.add_run(text)
    r.font.size = Pt(11.5)
    return p


def add_figure(doc, filename, caption, description=None, width_cm=16.0, max_h_cm=13.5):
    """Chèn ảnh + chú thích Hình N.M trong ô bảng không viền (giữ luôn cùng trang)."""
    global FIG_NO
    path = SHOTS / filename
    if not path.exists():
        print("  !! thiếu ảnh:", filename)
        return
    FIG_NO += 1

    # co ảnh vừa cả chiều rộng lẫn chiều cao tối đa
    from PIL import Image
    with Image.open(path) as im:
        iw, ih = im.size
    w = width_cm
    h = w * ih / iw
    if h > max_h_cm:
        h = max_h_cm
        w = h * iw / ih

    tbl = doc.add_table(rows=1, cols=1)
    tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
    # bỏ viền
    tblPr = tbl._tbl.tblPr
    borders = OxmlElement("w:tblBorders")
    for edge in ("top", "left", "bottom", "right", "insideH", "insideV"):
        el = OxmlElement(f"w:{edge}")
        el.set(qn("w:val"), "none")
        el.set(qn("w:sz"), "0")
        borders.append(el)
    tblPr.append(borders)

    cell = tbl.cell(0, 0)
    cell.width = Cm(16.5)

    # ảnh
    p = cell.paragraphs[0]
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_after = Pt(4)
    p.add_run().add_picture(str(path), width=Cm(w), height=Cm(h))

    # chú thích
    cap = cell.add_paragraph()
    cap.alignment = WD_ALIGN_PARAGRAPH.CENTER
    cap.paragraph_format.space_after = Pt(4 if description else Pt(0))
    r = cap.add_run(f"Hình {FIG_NO}. {caption}")
    r.font.size = Pt(10.5)
    r.bold = True
    r.font.color.rgb = ACCENT

    # mô tả
    if description:
        d = cell.add_paragraph()
        d.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
        d.paragraph_format.left_indent = Cm(0.4)
        rd = d.add_run(description)
        rd.font.size = Pt(10.5)
        rd.font.color.rgb = GREY

    doc.add_paragraph().paragraph_format.space_after = Pt(4)

    FIG_LIST.append((filename, caption))


def add_table(doc, headers, rows, widths=None):
    t = doc.add_table(rows=1, cols=len(headers))
    t.style = "Table Grid"
    t.alignment = WD_TABLE_ALIGNMENT.CENTER
    hdr = t.rows[0]
    set_repeat_header(hdr)
    for i, h in enumerate(headers):
        c = hdr.cells[i]
        c.text = ""
        p = c.paragraphs[0]
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        r = p.add_run(h)
        r.bold = True
        r.font.size = Pt(10)
        r.font.color.rgb = RGBColor(0xFF, 0xFF, 0xFF)
        set_cell_bg(c, "1F3B73")
    for row in rows:
        cells = t.add_row().cells
        for i, v in enumerate(row):
            cells[i].text = ""
            p = cells[i].paragraphs[0]
            r = p.add_run(str(v))
            r.font.size = Pt(10)
    if widths:
        for row in t.rows:
            for i, w in enumerate(widths):
                row.cells[i].width = Cm(w)
    doc.add_paragraph().paragraph_format.space_after = Pt(2)
    return t


def page_break(doc):
    doc.add_paragraph().add_run().add_break(WD_BREAK.PAGE)


# ----------------------------------------------------------------- cover
def build_cover(doc):
    for _ in range(3):
        doc.add_paragraph()
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r = p.add_run("BÁO CÁO KỸ THUẬT")
    r.font.size = Pt(26)
    r.bold = True
    r.font.color.rgb = ACCENT

    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r = p.add_run("GIAO DIỆN NGƯỜI DÙNG")
    r.font.size = Pt(18)
    r.bold = True
    r.font.color.rgb = ORANGE

    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r = p.add_run("VÀ NGHIỆM THU HỆ THỐNG")
    r.font.size = Pt(18)
    r.bold = True
    r.font.color.rgb = ORANGE

    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_before = Pt(6)
    r = p.add_run("PITECH LAB — Dynamic Portfolio Platform")
    r.font.size = Pt(16)
    r.font.color.rgb = ACCENT

    doc.add_paragraph()
    doc.add_paragraph()
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r = p.add_run("Hệ thống hồ sơ năng lực số cho tổ chức")
    r.font.size = Pt(13)
    r.italic = True
    r.font.color.rgb = GREY

    for _ in range(6):
        doc.add_paragraph()

    table = doc.add_table(rows=5, cols=2)
    table.style = "Table Grid"
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    info = [
        ("Người thực hiện", "Phạm Minh Đào"),
        ("Mã số sinh viên", "22810310271"),
        ("Lớp", "CNTT 14.1"),
        ("Trường", "Trường Đại học Điện lực"),
        ("Năm thực hiện", "2026"),
    ]
    for i, (k, v) in enumerate(info):
        for j, val in enumerate((k, v)):
            c = table.cell(i, j)
            c.text = ""
            p = c.paragraphs[0]
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER if j == 0 else WD_ALIGN_PARAGRAPH.LEFT
            r = p.add_run(val)
            r.font.size = Pt(12)
            r.bold = (j == 0)
            if j == 0:
                set_cell_bg(c, "EEF2F9")
        table.cell(i, 0).width = Cm(5)
        table.cell(i, 1).width = Cm(10)
    page_break(doc)


def build_toc(doc, entries=None):
    """Mục lục tay (bảng 2 cột) — số trang được điền ở pass 2."""
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r = p.add_run("MỤC LỤC")
    r.font.size = Pt(18)
    r.bold = True
    r.font.color.rgb = ACCENT
    doc.add_paragraph()

    entries = entries or []
    t = doc.add_table(rows=0, cols=2)
    t.style = "Table Grid"
    t.alignment = WD_TABLE_ALIGNMENT.CENTER
    for title, level, page in entries:
        row = t.add_row()
        c0, c1 = row.cells
        c0.text = ""
        p0 = c0.paragraphs[0]
        p0.paragraph_format.space_after = Pt(1)
        p0.paragraph_format.space_before = Pt(1)
        r0 = p0.add_run(("    " * (level - 1)) + title)
        r0.font.size = Pt(11)
        r0.bold = (level == 1)

        c1.text = ""
        p1 = c1.paragraphs[0]
        p1.alignment = WD_ALIGN_PARAGRAPH.RIGHT
        p1.paragraph_format.space_after = Pt(1)
        p1.paragraph_format.space_before = Pt(1)
        r1 = p1.add_run(str(page) if page else "—")
        r1.font.size = Pt(11)
        r1.bold = (level == 1)
        c0.width = Cm(14.5)
        c1.width = Cm(2.0)
    page_break(doc)


# ----------------------------------------------------------------- main
def build_document(toc_entries):
    """Sinh toàn bộ nội dung tài liệu. toc_entries = [(title, level, page)]"""
    global FIG_NO, FIG_LIST
    FIG_NO = 0
    FIG_LIST = []
    TOC_ENTRIES.clear()

    doc = Document()
    style_document(doc)

    sec = doc.sections[0]
    sec.page_width = Cm(21.0)
    sec.page_height = Cm(29.7)
    sec.top_margin = Cm(2.2)
    sec.bottom_margin = Cm(2.0)
    sec.left_margin = Cm(2.8)
    sec.right_margin = Cm(2.2)
    add_page_number_footer(sec)

    # ---------------- A. TRANG BÌA
    build_cover(doc)

    # ---------------- B. MỤC LỤC
    build_toc(doc, toc_entries)

    # ---------------- C. TỔNG QUAN
    heading(doc, "1. Tổng quan hệ thống", 1)
    para(doc,
         "PITECH LAB Dynamic Portfolio là nền tảng trình bày hồ sơ năng lực số cho tổ chức, "
         "cho phép mỗi nhân sự có một trang hồ sơ riêng với đa ngôn ngữ, xuất CV ra PDF và "
         "tương tác trực tiếp với quản trị viên. Hệ thống được xây dựng theo kiến trúc "
         "Single-Page Application ba tầng, tách biệt rõ ràng giữa tầng giao diện, tầng "
         "nghiệp vụ và tầng dữ liệu.")

    heading(doc, "1.1. Công nghệ sử dụng", 2)
    add_table(doc,
              ["Thành phần", "Công nghệ", "Phiên bản", "Vai trò"],
              [
                  ["Frontend", "React", "19.2.3", "Thư viện giao diện khai báo"],
                  ["Build tool", "Vite", "6.2.0", "Dev server & bundling ESM"],
                  ["Ngôn ngữ", "TypeScript", "5.8.2", "Kiểu dữ liệu tĩnh"],
                  ["Định tuyến", "react-router-dom", "7.11.0", "HashRouter, route bảo vệ"],
                  ["CSS", "Tailwind CSS", "CDN runtime", "Utility-first styling"],
                  ["Animation", "Framer Motion", "12.23.26", "Chuyển động giao diện"],
                  ["3D", "three.js / @react-three/fiber", "—", "Nền cảnh 3D trang chủ"],
                  ["Realtime", "@stomp/stompjs + sockjs-client", "—", "Chat và tín hiệu gọi video"],
                  ["Video", "WebRTC (native)", "—", "Gọi video peer-to-peer"],
                  ["In ấn", "react-to-print", "—", "Xuất CV theo mẫu A4"],
              ],
              widths=[3.0, 4.6, 2.6, 5.8])

    heading(doc, "1.2. Ba vai trò người dùng", 2)
    add_table(doc,
              ["Vai trò", "Đường dẫn", "Quyền hạn", "Giao diện"],
              [
                  ["Khách (Visitor)", "/", "Xem hồ sơ công khai, in CV, chat với quản trị viên", "Trang portfolio"],
                  ["Quản trị viên (Admin)", "/admin", "Quản lý hồ sơ, tài khoản, cây tổ chức, tin nhắn", "Bảng điều khiển 12 tab"],
                  ["Người dùng (User)", "/user", "Tự cập nhật hồ sơ, dự án, kỹ năng, đổi mật khẩu", "Bảng tự quản lý 9 tab"],
              ],
              widths=[3.4, 2.4, 6.4, 3.8])

    heading(doc, "1.3. Luồng xác thực", 2)
    para(doc,
         "Trang đăng nhập gửi yêu cầu POST /api/v1/auth/login. Phản hồi thành công trả về "
         "token, vai trò (role) và mã hồ sơ (profileId). Client lưu các giá trị này vào "
         "localStorage rồi chuyển hướng theo vai trò. Route /admin và /user được bọc trong "
         "ProtectedRoute — nếu không có token trong localStorage, ứng dụng tự chuyển về "
         "/login. Việc kiểm tra quyền thực tế vẫn phải do backend thực hiện.")

    # ---------------- D. GIAO DIỆN KHÁCH
    page_break(doc)
    heading(doc, "2. Giao diện trang công khai (khách truy cập)", 1)
    para(doc,
         "Trang chủ là điểm vào chính của hệ thống. Bố cục chia làm tám khu vực theo trục "
         "dọc: hero, kinh nghiệm, dự án, học vấn, kỹ năng, công bố, sự kiện và chân trang. "
         "Nền cảnh 3D (three.js) phủ toàn bộ vùng hero và chuyển động theo con trỏ chuột.")

    heading(doc, "2.1. Vùng Hero và thống kê", 2)
    add_figure(doc, "01_home_hero.png",
               "Trang chủ PITECH LAB — vùng Hero với nền cảnh 3D, thông tin cá nhân và thẻ thống kê",
               "Vùng hero chiếm một màn hình đầy đủ (min-h-screen). Bên trái là ảnh đại diện "
               "bo tròn kèm huy hiệu trạng thái, bên phải là khối thông tin tên, chức danh "
               "tiếng Việt/Anh và mô tả ngắn. Dải thẻ thống kê (số năm kinh nghiệm, số dự án, "
               "số kỹ năng, số công bố) đóng vai trò bảng tóm tắt nhanh cho người xem.")

    heading(doc, "2.2. Kinh nghiệm làm việc", 2)
    add_figure(doc, "02_home_experience.png",
               "Khu vực Kinh nghiệm làm việc hiển thị dạng dòng thời gian (timeline)",
               "Mỗi mục kinh nghiệm hiển thị tên công ty, vị trí, khoảng thời gian và mô tả "
               "công việc. Mục đang làm việc được đánh dấu bằng nhãn màu cam nổi bật. "
               "Đây là phần có giá trị cao nhất đối với bộ phận tuyển dụng.")

    heading(doc, "2.3. Dự án và cửa sổ chi tiết", 2)
    add_figure(doc, "03_home_projects.png",
               "Lưới thẻ dự án kèm công nghệ sử dụng",
               "Mỗi thẻ dự án gồm ảnh đại diện, tên dự án, mô tả ngắn, danh sách công nghệ "
               "và các liên kết tới mã nguồn/demo. Thẻ có hiệu ứng nâng lên khi rê chuột.")
    add_figure(doc, "09_home_project_modal.png",
               "Cửa sổ modal chi tiết dự án",
               "Nhấn vào thẻ dự án sẽ mở modal hiển thị đầy đủ: mô tả chi tiết, vai trò đảm nhiệm, "
               "khách hàng, công nghệ, liên kết mã nguồn và demo. Modal có nền tối phủ toàn màn hình.")

    heading(doc, "2.4. Học vấn, kỹ năng và công bố khoa học", 2)
    add_figure(doc, "04_home_education.png",
               "Khu vực Học vấn — thẻ trường học, bậc học và thời gian đào tạo")
    add_figure(doc, "05_home_skills.png",
               "Khu vực Kỹ năng — thanh biểu diễn mức độ thành thạo theo nhóm")
    add_figure(doc, "06_home_publications.png",
               "Khu vực Công bố khoa học — nền tối tương phản cao")
    add_figure(doc, "07_home_events.png",
               "Khu vực Sự kiện — giải thưởng, hội thảo và chứng chỉ")

    heading(doc, "2.5. Chân trang và liên hệ", 2)
    add_figure(doc, "08_home_footer.png",
               "Chân trang trang chủ — thông tin liên hệ và bản quyền")

    # ---------------- E. LOGIN
    page_break(doc)
    heading(doc, "3. Giao diện đăng nhập", 1)
    add_figure(doc, "10_login.png",
               "Trang đăng nhập PITECH LAB",
               "Form đăng nhập gồm hai trường tài khoản và mật khẩu, nút đăng nhập và liên kết "
               "hỗ trợ. Trang dùng nền gradient cùng hiệu ứng chuyển động nhẹ, tách biệt rõ "
               "với phần nội dung bên trong hệ thống.")

    # ---------------- F. ADMIN
    page_break(doc)
    heading(doc, "4. Giao diện quản trị viên", 1)
    para(doc,
         "Bảng điều khiển quản trị gồm thanh điều hướng bên trái với 12 mục và vùng nội dung "
         "bên phải. Mục Chat được chọn mặc định khi vào trang. Các mục còn lại bao gồm quản lý "
         "hồ sơ, quản lý tài khoản, cây tổ chức ba cấp (Vùng – Chi nhánh – Phòng ban), cùng "
         "các CRUD cho dự án, kỹ năng, kinh nghiệm, học vấn, công bố, sự kiện và nhập CV.")

    heading(doc, "4.1. Hộp thư và chat trực tiếp", 2)
    add_figure(doc, "11_admin_chat_inbox.png",
               "Hộp thư của quản trị viên — danh sách hội thoại và khung trò chuyện",
               "Chat dùng giao thức STOMP qua SockJS. Khách truy cập gửi tin nhắn từ widget "
               "góc phải trang chủ; quản trị viên nhận tin trong hộp thư, có bộ đếm tin nhắn "
               "chưa đọc và hỗ trợ gọi video WebRTC trực tiếp từ khung chat.")

    heading(doc, "4.2. Danh sách hồ sơ", 2)
    add_figure(doc, "12_admin_profile_list.png",
               "Danh sách hồ sơ nhân sự dạng thẻ, có phân trang",
               "Quản trị viên duyệt kích hoạt hồ sơ, xem trước hoặc xóa. Dữ liệu lấy từ "
               "GET /api/v1/admin/list với tham số page/size, mặc định 6 bản ghi mỗi trang.")

    heading(doc, "4.3. Chỉnh sửa hồ sơ", 2)
    add_figure(doc, "13_admin_profile_edit.png",
               "Màn hình chỉnh sửa hồ sơ — thông tin cá nhân, liên hệ và phân bổ tổ chức")
    heading(doc, "4.4. Quản lý tài khoản", 2)
    add_figure(doc, "14_admin_account.png",
               "Quản lý tài khoản — cấp tài khoản cho hồ sơ và kiểm tra trạng thái")
    heading(doc, "4.5. Cây tổ chức ba cấp", 2)
    add_figure(doc, "15_admin_organization.png",
               "Quản lý cây tổ chức — Vùng, Chi nhánh và Phòng ban",
               "Ba cấp độ được quản lý độc lập: Vùng (Miền Bắc/Trung/Nam), Chi nhánh thuộc "
               "vùng, Phòng ban thuộc chi nhánh. Cấu trúc này quyết định đường dẫn chia sẻ "
               "hồ sơ theo mã vùng/mã chi nhánh/mã phòng ban.")
    heading(doc, "4.6. Các mục quản lý nội dung", 2)
    add_figure(doc, "16_admin_projects.png", "Quản lý dự án — thêm, sửa, xóa và tải ảnh lên")
    add_figure(doc, "17_admin_skills.png", "Quản lý kỹ năng theo nhóm và mức độ thành thạo")
    add_figure(doc, "18_admin_experience.png", "Quản lý kinh nghiệm làm việc")
    add_figure(doc, "19_admin_education.png", "Quản lý học vấn")
    add_figure(doc, "20_admin_publications.png", "Quản lý công bố khoa học")
    add_figure(doc, "21_admin_events.png", "Quản lý sự kiện, giải thưởng và chứng chỉ")
    add_figure(doc, "22_admin_cv_import.png",
               "Nhập CV từ tệp — nạp dữ liệu hồ sơ từ CV đã có")

    # ---------------- G. USER
    page_break(doc)
    heading(doc, "5. Giao diện người dùng nội bộ", 1)
    para(doc,
         "Trang người dùng cho phép mỗi nhân sự tự quản lý hồ sơ của mình mà không cần "
         "quản trị viên can thiệp. Bảng điều khiển có 9 mục: hồ sơ, dự án, kỹ năng, kinh "
         "nghiệm, học vấn, công bố, sự kiện, đổi mật khẩu và đăng xuất.")

    add_figure(doc, "23_user_dashboard.png",
               "Bảng điều khiển người dùng — thông tin tài khoản và lựa chọn nhanh")
    add_figure(doc, "24_user_projects.png", "Tự quản lý danh sách dự án của bản thân")
    add_figure(doc, "25_user_skills.png", "Tự cập nhật kỹ năng và mức độ thành thạo")
    add_figure(doc, "26_user_experience.png", "Tự cập nhật kinh nghiệm làm việc")
    add_figure(doc, "27_user_education.png", "Tự cập nhật thông tin học vấn")
    add_figure(doc, "28_user_publications.png", "Tự cập nhật danh mục công bố")
    add_figure(doc, "29_user_events.png", "Tự cập nhật sự kiện và giải thưởng")
    add_figure(doc, "30_user_password.png",
               "Đổi mật khẩu — yêu cầu nhập mật khẩu cũ để xác nhận")

    # ---------------- H. KẾT LUẬN
    page_break(doc)
    heading(doc, "6. Đánh giá giao diện và kết luận", 1)
    heading(doc, "6.1. Điểm mạnh", 2)
    for t in [
        "Bố cục trang công khai rõ ràng theo trục dọc, người xem nắm được toàn bộ thông tin "
        "hồ sơ chỉ bằng một lần cuộn trang.",
        "Thiết kế đáp ứng (responsive) với nền tảng Tailwind CSS, hiển thị tốt trên máy tính, "
        "máy tính bảng và điện thoại.",
        "Bảng điều khiển quản trị phân tách rõ 12 nhóm chức năng, giảm tải việc nhập liệu thủ công.",
        "Trang người dùng cho phép tự phục vụ (self-service), giảm tải đáng kể cho quản trị viên.",
        "Chat trực tiếp và gọi video WebRTC tích hợp ngay trong giao diện quản trị, rút ngắn "
        "thời gian phản hồi với ứng viên.",
        "Mẫu in A4 riêng biệt giúp xuất CV đúng chuẩn in ấn.",
    ]:
        bullet(doc, t)

    heading(doc, "6.2. Hạn chế cần khắc phục", 2)
    add_table(doc,
              ["#", "Hạn chế", "Mức độ", "Khuyến nghị"],
              [
                  ["1", "Tailwind CSS không có trong devDependencies, phụ thuộc CDN cdn.tailwindcss.com "
                        "— giao diện mất hoàn toàn nếu mạng CDN bị chặn", "Nghiêm trọng",
                   "Đưa Tailwind vào pipeline build, biên dịch CSS tại thời điểm build"],
                  ["2", "Chưa có interceptor xử lý 401 tập trung; token hết hạn khiến các request "
                        "thất bại âm thầm", "Cao",
                   "Thêm interceptor response: 401 → xóa localStorage → chuyển về /login"],
                  ["3", "Kiểm tra quyền chỉ dựa trên sự tồn tại của token ở client", "Cao",
                   "Backend phải xác thực chữ ký token và phân quyền theo vai trò"],
                  ["4", "Chỉ cấu hình STUN công cộng, chưa có TURN server — hai bên cùng NAT ngăn chặn "
                        "sẽ không gọi được video", "Trung bình",
                   "Bổ sung TURN server cho môi trường production"],
                  ["5", "Chưa có kiểm thử tự động (unit test / E2E) cho frontend", "Trung bình",
                   "Bổ sung Vitest cho logic và Playwright cho luồng E2E"],
                  ["6", "Ảnh minh hoạ dự án phụ thuộc dịch vụ ảnh ngoài (placehold.co)", "Thấp",
                   "Lưu ảnh vào storage nội bộ và có cơ chế kiểm tra fallback"],
              ],
              widths=[1.0, 6.0, 2.2, 6.0])

    heading(doc, "6.3. Kết luận", 2)
    para(doc,
         "Giao diện PITECH LAB Dynamic Portfolio đã hoàn thành đầy đủ các chức năng cốt lõi: "
         "trình bày hồ sơ công khai, quản trị nội dung theo cây tổ chức ba cấp, tự phục vụ hồ sơ "
         "cho nhân sự, chat trực tiếp và gọi video. Các ảnh chụp trong báo cáo này được thực hiện "
         "trên môi trường chạy thật với dữ liệu mẫu, mô phỏng đầy đủ hành vi của từng vai trò. "
         "Các hạn chế nêu tại mục 6.2 tập trung chủ yếu ở vòn đời triển khai production "
         "(build CSS, xử lý token hết hạn, hạ tầng TURN) và không ảnh hưởng đến tính đúng đắn "
         "của nghiệp vụ đã triển khai.")

    # ---------------- phụ lục danh mục hình
    page_break(doc)
    heading(doc, "Phụ lục. Danh mục hình ảnh", 1, toc=False)
    rows = []
    for i, (f, cap) in enumerate(FIG_LIST, 1):
        rows.append([f"Hình {i}", cap, f])
    add_table(doc, ["Ký hiệu", "Nội dung", "Tệp ảnh"], rows, widths=[2.0, 10.0, 4.5])

    doc.save(str(OUT_DOCX))
    return doc


def main():
    # --- pass 1: sinh bản nháp để đo số trang thật
    TOC_ENTRIES.clear()
    build_document([])
    pagemap = measure_pages(OUT_DOCX, [t for t, _ in TOC_ENTRIES])
    print(f"  Đo được {len(pagemap)}/{len(TOC_ENTRIES)} mục.")

    # --- pass 2: sinh lại với mục lục đầy đủ số trang
    entries = [(t, lv, pagemap.get(t, "")) for t, lv in TOC_ENTRIES]
    build_document(entries)

    print("✓ Đã tạo:", OUT_DOCX.name, f"({FIG_NO} hình)")
    print("  Dung lượng:", round(OUT_DOCX.stat().st_size / 1024 / 1024, 2), "MB")


# danh sách hình để sinh phụ lục
FIG_LIST: list[tuple[str, str]] = []


if __name__ == "__main__":
    main()
