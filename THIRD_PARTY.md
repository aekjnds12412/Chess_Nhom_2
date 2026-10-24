# Thành phần bên thứ ba

## python-chess / chess 1.11.2

- Tác giả: Niklas Fiekas và những người đóng góp.
- Nguồn: https://github.com/niklasf/python-chess
- Tài liệu: https://python-chess.readthedocs.io/en/latest/
- Giấy phép: **GNU General Public License v3 hoặc mới hơn**.
- Mã nguồn nguyên bản kèm trong `vendor/chess/`; giấy phép nằm trong `vendor/chess-1.11.2.dist-info/licenses/LICENSE.txt`.

Việc phân phối ứng dụng kết hợp với thư viện này cần tuân thủ GPL. Mã riêng của Pixel Chess trong bản bàn giao này cũng được cung cấp theo GPL-3.0-or-later. Bộ ảnh do người dùng cung cấp có quyền sử dụng độc lập, không được tự động cấp lại giấy phép bởi tài liệu này.

## Pillow

- Nguồn: https://python-pillow.github.io/
- Dùng để nạp/resize sprite theo nearest-neighbor và tách sprite sheet trong công cụ phát triển.
- Cài từ môi trường Python hoặc `requirements.txt`, không chép mã Pillow vào dự án.

## Asset người dùng

`assets/original.png` là bản sao của `hQrS57.png` được cung cấp trong yêu cầu. Các file `w*.png` và `b*.png` là quân được cắt từ ảnh đó, chỉ bỏ nền đen và đặt trên canvas trong suốt cùng đường chân quân. Bàn cờ và giao diện được vẽ bằng Tkinter để co giãn theo cửa sổ.
