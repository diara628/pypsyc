#!/usr/bin/env python
# -*- coding: utf-8 -*-

## __init__.py


# Licensed under the MIT license
# http://opensource.org/licenses/mit-license.php

# <C> Copyright 2007, Manuel Jacob


import re

# the following two functions are from the 'original' pypsyc
# (and slightly modified)

def get_host(uni):
    m = re.match("^psyc:\/\/(.+)?\/~(.+)?\/?$", uni)
    if m: return m.group(1)

    m = re.match("^psyc:\/\/([^\/@]+)\@(.+?)\/?$", uni)
    if m: return m.group(2)
    
    m =  re.match("^psyc:\/\/(.+)?\/\@(.+)?\/?$", uni)
    if m: return m.group(1)

    m = re.match("^psyc:\/\/(.+)$", uni)
    if m: return m.group(1)

    raise "invalid uni"

def get_user(uni):
    m = re.match("^psyc:\/\/(.+)?\/~(.+)?\/?$", uni)
    if m: return m.group(2)

    m = re.match("^psyc:\/\/([^\/@]+)\@(.+?)\/?$", uni)
    if m: return m.group(1)

    raise "invalid uni"

def psyctext(packet):
    text = packet.data
    for key, value in packet.vars.items():
        text = text.replace('[%s]' % key, str(value))
    return text


class Vars(dict):
    def __init__(self, vars, existing = {}):
        dict.__init__(self, existing)
        self.vars = vars
        self.vars.update(existing)

    def __setitem__(self, key, value):
        dict.__setitem__(self, key, value)
        self.vars.__setitem__(key, value)


all_mmpvars = (
'_source', '_source_identification', '_source_location', '_source_relay',
'_target', '_context', '_counter', '_length', '_initialize', '_fragment',
'_encoding', '_amount_fragments', '_list_using_modules',
'_list_require_modules', '_list_understand_modules', '_list_using_encoding',
'_list_require_encoding', '_list_understand_encoding',
'_list_using_protocols', '_list_require_protocols',
'_list_understand_protocols', '_trace', '_tag', '_tag_relay', '_relay')
