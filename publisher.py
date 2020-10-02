import sys

from twisted.internet import reactor, task
from twisted.internet.defer import inlineCallbacks, DeferredList
from twisted.application.internet import ClientService, backoffPolicy
from twisted.internet.endpoints import clientFromString
from twisted.logger import (Logger, LogLevel, globalLogBeginner, textFileLogObserver, FilteringLogObserver, LogLevelFilterPredicate)

from mqtt.client.factory import MQTTFactory

endpoint = "tcp:localhost:1883"
logLevelFilterPredicate = LogLevelFilterPredicate(defaultLogLevel=LogLevel.debug)

def startLogging(console=True, filepath=None):
    
    observers = []

    if console:
        observers.append(FilteringLogObserver(observer=textFileLogObserver(sys.stdout), predicates=[logLevelFilterPredicate]))
    
    if filepath is not None and filepath != "":
        observers.append(FilteringLogObserver(observer=textFileLogObserver(open(filepath, 'a')), predicates=[logLevelFilterPredicate]))
    
    globalLogBeginner.beginLoggingTo(observers)


def setLogLevel(namespace=None, levelStr='info'):
    level = LogLevel.levelWithName(levelStr)
    logLevelFilterPredicate.setLogLevelForNamespace(namespace=namespace, level=level)


class MQTTService(ClientService):

    def __init__(self, endpoint, factory):
        self.endpoint = endpoint
        ClientService.__init__(self, endpoint, factory, retryPolicy=backoffPolicy())


    def startService(self):
        log.info("Publisher MQTT inizializzato")

        self.whenConnected().addCallback(self.connectToBroker)
        ClientService.startService(self)

    
    @inlineCallbacks
    def connectToBroker(self, protocol):
        self.protocol = protocol
        self.protocol.onDisconnection = self.onDisconnection
        self.protocol.setWindowSize(1)
        self.task = task.LoopingCall(self.publish)
        self.task.start(5.0)

        try:
            yield self.protocol.connect("myClientId", keepalive=60)
        except Exception as e:
            log.error(("Connecting to {} raised {}".format(self.endpoint, str(e))))
        else:
            log.info("Connesso al broker {broker}", broker=self.endpoint)


    def onDisconnection(self, reason):
        log.debug("Disconnesso, motivazione: {r}", r=reason)
        self.whenConnected().addCallback(self.connectToBroker)


    def publish(self):

        def _logFailure(failure):
            log.debug("errore: {f}", f=failure.getErrorMessage())

        def _logAll(*args):
            log.debug("publishing completo: {args}", args=args)

        log.debug("Publishing")

        d1 = self.protocol.publish(topic="test/publishtest", qos=0, message="hello")
        d1.addErrback(_logFailure)

        dlist = DeferredList([d1], consumeErrors=True)
        dlist.addCallback(_logAll)

        return dlist


if __name__ == "__main__":
    import sys

    log = Logger()
    startLogging()

    setLogLevel(namespace="mqtt", levelStr="debug")
    setLogLevel(namespace="__main__", levelStr= "debug")

    factory = MQTTFactory(profile=MQTTFactory.PUBLISHER)
    myend = clientFromString(reactor, endpoint)
    print(myend)
    serv = MQTTService(myend, factory)
    serv.startService()
    reactor.run()
