#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Licensed under the MIT license
# http://opensource.org/licenses/mit-license.php

# <C> Copyright 2007, Manuel Jacob

import os

from base import Config, BaseCenter
from lib.packets import PSYCPacket, MMPPacket
from lib import get_host, get_user

class ClientConfig(Config):
    def __init__(self, app):
        Config.__init__(self, app)
        self.uni_file = os.path.join(self.settings_folder, 'me')
        self.clientconfig_file = os.path.join(self.settings_folder, 'pypsyc', 'config') 
        
        #self.uni = self.get_uni()
        import random
        self.uni = 'psyc://beta.ve.symlynX.com/~pypsyctest' + ''.join([random.Random().choice('abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ123456789') for i in [0]*10])
        #self.uni = raw_input('uni?: ')
        self.host = get_host(self.uni)
        self.username = get_user(self.uni)

        self.ui = 'wx'

    def get_settings_folder(self):
        # resolve settings folder
        if os.name == 'posix':
            folder = os.path.join(os.environ.get('HOME'), ".psyc")
        elif os.name == 'nt':
            folder = os.path.join(os.environ.get('APPDATA'), 'psyc')
        else:
            folder = os.path.join(os.getcwd(), 'psyc')

        # create settings folder if necessary
        try:
            os.mkdir(folder)
        except OSError:
            pass

        return folder

    def get_uni(self):
        f = file(self.uni_file)
        uni = f.read().strip()
        f.close()
        return uni

    def open_configfile(self):
        return None


class ClientCenter(BaseCenter):
    type = 'client'

    def __init__(self):
        self.config = ClientConfig(self)

    def _connected(self, connection, host):
        pass

    def recv_mmp_packet(self, packet, physsource):
        if not packet.vars and not packet.body:
            return
        psyc_packet = physsource.psyc_parser.parse(packet)
        self.recv_psyc_packet(psyc_packet, physsource)

    def send_psyc_packet(self, packet):
        self._send_psyc_packet(packet, self.connections[self.config.host])

    def input(self, pagename, text):
        if '@' in pagename:
            self.send_psyc_packet(PSYCPacket(mmpvars = {'_target': pagename}, mc = '_message_public', data = text))

        if text.startswith('/'):
            self.command(pagename, text)

    def command(self, pagename, text):
        if text == '/quit' or '/bye':
            self.send_psyc_packet(PSYCPacket(mmpvars = {'_target': self.config.uni}, mc = '_request_execute', data = text))

        else:
            self.send_psyc_packet(PSYCPacket(psycvars = {'_focus': pagename}, mc = '_request_input', data = text))
