from pypsyc.State import State

from twisted.protocols.basic import LineReceiver


class PSYCProtocol(LineReceiver):
    statemachine = None
    state = 'vars' 
    mc = None
    text = None
    delimiter = '\n'
    initialized = False
    def connectionMade(self):
        self.statemachine = State()
        self.reset()
        self.transport.write('.\n')
    def msg(self, vars, mc, text):
        """serialize a packet and send to the other side
        
        @type vars: C{dict}
        @param vars: Dictionary of variables to be serialized.
        Variables should be strings or lists, variable names start
        with an underscore
        
        @type mc: C{str}
        @param mc: Methodname of the packet, starts with an underscore

        @type text: C{str}
        @param text: Data part of the packet"""
        packet = self.statemachine.serialize(vars) # this has a newline already!
        packet += mc + '\n'
        packet += text + '\n'
        packet += '.\n'
        self.transport.write(packet.encode('iso-8859-1'))
    def reset(self):
        self.statemachine.reset()
        self.state = 'vars'
        self.mc = ''
        self.text = ''
    def lineReceived(self, line):
        """this does not yet handle binary mode and fragments"""
        line = line.strip()
        if self.initialized is False:
            if line != '.':
                self.msg({}, '_error_syntax_protocol_initialization',
                         'The protocol begins with a dot on a line of by itself')
                self.transport.loseConnection()
                return
            else:
                self.initialized = True
                return
        if line == '.':
            self.packetReceived()
        elif self.state is 'vars' and line.startswith('_'):
            self.statemachine.eat(None)
            self.mc = line 
            self.state = 'text' 
        elif self.state == 'vars':
            self.statemachine.eat(line)
        else:
            self.text += line + '\n'
    def packetReceived(self):
        vars = self.statemachine.copy()
        peer = self.transport.getPeer()
        if not vars.has_key('_source'):
            vars['_source'] = 'psyc://%s:-%d'%(peer.host, peer.port)
        mc = self.mc[:]
        data = self.text[:].strip().decode('iso-8859-1')
        self.reset()
        self.factory.packetReceived(vars, mc, data, self, peer)
