#!/usr/bin/env python3
"""
Dựng lại file Word bàn giao từ các tài liệu Markdown trong docs/.

Cách dùng:
    # 1) Tạo reference.docx (style mẫu) — chỉ cần làm 1 lần
    pandoc --print-default-data-file reference.docx > /tmp/ref_base.docx
    python3 scripts/make_reference_docx.py

    # 2) Sinh file Word
    python3 scripts/build_handover_docx.py

Yêu cầu: pandoc >= 3.0, python-docx
"""
