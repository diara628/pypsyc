# -*- coding: latin-1 -*-
#from wxPython.wx import *
import wx
# XXX Please feel free to modify and vershclimmbesser this piece of code
# especially the bits marked with XXX
##from pypsyc.objects.PSYCObject import 
from pypsyc.objects.client import ClientUser, ClientPlace, PSYCClient
from pypsyc.objects import PSYCObject
from pypsyc.center import ClientCenter

from pypsyc import netLocation, parsetext
#from psycObjects import PUser, PPlace, PClient, PServer

import extras
import asyncore, sys, os

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


class wxObject:
	def __init__(self, parent, psyc_parent = None):
		""" basic display object """
		if not psyc_parent: print 'WARNING: no psyc_parent set, this could be a problem'
		self.netname = self.psyc_parent.netname
	def append1(self, text):
		""" use this to append multi/single line text"""
		pass


class wxPTab(wx.Panel):
	def __init__(self, parent, psyc_parent = None):
		""" all das ausehen usw """
		wx.Panel.__init__(self, parent, -1, style=wx.NO_BORDER)
		# we use logic_parent to call the functions pypsyc provides
		# gui stuff in the wx.Blah objects, psyc stuff in the PBlah objects
		if not psyc_parent: print 'WARNING: no psyc_parent set, this could be a problem'
		self.psyc_parent = psyc_parent
		config = self.psyc_parent.center.config
		self.prompt = config['prompt']
		self.lock = 0
		self.counter = 0
		self.buffer = ''
		self.text_box = wx.TextCtrl(self, -1, style=wx.NO_BORDER|wx.TE_MULTILINE|wx.TE_RICH2|wx.TE_READONLY, size=wx.DefaultSize)
		self.entry_box = wx.TextCtrl(self, ID_SAY, style=wx.NO_BORDER|wx.TE_PROCESS_ENTER|wx.TE_RICH2|wx.TE_PROCESS_TAB, size=wx.DefaultSize)
		
		fontcolour = wx.Colour(config['fontcolour'][0], config['fontcolour'][1], config['fontcolour'][2])
		bgcolour = wx.Colour(config['bgcolour'][0], config['bgcolour'][1], config['bgcolour'][2])
		points = self.text_box.GetFont().GetPointSize() # get the current size
		f = wx.Font(points, wx.MODERN, wx.NORMAL, wx.BOLD, False)
		if os.name == 'nt':
			self.text_box.SetDefaultStyle(wx.TextAttr(fontcolour, bgcolour, f))
			self.entry_box.SetDefaultStyle(wx.TextAttr(fontcolour, bgcolour, f))
			self.entry_box.SetBackgroundColour(bgcolour)
			self.text_box.SetBackgroundColour(bgcolour)
			self.SetBackgroundColour(bgcolour)
		if os.name == 'posix':
			self.text_box.SetDefaultStyle(wx.TextAttr(wx.NullColour, wx.NullColour, f))
			self.entry_box.SetDefaultStyle(wx.TextAttr(wx.NullColour, wx.NullColour, f))
			
		sizer = wx.BoxSizer(wx.VERTICAL)
		sizer.Add(self.text_box, 1, wx.EXPAND)
		sizer.Add(self.entry_box, 0, wx.EXPAND)
		self.SetSizer(sizer)

		#print 'wx.PTab: ' + str(dir(self))
		wx.EVT_TEXT_ENTER(self, ID_SAY, self.input)

	def input(self, event):
		text = event.GetString()
		text = text.lstrip() # only strip whites from the beginning
		mc = ''
		vars = {}
		data = ''
		vars['_target'] = self.psyc_parent.netname # eigentlich is target immer netname
		if text != '' and text[0] == '/':
			# houston we have a command
			if text.startswith("/join"): # and text.__len__() > 16:
				mc = '_request_enter'
				vars['_target'] = text[6:]
			#elif text.startswith("/part"):
			#	mc = '_request_leave'
			#	vars['_target'] = text[6:]
			elif text.startswith('/password'):
				mc = '_set_password'
				t = text.split('/password')
				if t[1] != '' and t[1] != ' ':
					vars['_password'] = t[1]
					vars['_target'] = self.psyc_parent.center.config['uni']
				else:
					self.append1('Usage: /password <secret>')
					return
			elif text.startswith('/connect'):
				self.psyc_parent.center.connect(text[9:])
				self.append1('connecting to: ' + text[9:])
				self.entry_box.SetValue('')
				return
			elif text.startswith('/retrieve'):
				mc = '_request_retrieve'
				vars['_target'] = self.psyc_parent.center.config['uni']
			elif text.startswith('/store'):
				mc = '_request_store'
				vars['_target'] = self.psyc_parent.center.config['uni']
				vars['_storic'] = text[7:]
				data = text[7:]
			else:
				vars['_target'] = self.psyc_parent.center.config['uni']
				#vars['_source']
				mc = '_request_execute'
				data = text
			
		elif text!= '' and text.startswith('##debug'):
			self.entry_box.SetValue('')
			self.append1(str(getattr(self.psyc_parent.center, text[8:])))
			return
			
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
		self.psyc_parent.sendmsg(vars, mc, data)
		
	def append1(self, line):
		""" use this to append multi/single line text"""
		if type(line) == type(u'öäü'):
			try:
				line = line.encode('iso-8859-1')
			except:
				print 'waahh'
		if os.name == 'posix':
			if self.lock == 0:
				self.lock = 1
				if self.buffer != '':
					self.text_box.AppendText('buffered: ' + self.buffer)
					self.buffer = ''
				for linex in line.split('\n'):
					self.text_box.AppendText(self.prompt.encode('iso-8859-15') + linex)
					self.text_box.AppendText('\n')
					self.psyc_parent.center.Yield()
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
			self.psyc_parent.center.Yield()
	
	def append(self, text):
		""" use this for more then one line USE append1() this is obsolete!! """
		# is this broken? do we have to do the same as in append1()?
		lines = text.split('\n')
		for line in lines:
			self.text_box.AppendText(self.prompt + line + '\n')
			#print self.netname + ': ' + str(text)


class wxPFrame(wx.Frame):
	def __init__(self, parent = None, psyc_parent = None, title = 'pypsyc-frame', pos = wx.DefaultPosition, size = wx.Size(920, 570), style = wx.DEFAULT_FRAME_STYLE):
		wx.Frame.__init__(self, None, -1, title, size=size)	
		# do we need it here? wx.Frame is only supposed to be a container
		# and shouldn't do that much -> only here to be flexible
		# we use logic_parent to call the functions pypsyc provides
		# gui stuff in the wx.Blah objects, psyc stuff in the PBlah objects
		if not psyc_parent: print 'WARNING: no psyc_parent set, this could be a problem'
		self.psyc_parent = psyc_parent
		self.notebook = wx.Notebook(self, -1, style=0)
		self.CreateStatusBar()
		self.SetStatusText("welcome to pypsyc")
		self.Show()

	def addTab(self, tab):
		tab.create_display(parent=self.notebook)
		self.notebook.AddPage(tab.display['default'], str(tab.netname), 1)


class wxPPlace(wxPTab):
	def __init__(self, parent, psyc_parent = None):
		wxPTab.__init__(self, parent=parent, psyc_parent=psyc_parent)
		self.netname = self.psyc_parent.netname


class wxPUser(wxPTab):
	def __init__(self, parent, psyc_parent = None):
		wxPTab.__init__(self, parent=parent, psyc_parent=psyc_parent)
		self.netname = self.psyc_parent.netname


class wxPClient(wx.Frame):
	def __init__(self, parent = None, title = 'pypsyc', psyc_parent = None, pos = wx.DefaultPosition, size = wx.Size(100, 400), style = wx.DEFAULT_FRAME_STYLE):
		wx.Frame.__init__(self, None, -1, title, size=size)
		if not psyc_parent: print 'WARNING: no psyc_parent set, this could be a problem'
		self.psyc_parent = psyc_parent
		
		self.CreateStatusBar()
		self.SetStatusText("welcome to pypsyc")
		self.BuddyList = wx.ListCtrl(self, 2222, style=wx.LC_REPORT|wx.LC_SINGLE_SEL|wx.SUNKEN_BORDER)
		self.BuddyList.InsertColumn(0, "ST")
		self.BuddyList.InsertColumn(1, "Nick")# , wx.LIST_FORMAT_RIGHT)
		self.BuddyList.SetColumnWidth(0, 20)
		
		self.status = wx.ComboBox(self, ID_STATUS, "", choices=["Offline", "Online", "Away"], size=(150,-1), style=wx.CB_DROPDOWN)
		self.menu_button = wx.Button( self, ID_MENU, 'pypsyc')
		self.exit_button = wx.Button( self, ID_EXIT, 'exit')
		self.con_menu = wx.BoxSizer(wx.HORIZONTAL)
		self.con_menu.Add(self.menu_button, 1, wx.ALIGN_BOTTOM)
		self.con_menu.Add(self.exit_button, 1, wx.ALIGN_BOTTOM)
		
		sizer = wx.FlexGridSizer(3, 0 , 0,0)
		sizer.Add(self.BuddyList, 1, wx.GROW)
		sizer.Add(self.con_menu, 1,wx.GROW)
		sizer.Add(self.status, 1,wx.GROW)
		sizer.AddGrowableRow(0)
		sizer.AddGrowableCol(0)
		# do something so that the buttons don't vanish in a too small window
		# this is h4x0r-style but does the job at the moment
		sizer.SetItemMinSize(self.BuddyList, 30, 10)
		sizer.SetMinSize(wx.Size(200,280))
		self.SetSizer(sizer)
		self.SetAutoLayout(True)
		self.Show()
