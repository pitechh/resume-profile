# PITECH LAB — Backend (Node.js + Express, không database)

Backend lưu dữ liệu dạng **file JSON trong thư mục** `backend/storage/`
(không cần cài database, không migration).

```
backend/
├── src/
│   ├── server.js              ← entry point, đăng ký router
│   ├── seed.js                ← tạo dữ liệu mẫu (npm run seed)
│   ├── lib/
│   │   └── store.js           ← tầng lưu trữ: đọc/ghi JSON nguyên tử (.tmp → rename)
│   ├── middleware/
│   │   └── validate.js        ← chuẩn hoá lỗi JSON / HttpError
│   └── routes/
│       ├── files.js           ← CRUD generic theo collection
│       ├── portfolio.js       ← snapshot hồ sơ có version
│       └── misc.js            ← health, liệt kê collection
├── storage/                   ← dữ liệu thật (đã gitignore, xem bên dưới)
├── package.json
└── README.md
```

## Chạy

```bash
cd backend
npm install        # 1 lần duy nhất
npm run seed       # tạo dữ liệu mẫu (tuỳ chọn)
npm start          # http://localhost:8080
npm run dev        # watch mode (tự restart khi sửa code)
```

| Biến môi trường      | Mặc định                  | Ý nghĩa                          |
| -------------------- | ------------------------- | -------------------------------- |
| `PORT`               | `8080`                    | Cổng lắng nghe (trùng FE `.env`) |
| `STORAGE_ROOT`       | `<backend>/storage`       | Thư mục gốc chứa dữ liệu         |
| `STORAGE_MAX_BYTES`  | `5242880` (5 MB)          | Giới hạn 1 document              |
| `STORAGE_MAX_FILES`  | `1000`                    | Giới hạn số file mỗi collection  |

## Quy ước lưu trữ

- Mỗi **collection** = 1 thư mục con trong `storage/`
- Mỗi **document** = 1 file `<docId>.json`
- Snapshot hồ sơ: `storage/portfolio/<profileId>/__current.json` (bản mới nhất)
  + `storage/portfolio/<profileId>/<stamp>__<id>.json` (lịch sử version)

## API

### Nhóm mới — file storage (lưu JSON, không DB)

Base: `http://localhost:8080/api/v1/storage`

### Nhóm tương thích — mock backend cũ (`routes/legacy.js`)

Base: `http://localhost:8080/api/v1` — giữ nguyên các endpoint mà FE đang gọi
(`GET /portfolio`, `/admin/*`, `/user/*`, `/org/*`, `/auth/*`, `POST /upload`...)
để giao diện chạy ổn định trong lúc chờ backend Spring Boot thật.

> Realtime (`/ws` STOMP over SockJS) đã có trong backend Node này (`src/lib/stomp.js`):
> chat khách↔Admin, yêu cầu & tín hiệu gọi video WebRTC, broadcast `PROFILE_UPDATED`
> trên `/topic/public/updates` khi `PUT /admin/profile` hoặc `PUT /user/profile`
> (trang chủ tự tải lại, đúng BR-20). Gói `sockjs` đã có trong `package.json`.

### CRUD file generic

| Method   | Endpoint                              | Mô tả                                    |
| -------- | ------------------------------------- | ---------------------------------------- |
| `GET`    | `/health`                             | Kiểm tra service                         |
| `GET`    | `/`                                   | Liệt kê collection + thống kê            |
| `GET`    | `/{collection}`                       | Liệt kê document (metadata nhẹ)          |
| `POST`   | `/{collection}`                       | Tạo document — body `{ id?, data, title? }`, `id` tự sinh nếu bỏ trống |
| `GET`    | `/{collection}/{docId}`               | Lấy 1 document                           |
| `PUT`    | `/{collection}/{docId}`               | Ghi đè / upsert                          |
| `PATCH`  | `/{collection}/{docId}`               | Merge 1 phần field                       |
| `DELETE` | `/{collection}/{docId}`               | Xoá document                             |
| `GET`    | `/{collection}/download/{docId}`      | Tải file `.json` gốc                     |
| `GET`    | `/{collection}/export`                | Gộp cả collection thành 1 file để tải    |
| `POST`   | `/import/{collection}`                | Nạp hàng loạt — body `{ items: [{id?, data}], overwrite? }` |

### Snapshot hồ sơ (có version)

| Method | Endpoint                          | Mô tả                          |
| ------ | --------------------------------- | ------------------------------ |
| `POST` | `/portfolio/{profileId}`          | Lưu snapshot mới (tạo version) |
| `GET`  | `/portfolio/{profileId}`          | Lấy bản mới nhất               |
| `GET`  | `/portfolio/{profileId}/versions` | Lịch sử các bản đã lưu         |

### Ví dụ curl

```bash
# tạo ghi chú
curl -X POST localhost:8080/api/v1/storage/notes \
  -H 'Content-Type: application/json' \
  -d '{"title":"Việc cần làm","data":{"title":"Việc cần làm","done":false}}'
# → {"status":"created","id":"1","collection":"notes",...}

# lấy ra
curl localhost:8080/api/v1/storage/notes/1

# sửa 1 phần
curl -X PATCH localhost:8080/api/v1/storage/notes/1 \
  -H 'Content-Type: application/json' -d '{"data":{"done":true}}'

# lưu snapshot hồ sơ
curl -X POST localhost:8080/api/v1/storage/portfolio/1 \
  -H 'Content-Type: application/json' -d '{"fullName":"PHẠM MINH ĐÀO"}'
```

## Nối với frontend

Frontend đã trỏ `VITE_API_URL=http://localhost:8080` (xem `.env.example`),
service gọi API nằm trong `services/api.ts` → `storageService` /
`portfolioStorageService`. Chỉ cần chạy `npm start` ở đây rồi `npm run dev`
ở thư mục gốc là hai bên gặp nhau.
