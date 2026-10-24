"""A frame is a network-order uint32 length followed by UTF-8 JSON."""
import json
import struct

MAX_FRAME = 65536


def encode(message):
    payload = json.dumps(message, ensure_ascii=False, separators=(',', ':')).encode('utf-8')
    if not 0 < len(payload) <= MAX_FRAME:
        raise ValueError('Frame quá lớn')
    return struct.pack('!I', len(payload)) + payload


def exact(sock, count):
    chunks = bytearray()
    while len(chunks) < count:
        chunk = sock.recv(count - len(chunks))
        if not chunk:
            raise EOFError('Connection closed')
        chunks.extend(chunk)
    return bytes(chunks)


def receive(sock):
    size, = struct.unpack('!I', exact(sock, 4))
    if not 0 < size <= MAX_FRAME:
        raise ValueError('Invalid frame size')
    result = json.loads(exact(sock, size).decode('utf-8'))
    if not isinstance(result, dict) or not isinstance(result.get('type'), str):
        raise ValueError('Invalid message')
    return result
