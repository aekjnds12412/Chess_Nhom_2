# Phân công nhóm 6 người

Phân công theo cấu trúc mã nguồn hiện có; mỗi người đọc hiểu, kiểm tra và hoàn thiện phần của mình. Chưa có thông tin về thế mạnh hoặc hạn nộp nên đây là phân công khởi đầu. Tên hiển thị không phải tên tài khoản GitHub; chưa gán tài khoản hoặc gửi lời mời.

| Thành viên | Phạm vi phụ trách | Công việc và tiêu chí bàn giao | Nhánh đề xuất |
|---|---|---|---|
| Trưởng nhóm (chủ kho aekjnds12412) | app.py, các launcher .cmd, Docker, README và tài liệu nhóm | Tích hợp PR, hướng dẫn máy mới, kiểm tra bản demo chung; tổng hợp báo cáo. Bàn giao bản chạy được từ hướng dẫn và sơ đồ kiến trúc. | team/integration |
| Đỗ Đức Huy | chessnet/gui.py, assets/, tools/extract_assets.py | Giao diện đăng nhập, phòng, bàn cờ, kéo thả, phong cấp, đồng hồ. Bàn giao ảnh demo và kiểm tra thao tác, không cập nhật widget từ luồng mạng. | feature/gui |
| Huy Huỳnh | chessnet/server.py | Phòng chơi, ghép trận, xử lý lượt đi, đồng hồ, hòa/đầu hàng, nhiều phòng. Bàn giao demo 2 phòng độc lập, server từ chối nước đi sai lượt và đồng bộ kết quả. | feature/server |
| Lê Công Thịnh | discover(), NetworkClient trong chessnet/client.py; chessnet/protocol.py | TCP framing, UDP, tìm LAN, heartbeat, tự kết nối lại. Bàn giao kiểm tra phân mảnh/dính gói, 2 máy kết nối và khôi phục đúng FEN/vai trò. | feature/network |
| Quang Linh | chessnet/storage.py | Đăng ký/đăng nhập, băm mật khẩu, SQLite, ELO, lịch sử và PGN. Bàn giao mô tả bảng dữ liệu, kiểm tra tài khoản trùng/sai mật khẩu, kết quả lưu còn sau restart. | feature/storage |
| Trần Phúc Hậu | evaluate(), choose_move(), PracticeBot trong chessnet/client.py; tests/ | Bot và kiểm thử tích hợp. Phối hợp Công Thịnh điều tra bài framing đang treo; kiểm tra nước đặc biệt, reconnect, UDP và lịch sử. Bàn giao log test, bảng kết quả, bot chỉ đi nước hợp lệ. | feature/bot-tests |

## Tránh sửa trùng

- Thịnh và Hậu dùng chung client.py nhưng phụ trách các hàm/lớp khác nhau; báo nhau trước khi sửa. Nếu tách bot ra tệp riêng, thống nhất giao diện import trước.
- Thay đổi định dạng thông điệp do Thịnh đề xuất, Huy Huỳnh và Đức Huy cùng kiểm tra tác động trước khi gộp.
- Khi test phát hiện lỗi, Hậu ghi Issue và người sở hữu module sửa; Hậu kiểm tra lại.
- Luật cờ đang dùng thư viện vendor/chess; không chia nhiệm vụ viết lại thư viện đó.
- Mỗi người viết phần báo cáo của mình: chức năng, thiết kế, hàm chính, kết quả kiểm tra và hạn chế.

## Các mốc triển khai (chưa ấn định ngày)

1. Mốc 1: cả 6 người lấy mã, cài môi trường và chạy bản gốc; ghi lỗi trước khi sửa.
2. Mốc 2: thống nhất giao thức, mỗi người xử lý Issue trên nhánh riêng; PR nhỏ kèm bằng chứng kiểm tra.
3. Mốc 3: trưởng nhóm tích hợp, Hậu chạy toàn bộ tests, cả nhóm kiểm tra LAN và sửa lỗi còn lại.
4. Mốc 4: tổng hợp báo cáo, ảnh và tập thuyết trình.

## Kịch bản demo 6 người

Trưởng nhóm vận hành server riêng. Đức Huy và Huy Huỳnh chơi một ván. Công Thịnh kiểm tra ngắt mạng/kết nối lại với một người chơi. Quang Linh xem kết quả, PGN và ELO. Phúc Hậu thử chế độ xem, phối hợp tạo phòng thứ hai và ghi kết quả.

## Điều kiện hoàn thành một công việc

- Có commit và pull request mô tả thay đổi.
- Có cách kiểm tra và kết quả thực tế; không ghi đạt nếu chưa chạy.
- Không đưa dữ liệu cá nhân, token, môi trường ảo hoặc cache lên kho.
- Được ít nhất một thành viên xem lại trước khi trưởng nhóm gộp theo quy ước nhóm. Đây chưa phải quy tắc bảo vệ nhánh được GitHub cưỡng chế.
