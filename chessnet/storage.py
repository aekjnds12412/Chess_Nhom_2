import hashlib
import hmac
import os
import sqlite3
import threading
import re


class Store:
    def __init__(self, path):
        self.lock = threading.RLock()
        self.db = sqlite3.connect(str(path), check_same_thread=False)
        self.db.executescript('''
        CREATE TABLE IF NOT EXISTS users(
          name TEXT PRIMARY KEY COLLATE NOCASE, salt BLOB NOT NULL,
          password BLOB NOT NULL);
        CREATE TABLE IF NOT EXISTS games(
          id INTEGER PRIMARY KEY, white TEXT, black TEXT, result TEXT,
          reason TEXT, pgn TEXT, finished TEXT DEFAULT CURRENT_TIMESTAMP);
        ''')
        self.db.commit()

    def authenticate(self, name, password, register=False):
        if not isinstance(name, str) or not re.fullmatch(r'[\w -]{2,24}', name):
            raise ValueError('Tên cần 2–24 ký tự: chữ, số, khoảng trắng hoặc dấu gạch.')
        if not isinstance(password, str) or not 4 <= len(password) <= 128:
            raise ValueError('Mật khẩu cần từ 4 đến 128 ký tự.')
        with self.lock:
            row = self.db.execute('SELECT name,salt,password FROM users WHERE name=?', (name,)).fetchone()
            if register:
                if row:
                    raise ValueError('Tên đã tồn tại. Hãy đăng nhập.')
                salt = os.urandom(16)
                digest = hashlib.pbkdf2_hmac('sha256', password.encode(), salt, 120000)
                self.db.execute('INSERT INTO users(name,salt,password) VALUES(?,?,?)', (name, salt, digest))
                self.db.commit()
                return name
            if not row or not hmac.compare_digest(row[2], hashlib.pbkdf2_hmac('sha256', password.encode(), row[1], 120000)):
                raise ValueError('Tên đăng nhập hoặc mật khẩu không đúng.')
            return row[0]

    def finish(self, white, black, result, reason, pgn):
        with self.lock:
            self.db.execute('INSERT INTO games(white,black,result,reason,pgn) VALUES(?,?,?,?,?)',
                            (white, black, result, reason, pgn))
            self.db.commit()

    def history(self, name):
        with self.lock:
            rows = self.db.execute('SELECT id,white,black,result,reason,finished FROM games WHERE white=? OR black=? ORDER BY id DESC LIMIT 30', (name, name)).fetchall()
            return [dict(zip(('id','white','black','result','reason','finished'), row)) for row in rows]

    def pgn(self, game_id, name):
        with self.lock:
            row = self.db.execute('SELECT pgn FROM games WHERE id=? AND (white=? OR black=?)', (game_id,name,name)).fetchone()
            return row[0] if row else ''

    def close(self):
        with self.lock:
            self.db.close()
