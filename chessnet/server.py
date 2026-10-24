import argparse
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass, field
import json
import logging
from pathlib import Path
import secrets
import socket
import threading
import time

import chess
import chess.pgn
from .protocol import encode, receive
from .storage import Store

LOG = logging.getLogger('chessnet')
CONTROLS = {'3+0': (180, 0), '5+0': (300, 0), '10+5': (600, 5)}


@dataclass
class Session:
    token: str
    name: str
    sock: object = None
    room: str = None
    disconnected: float = None
    seen: float = field(default_factory=time.monotonic)
    udp: object = None
    ip: str = ''
    send_lock: object = field(default_factory=threading.Lock)
    last_chat: float = 0

    def send(self, message):
        with self.send_lock:
            if self.sock:
                try:
                    self.sock.sendall(encode(message))
                except OSError:
                    pass


@dataclass
class Room:
    id: str
    title: str
    control: str
    private: bool = False
    rated: bool = True
    players: list = field(default_factory=list)
    watchers: set = field(default_factory=set)
    board: object = field(default_factory=chess.Board)
    moves: list = field(default_factory=list)
    messages: list = field(default_factory=list)
    clocks: list = field(default_factory=list)
    status: str = 'waiting'
    result: str = '*'
    reason: str = ''
    tick: float = field(default_factory=time.monotonic)
    offer: str = None
    revision: int = 0
    finished_at: float = None


class GameServer:
    def __init__(self, host='0.0.0.0', port=8765, udp_port=9999, db_path='data/chess.db', reconnect_seconds=60):
        self.host, self.port, self.udp_port = host, port, udp_port
        self.reconnect_seconds = reconnect_seconds
        Path(db_path).parent.mkdir(parents=True, exist_ok=True)
        self.store = Store(db_path)
        self.sessions, self.rooms, self.queue = {}, {}, {}
        self.lock = threading.RLock()
        self.stop_event = threading.Event()
        self.pool = ThreadPoolExecutor(max_workers=128, thread_name_prefix='chess-client')
        self.slots = threading.BoundedSemaphore(128)
        self.threads = []
        self.connections = set()

    def start(self):
        self.tcp = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            self.tcp.bind((self.host, self.port))
            self.port = self.tcp.getsockname()[1]
            self.tcp.listen(128)
            self.tcp.settimeout(.5)
            self.udp = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            self.udp.bind((self.host, self.udp_port))
            self.udp_port = self.udp.getsockname()[1]
            self.udp.settimeout(.5)
        except OSError:
            self.tcp.close()
            if hasattr(self, 'udp'):
                self.udp.close()
            self.store.close()
            self.pool.shutdown(wait=False)
            raise
        for target in (self.accept_loop, self.udp_loop, self.clock_loop):
            thread = threading.Thread(target=target, daemon=True)
            thread.start()
            self.threads.append(thread)
        return self

    def accept_loop(self):
        while not self.stop_event.is_set():
            try:
                sock, addr = self.tcp.accept()
                sock.settimeout(15)
                if not self.slots.acquire(blocking=False):
                    sock.close()
                    continue
                with self.lock:
                    self.connections.add(sock)
                self.pool.submit(self.client_loop, sock, addr)
            except socket.timeout:
                continue
            except OSError:
                break

    def client_loop(self, sock, addr):
        session = None
        try:
            hello = receive(sock)
            with self.lock:
                token = hello.get('token')
                if hello['type'] == 'RESUME':
                    session = self.sessions.get(token) if isinstance(token, str) else None
                    if not session or (session.disconnected is not None and time.monotonic()-session.disconnected > self.reconnect_seconds):
                        raise ValueError('Phiên đã hết hạn. Hãy đăng nhập lại.')
                    if session.sock:
                        raise ValueError('Phiên đang kết nối ở nơi khác.')
                elif hello['type'] == 'LOGIN':
                    name, _ = self.store.authenticate(hello.get('name'), hello.get('password'), hello.get('register') is True)
                    if any(s.name.casefold() == name.casefold() and (s.sock or (s.disconnected is not None and time.monotonic()-s.disconnected <= self.reconnect_seconds)) for s in self.sessions.values()):
                        raise ValueError('Tài khoản có phiên đang mở. Khôi phục phiên hoặc chờ 60 giây.')
                    session = Session(secrets.token_urlsafe(32), name)
                    self.sessions[session.token] = session
                else:
                    raise ValueError('Cần đăng nhập trước.')
                session.sock, session.ip = sock, addr[0]
                session.disconnected, session.seen = None, time.monotonic()
                session.send({'type':'WELCOME', 'token':session.token, 'name':session.name,
                              'elo':self.store.rating(session.name), 'udp_port':self.udp_port})
                self.lobby()
                if session.room and session.room in self.rooms:
                    self.broadcast_room(self.rooms[session.room])
            while not self.stop_event.is_set():
                message = receive(sock)
                with self.lock:
                    session.seen = time.monotonic()
                    try:
                        self.handle(session, message)
                    except (ValueError, KeyError, TypeError) as exc:
                        session.send({'type':'ERROR', 'message':str(exc)})
        except (ValueError, KeyError, TypeError, json.JSONDecodeError) as exc:
            try:
                sock.sendall(encode({'type':'ERROR','message':str(exc)}))
            except OSError:
                pass
        except (OSError, EOFError):
            pass
        except Exception:
            LOG.exception('Client handler failed')
        finally:
            with self.lock:
                self.connections.discard(sock)
                if session and session.sock is sock:
                    session.sock = None
                    session.disconnected = time.monotonic()
                    session.udp = None
                    self.queue.pop(session.token, None)
                    if session.room in self.rooms:
                        self.broadcast_room(self.rooms[session.room])
                    self.lobby()
            sock.close()
            self.slots.release()

    def room_for(self, s):
        room = self.rooms.get(s.room)
        if not room:
            raise ValueError('Bạn chưa ở trong phòng.')
        return room

    def lobby(self, session=None):
        message = {'type':'LOBBY', 'online':sum(s.sock is not None for s in self.sessions.values()),
                   'rooms':[{'id':r.id,'title':r.title,'control':r.control,'status':r.status,
                             'players':len(r.players),'watchers':len(r.watchers)} for r in self.rooms.values() if not r.private]}
        for s in ([session] if session else list(self.sessions.values())):
            s.send(message)

    def snapshot(self, r):
        players = []
        for token in r.players:
            s = self.sessions[token]
            players.append({'name':s.name,'elo':self.store.rating(s.name),'connected':s.sock is not None})
        return {'type':'STATE','id':r.id,'title':r.title,'control':r.control,'private':r.private,
                'players':players,'player_tokens':[], 'watchers':len(r.watchers),
                'fen':r.board.fen(),'legal':[m.uci() for m in r.board.legal_moves] if r.status=='playing' else [],
                'moves':r.moves,'clocks':r.clocks,'turn':0 if r.board.turn else 1,
                'status':r.status,'result':r.result,'reason':r.reason,'check':r.board.is_check(),
                'offer':self.sessions[r.offer].name if r.offer in self.sessions else None,
                'messages':r.messages[-60:],'revision':r.revision}

    def broadcast_room(self, r):
        state = self.snapshot(r)
        for token in r.players + list(r.watchers):
            if token in self.sessions and self.sessions[token].room == r.id:
                self.sessions[token].send(dict(state, role=r.players.index(token) if token in r.players else -1))

    def settle(self, r, now=None):
        now = time.monotonic() if now is None else now
        if r.status == 'playing':
            side = 0 if r.board.turn else 1
            r.clocks[side] = max(0, r.clocks[side] - (now-r.tick))
            if r.clocks[side] <= 0:
                winner = not r.board.turn
                result = '1/2-1/2' if r.board.has_insufficient_material(winner) else ('1-0' if winner else '0-1')
                self.finish(r, result, 'Hết thời gian')
        r.tick = now

    def finish(self, r, result, reason):
        if r.status != 'playing':
            return
        r.status, r.result, r.reason, r.finished_at = 'finished', result, reason, time.monotonic()
        r.revision += 1
        game = chess.pgn.Game.from_board(r.board)
        names = [self.sessions[t].name for t in r.players]
        game.headers.update({'White':names[0],'Black':names[1],'Result':result,'Event':'Pixel Chess','TimeControl':str(CONTROLS[r.control][0])+'+'+str(CONTROLS[r.control][1])})
        self.store.finish(*names, result, reason, str(game), r.rated)
        self.broadcast_room(r)
        self.lobby()

    def leave(self, s):
        self.queue.pop(s.token, None)
        r = self.rooms.get(s.room)
        if r:
            if s.token in r.players and r.status=='playing':
                self.settle(r)
                self.finish(r, '0-1' if r.players.index(s.token)==0 else '1-0', 'Rời phòng')
            if s.token in r.watchers:
                r.watchers.discard(s.token)
            # Keep player identities in completed games for spectators/history.
            if r.status == 'waiting' and s.token in r.players:
                self.rooms.pop(r.id, None)
            else:
                self.broadcast_room(r)
        s.room = None
        s.send({'type':'LEFT'})
        self.lobby()

    def new_room(self, s, msg):
        if s.room:
            raise ValueError('Hãy rời phòng hiện tại trước.')
        if msg.get('control', '5+0') not in CONTROLS:
            raise ValueError('Thời gian không hợp lệ.')
        title = str(msg.get('title', 'Bàn của '+s.name)).strip()[:40] or 'Bàn cờ'
        r = Room(secrets.token_hex(3).upper(), title, msg.get('control','5+0'), msg.get('private') is True,
                 rated=not title.startswith('Luyện tập · '))
        r.players.append(s.token)
        r.clocks = [CONTROLS[r.control][0]] * 2
        self.rooms[r.id] = r
        s.room = r.id
        self.queue.pop(s.token, None)
        return r

    def join(self, s, r, spectate=False):
        if s.room:
            raise ValueError('Hãy rời phòng hiện tại trước.')
        if spectate:
            r.watchers.add(s.token)
        else:
            if r.status != 'waiting' or len(r.players) >= 2:
                raise ValueError('Phòng đã đủ người. Bạn có thể vào xem.')
            r.players.append(s.token)
            r.status, r.tick = 'playing', time.monotonic()
        s.room = r.id
        self.queue.pop(s.token, None)
        self.broadcast_room(r)
        self.lobby()

    def handle(self, s, msg):
        kind = msg['type']
        if kind == 'PING':
            s.send({'type':'PONG','at':msg.get('at')})
        elif kind == 'LOBBY':
            self.lobby(s)
        elif kind == 'HISTORY':
            s.send({'type':'HISTORY','games':self.store.history(s.name),'elo':self.store.rating(s.name)})
        elif kind == 'PGN':
            s.send({'type':'PGN','pgn':self.store.pgn(int(msg.get('id',0)),s.name)})
        elif kind == 'CREATE':
            r = self.new_room(s, msg)
            self.broadcast_room(r)
            self.lobby()
        elif kind in ('JOIN','SPECTATE'):
            r = self.rooms.get(str(msg.get('id','')).upper())
            if not r:
                raise ValueError('Không tìm thấy mã phòng.')
            self.join(s, r, kind=='SPECTATE')
        elif kind == 'MATCH':
            control = msg.get('control','5+0')
            if s.room or control not in CONTROLS:
                raise ValueError('Không thể ghép trận lúc này.')
            self.queue.pop(s.token,None)
            other = next((self.sessions[t] for t,c in self.queue.items() if c==control and self.sessions[t].sock),None)
            if other:
                r = self.new_room(other, {'control':control,'title':'Ghép trận · '+control})
                self.join(s,r)
            else:
                self.queue[s.token] = control
                s.send({'type':'QUEUED'})
        elif kind == 'CANCEL_MATCH':
            self.queue.pop(s.token,None)
            s.send({'type':'QUEUE_CANCELLED'})
        elif kind == 'LEAVE':
            self.leave(s)
        elif kind == 'MOVE':
            r = self.room_for(s)
            self.settle(r)
            if r.status != 'playing' or s.token not in r.players or r.players.index(s.token) != (0 if r.board.turn else 1):
                raise ValueError('Chưa đến lượt bạn.')
            uci = str(msg.get('from',''))+str(msg.get('to',''))+str(msg.get('promotion',''))
            try:
                move = chess.Move.from_uci(uci)
            except ValueError:
                raise ValueError('Nước đi không hợp lệ.')
            if move not in r.board.legal_moves:
                raise ValueError('Nước đi không hợp lệ.')
            san = r.board.san(move)
            side = 0 if r.board.turn else 1
            r.board.push(move)
            r.moves.append({'uci':move.uci(),'san':san})
            r.clocks[side] += CONTROLS[r.control][1]
            r.offer = None
            r.tick = time.monotonic()
            r.revision += 1
            outcome = r.board.outcome()
            if outcome:
                self.finish(r, outcome.result(), {'CHECKMATE':'Chiếu hết','STALEMATE':'Hết nước đi','INSUFFICIENT_MATERIAL':'Không đủ quân chiếu hết','FIVEFOLD_REPETITION':'Lặp thế 5 lần','SEVENTYFIVE_MOVES':'Luật 75 nước'}.get(outcome.termination.name,'Hòa cờ'))
            self.broadcast_room(r)
        elif kind in ('RESIGN','DRAW','CLAIM_DRAW'):
            r = self.room_for(s)
            self.settle(r)
            if r.status != 'playing' or s.token not in r.players:
                raise ValueError('Bạn không phải kỳ thủ đang thi đấu.')
            if kind == 'RESIGN':
                self.finish(r,'0-1' if r.players.index(s.token)==0 else '1-0','Đầu hàng')
            elif kind == 'CLAIM_DRAW':
                if r.players.index(s.token) != (0 if r.board.turn else 1) or not r.board.can_claim_draw():
                    raise ValueError('Chưa đủ điều kiện yêu cầu hòa.')
                self.finish(r,'1/2-1/2','Yêu cầu hòa theo luật')
            elif r.offer and r.offer != s.token:
                self.finish(r,'1/2-1/2','Hai bên đồng ý hòa')
            else:
                r.offer = s.token
                self.broadcast_room(r)
        elif kind == 'CHAT':
            r = self.room_for(s)
            if time.monotonic()-s.last_chat < .5:
                raise ValueError('Bạn gửi tin nhắn quá nhanh.')
            body = str(msg.get('text','')).strip()[:280]
            if body:
                s.last_chat = time.monotonic()
                r.messages.append({'name':s.name,'text':body,'time':time.strftime('%H:%M')})
                r.messages = r.messages[-60:]
                self.broadcast_room(r)
        else:
            raise ValueError('Loại thông điệp không được hỗ trợ.')

    def udp_loop(self):
        while not self.stop_event.is_set():
            try:
                data, addr = self.udp.recvfrom(4096)
                msg = json.loads(data.decode('utf-8'))
                if not isinstance(msg, dict):
                    continue
                if msg.get('type')=='DISCOVER' and msg.get('app')=='PIXEL_CHESS_V1':
                    self.udp.sendto(json.dumps({'type':'SERVER','app':'PIXEL_CHESS_V1','name':socket.gethostname(), 'port':self.port,'udp_port':self.udp_port}).encode(), addr)
                    continue
                with self.lock:
                    token = msg.get('token')
                    s = self.sessions.get(token) if isinstance(token,str) else None
                    if not s or not s.sock or s.ip != addr[0]:
                        continue
                    if msg.get('type')=='REGISTER':
                        s.udp = addr
                    elif msg.get('type')=='EMOJI' and s.udp == addr and msg.get('emoji') in ('👍','🔥','👏','🤔') and time.monotonic()-s.last_chat>.5:
                        s.last_chat=time.monotonic()
                        r=self.rooms.get(s.room)
                        if r:
                            for t in r.players+list(r.watchers):
                                peer=self.sessions[t]
                                if peer.udp:
                                    self.udp.sendto(json.dumps({'type':'EMOJI','name':s.name,'emoji':msg['emoji'],'id':r.id},ensure_ascii=False).encode(),peer.udp)
            except (socket.timeout, ValueError, TypeError, KeyError, UnicodeError):
                continue
            except OSError:
                if self.stop_event.is_set():
                    break

    def clock_loop(self):
        last_tcp = 0
        while not self.stop_event.wait(.2):
            with self.lock:
                now=time.monotonic()
                for r in list(self.rooms.values()):
                    self.settle(r,now)
                    if r.status=='playing':
                        packet={'type':'CLOCK','id':r.id,'clocks':r.clocks,'turn':0 if r.board.turn else 1,'revision':r.revision}
                        for token in r.players+list(r.watchers):
                            s=self.sessions[token]
                            if s.udp:
                                try:
                                    self.udp.sendto(json.dumps(packet).encode(),s.udp)
                                except OSError:
                                    pass
                            if now-last_tcp>=2:
                                if s.room == r.id:
                                    s.send(packet)
                if now-last_tcp>=2:
                    last_tcp=now
                for token,s in list(self.sessions.items()):
                    if s.sock and now-s.seen>12:
                        try:
                            s.sock.shutdown(socket.SHUT_RDWR)
                        except OSError:
                            pass
                    if s.disconnected is not None and now-s.disconnected>self.reconnect_seconds:
                        r=self.rooms.get(s.room)
                        if r and r.status=='playing' and token in r.players:
                            self.finish(r,'0-1' if r.players.index(token)==0 else '1-0','Mất kết nối quá 60 giây')
                        # Retain identities referenced by completed rooms until their cleanup.
                        if r and r.status=='waiting' and token in r.players:
                            self.rooms.pop(r.id,None)
                        if r:
                            r.watchers.discard(token)
                        s.room=None
                        if not any(token in room.players for room in self.rooms.values()):
                            self.sessions.pop(token,None)
                for rid,r in list(self.rooms.items()):
                    if r.finished_at and now-r.finished_at>300 and not any(s.room==rid and s.sock for s in self.sessions.values()):
                        self.rooms.pop(rid,None)

    def stop(self):
        if self.stop_event.is_set():
            return
        self.stop_event.set()
        self.tcp.close()
        self.udp.close()
        with self.lock:
            for sock in list(self.connections):
                try:
                    sock.shutdown(socket.SHUT_RDWR)
                except OSError:
                    pass
                sock.close()
        for t in self.threads:
            t.join(timeout=2)
        self.pool.shutdown(wait=True, cancel_futures=True)
        self.store.close()


def main():
    parser=argparse.ArgumentParser(description='Pixel Chess authoritative TCP/UDP server')
    parser.add_argument('--host',default='0.0.0.0')
    parser.add_argument('--port',type=int,default=8765)
    parser.add_argument('--udp-port',type=int,default=9999)
    parser.add_argument('--db',default='data/chess.db')
    args=parser.parse_args()
    logging.basicConfig(level=logging.INFO)
    server=GameServer(args.host,args.port,args.udp_port,args.db).start()
    print(f'Pixel Chess TCP {server.host}:{server.port} | UDP {server.udp_port}', flush=True)
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        server.stop()
