# Kịch bản thuyết trình Pixel Chess

**Thời lượng đúng 7 phút:** giới thiệu 1 phút, demo 3 phút, thảo luận 3 phút.

Phân công trình bày đề xuất. Trình thực hiện và thuyết minh toàn bộ demo. Không xác nhận tác giả từng phần mã nguồn.

## Phân công sáu thành viên

| Thành viên | Mã trong danh sách | Vai trò | Phần trình bày | Slide | Thời gian |
|---|---|---|---|---|---|
| Nguyễn Trọng Trình | 064206002062 | Nhóm trưởng | Thực hiện và thuyết minh demo | 2–4 | 180 giây |
| Huỳnh Xuân Huy | 087205004266 | Thành viên | Giới thiệu đề tài và nhóm | 1 | 60 giây |
| Lê Công Thịnh | 058206008700 | Thành viên | Thảo luận TCP và framing | 5 | 45 giây |
| Trần Phúc Hậu | 082206017584 | Thành viên | Thảo luận vai trò UDP | 6 | 45 giây |
| Đinh Quang Linh | 075206004391 | Thành viên | Thảo luận reconnect và server | 7 | 45 giây |
| Đỗ Đức Huy | 079206017998 | Thành viên | Thảo luận kiểm thử và kết lời | 8 | 45 giây |

## Lịch sân khấu

| Mốc cả bài | Người nói | Nội dung |
|---|---|---|
| 00:00–01:00 | Huỳnh Xuân Huy | Giới thiệu nhóm và đề tài |
| 01:00–04:00 | Nguyễn Trọng Trình | Trực tiếp demo và thuyết minh |
| 04:00–04:45 | Lê Công Thịnh | Thảo luận TCP và framing |
| 04:45–05:30 | Trần Phúc Hậu | Thảo luận UDP và đồng hồ |
| 05:30–06:15 | Đinh Quang Linh | Thảo luận reconnect |
| 06:15–07:00 | Đỗ Đức Huy | Thảo luận kiểm thử, giới hạn, kết lời |

## Lời nói theo slide

### Slide 1. Cờ vua trực tuyến đa luồng

**Người nói:** Huỳnh Xuân Huy. **Thời lượng:** 60 giây.

**Nội dung chiếu:**
- Hai kỳ thủ và khán giả cùng một ván cờ
- TCP truyền nước đi, UDP tìm server
- Server kiểm tra luật, đồng hồ và phiên
- Giới thiệu 1 phút, demo 3 phút, thảo luận 3 phút

**Lời nói gợi ý:**
Kính chào thầy cô và các bạn. Em là Huỳnh Xuân Huy, đại diện nhóm giới thiệu đề tài cờ vua trực tuyến đa luồng kết hợp TCP và UDP. Nhóm gồm Nguyễn Trọng Trình là nhóm trưởng, Lê Công Thịnh, Trần Phúc Hậu, Đinh Quang Linh, Đỗ Đức Huy và em. Hai kỳ thủ có thể chơi trên hai máy khác nhau, còn máy khác vào xem. Server giữ bàn cờ và thời gian chính thức. Nhóm dùng python-chess để kiểm tra luật, tập trung xây dựng phần mạng. Bài trình bày gồm một phút giới thiệu, ba phút demo và ba phút thảo luận. Sau đây, nhóm trưởng Trình trực tiếp thực hiện demo.

**Chuyển tiếp:** Em xin mời Nguyễn Trọng Trình thực hiện demo.

### Slide 2. Demo tìm server và vào phòng

**Người nói:** Nguyễn Trọng Trình. **Thời lượng:** 60 giây.

**Nội dung chiếu:**
- Server riêng đã chạy, ba tài khoản sẵn sàng
- Tìm server LAN và tạo phòng 5+0
- Client B vào đấu, client C vào xem
- Đối chiếu cùng mã phòng

**Lời nói gợi ý:**
Em là Nguyễn Trọng Trình và sẽ điều khiển, thuyết minh toàn bộ demo. Server riêng và ba tài khoản đã chuẩn bị trước. Máy A là kỳ thủ Trắng, máy B là kỳ thủ Đen, máy C là khán giả. Em chọn Tìm server LAN để client nhận địa chỉ phản hồi qua UDP, rồi đăng nhập bằng TCP. Em tạo phòng năm phút không cộng giờ, ra hiệu cho client B vào đấu và client C vào xem. Chúng ta đối chiếu mã phòng để xác nhận ba client cùng tham gia một ván.

**Chuyển tiếp:** Em chuyển sang đi quân và kiểm tra đồng bộ.

### Slide 3. Demo đồng bộ ván đấu

**Người nói:** Nguyễn Trọng Trình. **Thời lượng:** 60 giây.

**Nội dung chiếu:**
- Trắng đi e2–e4, Đen đi e7–e5
- Ba màn hình cùng bàn cờ và lượt đi
- Khán giả theo dõi, không đi quân
- Chat TCP rồi biểu cảm UDP

**Lời nói gợi ý:**
Em đi tốt từ e2 đến e4, sau đó phía Đen đi e7 đến e5. Mọi yêu cầu đều qua server kiểm tra trước khi phát trạng thái mới. Trên cả ba màn hình, vị trí quân, nhật ký và lượt đi giống nhau. Client khán giả nhận cùng trạng thái nhưng không có quyền đi quân. Em gửi thêm một tin nhắn, chờ hơn nửa giây rồi gửi biểu cảm vì hai thao tác dùng chung giới hạn tốc độ. Chat dùng TCP, biểu cảm dùng UDP. Đồng hồ giảm theo trạng thái do server quản lý.

**Chuyển tiếp:** Tiếp theo em thử ngắt socket và lấy lại phiên hiện tại.

### Slide 4. Demo reconnect và lưu kết quả

**Người nói:** Nguyễn Trọng Trình. **Thời lượng:** 60 giây.

**Nội dung chiếu:**
- Thử ngắt mạng và kết nối lại
- Giữ phòng, vai trò và vị trí quân
- Đồng hồ vẫn chạy khi ngắt
- Đầu hàng rồi mở Lịch sử & ELO

**Lời nói gợi ý:**
Em bấm tên tài khoản, mở Kết nối của bạn rồi chọn Thử ngắt mạng và kết nối lại. Nút này đóng socket thật, server vẫn chạy. Client tự gửi RESUME bằng mã phiên. Sau khi nối lại, mã phòng, vai trò và bàn cờ vẫn giữ đúng, đồng hồ tiếp tục giảm. Không cần đợi hết sáu mươi giây. Em cho một bên đầu hàng, xác nhận nhận thua rồi mở Lịch sử và ELO. Kết quả xuất hiện và nhãn điểm cập nhật lại khi mở lịch sử. Đây là khôi phục sau ngắt client, không phải phục hồi sau restart server.

**Chuyển tiếp:** Demo kết thúc. Em xin mời Lê Công Thịnh mở phần thảo luận TCP.

### Slide 5. TCP cần thêm độ dài thông điệp?

**Người nói:** Lê Công Thịnh. **Thời lượng:** 45 giây.

**Nội dung chiếu:**
- TCP tin cậy, vì sao vẫn cần framing?
- TCP giữ thứ tự byte, không giữ ranh giới JSON
- 4 byte độ dài giúp đọc đủ từng payload

**Lời nói gợi ý:**
[0–10 giây, hỏi] TCP đã bảo đảm truyền đúng thứ tự. Vậy vì sao nhóm vẫn phải thêm bốn byte độ dài trước mỗi JSON? [10–15 giây, dừng] Mời một ý kiến ngắn. [15–40 giây, chốt] TCP là luồng byte nên một JSON có thể bị chia thành nhiều lần đọc, hoặc hai JSON cùng đến trong một lần đọc. Header độ dài giúp bên nhận đọc đúng số byte của từng thông điệp, xử lý cả phân mảnh và dính gói. [40–45 giây, chuyển] Mời bạn Trần Phúc Hậu trao đổi về UDP.

**Chuyển tiếp:** Mời bạn Trần Phúc Hậu trao đổi về UDP.

### Slide 6. Mất gói UDP có làm sai đồng hồ?

**Người nói:** Trần Phúc Hậu. **Thời lượng:** 45 giây.

**Nội dung chiếu:**
- Mất một gói CLOCK có làm xử thua sai?
- Server giữ thời gian chính thức
- TCP dự phòng đồng hồ mỗi 2 giây
- Broadcast tìm server trong LAN

**Lời nói gợi ý:**
[0–10 giây, hỏi] Nếu UDP làm mất một gói cập nhật đồng hồ thì server có xử thua sai không? [10–15 giây, dừng] Mời một câu trả lời ngắn. [15–40 giây, chốt] Server tự tính thời gian chính thức nên mất một bản cập nhật ở client không đổi kết quả ván. Client có thể hiển thị chậm rồi đồng bộ lại ở gói tiếp theo. TCP gửi đồng hồ dự phòng mỗi hai giây. UDP còn dùng broadcast tìm server trong LAN và truyền emoji. [40–45 giây, chuyển] Mời bạn Đinh Quang Linh trình bày tình huống reconnect.

**Chuyển tiếp:** Mời bạn Đinh Quang Linh trao đổi về reconnect.

### Slide 7. Reconnect có tạm dừng ván cờ?

**Người nói:** Đinh Quang Linh. **Thời lượng:** 45 giây.

**Nội dung chiếu:**
- Mất mạng 10 giây có mất thời gian?
- Đồng hồ vẫn chạy trên server
- Giữ phiên 60 giây sau khi phát hiện ngắt
- RESUME lấy lại trạng thái hiện tại

**Lời nói gợi ý:**
[0–10 giây, hỏi] Người chơi mất mạng mười giây rồi quay lại. Đồng hồ có dừng trong mười giây đó không? [10–15 giây, dừng] Mời một ý kiến. [15–40 giây, chốt] Đồng hồ vẫn chạy trên server. Khi còn hạn, client dùng token gửi RESUME để nhận lại đúng phòng, vai trò và trạng thái. Sáu mươi giây tính từ khi server phát hiện ngắt, không nhất thiết từ lúc Wi-Fi bị tắt. Server phải tiếp tục chạy vì ván hiện tại nằm trong RAM. [40–45 giây, chuyển] Mời bạn Đỗ Đức Huy chốt phần kiểm thử.

**Chuyển tiếp:** Mời bạn Đỗ Đức Huy chốt phần kiểm thử và giới hạn.

### Slide 8. Kiểm thử đã đủ cho Internet?

**Người nói:** Đỗ Đức Huy. **Thời lượng:** 45 giây.

**Nội dung chiếu:**
- 14 bài kiểm thử đạt trên loopback
- Kết quả chức năng chưa phải benchmark tải
- Cần TLS và lưu ván qua restart
- Cảm ơn thầy cô và các bạn

**Lời nói gợi ý:**
[0–10 giây, hỏi] Mười bốn bài kiểm thử đã đạt trên loopback. Điều đó đã đủ để đưa lên Internet công cộng chưa? [10–15 giây, dừng] Mời một ý kiến ngắn. [15–38 giây, chốt] Chưa. Các bài kiểm tra xác minh các ca chức năng như framing, luật cờ, UDP và reconnect. Bản hiện tại chưa có TLS, chưa đo tải nhiều client thực tế và chưa lưu ván đang chơi qua restart server. Giới hạn cấu hình 128 kết nối chưa phải kết quả benchmark. [38–45 giây, kết] Nhóm em xin cảm ơn thầy cô và các bạn.

**Chuyển tiếp:** Nếu còn thời gian ngoài bảy phút, dùng phụ lục để trao đổi chuyên sâu.

## Chuẩn bị demo cho Trình

**Người điều khiển chính và người thuyết minh duy nhất:** Nguyễn Trọng Trình. Các bạn khác hỗ trợ im lặng khi cần.

- **Trần Phúc Hậu:** Chuẩn bị IP/LAN, giữ client B Đen, chỉ hỗ trợ vào phòng và e7e5 theo hiệu lệnh Trình.
- **Đinh Quang Linh:** Chuẩn bị client C khán giả, thao tác hỗ trợ theo hiệu lệnh, không thuyết minh demo.
- **Huỳnh Xuân Huy:** Bấm giờ, báo mốc 60, 120, 180 giây bằng tín hiệu im lặng.
- **Lê Công Thịnh:** Kiểm tra server riêng trước buổi, không tắt server trong reconnect.
- **Đỗ Đức Huy:** Chuẩn bị kết quả test và ảnh/video dự phòng đã tự xác minh trước buổi.

### Trước buổi trình bày

- Chạy lại python app.py --test trước buổi bảo vệ; lần 19/11/2026 đạt 14/14.
- Ba máy cùng LAN đã cài Python, Pillow và chess.
- Chạy Server.cmd riêng trước giờ, giữ server suốt demo.
- Ba tài khoản demo đã tạo trước. A ở màn hình đăng nhập với thông tin đã nhập; B/C ở sảnh.
- Biết IP server, kiểm tra TCP 8765 và UDP 9999 trước giờ.
- Dùng Tạo phòng thường với 5+0 để kiểm tra ELO; không dùng PixelBot.
- Không chiếu token hoặc mật khẩu. Có ảnh/video dự phòng nếu có thể.

### Ba phút demo

Mốc dưới đây tính riêng từ lúc Trình bắt đầu demo (tương ứng 01:00 của toàn bài).

| Mốc demo | Thao tác của Trình hoặc hiệu lệnh hỗ trợ | Dấu hiệu quan sát |
|---|---|---|
| 00:00–00:10 | Trình giới thiệu A Trắng, B Đen, C khán giả | Server riêng đang chạy. |
| 00:10–00:30 | Client A tìm server LAN, đăng nhập tài khoản sẵn | Client nhận IP rồi kết nối. |
| 00:30–01:00 | Tạo phòng 5+0, B vào đấu, C vào xem | Ba client cùng mã phòng. |
| 01:00–01:30 | Đi e2e4, e7e5, đối chiếu ba màn hình | Cùng bàn cờ, SAN và lượt. |
| 01:30–02:00 | Khán giả thử bấm quân; chat rồi chờ hơn 0,5 giây mới emoji | Khán giả không đi quân, chat/emoji hiện trong phòng. |
| 02:00–02:30 | Trình bấm tên tài khoản, Thử ngắt mạng & kết nối lại | Giữ phòng, vai trò, thế cờ, clock vẫn giảm. |
| 02:30–02:50 | Đầu hàng, xác nhận, mở Lịch sử & ELO | Có kết quả và điểm cập nhật. |
| 02:50–03:00 | Trình kết demo và mời Thịnh | Quay slide 5 đúng giờ. |

### Khi có sự cố

- Không thấy broadcast sau vài giây: nhập IP_MAY_CHU:8765 sẵn có, nói rõ bỏ qua discovery.
- Không có LAN: server riêng và ba client localhost; nói rõ mô phỏng trên một máy.
- Reconnect lỗi hoặc chậm: dùng ảnh/video đã kiểm tra, không kéo quá ba phút.
- Không chờ hết hạn 60 giây trên sân khấu; ca này nằm trong kiểm thử.
- Không mở hộp lưu PGN nếu thiếu giờ. Lịch sử là bước chính, PGN dành phần hỏi thêm.

## Cách điều phối ba phút thảo luận

Bốn câu 45 giây. Hỏi 8–10 giây, chờ tối đa 5 giây, chốt khoảng 25 giây, chuyển 5 giây. Không có phản hồi thì người phụ trách tự chốt. Nếu giảng viên hỏi trực tiếp, thay câu gợi ý bằng câu hỏi thật trong cùng khung ba phút; Trình điều phối.

Các câu hỏi trên slide 5–8 là gợi ý dẫn dắt, không yêu cầu khán giả phải phản hồi. Khi giảng viên đặt câu hỏi khác, trả lời câu hỏi thực thay cho câu gợi ý và giữ thời gian. Không đọc toàn bộ phụ lục trong bảy phút.

## Bốn slide phụ lục ngoài bảy phút

### Slide 9. Phụ lục A1: Kiến trúc hệ thống

**Người phụ trách:** Huỳnh Xuân Huy. **Thời lượng trong bài chính:** 0 giây.

Chỉ mở khi cần giải thích kiến trúc. Server giữ trạng thái chính thức. Client đưa sự kiện mạng vào hàng đợi để Tkinter cập nhật widget trên luồng giao diện. Mỗi phòng giữ bàn cờ, đồng hồ, hai kỳ thủ và khán giả riêng. Dữ liệu phòng nằm trong RAM. Tài khoản và kết quả đã kết thúc lưu SQLite. Các vùng cập nhật dùng RLock nên việc phục vụ nhiều kết nối không có nghĩa mọi thao tác game chạy đồng thời hoàn toàn. Phần này nằm ngoài bảy phút.

### Slide 10. Phụ lục A2: Framing và MOVE

**Người phụ trách:** Lê Công Thịnh. **Thời lượng trong bài chính:** 0 giây.

Ví dụ payload: {"type":"MOVE","from":"e2","to":"e4"}. Header ghi số byte payload theo big-endian. Server kiểm tra phòng, vai trò, lượt, clock và luật rồi phát STATE. Hàm đọc đủ byte tách đúng mỗi frame. Client không tự ghi đè FEN hay clock của server. Cơ chế này hạn chế cập nhật trái phép, chưa phát hiện engine bên ngoài hoặc thông đồng. GUI tự chặn nước sai không phải bằng chứng riêng cho kiểm tra server; bộ test gửi trực tiếp qua TCP để xác minh phần đó.

### Slide 11. Phụ lục A3: UDP và reconnect

**Người phụ trách:** Trần Phúc Hậu / Đinh Quang Linh. **Thời lượng trong bài chính:** 0 giây.

Broadcast thường chỉ trong cùng subnet, nên cần nhập IP khi discovery thất bại. Server đăng ký endpoint UDP theo token và IP TCP. Heartbeat mỗi ba giây; mạng mất im lặng cần timeout để phát hiện. Sáu mươi giây bắt đầu khi server ghi nhận ngắt. Đồng hồ vẫn chạy và server phải còn sống. Mỗi kết nối có khóa gửi tránh xen kẽ frame. Giới hạn 128 là cấu hình ThreadPool và semaphore, không phải số người chơi đã đo tải.

### Slide 12. Phụ lục A4: Dữ liệu và kiểm thử

**Người phụ trách:** Đỗ Đức Huy. **Thời lượng trong bài chính:** 0 giây.

Bộ kiểm thử có mười bốn ca TCP/UDP loopback. Ngày 19/11/2026, cả mười bốn ca đều đạt trong môi trường kiểm thử, không chứng minh tải nhiều máy hay GUI. Một số ca chỉnh thời gian phía server để chạy nhanh, không chờ sáu mươi giây thật. ELO dùng K bằng hai mươi bốn; ván luyện tập không tính điểm. Mật khẩu băm bảo vệ database nhưng transport chưa có TLS. Phòng, chat và phiên ở RAM. Cấu hình Docker có sẵn nhưng chưa được xác minh trong triển khai thực tế.

## Câu hỏi dự kiến để luyện tập

### 1. Vì sao không dùng toàn bộ TCP?

**Phụ trách:** Trần Phúc Hậu

TCP dùng cho nước đi và chat. UDP broadcast tìm server khi chưa biết IP, còn CLOCK/emoji là cập nhật ngắn hạn. Server vẫn quyết định kết quả.

### 2. Vì sao TCP cần framing?

**Phụ trách:** Lê Công Thịnh

TCP giữ thứ tự byte, không giữ ranh giới JSON. Header độ dài cho biết số byte payload để tách đúng từng thông điệp khi bị chia hoặc gộp.

### 3. Mất gói UDP có sai kết quả hết giờ?

**Phụ trách:** Trần Phúc Hậu

Server tự tính bằng thời gian monotonic. Client có thể hiển thị chậm rồi hiệu chỉnh, nhưng server không dùng đồng hồ client để kết luận.

### 4. FEN có chứa lịch sử ván không?

**Phụ trách:** Đinh Quang Linh

Không có cả chuỗi nước đi. Server giữ lịch sử board và gửi SAN/UCI riêng. PGN ghi lại cả ván.

### 5. 60 giây bắt đầu từ khi nào?

**Phụ trách:** Đinh Quang Linh

Từ khi server ghi nhận kết nối ngắt. Mất mạng im lặng cần heartbeat/timeout để phát hiện. Clock vẫn chạy, ván RAM không sống qua restart server.

### 6. Server đã chống gian lận hoàn toàn chưa?

**Phụ trách:** Lê Công Thịnh

Chưa. Server kiểm tra quyền, lượt, luật và clock. Hệ thống chưa phát hiện engine bên ngoài, thông đồng hoặc chiếm token.

### 7. 128 kết nối có phải benchmark?

**Phụ trách:** Trần Phúc Hậu

Không. Đó là giới hạn ThreadPool và semaphore. Chưa có đo độ trễ/tài nguyên với 128 client thực tế.

### 8. Băm mật khẩu đã đủ cho Internet chưa?

**Phụ trách:** Đỗ Đức Huy

Băm bảo vệ database, không mã hóa truyền tải. Cần thêm TLS, bảo vệ token, kiểm thử tải và lưu ván bền vững.

## Nhắc trước giờ bảo vệ

- Trình là người thực hiện demo. Thành viên khác chỉ hỗ trợ khi được ra hiệu.
- Một phút giới thiệu đã bao gồm lời mời chuyển người. Ba phút thảo luận đã bao gồm kết lời.
- Không chờ hết 60 giây reconnect trên sân khấu. Giữ server riêng chạy liên tục.
- Gửi chat rồi chờ hơn 0,5 giây mới gửi emoji.
- Đầu hàng cần xác nhận. Mở Lịch sử & ELO để nhãn điểm cập nhật.
- Nêu đúng phạm vi test loopback và những giới hạn chưa làm, không khẳng định benchmark hay chống gian lận hoàn toàn.
- Lần chạy kiểm thử ngày 19/11/2026 đạt 14/14. Chạy lại trước buổi bảo vệ để ghi nhận kết quả tại thời điểm trình bày.

## Căn cứ nội dung

Danh sách sáu thành viên do người dùng cung cấp trong tài liệu Word. Các mô tả kỹ thuật đối chiếu README.md, chessnet/protocol.py, chessnet/server.py, chessnet/client.py, chessnet/gui.py, chessnet/storage.py và tests/test_network.py của dự án. Phân công phát biểu là đề xuất cho buổi thuyết trình.
