import click
import random
import json

def longNameGenerator(string, count):
    a = ""
    for i in range(0, count):
        if len(a) > 60000:
            break
        a += "/" + string
    return a

def buildSubscribe(inputpassed):
    sk = json.loads(inputpassed) # [count, name, longname]
    count, name, longname = sk
    data = []
    for i in range(0, count):
        topic = ""
        if name:
            topic = name
        elif not name and not longname:
            topic = "random_topic_subscription_" + str(random.randint(0, 6000))
        else:
            topic = longNameGenerator("tpo", 60000)

        packet = {
            "type": "subscribe",
            "params": {
                "topic": topic,
                "packetId": random.randint(0, 6000)
            }
        }
        data.append(packet)
    return data

def buildPublish(count):
    data = []
    for i in range(1, count):
        topic = "/test/topic"
        qos = random.randint(0, 2)
        packetId = i
        packet = {
            "type": "publish",
            "params": {
                "topic": topic,
                "packetId": packetId,
                "message": "test",
                "qos": qos,
                "retain": False,
                "dup": False
            }
        }
        
        data.append(packet)
        if qos == 2:
            packet = {
                "type": "pubrel",
                "params": {
                    "packetId": packetId,
                }
            }
        data.append(packet)
    return data

@click.command()
@click.option("-sub", default=[0, False, False], help="Subscription packets", show_default=True)
@click.option('-pub', default=0, help="Publish packets", show_default=True)
@click.option('-ping', default=0, help="Pingresp packet", show_default=True)
@click.option('-disc', default=0, help="Disconnect packet", show_default=True)
@click.option('-o', help="Output file", required=True)
@click.option('-r', default=False, show_default=True, help="Randomization")

def fun(sub, pub, ping, disc, o, r):
    outpuData = buildPublish(pub)
    with open('packets_generated/' + o, mode='w') as f:
        json.dump(outpuData, f)

    print("Packets generated successfully in packets_generated/" + o)
    return 1


if __name__ == "__main__":
    fun()