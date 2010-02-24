# -*- coding: latin-1 -*-

#from wxPython.wx import *
import wx
# XXX Please feel free to modify and vershclimmbesser this piece of code
# especially the bits marked with XXX
##from pypsyc.objects.PSYCObject import 
from pypsyc.objects.client import ClientUser, ClientPlace, PSYCClient
from pypsyc.objects import PSYCObject
from pypsyc.center import ClientCenter

from pypsyc import netLocation, parsetext, UNL2Location
from displays import wxPFrame, wxPTab, wxPPlace, wxPUser, wxPClient
import asyncore, sys, os
import extras

class PObject(PSYCObject):
    def __init___(self, netname, center):
        PSYCObject.__init__(self, netname, center)
        self.context = extras.Context()
        self.display = extras.Display()
        self.queue = []  # a place to store pakets

    def create_display(self, display=None, parent=None, name = 'default'):
        """ create a new display for this object """
        # display := display object
        # parent := if we don't have a display object we need to create one
        #           and perhaps need a parent
        # name := the display needs a name so we can access it later
        if name == 'default':
            if self.display['default']:
                print 'there is already a default display, \
                    if you want a new display give it a unique name'
                return
        else:
            if display:
                # a display has to have some basic functionality
                self.display[name] = display
            else:
                # we're a bit confused now because we can't know what sort of
                # display to create, but perhas someone comes up with a idea later
                print 'HELP!'

    def msg(self, vars, mc, data, caller):
        PSYCObject.msg(self, vars, mc, data, caller)
        # store things until we know what do with them
        f = (vars, mc, data, caller)
        self.queue.append(f)


class wxCenter(wx.App, ClientCenter):
    def __init__(self): #vllt noch cmd line args uebergeben or so
        wx.App.__init__(self, 0)
        #self.run()

    def OnInit(self):
        ClientCenter.__init__(self)
        self.context = extras.Context()
        self.context.config = extras.Config()
        self.config = self.context.config

        self.frame = wxPFrame(psyc_parent=self)  # nen frame um die tabs aufzuheben
        self.timer = wx.PyTimer(self.socket_check)
        self.timer.Start(100) # alle 100 ms
        return True

    def socket_check(self):
        asyncore.poll(timeout=0.0) # das sollte vllt klappen

    def run(self):
        puni = UNL2Location(self.config['uni'])
        self.client = PClient(puni, self) 
        self.create_server_place(netLocation(self.config['uni']))
        # XXX extremly buggy here!!
        #self.create_server_place('psyc://adamantine.fippo.int')

        self.default_connection = netLocation(self.config['uni'])
        self.client.online() 
        self.client.create_display(self)
        self.SetTopWindow(self.client.display['default'])
        self.client.display['default'].Show()

        self.MainLoop()
        
    def sendmsg(self, vars, mc, data, caller = None):
        extras.print_psyc(vars, mc, data, 'center sending')
        ClientCenter.sendmsg(self, vars, mc, data, caller)

    def set_default_connection(self, uni):
        #netLocation(self.uni)
        print 'set_default_connect: ' + netLocation(uni)
        self.default_connection = netLocation(uni)

    def msg(self, vars, mc, data, caller):
        source = vars['_context'] or vars['_source']
        if not ClientCenter.msg(self, vars, mc, data, caller):
            # create a psyc object of unknown type
            #self.create_psyc_object(source)
            #print '\n\n !!WE ARE IN TROUBLE!!\n\n\n'
            print ''
    
    def create_psyc_object(self, netname):
        # this could do some better guessing about the type
        self.create_server_place(netname)
        # XXX

    def create_user(self, netname):
        t = PUser(netname, self)
        #print 'i am a USER and my name is: ' + netname + ' / ' + netLocation(netname)
        self.frame.addTab(t)
        return t

    def create_place(self, netname):
        t = PPlace(netname, self)
        #print 'i am a PLACE and my name is: ' + netname + ' / ' + netLocation(netname)
        self.frame.addTab(t)
        return t

    def create_server_place(self, netname):
        t = PServer(netname, self)
        #print 'i am a SERVER and my name is: ' + netname + ' / ' + netLocation(netname)
        self.frame.addTab(t)
        self.client.create_display(name='server', display=t.display['default'])
        #sys.stdout = extras.DevNull()
        return t	

class PPlace(ClientPlace):
    def __init__(self, netname, center):
        ClientPlace.__init__(self, netname, center)
        self.display = extras.Display()
        print 'i am a PLACE and my name is: ' + self.netname + ' / ' + netLocation(self.netname)

    def create_display(self, parent = None, name = 'default', display = None):
        if name == 'default':
            self.display['default'] = wxPPlace(parent=parent, psyc_parent=self)
        else:
            self.display[name] = display

    def msg(self, vars, mc, data, caller = None):
        extras.print_psyc(vars, mc, data, 'place')
        #print 'ddd' +  str(type(data))
        parsedtext = parsetext(vars, mc, data)
        #print dir(parsedtext) , type(parsedtext)
        #parsedtext = parsedtext.encode('iso-8859-15')
        #print type(parsedtext)
        if mc == '_message_public':
            line = u''
            if vars['_nick']: 
                line += vars['_nick']
            else:
                line += vars['_source']
            
            if vars['_action']: line += ' ' + vars['_action'] + '>'
            else: line += '>'
            try:
                line += ' ' + parsedtext.decode('iso-8859-15')
            except:
                line += ' ' + parsedtext
            self.display.append1(line)
        elif mc == '_message_public_question':
            line = u''
            line += vars['_nick']
            if vars['_action']: line += ' ' + vars['_action'] + '>'
            else: line += ' fragt>'
            try:
                line += ' ' + parsedtext.decode('iso-8859-15')
            except:
                line += ' ' + parsedtext
            self.display.append1(line)
        elif mc.startswith('_status_place_topic'):
            self.display.append1('TOPIC: ' + parsedtext)
        else:
            self.display.append1(parsedtext)


class PUser(ClientUser):
    def __init__(self, netname, center):
        ClientUser.__init__(self, netname, center)
        self.display = extras.Display()
        print 'i am a USER and my name is: ' + self.netname + ' / ' + netLocation(self.netname)

    def create_display(self, parent = None, name = 'default', display = None):
        if name == 'default':
            self.display['default'] = wxPUser(parent=parent, psyc_parent=self)
        else:
            self.display[name] = display

    def msg(self, vars, mc, data, caller = None):
        extras.print_psyc(vars, mc, data, caller)
        parsedtext = parsetext(vars, mc,data)
        #parsedtext = parsedtext.encode('iso-8859-15')
        if mc == '_message_private':
            self.display.append1(parsedtext)
        else:
            self.display.append1(parsedtext)


class PServer(PSYCObject):
    def __init__(self, netname, center):
        PSYCObject.__init__(self, netname, center)
        print 'registered server'
        #print 'PServer: ' + str(dir(self))
        self.display = extras.Display()
        print 'i am a SERVER and my name is: ' + self.netname + ' / ' + netLocation(self.netname)

    def create_display(self, parent = None, name = 'default', display = None):
        if name == 'default':
            self.display['default'] = wxPPlace(parent=parent, psyc_parent=self)
        else:
            self.display[name] = display

    def msg(self, vars, mc, data, caller = None):
        extras.print_psyc(vars, mc, data, 'server')
        parsedtext = parsetext(vars, mc,data)
        #parsedtext = parsedtext.encode('iso-8859-15')
        #self.center.Yield()
        if mc == '_notice_circuit_established' and vars['_source'] == netLocation(self.center.config['uni']):
            mc = '_request_link'
            vars = {}
            data =''
            vars['_target'] = self.center.config['uni']
            self.sendmsg(vars, mc, data)
            self.display.append1(parsedtext)
        else:
            self.display.append1(parsedtext)

    def write(self, text):
        """ redirected stdout """
        # we have problems if text contains \n and with print adding an extra \n
        lines = text.split('\n')
        for line in lines:
            if line == '':
                return
            else:
                self.display.append1('printed: ' + line)

    def sendmsg(self, vars, mc, data, caller = None):
        extras.print_psyc(vars, mc, data, 'server sending...')
        PSYCObject.sendmsg(self, vars, mc, data, caller)


class PClient(PSYCClient):
    def __init__(self, netname, center):
        PSYCClient.__init__(self, netname, center)
        self.display = extras.Display()
        #self.extra_display = {} # XXX
        #self.create_display(parent=None)
        print 'default_conmnect is --> ' + self.center.default_connection
        print 'i am a CLIENT and my name is: ' + self.netname + ' / ' + netLocation(self.netname)

    def create_display(self, parent = None, name = 'default', display = None):
        if name == 'default':
            self.display[name] = wxPClient(parent=parent, psyc_parent=self)
        else:
            if self.display.has_key(name):
                # XXX tempory hack for multi server connect
                print 'HACKING GOING ON!'
                return
            else:
                self.display[name] = display

    def set_display(self, which, display):
        self.display[which] = display

    def msg(self, vars, mc, data, caller = None):
        extras.print_psyc(vars, mc, data, 'client')
        parsedtext = parsetext(vars, mc,data)
        #parsedtext = parsedtext.encode('iso-8859-15')
        if mc == '_query_password':
            if self.center.config['password'] != '':
                mc = '_set_password'
                vars = {'_password' : self.center.config['password']}
                vars['_target'] = self.netname
                data =''
                self.sendmsg(vars, mc, data)
            else:
                self.display['server'].append1("Please enter your password or choose a different nick if you don't know the password")
                self.display['server'].entry_box.SetValue('/password ')
        elif mc == '_status_friends':
            self.display['server'].append1(parsedtext)

        elif mc == '_error_invalid_password':
            self.display['server'].append1(parsedtext)
            self.display['server'].append1("Please enter your password or choose a different nick if you don't know the password")
            self.display['server'].entry_box.SetValue('/password ')
        else:
            self.display['server'].append1(parsedtext)

    def online(self):
        self.center.connect(self.center.default_connection)
        #mc = '_request_link'
        #mmp = {}
        #psyc = {}
        #data =''
        #mmp['_target'] = self.netname
        
        #self.sendmsg(mmp, psyc, mc, data)
