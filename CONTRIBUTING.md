# Hướng dẫn làm việc nhóm

## Chuẩn bị

1. Người sở hữu repository mời thành viên trong **Settings → Collaborators**; thành viên cần chấp nhận lời mời.
2. Clone bằng URL HTTPS/SSH của repository (nút **Code** trên GitHub).
3. Cài Python 3.10+ và Tcl/Tk. Trong thư mục dự án chạy:

```powershell
python -m pip install -r requirements.txt
python app.py --test
python app.py
```

Không cần chia sẻ tài khoản GitHub hoặc token cho nhau. Mỗi thành viên dùng tài khoản riêng.

## Quy trình mỗi đầu việc

Tạo một issue bằng mẫu **Công việc nhóm**, ghi mục tiêu, người nhận và tiêu chí hoàn thành. Mỗi đầu việc dùng một nhánh riêng:

```powershell
git switch main
git pull --ff-only origin main
git switch -c feature/ten-cong-viec
```

Sau khi sửa và kiểm tra:

```powershell
python app.py --test
git add ten_file_da_sua
git commit -m "Mo ta thay doi"
git push -u origin feature/ten-cong-viec
```

Mở pull request vào `main`, liên kết issue bằng `Closes #SO_ISSUE`, mô tả cách kiểm tra và nhờ ít nhất một thành viên khác review. Chờ CI đạt trước khi merge. Dùng **Squash and merge** nếu một nhánh có nhiều commit nhỏ.

Trước khi bắt đầu đầu việc tiếp theo, quay về `main` và pull lại. Nếu có xung đột, cập nhật nhánh bằng `git merge origin/main`, sửa các vùng xung đột rồi chạy lại kiểm thử. Tránh force-push lên nhánh người khác đang dùng.

## Gợi ý chia nhóm 6 người

| Thành viên | Phạm vi chính | File liên quan |
|---|---|---|
| 1 | TCP server, framing, heartbeat, reconnect | `protocol.py`, phần session/TCP của `server.py` |
| 2 | Phòng, matchmaking, luật, đồng hồ | phần room/game của `server.py` |
| 3 | UDP discovery, clock, emoji, spectator | phần UDP/spectator của `server.py` và `client.py` |
| 4 | Client networking, trạng thái kết nối | `client.py` |
| 5 | GUI và asset | `gui.py`, `assets/` |
| 6 | Database, kiểm thử, Docker và tài liệu | `storage.py`, `tests/`, Docker, README |

`server.py` và `client.py` đang có nhiều phần dùng chung. Những người cùng sửa một file nên trao đổi phạm vi trước, chia PR nhỏ hoặc tách module trong một issue riêng để hạn chế xung đột. Không đồng thời tự đổi cấu trúc thông điệp ở cả hai nhánh mà chưa thống nhất.

## Quy ước

- Nhánh: `feature/...`, `fix/...`, `docs/...`, `test/...`.
- Commit ngắn gọn, nói rõ thay đổi; không commit chỉ với nội dung “update”.
- Thay đổi giao thức cần sửa cả server/client, cập nhật README và kiểm thử tương ứng.
- Không sửa trực tiếp thư viện trong `vendor/` nếu không có đầu việc rõ ràng.
- Không commit `data/`, `.local/`, `.venv/`, log, mật khẩu hoặc token. `.gitignore` đã loại các thư mục này.
- Khi chia sẻ ảnh/log để debug, kiểm tra và ẩn token trước.

## CI

GitHub Actions chạy `compileall` và bộ kiểm thử mạng trên Windows/Linux, Python 3.10/3.12 khi push hoặc mở pull request. GUI được kiểm tra thủ công trên Windows; CI không mở cửa sổ Tkinter.

Sau khi repository được tạo, chủ repository nên bật rule cho `main` yêu cầu pull request, review và CI đạt trước khi merge (nếu gói GitHub hỗ trợ với chế độ repository đang chọn).
