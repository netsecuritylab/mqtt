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
        self.mapPacketsFunction = {
            "subscribe": self.sendSubscribe,
            "publish": self.sendPublish,
            "unsubscribe": self.sendUnsubscribe,
            "pubrel": self.sendPubrel,
            "pingreq": self.sendPingreq,
            "disconnect": self.sendDisconnect
        }

    def connectionMade(self):
        #print("[CLIENT] INVIO CONNECT")
        self.connect(self.clientId, self.keepalive, self.willTopic, self.willMessage, self.willQoS, self.willRetain, True)
        #print("[CLIENT] CONNESSO AL BROKER")
        reactor.callLater(self.keepalive//1000, self.pingreq)
       
        reactor.callLater(1/100, self.processPackets)

    def pingrespReceived(self):
        #print("[CLIENT] PINGRESP RICEVUTO DAL BROKER")
        reactor.callLater(self.keepalive//1000, self.pingreq)

    def connackReceived(self, status):
        if status == 0: # 0 per "connessione accettata"
            self.processPackets()
        else:
            print("[CLIENT] ERRORE CONNACK")
            pass

    def processPackets(self):
        if True == True:
            while len(self.packets):
                """packet = self.packets[0]
                self.packets = self.packets[1:]"""
                packet = self.packets.pop(0)
                packetName = packet["type"]
                self.mapPacketsFunction[packetName](packet)
        else:
            if len(self.packets) > 0:
                packet = self.packets.pop(0)
                packetName = packet["type"]
                self.mapPacketsFunction[packetName](packet)

        reactor.callLater(1//5, self.processPackets)

    def addPacket(self, packet):
        self.packets.append(packet)

    def sendSubscribe(self, packet):
        params = packet["params"]

        if "packetId" in params:
            return self.subscribe(params["topic"], messageId=params["packetId"])
        
        return self.subscribe(params["topic"], messageId=None)

    def sendPublish(self, packet):
        params = packet["params"]
        #print("PUBBLICO PACCHETTO id: " + str(params["packetId"]) + ", qos: " + str(params["qos"]))
        return self.publish(topic=params["topic"], message=params["message"], dup=params["dup"], qos=params["qos"], messageId=params["packetId"], retain=params["retain"])

    def sendUnsubscribe(self, packet):
        params = packet["params"]

        if "packetId" in params:
            return self.unsubscribe(params["topic"], messageId=params["packetId"])
        
        return self.unsubscribe(params["topic"])

    def sendPubrel(self, packet):
        params = packet["params"]
        return self.pubrel(params["packetId"])

    def sendPingreq(self, packet):
        return self.pingreq()

    def sendDisconnect(self, packet):
        return self.disconnect()

    def connectMqtt(self):
        pass
    


