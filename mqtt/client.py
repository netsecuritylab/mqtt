from mqttprotocol import MQTTProtocol
import random
import time
from twisted.internet import reactor

class MQTTClient(MQTTProtocol):

    def __init__(self, clientId=None, keepalive=None, willQoS=1, willTopic=None, willMessage=None, willRetain=None, packets=None):

        self.clientId = clientId if clientId is not None else "client_" + str(random.randint(0, 2000))
        self.keepalive = keepalive if keepalive is not None else 60000
        self.willQoS = willQoS
        self.willTopic = willTopic
        self.willMessage = willMessage
        self.willRetain = willRetain
        self.packets = packets

    def connectionMade(self):
        print("[CLIENT] INVIO CONNECT")
        self.connect(self.clientId, self.keepalive, self.willTopic, self.willMessage, self.willQoS, self.willRetain, True)
        print("[CLIENT] CONNESSO AL BROKER")
        reactor.callLater(self.keepalive//1000, self.pingreq)
        reactor.callLater(5, self.processPackets)

    def pingrespReceived(self):
        print("[CLIENT] PINGRESP RICEVUTO DAL BROKER")
        reactor.callLater(self.keepalive//1000, self.pingreq)

    def connackReceived(self, status):
        if status == 0: # 0 per "connessione accettata"
            self.processPackets()
        else:
            print("[CLIENT] ERRORE CONNACK")
            pass

    def processPackets(self):
        print(self.packets)
        reactor.callLater(5, self.processPackets)

    def addPacket(self, packet):
        self.packets.append(packet)

    def connectMqtt(self):
        pass
        """print("[CLIENT] CONNACK => RICEVUTO")

        print("[CLIENT] INVIO SUBSCRIBE")
        self.subscribe("prova_sub_false", qos=0, messageId=20)

        print("[CLIENT] INVIO PUBLISH")
        #self.publish("prova_sub", message="packet 1", messageId=5005, qos=2)

        #self.pubrel(messageId=5007)

        #time.sleep(5)

        #self.publish("prova_sub", message="packet 2", messageId=5005, qos=2)
        #self.pubrel(messageId=5005)
        self.pubrel(messageId=5005)
        self.pingreq()
        self.disconnect()

        #print("[CLIENT] INVIO UNSUBSCRIBE")
        #self.unsubscribe("prova_sub", messageId=30)"""
    


