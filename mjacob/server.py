#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Licensed under the MIT license
# http://opensource.org/licenses/mit-license.php

# <C> Copyright 2007, Manuel Jacob

import os

from base import Config, BaseCenter, MMPCircuit


### TODO: This don't works yet ###


class ToClientCircuit(MMPCircuit):
    def __init__(self, center):
        MMPCircuit.__init__(self, center)

    def init(self):
        MMPCircuit.init(self)
        #self.


class ServerConfig(Config):
    def __init__(self, app):
        Config.__init__(self, app)
        self.serverconfig_file = os.path.join(self.settings_folder, 'config') 

    def get_settings_folder(self):
        # resolve settings folder
        if os.name == 'posix':
            folder = os.path.join(os.environ.get('HOME'), ".pypsyced")
        elif os.name == 'nt':
            folder = os.path.join(os.environ.get('APPDATA'), 'pypsyced')
        else:
            folder = os.path.join(os.getcwd(), 'pypsyced')

        # create settings folder if necessary
        try:
            os.mkdir(folder)
        except OSError:
            pass

        return folder

    def open_configfile(self):
        return None


class ServerCenter(BaseCenter):
    def __init__(self):
        self.config = ServerConfig(self)

    def recv_mmp_packet(self, packet, physsource):
        if not packet.vars and not packet.body:
            return

        if physsource.linked_uni == None or packet.mmpvars['_target']:
            psyc_packet = physsource.psyc_parser.parse(packet)
            self.recv_psyc_packet(psyc_packet, physsource)
