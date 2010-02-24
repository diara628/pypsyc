#!/usr/bin/env python
# -*- coding: utf-8 -*-

## parse.py


# Licensed under the MIT license
# http://opensource.org/licenses/mit-license.php

# <C> Copyright 2007, Manuel Jacob


from packets import MMPPacket, PSYCPacket

def parse_vars(lines):
    cvars = {}
    pvars = {}

    _list = None

    for i in lines:
        tmp = i.split('\t')
        if tmp[0] == ':':
            vars[_list].append(tmp[1])
            continue
            
        elif tmp[0].startswith(':'):
            vars = cvars

        elif tmp[0].startswith('='):
            vars = pvars

        if tmp[0][1:6] == '_list':
            _list = tmp[0][1:]
            vars[_list] = [tmp[1]]

        else:
            _list = None
            vars[tmp[0][1:]] = tmp[1]

    return cvars, pvars


class LineBased:
    def __init__(self):
        self.__buffer = ''
        self.linemode = True

    def data(self, data):
        self.__buffer += data
        while self.linemode and self.__buffer:
            try:
                line, self.__buffer = self.__buffer.split('\n', 1)
                self.line(line)
            except ValueError:
                return

        else:
            if not self.linemode:
                __buffer = self.__buffer
                self.__buffer = ''
                self.raw(__buffer)


class MMPParser(LineBased): # callback-based
    pvars = {}
    def __init__(self):
        LineBased.__init__(self)
        self.reset()

    def reset(self):
        self.mode = 'vars'
        self.varlines = []

        self.cvars = {}
        self.body = ''

    def line(self, line):
        if line == '.':
            self.recv()
        elif self.mode == 'vars':
            if line:
                self.varlines.append(line)
            else:
                self.cvars, pvars = parse_vars(self.varlines)

                for key, value in pvars.items():
                    if value:
                        self.pvars[key] = value
                    else:
                        if key in self.pvars:
                            del self.pvars[key]

                self.mode = 'body'

        else:
            self.body += line + '\n'

    def recv(self):
        vars = self.pvars.copy()
        vars.update(self.cvars)
        if self.body and self.body[-1] == '\n':
            self.body = self.body[:-1]
        packet = MMPPacket(vars, self.body)
        packet.not_to_render = True
        self.recv_packet(packet)
        self.reset()

    def recv_packet(self, packet):
        raise NotImplementedError


class PSYCParser:
    pvars = {}

    def parse(self, packet):
        lines = packet.body.split('\n')
        _is_text = False
        cvars = {}
        varlines = []
        textlines = []
        mc = ''

        for i in lines:
            if not i:
                continue

            tmp = i.split('\t')

            if _is_text:
                textlines.append(i)

            elif i[0] in (':', '='):
                varlines.append(i)

            elif i[0] == '_':
                cvars, pvars = parse_vars(varlines)

                for key, value in pvars.items():
                    if value:
                        self.pvars[key] = value
                    else:
                        if key in self.pvars:
                            del self.pvars[key]

                mc = i
                _is_text = True

        text = '\n'.join(textlines)
        vars = self.pvars.copy()
        vars.update(cvars)
        packet = PSYCPacket(packet.mmpvars, vars, mc, text)
        packet.not_to_render = True
        return packet


if __name__ == '__main__':
    MMPParser().data(':_context\ti\n=_foo\tbar\n\n_message_public\nHello\n.\n')
    MMPParser().data(':_context\ti\n\n_message_public\nHello\n.\n')
