# TODO: write tests
from pypsyc import MMPVARS

from copy import deepcopy

class SenderState:
    def __init__(self):
        self.laststate = {}
        self.persistent_out = {}
    def serializeList(self, varname, value):
        t = []
        old = self.persistent_out.get(varname)
        # that is far to experimental
        if True: # not old: # no previous list sent
            self.persistent_out[varname] = value
            t.append(':%s\t%s\n'%(varname, value[0].replace('\n', '\n\t')))
            for item in value[1:]:
                t.append(':\t%s\n'%(item.replace('\n', '\n\t')))

        return '\n'.join(t) 
        if False:
            augmented = filter(lambda x: x not in old, value)
            if augmented:
                packet += '+%s\t%s\n'%(varname, augmented[0].replace('\n', 
                                                                     '\n\t'))
                for item in augmented[1:]:
                    packet += '+\t%s\n'%(item.replace('\n', '\n\t'))
            diminished = filter(lambda x: x not in value, old)
            if diminished:
                packet += '-%s\t%s\n'%(varname, diminished[0].replace('\n', 
                                                                      '\n\t'))
                for item in diminished[1:]:
                    packet += '-\t%s\n'%(item.replace('\n', '\n\t'))
            self.persistent_out[varname] = value
    def serialize(self, state):
        """
        serializes a set of variables into a string

        @type state: C{dict}
        @param state: Dictionary of variables to be serialized
        """
        L = []
        # beware of the lambdas!
        L.append(self.varencode(filter(lambda x: x[0] in MMPVARS and x[1], 
                                       state.items())))
        if L != []:
            L.append('\n')
        L.append(self.varencode(filter(lambda x: x[0] not in MMPVARS and x[1],
                                       state.items())))
        self.laststate = state
        bytes = '\n'.join(L)
        return bytes
    def varencode(self, v):
        """
        encodes a set of variables, setting the state persistent according to
        some strategy
        
        @type v: C{dict}
        @param v: Dictionary of variables to be serialized
        """
        t = []
        for (varname, value) in v:
            if self.persistent_out.get(varname) == value:
                pass
            elif varname.startswith('_list') or type(value) == type([]):
                t.append(self.serializeList(varname, value))
            elif self.laststate.get(varname) == value and varname != '_context':
                self.persistent_out[varname] = value
                t.append('=%s\t%s\n'%(varname, value.replace('\n', '\n\t')))
            else:
                t.append(':%s\t%s\n'%(varname, value.replace('\n', '\n\t')))
        return '\n'.join(t)


class ReceiverState:
    glyph = ''
    varname = ''
    listFlag = False
    value = ''
    def __init__(self):
        self.state = {}
        self.persistent = {}
    def reset(self):
        self.state = {}
        self.glyph = ''
        self.varname = ''
        self.listFlag= False
        self.value = ''
    def copy(self):
        # do we actually need those deep copys? TODO
        t = deepcopy(self.persistent)
        t.update(deepcopy(self.state)) 
        return t
    def eat(self, line):
        """
        this one is tricky... first it handles the previous line, 
        and then it prepares the current line.
        This is needed to implement multiline-continuations in lists

        @type line: C{str} or C{None}
        @param line: line to be parsed, a None signals that variable
        parsing for current packet is finished
        """
        if line: line = line.decode('iso-8859-1') # we use unicode internally
        if line and (line[0] == ' ' or line[0] == '\t'): # multiline support
            self.value += '\n' + line[1:]
            return

        # glyph handling
        if self.glyph == ':':
            if self.listFlag:
                if not type(self.state[self.varname]) == list:
                    self.state[self.varname] = [self.state[self.varname]]
                self.state[self.varname].append(self.value)
            else:
                if self.varname.startswith('_list'): 
                    self.value = [self.value]
                self.state[self.varname] = self.value
        elif self.glyph == '=':
            if self.listFlag:
                if not type(self.persistent[self.varname]) == list:
                    self.persistent[self.varname] = [self.self.persistent[self.varname]]
                self.persistent[self.varname].append(self.value)
            else:
                self.persistent[self.varname] = self.value
        elif self.glyph == '+':
            self.persistent.get(self.varname, []).append(self.value)
        elif self.glyph == '-':
            raise NotImplementedError
        elif self.glyph == '?':
            raise NotImplementedError

        if not line: # feeding done
            return

        # here we parse the current line
        self.glyph = line[0]
        if line[1] == '\t':
            # lastvarname-optimization: varname remains the same 
            self.listFlag = True
            self.value = line[2:]
        else:
            self.listFlag = False
            if line.find('\t') == -1:
                self.varname = line[1:]
                self.value = ''
            else: 
                self.varname, self.value = line[1:].split('\t', 1)
                self.value = self.value


class State(SenderState, ReceiverState):
    """combination of sender and receiver state"""
    def __init__(self):
        SenderState.__init__(self)
        ReceiverState.__init__(self)
