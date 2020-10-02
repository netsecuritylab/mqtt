import sys

from twisted.internet import reactor, task
from twisted.internet.defer import inlineCallbacks, DeferredList
from twisted.application.internet import ClientService, backoffPolicy
from twisted.internet.endpoints import clientFromString
from twisted.logger import (Logger, LogLevel, globalLogBeginner, textFileLogObserver, FilteringLogObserver, LogLevelFilterPredicate)
from twisted.internet.protocol import Protocol, ClientFactory
from mqtt.client.factory import MQTTFactory


class MQTTProtocol(Protocol):

    def dataReceived(self, data):
        sys.stdout.write(data)


class MQTTClientFactory(ClientFactory):

    def startedConnecting(self, connector):
        print("Connessione in corso")

    def buildProtocol(self, addr):
        print("Connesso")
        return MQTTProtocol()

    def clientConnectionLost(self, connector, reason):
        print("Connessione persa, motivazione: {}".format(reason))

    def clientConnectionFailed(self, connector, reason):
        print("Connessione fallita, motivazione: {}".format(reason))

if __name__ == "__main__":
    reactor.connectTCP("localhost", 1883, MQTTClientFactory())
    reactor.run()

