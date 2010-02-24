#!/usr/bin/env python
# -*- coding: utf-8 -*-

class PSYCPacket:
    def __init__(self, mmpvars = {}, psycvars = {}, mc = None, text = ''):
        self.mmpvars = mmpvars
        self.psycvars = psycvars
        self.vars = mmpvars.copy()
        self.vars.update(psycvars)
        self.mc = mc
        self.text = text

    def __repr__(self):
        return 'vars: %s, mc: %s, text: %s' % (self.vars, self.mc, self.text)
