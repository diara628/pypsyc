"""network code for pyPSYC"""

from pypsyc import GLYPHS

from pypsyc.PSYC import PSYCProtocol
from pypsyc import parseUNL, UNL2Location

from twisted.names import client
from twisted.internet import reactor
from twisted.internet.protocol import ClientFactory, ServerFactory


class HostChecker:
    """checks validity of _source/_context in a packet
        this could well implement policies like trusted from localhost"""
    def __init__(self, center, target, myname):
        self.target = target
        self.myname = myname
        self.center = center
    def check(self, vars, mc, data, protocol, peer):
        source = vars.get('_context') or vars.get('_source')
        if (source and not 
            source.startswith('psyc://%s'%(peer.host))):
            u = parseUNL(source)
            d = client.lookupAddress(u['host'])
            d.addCallback(self.resolved, peer.host, vars, mc, data, protocol)
        elif source:
            # numeric address
            self.handle(vars, mc, data, protocol)
        else:
            protocol.msg({ '_source' : self.myname }, 
                        '_error_syntax_protocol_missing_source', 
                        'Your implementation is broken')
    def handle(self, vars, mc, data, protocol):
        method = getattr(self, 'recv%s'%mc, None)
        if method is not None:
            method(vars, mc, data, protocol) 
        else:
            u = parseUNL(vars['_source'])
            self.center.register_remote(protocol, u['root'])
            self.center.msg(vars, mc, data)
    def resolved(self, record, shouldbe, vars, mc, data, protocol):
        v = { '_source' : self.myname, 
            '_target' : vars['_source'] }
        if not record[0]:
            print 'name not resolvable'
            protocol.msg(v, '_error_rejected_relay', 
                       '[_source] is not resolvable. Goodbye')
            protocol.transport.loseConnection()
        elif record[0][0].type == 5:
            payload = record[0][0].payload
            d = client.lookupAddress(payload.name.name)
            d.addCallback(self.resolved, shouldbe, vars, mc, data, protocol)
        else:
            payload = record[0][0].payload
            if payload.dottedQuad() == shouldbe:
                self.handle(vars, mc, data, protocol)
            else: 
                print 'rejected relay'
                protocol.msg(v, '_error_rejected_relay', 
                           '[_source] does not resolve to your ip.')
                protocol.transport.loseConnection()
  

class PSYCConnector:
    hostname = ''
    port = 4404
    factory = None
    factory_type = None
    real_hostname = ''
    def __init__(self, center, target, myname = None):
        # TODO: dont try to resolve IP addresses ;)
        # must subclass
        if not self.factory_type: raise NotImplementedError
        try:
            self.factory = self.factory_type(center, target, myname)
        except:
            print self.factory_type
            raise
        u = parseUNL(target)
        self.host = u['host']
        d = client.lookupService('_psyc._tcp.' + self.host)
        d.addCallback(self.srvResolved)
    def get_queue(self):
        return self.factory
    def resolved(self, record):
        if not record[0]:
            print 'resolution failed...'
        else:
            payload = record[0][0].payload
            if record[0][0].type == 5: # evil cname
                d = client.lookupAddress(payload.name.name)
                d.addCallback(self.resolved)
            else:
                reactor.connectTCP(payload.dottedQuad(), self.port, self.factory)
        return True
    def srvResolved(self, record):
        if not record[0]:
            d = client.lookupAddress(self.host)
            d.addCallback(self.resolved)
        else: 
            payload = record[0][0].payload
            self.port = payload.port
            d = client.lookupAddress(payload.target.name)
            d.addCallback(self.resolved)
        return True


class PSYCClientFactory(ClientFactory):
    """a factory for a client which does not have to check
        for validity of host names"""
    class PSYCClient(PSYCProtocol):
        def connectionMade(self):
            PSYCProtocol.connectionMade(self)
            self.factory.connectionMade(self)

    protocol = PSYCClient
    center = None
    location = None
    def __init__(self, center, location, myname):
        self.center = center
        self.location = location
    def connectionMade(self, proto):
        self.center.register_remote(proto, self.location)
        self.center.gotOnline()
    def packetReceived(self, vars, mc, data, protocol, peer):
        self.center.msg(vars, mc, data)
    
  
class PSYCClientConnector(PSYCConnector):
    factory_type = PSYCClientFactory


class PSYCActiveFactory(ClientFactory, HostChecker):
    """a factory for a client which does hostname checks
        maybe this will also become a Q
        probably we want to override connectionMade?"""
    protocol = PSYCProtocol
    queue = []
    connected = None
    def packetReceived(self, vars, mc, data, protocol, peer):
        self.check(vars, mc, data, protocol, peer) 
    def msg(self, vars, mc, data):
        # watch out, if we dont use dict-vars we may need deepcopy
        if self.connected is not None:
            self.connected.msg(vars, mc, data)
        else:
            self.queue.append((vars, mc, data))
    def run_queue(self, target):
        for (vars, mc, data) in self.queue:
            target.msg(vars, mc, data) 
        self.queue = []
        self.connected = target
    def recv_notice_circuit_established(self, vars, mc, data, protocol):
        print 'got _notice_circuit_established'
        protocol.msg({'_source' : self.myname, 
                     '_target' : self.target or vars['_source'] },
                     '_notice_circuit_established',
                     'hi there')
        # TODO: what do we register here? source oder our definition of 
        # what the source should be (self.target)
        self.center.register_remote(protocol, self.target)
        self.run_queue(protocol)

    
class PSYCActiveConnector(PSYCConnector):
    factory_type = PSYCActiveFactory


class PSYCServerFactory(ServerFactory, HostChecker):
    """funny question... do we deal all the stuff about 
        modules, compression, tls etc here?"""
    class PSYCServerProtocol(PSYCProtocol):
        def connectionMade(self):
            peer = self.transport.getPeer()
            PSYCProtocol.connectionMade(self)
            self.msg({ '_source' : self.factory.myname, 
                     '_target' : 'psyc://%s:-%d'%(peer.host, peer.port)}, 
                     '_notice_circuit_established', 
                     'Connection to [_source] established')

    protocol = PSYCServerProtocol
    def packetReceived(self, vars, mc, data, protocol, peer):
        self.check(vars, mc, data, protocol, peer) 
    def recv_notice_circuit_established(self, vars, mc, data, protocol):
        self.center.register_remote(protocol, vars['_source'])
