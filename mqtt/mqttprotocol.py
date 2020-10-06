from twisted.internet.protocol import Protocol
from utils import _decodeLength, _decodeValue, _decodeString, _encodeLength, _encodeString, _encodeValue
import random

class MQTTProtocol(Protocol):

    buffer = bytearray()
    availablePackets = {
            0x00: "null",
            0x01: "connect",
            0x02: "connack",
            0x03: "publish",
            0x04: "puback",
            0x05: "pubrec",
            0x06: "pubrel",
            0x07: "pubcomp",
            0x08: "subscribe",
            0x09: "suback",
            0x0A: "unsubscribe",
            0x0B: "unsuback",
            0x0C: "pingreq",
            0x0D: "pingresp",
            0x0E: "disconnect"
        }

    def __init__(self):
        pass

    def connectionMade(self):
        print("[PROTOCOL] CONNESSIONE EFFETTUATA")

    def connectionLost(self, reason):
        pass

    def dataReceived(self, data):
        self._packetQueue(data)

    def _packetQueue(self, data):
        self.buffer.extend(data)
        length = None
        while len(self.buffer):
            if length is None:
                # si ha un pacchetto da processare

                if len(self.buffer) < 2: # non ci sono abbastanza dati per inizializzare un nuovo pacchetto
                    break

                newLength = 1

                while newLength < len(self.buffer):
                    if not self.buffer[newLength] & 0x80:
                        break
                    newLength += 1

                if newLength < len(self.buffer) and self.buffer[newLength] & 0x80:
                    return

                length = _decodeLength(self.buffer[1:])

                if len(self.buffer) >= length:
                    chunk = self.buffer[:length + newLength + 1]
                    self._workPacket(chunk)
                    self.buffer = self.buffer[length + newLength + 1:]
                    length = None
                else:
                    break
        
    def _workPacket(self, packet):
        try:
            packetType = self.availablePackets[(packet[0] & 0xF0) >> 4]
            print("[PROTOCOL] RICEVO => " + packetType.upper())
            duplicate = (packet[0] & 0x08) == 0x08
            packetQoS = (packet[0] & 0x06) >> 1
            retain = (packet[0] & 0x01) == 0x01
        except:
            print("ID PACCHETTO " + str((packet[0] & 0xF0) >> 4) + " NON RICONOSCIUTO.")
            return

        newLength = 1
        while packet[newLength] & 0x80:
            newLength += 1

        packet = packet[newLength+1:]
        packetHandler = getattr(self, "{}_event".format(packetType), None)
        if packetHandler:
            packetHandler(packet, packetQoS, duplicate, retain)
        else:
            print("Non posso gestire questo pacchetto")
            return

    def connack_event(self, packet, qos, dup, retain):
        self.connackReceived(packet[0])

    def suback_event(self, packet):
        self.subackReceived(packet[0])

    def connect_event(self, packet, qos, dup, retain):
        packet = packet[len("MQisdp")]

        willRetain = packet[0] & 0x20 == 0x20
        willQoS = packet[0] & 0x18 >> 3
        willFlag = packet[0] & 0x04 == 0x04
        cleanStart = packet[0] & 0x02 == 0x02
        
        packet = packet[1:]
        keepalive = _decodeValue(packet[:2])

        packet = packet[2:]

        clientId = _decodeString(packet)
        packet = packet[len(clientId) + 2:]

        willTopic = None
        willMessage = None
        if willFlag:
            willTopic = _decodeString(packet)
            packet = packet[len(willTopic) + 2:]
            willMessage = packet

        self.connectReceived(clientId, keepalive, willTopic, willMessage, willQoS, willRetain, cleanStart)

    def subscribe_event(self, packet, qos, dup, retain):
        messageId = _decodeValue(packet[:2])
        packet = packet[2:]

        topics = []
        while len(packet):
            topic = _decodeString(packet)
            packet = packet[len(topic) + 2:]
            qos = packet[0]
            packet = packet[1:]
            topics.append((topic, qos))

        self.subscribeReceived(topics, messageId)

    def publish_event(self, packet, qos, dup, retain):
        topic = _decodeString(packet)
        packet = packet[len(topic) + 2:]

        messageId = None

        if qos > 0:
            messageId = _decodeValue(packet[:2])
            packet = packet[2:]
        

        message = str(packet)
        
        self.publishReceived(topic, message, qos, dup, retain, messageId)

    def suback_event(self, packet, qos, dup, retain):
        messageId = _decodeValue(packet[:2])
        packet = packet[2:]
        qos = []

        while len(packet):
            qos.append(packet[0])
            packet = packet[1:]

        
        self.subackReceived(qos, messageId)

    def unsuback_event(self, packet, qos, dup, retain):
        messageId = _decodeValue(packet[:2])
        
        self.unsubackReceived(messageId)

    def connect(self, clientId, keepalive=60, willTopic=None, willMessage=None, willQoS=0, willRetain=False, cleanStart=True):
        
        header = bytearray()
        varHeader = bytearray()
        payload = bytearray()
        
        varHeader.extend(_encodeString(b"MQTT")) # nome del protocollo
        varHeader.append(4) # versione del protocollo

        if willMessage is None or willTopic is None:
            varHeader.append(0 << 2 | cleanStart << 1) # byte per il cleanSession
        else:
            varHeader.append(willRetain << 5 | willQoS << 3 | 1 << 2 | cleanStart << 1) # produce i bit per i vari valori del pacchetto

        varHeader.extend(_encodeValue(keepalive//1000)) # byte per il keepalive

        payload.extend(_encodeString(bytes(clientId, "utf-8"))) # clientId in bytes, utf-8.

        if willMessage is not None and willTopic is not None:
            payload.extend(_encodeString(bytes(willTopic, "utf-8"))) # topic
            payload.extend(_encodeString(bytes(willMessage, "utf-8"))) # message

        header.append(0x01 << 4)
        header.extend(_encodeLength(len(varHeader) + len(payload)))

        self.transport.write(header)
        self.transport.write(varHeader)
        self.transport.write(payload)

    def connack(self, status):
        header = bytearray()
        payload = bytearray()

        header.append(0x02 << 4)
        payload.append(status)

        header.extend(_encodeLength(len(payload)))
        self.transport.write(header)
        self.transport.write(payload)

    def subscribe(self, topic, qos=0, messageId=None):
        header = bytearray()
        varHeader = bytearray()
        payload = bytearray()

        header.append(0x08 << 4 | 0x01 << 1) # 130 in decimale, 1000010 in binario (packet header subscribe richiede 1 0 0 0 0 0 1 0)

        if messageId is None:
            varHeader.extend(_encodeValue(random.randint(1, 65535))) # max id 65535, da provare messaggi id più grandi di 65535
        else:
            varHeader.extend(_encodeValue(messageId))

        payload.extend(_encodeString(bytes(topic, "utf-8"))) # payload data
        payload.append(qos) # il qos è alla finne quindi append
        header.extend(_encodeLength(len(varHeader) + len(payload)))

        self.transport.write(header)
        self.transport.write(varHeader)
        self.transport.write(payload)

    def unsubscribe(self, topic, messageId):
        header = bytearray()
        varHeader = bytearray()
        payload = bytearray()

        header.append(0x0A << 4 | 0x01 << 1) # 1010 0010

        if messageId is None:
            varHeader.extend(_encodeValue(random.randint(1, 65535))) # max id 65535, da provare messaggi id più grandi di 65535
        else:
            varHeader.extend(_encodeValue(messageId))

        payload.extend(_encodeString(bytes(topic, "utf-8"))) # topic da unsubscribe

        header.extend(_encodeLength(len(varHeader) + len(payload)))

        self.transport.write(header)
        self.transport.write(varHeader)
        self.transport.write(payload)

    def publish(self, topic, message, dup=False, qos=0, retain=False, messageId=None):
        header = bytearray()
        varHeader = bytearray()
        payload = bytearray()

        header.append(0x03 << 4 | dup << 3 | qos << 1 | retain) # primo byte: 0011 dup qos retain

        varHeader.extend(_encodeString(topic.encode('utf-8'))) # topic


        if qos > 0:
            if messageId is None:
                varHeader.extend(_encodeValue(random.randint(1, 65535)))
            else:
                varHeader.extend(_encodeValue(messageId))

        
        payload.extend(_encodeString(message.encode("utf-8")))


        print(payload)
        header.extend(_encodeLength(len(varHeader) + len(payload)))

        self.transport.write(header)
        self.transport.write(varHeader)
        self.transport.write(payload)
        

    def connackReceived(self, status):
        pass

    def subackReceived(self, qos, messageId):
        pass

    def unsubackReceived(self, messageId):
        pass

    def subscribeReceived(self, topics, messageId):
        pass

    def connectReceived(self, clientId, keepalive, willTopic, willMessage, willQoS, willRetain, cleanStart):
        pass

    def publishReceived(self, topic, message, qos=0, dup=False, retain=False, messageId=None):
        print("NUOVO MESSAGGIO RICEVUTO DAL TOPIC " + str(topic).upper() + " => " + message)
        pass

    


