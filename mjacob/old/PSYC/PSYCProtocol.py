#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Licensed under the MIT license
# http://opensource.org/licenses/mit-license.php

# <C> Copyright 2007, Manuel Jacob


from MMP.MMPProtocol import MMPProtocol, convert_lines
from PSYC.PSYCPacket import PSYCPacket

class PSYCProtocol(MMPProtocol):
    mmpvars = (
'_source', '_source_identification', '_source_location', '_source_relay',
'_target', '_context', '_counter', '_length', '_initialize', '_fragment',
'_encoding', '_amount_fragments', '_list_using_modules',
'_list_require_modules', '_list_understand_modules', '_list_using_encoding',
'_list_require_encoding', '_list_understand_encoding',
'_list_using_protocols', '_list_require_protocols',
'_list_understand_protocols', '_trace', '_tag', '_tag_relay', '_relay')

    def _reset(self):
        pass

    def __init__(self, callback):
        MMPProtocol.__init__(self, callback)

    def _recv_packet(self, mmpvars, data):
        #print 'recv'
        psycvars, mc, text = convert_lines(data)
        packet = PSYCPacket(mmpvars, psycvars, mc, text)

        func = getattr(self, "handle_%s" % packet.mc[1:], None)

        not_call_msg = False

        if func:
            not_call_msg = func(packet)

        if not not_call_msg:
            self.msg(packet)

    def handle_status_circuit(self, packet):
        self._send_packet(None, None) # send an empty mmp packet (single dot)
        self.send_packet(PSYCPacket(mmpvars =
                  {'_target': self.factory.config.uni}, mc = '_request_link'))

        self.charset = packet.vars['_using_characters']

    def send_packet(self, packet):
        self.factory.ui.outpacketcount += 1
        self.factory.ui.pre_send(packet)
        data = ''

        if packet.psycvars:
            data += '\n'
            for key, value in packet.psycvars.items():
                data += ":%s\t%s\n" % (key, value)

        if packet.mc:
            data += packet.mc + '\n'

        if packet.text:
            data += packet.text + '\n'

        self._send_packet(packet.mmpvars, data)

    ################################
    # implementation of the PSYC API
    ################################

    def msg(self, packet):
        raise NotImplementedError

    def sendmsg(self, target, mc, data, vars):
        mmpvars = {'_target': target}
        psycvars = {}
        for key, value in vars.items():
            if i in self.mmpvars:
                mmpvars[key] = value
            else:
                psycvars[key] = value

        packet = PSYCPacket(mmpvars, psycvars, mc, data)
        self.send_packet(packet)

    def castmsg(self, source, mc, data, vars):
        mmpvars = {'_context': source}
        psycvars = {}
        for key, value in vars.items():
            if i in self.mmpvars:
                mmpvars[key] = value
            else:
                psycvars[key] = value

        packet = PSYCPacket(mmpvars, psycvars, mc, data)
        self.send_packet(packet)
