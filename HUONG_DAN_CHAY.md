# Hướng dẫn chạy — dành cho thành viên mới

## 1. Lấy mã nguồn

Chấp nhận lời mời vào kho nếu kho riêng tư. Mở https://github.com/aekjnds12412/Chess_Nhom_2 → Code → Download ZIP, giải nén vào một thư mục của bạn. Mở Terminal/PowerShell tại thư mục có `app.py`.

Để cùng phát triển, nên dùng GitHub Desktop: File → Clone repository → chọn Chess_Nhom_2. Không tải lại ZIP rồi chép đè mỗi lần làm việc.

## 2. Cài lần đầu trên Windows

Cài Python 3.10 trở lên từ https://www.python.org/downloads/; bật Add Python to PATH và cài thành phần Tcl/Tk. Sau đó mở lại Terminal.

```powershell
python --version
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

Không cần kích hoạt môi trường bằng Activate.ps1. Các lệnh dưới gọi trực tiếp Python trong `.venv`.

## 3. Chạy trò chơi

```powershell
.\.venv\Scripts\python.exe app.py
```

Chọn chơi thử với máy hoặc đăng ký tài khoản và đăng nhập. Chạy demo nhanh:

```powershell
.\.venv\Scripts\python.exe app.py --demo
```

## 4. Chơi giữa hai máy cùng mạng LAN

Máy chủ mở một Terminal riêng và giữ cửa sổ đó chạy:

```powershell
.\.venv\Scripts\python.exe app.py --server
```

Trên máy chủ chạy `ipconfig` để xem IPv4 của kết nối Wi-Fi/Ethernet đang dùng. Mỗi máy người chơi chạy `app.py`, chọn Tìm server LAN hoặc nhập `IP_MAY_CHU:8765` (thay bằng IP thật). Tạo tài khoản khác nhau, một người tạo phòng, người còn lại vào phòng.

Nếu Windows hỏi tường lửa, người vận hành cho phép Python trên mạng riêng. Server dùng TCP 8765 và UDP 9999. Không dùng `127.0.0.1` để kết nối sang máy khác. Nếu dò LAN không thấy, thử nhập IP trực tiếp. Bản này dành cho LAN/demo; chưa cấu hình dịch vụ Internet hay TLS.

## 5. Kiểm thử

```powershell
.\.venv\Scripts\python.exe app.py --test
```

Chỉ báo đạt khi tất cả bài kiểm thử kết thúc và hiện `OK`. Nếu bị treo, Ctrl+C và gửi tên bài đang chạy cùng log vào Issue.

Kiểm tra khi chuẩn bị đưa lên kho ngày 24/10/2026: toàn bộ mã Python qua kiểm tra cú pháp; 14/14 bài kiểm thử TCP/UDP và luật cờ đạt (OK, 3,385 giây) khi chạy ngoài sandbox. Lần chạy trong sandbox bị treo; không tái hiện khi được phép dùng socket cục bộ. Cần kiểm tra giao diện và demo LAN trên các máy thật trước khi nghiệm thu. Docker chưa được kiểm chứng trong đợt bàn giao này.

## 6. Lỗi thường gặp

- Không tìm thấy Python: cài Python, bật PATH và mở lại Terminal; có thể dùng `py -3` thay `python` ở bước tạo môi trường.
- `No module named PIL`: chạy lại lệnh cài requirements bằng đúng Python trong `.venv`.
- Không thấy bàn cờ hoặc thiếu ảnh: giữ nguyên thư mục `assets` và chạy tại thư mục có `app.py`.
- Không kết nối được: kiểm tra server đang chạy, IP, cổng và mạng riêng; thử IP thủ công.

`data/chess.db` và `.local/client.json` được tạo khi chạy. Không đưa chúng lên GitHub. Không sửa thư viện trong `vendor/chess` nếu chưa thống nhất với nhóm; giữ nguyên thông tin giấy phép.

