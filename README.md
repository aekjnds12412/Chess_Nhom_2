# ♟️ PIXEL CHESS — CỜ VUA TRỰC TUYẾN ĐA LUỒNG (TCP & UDP)

> **Đồ án môn Lập trình Mạng (Network Programming) — Trường ĐH Giao thông vận tải TP.HCM (UTH)**  
> **Sinh viên thực hiện:** Nguyễn Trọng Trình

Ứng dụng cờ vua trực tuyến nhiều người chơi (Multiplayer Online Chess) viết bằng **Python & Tkinter**, kết hợp kiến trúc mạng đa luồng giữa **TCP (bảo đảm toàn vẹn dữ liệu)** và **UDP (tốc độ cao, độ trễ thấp)**. Giao diện Pixel Art cổ điển, hỗ trợ tiếng Việt đầy đủ.

---

## 🚀 HƯỚNG DẪN CHẠY NHANH (QUICK START)

Bạn có thể chạy thử nghiệm ngay lập tức trên Windows bằng các file kịch bản `.cmd` có sẵn:

### Cách 1: Chơi thử ngay một mình với máy (PixelBot)
* Mở **`Run.cmd`** $\rightarrow$ bấm nút **`Chơi thử ngay với máy`** (hoặc chạy **`tools/Play-Demo.cmd`**).
* Ứng dụng sẽ tự khởi động Server ngầm, tự tạo tài khoản khách và mở bàn cờ đấu ngay với PixelBot.

---

### Cách 2: Chạy Demo 2 người chơi trên cùng 1 máy tính (Khuyên dùng khi báo cáo)
Chỉ mất **3 bước đơn giản**:
1. **Bước 1 — Mở Server:** Double-click file **`Server.cmd`** (cửa sổ đen hiện thông báo `Pixel Chess TCP 0.0.0.0:8765 | UDP 9999` -> thu nhỏ cửa sổ xuống taskbar, giữ chạy ngầm).
2. **Bước 2 — Mở Người chơi 1:** Double-click file **`Run.cmd`**, chọn **Tạo tài khoản mới** (vd: `alice` / `1234`), bấm **Đăng nhập**, sau đó bấm **Tạo phòng** (chọn cờ trắng).
3. **Bước 3 — Mở Người chơi 2:** Double-click tiếp file **`Run.cmd`** (mở cửa sổ thứ hai), tạo tài khoản (vd: `bob` / `1234`), bấm **Đăng nhập**, nhìn vào Sảnh chờ sẽ thấy bàn cờ của `alice` -> bấm **Vào đấu**.
   *(Bàn cờ bắt đầu ngay lập tức, 2 người chơi có thể đi quân, chat và thả icon qua lại).*
4. **Thử nghiệm Reconnect trong 60 giây:** Ở cửa sổ `alice`, bấm vào tên góc trên phải -> bấm nút duy nhất **`Rời ván & Đăng xuất`**:
   * Cửa sổ Alice tự động bật ngay màn hình Đăng nhập kèm thông báo: *"Đã ngắt kết nối. Bạn có 60 giây để đăng nhập lại ván cờ."*
   * Cửa sổ Bob lập tức hiển thị thẻ người chơi: `Trắng · Mất kết nối (Chờ 60s)`.
   * Ở cửa sổ Alice: Tên và mật khẩu đã sẵn sàng, chỉ cần bấm **Đăng nhập** lại $\rightarrow$ Lập tức quay lại đúng bàn cờ đang chơi dở!
   * *(Nếu để quá 60 giây không đăng nhập lại: Server sẽ tự động xử thua Alice do "Mất kết nối quá 60 giây" và Bob thắng).*

---

### Cách 3: Chơi giữa 2 máy tính khác nhau qua mạng LAN / Wi-Fi
1. **Máy 1 (Máy chủ):** Double-click file **`Server.cmd`**. Cho phép Tường lửa Windows (Firewall) nếu có hỏi.
2. **Máy 2 (Máy khách):** Mở **`Run.cmd`** -> tại hộp thoại đăng nhập, bấm nút **`Tìm server LAN`**. 
   * Hệ thống sẽ tự động quét UDP Broadcast và điền IP của Máy 1 vào ô địa chỉ.
   * *(Nếu router Wi-Fi chặn Broadcast, chỉ cần gõ thủ công `IP_CUA_MAY_1:8765`).*
3. Cả 2 máy đăng nhập tài khoản và vào thi đấu bình thường.
4. **Người thứ 3 vào xem:** Bấm nút **Vào xem** (Spectator) để theo dõi trực tiếp bàn cờ mà không được can thiệp nước đi.

---

## 🛠️ CÀI ĐẶT THỦ CÔNG (Dành cho máy mới chưa có môi trường)

Yêu cầu máy đã cài **Python 3.10 trở lên** (tích chọn *Add Python to PATH* khi cài đặt):

```powershell
# 1. Cài đặt các thư viện cần thiết (Pillow xử lý ảnh đồ họa)
pip install -r requirements.txt

# 2. Khởi động ứng dụng (hoặc app.py --server để chạy máy chủ)
python app.py
```
*(Ghi chú: Thư viện luật cờ vua chuẩn quốc tế `python-chess` đã được tích hợp sẵn trong thư mục `vendor/`, không cần tải thêm).*

---

## 🌟 ĐẶC TÍNH KỸ THUẬT NỔI BẬT

| Tính năng | Giao thức | Cổng (Port) | Chi tiết triển khai |
| :--- | :---: | :---: | :--- |
| **Đăng nhập / Đăng ký** | **TCP** | `8765` | Header 4-byte framing độ dài, bảo mật băm mật khẩu PBKDF2-HMAC-SHA256 (120.000 vòng + Salt 16 byte). |
| **Nước cờ & Đồng bộ FEN** | **TCP** | `8765` | Server-Authoritative: Server độc quyền kiểm tra luật cờ FIDE, broadcast FEN chuẩn cho 2 bên. |
| **Khung chat chữ** | **TCP** | `8765` | Đảm bảo tin nhắn hiển thị đúng thứ tự, không bị thất lạc chữ. |
| **Dò tìm Server mạng LAN** | **UDP** | `9999` | Client gửi gói Broadcast `255.255.255.255:9999`, Server phản hồi IP tự động. |
| **Đồng hồ đếm ngược** | **UDP + TCP** | `UDP: 9999`<br>`TCP: 8765` | **Kết hợp thông minh**: UDP phát nhịp 5Hz (0.2s/lần) cho kim giây hiển thị mượt mà; TCP gửi chốt chặn mỗi 2s để chống lệch giờ và dự phòng nếu mạng rớt gói UDP. |
| **Thả biểu cảm Emoji** | **UDP** | `9999` | Bắn icon tức thời (`👍`, `🔥`, `👏`, `🤔`), có rate-limit chống spam. |
| **Khôi phục phiên (Reconnect 60s)** | **TCP** | `8765` | **Tự động hiện màn hình đăng nhập**: Khi mất kết nối hoặc đóng app, giao diện tự động bật ngay màn hình Đăng nhập. Người chơi có **60 giây** để đăng nhập lại bằng tài khoản của mình và tiếp tục ván đấu (giữ nguyên thế cờ FEN và thời gian đồng hồ). Quá 60s Server tự động xử thua. |

---

## 🎮 THAO TÁC ĐIỀU KHIỂN TRONG TRẬN ĐẤU

- **Đi quân:** Bấm vào quân cờ rồi bấm ô đích, hoặc nhấn giữ và kéo thả. Các ô đi hợp lệ sẽ có dấu chấm tròn màu xám gợi ý.
- **Nhập thành:** Kéo Vua đi ngang 2 ô; hệ thống tự nhảy Xe theo đúng luật.
- **Bắt Tốt qua đường (En Passant) & Phong cấp:** Tự động nhận diện; khi Tốt chạm hàng cuối sẽ hiện bảng chọn Hậu / Xe / Tượng / Mã.
- **Lật bàn cờ:** Bấm nút **Lật bàn** hoặc nhấn phím tắt `Ctrl + F`.
- **Xin hòa & Đầu hàng:** Bấm **Hòa** (đối thủ bấm Hòa để chấp thuận), hoặc bấm **Đầu hàng** để xử thua ngay.
- **Xuất biên bản ván cờ:** Bấm **`PGN ↓`** để tải về file PGN chuẩn thi đấu quốc tế.
- **Xem lại lịch sử:** Bấm nút **`Lịch sử ván đấu`** để xem 30 ván gần nhất lưu trong cơ sở dữ liệu.

---

## 🔍 TIỆN ÍCH XEM CƠ SỞ DỮ LIỆU (DATABASE VIEWER)

Dự án có sẵn công cụ xem nhanh Database mà không cần cài phần mềm SQLite bên ngoài:
* Double-click file **`tools/Xem_Database.cmd`**.
* Terminal sẽ hiển thị trực quan:
  1. **Bảng Users:** Danh sách tài khoản đã đăng ký, chuỗi Hash bảo mật PBKDF2 và Salt.
  2. **Bảng Games:** Lịch sử các ván cờ (Tên người chơi, kết quả `1-0`, `0-1`, `1/2-1/2`, lý do kết thúc, thời gian thi đấu).

---

## 📂 CẤU TRÚC THƯ MỤC DỰ ÁN

Thư mục đã được sắp xếp tinh gọn — ở ngoài cùng chỉ giữ lại 2 file chạy chính:

```text
D:\LTM\Chess\Chess\
├── Run.cmd                 # 🟢 Kịch bản khởi động Client (Chơi cờ)
├── Server.cmd              # 🟢 Kịch bản khởi động Server chuyên dụng
├── app.py                  # Điểm khởi động chính của Python
├── README.md               # Hướng dẫn sử dụng trực quan
├── requirements.txt        # Danh sách thư viện Python (Pillow)
│
├── chessnet/               # Gói mã nguồn mạng và logic cờ vua
│   ├── protocol.py         # 4-byte Length-Prefix framing, JSON protocol
│   ├── server.py           # GameServer đa luồng (TCP 8765 + UDP 9999)
│   ├── client.py           # NetworkClient nền, luồng nhận sự kiện
│   ├── gui.py              # Toàn bộ giao diện Tkinter, Canvas bàn cờ
│   └── storage.py          # Quản lý SQLite, băm mật khẩu PBKDF2
│
├── assets/                 # Hình ảnh sprite quân cờ Pixel Art
├── data/                   # Cơ sở dữ liệu SQLite (pixel_chess.db)
├── docs/                   # Tài liệu đồ án, giấy phép và kịch bản
├── docker/                 # Cấu hình container Dockerfile & compose
├── tests/                  # Bộ kiểm thử mạng tự động (test_network.py)
├── tools/                  # Các công cụ phụ (Play-Demo, Test, Xem_Database)
└── vendor/                 # Thư viện ngoài đính kèm sẵn (python-chess 1.11.2)
```

---

## 🧪 CHẠY KIỂM THỬ TỰ ĐỘNG (UNIT TESTS)

Để chạy kiểm tra toàn bộ hoạt động của socket mạng TCP, UDP, xử lý framing và luật cờ:
* Double-click file **`tools/Test.cmd`**, hoặc chạy lệnh:
```powershell
python app.py --test
```
*Kết quả:* **14/14 bài kiểm thử đạt chuẩn (OK)** chạy trên môi trường Loopback Socket thực tế.

---

## ❓ CÁC VẤN ĐỀ THƯỜNG GẶP (TROUBLESHOOTING)

1. **Lỗi "Đã ngắt kết nối với máy chủ" ngay khi vừa đăng nhập:**
   * *Nguyên nhân:* Cổng `8765` đang bị một tiến trình khác (như Node.js, Web Server) chiếm giữ.
   * *Khắc phục:* Mở PowerShell kiểm tra và tắt ứng dụng trùng cổng:
     ```powershell
     Get-Process -Id (Get-NetTCPConnection -LocalPort 8765).OwningProcess | Stop-Process -Force
     ```
2. **Không tìm thấy server khi bấm "Tìm server LAN":**
   * *Nguyên nhân:* Mạng Wi-Fi chặn gói tin UDP Broadcast giữa các thiết bị.
   * *Khắc phục:* Gõ trực tiếp địa chỉ IP nội bộ của máy chủ vào ô `Địa chỉ server` (Ví dụ: `192.168.1.15:8765`).
