# 🤖 Antigravity Telegram Remote Controller 📱

Công cụ mạnh mẽ giúp bạn **điều khiển Google Antigravity trên máy tính từ điện thoại thông qua Telegram** ở bất cứ đâu (4G, 5G, Wi-Fi khác mạng):
- 💬 **Gửi Prompt**: Nhắn tin tiếng Việt, dán code, tự động gõ vào ô chat Antigravity và nhấn Enter.
- 🖼️ **Gửi Ảnh**: Chụp ảnh từ camera điện thoại hoặc chọn từ thư viện $\rightarrow$ dán trực tiếp vào Antigravity IDE qua Windows Clipboard.
- ⚡ **Duyệt Lệnh Nhanh**: Bấm nút `[Accept All]`, `[Reject All]`, `[Proceed]`, `[Stop]` ngay trên Telegram.
- 📸 **Xem Màn Hình Live**: Bấm nút chụp màn hình thời gian thực để theo dõi AI đang làm gì.
- 🔒 **Bảo Mật**: Chỉ tài khoản Telegram có User ID của bạn mới có quyền điều khiển.

---

## 🚀 Hướng Dẫn Cài Đặt Trong 2 Phút

### Bước 1: Lấy Token Bot Telegram (Miễn phí 100%)
1. Mở ứng dụng Telegram trên điện thoại hoặc máy tính, tìm kiếm **`@BotFather`**.
2. Nhắn `/newbot` cho BotFather.
3. Đặt **Tên Bot** (ví dụ: `My Antigravity Assistant`) và **Username Bot** (kết thúc bằng chữ `bot`, ví dụ: `my_antigravity_control_bot`).
4. BotFather sẽ gửi cho bạn đoạn **HTTP API Token** (dạng `7123456789:ABCdefGhIJKlmNoPQRstuVWXyz`).

### Bước 2: Lấy User ID Telegram của bạn
1. Trên Telegram, tìm kiếm **`@userinfobot`** và bấm Start.
2. Bot sẽ gửi cho bạn một dãy số `Id:` (ví dụ: `123456789`).

### Bước 3: Điền vào file `.env`
Mở file `.env` trong thư mục này và điền thông tin vừa lấy:
```env
TELEGRAM_BOT_TOKEN=7123456789:ABCdefGhIJKlmNoPQRstuVWXyz
ALLOWED_USER_IDS=123456789
WINDOW_TITLE_KEYWORD=Antigravity
```

### Bước 4: Khởi động Bot
- Chỉ cần **nhấp đúp chuột vào file `run.bat`** (hoặc gõ lệnh `python main.py` trong terminal).
- Mở Telegram trên điện thoại, bấm vào Bot của bạn và gửi `/start` để bắt đầu điều khiển!

---

## 🛠️ Công Cụ Hiệu Chỉnh Toạ Độ (Calibrate)
Nếu bạn muốn Bot click chính xác 100% vào các vị trí nút `Accept All`, `Reject All`, `Ô Chat`:
1. Nhấp đúp vào file `calibrate.bat` (hoặc chạy `python calibrate.py`).
2. Chọn số tương ứng và di chuyển chuột đến vị trí nút bấm trên màn hình máy tính. Toạ độ sẽ được tự động lưu vào `calibration.json`.

---

## 🧪 Kiểm Thử Hệ Thống
Nhấp đúp vào file `test.bat` để chạy kiểm thử tự động toàn bộ tính năng và edge cases.
