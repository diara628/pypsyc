# ask fippo if we need all this
#import pypsyc.GUI.Abstract.Gui as AbstractGui
import sys
#from pypsyc.PSYC.PSYCRoom import  PSYCPackage

# we need this
from wxPython.wx import *
from wxPython.lib.rcsizer import RowColSizer
from wxPython.lib.grids import wxFlexGridSizer
#from wxPython.lib.mixins.listctrl import wxColumnSorterMixin, wxListCtrlAutoWidthMixin
# have to read about Create_Id() so we don't have to bother with the numbers
ID_ABOUT = 1002
ID_CONNECT = 1001
ID_DISCONNECT = 10011
ID_STATUS = 9901
ID_MENU = 9902
ID_BUDDY_LIST = 9903
ID_BUDDY_LIST_DK = 990301
ID_EXIT = 1099
ID_CLOSECHATNOTEBOOK = 2099
ID_CLOSECHATNOTE = 2098


class Friend:
	""" a user object """
	def __init__(self, uni, unl='255.255.255.255'):
		self.uni = str(uni)
		self.unl = str(unl)
		self.chatting = 0
		self.tab = None
		
	def chat(self, inst):
		# das hier sollte zu dem schon bestehenden fenster extrawin(was direkt beim
		# starten des cients erzeugt wird und beim connecten sichtbar wird
		# ein tab hinzufügen
		if self.chatting == 1:
			inst.notebook.Show(True)
			# focus the window where the chat is taking place
			# still a bit buggy
			# if you close a tab self.tab is wrong
			inst.notebook.SetSelection(self.tab)

		else:
			panel = wxPanel(inst.notebook, -1)
			
			button = wxButton(panel, ID_CLOSECHATNOTE, "close chat")
			button2 = wxButton(panel, ID_STATUS, "online")
			nick_box = wxTextCtrl(panel, -1, style=wxTE_READONLY)
			box = wxBoxSizer(wxHORIZONTAL)
			box.Add(nick_box, 1,wxEXPAND)
			box.Add(button2,0,wxEXPAND)
			box.Add(button,0,wxEXPAND)
			
			text_box = wxTextCtrl(panel, -1, style=wxTE_MULTILINE|wxTE_READONLY)
			entry_box = wxTextCtrl(panel, -1, style=wxTE_MULTILINE, size=wxDefaultSize)
			
			sizer = RowColSizer()
			#sizer.Add(button, pos=(1,1))
			#sizer.Add(nick_box, pos=(1,2), flag=wxEXPAND)
			#sizer.Add(button2, pos=(1,3))
			sizer.Add(box, pos=(1,1), colspan=3,flag=wxEXPAND)
			sizer.Add(text_box, pos=(2,1),flag=wxEXPAND, colspan=3)
			sizer.Add(entry_box, pos=(3,1),flag=wxEXPAND, colspan=2)
			sizer.AddGrowableCol(1)
			#sizer.AddGrowableCol(2)
			sizer.AddGrowableRow(2)
			panel.SetSizer(sizer)
			inst.notebook.AddPage(panel, self.uni, select=1)
			self.tab = inst.notebook.GetSelection()
			self.chatting = 1
		
	def getStatus(self):
		return 'On'
		
	def stop_chat(self):
		self.chatting = 0
		self.tab = None
		# do whatever has to be done
		
		
		
		
class TabBook(wxFrame):
	""" do the actual displaying """
	def __init__(self, parent, ID, title, pos=wxDefaultPosition, size=wxDefaultSize, style=wxDEFAULT_FRAME_STYLE):
		wxFrame.__init__(self, parent, ID, title, pos, size, style)
		menu = wxMenu()
		menu.Append(ID_DISCONNECT, "&Disconnect", "bye-bye")
		menu.Append(ID_ABOUT, "&About", "tritratrullala")
		menu.AppendSeparator()
		menu.Append(ID_EXIT, "&Exit", "leave us")
		menuBar = wxMenuBar()
		menuBar.Append(menu, "&File");
		self.SetMenuBar(menuBar)
		self.notebook = wxNotebook(self, -1)
		
		status_panel = wxPanel(self.notebook, -1)
		button = wxButton(status_panel, ID_CLOSECHATNOTEBOOK, "close status win")
		self.notebook.AddPage(status_panel, 'status')
		
		# event handling
		EVT_BUTTON(self, ID_CLOSECHATNOTEBOOK, self.OnCloseMe)
		#EVT_BUTTON(self, ID_CLOSECHATNOTE, self.OnCloseChat)
		EVT_CLOSE(self, self.OnCloseWindow)
	
	def newChat(self, who):
		#todo: check if there is already a 'chat' with that who, make a nice panel, nicklist option?
		panel = wxPanel(self.notebook, -1)
		button = wxButton(panel, ID_CLOSECHATNOTE, "close chat")
		self.notebook.AddPage(panel, who, select =1)
		
	# event methods
	def OnCloseChat(self, event):
		where = self.notebook.GetSelection()
		t = self.notebook.GetPageText(where)
		self.notebook.DeletePage(where)
		self.notebook.Show(True)
		event.Skip()
		return t
		
	def OnCloseMe(self, event):
		self.Show(False)
		#self.Close(true)
		event.Skip()

	def OnCloseWindow(self, event):
		self.Show(False)
		#self.Destroy()
		event.Skip()
		
		
		

class UserGui(wxFrame):
	""" handle the "querys" / chats with a single user """
	def __init__(self, parent, ID, title, pos=wxDefaultPosition, size=wxDefaultSize, style=wxDEFAULT_FRAME_STYLE):
		wxFrame.__init__(self, parent, ID, title, pos, size, style)
		menu = wxMenu()
		menu.Append(ID_DISCONNECT, "&Disconnect", "bye-bye")
		menu.Append(ID_ABOUT, "&About", "tritratrullala")
		menu.AppendSeparator()
		menu.Append(ID_EXIT, "&Exit", "leave us")
		menuBar = wxMenuBar()
		menuBar.Append(menu, "&File");
		self.SetMenuBar(menuBar)
		self.notebook = wxNotebook(self, -1)
		
		status_panel = wxPanel(self.notebook, -1)
		button = wxButton(status_panel, ID_CLOSECHATNOTEBOOK, "close status win")
		self.notebook.AddPage(status_panel, 'status')
		
		# event handling
		EVT_BUTTON(self, ID_CLOSECHATNOTEBOOK, self.OnCloseMe)
		#EVT_BUTTON(self, ID_CLOSECHATNOTE, self.OnCloseChat)
		EVT_CLOSE(self, self.OnCloseWindow)
	
	def newChat(self, who):
		#todo: check if there is already a 'chat' with that who, make a nice panel, nicklist option?
		panel = wxPanel(self.notebook, -1)
		button = wxButton(panel, ID_CLOSECHATNOTE, "close chat")
		self.notebook.AddPage(panel, who, select =1)
		
	# event methods
	def OnCloseChat(self, event):
		where = self.notebook.GetSelection()
		t = self.notebook.GetPageText(where)
		self.notebook.DeletePage(where)
		self.notebook.Show(True)
		event.Skip()
		return t
		
	def OnCloseMe(self, event):
		self.Show(False)
		#self.Close(true)
		event.Skip()

	def OnCloseWindow(self, event):
		self.Show(False)
		#self.Destroy()
		event.Skip()


class FriendList(wxFrame):
	""" buddy list and other stuff """
	def __init__(self, parent, ID, title, pos=wxDefaultPosition, size=wxSize(190, 400), style=wxDEFAULT_FRAME_STYLE):
		wxFrame.__init__(self, parent, ID, title, pos , size, style)
		
		# menubar, statusbar et al
		self.CreateStatusBar()
		self.SetStatusText("welcome to pyPSYC")
		menu = wxMenu()
		menu.Append(ID_CONNECT, "&Connect", "connect to the net")
		menu.Append(ID_ABOUT, "&About", "tritratrullala")
		menu.AppendSeparator()
		menu.Append(ID_EXIT, "&Exit", "leave us")
		menuBar = wxMenuBar()
		menuBar.Append(menu, "&File");
		self.SetMenuBar(menuBar)
	
		
		##'buddy' list, perhaps ;]]
		self.SampleList= []
		self.buddylist_dict ={}
		#self.BuddyList = wxListBox(self , ID_BUDDY_LIST,style=wxLB_NEEDED_SB|wxLB_SINGLE, choices=self.SampleList)
		self.BuddyList = wxListCtrl(self, ID_BUDDY_LIST, style=wxLC_REPORT|wxLC_SINGLE_SEL|wxSUNKEN_BORDER)
		self.BuddyList.InsertColumn(0, "ST")
		self.BuddyList.InsertColumn(1, "Nick")# , wxLIST_FORMAT_RIGHT)
		self.BuddyList.SetColumnWidth(0, 20)
		##end buddy list
		
		# define the buttons and so on at the bottom of the window 
		self.status = wxComboBox(self, ID_STATUS, "", choices=["", "This", "is a", "Place", "to put commands"], size=(150,-1), style=wxCB_DROPDOWN)
		self.menu_button = wxButton( self, ID_MENU, 'pyPSYC')
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
		# do somethign so that the buttons don't vanish in a too small window
		# this is h4x0r-style but does the job at the moment
		sizer.SetItemMinSize(self.BuddyList, 30, 10)
		sizer.SetMinSize(wxSize(200,280))
		self.SetSizer(sizer)
		self.SetAutoLayout(true)
		##dunno where to put it at the moment,but believe it shouldn't be here
		# wir machen uns ne instanz von dem fenster wo alle chats rein kommen sollen
		self.extrawin = TabBook(self, -1, "blah blubb", size=(800, 400), style = wxDEFAULT_FRAME_STYLE)
		# für buddy auswahl
		self.currentBuddy = 0

		# event handling
		EVT_BUTTON( self, ID_EXIT, self.onExit )
		EVT_BUTTON(self, ID_CONNECT, self.doConnect)
		EVT_BUTTON(self, ID_CLOSECHATNOTE, self.closeChat)
		EVT_MENU( self, ID_EXIT, self.onExit)
		EVT_MENU(self, ID_CONNECT, self.doConnect)
		##EVT_LEFT_DCLICK(self.BuddyList,  self.onFriend)
		EVT_LIST_ITEM_SELECTED(self, ID_BUDDY_LIST, self.OnBuddySelected)
		# ect_activated muß weg sosnt wird zweimal nen chat geöffnet ;]]
		EVT_LIST_ITEM_ACTIVATED(self, ID_BUDDY_LIST, self.onFriend)
		
	def PopulateBuddyList(self):
		items = self.buddylist_dict.items()
		for x in range(len(items)):
			nick, obj = items[x]
			self.BuddyList.InsertStringItem(x ,obj.getStatus())
			self.BuddyList.SetStringItem(x, 1,str(nick))
			
		self.BuddyList.SetColumnWidth(0, wxLIST_AUTOSIZE)
		self.BuddyList.SetColumnWidth(1, wxLIST_AUTOSIZE)
		
	def getColumnText(self, index, col):
		item = self.BuddyList.GetItem(index, col)
		return item.GetText()
		
		
	def onExit(self, event):
		"""do magic stuff before closing"""
		#disconnect() oder sowas
		self.Close(TRUE)
	
	def doConnect(self , event):
		#todo: all the socket stuff, way to much
		"""do even more fippo(psyc-proto) magic"""
		# this list is created by some network magic
		self.current_buddys = ['tim', 'tom', 'foo', 'neo', 'fippo', 'garrit', 'marder', 'troete', 'bar', '23', 'ten', 'eleven', 'twelve', 'thirteen', 'fourteen']
		
		for user in self.current_buddys:
			tt = Friend(user)
			self.buddylist_dict[user] = tt
			
		#print self.buddylist_dict
		#print '----\n'
		##self.extrawin = TabBook(self, -1, "blah blubb", size=(800, 400), style = wxDEFAULT_FRAME_STYLE)
		##self.otherWin = self.extrawin
		self.PopulateBuddyList()
		event.Skip()
		
	def OnBuddySelected(self, event):
		self.currentBuddy = event.m_itemIndex
		#print str(self.currentBuddy) +'--'
	
	def onFriend(self, event):
		#todo: catch the case that there is no extrawin(we aren't connected)
		"""open a new tab in the usergui"""
		tt = str(self.getColumnText(self.currentBuddy, 1))
		t = self.buddylist_dict[tt]
		t.chat(self.extrawin)
		self.extrawin.Show(True)
		#print self.getColumnText(self.currentBuddy, 1)
		event.Skip()
	
	def closeChat(self, event):
		t = self.extrawin.OnCloseChat(event)
		buddy = self.buddylist_dict[t]
		buddy.stop_chat()
		event.Skip()
		

class Application(wxApp):
	def OnInit(self):
		frame = FriendList(NULL, -1, "pyPSYC 0.0.0.0.0.1")
		frame.Show(true)
		self.SetTopWindow(frame)
		#self.timer = wxTimer()
		#self.timer.SetOwner(self.socket_check, 6666)
		#self.timer.Start(5000) # alle 100 ms / 5 secs
		#self.timer = wxPyTimer(self.socket_check)
		#self.timer.Start(500) # alle 500 ms
		return true
		
	def run(self):
		# blah mainloop
		from twisted.internet import wxsupport, reactor
		wxsupport.install(self)
		print "running reactor..."
		reactor.run()

##		self.MainLoop()
	

## this has to change i guess
#app = PsycApp(0)
#app.MainLoop()

##EOF
