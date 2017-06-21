#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import threading
from twisted.internet import protocol, reactor

HOST = 'localhost'
PORT = 21567


class DuplexChat(protocol.Protocol):
    def connectionMade(self):
        threading.Thread(target=self.sendData).start()

    def dataReceived(self, data):
        print(data)

    def sendData(self):
        while True:
            data = input("> ")
            if data:
                self.transport.write(data.encode('utf-8'))
            else:
                self.transport.loseConnection()
                break


class DuplexChatFactory(protocol.ClientFactory):
    protocol = DuplexChat
    clientConnectionLost = clientConnectionFailed = lambda self, connector, reason: reactor.stop()

reactor.connectTCP(HOST,PORT,DuplexChatFactory())
reactor.run()