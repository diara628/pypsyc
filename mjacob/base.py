#!/usr/bin/env python
# -*- coding: utf-8 -*-

## base.py


# Licensed under the MIT license
# http://opensource.org/licenses/mit-license.php

# <C> Copyright 2007, Manuel Jacob


from lib.parse import MMPParser, PSYCParser
from lib.render import MMPRenderer, PSYCRenderer
from lib.packets import MMPPacket, PSYCPacket


debug = False


class Module:
    methods = []

    def register_center(self, center):
        self.center = center

    def received(self, packet, physsource):
        func = getattr(self, 'handle_%s' % packet.mc[1:], None)

        if func:
            func(packet, physsource)

        else:
            self.handle(packet, physsource)


class MMPCircuit:
    def __init__(self, center):
        self.center = center
        self.mmp_parser = MMPParser()
        self.mmp_parser.recv_packet = self.recv_packet
        self.mmp_renderer = MMPRenderer()

    def init(self):
        self.send_mmp_packet(MMPPacket())

    def recv_packet(self, packet):
        self.center.recv_mmp_packet(packet, self)

    def send_mmp_packet(self, packet):
        self._send(self.mmp_renderer.render(packet))


class PSYCCircuit(MMPCircuit):
    def __init__(self, center):
        MMPCircuit.__init__(self, center)
        self.psyc_parser = PSYCParser()
        self.psyc_renderer = PSYCRenderer()

    def send_psyc_packet(self, packet):
        self.send_mmp_packet(self.psyc_renderer.render(packet))


class Plugin:
    def __init__(self, name):
        self.name = name
        self.p = __import__('plugins.' + self.name, (), (), [self.name])
        self.needs = self.p.needs

    def load(self):
        self.instance = self.p.Module()


class Config:
    def __init__(self, app):
        self.app = app

        self.settings_folder = self.get_settings_folder()
        self.configfile = self.open_configfile()


class BaseCenter:
    type = 'base'
    registered_modules = []
    handlers = {}
    plugins = {}
    connections = {}

    def load_plugin(self, name):
        p = Plugin(name)

        for load in p.needs:
            self.load_plugin(load)

        p.load()
        self.register_module(p.instance)
        self.plugins[name] = p

    def register_module(self, module):
        for i in module.methods:
            if i in self.handlers:
                self.handlers[i].append(module)

            else:
                self.handlers[i] = [module]

        module.register_center(self)
        self.registered_modules.append(module)

    def connected(self, connection, host):
        self.connections[host] = connection
        self._connected(connection, host)

    def _connected(self, connection, host):
        pass

    def recv_mmp_packet(self, packet, physsource): # called by circuit
        raise NotImplementedError

    def recv_psyc_packet(self, packet, physsource): # called by subclass
        handlers = []

        for key, value in self.handlers.items():
            if key == packet.mc or \
            (key[-1] == '*' and packet.mc.startswith(key[:-1])):
                handlers.extend(value)

        for i in handlers:
            i.received(packet, physsource)

    def send_mmp_packet(self, packet, physdest):
        raise NotImplemented

    def _send_psyc_packet(self, packet, physdest):
        if debug: # WARNING: Do not show all packets
            print """packet to %s::
mmpvars: %s
psycvars: %s
mc: %s
text: %s
""" % (physdest, packet.mmpvars, packet.psycvars, packet.mc, packet.data)
        
        physdest.send_psyc_packet(packet)
