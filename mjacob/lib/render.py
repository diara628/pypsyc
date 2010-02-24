#!/usr/bin/env python
# -*- coding: utf-8 -*-

## render.py


# Licensed under the MIT license
# http://opensource.org/licenses/mit-license.php

# <C> Copyright 2007, Manuel Jacob

from packets import MMPPacket

def to_vars(cvars = {}, pvars = {}, other = {}):
    data = ''
    for key, value in cvars.items():
        data += ":%s\t%s\n" % (key, value)
    for key, value in pvars.items():
        data += "=%s\t%s\n" % (key, value)
    for key, value in other.items():
        data += "%s\t%s\n" % (key, value)
    return data


class MMPRenderer:
    pvars = {}
    new_pvars = {}
    def render(self, packet):
        data = ''
        if packet.mmpvars:
            data += to_vars(packet.mmpvars, self.new_pvars) + '\n'
            self.new_pvars = {}

        data += '%s\n.\n' % packet.body

        return data.encode('utf-8')

    def set_pvar(self, key, value):
        self.new_pvars[key] = value
        self.pvars[key] = value

    def del_pvar(self, key):
        self.new_pvars[key] = ''
        del self.pvars[key]


class PSYCRenderer:
    pvars = {}
    new_pvars = {}
    def render(self, packet):
        data = ''
        if packet.psycvars:
            data += to_vars(packet.psycvars, self.new_pvars)
            self.new_pvars = {}

        if packet.mc:
            data += packet.mc + '\n'

        if packet.data:
            data += packet.data

        return MMPPacket(packet.mmpvars, data)

    def set_pvar(self, key, value):
        self.new_pvars[key] = value
        self.pvars[key] = value

    def del_pvar(self, key):
        self.new_pvars[key] = ''
        del self.pvars[key]
