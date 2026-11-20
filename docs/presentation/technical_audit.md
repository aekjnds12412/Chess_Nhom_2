# Kiểm tra kỹ thuật cho slide và demo

## Kết luận dùng cho kịch bản 7 phút

Nội dung TCP, UDP, server authoritative, spectator và reconnect phù hợp mã hiện tại. Demo 180 giây khả thi nếu tạo sẵn tài khoản, chạy server riêng và chuẩn bị ba client. Trình dẫn và thao tác máy chính, người hỗ trợ chỉ phản hồi nước đi/vào xem khi được ra hiệu.

## Câu chữ cần giữ chính xác

- **60 giây tính từ khi server ghi nhận ngắt kết nối**, không tính ngay khi người dùng rút dây mạng. Server gửi/nhận heartbeat, client gửi `PING` mỗi 3 giây. Server kiểm tra `seen > 12 giây` và socket có timeout 15 giây, vì vậy thời gian phát hiện mất mạng không cố định đúng 12 giây.
- Reconnect tự động dùng token phiên, nhận lại FEN, vai trò, người chơi và đồng hồ. **Đồng hồ vẫn chạy**, có thể hết giờ trước khi hết hạn phiên. Server phải tiếp tục hoạt động. Không khẳng định ván sống qua restart server vì phòng/phiên nằm trong RAM.
- Nút góc trên phải có tên tài khoản. Bấm nút đó mở **Kết nối của bạn**, rồi bấm **Thử ngắt mạng & kết nối lại**. Nút này đóng socket thật, client tự nối lại sau khoảng 1 giây. Trạng thái mất mạng có thể hiện rất nhanh; nói trước cho người xem quan sát. Không dùng **Rời phòng**, **Đăng xuất** hoặc tắt server để minh họa reconnect.
- **Đầu hàng** có hộp xác nhận **Kết thúc ván đấu và nhận thua?**. Bấm đồng ý kết thúc ván. **Rời phòng** khi đang đấu cũng có hộp xác nhận và tính thua, nên chỉ dùng sau khi kết thúc.
- ELO cập nhật trong SQLite khi ván kết thúc. Nhãn tài khoản trên GUI cập nhật lại khi mở **Lịch sử & ELO**. Đừng chỉ vào nhãn cũ rồi nói điểm chưa thay đổi. Phòng thường tính ELO, phòng tên bắt đầu `Luyện tập · ` không tính ELO. Demo nên dùng **Tạo phòng**, không dùng PixelBot nếu muốn chứng minh ELO.
- UDP clock gửi khoảng 5 lần/giây. TCP clock dự phòng khoảng mỗi 2 giây. Server kiểm soát thời gian, client nội suy để hiển thị. Không nói UDP bảo đảm đến nơi hay luôn nhanh hơn TCP.
- UDP discovery dùng broadcast cổng 9999; nếu cùng LAN nhưng router chặn broadcast, nhập IP thủ công. UDP endpoint sau đăng nhập đăng ký bằng token/IP. LAN demo này chưa dùng TLS, nên không quảng cáo bảo mật Internet hoàn chỉnh.
- `ThreadPoolExecutor(max_workers=128)` và semaphore cấu hình tối đa 128 kết nối. Đây là **giới hạn cấu hình**, không phải kết quả benchmark 128 người chơi. Server có `RLock` chung, xử lý nhiều kết nối nhưng các vùng cập nhật game vẫn tuần tự dưới khóa; broadcast đồng bộ nên client chậm có thể ảnh hưởng độ trễ. Tránh nói phòng độc lập tuyệt đối về hiệu năng.
- Mỗi kết nối có `send_lock` để các frame không xen kẽ byte. TCP là luồng byte, framing gồm 4 byte unsigned big-endian + JSON UTF-8, payload tối đa 65536 byte. `receive` đọc đủ byte rồi giải mã.
- Server xác nhận đúng phòng, vai trò, lượt đi, luật cờ và đồng hồ. Đây là kiểm soát tính hợp lệ, **không phải hệ thống phát hiện mọi gian lận** như dùng engine ngoài.

## Demo đề xuất 180 giây

### Chuẩn bị trước giờ

Chạy `Server.cmd` riêng. Tạo ba tài khoản khác nhau. Client A ở màn hình đăng nhập với tên/mật khẩu đã nhập để còn minh họa Tìm server LAN, B/C đã đăng nhập sảnh chờ. Dùng mức 5+0 để tránh hết giờ khi chuyển màn hình. Có sẵn IP server để nhập nếu broadcast lỗi. Không lưu mật khẩu thật vào slide.

### 0 đến 60 giây

Trình ở client A bấm **Tìm server LAN**, **Đăng nhập**. Bấm **Tạo phòng**, **Mở phòng**. Người hỗ trợ ở B chọn phòng và bấm **Vào đấu**. Người hỗ trợ C chọn **Vào xem**. Trình chỉ ra hai kỳ thủ và số khán giả. Nếu không đủ ba máy, ba cửa sổ riêng vẫn demo giao thức thật trên loopback, nhưng phải nói rõ đây là mô phỏng nhiều client trên một máy.

### 60 đến 120 giây

A đi `e2e4`, B phản hồi `e7e5`. Chỉ ra cùng trạng thái ở người chơi và khán giả, nhật ký SAN. Gửi một chat ngắn, chờ hơn nửa giây rồi gửi emoji vì chat/emoji cùng giới hạn tốc độ 0,5 giây. Có thể thử kéo quân sai ô để cho thấy GUI ngăn nước sai, nhưng không lấy thao tác đó làm bằng chứng riêng về server validation; bộ test có kiểm tra gửi nước sai trực tiếp qua TCP.

### 120 đến 180 giây

Trình mở tên tài khoản, bấm **Thử ngắt mạng & kết nối lại**. Chỉ ra bàn cờ còn nguyên, đồng hồ tiếp tục. Sau đó bấm **Đầu hàng**, xác nhận. Mở **Lịch sử & ELO** để thấy kết quả/điểm. Không mở hộp lưu PGN nếu thiếu thời gian, chỉ chỉ ra nút tải. Chuyển lại slide thảo luận.

## Kiểm thử

Có đúng **14 phương thức kiểm thử** trong `tests/test_network.py` (2 framing và 12 tích hợp). Chúng bao phủ nhiều tình huống, không phải 14 chức năng độc lập. Một vài kiểm thử hết hạn/hết giờ chỉnh trạng thái/thời gian trong server để chạy nhanh, không phải chờ 60 giây thật. Chúng không chứng minh tải lớn, tốc độ Internet hoặc GUI tự động.

Ngày 19/11/2026 đã thử `python app.py --test` bằng runtime đi kèm. Sandbox dừng ở test đầu sử dụng `socket.socketpair`, không có kết quả hoàn thành, và đã chủ động kết thúc tiến trình. **Không ghi mới chạy 14/14 đạt trong hôm nay.** Có thể ghi “Bộ kiểm thử gồm 14 ca; lần kiểm tra trước ghi nhận 14/14 đạt” dựa vào lịch sử, hoặc chỉ ghi “14 ca kiểm thử tích hợp và framing”. Không yêu cầu thêm quyền hay thay đổi mã app trong đợt audit này.

## Tham chiếu mã

`chessnet/gui.py`: `login_dialog`, `resign`, `leave`, `history_dialog`, `close`.

`chessnet/server.py`: `client_loop`, `snapshot`, `settle`, `finish`, `udp_loop`, `clock_loop`.

`chessnet/client.py`: `discover`, `NetworkClient.run`, `heartbeat`, `disconnect_transport`.

`chessnet/protocol.py`: `encode`, `exact`, `receive`.

`tests/test_network.py`: 14 phương thức `test_*`.
