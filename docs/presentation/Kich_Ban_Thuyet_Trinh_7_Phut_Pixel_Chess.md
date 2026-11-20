# TRƯỜNG ĐẠI HỌC GIAO THÔNG VẬN TẢI TP.HCM (UTH)
## VIỆN CÔNG NGHỆ THÔNG TIN VÀ ĐIỆN, ĐIỆN TỬ — NGÀNH CÔNG NGHỆ THÔNG TIN
### BÀI TẬP LỚN LẬP TRÌNH MẠNG — NHÓM 2

---

# KỊCH BẢN BẢO VỆ ĐỒ ÁN PIXEL CHESS (CHUẨN 7 PHÚT)
**Tổng thời lượng:** Đúng 7 phút (1 phút Slide + 3 phút Demo + 3 phút Thảo luận / Phản biện)  
**Người báo cáo chính:** **Nguyễn Trọng Trình** (MSSV: 064206002062 — Nhóm trưởng)  
**Danh sách thành viên Nhóm 2:**
1. **Nguyễn Trọng Trình** (064206002062 - Nhóm trưởng)
2. **Huỳnh Xuân Huy** (087205004266)
3. **Lê Công Thịnh** (058206008700)
4. **Trần Phúc Hậu** (082206017584)
5. **Đinh Quang Linh** (075206004391)
6. **Đỗ Đức Huy** (079206017998)

---

## PHẦN 1: THUYẾT TRÌNH SLIDE TỔNG QUAN ĐỀ TÀI (0:00 – 1:00 · ĐÚNG 1 PHÚT)

### ⏱ 0:00 – 1:00 · Báo cáo Slide: Kiến trúc Hybrid TCP & UDP và 3 Trụ cột cốt lõi

* **🗣 LỜI THOẠI NÓI TRƯỚC LỚP:**  
  > "Kính chào quý Thầy Cô và các bạn. Em là **Nguyễn Trọng Trình**, đại diện Nhóm 2 xin phép báo cáo bài tập lớn môn Lập trình Mạng với đề tài: **Cờ vua trực tuyến đa luồng Pixel Chess kết hợp giao thức TCP và UDP**.  
  > Hệ thống của nhóm em được xây dựng trên mô hình **Server-Authoritative** đa luồng với 3 trụ cột kỹ thuật cốt lõi:  
  > • **TCP (Port 8765):** Đảm bảo độ tin cậy tuyệt đối cho các nghiệp vụ xác thực tài khoản, quản lý sảnh chờ, nước đi quân cờ và khung trò chuyện. Nhóm sử dụng cơ chế đóng gói **Length-Prefix 4 byte** để triệt tiêu hoàn toàn sự cố dính gói và phân mảnh TCP.  
  > • **UDP (Port 9999):** Tối ưu hóa tốc độ cao và giảm tải tối đa cho hệ thống với 3 tính năng: **Broadcast (255.255.255.255)** để tự động dò tìm Server trong mạng LAN không cần gõ IP; **Đồng bộ nhịp đếm đồng hồ 5Hz (0.2s/lần)** giúp kim giây trôi mượt mà kết hợp chốt chặn TCP 2s chống lệch giờ; và **Thả biểu cảm Emoji tức thời** có giới hạn tần suất chống spam.  
  > • **Cơ chế Khôi phục phiên (60s Reconnect):** Khi người chơi bị đứt mạng hoặc vô tình văng app, Server tự động bảo lưu phòng trong 60 giây, cho phép người chơi đăng nhập lại để tiếp tục ván đấu ngay lập tức mà không bị mất dữ liệu.  
  > Sau đây em xin bắt đầu phần chạy Demo thực tế!"

* **👉 THAO TÁC THỰC HIỆN TRÊN MÀN HÌNH:**  
  Mở Slide trình chiếu của nhóm (Slide UTH Nhóm 2) ➔ Chỉ tay dõng dạc vào 3 biểu tượng trên slide:  
  Biểu tượng máy bay giấy (TCP) ➔ Biểu tượng cột sóng phát thanh (UDP) ➔ Biểu tượng máy chủ Server ➔ Chuyển ngay sang cửa sổ Desktop chuẩn bị thực hiện Demo.

* **✅ KẾT QUẢ ĐẠT ĐƯỢC:**  
  Gây ấn tượng mạnh ngay phút đầu tiên: Nắm chắc bản chất mạng, phân biệt rạch ròi TCP vs UDP, phong thái tự tin, chuyên nghiệp.

---

## PHẦN 2: TRÌNH DIỄN DEMO SỐNG ĐỘNG TRÊN MÁY TÍNH (1:00 – 4:00 · ĐÚNG 3 PHÚT)

### ⏱ 1:00 – 1:30 · Khởi động Server chuyên dụng (TCP 8765 & UDP 9999)

* **🗣 LỜI THOẠI NÓI TRƯỚC LỚP:**  
  > "Trước tiên em khởi động máy chủ bằng file **Server.cmd**. Máy chủ khởi chạy Socket TCP trên cổng **8765** và Socket UDP trên cổng **9999** tại địa chỉ **0.0.0.0**, chấp nhận mọi kết nối từ cạc mạng Wi-Fi và LAN. Cửa sổ console thông báo sẵn sàng, em thu nhỏ xuống taskbar để server chạy ngầm suốt buổi demo."

* **👉 THAO TÁC THỰC HIỆN TRÊN MÀN HÌNH:**  
  Double-click file `Server.cmd` ➔ Thấy dòng chữ `Pixel Chess TCP 0.0.0.0:8765 | UDP 9999` ➔ Thu nhỏ cửa sổ xuống Taskbar.

* **✅ KẾT QUẢ ĐẠT ĐƯỢC:**  
  Chứng minh Server độc lập, đa luồng, sẵn sàng đón nhận nhiều Client kết nối cùng lúc.

---

### ⏱ 1:30 – 2:10 · Khởi động 2 Client, UDP LAN Discovery và Ghép phòng thi đấu

* **🗣 LỜI THOẠI NÓI TRƯỚC LỚP:**  
  > "Bây giờ em mở 2 Client tượng trưng cho 2 kỳ thủ. Em mở **Run.cmd** lần 1, bấm nút **Tìm server LAN** để UDP Broadcast tự bắt IP máy chủ. Em đăng ký tài khoản **alice** mật khẩu **1234**, đăng nhập và bấm **Tạo phòng 5+0** làm quân Trắng.  
  > Tiếp theo, em mở **Run.cmd** lần 2 cho kỳ thủ Đen, đăng ký tài khoản **bob** mật khẩu **1234**. Ở màn hình Sảnh chờ của Bob lập tức thấy phòng của Alice, Bob bấm **Vào đấu**. Hai bên ghép trận thành công!"

* **👉 THAO TÁC THỰC HIỆN TRÊN MÀN HÌNH:**  
  1. Double-click `Run.cmd` ➔ Bấm 'Tìm server LAN' ➔ Tạo tài khoản `alice` / `1234` ➔ Tạo phòng 5+0 ➔ Snap nửa trái màn hình (`Win + Phím mũi tên Trái`).  
  2. Double-click `Run.cmd` lần 2 ➔ Tạo tài khoản `bob` / `1234` ➔ Bấm 'Vào đấu' bàn Alice ➔ Snap nửa phải màn hình (`Win + Phím mũi tên Phải`).

* **✅ KẾT QUẢ ĐẠT ĐƯỢC:**  
  Khán phòng thấy đồng thời 2 góc nhìn đối kháng (Alice góc nhìn Trắng bên trái, Bob góc nhìn Đen bên phải) trên cùng màn hình.

---

### ⏱ 2:10 – 2:40 · Đồng bộ nước đi cờ (TCP) · Chat phòng (TCP) · Biểu cảm Emoji (UDP)

* **🗣 LỜI THOẠI NÓI TRƯỚC LỚP:**  
  > "Ván đấu bắt đầu! Tại Client 1 (Alice), em đi quân Tốt từ **e2 sang e4**. Gói tin MOVE được gửi qua **TCP**, Server kiểm tra luật FIDE bằng thư viện python-chess rồi Broadcast trạng thái FEN mới về cả 2 máy. Nhìn sang màn hình Bob bên phải: quân cờ lập tức cập nhật và lượt chuyển sang Đen! Bob đi Tốt **e7 sang e5**.  
  > Em gõ tin nhắn trò chuyện: tin nhắn đi qua **TCP** đảm bảo không thất lạc chữ. Sau đó em bấm thả icon biểu cảm: Emoji được bắn qua **UDP** với độ trễ cực thấp dưới 5ms, hiển thị tức thì trên cả 2 bàn cờ!"

* **👉 THAO TÁC THỰC HIỆN TRÊN MÀN HÌNH:**  
  1. Client 1 (Alice): Nhấp Tốt **e2** ➔ Nhấp ô **e4**. Chỉ sang màn hình Bob: bàn cờ đã cập nhật, đồng hồ Đen đếm ngược.  
  2. Client 2 (Bob): Nhấp Tốt **e7** ➔ Nhấp ô **e5**. Chỉ sang màn hình Alice: Tốt Đen đã nhảy.  
  3. Gõ chat ở Client 1: 'Chao ban' ➔ Enter ➔ Màn hình Client 2 nhận ngay.  
  4. Bấm icon 🔥 hoặc 👍 ở góc dưới ➔ Biểu cảm bay lên tức thì trên cả 2 màn hình.

* **✅ KẾT QUẢ ĐẠT ĐƯỢC:**  
  Minh họa hoàn hảo: Nước cờ + Chat qua TCP tin cậy; Đồng hồ 5Hz + Biểu cảm qua UDP siêu tốc.

---

### ⏱ 2:40 – 3:30 · Mô phỏng ngắt kết nối và Khôi phục ván cờ trong 60 giây (60s Reconnect)

* **🗣 LỜI THOẠI NÓI TRƯỚC LỚP:**  
  > "Sau đây là tính năng chịu lỗi đặc biệt của nhóm: **Khôi phục phiên (60s Reconnect)**.  
  > Giả sử kỳ thủ Alice gặp sự cố rớt mạng hoặc bấm nhầm đăng xuất: Em bấm vào tên tài khoản Alice ở góc trên phải, chọn nút duy nhất: **'Rời ván & Đăng xuất'**. Socket TCP lập tức bị ngắt kết nối!  
  > • Cửa sổ của Alice tự động ngắt kết nối và **bật ngay màn hình Đăng nhập** kèm thông báo đếm ngược: *'Bạn có 60 giây để đăng nhập lại ván cờ'*.  
  > • Nhìn sang màn hình Bob bên phải: Thẻ của Alice lập tức chuyển sang trạng thái **'Trắng · Mất kết nối (Chờ 60s)'**, đồng hồ thi đấu trên Server vẫn tiếp tục đếm chính xác bằng monotonic clock.  
  > • Bây giờ tại Alice: Tên tài khoản và mật khẩu đã được tự động điền sẵn, em chỉ cần bấm **'Đăng nhập'** lại khi chưa hết 60 giây — và Thầy Cô thấy ngay: **Alice lập tức trở lại đúng bàn cờ đang chơi dở, thế cờ FEN và thời gian giữ nguyên 100%!** Thẻ bên Bob đổi lại thành 'Đã kết nối' và hai người tiếp tục thi đấu bình thường!"

* **👉 THAO TÁC THỰC HIỆN TRÊN MÀN HÌNH:**  
  1. Client 1 (Alice): Click vào tên góc trên phải ➔ Click nút xanh **'Rời ván & Đăng xuất'**.  
  2. Chỉ màn hình Alice: Hộp thoại Đăng nhập tự động hiện lên, thông báo còn hạn 60s, username/password đã có sẵn.  
  3. Chỉ màn hình Bob: Thẻ người chơi Alice hiện rõ chữ màu đỏ: `Trắng · Mất kết nối (Chờ 60s)`.  
  4. Client 1 (Alice): Click **'Đăng nhập'** (hoặc nhấn phím Enter) ➔ Màn hình Alice lập tức trở lại bàn cờ, thẻ phía Bob đổi lại màu xanh `Trắng · Đã kết nối`!

* **✅ KẾT QUẢ ĐẠT ĐƯỢC:**  
  **Điểm sáng lớn nhất của bài báo cáo!** Cơ chế Reconnect xử lý mượt mà, thông minh, thuyết phục hoàn toàn hội đồng.

---

### ⏱ 3:30 – 4:00 · Lịch sử ván đấu (SQLite) · Xuất biên bản PGN chuẩn · Kết thúc Demo

* **🗣 LỜI THOẠI NÓI TRƯỚC LỚP:**  
  > "Nếu người chơi mất kết nối quá 60 giây, Server sẽ tự động xử thua do 'Mất kết nối quá 60 giây'. Tại Client của Bob, em bấm vào nút **'Lịch sử ván đấu'**: Toàn bộ thông tin các ván cờ đã thi đấu, thời gian, kết quả và chuỗi nước đi định dạng chuẩn thi đấu quốc tế **PGN** đều được lưu trữ an toàn trong SQLite. Người chơi có thể tải file PGN về máy.  
  > Em xin kết thúc phần Demo và sẵn sàng bước sang phần phản biện thảo luận cùng Thầy Cô!"

* **👉 THAO TÁC THỰC HIỆN TRÊN MÀN HÌNH:**  
  Client 2 (Bob): Nhấp nút **'Lịch sử ván đấu'** ở cột trái ➔ Mở hộp thoại danh sách các ván cờ ➔ Chỉ nút tải PGN ➔ Đóng cửa sổ, kết thúc demo đúng 4:00.

* **✅ KẾT QUẢ ĐẠT ĐƯỢC:**  
  Khép lại vòng đời hoàn chỉnh của ván cờ: Lưu trữ CSDL chuẩn mực, bảo đảm tính toàn vẹn dữ liệu.

---

## PHẦN 3: BỘ CÂU HỎI VẤN ĐÁP PHẢN BIỆN CỦA HỘI ĐỒNG (4:00 – 7:00 · ĐÚNG 3 PHÚT)

### CÂU HỎI 1: "Tại sao nước đi cờ lại dùng TCP mà đồng hồ đếm ngược lại dùng UDP?"
*(Trọng tâm kiểm tra: So sánh bản chất truyền thông giữa TCP và UDP)*

* **👉 CÂU TRẢ LỜI CHUẨN 10 ĐIỂM:**  
  • **Nước đi cờ (MOVE)** là dữ liệu quyết định thắng thua, bắt buộc phải bảo đảm 100% không mất mát và đúng thứ tự ➔ Bắt buộc dùng **TCP (SOCK_STREAM)** có kiểm soát luồng và cơ chế ACK.  
  • **Đồng hồ (CLOCK)** cần tần số cập nhật rất cao (5 lần/giây - 5Hz) để kim giây nhảy mượt mà. Nếu gửi qua TCP, khi mạng lag cơ chế Retransmit sẽ làm ứ đọng bộ đệm (Buffer Bloat), gây nghẽn đường truyền nước cờ. Dùng **UDP (SOCK_DGRAM)** gói tin cực nhẹ, bắn đi ngay, độ trễ < 5ms và không bao giờ làm nghẽn mạng.

---

### CÂU HỎI 2: "UDP có thể bị mất gói (packet loss), vậy lỡ rớt mạng mất gói tin UDP thì người chơi có bị xử thua oan không?"
*(Trọng tâm kiểm tra: Nguyên lý Server-Authoritative trong tính toán thời gian)*

* **👉 CÂU TRẢ LỜI CHUẨN 10 ĐIỂM:**  
  **Dạ hoàn toàn KHÔNG THỂ bị thua oan!** Vì 2 lý do:  
  1. **Server là trọng tài thời gian độc quyền (Server-Authoritative):** Đồng hồ chính thức chạy 100% trên Server bằng hàm phần cứng `time.monotonic()`. Quyết định hết giờ (Timeout) là do Server phát hiện, không phụ thuộc vào gói tin gửi tới Client.  
  2. **Cơ chế bù đắp tự nhiên của UDP 5Hz:** Gói UDP gửi tới Client chỉ để hiển thị mượt trên màn hình. Nếu rớt 1 gói UDP, chỉ đúng **0.2 giây sau** gói mới đã tới đè lên ngay, người chơi thậm chí không nhận ra có gói vừa bị rớt!

---

### CÂU HỎI 3: "Tại sao trong code đồng hồ lại có cả TCP dự phòng mỗi 2 giây?"
*(Trọng tâm kiểm tra: Kỹ thuật tối ưu mạng UDP Fast-path & TCP Checkpoint)*

* **👉 CÂU TRẢ LỜI CHUẨN 10 ĐIỂM:**  
  Dạ đây là kỹ thuật đồng bộ 2 tầng: **UDP 5Hz là tuyến chính** để kim giây hiển thị mượt mà; còn **TCP định kỳ 2 giây/lần là tuyến chốt chặn (Checkpoint Reconciliation)** đóng vai trò dự phòng nếu Client chơi trong mạng Wi-Fi bị tường lửa (Firewall) chặn cổng UDP, hoặc để triệt tiêu hiện tượng lệch đồng hồ tích lũy (Clock Drift) giữa 2 máy.

---

### CÂU HỎI 4: "Cơ chế 60s Reconnect hoạt động ra sao? Người chơi đăng nhập lại bằng cách nào?"
*(Trọng tâm kiểm tra: Khôi phục phiên và chịu lỗi hệ thống - Fault tolerance)*

* **👉 CÂU TRẢ LỜI CHUẨN 10 ĐIỂM:**  
  • Khi Client đứt kết nối (hoặc bấm Rời ván & Đăng xuất), Server bắt ngoại lệ socket đóng (EOF/OSError) và ghi nhận `session.disconnected = now`. Server **giữ nguyên trạng thái phòng trong RAM trong 60 giây**, phía đối thủ thấy trạng thái 'Mất kết nối (Chờ 60s)'.  
  • Client tự động bật ngay màn hình Đăng nhập (tên và mật khẩu đã điền sẵn). Khi người chơi bấm **Đăng nhập** lại: Server nhận diện tài khoản đã có session đang chờ, liền **nối socket mới vào session cũ**, phát lại chuỗi FEN và đồng hồ để người chơi tiếp tục ván đấu ngay lập tức. Quá 60s Server mới xử thua.

---

### CÂU HỎI 5: "Hiện tượng Dính gói (Coalescing) và Phân mảnh (Fragmentation) trong TCP được nhóm giải quyết thế nào?"
*(Trọng tâm kiểm tra: Đóng gói dữ liệu tầng ứng dụng - Application-level Framing)*

* **👉 CÂU TRẢ LỜI CHUẨN 10 ĐIỂM:**  
  TCP là giao thức hướng luồng (Stream-oriented), không có ranh giới giữa các thông điệp JSON. Nhóm giải quyết bằng giao thức đóng gói **Length-Prefix 4 byte Big-Endian** (`chessnet/protocol.py`):  
  • Mỗi gói tin luôn gửi 4 byte đầu tiên chứa độ dài N của dữ liệu JSON phía sau.  
  • Phía nhận dùng vòng lặp `exact(sock, 4)` để đọc đủ 4 byte kích thước, sau đó gọi `exact(sock, N)` đọc đủ đúng N byte thì mới giải mã JSON. Nhờ đó gói tin không bao giờ bị cắt vụn hoặc dính vào nhau.

---

### CÂU HỎI 6: "Mật khẩu người dùng được lưu trữ và bảo mật trong cơ sở dữ liệu SQLite như thế nào?"
*(Trọng tâm kiểm tra: Bảo mật thông tin xác thực và mã hóa)*

* **👉 CÂU TRẢ LỜI CHUẨN 10 ĐIỂM:**  
  Mật khẩu **tuyệt đối KHÔNG lưu ở dạng văn bản thuần (plain text)**. Nhóm sử dụng chuẩn bảo mật quốc tế **PBKDF2-HMAC-SHA256** với **120.000 vòng lặp băm** kết hợp với chuỗi **Salt ngẫu nhiên 16 byte** cho từng tài khoản (`secrets.token_bytes(16)`). Khi so sánh mật khẩu, hệ thống dùng hàm `secrets.compare_digest()` để chống tấn công phân tích thời gian (Timing Attacks).

---

*Chúc Nhóm trưởng Nguyễn Trọng Trình và các thành viên Nhóm 2 bảo vệ đạt kết quả xuất sắc 10/10!*  
*Mã nguồn chính thức đã đồng bộ tại: https://github.com/aekjnds12412/Chess_Nhom_2*
