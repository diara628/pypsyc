from pypsyc.objects import PSYCObject
from pypsyc import parseUNL

from twisted.internet import defer
    
class GroupMaster(PSYCObject):
    """
    @type members: C{dict}
    @ivar members: list of members of the group
    """
    def __init__(self, netname, center):
        PSYCObject.__init__(self, netname, center)
        self.members = {}
        self.flat = {}
    def sizeof(self):
        return len(self.flat)
    def remove(self, whom, origin = None):
        self.flat.pop(whom, None)
        if origin is not None:
            self.members.get(origin, {}).pop(whom, None)
            if not self.members.get(origin, None):
                self.members.pop(origin, None)
        else:
            self.members.pop(whom, None)
    def insert(self, whom, origin = None, data = None):
        if not data: data = True
        self.flat[whom] = data
        if origin and not self.netname.startswith(origin):
            if not self.members.get(origin):
                self.members[origin] = {}
            self.members[origin][whom] = True
        else:
            self.members[whom] = True
    def getData(self, whose):
        return self.flat[whose]
    def setData(self, whose, data):
        self.flat[whose] = data
    def member(self, who):
        return who in self.flat
    def castmsg(self, vars, mc, data): 
        vars['_nick_place'] = 'muh' # IMHO _nick_place is superflous
        vars['_context'] = self.netname
        for (route, list) in self.members.items():
            # TODO: deepcopy needed?
            vars['_target'] = route
            self.center.sendmsg(vars, mc, data)


class GroupSlave:
    def __init__(self, netname, center):
        self.center = center
        self.context = netname
        self.members = {}
    def join(self, obj):
        url = obj.url()
        self.members[url] = obj
        # TODO: install a watcher on memberobj?
    def leave(self, obj):
        url = obj.url()
        if url in self.members:
            self.members.pop(url)
    def castmsg(self, vars, mc, data):
        for (target, obj) in self.members.items():
            vars['_target'] = target
            obj.msg(vars, mc, data)
       

class Place(GroupMaster):
    silent = False
    def __init__(self, netname, center):
        self.idcallbacks = {}
        self.identifications = {}
        self.reverseidentifications = {}
        GroupMaster.__init__(self, netname, center)
    def sendmsg(self, vars, mc, data):
        # things like setting vars['_nick_place']
        vars['_source'] = self.netname
        t = self.reverseidentifications.get(vars['_target'])
        if t:
            print 'setting target from %s to %s'%(vars['_target'], t)
            vars['_target'] = t 
        GroupMaster.sendmsg(self, vars, mc, data)
    def showMembers(self):
        return self.flat.keys()
    def showTopic(self):
        return ''
    def msg(self, vars, mc, data):
        if '_context' in vars:
            print '%s got %s with context %s from %s, bad' % (self.netname, mc,
                                                              vars['_context'],
                                                              vars['_source'])
            return
        ident = vars.get('_identification')
        source = vars['_source']
        if ident and self.identifications.get(source) == ident:
            print 'ident of %s is %s'%(source, 
                                       self.identifications[vars['_source']])
            vars['_source'] = ident
            vars.pop('_identification')
        GroupMaster.msg(self, vars, mc, data)
    def msg_error_invalid_authentication(self, vars, mc, data):
        print 'invalid auth'
        d = self.idcallbacks.pop((vars['_location'], vars['_source']), None)
        if d:
            d.errback(1)
    def msg_notice_authentication(self, vars, mc, data):
        print 'valid auth'
        d = self.idcallbacks.pop((vars['_location'], vars['_source']), None)
        if d:
            self.identifications[vars['_location']] = vars['_source']
            self.reverseidentifications[vars['_source']] = vars['_location']
            d.callback(1)
    def helper(self, res, vars, mc, data):
        self.msg(vars, mc, data)
    def msg_request_enter(self, vars, mc, data):
        source = vars['_source']
        if '_identification' in vars:
            ident = vars.get('_identification')
            print 'looking up identification %s'%(ident,)
            self.sendmsg({ '_target' : ident,
                         '_location' : source },
                         '_request_authenticate', 'Is that really you?')
            d = defer.Deferred()
            d.addCallback(self.helper, vars, mc, data)
            d.addErrback(self.helper, vars, mc, data)
            self.idcallbacks[(source, ident)] = d
            return
        # TODO: while it is not the final plan to make this via parseUNL
        #       it is acceptable for now
        origin = parseUNL(source)['root']
        v = { '_target' : source,
            '_source' : self.netname }
        if '_tag' in vars:
            v['_tag'] = vars['_tag']
        else:
            pass
        if '_nick' in vars:
            v['_nick'] = vars['_nick']
        else:
            pass
        if self.silent is True:
            v['_control'] = '_silent'
        self.sendmsg(v, '_echo_place_enter', 
                     '[_nick] enters')
        v.pop('_control', None)
        v.pop('_tag', None)
        
        v['_list_members'] = self.showMembers() + [ source ]
        self.sendmsg(v, '_status_place_members', '...')
            
        v.pop('_list_members')
        if not self.member(source): 
            v['_source'] = source
            self.castmsg(v, '_notice_place_enter', '[_nick] enters')
        self.insert(vars['_source'], origin)
    def msg_request_leave(self, vars, mc, data):
        source = vars['_source']
        # TODO again 
        origin = parseUNL(source)['root']
        v = { '_source' : source }
        if self.member(source):
            self.castmsg({ '_source' : source }, '_notice_place_leave', 
                         '[_nick] leaves')
            self.remove(source)
        else: # not a member for whatever reason
            self.sendmsg({ '_target' : source}, '_echo_place_leave',
                         'You are not even a member')
            pass
        if self.sizeof() == 0:
            # empty
            pass
    def msg_message_public(self, vars, mc, data):
        if self.silent is False and self.member(vars['_source']):
            self.castmsg(vars, mc, data)


class Person(GroupMaster):
    def __init__(self, netname, center):
        GroupMaster.__init__(self, netname, center)
        self.location = None
        self.forward = False
        self.places = {}
        self.tags = {}
    def disconnected(self, prot, loc):
        """client has closed connection"""
        self.location = None
        print 'should leave', places.keys()
        self.center.disconnected(prot, loc)
        print self.center.remote_connections
    def msg(self, vars, mc, data):
        if '_context' in vars and not vars['_context'] in self.places:
            # context faking, should be impossible as of now
            print 'catching fake context!'
            return
        # dont forward messages from our location to it...
        self.forward = vars['_source'] is not self.location
        GroupMaster.msg(self, vars, mc, data)
        if self.forward is True and self.location is not None:
            vars['_target'] = self.location
            self.sendmsg(vars, mc, data)
        self.forward = False
        # user is offline
    def sendmsg(self, vars, mc, data):
        # TODO: things like tag-creation for joins belong here
        # as well as setting vars['_nick']
        if not '_source' in vars or vars['_source'] == self.location: 
            vars['_source'] = self.netname
        if vars['_target'] == self.location:
            self.center.sendmsg(vars, mc, data)
        else:
            GroupMaster.sendmsg(self, vars, mc, data)
    def sendmsg_request_enter(self, vars, mc, data):
        import random
        t = str(random.randint(0, 10000))
        self.tags[vars['_target']] = t
        vars['_tag'] = t
        # tobi says, tags become invalid after a certain amount of time 
        self.center.sendmsg(vars, mc, data)
    def sendmsg_request_leave(self, vars, mc, data):
        # prepare to leave context after a reasonable amount of time
        self.center.sendmsg(vars, mc, data)
    def msgUnknownMethod(self, vars, mc, data):
        if not self.location:
            print 'person:unknown %s for offline user'%mc
    def msg_request_link(self, vars, mc, data):
        if vars['_password']: 
            self.msg_set_password(vars, mc, data)
        else: 
            self.sendmsg({ '_target' : vars['_source'] },
                         '_query_password', 'Is that really you?')

            self.forward = False
    def msg_set_password(self, vars, mc, data):
        """note that we have NO authorization"""
        # TODO: here we have to use origin
        if self.location is not None:
            self.sendmsg({ '_target' : self.location}, 
                         '_notice_unlink',
                         'You have just lost the magic feeling.')
        self.location = vars['_source']
        # TODO: we may need to deregister this thing...
        self.center.link_unl(self.location, self)
        self.sendmsg({ '_target' : self.location}, 
                     '_notice_link', 'You are now connected')
        self.forward = False
    def msg_request_unlink(self, vars, mc, data):
        if vars['_source'] == self.netname: # heh, this one is nifty!
            self.sendmsg({'_source' : self.netname, 
                         '_target' : self.location },
                         '_notice_unlink', 
                         'You have just lost the magic feeling.')
            self.location = None
            self.center.unlink_unl(self.location, self.netname)
        for place in self.places.copy():
            self.sendmsg({'_source' : self.netname, 
                         '_target' : place },
                         '_request_leave_logout',
                         'l8er')
        self.forward = False
    def msg_echo_place_enter(self, vars, mc, data):
        source = vars['_source']
        tag = vars.get('_tag')
        if not source in self.tags:
            self.forward = False
        elif self.tags[source] != tag:
            self.tags.pop(source) # wrong tag, you get invalid
            self.forward = False
        else:
            self.places[vars['_source']] = 1
            self.center.join_context(source, self)
    def msg_notice_place_leave(self, vars, mc, data):
        if vars['_source'] == self.netname:
            mc = '_echo' + mc[7:]
            vars['_source'] = vars['_context']
            self.msg(vars, mc, data)
    def msg_echo_place_leave(self, vars, mc, data):
        place = vars.get('_context') or vars['_source']
        if place in self.places:
            self.places.pop(place)
        self.forward = True
    def msg_request_roster(self, vars, mc, data):
        print 'Roster: %s'%(self.flat)
        self.sendmsg({'_source' : self.netname,
                     '_target' : self.location,
                     '_list_places' : self.places,
                     '_list_friends' : self.flat.keys()},
                     '_notice_roster', 
                     'Your friends are [_friends], you have entered in [_list_places].')
        self.forward = False
    def msg_request_friendship(self, vars, mc, data):
        """
        Friendship states:
            known -> 0
            asked from -> 1
            offered to -> 2
            dual accepted -> 3
        """
        source = vars['_source']
        if self.member(source) and self.getData(source) == 2:
            self.setData(source, 3)
            mc = '_notice_friendship_establshed'
            # TODO
        else:
            self.insert(source, None, 1)
        self.forward = True
    def sendmsg_request_friendship(self, vars, mc, data):
        target = vars['_target']
        if self.member(target) and self.getData(target) == 1:
            self.setData(target, 3)
            mc = '_notice_friendship_established'
            # TODO: echo_notice_friendship_established
        else:
            self.insert(target, None, 2)
        self.center.sendmsg(vars, mc, data)
        self.forward = True
    def msg_notice_friendship_established(self, vars, mc, data):
        source = vars['_source']
        if self.member(source) and self.getData(source) == 2:
            self.setData(source, 3)
