from mqttprotocol import MQTTProtocol
import random

class MQTTClient(MQTTProtocol):

    def __init__(self, clientId=None, keepalive=None, willQoS=1, willTopic=None, willMessage=None, willRetain=None):

        self.clientId = clientId if clientId is not None else "client_" + str(random.randint(0, 2000))
        self.keepalive = keepalive if keepalive is not None else 60
        self.willQoS = willQoS
        self.willTopic = willTopic
        self.willMessage = willMessage
        self.willRetain = willRetain

    def connectionMade(self):
        print("[CLIENT] INVIO CONNECT")
        self.connect(self.clientId, self.keepalive, self.willTopic, self.willMessage, self.willQoS, self.willRetain, True)
        print("[CLIENT] CONNESSO AL BROKER")


    def connackReceived(self, status):
        if status == 0:
            self.connectMqtt()
        else:
            print("[CLIENT] ERRORE CONNACK")
            pass

    def connectMqtt(self):
        print("[CLIENT] CONNACK => RICEVUTO")

        print("[CLIENT] INVIO SUBSCRIBE")
        self.subscribe("prova_sub", qos=0, messageId=20)
        print("[CLIENT] INVIO UNSUBSCRIBE")
        self.unsubscribe("prova_sub", messageId=30)
    


