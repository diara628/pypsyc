# usage: twistd -noy ircd.py

import sys
from twisted.application import service, internet
from pypsyc.center import ServerCenter
from pypsyc.net import PSYCServerFactory
from pypsyc.objects import PSYCReceiver
from pypsyc.objects.server import Person, Place, GroupSlave
from pypsyc import parseURL

from twisted.protocols import irc 
from twisted.internet.protocol import ServerFactory


"""
watch out, the main purpose of this thing is to debug the context slave
system
"""

class IRCD(irc.IRC, PSYCReceiver):
    center = None
    password = ''
    nick = ''
    url = ''
    source = None
    def __init__(self, center, hostname):
	self.center = center
        self.hostname = hostname
    def connectionMade(self):
        peer = self.transport.getPeer()
        self.source = 'object:%s:%d'%(peer.host, peer.port)
        self.center.register_object(self.source, self)
    def connectionLost(self, reason):
        if self.url:
            self.irc_QUIT(None, None)
        elif self.nick is '':
            print 'closing unknown connection'
    def sendNumeric(self, numeric, msg):
        self.sendLine(':%s %s %s :%s'%(self.hostname, numeric, self.nick, msg))
#   def sendLine(self, line):
#       irc.IRC.sendLine(self, line.encode('iso-8859-1'))
    def sendMessage(self, source, target, cmd, data = None):
        s = ':%s %s %s'%(self.url2prefix(source), target, cmd)
        if data: 
            s += ' :%s'%data
        self.sendLine(s)
    def sNotice(self, data):
        self.sendLine(':%s NOTICE %s :%s'%(self.hostname, self.nick, data))
    """helper functions"""
    def expandUrl(self, target):
        """quick and dirty is_uniform check"""
        if target.find(':') is -1:
            if target[0] == '#':
                return self.hostname + '/@%s'%target[1:]
            return self.hostname + '/~%s'%target
        if target[0] == '#':
            return target[1:]
        return target
    def minimizeUrl(self, source):
        if source.startswith(self.hostname):
            # remark: +2 to skip trailing /@
            return source[len(self.hostname) + 2:]
        return source
    def url2prefix(self, url):
        if url.find(':') != -1:
            u = parseURL(url)
            if u['resource'][0] == '~':
                ident = u['resource'][1:]
            else:
                ident = '*'
            host = u['host']
        else:
            ident = url # its a local nick
            host = 'localuser'
        return '%s!%s@%s'%(url, ident, host)

    """irc_ command hooks"""
    def irc_USER(self, prefix, params):
        pass
    def irc_PASS(self, prefix, params):
        self.password = params[0]
    def irc_NICK(self, prefix, params):
        self.nick = params[0]
        self.center.msg({'_source' : self.source, 
                        '_target' : self.expandUrl(self.nick),
                        '_password' : self.password},
                        '_request_link', '')
    def irc_PRIVMSG(self, prefix, params):
        target = params[0]
        mc = '_message_private'
        if target[0] == '#': 
            mc = '_message_public'
        self.center.msg({ '_source' : self.source, 
                        '_target' : self.expandUrl(target),
                        '_nick' : self.nick}, 
                        mc, params[-1])
    def irc_JOIN(self, prefix, params):
        chan = params[0]
        self.center.msg({ '_source' : self.source,
                        '_target' : self.expandUrl(chan), 
                        '_nick' : self.nick}, 
                        '_request_enter', '')
    def irc_PART(self, prefix, params):
        chan = params[0]
        self.center.msg({ '_source' : self.source,
                        '_target' : self.expandUrl(chan),
                        '_nick' : self.nick},
                        '_request_leave', '')
    def irc_QUIT(self, prefix, params):
        self.center.msg({ '_source' : self.source,
                        '_target' : self.url },
                        '_request_unlink', '')
    def irc_unknown(self, prefix, command, params):
        if command == 'ROSTER':
            self.center.msg({ '_source' : self.source,
                            '_target' : self.url },
                            '_request_roster', '')
        elif command == 'FRIEND':
            self.center.msg({ '_source' : self.source, 
                            '_target' : self.expandUrl(params[0]) },
                            '_request_friendship', 'Lass uns Freunde sein')
        else:
            print 'unknown irc cmd %s'%command
    """pypsyc msg API"""
    def msgUnknownMethod(self, vars, mc, data):
        print 'unsupported %s from %s'%(mc, vars['_source'])
    def msg_notice_link(self, vars, mc, data):
        self.url = vars['_source']
        self.sendNumeric(irc.RPL_WELCOME, 'Hello, %s'%self.nick)
        self.sendNumeric(irc.RPL_YOURHOST, 'Welcome to %s'%self.hostname)
        self.sendNumeric(irc.RPL_MYINFO, '%s is a pyPSYC daemon IRC interface'%self.hostname)
    def msg_message_private(self, vars, mc, data):
        if vars['_target'] is self.source:
            t = self.nick
        else: # should not happen
            raise
        # TODO: might be appropriate to use self.privmsg()
        # self.privmsg(vars['_source'], self.nick, None, data)
        s = self.minimizeUrl(vars['_source'])
        self.sendMessage(s, 'PRIVMSG', t, data)
    def msg_message_echo_private(self, vars, mc, data):
        pass # echo is not common in irc
    def msg_message_public(self, vars, mc, data):
        if vars['_source'] != self.url: # skip echo
            if vars.has_key('_context'):
                t = '#' + self.minimizeUrl(vars['_context'])
            else:
                t = '#' + self.minimizeUrl(vars['_source'])
            s = self.minimizeUrl(vars['_source'])
            # TODO: might be appropriate to use self.privmsg()
            # self.privmsg(vars['_source'], None, t, data)
            self.sendMessage(s, 'PRIVMSG', t, data)
        else:
            pass # echo is not common in IRC
    def msg_echo_place_enter(self, vars, mc, data):
        t = '#' + self.minimizeUrl(vars['_source'])
        self.sendMessage(self.nick, 'JOIN', t)
    def msg_echo_place_leave(self, vars, mc, data):
        t = '#' + self.minimizeUrl(vars['_source'])
        self.sendMessage(self.nick, 'PART', t)
    def msg_status_place_members(self, vars, mc, data):
        t = '#' + self.minimizeUrl(vars['_source'])
        self.names(self.nick, t, map(self.minimizeUrl, vars['_list_members']))
    def msg_notice_unlink(self, vars, mc, data):
        if vars['_source'] == self.url:
            self.url = None
            self.transport.loseConnection()
    def msg_notice_place_enter(self, vars, mc, data):
        s = vars['_source']
        c = '#' + self.minimizeUrl(vars['_context'])
        if s == self.url: 
            return # we dont like being joined via notice!
        self.join(self.url2prefix(self.minimizeUrl(s)), c)
    def msg_notice_place_leave(self, vars, mc, data):
        s = vars['_source']
        c = '#' + self.minimizeUrl(vars['_context'])
        self.part(self.url2prefix(self.minimizeUrl(s)), c)
    def msg_notice_roster(self, vars, mc, data):
        friends = vars['_list_friends']
        places = vars['_list_places']
        if friends:
            self.sNotice('Friends')
            for friend in vars['_list_friends']:
                self.sNotice('~ %s'%friend)
        if places:
            self.sNotice('Places')
            for place in places:
                self.sNotice('@ %s'%place)
    def msg_request_friendship(self, vars, mc, data):
        sni = self.minimizeUrl(vars['_source'])
        self.notice(sni, self.nick, 
                    '%s wants to be your friend'%(sni))
    def msg_notice_friendship_established(self, vars, mc, data):
        sni = self.minimizeUrl(vars['_source'])
        self.notice(sni, self.nick, 
                    '%s is now your friend'%(sni))

class IRCDFactory(ServerFactory):
    center = None
    def __init__(self, center, location):
	self.center = center
        self.location = location
    def buildProtocol(self, addr):
        p = IRCD(self.center, self.location)
        p.factory = self
        return p

class MyServerCenter(ServerCenter):
    def create_user(self, netname):
	return Person(netname, self)
    def create_place(self, netname):
        return Place(netname, self)
    def create_context(self, netname):
        return GroupSlave(netname, self)


root = 'psyc://ente' # TODO: this does belong into a config file!
application = service.Application('psycserver')

center = MyServerCenter(root)
    
factory = PSYCServerFactory(center, None, root)
psycServer = internet.TCPServer(4404, factory)

ircfactory = IRCDFactory(center, root)
ircServer = internet.TCPServer(6667, ircfactory)

myService = service.IServiceCollection(application)
psycServer.setServiceParent(myService)
ircServer.setServiceParent(myService)
