#!/usr/bin/env python3
"""
Build the single Word handover document from the markdown docs.

Steps:
  1. Strip manual heading numbers so pandoc can renumber continuously.
  2. Merge all docs into one markdown file.
  3. Convert to docx with a styled reference document.
  4. Inject a cover page + footer page numbers.
"""
import re
import subprocess
import sys
from pathlib import Path

import docx
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_BREAK
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Cm, Pt, RGBColor

REPO = Path(__file__).resolve().parent.parent
DOCS = REPO / "docs"
OUT = REPO / "Tai-lieu-ban-giao-PITECHLAB-Dynamic-Portfolio.docx"
REF = "/tmp/reference_styled.docx"
MERGED = Path("/tmp/merged.md")

ORDER = [
    "README.md",
    "01-TONG-QUAN-HET-THONG.md",
    "02-DAC-TA-CHUC-NANG.md",
    "03-HUONG-DAN-CAI-DAT-VA-SU-DUNG.md",
    "04-KIEM-TRA-VA-BAN-GIAO.md",
    "05-PHU-LUC-KY-THUAT.md",
    "06-BAO-CAO-GIAO-DIEN.md",
]

HEADING_RE = re.compile(r"^(#{1,6})\s+(.*)$")
NUM_PREFIX_RE = re.compile(r"^\s*\d+(?:\.\d+)*\.?\s+(?!—)")


def strip_manual_numbers(lines):
    out, in_fence = [], False
    for line in lines:
        if line.lstrip().startswith("```"):
            in_fence = not in_fence
            out.append(line)
            continue
        if not in_fence:
            m = HEADING_RE.match(line)
            if m:
                hashes, text = m.group(1), m.group(2)
                line = f"{hashes} {NUM_PREFIX_RE.sub('', text)}"
        out.append(line)
    return out


def build_merged():
    chunks = []
    for name in ORDER:
        path = DOCS / name
        if not path.exists():
            sys.exit(f"missing: {path}")
        lines = strip_manual_numbers(path.read_text(encoding="utf-8").split("\n"))
        if name == "README.md":
            lines = [
                "# Giới thiệu bộ tài liệu" if (HEADING_RE.match(l) and l.startswith("# ")) else l
                for l in lines
            ]
        chunks.append("\n".join(lines))
    merged = "\n\n".join(chunks)
    # đường dẫn ảnh trong docs/ là tương đối so với docs/ → đổi sang tuyệt đối
    # để pandoc (chạy trên /tmp/merged.md) vẫn tìm thấy tệp ảnh.
    merged = merged.replace("(../assets/", f"({REPO}/assets/")
    MERGED.write_text(merged, encoding="utf-8")
    print(f"merged -> {MERGED}")


def run_pandoc():
    cmd = [
        "pandoc",
        "--from", "markdown+pipe_tables+raw_html+tex_math_dollars+implicit_figures",
        "--to", "docx",
        "--reference-doc", REF,
        "--toc", "--toc-depth=3",
        "--number-sections",
        "--highlight-style", "pygments",
        "-o", str(OUT),
        str(MERGED),
    ]
    res = subprocess.run(cmd, capture_output=True, text=True)
    if res.stderr:
        print(res.stderr, file=sys.stderr)
    res.check_returncode()
    print("pandoc done")


NAVY = RGBColor(0x1F, 0x3B, 0x73)
TEAL = RGBColor(0x0B, 0x6B, 0x6B)
GREY = RGBColor(0x55, 0x5B, 0x66)
BODY = "Times New Roman"


def _run(p, text, size, bold=False, color=None, space_after=0, italic=False):
    r = p.add_run(text)
    r.font.name = BODY
    r.font.size = Pt(size)
    r.font.bold = bold
    r.font.italic = italic
    if color is not None:
        r.font.color.rgb = color
    r._element.rPr.rFonts.set(qn("w:eastAsia"), BODY)
    p.paragraph_format.space_after = Pt(space_after)
    return r


def build_cover(doc):
    anchor = doc.element.body[0]
    made = []

    def par(text="", size=11, bold=False, color=None,
            before=0, after=0, italic=False, align=WD_ALIGN_PARAGRAPH.CENTER):
        p = doc.add_paragraph()
        p.alignment = align
        if text:
            _run(p, text, size, bold, color, after, italic)
        p.paragraph_format.space_before = Pt(before)
        p.paragraph_format.space_after = Pt(after)
        made.append(p._p)
        return p

    def rule():
        p = doc.add_paragraph()
        pPr = p._p.get_or_add_pPr()
        bdr = OxmlElement("w:pBdr")
        bottom = OxmlElement("w:bottom")
        bottom.set(qn("w:val"), "single")
        bottom.set(qn("w:sz"), "12")
        bottom.set(qn("w:space"), "1")
        bottom.set(qn("w:color"), "1F3B73")
        bdr.append(bottom)
        pPr.append(bdr)
        p.paragraph_format.space_before = Pt(4)
        p.paragraph_format.space_after = Pt(16)
        made.append(p._p)

    par("HỘI ĐỒNG ĐÀN", 12.5, True, GREY, before=54, after=2)
    par("BÁO CÁO BÀN GIAO HỆ THỐNG", 12.5, True, GREY, after=2)
    par("ĐỒ ÁN THỰC TẬP TỐT NGHIỆP", 12.5, True, GREY, after=30)

    par("PITECH LAB", 14, True, TEAL, after=5)
    par("HỆ THỐNG QUẢN LÝ HỒ SƠ NĂNG LỰC", 23, True, NAVY, after=4)
    par("CV PROFILE PLATFORM", 14, True, TEAL, after=6)
    par("DYNAMIC PORTFOLIO", 14, True, TEAL, after=24)

    par("Tài liệu đặc tả kỹ thuật · Hướng dẫn cài đặt và vận hành", 12,
        False, GREY, italic=True, after=3)
    par("Kèm kiểm tra chất lượng và danh mục bàn giao", 12,
        False, GREY, italic=True, after=20)

    rule()

    par("MÃ NGUỒN", 10, True, GREY, after=2)
    par("github.com/dao24092004/pitechlab-cv-profile", 11.5, True, NAVY, after=2)
    par("Nhánh main  ·  commit 886de4b  ·  24 commit", 10.5, False, GREY, after=14)

    par("CÔNG NGHỆ", 10, True, GREY, after=2)
    par("React 19 · TypeScript · Vite 6 · Tailwind CSS · Framer Motion · three.js",
        11.5, False, NAVY, after=2)
    par("STOMP / SockJS · WebRTC", 11.5, False, NAVY, after=14)

    par("PHẠM VI TÀI LIỆU", 10, True, GREY, after=2)
    par("Frontend — 4 trang, 18 component, 46 endpoint REST, 7 topic STOMP",
        11.5, False, NAVY, after=2)
    par("Phát hành ngày 08/11/2026", 10.5, False, GREY, after=0)

    brk = doc.add_paragraph()
    brk.add_run().add_break(WD_BREAK.PAGE)
    made.append(brk._p)

    for el in made:
        anchor.addprevious(el)


def fix_code_paragraphs(doc):
    """Force left alignment on every code block paragraph (no justification)."""
    n = 0
    for p in doc.paragraphs:
        if p.style.name not in ("Source Code", "Verbatim Char"):
            continue
        pPr = p._p.get_or_add_pPr()
        for jc in pPr.findall(qn("w:jc")):
            pPr.remove(jc)
        jc = OxmlElement("w:jc")
        jc.set(qn("w:val"), "left")
        pPr.append(jc)
        n += 1
    print(f"code paragraphs left-aligned: {n}")


def fix_tables(doc):
    """Enable autofit + shrink table text so long URLs stay readable."""
    n = 0
    for table in doc.tables:
        table.autofit = True
        tblPr = table._tbl.tblPr
        for layout in tblPr.findall(qn("w:tblLayout")):
            tblPr.remove(layout)
        layout = OxmlElement("w:tblLayout")
        layout.set(qn("w:type"), "autofit")
        tblPr.append(layout)

        for row in table.rows:
            for cell in row.cells:
                for p in cell.paragraphs:
                    pf = p.paragraph_format
                    pf.space_before = Pt(1)
                    pf.space_after = Pt(1)
                    pf.line_spacing = 1.12
                    for r in p.runs:
                        r.font.size = Pt(9)
                        r.font.name = BODY
        n += 1
    print(f"tables normalised: {n}")


def shade_header_rows(doc):
    """Light shading on the first row of every table + repeat it across pages."""
    n = 0
    for table in doc.tables:
        if not table.rows:
            continue
        hdr = table.rows[0]
        # repeat header row on page breaks
        trPr = hdr._tr.get_or_add_trPr()
        if not trPr.findall(qn("w:tblHeader")):
            th = OxmlElement("w:tblHeader")
            trPr.append(th)
        for cell in hdr.cells:
            tcPr = cell._tc.get_or_add_tcPr()
            for old in tcPr.findall(qn("w:shd")):
                tcPr.remove(old)
            shd = OxmlElement("w:shd")
            shd.set(qn("w:val"), "clear")
            shd.set(qn("w:color"), "auto")
            shd.set(qn("w:fill"), "E8EDF6")
            tcPr.append(shd)
            for p in cell.paragraphs:
                for r in p.runs:
                    r.font.bold = True
                    r.font.color.rgb = NAVY
        n += 1
    print(f"header rows shaded: {n}")


def set_a4(doc):
    """Đặt khổ A4 cho toàn bộ section (mặc định pandoc để khổ Letter)."""
    for section in doc.sections:
        section.page_width = Cm(21.0)
        section.page_height = Cm(29.7)


def add_footer_page_numbers(doc):
    for section in doc.sections:
        footer = section.footer
        p = footer.paragraphs[0] if footer.paragraphs else footer.add_paragraph()
        p.text = ""
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER

        def styled(run):
            run.font.name = BODY
            run.font.size = Pt(9)
            run.font.color.rgb = GREY
            return run

        def field(instr):
            r = styled(p.add_run())
            fld = OxmlElement("w:fldChar")
            fld.set(qn("w:fldCharType"), "begin")
            r._r.append(fld)
            r2 = styled(p.add_run())
            it = OxmlElement("w:instrText")
            it.set(qn("xml:space"), "preserve")
            it.text = instr
            r2._r.append(it)
            r3 = styled(p.add_run())
            fld2 = OxmlElement("w:fldChar")
            fld2.set(qn("w:fldCharType"), "end")
            r3._r.append(fld2)

        styled(p.add_run("PITECH LAB — Dynamic Portfolio  ·  Trang "))
        field(" PAGE ")
        styled(p.add_run(" / "))
        field(" NUMPAGES ")


def main():
    build_merged()
    run_pandoc()
    doc = docx.Document(str(OUT))
    set_a4(doc)
    build_cover(doc)
    fix_code_paragraphs(doc)
    fix_tables(doc)
    shade_header_rows(doc)
    add_footer_page_numbers(doc)
    doc.save(str(OUT))
    print("cover + footer applied ->", OUT, OUT.stat().st_size, "bytes")


if __name__ == "__main__":
    main()