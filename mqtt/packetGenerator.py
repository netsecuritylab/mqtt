import click
import random
import json

def buildSubscribe(count):
    data = []
    for i in range(0, count):
        packet = {
            "type": "subscribe",
            "params": {
                "topic": "random_topic_subscription_" + str(random.randint(0, 6000)),
                "packetId": random.randint(0, 6000)
            }
        }
        data.append(packet)
    return data

@click.command()
@click.option("-sub", default=0, help="Pacchetti subscribe da inviare", show_default=True)
@click.option('-pub', default=0, help="Pacchetti publish da inviare", show_default=True)
@click.option('-ping', default=0, help="Pacchetti pingresp da inviare", show_default=True)
@click.option('-disc', default=0, help="Pacchetti disconnect da inviare", show_default=True)
@click.option('-o', help="Nome file json di output", required=True)
@click.option('-r', default=False, show_default=True, help="Randomizzazione dei pacchetti")

def fun(sub, pub, ping, disc, o, r):
    outpuData = buildSubscribe(sub)
    with open('packets_generated/' + o, mode='w') as f:
        json.dump(outpuData, f)

    print("Pacchetti generati con successo nel file packets_generated/" + o)
    return 1


if __name__ == "__main__":
    fun()