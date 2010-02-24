#!/usr/bin/env python
# -*- coding: utf-8 -*-

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
