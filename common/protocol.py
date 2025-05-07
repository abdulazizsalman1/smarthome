# common/protocol.py
import json

def marshal(data):
    return json.dumps(data).encode('utf-8')

def unmarshal(data):
    return json.loads(data.decode('utf-8'))
