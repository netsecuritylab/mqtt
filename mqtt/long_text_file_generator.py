import json
def t():
    a = ""
    for i in range(0, 0x989680):
        a += "a"

    with open('test.txt', mode='w') as f:
        f.write(a)
    print("created")

"""

{
        "type": "publish",
        "params": {
            "topic": "test/topic",
            "message": "pacchetto #1",
            "qos": 2,
            "dup": false,
            "retain": false,
            "packetId": 1
        }
    },
"""

def buildPacketBig():
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
    print("FILE PACKET CREATO")

if __name__ == "__main__":
    buildPacketBig()