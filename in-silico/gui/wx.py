# -*- coding: latin-1 -*-
from wxPython.wx import *

# XXX Please feel free to modify and vershclimmbesser this piece of code
# especially the bits marked with XXX
##from pypsyc.objects.PSYCObject import 
from pypsyc.objects.PSYCObject import ClientUser, ClientPlace, PSYCClient, PSYCObject
from pypsyc.center import ClientCenter

from pypsyc import netLocation, parsetext

import asyncore, sys, os

# ich glaub ich weiss jetzt wofuer die hier toll sind
# !!!
# this list isn't up-to-date anymore, stolen from the old gui code
# !!!
ID_ABOUT = 1002
ID_CONNECT = 1001
ID_DISCONNECT = 10011
ID_SAY = 3300
ID_NOTEBOOK = 3301
ID_STATUS = 9901
ID_MENU = 9902
ID_BUDDY_LIST = 9903
ID_BUDDY_LIST_DK = 990301
ID_EXIT = 1099
ID_CLOSECHATNOTEBOOK = 2099
ID_CLOSECHATNOTE = 2098

def opj(path):
	"""Convert paths to the platform-specific separator"""
	return apply(os.path.join, tuple(path.split('/')))
	
def print_psyc(vars, mc, data, caller = ''):
	print '------ ' + str(caller)
	print '-- mc:'
	print mc
	print '-- vars:'
	print str(vars.items())
	print '-- data:'
	print str([data])
	print '------'
	
	
class DevNull:
	def write(self, text):
		return

class wxCenter(wxApp, ClientCenter):
	def __init__(self): #vllt noch cmd line args uebergeben or so
		wxApp.__init__(self, 0)
		self.run()

	def OnInit(self):
		ClientCenter.__init__(self)
		self.config = {} # = { 'uin' : 'psyc://blah/~user', 'foo': 'bar'}
		self.config[u'uni'] = u'psyc://ve.symlynx.com/~betatim3'
		self.config[u'password'] = u'tim'
		self.config[u'action'] = u'brabbel'
		self.config[u'bgcolour'] = (255, 236, 191)
		self.config[u'fontcolour'] = (34, 63, 92)
		self.config[u'fontsize'] = 8
		self.config[u'prompt'] = u'* '
		print sys.getdefaultencoding()
		print os.name

		#print self.config
		self.frame = wxPFrame(logic_parent=self)	# nen frame um die tabs aufzuheben
		self.client = PClient(self.config['uni'], self) 
		self.create_server_place(netLocation(self.config['uni'])) # eignetlich is es kein place aber naja

		self.default_connection =  netLocation(self.config['uni'])
		self.client.online() 
		self.client.create_display(self)
		self.SetTopWindow(self.client.display)
		self.client.display.Show()

		self.timer = wxPyTimer(self.socket_check)
		self.timer.Start(100) # alle 100 ms
		return True

	def input(self, event):
		print event.GetString()
		event.Skip()

	def socket_check(self):
		asyncore.poll(timeout=0.0) # das sollte vllt klappen

	def run(self):
		self.MainLoop()
		
	def sendmsg(self, vars, mc, data, caller = None):
		print_psyc(vars, mc, data, 'center sending')
		ClientCenter.sendmsg(self, vars, mc, data, caller)

	def set_default_connection(self, uni):
		#netLocation(self.uni)
		print 'set_default_connect: ' + netLocation(uni)
		self.default_connection = netLocation(uni)

	def create_user(self, netname):
		#print "this should create a user"
		t = PUser(netname, self)
		# nicht tab.display damit wir netname haben ,]]
		# auch wenn es extrem strange ist wir uebergeben
		self.frame.addTab(t)
		return t

	def create_place(self, netname):
		#print "this should create a room"
		t = PPlace(netname, self)
		self.frame.addTab(t) # same here
		return t

	def create_server_place(self, netname):
		t = PServer(netname, self)
		self.frame.addTab(t, extra_display='server') # same here
		sys.stdout = t
		return t


class wxPTab(wxPanel):
	def __init__(self, parent, logic_parent = None):
		""" all das ausehen usw """
		wxPanel.__init__(self, parent, -1, style=0)
		# we use logic_parent to call the functions pypsyc provides
		# gui stuff in the wxBlah objects, psyc stuff in the PBlah objects
		if not logic_parent: print 'WARNING: no logic_parent set, this could be a problem'
		self.logic_parent = logic_parent
		config = self.logic_parent.center.config
		self.prompt = config['prompt']
		self.lock = 0
		self.counter = 0
		self.buffer = ''
		self.text_box = wxTextCtrl(self, -1, style=wxTE_MULTILINE|wxTE_RICH2|wxTE_READONLY, size=wxDefaultSize)
		self.entry_box = wxTextCtrl(self, ID_SAY, style=wxTE_PROCESS_ENTER|wxTE_RICH2|wxTE_PROCESS_TAB, size=wxDefaultSize)
		
		fontcolour = wxColour(config['fontcolour'][0], config['fontcolour'][1], config['fontcolour'][2])
		bgcolour = wxColour(config['bgcolour'][0], config['bgcolour'][1], config['bgcolour'][2])
		self.entry_box.SetBackgroundColour(bgcolour)
		self.text_box.SetBackgroundColour(bgcolour)
		points = self.text_box.GetFont().GetPointSize() # get the current size
		f = wxFont(points, wxMODERN, wxNORMAL, wxBOLD, False)
		self.text_box.SetDefaultStyle(wxTextAttr(fontcolour, bgcolour, f))
		self.entry_box.SetDefaultStyle(wxTextAttr(fontcolour, bgcolour, f))
		self.SetBackgroundColour(bgcolour)
		
		sizer = wxBoxSizer(wxVERTICAL)
		sizer.Add(self.text_box, 1, wxEXPAND)
		sizer.Add(self.entry_box, 0, wxEXPAND)
		self.SetSizer(sizer)

		#print 'wxPTab: ' + str(dir(self))
		EVT_TEXT_ENTER(self, ID_SAY, self.input)

	def input(self, event):
		text = event.GetString()
		text = text.lstrip() # only strip whites from the beginning
		mc = ''
		vars = {}
		data = ''
		vars['_target'] = self.logic_parent.netname # eigentlich is target immer netname
		if text != '' and text[0] == '/':
			# houston we have a command
			if text.startswith("/join"): # and text.__len__() > 16:
				mc = '_request_enter'
				vars['_target'] = text[6:]
			elif text.startswith("/part"):
				mc = '_request_leave'
				vars['_target'] = text[6:]
			elif text.startswith('/password'):
				mc = '_set_password'
				t = text.split('/password')
				if t[1] != '' and t[1] != ' ':
					vars['_password'] = t[1]
					vars['_target'] = self.logic_parent.center.config['uni']
				else:
					self.append1('Usage: /password <secret>')
					return
			elif text.startswith('/retrieve'):
				mc = '_request_retrieve'
				vars['_target'] = self.logic_parent.center.config['uni']
			else:
				mc = '_request_execute'
				data = text
			
		elif text != '' and text[0] == '#':
			self.append1(text)
			self.entry_box.SetValue('')
			return
			
		else:
			mc = '_message_public'
			try:
				text2 = text.decode('iso-8859-15')
			except:
				text2 = text
				print 'unicode'
			data1 = text2.encode('iso-8859-1')
			data = data1
		# am ende einfach wegschicken das fertige paket
		self.entry_box.SetValue('')
		#print_psyc(mmp, psyc, mc, data, 'place sending')
		self.logic_parent.sendmsg(vars, mc, data)
		
	def append1(self, line):
		""" use this to append multi/single line text"""
		if type(line) == type(u'öäü'):
			line = line.encode('iso-8859-15')
		if os.name == 'posix':
			if self.lock == 0:
				self.lock = 1
				if self.buffer != '':
					self.text_box.AppendText('buffered: ' + self.buffer)
					self.buffer = ''
				for linex in line.split('\n'):
					self.text_box.AppendText(self.prompt.encode('iso-8859-15') + linex)
					self.text_box.AppendText('\n')
					self.logic_parent.center.Yield()
					self.lock = 0
			else:
				self.buffer += line + '\n'
		elif os.name == 'nt':
			# AppendText() doesn't seem to do the right thing in windows
			for linex in line.split('\n'):
				self.text_box.WriteText(self.prompt.encode('iso-8859-15') + linex)
				self.text_box.WriteText('\n')
			# we should find out how many 'lines' we write and scroll the right
			# amount instead of scrolling 10000 at once XXX
			self.text_box.ScrollLines(10000)
			self.logic_parent.center.Yield()
	
	def append(self, text):
		""" use this for more then one line USE append1() this is obsolete!! """
		# is this broken? do we have to do the same as in append1()?
		lines = text.split('\n')
		for line in lines:
			self.text_box.AppendText(self.prompt + line + '\n')
			#print self.netname + ': ' + str(text)


class wxPFrame(wxFrame):
	def __init__(self, parent = None, logic_parent = None, title = 'pypsyc-frame', pos = wxDefaultPosition, size = wxSize(920, 570), style = wxDEFAULT_FRAME_STYLE):
		wxFrame.__init__(self, None, -1, title, size=size)	
		# do we need it here? wxFrame is only supposed to be a container
		# and shouldn't do that much -> only here to be flexible
		# we use logic_parent to call the functions pypsyc provides
		# gui stuff in the wxBlah objects, psyc stuff in the PBlah objects
		if not logic_parent: print 'WARNING: no logic_parent set, this could be a problem'
		self.logic_parent = logic_parent
		self.notebook = wxNotebook(self, -1, style=0)
		self.CreateStatusBar()
		self.SetStatusText("welcome to pypsyc")
		self.Show()

	def addTab(self, tab,extra_display = None):
		tab.create_display(self.notebook)
		if extra_display:
			self.logic_parent.client.set_display(extra_display, tab.display)
		self.notebook.AddPage(tab.display, str(tab.netname), 1)


class wxPPlace(wxPTab):
	def __init__(self, parent, logic_parent = None):
		wxPTab.__init__(self, parent=parent, logic_parent=logic_parent)
		self.netname = self.logic_parent.netname


class wxPUser(wxPTab):
	def __init__(self, parent, logic_parent = None):
		wxPTab.__init__(self, parent=parent, logic_parent=logic_parent)
		self.netname = self.logic_parent.netname


class wxPClient(wxFrame):
	def __init__(self, parent = None, title = 'pypsyc', logic_parent = None, pos = wxDefaultPosition, size = wxSize(100, 400), style = wxDEFAULT_FRAME_STYLE):
		wxFrame.__init__(self, None, -1, title, size=size)
		# we use logic_parent to call the functions pypsyc provides
		# gui stuff in the wxBlah objects, psyc stuff in the PBlah objects
		if not logic_parent: print 'WARNING: no logic_parent set, this could be a problem'
		self.logic_parent = logic_parent
		
		self.CreateStatusBar()
		self.SetStatusText("welcome to pypsyc")
		self.BuddyList = wxListCtrl(self, 2222, style=wxLC_REPORT|wxLC_SINGLE_SEL|wxSUNKEN_BORDER)
		self.BuddyList.InsertColumn(0, "ST")
		self.BuddyList.InsertColumn(1, "Nick")# , wxLIST_FORMAT_RIGHT)
		self.BuddyList.SetColumnWidth(0, 20)
		
		self.status = wxComboBox(self, ID_STATUS, "", choices=["Offline", "Online", "Away"], size=(150,-1), style=wxCB_DROPDOWN)
		self.menu_button = wxButton( self, ID_MENU, 'pypsyc')
		self.exit_button = wxButton( self, ID_EXIT, 'exit')
		self.con_menu = wxBoxSizer(wxHORIZONTAL)
		self.con_menu.Add(self.menu_button, 1, wxALIGN_BOTTOM)
		self.con_menu.Add(self.exit_button, 1, wxALIGN_BOTTOM)
		
		sizer = wxFlexGridSizer(3, 0 , 0,0)
		sizer.Add(self.BuddyList, 1, wxGROW)
		sizer.Add(self.con_menu, 1,wxGROW)
		sizer.Add(self.status, 1,wxGROW)
		sizer.AddGrowableRow(0)
		sizer.AddGrowableCol(0)
		# do something so that the buttons don't vanish in a too small window
		# this is h4x0r-style but does the job at the moment
		sizer.SetItemMinSize(self.BuddyList, 30, 10)
		sizer.SetMinSize(wxSize(200,280))
		self.SetSizer(sizer)
		self.SetAutoLayout(true)
		self.Show()


class PPlace(ClientPlace):
	def __init__(self, netname, center):
		ClientPlace.__init__(self, netname, center)
		self.display = None

	def create_display(self, parent):
		self.display = wxPPlace(parent=parent, logic_parent=self)

	def msg(self, vars, mc, data, caller = None):
		print_psyc(vars, mc, data, 'place')
		#print 'ddd' +  str(type(data))
		parsedtext = parsetext(vars, mc, data)
		#print dir(parsedtext) , type(parsedtext)
		#parsedtext = parsedtext.encode('iso-8859-15')
		#print type(parsedtext)
		if mc == '_message_public':
			line = u''
			line += vars['_nick']
			if vars['_action']: line += ' ' + vars['_action'] + '>'
			else: line += '>'
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
		self.display = None

	def create_display(self, parent):
		self.display = wxPUser(parent=parent, logic_parent=self)
	
	def msg(self, vars, mc, data, caller = None):
		print_psyc(vars, mc, data, caller)
		parsedtext = parsetext(vars, mc,data)
		#parsedtext = parsedtext.encode('iso-8859-15')
		if mc == '_message_public':
			self.display.append1(parsedtext)
		else:
			self.display.append1(parsedtext)


class PServer(PSYCObject):
	def __init__(self, netname, center):
		PSYCObject.__init__(self, netname, center)
		print 'registered server'
		#print 'PServer: ' + str(dir(self))
		self.display = None

	def create_display(self, parent):
		self.display = wxPPlace(parent=parent, logic_parent=self)

	def msg(self, vars, mc, data, caller = None):
		print_psyc(vars, mc, data, 'server')
		parsedtext = parsetext(vars, mc,data)
		#parsedtext = parsedtext.encode('iso-8859-15')
		#self.center.Yield()
		if mc == '_notice_circuit_established':
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
		print_psyc(vars, mc, data, 'server sending...')
		PSYCObject.sendmsg(self, vars, mc, data, caller)


class PClient(PSYCClient):
	def __init__(self, netname, center):
		PSYCClient.__init__(self, netname, center)
		self.display = None
		self.extra_display = {} # XXX
		#self.create_display(parent=None)
		print 'default_conmnect is --> ' + self.center.default_connection

	def create_display(self, parent):
		self.display = wxPClient(parent=parent)
	def set_display(self, which, display):
		self.extra_display[which] = display


	def msg(self, vars, mc, data, caller = None):
		print_psyc(vars, mc, data, 'client')
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
				self.extra_display['server'].append1("Please enter your password or choose a different nick if you don't know the password")
				self.extra_display['server'].entry_box.SetValue('/password ')
		elif mc == '_status_friends':
			self.extra_display['server'].append1(parsedtext)
		
		elif mc == '_error_invalid_password':
			self.extra_display['server'].append1(parsedtext)
			self.extra_display['server'].append1("Please enter your password or choose a different nick if you don't know the password")
			self.extra_display['server'].entry_box.SetValue('/password ')
		else:
			self.extra_display['server'].append1(parsedtext)
		
	def online(self):
		self.center.connect(self.center.default_connection)
		#mc = '_request_link'
		#mmp = {}
		#psyc = {}
		#data =''
		#mmp['_target'] = self.netname
		
		#self.sendmsg(mmp, psyc, mc, data)


