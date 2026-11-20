import sqlite3
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
db_path = ROOT / 'data' / 'chess.db'

if not db_path.exists():
    print(f"Chua tim thay file CSDL tai: {db_path}")
    input("Nhan Enter de thoat...")
    exit()

db = sqlite3.connect(str(db_path))

print("=" * 75)
print("             DANH SÁCH TÀI KHOẢN TRONG FILE DATABASE CHESS.DB")
print("=" * 75)
print(f"{'STT':<5} | {'TÊN TÀI KHOẢN (NAME)':<25} | {'MÃ BĂM MẬT KHẨU (PASSWORD HASH)':<35}")
print("-" * 75)

users = db.execute("SELECT name, hex(password) FROM users").fetchall()
if not users:
    print("Chưa có tài khoản nào được tạo.")
else:
    for idx, (name, pass_hash) in enumerate(users, 1):
        print(f"{idx:<5} | {name:<25} | {pass_hash[:32]}... (32 bytes)")

print("\n" + "=" * 75)
print("             DANH SÁCH CÁC VÁN ĐẤU ĐÃ LƯU TRONG CSDL (GAMES)")
print("=" * 75)
print(f"{'ID':<5} | {'TRẮNG vs ĐEN':<25} | {'KẾT QUẢ':<10} | {'LÝ DO KẾT THÚC':<20}")
print("-" * 75)

games = db.execute("SELECT id, white, black, result, reason FROM games ORDER BY id DESC LIMIT 15").fetchall()
if not games:
    print("Chưa có ván đấu nào hoàn thành.")
else:
    for gid, w, b, res, reason in games:
        vs = f"{w} vs {b}"
        print(f"{gid:<5} | {vs:<25} | {res:<10} | {reason:<20}")

print("=" * 75)
print("\nLƯU Ý QUAN TRỌNG:")
print("- Mật khẩu gốc được mã hóa 1 chiều (PBKDF2-SHA256) nên CHỈ THẤY MÃ BĂM, không thể dịch ngược thành chữ thường.")
print("- Để xem trực quan bằng giao diện đồ họa, bạn có thể tải phần mềm 'DB Browser for SQLite'.")
print("=" * 75)
