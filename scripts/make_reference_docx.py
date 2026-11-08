#!/usr/bin/env python3
"""Build a styled reference.docx for pandoc (Vietnamese technical report)."""
import copy
import docx
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml.ns import qn
from docx.oxml import OxmlElement
from docx.shared import Pt, RGBColor

REF = "/tmp/ref_base.docx"
OUT = "/tmp/reference_styled.docx"

BODY_FONT = "Times New Roman"
MONO_FONT = "Consolas"
ACCENT = RGBColor(0x1F, 0x3B, 0x73)      # navy
ACCENT2 = RGBColor(0x0B, 0x6B, 0x6B)     # teal
GREY = RGBColor(0x44, 0x4A, 0x55)

doc = docx.Document(REF)


def set_style_font(style, name, size=None, bold=None, color=None, space_before=None,
                   space_after=None, keep_next=None, line=None):
    f = style.font
    f.name = name
    if size is not None:
        f.size = Pt(size)
    if bold is not None:
        f.bold = bold
    if color is not None:
        f.color.rgb = color
    # east-asian font
    rpr = style.element.get_or_add_rPr()
    rfonts = rpr.find(qn("w:rFonts"))
    if rfonts is None:
        rfonts = rpr.makeelement(qn("w:rFonts"), {})
        rpr.append(rfonts)
    for attr in ("w:ascii", "w:hAnsi", "w:cs", "w:eastAsia"):
        rfonts.set(qn(attr), name)
    pf = getattr(style, "paragraph_format", None)
    if pf is None:
        return
    if space_before is not None:
        pf.space_before = Pt(space_before)
    if space_after is not None:
        pf.space_after = Pt(space_after)
    if keep_next is not None:
        pf.keep_with_next = keep_next
    if line is not None:
        pf.line_spacing = line


# ---- Normal ----
normal = doc.styles["Normal"]
set_style_font(normal, BODY_FONT, size=11.5, space_after=6, line=1.35)
normal.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY

# ---- Headings ----
for lvl, (size, color, sb, sa) in enumerate(
    [(16, ACCENT, 16, 8), (13.5, ACCENT, 13, 6), (12, ACCENT2, 10, 5), (11.5, GREY, 8, 4)],
    start=1,
):
    st = doc.styles[f"Heading {lvl}"]
    set_style_font(st, BODY_FONT, size=size, bold=True, color=color,
                   space_before=sb, space_after=sa, keep_next=True)
    st.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.LEFT
    # remove italics that pandoc default may carry
    st.font.italic = False

# ---- Title / Subtitle ----
for name, size, color in [("Title", 24, ACCENT), ("Subtitle", 14, GREY)]:
    try:
        st = doc.styles[name]
    except KeyError:
        continue
    set_style_font(st, BODY_FONT, size=size, bold=True, color=color,
                   space_before=0, space_after=10)
    st.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.LEFT

# ---- Code ----
for name in ("Source Code", "Verbatim Char"):
    try:
        st = doc.styles[name]
    except KeyError:
        continue
    st.font.name = MONO_FONT
    st.font.size = Pt(9.5)
    if hasattr(st, "paragraph_format"):
        pf = st.paragraph_format
        pf.space_before = Pt(4)
        pf.space_after = Pt(4)
        pf.line_spacing = 1.15
        pf.alignment = WD_ALIGN_PARAGRAPH.LEFT
        # never justify monospace blocks
        ppr = st.element.get_or_add_pPr()
        for jc in ppr.findall(qn("w:jc")):
            ppr.remove(jc)
        jc = OxmlElement("w:jc")
        jc.set(qn("w:val"), "left")
        ppr.append(jc)

# ---- Table styles: shade header row ----
for tname in ("Table", "Compact", "Table Grid"):
    try:
        st = doc.styles[tname]
    except KeyError:
        continue
    st.font.name = BODY_FONT
    st.font.size = Pt(10)

doc.save(OUT)
print("written:", OUT)
