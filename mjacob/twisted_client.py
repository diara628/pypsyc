#!/usr/bin/env python
# -*- coding: utf-8 -*-

from lib import psyctext
from lib.packets import MMPPacket, PSYCPacket
from socket_.twisted_ import TwistedClientCenter#, reactor

factory = TwistedClientCenter()
#factory.connect(factory.config.host)

debug = True

import base
base.debug = debug

def install_wx(app): # not tested
    #del sys.modules['twisted.internet.reactor']
    from twisted.internet import wxreactor
    wxreactor.install()
    from twisted.internet import reactor
    reactor.registerWxApp(app)

def install_tk(app): # not tested
    from twisted.internet import tksupport
    tksupport.install(app)

def install_gtk(app): # not tested
    del sys.modules['twisted.internet.reactor']
    from twisted.internet import gtkreactor
    gtkreactor.install()
    from twisted.internet import reactor

def install_gtk2(app): # not tested
    del sys.modules['twisted.internet.reactor']
    from twisted.internet import gtk2reactor
    gtk2reactor.install()
    from twisted.internet import reactor

if debug and __name__ == '__main__': # You can test modules here
    from base import Module

    class DebugModule(Module):
        methods = ['*']
        def received(self, packet, physsource):
            print """packet from %s::
mmpvars: %s
psycvars: %s
mc: %s
text: %s
""" % (physsource, packet.mmpvars, packet.psycvars, packet.mc, psyctext(packet))

    factory.register_module(DebugModule())


    class AuthModule(Module):
        methods = ['_notice_circuit_established']

        def handle_notice_circuit_established(self, packet, physsource):
            physsource.send_psyc_packet(PSYCPacket(mmpvars = {'_target': factory.config.uni}, mc = '_request_link'))
            physsource.mmp_renderer.set_pvar('_source_identification', factory.config.uni)

    factory.register_module(AuthModule())


if __name__ == '__main__':
    from UI.wx_ import UI

    app = UI(factory)

    from twisted.internet import reactor
    factory.reactor = reactor

    print 'start reactor'
    reactor.run()
