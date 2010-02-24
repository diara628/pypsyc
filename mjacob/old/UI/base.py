#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Licensed under the MIT license
# http://opensource.org/licenses/mit-license.php

# <C> Copyright 2007, Manuel Jacob

import re

from twisted.internet import reactor

from PSYC.PSYCPacket import PSYCPacket

re_var = re.compile('\[_.[^\[]+\]')

class BaseUI:
    ignored_mcs = []
    ignored_users = []
    mc_prefixes = ('_notice', '_error', '_info', '_status')
    inpacketcount = 0
    outpacketcount = 0
    connected = False

    def recv(self, packet):
        self.inpacketcount += 1
        if packet.mc in self.ignored_mcs:
            return

        #if packet.vars['_source'] in self.ignored_users:
        #    return

        self.pre_print(packet)
        self._insert_vars(packet)
        self.print_(packet)

    def _insert_vars(self, packet):
        while True:
            x = re_var.search(packet.text)
            if not x:
                break
            tmp = x.group()
            if tmp[1:-1] in packet.vars:
                packet.text = packet.text.replace(tmp, packet.vars[tmp[1:-1]])

    def print_(self, packet):
        func = None
        for i in self.mc_prefixes:
            if packet.mc.startswith(i):
                func = getattr(self, 'handle_%s_' % i[1:], None)

        tmp = getattr(self, 'handle_%s' % packet.mc[1:], None)

        if tmp:
            func = tmp

        if func:
            func(packet)

        else:
            self._print('Server', 'unhandled packetmc (Packet %s)' 
                                                      % self.inpacketcount)

    def handle_notice_(self, packet):
        self._print('Server', "%s: %s" % (packet.mc, packet.text))
    
    def handle_error_(self, packet):
        self._print('Server', "%s: %s" % (packet.mc, packet.text))

    def handle_info_(self, packet):
        self._print('Server', "%s: %s" % (packet.mc, packet.text))

    def handle_status_(self, packet):
        self._print('Server', "%s: %s" % (packet.mc, packet.text))

    def handle_message_public(self, packet):
        self._print(packet.vars['_context'], '%s says: %s'
                                        % (packet.vars['_nick'], packet.text))

    def handle_status_place_topic_official(self, packet):
        pass
    
    def handle_echo_logoff(self, packet):
        reactor.stop()

    def server_command(self, command, target):
        if target == 'Server':
            target = 'psyc://%s/' % self.factory.config.host

        if command.startswith('/go'):
            self.factory.sc.send_packet(PSYCPacket(mmpvars = {'_target': command[4:]}, psycvars = {'_nick': self.factory.config.username}, mc = '_request_enter'))
        
        elif command.startswith('/join'):
            self.factory.sc.send_packet(PSYCPacket(mmpvars = {'_target': command[6:]}, psycvars = {'_nick': self.factory.config.username}, mc = '_request_enter'))

        elif command.startswith('/quit'):
            self.factory.sc.send_packet(PSYCPacket(mmpvars = {'_target': self.factory.config.uni, '_source_identification': self.factory.config.uni}, mc = '_request_execute', text = 'bye'))
            

        else:
            self.factory.sc.send_packet(PSYCPacket(mmpvars = {'_target': self.factory.config.uni, '_source_identification': self.factory.config.uni}, mc = '_request_input', text = command))

        #if command.startswith('/quit'):
        #    reactor.stop()

        #if command.startwith('/part'):
        #    self.factory.sc.send_packet(PSYCPacket())
