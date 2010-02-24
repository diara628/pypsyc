#!/usr/bin/env python
# -*- coding: utf-8 -*-

from twisted.internet import protocol

from base import MMPCircuit, PSYCCircuit
from client import ClientCenter
from server import ServerCenter


class CircuitBaseProtocol(protocol.Protocol):
    def connectionMade(self):
        self.init()

    def dataReceived(self, data):
        self.mmp_parser.data(data)

    def _send(self, data):
        print (data,)
        self.transport.write(data)


class MMPCircuitProtocol(CircuitBaseProtocol, MMPCircuit): pass


class PSYCCircuitProtocol(CircuitBaseProtocol, PSYCCircuit): pass


class TwistedClientCenter(ClientCenter, protocol.ClientFactory):
    def buildProtocol(self, addr):
        p = PSYCCircuitProtocol(self)
        self.connected(p, addr.host)
        return p

    def connect(self, host, port = 4404):
        self.reactor.connectTCP(host, port, self)


#class TwistedServerCenter(ClientCenter, protocol.ClientFactory):
#    def buildProtocol(self, addr):
#        p = CircuitProtocol(self)
#        self.connected(p, addr.host)
#        return p
#
#    def connect(self, host, port = 4404):
#        self.reactor.connectTCP(host, port, self)
