import json
from pathlib import Path
import socket
import struct
import tempfile
import threading
import time
import unittest

import chess
from chessnet.protocol import encode, receive, MAX_FRAME
from chessnet.server import GameServer
from chessnet.client import NetworkClient


class Wire:
    def __init__(self, server, name=None, token=None, password='test1234', register=True):
        self.sock=socket.create_connection(('127.0.0.1',server.port),timeout=3)
        self.sock.settimeout(3)
        self.send('RESUME',token=token) if token else self.send('LOGIN',name=name,password=password,register=register)
        self.welcome=self.next('WELCOME','ERROR')
        self.token=self.welcome.get('token')
        self.server=server

    def send(self,kind,**kwargs):
        self.sock.sendall(encode(dict(type=kind,**kwargs)))

    def next(self,*kinds):
        end=time.monotonic()+4
        while time.monotonic()<end:
            msg=receive(self.sock)
            if msg['type'] in kinds:
                return msg
        raise AssertionError('Message not received: '+str(kinds))

    def close(self):
        try:
            self.sock.shutdown(socket.SHUT_RDWR)
        except OSError:
            pass
        self.sock.close()


class FramingTests(unittest.TestCase):
    def test_fragmentation_and_coalescing(self):
        left,right=socket.socketpair()
        def writer():
            for byte in encode({'type':'CHAT','text':'Xin chào ♟'}):
                left.sendall(bytes([byte]))
            left.sendall(encode({'type':'PING'})+encode({'type':'PING','n':2}))
        thread=threading.Thread(target=writer)
        thread.start()
        try:
            self.assertEqual(receive(right)['text'],'Xin chào ♟')
            self.assertEqual(receive(right)['type'],'PING')
            self.assertEqual(receive(right)['n'],2)
        finally:
            thread.join()
            left.close()
            right.close()

    def test_frame_limits_and_shape(self):
        for frame in (struct.pack('!I',MAX_FRAME+1),struct.pack('!I',0),struct.pack('!I',2)+b'[]'):
            left,right=socket.socketpair()
            left.sendall(frame)
            with self.assertRaises(ValueError):
                receive(right)
            left.close()
            right.close()


class NetworkTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory()
        self.server=GameServer('127.0.0.1',0,0,Path(self.tmp.name)/'games.db').start()
        self.clients=[]

    def tearDown(self):
        for client in self.clients:
            client.close()
        self.server.stop()
        self.tmp.cleanup()

    def user(self,name,**kwargs):
        client=Wire(self.server,name,**kwargs)
        self.clients.append(client)
        return client

    def game(self):
        white,black=self.user('White'),self.user('Black')
        white.send('CREATE',title='Test',control='5+0')
        room=white.next('STATE')['id']
        black.send('JOIN',id=room)
        black.next('STATE')
        white.next('STATE')
        return white,black,self.server.rooms[room]

    def move(self,client,uci):
        client.send('MOVE',**{'from':uci[:2],'to':uci[2:4],'promotion':uci[4:]})
        return client.next('STATE','ERROR')

    def wait_for(self,predicate,seconds=2):
        end=time.monotonic()+seconds
        while time.monotonic()<end:
            if predicate():
                return
            time.sleep(.02)
        self.fail('Timed out waiting for state')

    def test_authentication_and_no_plaintext_password(self):
        a=self.user('Alice')
        self.assertEqual(a.welcome['type'],'WELCOME')
        wrong=self.user('Alice',password='wrong',register=False)
        self.assertEqual(wrong.welcome['type'],'ERROR')
        with self.server.store.lock:
            row=self.server.store.db.execute('SELECT salt,password FROM users').fetchone()
        self.assertEqual(len(row[0]),16)
        self.assertNotEqual(row[1],b'test1234')

    def test_illegal_move_turn_and_spectator(self):
        w,b,r=self.game()
        self.assertEqual(self.move(w,'e2e5')['type'],'ERROR')
        self.assertEqual(self.move(b,'e7e5')['type'],'ERROR')
        watcher=self.user('Viewer')
        watcher.send('SPECTATE',id=r.id)
        self.assertEqual(watcher.next('STATE')['role'],-1)
        w.next('STATE')
        b.next('STATE')
        self.assertEqual(self.move(watcher,'e2e4')['type'],'ERROR')
        state=self.move(w,'e2e4')
        self.assertEqual(state['moves'][0]['san'],'e4')
        self.assertEqual(watcher.next('STATE')['fen'],state['fen'])
        self.assertEqual(b.next('STATE')['fen'],state['fen'])

    def test_checkmate_history_and_elo(self):
        w,b,r=self.game()
        for actor,uci in [(w,'f2f3'),(b,'e7e5'),(w,'g2g4'),(b,'d8h4')]:
            self.move(actor,uci)
            (b if actor is w else w).next('STATE')
        self.assertEqual(r.result,'0-1')
        self.assertEqual(r.reason,'Chiếu hết')
        self.assertEqual(self.server.store.rating('White'),1188)
        w.send('HISTORY')
        history=w.next('HISTORY')['games']
        self.assertEqual(history[0]['result'],'0-1')
        w.send('PGN',id=history[0]['id'])
        self.assertIn('Qh4#',w.next('PGN')['pgn'])

    def test_special_moves_castle_en_passant_promotion(self):
        w,b,r=self.game()
        cases=[('r3k2r/8/8/8/8/8/8/R3K2R w KQkq - 0 1','e1g1',chess.G1,chess.KING),
               ('4k3/8/8/3pP3/8/8/8/4K3 w - d6 0 1','e5d6',chess.D6,chess.PAWN),
               ('4k3/P7/8/8/8/8/8/4K3 w - - 0 1','a7a8n',chess.A8,chess.KNIGHT)]
        for fen,uci,target,piece_type in cases:
            with self.server.lock:
                r.board=chess.Board(fen)
                r.status='playing'
                r.tick=time.monotonic()
            state=self.move(w,uci)
            b.next('STATE')
            self.assertEqual(state['type'],'STATE')
            self.assertEqual(r.board.piece_at(target).piece_type,piece_type)
        self.assertEqual(r.result,'1/2-1/2')

    def test_reconnect_preserves_fen_clock_and_role(self):
        w,b,r=self.game()
        self.move(w,'e2e4')
        b.next('STATE')
        old_fen=r.board.fen()
        token=w.token
        w.close()
        self.wait_for(lambda:self.server.sessions[token].sock is None)
        resumed=Wire(self.server,token=token)
        self.clients.append(resumed)
        state=resumed.next('STATE')
        self.assertEqual(state['fen'],old_fen)
        self.assertEqual(state['role'],0)
        self.assertGreater(state['clocks'][1],295)
        self.assertEqual(self.move(b,'e7e5')['type'],'STATE')

    def test_expired_reconnect_loses_and_cannot_resume(self):
        w,b,r=self.game()
        token=w.token
        w.close()
        self.wait_for(lambda:self.server.sessions[token].sock is None)
        with self.server.lock:
            self.server.sessions[token].disconnected=time.monotonic()-61
        self.wait_for(lambda:r.status=='finished')
        self.assertEqual(r.result,'0-1')
        resumed=Wire(self.server,token=token)
        self.clients.append(resumed)
        self.assertEqual(resumed.welcome['type'],'ERROR')
        again=self.user('White',register=False)
        self.assertEqual(again.welcome['type'],'WELCOME')

    def test_clock_timeout_and_increment(self):
        w,b,r=self.game()
        with self.server.lock:
            r.control='10+5'
            r.clocks=[10,10]
        self.move(w,'e2e4')
        b.next('STATE')
        self.assertGreater(r.clocks[0],14)
        with self.server.lock:
            r.clocks[1]=.02
        self.wait_for(lambda:r.status=='finished')
        self.assertEqual(r.result,'1-0')

    def test_udp_discovery_clock_and_emoji(self):
        w,b,r=self.game()
        udp=socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
        udp.bind(('127.0.0.1',0))
        udp.settimeout(3)
        target=('127.0.0.1',self.server.udp_port)
        def send(obj):
            udp.sendto(json.dumps(obj).encode(),target)
        def next_packet(kind):
            for _ in range(30):
                msg=json.loads(udp.recvfrom(4096)[0])
                if msg['type']==kind:
                    return msg
            self.fail('No UDP '+kind)
        try:
            send({'type':'DISCOVER','app':'PIXEL_CHESS_V1'})
            self.assertEqual(next_packet('SERVER')['port'],self.server.port)
            send({'type':'REGISTER','token':w.token})
            self.assertEqual(next_packet('CLOCK')['id'],r.id)
            send({'type':'EMOJI','token':w.token,'emoji':'👍'})
            self.assertEqual(next_packet('EMOJI')['name'],'White')
            # Untrusted malformed packets must not kill the UDP thread.
            send([])
            send({'type':'REGISTER','token':[]})
            send({'type':'DISCOVER','app':'PIXEL_CHESS_V1'})
            self.assertEqual(next_packet('SERVER')['port'],self.server.port)
        finally:
            udp.close()

    def test_matchmaking_multiple_rooms_and_private_lobby(self):
        a,b,c,d=[self.user(n) for n in ('One','Two','Three','Four')]
        a.send('MATCH',control='3+0')
        a.next('QUEUED')
        b.send('MATCH',control='3+0')
        room1=b.next('STATE')['id']
        c.send('CREATE',control='10+5',private=True)
        room2=c.next('STATE')['id']
        d.send('JOIN',id=room2)
        d.next('STATE')
        c.next('STATE')
        self.assertNotEqual(room1,room2)
        self.move(a,'e2e4')
        self.assertEqual(self.server.rooms[room2].board.fen(),chess.STARTING_FEN)
        d.send('LOBBY')
        while True:
            listing=d.next('LOBBY')
            if len(listing['rooms'])==1:
                break
        self.assertNotIn(room2,[r['id'] for r in listing['rooms']])

    def test_chat_draw_and_room_leave(self):
        w,b,r=self.game()
        w.send('CHAT',text='Chào bạn!')
        self.assertEqual(w.next('STATE')['messages'][-1]['text'],'Chào bạn!')
        b.next('STATE')
        w.send('DRAW')
        w.next('STATE')
        b.next('STATE')
        b.send('DRAW')
        self.assertEqual(b.next('STATE')['result'],'1/2-1/2')
        w.send('LEAVE')
        w.next('LEFT')
        self.assertIsNone(self.server.sessions[w.token].room)

    def test_claim_draw_and_resign(self):
        w,b,r=self.game()
        w.send('CLAIM_DRAW')
        self.assertEqual(w.next('ERROR')['type'],'ERROR')
        w.send('RESIGN')
        self.assertEqual(w.next('STATE')['result'],'0-1')

    def test_real_client_heartbeat_and_auto_reconnect(self):
        events=[]
        lock=threading.Lock()
        def emit(event):
            with lock:
                events.append(event)
        client=NetworkClient(emit)
        try:
            client.connect('127.0.0.1',self.server.port,'RealClient','password',True)
            self.wait_for(lambda:any(e['type']=='WELCOME' for e in events))
            token=client.token
            client.disconnect_transport()
            self.wait_for(lambda:sum(e['type']=='WELCOME' for e in events)>=2,4)
            self.assertEqual(client.token,token)
            self.assertTrue(client.connected)
            client.send('PING',at=123)
            self.wait_for(lambda:any(e['type']=='PONG' for e in events))
        finally:
            client.close()


if __name__=='__main__':
    unittest.main()
