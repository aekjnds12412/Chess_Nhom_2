"""Background networking; GUI callbacks only enqueue events on the Tk thread."""
import json
import queue
import random
import socket
import threading
import time
import uuid

import chess
from .protocol import encode, receive


def discover(timeout=1.4):
    results={}
    with socket.socket(socket.AF_INET,socket.SOCK_DGRAM) as sock:
        sock.setsockopt(socket.SOL_SOCKET,socket.SO_BROADCAST,1)
        sock.settimeout(.2)
        payload=json.dumps({'type':'DISCOVER','app':'PIXEL_CHESS_V1'}).encode()
        for address in ('255.255.255.255','127.0.0.1'):
            try:
                sock.sendto(payload,(address,9999))
            except OSError:
                pass
        end=time.monotonic()+timeout
        while time.monotonic()<end:
            try:
                data,addr=sock.recvfrom(4096)
                item=json.loads(data)
                if isinstance(item,dict) and item.get('type')=='SERVER' and item.get('app')=='PIXEL_CHESS_V1':
                    item['host']=addr[0]
                    results[(addr[0],item['port'])]=item
            except (socket.timeout, ValueError, TypeError, KeyError, OSError):
                pass
    return list(results.values())


class NetworkClient:
    def __init__(self, callback):
        self.callback=callback
        self.sock=None
        self.udp=None
        self.token=None
        self.connected=False
        self.stop_event=threading.Event()
        self.send_lock=threading.Lock()
        self.thread=None
        self.udp_port=9999

    def connect(self, host, port, name='', password='', register=False, token=None):
        self.host,self.port=host,int(port)
        self.token=token
        self.credentials={'type':'RESUME','token':token} if token else {'type':'LOGIN','name':name,'password':password,'register':register}
        self.thread=threading.Thread(target=self.run,daemon=True)
        self.thread.start()

    def emit(self, kind, **kwargs):
        self.callback(dict(type=kind,**kwargs))

    def run(self):
        first=True
        deadline=None
        while not self.stop_event.is_set():
            sock=None
            try:
                sock=socket.create_connection((self.host,self.port),timeout=3)
                sock.settimeout(8)
                sock.sendall(encode(self.credentials if first else {'type':'RESUME','token':self.token}))
                welcome=receive(sock)
                if welcome['type']!='WELCOME':
                    self.emit('AUTH_ERROR',message=welcome.get('message','Không thể đăng nhập.'))
                    break
                self.sock=sock
                self.connected=True
                self.token=welcome['token']
                self.peer_ip=sock.getpeername()[0]
                self.udp_port=welcome['udp_port']
                self.setup_udp()
                self.callback(welcome)
                first=False
                deadline=None
                heartbeat=threading.Thread(target=self.heartbeat,args=(sock,),daemon=True)
                heartbeat.start()
                while not self.stop_event.is_set():
                    self.callback(receive(sock))
            except (OSError,EOFError,ValueError,KeyError) as exc:
                if self.stop_event.is_set():
                    break
                if first:
                    self.emit('AUTH_ERROR',message='Không kết nối được server: '+str(exc))
                    break
                deadline=deadline or time.monotonic()+58
                if time.monotonic()>deadline:
                    self.emit('AUTH_ERROR',message='Đã hết thời gian kết nối lại. Hãy đăng nhập lại.')
                    break
                self.emit('RECONNECTING',remaining=max(0,int(deadline-time.monotonic())))
            finally:
                self.connected=False
                if self.sock is sock:
                    self.sock=None
                if sock:
                    sock.close()
            if self.stop_event.wait(1):
                break
        if self.udp:
            self.udp.close()

    def setup_udp(self):
        if not self.udp:
            self.udp=socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
            self.udp.bind(('0.0.0.0',0))
            self.udp.settimeout(.5)
            threading.Thread(target=self.udp_loop,daemon=True).start()
        self.send_udp('REGISTER')

    def udp_loop(self):
        while not self.stop_event.is_set():
            try:
                data,addr=self.udp.recvfrom(8192)
                if addr!=(self.peer_ip,self.udp_port):
                    continue
                msg=json.loads(data.decode('utf-8'))
                if isinstance(msg,dict) and msg.get('type') in ('CLOCK','EMOJI'):
                    self.callback(msg)
            except (socket.timeout,ValueError,UnicodeError,AttributeError):
                pass
            except OSError:
                break

    def heartbeat(self, sock):
        while not self.stop_event.wait(3):
            if self.sock is not sock:
                break
            self.send('PING',at=time.monotonic())
            self.send_udp('REGISTER')

    def send(self, kind, **kwargs):
        with self.send_lock:
            sock=self.sock
            if not sock or not self.connected:
                return False
            try:
                sock.sendall(encode(dict(type=kind,**kwargs)))
                return True
            except OSError:
                try:
                    sock.shutdown(socket.SHUT_RDWR)
                except OSError:
                    pass
                return False

    def send_udp(self, kind, **kwargs):
        if self.udp and self.token:
            try:
                self.udp.sendto(json.dumps(dict(type=kind,token=self.token,**kwargs),ensure_ascii=False).encode(),(self.peer_ip,self.udp_port))
                return True
            except OSError:
                pass
        return False

    def disconnect_transport(self):
        """Used by the demo menu to exercise the real reconnect mechanism."""
        if self.sock:
            try:
                self.sock.shutdown(socket.SHUT_RDWR)
            except OSError:
                pass

    def close(self):
        self.stop_event.set()
        self.disconnect_transport()
        if self.udp:
            self.udp.close()


VALUES={chess.PAWN:100,chess.KNIGHT:320,chess.BISHOP:330,chess.ROOK:500,chess.QUEEN:900,chess.KING:0}


def evaluate(board):
    outcome=board.outcome()
    if outcome:
        return 0 if outcome.winner is None else (100000 if outcome.winner else -100000)
    total=0
    for square,piece in board.piece_map().items():
        center=7-(abs(chess.square_file(square)-3.5)+abs(chess.square_rank(square)-3.5))
        bonus=center*(5 if piece.piece_type in (chess.KNIGHT,chess.BISHOP) else 1)
        if piece.piece_type==chess.PAWN:
            bonus+=(chess.square_rank(square) if piece.color else 7-chess.square_rank(square))*6
        total+=(VALUES[piece.piece_type]+bonus)*(1 if piece.color else -1)
    return total


def choose_move(board):
    """Two-ply minimax: deliberately lightweight practice opponent, not Stockfish."""
    side=1 if board.turn else -1
    best=-float('inf')
    selected=None
    moves=list(board.legal_moves)
    random.shuffle(moves)
    for move in moves:
        board.push(move)
        responses=list(board.legal_moves)
        if not responses:
            score=side*evaluate(board)
        else:
            score=float('inf')
            for reply in responses:
                board.push(reply)
                value=side*evaluate(board)
                board.pop()
                score=min(score,value)
                if score<best:
                    break
        board.pop()
        if score>best:
            best,selected=score,move
    return selected


class PracticeBot:
    def __init__(self,host,port,room):
        self.room=room
        self.events=queue.Queue()
        self.client=NetworkClient(self.events.put)
        self.client.connect(host,port,'PixelBot_'+uuid.uuid4().hex[:7],uuid.uuid4().hex,register=True)
        self.stop_event=threading.Event()
        self.last_fen=None
        threading.Thread(target=self.run,daemon=True).start()

    def run(self):
        while not self.stop_event.is_set():
            try:
                event=self.events.get(timeout=.5)
            except queue.Empty:
                continue
            if event['type']=='WELCOME':
                self.client.send('JOIN',id=self.room)
            elif event['type']=='STATE' and event['status']=='playing' and event['role']==event['turn'] and event['fen']!=self.last_fen:
                self.last_fen=event['fen']
                if event.get('offer'):
                    self.client.send('DRAW')
                    continue
                board=chess.Board(event['fen'])
                move=choose_move(board)
                if move and not self.stop_event.wait(.45):
                    self.client.send('MOVE',**{'from':chess.square_name(move.from_square),'to':chess.square_name(move.to_square),
                                             'promotion':chess.piece_symbol(move.promotion) if move.promotion else ''})
            elif event['type']=='STATE' and event.get('offer') and event['status']=='playing':
                self.client.send('DRAW')

    def close(self):
        self.stop_event.set()
        self.client.send('LEAVE')
        self.client.close()
