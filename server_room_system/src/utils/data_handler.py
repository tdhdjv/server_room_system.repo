import pickle

def encode(protocol:str, data) -> bytes:
    packet = {'protocol': protocol, 'data': data}
    packet_bytes = pickle.dumps(packet)
    return packet_bytes

def decode(data:bytes) -> dict:
    if not data:
        return None
    packet = pickle.loads(data)
    return packet