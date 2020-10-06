from twisted.internet import reactor
from twisted.internet.protocol import ReconnectingClientFactory
from twisted.internet.task import LoopingCall

from mqttprotocol import MQTTProtocol
from client import MQTTClient


class MQTTListenerFactory(ReconnectingClientFactory):

    def __init__(self, service=None):
        self.service = service
        self.protocol = MQTTClient

    def buildProtocol(self, addr):
        p = self.protocol(clientId="edo_best", keepalive=60000, willQoS=1, willTopic="True", willMessage="True", willRetain=0)
        p.factory = self
        self.protocol = p
        return p

    def clientConnectionLost(self, connector, reason):
        print("CONNESSIONE PERSA: {}".format(reason))
        #ReconnectingClientFactory.clientConnectionLost(self, connector, reason)
    
    def clientConnectionFailed(self, connector, reason):
        print("CONNNESSIONE FALLITA: {}".format(reason))
        #ReconnectingClientFactory.clientConnectionFailed(self, connector, reason)


if __name__ == "__main__":
    mqttFactory = MQTTListenerFactory()
    reactor.connectTCP("192.168.1.24", 1883, mqttFactory)
    reactor.run()