#!/usr/bin/env python3
"""
Mock backend cho PITECH LAB Dynamic Portfolio.

Mục đích: chạy frontend khi chưa có backend Spring Boot thật, phục vụ
việc chụp ảnh giao diện và nghiệm thu trực quan.

Cung cấp:
  - REST  : /api/v1/{portfolio, admin/*, user/*, org/*, auth/*, upload}
  - STOMP : /ws  (SockJS fallback) — chat realtime + tín hiệu gọi video
  - Ảnh   : sinh từ https://placehold.co (không cần file cục bộ)

Chạy:
    python3 mock_backend.py [--port 8080]
"""
import json
import random
import string
import time
import uuid
from pathlib import Path

from fastapi import FastAPI, Request, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, Response
from starlette.websockets import WebSocket

app = FastAPI(title="PITECH LAB Mock Backend")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ----------------------------------------------------------------- dữ liệu mẫu
def _img(text: str, w=600, h=400) -> str:
    from urllib.parse import quote
    return f"https://placehold.co/{w}x{h}/1F3B73/FFFFFF?text={quote(text)}"


PROFILE = {
    "id": 1,
    "fullName": "PHẠM MINH ĐÀO",
    "userName": "minhdao",
    "titleVi": "KỸ SƯ PHẦM MỀM | FULL-STACK DEVELOPER",
    "titleEn": "SOFTWARE ENGINEER | FULL-STACK DEVELOPER",
    "jobTitle": "Backend Developer / DevOps Engineer",
    "bio": (
        "Kỹ sư phần mềm với hơn 3 năm kinh nghiệm thiết kế và vận hành hệ thống "
        "web phân tán. Chuyên sâu về Java/Spring Boot, React, DevSecOps và kiểm thử "
        "tự động. Đã tham gia nhiều dự án chuyển đổi số cho doanh nghiệp vừa và nhỏ, "
        "từ phân tích yêu cầu đến triển khai vận hành trên môi trường production."
    ),
    "avatarUrl": _img("MINH DAO", 600, 800),
    "strengths": "Problem Solving",
    "workStyle": "Professional",
    "regionName": "Miền Bắc",
    "localOrgName": "Chi nhánh Hà Nội",
    "departmentName": "Phòng Công nghệ Phần mềm",
    "departmentId": 3,
    "contact": {
        "email": "minhdao.pitechlab@gmail.com",
        "github": "https://github.com/dao24092004",
        "linkedin": "https://www.linkedin.com/in/dao24092004",
        "address": "Hà Nội, Việt Nam",
        "phone": "0904 140 022",
    },
    "projects": [
        {
            "id": 1,
            "name": "Hệ thống Quản lý Hồ sơ Năng lực (CV Profile Platform)",
            "description": (
                "Nền tảng portfolio động cho tổ chức, cho phép mỗi nhân sự có một trang hồ sơ "
                "riêng với đa ngôn ngữ và xuất CV ra PDF.\n"
                "Quản trị viên nhập liệu, duyệt kích hoạt hồ sơ và quản lý cây tổ chức 3 cấp.\n"
                "Tích hợp chat realtime STOMP và gọi video WebRTC peer-to-peer giữa khách truy cập "
                "và quản trị viên.\n"
                "Tối ưu bundle production từ 1,6 MB xuống dưới 500 KB thông qua code splitting."
            ),
            "imageUrl": _img("CV PLATFORM", 800, 450),
            "techStack": "React, TypeScript, Vite, Tailwind CSS, Framer Motion, STOMP, WebRTC",
            "sourceCodeUrl": "https://github.com/dao24092004/pitechlab-cv-profile",
            "demoUrl": "https://frontendcv.vercel.app",
            "role": "Full-stack Developer",
            "customer": "PITECH LAB",
        },
        {
            "id": 2,
            "name": "Ứng dụng Quản lý Sinh viên (JavaFX Multi-Tiers MVC)",
            "description": (
                "Ứng dụng desktop quản lý sinh viên theo kiến trúc MVC nhiều tầng trên JavaFX.\n"
                "Tách biệt rõ ràng model, repository, service, presentation và controller.\n"
                "Lưu trữ dữ liệu CSV với cơ chế kiểm tra ràng buộc dữ liệu tại tầng service.\n"
                "Đóng góp đầy đủ hồ sơ thiết kế, sơ đồ kiến trúc và bộ ảnh giao diện."
            ),
            "imageUrl": _img("JAVAFX MVC", 800, 450),
            "techStack": "Java 21, JavaFX, Maven, CSV, MVC Multi-Tiers",
            "sourceCodeUrl": "https://github.com/dao24092004",
            "role": "Backend Developer",
            "customer": "Đồ án thực tập",
        },
        {
            "id": 3,
            "name": "Pipeline DevSecOps với phát hiện mã độc tự động",
            "description": (
                "Pipeline CI/CD tích hợp quét mã nguồn bằng nhiều bộ công cụ phát hiện lỗ hổng.\n"
                "Mô hình học máy phân loại mã độc ransomware và dữ liệu rò rỉ DLP trên tập mẫu thật.\n"
                "Đánh giá độ chính xác theo ma trận nhầm lẫn trên ba lớp mô hình.\n"
                "Báo cáo kết quả định kỳ kèm biểu đồ so sánh hiệu năng."
            ),
            "imageUrl": _img("DEVSECOPS", 800, 450),
            "techStack": "Python, scikit-learn, Docker, GitHub Actions, Semgrep",
            "sourceCodeUrl": "https://github.com/dao24092004",
            "role": "DevOps Engineer",
            "customer": "Nghiên cứu khoa học",
        },
        {
            "id": 4,
            "name": "Hệ thống xác thực không mật khẩu WebAuthn",
            "description": (
                "Triển khai xác thực WebAuthn/FIDO2 trên Spring Boot kết hợp khóa bảo mật U2F.\n"
                "Đăng ký và xác thực bằng khóa công khai với thử thách bất biến ngẫu nhiên.\n"
                "Tài liệu đặc tả kỹ thuật kèm sơ đồ luồng đăng ký và luồng xác thực."
            ),
            "imageUrl": _img("WEBAUTHN", 800, 450),
            "techStack": "Spring Boot, Spring Security, WebAuthn, FIDO2",
            "sourceCodeUrl": "https://github.com/dao24092004",
            "role": "Backend Developer",
            "customer": "Đồ án thực tập",
        },
    ],
    "workHistory": [
        {
            "id": 1,
            "companyName": "PITECH LAB / INNOTECH SOLUTIONS",
            "position": "Backend Developer",
            "startDate": "06/2023",
            "endDate": "Hiện tại",
            "isCurrent": True,
            "description": (
                "Phát triển và vận hành các hệ thống web phục vụ khách hàng doanh nghiệp.\n"
                "Thiết kế REST API và mô hình dữ liệu phục vụ nhiều ứng dụng đồng thời.\n"
                "Xây dựng quy trình CI/CD với Docker và triển khai trên nền tảng đám mây."
            ),
        },
        {
            "id": 2,
            "companyName": "Trường Đại học Điện lực",
            "position": "Trợ giảng · Lập trình viên",
            "startDate": "09/2022",
            "endDate": "06/2023",
            "description": (
                "Hỗ trợ giảng dạy các môn lập trình Java và cơ sở dữ liệu.\n"
                "Xây dựng bộ tài liệu hướng dẫn và đồ án thực hành cho sinh viên."
            ),
        },
        {
            "id": 3,
            "companyName": "Công ty TNHH Phần mềm Vina",
            "position": "Thực tập sinh Backend",
            "startDate": "06/2022",
            "endDate": "08/2022",
            "description": (
                "Phát triển module thanh toán trên nền Spring Boot.\n"
                "Viết unit test và sửa lỗi bug được giao từ đội QA."
            ),
        },
        {
            "id": 4,
            "companyName": "Dự án mở nguồn cộng tác",
            "position": "Contributor",
            "startDate": "01/2022",
            "endDate": "Hiện tại",
            "description": (
                "Đóng góp mã nguồn và tài liệu cho các dự án mở nguồn trong lĩnh vực giáo dục.\n"
                "Tham gia code review và hỗ trợ cộng đồng."
            ),
        },
    ],
    "skills": [
        {"id": 1, "name": "Java / Spring Boot", "proficiency": 90, "category": "Backend"},
        {"id": 2, "name": "React / TypeScript", "proficiency": 85, "category": "Frontend"},
        {"id": 3, "name": "MySQL / PostgreSQL", "proficiency": 78, "category": "Database"},
        {"id": 4, "name": "Docker / Kubernetes", "proficiency": 72, "category": "DevOps"},
        {"id": 5, "name": "REST API Design", "proficiency": 88, "category": "Backend"},
        {"id": 6, "name": "Tailwind CSS", "proficiency": 80, "category": "Frontend"},
        {"id": 7, "name": "Unit Testing", "proficiency": 82, "category": "Backend"},
        {"id": 8, "name": "Git / GitHub Actions", "proficiency": 85, "category": "DevOps"},
        {"id": 9, "name": "Machine Learning", "proficiency": 70, "category": "Scientific"},
    ],
    "education": [
        {
            "id": 1,
            "school": "Trường Đại học Điện lực",
            "degree": "Kỹ sư Thông tin",
            "period": "2019 - 2023",
            "startDate": "2019-09-01",
            "endDate": "2023-06-30",
            "description": "Chuyên ngành Kỹ thuật phần mềm. Đạt giải Ba khoa học cấp trường.",
        },
        {
            "id": 2,
            "school": "Trung tâm Luyện thi ICPC",
            "degree": "Chứng chỉ ACM",
            "period": "2021",
            "startDate": "2021-01-01",
            "endDate": "2021-12-31",
            "description": "Luyện tập và thi chuẩn bị khu vực về thuật toán lập trình.",
        },
    ],
    "publications": [
        {
            "id": 1,
            "title": "Phát hiện mã độc ransomware bằng học máy trên luồng hành vi",
            "publisher": "Tạp chí Khoa học & Công nghệ",
            "releaseDate": "2024-06-15",
            "link": "https://doi.org/10.1000/pitechlab.2024.001",
        },
        {
            "id": 2,
            "title": "Đánh giá hiệu năng bộ lọc dữ liệu nhạy cảm DLP trong DevSecOps",
            "publisher": "Tạp chí An toàn thông tin",
            "releaseDate": "2024-12-20",
            "link": "https://doi.org/10.1000/pitechlab.2024.002",
        },
        {
            "id": 3,
            "title": "Kiến trúc portfolio động hỗ trợ trực tiếp WebRTC trong tuyển dụng",
            "publisher": "Nhập ký Nghiên cứu NCKH",
            "releaseDate": "2025-03-10",
            "link": "https://github.com/dao24092004/pitechlab-cv-profile",
        },
    ],
    "events": [
        {
            "id": 1,
            "name": "Giải Nhì Hackathon mùa hè",
            "role": "Trưởng nhóm",
            "date": "08/2023",
            "description": "Đạt giải Nhì với hệ thống phân tích log tự động.",
            "imageUrl": _img("HACKATHON", 400, 400),
        },
        {
            "id": 2,
            "name": "Hội thảo Khoa học Công nghệ Trẻ",
            "role": "Trình bày viên",
            "date": "11/2023",
            "description": "Trình bày nghiên cứu về nhận diện lỗ hổng bằng học máy.",
            "imageUrl": _img("SEMINAR", 400, 400),
        },
        {
            "id": 3,
            "name": "Chứng chỉ AWS Certified Solutions Architect",
            "role": "Ứng viên",
            "date": "05/2024",
            "description": "Đạt chứng chỉ thiết kế kiến trúc trên nền tảng đám mây.",
            "imageUrl": _img("CERT", 400, 400),
        },
        {
            "id": 4,
            "name": "Trợ giảng khóa học Lập trình Web",
            "role": "Giảng viên",
            "date": "09/2024",
            "description": "Hướng dẫn sinh viên năm ba xây dựng dự án full-stack.",
            "imageUrl": _img("TEACHING", 400, 400),
        },
    ],
}

REGIONS = [
    {"id": 1, "name": "Miền Bắc", "code": "MB"},
    {"id": 2, "name": "Miền Trung", "code": "MT"},
    {"id": 3, "name": "Miền Nam", "code": "MN"},
]
LOCALS = [
    {"id": 1, "name": "Chi nhánh Hà Nội", "code": "HN", "regionId": 1, "regionName": "Miền Bắc"},
    {"id": 2, "name": "Chi nhánh Hải Phòng", "code": "HP", "regionId": 1, "regionName": "Miền Bắc"},
    {"id": 3, "name": "Chi nhánh Đà Nẵng", "code": "DN", "regionId": 2, "regionName": "Miền Trung"},
    {"id": 4, "name": "Chi nhánh TP.HCM", "code": "HCM", "regionId": 3, "regionName": "Miền Nam"},
]
DEPARTMENTS = [
    {"id": 1, "name": "Phòng Phát triển", "code": "DEV", "localOrgId": 1, "localOrgName": "Chi nhánh Hà Nội"},
    {"id": 2, "name": "Phòng Kiểm thử", "code": "QA", "localOrgId": 1, "localOrgName": "Chi nhánh Hà Nội"},
    {"id": 3, "name": "Phòng Công nghệ Phần mềm", "code": "IT", "localOrgId": 1, "localOrgName": "Chi nhánh Hà Nội"},
    {"id": 4, "name": "Phòng Vận hành", "code": "OPS", "localOrgId": 2, "localOrgName": "Chi nhánh Hải Phòng"},
    {"id": 5, "name": "Phòng Hạ tầng", "code": "INFRA", "localOrgId": 3, "localOrgName": "Chi nhánh Đà Nẵng"},
    {"id": 6, "name": "Phòng Kinh doanh", "code": "BIZ", "localOrgId": 4, "localOrgName": "Chi nhánh TP.HCM"},
]

PROFILE_LIST = [
    {
        "id": 1,
        "fullName": PROFILE["fullName"],
        "jobTitle": PROFILE["jobTitle"],
        "avatarUrl": PROFILE["avatarUrl"],
        "userName": "minhdao",
    },
    {
        "id": 2,
        "fullName": "NGUYỄN THỊ BÍCH NGỌC",
        "jobTitle": "Frontend Developer",
        "avatarUrl": _img("BICH NGOC", 300, 300),
        "userName": "bichngoc",
    },
    {
        "id": 3,
        "fullName": "TRẦN VĂN HÙNG",
        "jobTitle": "DevOps Engineer",
        "avatarUrl": _img("VAN HUNG", 300, 300),
        "userName": "vanhung",
    },
    {
        "id": 4,
        "fullName": "LÊ THỊ MINH THU",
        "jobTitle": "QA Engineer",
        "avatarUrl": _img("MINH THU", 300, 300),
        "userName": "minhthu",
    },
    {
        "id": 5,
        "fullName": "VÕ THÀNH LONG",
        "jobTitle": "Data Engineer",
        "avatarUrl": _img("THANH LONG", 300, 300),
        "userName": "thanhlong",
    },
    {
        "id": 6,
        "fullName": "PHẠM QUỐC TUẤN",
        "jobTitle": "Mobile Developer",
        "avatarUrl": _img("QUOC TUAN", 300, 300),
        "userName": "quoctuan",
    },
    {
        "id": 7,
        "fullName": "ĐINH THỊ HẰNG NGA",
        "jobTitle": "Business Analyst",
        "avatarUrl": _img("HANG NGA", 300, 300),
        "userName": "hangnga",
    },
    {
        "id": 8,
        "fullName": "HOÀNG ANH TUẤN",
        "jobTitle": "Solution Architect",
        "avatarUrl": _img("ANH TUAN", 300, 300),
        "userName": "anhtuan",
    },
]

USERS = {"admin": {"role": "ADMIN", "profileId": 1, "username": "admin", "fullName": "Quản trị viên"},
         "minhdao": {"role": "USER", "profileId": 1, "username": "minhdao", "fullName": "Phạm Minh Đào"}}

# --------------------------------------------------------------- STOMP relay
_subscribers: dict = {}
_rooms: dict = {}


@app.websocket("/ws")
async def ws_endpoint(ws: WebSocket):
    await ws.accept()
    sub_ids = {}
    try:
        while True:
            raw = await ws.receive_text()
            try:
                msg = json.loads(raw)
            except Exception:
                continue
            body = msg.get("body")
            if body:
                try:
                    body = json.loads(body)
                except Exception:
                    pass
            headers = {k.lower(): v for k, v in (msg.get("headers") or {}).items()}
            destination = headers.get("destination") or ""
            action = msg.get("command")

            if action == "SUBSCRIBE":
                sub_ids[destination] = ws
                _subscribers.setdefault(destination, []).append(ws)
                continue
            if action == "UNSUBSCRIBE":
                lst = _subscribers.get(destination, [])
                if ws in lst:
                    lst.remove(ws)
                sub_ids.pop(destination, None)
                continue
            if action == "DISCONNECT":
                break

            # điều phối tin nhắn
            if destination == "/app/chat.sendToAdmin":
                relay(ws, "/topic/admin/messages", body)
                relay(ws, f"/topic/private/{body.get('senderId')}", body)
            elif destination == "/app/chat.replyToUser":
                relay(ws, "/topic/admin/messages", body)
                relay(ws, f"/topic/private/{body.get('recipientId')}", body)
            elif destination == "/app/video.request":
                relay(ws, "/topic/call-requests", body)
                relay(ws, "/topic/private/1", body)
            elif destination == "/app/video.signal":
                rid = body.get("roomId") if isinstance(body, dict) else None
                if rid:
                    relay(ws, f"/topic/video/{rid}", body)
    except Exception:
        pass
    finally:
        for dest in list(_subscribers):
            lst = _subscribers.get(dest, [])
            if ws in lst:
                lst.remove(ws)


def relay(sender, destination, body):
    payload = json.dumps({"body": json.dumps(body) if not isinstance(body, str) else body,
                          "headers": {}, "destination": destination})
    for target in list(_subscribers.get(destination, [])):
        if target is sender:
            continue
        try:
            import anyio
            anyio.from_thread.run  # noqa
        except Exception:
            pass
        try:
            asyncio_target = target
            asyncio_target._send(payload)
        except Exception:
            pass


# --------------------------------------------------------------- REST helpers
def ok(data):
    return JSONResponse(data)


@app.get("/api/v1/portfolio")
async def get_portfolio():
    return ok(PROFILE)


@app.get("/api/v1/admin/list")
async def admin_list(page: int = 0, size: int = 6):
    start = page * size
    content = PROFILE_LIST[start:start + size]
    total = len(PROFILE_LIST)
    pages = (total + size - 1) // size
    return ok({"content": content, "totalPages": pages, "totalElements": total,
               "number": page, "size": size})


@app.get("/api/v1/admin/portfolio/{pid}")
async def admin_portfolio(pid: int):
    return ok(PROFILE)


@app.get("/api/v1/view/code/{r}/{l}/{d}/{pid}")
async def view_hierarchy(r: str, l: str, d: str, pid: int):
    return ok(PROFILE)


@app.get("/api/v1/view/{r}/{pid}")
async def view_region(r: str, pid: int):
    return ok(PROFILE)


@app.get("/api/v1/view/{r}/{l}/{pid}")
async def view_local(r: str, l: str, pid: int):
    return ok(PROFILE)


@app.get("/api/v1/user/profile")
async def user_profile():
    return ok([PROFILE])


# ------------------------------------------------- CRUD thực thể con (mock)
_SUB = {
    "projects": "projects",
    "skills": "skills",
    "experiences": "workHistory",
    "educations": "education",
    "publications": "publications",
    "events": "events",
}


def _find(sub, sid):
    for item in PROFILE.get(_SUB[sub], []):
        if item.get("id") == sid:
            return item
    return None


def _make_admin_item(sub, body, pid):
    if sub == "projects":
        return {"id": body.get("id") or 99, "name": body.get("title") or body.get("name"),
                "description": body.get("description", ""), "imageUrl": body.get("imageUrl", ""),
                "techStack": ", ".join(body.get("technologies") or []),
                "sourceCodeUrl": body.get("repoUrl", ""), "role": body.get("role", ""),
                "customer": body.get("customer", "")}
    if sub == "skills":
        return {"id": body.get("id") or 99, "name": body.get("name", ""),
                "proficiency": body.get("proficiency", 50), "category": body.get("category", "")}
    if sub == "experiences":
        return {"id": body.get("id") or 99, "companyName": body.get("company", ""),
                "position": body.get("role", ""), "startDate": body.get("startDate", ""),
                "endDate": body.get("endDate", ""), "isCurrent": body.get("isCurrent", False),
                "description": body.get("description", "")}
    if sub == "educations":
        return {"id": body.get("id") or 99, "school": body.get("school", ""),
                "degree": body.get("degree", ""), "period": body.get("year", ""),
                "description": body.get("description", "")}
    if sub == "publications":
        return {"id": body.get("id") or 99, "title": body.get("title", ""),
                "publisher": body.get("publisher", ""), "releaseDate": body.get("releaseDate", ""),
                "link": body.get("url", "")}
    return {"id": body.get("id") or 99, "name": body.get("name", ""), "role": body.get("role", ""),
            "date": body.get("date", ""), "description": body.get("description", ""),
            "imageUrl": body.get("imageUrl", "")}


def _register_sub_entity_routes(prefix: str) -> None:
    """Đăng ký CRUD động cho /api/v1/{prefix}/{sub}[/{id}]"""

    @app.get(f"/api/v1/{prefix}/{{sub}}")
    async def _list(sub: str):
        return ok(PROFILE.get(_SUB.get(sub, ""), []))

    @app.post(f"/api/v1/{prefix}/{{sub}}")
    async def _create(sub: str, request: Request):
        body = await request.json()
        item = _make_admin_item(sub, body, body.get("profileId"))
        PROFILE.setdefault(_SUB[sub], []).append(item)
        return ok(item)

    @app.get(f"/api/v1/{prefix}/{{sub}}/{{sid}}")
    async def _detail(sub: str, sid: int):
        return ok(_find(sub, sid) or {})

    @app.put(f"/api/v1/{prefix}/{{sub}}/{{sid}}")
    async def _update(sub: str, sid: int, request: Request):
        body = await request.json()
        item = _find(sub, sid)
        new_item = _make_admin_item(sub, {**(item or {}), **body}, body.get("profileId"))
        new_item["id"] = sid
        lst = PROFILE.setdefault(_SUB[sub], [])
        for i, x in enumerate(lst):
            if x.get("id") == sid:
                lst[i] = new_item
                break
        else:
            lst.append(new_item)
        return ok(new_item)

    @app.delete(f"/api/v1/{prefix}/{{sub}}/{{sid}}")
    async def _delete(sub: str, sid: int):
        PROFILE[_SUB[sub]] = [x for x in PROFILE.get(_SUB[sub], []) if x.get("id") != sid]
        return ok({"status": "deleted"})


_register_sub_entity_routes("admin")
_register_sub_entity_routes("user")


@app.get("/api/v1/user/portfolio/{pid}")
async def user_portfolio(pid: int):
    return ok(PROFILE)


@app.post("/api/v1/user/import-cv")
async def user_import_cv(file: UploadFile = File(...)):
    await file.read()
    return ok({"status": "imported"})


@app.put("/api/v1/user/profile")
async def user_profile_put(request: Request):
    body = await request.json()
    PROFILE.update({k: v for k, v in body.items() if k in PROFILE})
    return ok(PROFILE)


@app.put("/api/v1/admin/profile")
async def admin_profile_put(request: Request):
    body = await request.json()
    for k, v in body.items():
        if k in PROFILE and k != "id":
            PROFILE[k] = v
    if body.get("departmentId"):
        dep = next((x for x in DEPARTMENTS if x["id"] == body["departmentId"]), None)
        if dep:
            PROFILE["departmentName"] = dep["name"]
            loc = next((x for x in LOCALS if x["id"] == dep["localOrgId"]), None)
            if loc:
                PROFILE["localOrgName"] = loc["name"]
                reg = next((x for x in REGIONS if x["id"] == loc["regionId"]), None)
                if reg:
                    PROFILE["regionName"] = reg["name"]
    return ok(PROFILE)


@app.delete("/api/v1/admin/profile/{pid}")
async def admin_profile_del(pid: int):
    return ok({"status": "deleted"})


@app.post("/api/v1/admin/profile/{pid}/activate")
async def admin_activate(pid: int):
    return ok({"status": "active"})


@app.get("/api/v1/org/regions")
async def get_regions():
    return ok(REGIONS)


@app.post("/api/v1/org/regions")
async def create_region(request: Request):
    body = await request.json()
    body["id"] = len(REGIONS) + 1
    REGIONS.append(body)
    return ok(body)


@app.put("/api/v1/org/regions/{rid}")
async def update_region(rid: int, request: Request):
    body = await request.json()
    for i, r in enumerate(REGIONS):
        if r["id"] == rid:
            REGIONS[i] = {**r, **body}
    return ok(body)


@app.delete("/api/v1/org/regions/{rid}")
async def delete_region(rid: int):
    REGIONS[:] = [r for r in REGIONS if r["id"] != rid]
    return ok({"status": "deleted"})


@app.get("/api/v1/org/locals")
async def get_locals():
    return ok(LOCALS)


@app.post("/api/v1/org/locals")
async def create_local(request: Request):
    body = await request.json()
    body["id"] = len(LOCALS) + 1
    LOCALS.append(body)
    return ok(body)


@app.put("/api/v1/org/locals/{lid}")
async def update_local(lid: int, request: Request):
    body = await request.json()
    for i, x in enumerate(LOCALS):
        if x["id"] == lid:
            LOCALS[i] = {**x, **body}
    return ok(body)


@app.delete("/api/v1/org/locals/{lid}")
async def delete_local(lid: int):
    LOCALS[:] = [x for x in LOCALS if x["id"] != lid]
    return ok({"status": "deleted"})


@app.get("/api/v1/org/departments")
async def get_departments():
    return ok(DEPARTMENTS)


@app.post("/api/v1/org/departments")
async def create_department(request: Request):
    body = await request.json()
    body["id"] = len(DEPARTMENTS) + 1
    DEPARTMENTS.append(body)
    return ok(body)


@app.put("/api/v1/org/departments/{did}")
async def update_department(did: int, request: Request):
    body = await request.json()
    for i, x in enumerate(DEPARTMENTS):
        if x["id"] == did:
            DEPARTMENTS[i] = {**x, **body}
    return ok(body)


@app.delete("/api/v1/org/departments/{did}")
async def delete_department(did: int):
    DEPARTMENTS[:] = [x for x in DEPARTMENTS if x["id"] != did]
    return ok({"status": "deleted"})


@app.post("/api/v1/auth/login")
async def login(request: Request):
    body = await request.json()
    u = (body.get("username") or "").strip()
    if u not in USERS:
        return JSONResponse({"message": "Tài khoản hoặc mật khẩu không đúng."}, status_code=401)
    info = USERS[u]
    return ok({"token": "mock-token-" + uuid.uuid4().hex[:16], **info})


@app.post("/api/v1/auth/register")
async def register(request: Request):
    body = await request.json()
    u = body.get("username")
    USERS[u] = {"role": "USER", "profileId": body.get("profileId"),
                "username": u, "fullName": body.get("fullName")}
    PROFILE["userName"] = u
    return ok({"status": "registered"})


@app.post("/api/v1/auth/change-password")
async def change_password(request: Request):
    return ok({"status": "changed"})


@app.post("/api/v1/upload")
async def upload(file: UploadFile = File(...)):
    ext = (file.filename or "image.png").split(".")[-1].lower()
    return ok(f"/uploads/{uuid.uuid4().hex[:8]}.{ext}")


@app.post("/api/v1/admin/import-cv")
async def import_cv(file: UploadFile = File(...)):
    await file.read()
    return ok({"status": "imported"})


@app.get("/api/v1/chat/history")
async def chat_history():
    return ok([])


@app.get("/api/v1/export/cv-data")
async def export_cv():
    return Response("CV export mock", media_type="text/plain")


@app.get("/api/v1/health")
async def health():
    return ok({"status": "UP"})


if __name__ == "__main__":
    import argparse
    import uvicorn

    ap = argparse.ArgumentParser()
    ap.add_argument("--port", type=int, default=8080)
    ap.add_argument("--host", default="0.0.0.0")
    args = ap.parse_args()
    uvicorn.run(app, host=args.host, port=args.port, log_level="warning")
