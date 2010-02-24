#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Licensed under the MIT license
# http://opensource.org/licenses/mit-license.php

# <C> Copyright 2007, Manuel Jacob

from UI import base

class Interface(base.BaseUI):
    def __init__(self, factory):
        self.factory = factory
        self.factory.connect()
        #BaseUI.__init__(self)

    def _print(self, window, text):
        print '%s: %s' % (window, text)
