#!/usr/bin/env python
# -*- coding: utf-8 -*-

## packets.py


# Licensed under the MIT license
# http://opensource.org/licenses/mit-license.php

# <C> Copyright 2007, Manuel Jacob

from __init__ import Vars

class MMPPacket:
    def __init__(self, mmpvars = {}, body = ''):
        self.vars = {}
        self.mmpvars = Vars(self.vars, mmpvars)
        self.body = body


class PSYCPacket(MMPPacket):
    def __init__(self, mmpvars = {}, psycvars = {}, mc = None, data = ''):
        MMPPacket.__init__(self, mmpvars)
        self.psycvars = Vars(self.vars, psycvars)
        self.mc = mc
        self.data = data
