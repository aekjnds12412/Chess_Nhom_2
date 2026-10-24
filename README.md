# Chess Nhóm 2 — Cờ vua kết nối

Dự án desktop Python/Tkinter, chơi qua mạng TCP/UDP, có tài khoản, phòng chơi, bot và lịch sử ván.

## Tài liệu của nhóm

- [Hướng dẫn cài và chạy từng bước](HUONG_DAN_CHAY.md)
- [Phân công 6 thành viên và tiêu chí bàn giao](PHAN_CONG.md)
- [Quy trình đóng góp trên GitHub](CONTRIBUTING.md)

Mã nguồn tiếp tục từ bản Chess.rar do trưởng nhóm cung cấp. Không đưa cơ sở dữ liệu cá nhân, token phiên, môi trường ảo hoặc lịch sử Git cũ vào kho.

---

# Pixel Chess — Cờ vua kết nối

Ứng dụng desktop Python cho đề tài **Cờ vua trực tuyến đa luồng kết hợp TCP & UDP**. Giao diện tiếng Việt, dùng 12 quân pixel được tách trực tiếp từ ảnh bạn cung cấp trong `assets/original.png`.

## Chạy ngay trên Windows

- **`Play-Demo.cmd`**: mở ván luyện tập với PixelBot, tự tạo tài khoản khách và server cục bộ.
- **`Run.cmd`**: mở giao diện đăng nhập, tạo tài khoản hoặc chọn **Chơi thử ngay với máy**.
- **`Server.cmd`**: chạy server riêng; giữ cửa sổ này mở khi chơi LAN hoặc thử kết nối lại.
- **`Test.cmd`**: chạy bộ kiểm thử mạng và luật cờ.

Các launcher nhận thư mục hiện tại làm thư mục dự án. Trên máy đang phát triển, launcher tự nhận Python runtime có sẵn của Codex. Trên máy khác, cài Python **3.10 trở lên** từ python.org (bật Tcl/Tk và Add Python to PATH), rồi chạy:

```powershell
python -m pip install -r requirements.txt
python app.py
```

Thư viện luật cờ `chess==1.11.2` đã được kèm trong `vendor/`, nên không cần tải lại thư viện này để chạy bản được bàn giao. Pillow được dùng để hiển thị sprite. GUI cần màn hình tối thiểu khoảng 1100 × 760.

## Chơi hai máy trong LAN

1. Máy chủ mở `Server.cmd` trước. Mặc định lắng nghe **TCP 8765** và **UDP 9999** trên `0.0.0.0`.
2. Các máy cùng mạng mở `Run.cmd`, chọn **Tìm server LAN**. Có thể nhập trực tiếp `IP_MAY_CHU:8765` nếu broadcast bị router chặn. Nếu tìm được nhiều server, ô thông báo liệt kê địa chỉ để chọn bằng cách nhập vào trường server.
3. Mỗi kỳ thủ tạo tài khoản riêng trên server rồi đăng nhập.
4. Người thứ nhất **Tạo phòng**, người thứ hai chọn phòng và **Vào đấu**. Với phòng riêng, gửi mã 6 ký tự cho người kia để **Nhập mã phòng**.
5. Những máy còn lại chọn **Vào xem** để theo dõi cùng trạng thái bàn cờ. Có thể vào xem phòng riêng bằng mã.
6. Có thể chọn **Ghép trận ngẫu nhiên**: hai người cùng mức thời gian sẽ được ghép vào một phòng mới.

Nếu Windows hỏi quyền tường lửa khi chạy server, người vận hành cần cho phép kết nối trong mạng riêng. UDP broadcast thường chỉ đi trong cùng subnet. Với mạng Internet cần địa chỉ server truy cập được và cấu hình định tuyến các cổng tương ứng; tính năng tự dò không xuyên qua Internet/NAT.

Tự khởi động server: khi kết nối `127.0.0.1` mà chưa có server, ứng dụng sẽ chạy server nhúng. **Đóng ứng dụng đang giữ server nhúng sẽ đóng server đó.** Dùng `Server.cmd` riêng cho buổi demo nhiều máy và demo khôi phục phiên.

## Điều khiển

- Bấm quân rồi bấm ô đích, hoặc kéo thả. Các ô có dấu chấm/vòng tròn là nước đi hợp lệ.
- Nhập thành bằng cách đưa vua đi hai ô; bắt tốt qua đường thực hiện như một nước tốt bình thường.
- Khi tốt đến hàng cuối, chọn Hậu/Xe/Tượng/Mã trong hộp phong cấp.
- **Lật bàn** hoặc `Ctrl+F`; `Esc` bỏ chọn quân.
- **Hòa** gửi đề nghị; đối thủ bấm **Hòa** để đồng ý. Nước đi tiếp theo hủy đề nghị đang chờ.
- **Yêu cầu hòa theo luật** áp dụng lặp thế ba lần/luật 50 nước khi đến lượt và đủ điều kiện, gồm nước dự định mà thư viện xác định có thể yêu cầu hòa. Server tự xử lý hòa bắt buộc, chiếu hết, hết nước đi và thiếu quân.
- **Đầu hàng** hoặc rời phòng đang chơi sẽ kết thúc ván với kết quả thua.
- Chat phòng qua TCP; bốn biểu cảm nhanh qua UDP.
- **PGN ↓** xuất ván hiện tại. **Lịch sử & ELO** xem tối đa 30 ván gần nhất và tải lại PGN đã lưu.

### Đồng hồ

Hỗ trợ `3+0`, `5+0`, `10+5` (phút ban đầu + giây cộng sau mỗi nước đi). Chỉ server quyết định thời gian còn lại và kết quả hết giờ. Client nội suy để hiển thị mượt; nhận cập nhật UDP khoảng 5 lần/giây và TCP dự phòng mỗi 2 giây. Khi hết giờ, nếu đối phương không đủ vật chất chiếu hết theo kiểm tra của thư viện thì kết quả là hòa.

### Khôi phục kết nối

Client tự thử kết nối lại khi socket bị đứt; server giữ phiên **60 giây tính từ lúc phát hiện ngắt kết nối**. Heartbeat mỗi 3 giây và ngắt kết nối không phản hồi sau khoảng 12–15 giây. Đồng hồ **vẫn chạy** lúc mất mạng: có thể hết giờ trước khi hết hạn phiên.

Token được lưu tại `.local/client.json` để nút **Khôi phục phiên trước** có thể nối lại sau khi mở lại ứng dụng. Không lưu mật khẩu trong file này. Mỗi thư mục chạy giữ một token cuối; chạy hai cửa sổ bằng tài khoản khác nhau vẫn chơi được nhưng token lưu trên đĩa sẽ là phiên đăng nhập sau cùng. Trong bộ nhớ, hai cửa sổ vẫn giữ token độc lập.

Để demo mà không tắt Wi-Fi: bấm tên tài khoản ở góc trên phải → **Thử ngắt mạng & kết nối lại**. Đây là đóng socket thật, sau đó client tự bắt tay `RESUME` và nhận lại FEN, vai trò và đồng hồ. Server cần tiếp tục chạy; trạng thái ván đang chơi nằm trong RAM, không sống qua việc khởi động lại server.

## Kiến trúc

```text
Tkinter GUI ── hàng đợi sự kiện ── NetworkClient
                                  │
                     TCP 8765     │     UDP 9999
                length + JSON     │     discovery / clock / emoji
                                  ▼
                    GameServer (ThreadPoolExecutor)
                      ├─ Session + heartbeat + token
                      ├─ Lobby + matchmaking + private rooms
                      ├─ Room + python-chess + monotonic clock
                      └─ SQLite: accounts / ratings / history / PGN
```

| File | Trách nhiệm |
|---|---|
| `app.py` | Điểm khởi động GUI, server hoặc tests; nạp thư viện vendor |
| `chessnet/protocol.py` | Length-prefix framing, đọc đủ byte, kiểm tra frame |
| `chessnet/server.py` | Server TCP đa luồng, UDP, phiên và phòng, đồng hồ |
| `chessnet/storage.py` | SQLite, băm mật khẩu PBKDF2, lịch sử/ELO |
| `chessnet/client.py` | Luồng mạng, reconnect, UDP discovery, PixelBot |
| `chessnet/gui.py` | Giao diện Tkinter, bàn cờ Canvas, sprite và hộp thoại |
| `tools/extract_assets.py` | Tách 12 quân, loại nền đen, giữ nguyên pixel gốc |
| `tests/test_network.py` | Kiểm thử framing, luật và tích hợp TCP/UDP thực |

Server giới hạn 128 kết nối đồng thời bằng semaphore và `ThreadPoolExecutor`, một tác vụ đọc cho mỗi client. Dữ liệu phòng được bảo vệ bằng `RLock`; mỗi kết nối có khóa gửi để không đan xen frame. Mạng chạy ngoài luồng GUI; mọi cập nhật widget đều qua hàng đợi và `after()` của Tkinter.

TCP frame: **`[4 byte unsigned big-endian: N][N byte UTF-8 JSON]`**, giới hạn 64 KiB mỗi frame. `receive()` đọc đủ byte nên xử lý được dính gói, phân mảnh và Unicode. Sai định dạng hoặc vượt giới hạn sẽ bị từ chối.

Ví dụ thông điệp:

```json
{"type":"LOGIN","name":"Alice","password":"demo1234","register":true}
{"type":"CREATE","title":"Bàn của Alice","control":"10+5","private":false}
{"type":"JOIN","id":"A1B2C3"}
{"type":"MOVE","from":"e2","to":"e4","promotion":""}
{"type":"SPECTATE","id":"A1B2C3"}
{"type":"RESUME","token":"<token nhận từ WELCOME>"}
```

Các loại khác: `LOBBY`, `MATCH`, `CANCEL_MATCH`, `LEAVE`, `PING`, `PONG`, `CHAT`, `DRAW`, `CLAIM_DRAW`, `RESIGN`, `HISTORY`, `PGN`. Server phát `STATE` gồm FEN, SAN/UCI, danh sách nước hợp lệ, vai trò, người chơi, đồng hồ và kết quả. Client không gửi FEN hay thời gian để ghi đè server.

UDP: `DISCOVER` kèm `app: PIXEL_CHESS_V1` gửi broadcast cổng 9999; server trả địa chỉ nguồn cùng cổng TCP. Sau đăng nhập, `REGISTER` gắn endpoint UDP với token và IP của kết nối TCP. `CLOCK` có mã phòng/revision; `EMOJI` chỉ nhận bốn giá trị cho phép và có giới hạn tốc độ. Chat tối đa 280 ký tự, giữ 60 tin gần nhất.

## Dữ liệu và phạm vi

- Cơ sở dữ liệu `data/chess.db` được tạo tự động. Mật khẩu dùng PBKDF2-HMAC-SHA256, salt ngẫu nhiên riêng và so sánh constant-time.
- ELO khởi tạo 1200, hệ số K=24, cập nhật hai người khi kết thúc ván. Ván có tên bắt đầu `Luyện tập · ` không tính ELO. Đây là quy ước cho bản bài tập, chưa phải hệ thống xếp hạng chống lạm dụng.
- PixelBot là minimax sâu 2 nửa nước, có chấm vật chất/vị trí đơn giản. Nó tham gia qua một TCP client thật và chỉ nhằm luyện tập/demo; không phải engine chuyên nghiệp.
- Trạng thái phiên, phòng, chat và ghép trận nằm trong RAM. Tài khoản, kết quả, PGN và ELO nằm trong SQLite.
- Chọn **chat + emoji** trong phần tương tác mở rộng; chưa có voice chat. Chưa có đăng nhập TLS, reset mật khẩu, lưu ván đang chơi qua restart hoặc dịch vụ triển khai Internet được quản trị. Phù hợp chạy LAN/demo học phần.
- Bộ asset là ảnh người dùng cung cấp; không suy đoán giấy phép phân phối ảnh. Xem `THIRD_PARTY.md` về thư viện luật cờ và giấy phép GPL.

## Kiểm thử

```powershell
python app.py --test
```

14 bài kiểm thử chạy socket TCP/UDP thực trên `127.0.0.1` với cổng và SQLite tạm. Bao phủ phân mảnh/dính gói, giới hạn frame, đăng nhập/băm mật khẩu, nước đi sai lượt, spectator chỉ xem, chiếu hết/PGN/ELO, nhập thành/bắt tốt qua đường/phong cấp Mã, reconnect còn hạn/hết hạn, hết giờ/cộng giờ, UDP discovery/clock/emoji, nhiều phòng/ghép trận, chat/hòa và client tự reconnect. Chạy trong môi trường cho phép socket loopback.

### Demo cho nhóm 6 người

1. Một máy chạy server riêng; hai máy đăng nhập, ghép trận và chơi vài nước.
2. Máy thứ tư vào xem, gửi chat và emoji; xác minh bàn cờ giống nhau.
3. Máy thứ năm/sáu tạo bàn khác; minh họa hai phòng không ảnh hưởng nhau.
4. Một kỳ thủ thử ngắt socket rồi reconnect; kiểm tra giữ FEN và thời gian tiếp tục giảm.
5. Mô phỏng ngắt hơn 60 giây để thấy xử thua; kiểm tra lịch sử và ELO.

## Docker (server)

```powershell
docker compose up --build
```

GUI chạy ở máy Windows, kết nối `IP_MAY_CHAY_DOCKER:8765`. Dữ liệu giữ trong volume `chess-data`. UDP discovery broadcast qua Docker bridge/Docker Desktop có thể không được chuyển tiếp; nhập IP thủ công khi cần. Dockerfile chỉ khởi động server nên không cần thư viện đồ họa. Cấu hình Docker được cung cấp nhưng chưa chạy kiểm thử Docker trên máy này.

## Nguồn tham khảo

Luật cờ, FEN, SAN và PGN sử dụng [tài liệu chính thức python-chess](https://python-chess.readthedocs.io/en/latest/). Phần TCP/UDP, quản lý phòng, phiên, lưu trữ, bot và giao diện nằm trong mã nguồn dự án.
