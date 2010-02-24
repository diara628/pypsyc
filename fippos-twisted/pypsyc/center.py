#!/usr/bin/env python
from pypsyc import parseUNL, UNL2Location, netLocation

from twisted.internet import reactor, defer
from pypsyc.net import PSYCClientConnector, PSYCActiveConnector

from pypsyc import dump_packet


class Center:
    object_handlers = {}
    remote_connections = {}
    def msg(self, vars, mc, data):
        raise NotImplementedError

    def sendmsg(self, vars, mc, data, target = None):
        raise NotImplementedError

    def register_object(self, netname, object):
        # multiple handlers are not possible 
        # we only want lower case netnames
        self.object_handlers[netname.lower()] = object

    def find_object(self, netname):
        """find a local object that corresponds to netname"""
        # try "real/local" object"
        # we only have lower case netnames
        return self.object_handlers.get(netname.lower())

    def find_remote(self, netname):
        """find a remote location where netname may be located"""
        address = netLocation(netname)
        if self.remote_connections.has_key(address):
            return self.remote_connections[address]
        return None
    def register_remote(self, obj, where):
        self.remote_connections[where] = obj
    def unregister_remote(self, obj, where):
        if self.remote_connections.get(where) == obj:
            self.remote_connections.pop(where)
    def connect(self, location):
        raise NotImplementedError
    def create_user(self, netname):
        raise NotImplementedError
    def create_place(self, netname):
        raise NotImplementedError


class ClientCenter(Center):
    # connection to the homeserver, default return for find_remote
    default_connection = None
    options = {}
    def get_option(self, option):
        return self.options.get(option)
    def connect(self, location):
        # already connected or connecting?
        a = self.find_remote(location)
        if a: 
            return a
        a = PSYCClientConnector(self, location)
        return a.get_queue()
    def find_remote(self, netname):
        """clients will send most things via their homeserver
            p2p connections are an exception to that, but they will be 
            created by user objects"""
        return Center.find_remote(self, netname) or Center.find_remote(self, self.default_connection)
    def msg(self, vars, mc, data):
        if not mc:
            #print "warning: minor bug in pypsyc: msg() without mc"
            return
        if self.get_option('debug'): 
            dump_packet(">>>", vars, mc, data)
        source = vars.get('_context') or vars.get('_source')
        if not source: return # ignore empty packets?
        obj = self.find_object(source)
        if obj:
            obj.msg(vars, mc, data)
            return
        print 'unhandled packet from %s'%source
        # do something about it... pop up a window, etc
        u = parseUNL(source)
        if u['resource'] and u['resource'].startswith('~'):
            # create a user object
            obj = self.create_user(source)
            obj.msg(vars, mc, data)
        elif u['resource'] and u['resource'].startswith('@'):
            # create a place object
            obj = self.create_place(source)
            obj.msg(vars, mc, data)
        else:
            print 'no handler for %s object'%(source)
    def sendmsg(self, vars, mc, data):
        target = vars.get('_target')
        if not target: return
        obj = self.find_remote(target)
        if obj:
            obj.msg(vars, mc, data)
        else: 
            raise
        # this should not happen!


# TODO this does not belong here
import sha
class Authenticator:
    def __init__(self, center, uni, password):
        self.center = center
        self.uni = uni
        self.password = password
    def startLink(self):
        print 'start link'
        self.sendmsg({'_target' : uni }, '_request_link', '')
    def msg_query_password(self, vars, mc, data):
        if vars['_nonce'] and self.center.get_option('auth_sha'):
            digest = sha.sha(vars['_nonce'] + self.password).hexdigest()
            self.center.sendmsg({ '_method' : 'sha1',
                                '_password' : digest },
                                '_set_password', '')
        elif self.center.get_option('auth_plain'):
            self.sendmsg({ '_password' : self.password },
                         '_set_password', '')
        else:
            print 'no authorization method available!'
        return
        

class Client(ClientCenter):
    default_uni = ''
    nick = ''
    online_callback = None
    def __init__(self, config):
        self.config = config

        self.default_uni = config.get('main', 'uni')

        u = parseUNL(self.default_uni)
        self.nick = u['resource'][1:]
        self.default_connection = netLocation(self.default_uni)
        if self.config.has_section('library'):
            for option in self.config.options('library'):
                self.options[option] = self.config.getboolean('library', option)
    def online(self):
        self.connect(self.default_connection)
        # experimental API using the cool Deferred's
        self.online_callback = defer.Deferred()
        return self.online_callback
    def gotOnline(self):
	if self.online_callback:
	    self.online_callback.callback(None)
        print 'connected to host of default location'
    def sendmsg(self, vars, mc, data):
        if vars.get('_nick') == '': 
            vars['_nick'] = self.nick
        # TODO: I am not sure, it this is correct
        if vars.get('_source') == '':
            vars['_source'] = self.default_uni
        ClientCenter.sendmsg(self, vars, mc, data)


class ServerCenter(Center):
    unl2uni = {}
    remote_contexts = {}
    def __init__(self, location):
        self.location = location
    def msg(self, vars, mc, data):
        if not mc: 
            return # ignore empty packets
        source = vars['_source']
        # TODO: auth check 'global' or per-object
        if vars.has_key('_identification'):
            print 'Identification of %s is %s'%(source, vars['_identification'])
        context = vars.get('_context')
        if context and not self.is_local_object(context):
            target = context
        else:
            target = vars['_target']
        if self.unl2uni.has_key(source):
            """local client who is using us as a proxy"""
            self.unl2uni[source].sendmsg(vars, mc, data)
        elif target:
            obj = self.find_object(target) 
            if obj:
                return obj.msg(vars, mc, data)
            # probably object has to be created
            if self.is_local_object(target):
                u = parseUNL(target)
                if (u['resource'] and u['resource'].startswith('@')):
                    obj = self.create_place(target)
                    if obj:
                        return obj.msg(vars, mc, data)
                    else:
                        vars['_target'], vars['_source'] = vars['_source'], vars['_target']
                        self.sendmsg(vars, '_error_unknown_name_place',
                                     'No such place: [_source]')
                elif (u['resource'] and u['resource'].startswith('~')):
                    obj = self.create_user(target)
                    if obj:
                        return obj.msg(vars, mc, data)
                    else:
                        vars['_target'], vars['_source'] = vars['_source'], vars['_target']
                        self.sendmsg(vars, '_error_unknown_name_user', 
                                     'No such user: [_source]')
                elif u['resource']:
                    vars['_target'] = source
                    vars['_source'] = target
                    self.sendmsg(vars, '_error_unknown_name', 
                                 'No such object: [_source]')
                else: # rootmsg
                    pass
            elif context is not None and self.remote_contexts.has_key(context):
                self.remote_contexts[context].castmsg(vars, mc, data)
            else: # nonlocal target
                print 'rejected relay %s from %s to %s'%(mc, source, target)
                return # skip it for now
                self.sendmsg({ '_target' : source, '_source' : self.location,
                             '_destination' : target },
                             '_error_rejected_relay',
                             'You are not allowed to send messages to [_destination]')
        else:
            # no target???
            print 'no target in packet???'

    def sendmsg(self, vars, mc, data):
        target = vars['_target']    
        if self.is_local_object(target):
            self.msg(vars, mc, data)
        else:
            u = parseUNL(target)      
            target = (self.find_object(target) or
                      self.find_remote(target) or 
                      self.find_remote(target))
            if not target and u['scheme'] == 'psyc':
                q = self.connect(u['root'])
                q.msg(vars, mc, data)
            elif target: 
                target.msg(vars, mc, data)
            else:
                raise 'can not find %s'%(target) # programming error?
    def register_object(self, netname, object):
        self.object_handlers[netname.lower()] = object
    def link_unl(self, unl, uni):
        self.unl2uni[unl] = uni
    def unlink_unl(self, unl, uni):
        if self.unl2uni.has_key(unl) and self.unl2uni[unl] == uni:
            self.unl2uni.pop(unl)
    def is_local_object(self, location):
        return netLocation(location) == netLocation(self.location)
    def connect(self, location):
        a = PSYCActiveConnector(self, location, self.location)
        self.remote_connections[location] = a.get_queue() 
        return a.get_queue()
    def find_remote(self, netname):
        address = netLocation(netname)
        return self.remote_connections.get(address, None)       
    def join_context(self, context, obj):
        if self.is_local_object(context):
            print 'skipping join to local context'
        if not self.remote_contexts.has_key(context):
            self.remote_contexts[context] = self.create_context(context)
        self.remote_contexts[context].join(obj) 
    def leave_context(self, context, obj):
        if self.is_local_object(context):
            print 'skipping part of local context'
        if self.remote_contexts.has_key(context):
            self.remote_contexts[context].leave(obj)
        # TODO possibly clean_up that context
    def create_context(self, netname):
        """this is how we create context slaves"""
        raise NotImplementedError
