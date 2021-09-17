import json
def t():
    a = ""
    for i in range(0, 4097):
        a += "a"

    with open('test.txt', mode='w') as f:
        f.write(a)
    print("created")

def buildPacketBig():
    # it was used to build a packet with big payload.
    a = ""
    for i in range(0, 0xF4240):
        a += "a"

    packetsub = {}
    packetsub["type"] = "subscribe"
    packetsub["params"] = {
        "topic": "test/topic"
    }

    packetpub = {}
    packetpub["type"] = "publish"
    packetpub["params"] = {
        "topic": "test/topic",
        "message": a,
        "qos": 0,
        "dup": False,
        "retain": False,
        "packetId": 1
    }
    data = [packetsub, packetpub]
    with open('packets_generated/1mb_payload_test.json', mode='w') as f:
        json.dump(data, f)
    print("JSON File created")

if __name__ == "__main__":
    t()