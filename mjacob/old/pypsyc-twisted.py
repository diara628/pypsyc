#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Licensed under the GPLv2 license
# http://www.gnu.org/licenses/old-licenses/gpl-2.0.html

# <C> Copyright 2007, Manuel Jacob

import os

from __init__ import get_host, get_user
from PSYC.PSYCProtocol import PSYCProtocol
from PSYC.PSYCPacket import PSYCPacket

try:
    from twisted.internet import wxreactor
    wxreactor.install()
except ImportError:
    pass

from twisted.internet import reactor, protocol

class Config:
    def __init__(self, factory):
        self.factory = factory
        self.settings_folder = self.get_settings_folder()

        self.uni_file = os.path.join(self.settings_folder, 'me')
        self.clientconfig_file = os.path.join(self.settings_folder, 'pypsyc', 'config')

        self.uni = self.get_uni()
        #self.uni = 'psyc://beta.ve.symlynX.com/~pypsyctest'
        #self.uni = raw_input('uni?: ')
        self.host = get_host(self.uni)
        self.username = get_user(self.uni)

        self.configfile = self.open_configfile()

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


class App(protocol.ClientFactory):
    def __init__(self):
        self.config = Config(self)
        self.protocol = PSYCProtocol
        self.connections = {}

        #Interface = __import__('UI.%s.Interface' % self.config.ui, [], [], ['Interface'])
        exec("from UI.%s.Interface import Interface" % self.config.ui)
        self.ui = Interface(self)

        self.callback_on_recv = self.ui.recv

    def connect(self):
        reactor.connectTCP(self.config.host, 4404, self, timeout = 20)

    def buildProtocol(self, addr):
        p = self.protocol(self.callback_on_recv)
        p.factory = self
        self.callback_on_recv
        self.connections[addr.host] = p
        if len(self.connections) == 1:
            self.sc = p # sc = server connection
        return p


factory = App()
reactor.run()
