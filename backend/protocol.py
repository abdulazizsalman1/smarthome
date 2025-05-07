import json

def marshal(data):
    """ Serialize Python dictionary to JSON string """
    return json.dumps(data)

def unmarshal(json_data):
    """ Deserialize JSON string to Python dictionary """
    return json.loads(json_data)
