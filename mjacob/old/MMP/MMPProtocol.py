#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Licensed under the MIT license
# http://opensource.org/licenses/mit-license.php

# <C> Copyright 2007, Manuel Jacob

from twisted.protocols import basic


def convert_lines(lines):
    """convert list of lines to vars, method (mc) and text"""
    _is_text = False
    dict = {}
    mc = None
    textlines = []
    for i in lines:
        tmp = i.split('\t')

        if _is_text:
            textlines.append(i)

        elif tmp[0] == ':': # second or later item in the list
            dict[_list].append(tmp[1])

        elif i[0] in (':', '='):
            if tmp[0][1:6] == '_list':
                _list = tmp[0][1:]
                dict[_list] = [tmp[1]]
            else: dict[tmp[0][1:]] = tmp[1]

        elif i[0] == '_':
            mc = i
            _is_text = True

    text = '\n'.join(textlines)
    return dict, mc, text


class MMPProtocol(basic.LineReceiver):
    def __init__(self, callback):
        self.msg = callback
        self.delimiter = '\n'
        self.initialized = False
        self.charset = 'UTF-8'
        self.reset()

    def reset(self):
        self.lines = []
        self._reset()

    def _reset(self):
        raise NotImplementedError('Implement in Subclass.')

    def lineReceived(self, line):
        if not self.initialized:
            assert line == '.', 'first line is not ".", line is "%s"' % line
            self.initialized = True
            return

        if line == '.': # packet ends
            self.recv_packet()
        else:
            self.lines.append(line)

    def recv_packet(self):
        h2b = self.lines.index('') # head to body delimiter
        mmp = self.lines[:h2b]
        data = self.lines[h2b+1:]
        mmpvars = convert_lines(mmp)[0]
        if '_length' in mmpvars:
            bodylength = mmpvars['_length']
        else:
            bodylength = len(data)

        if len(data) == bodylength:
            self._recv_packet(mmpvars, data)
            self.reset()

    def _recv_packet(self, mmpvars, data):
        raise NotImplementedError('Implement in Subclass.')

    def _send_packet(self, mmpvars, data):
        mmpstring = ''
        if mmpvars:
            for key, value in mmpvars.items():
                mmpstring += "=%s\t%s\n" % (key, value)

        if not data:
            data = ''

        send = "%s%s.\n" % (mmpstring, data)
        #print ('send', send.encode(self.charset))
        self.transport.write(send.encode(self.charset))
