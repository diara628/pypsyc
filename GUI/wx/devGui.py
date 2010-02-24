# be warned this is the _dev_ version of the wx gui
# perhaps it will work, perhaps it's all borked up,
# this is a plazground shouldn't be used on a day to
# day basis
import GUI.Abstract.Gui as AbstractGui
import asyncore, sys, os
import ConfigParser
from string import split, rfind, strip

from pypsyc.PSYC.PSYCRoom import PSYCPackage
from pypsyc.PSYC.PSYCRoom import Friends as FriendsPackage
from pypsyc.PSYC import parsetext, get_user

from wxPython.wx import *
from wxPython.stc import *


from wxPython.lib.rcsizer import RowColSizer
from wxPython.lib.grids import wxFlexGridSizer

VERSION = 'pyPSYC-wx 0.0.1'

# for linux/posix this should work
CONFIG_FILE = os.getenv("HOME") + "/.pypsyc/wx-config"

# windows users should uncomment the next line and comment out the line above
# CONFIG_FILE  = 'wx-config'

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

class Tab(wxPanel):
    def __init__(self, context, notebook):
        self.notebook = notebook
        wxPanel.__init__(self, self.notebook, -1)
        #panel = wxPanel(self.notebook, -1)
        button = wxButton(self, ID_CLOSECHATNOTE, "close chat")
        #button2 = wxButton(self, ID_STATUS, "NOOP")
        self.nick_box = wxTextCtrl(self, -1, style=wxTE_READONLY)
        box = wxBoxSizer(wxHORIZONTAL)
        box.Add(self.nick_box, 1,wxEXPAND)
        #box.Add(button2,0,wxEXPAND)
        box.Add(button,0,wxEXPAND)
        
        #scroller = wxScrolledWindow(self, -1, size=(-1,-1))
        self.text_box = wxTextCtrl(self, -1, style=wxTE_MULTILINE|wxTE_RICH2|wxTE_READONLY|wxTE_AUTO_URL, size=wxDefaultSize)
        self.entry_box = wxTextCtrl(self, ID_SAY, style=wxTE_PROCESS_ENTER|wxTE_PROCESS_TAB, size=wxDefaultSize)
        
        sizer = RowColSizer()
        sizer.Add(box, pos=(1,1), colspan=3,flag=wxEXPAND)
        sizer.Add(self.text_box, pos=(2,1),flag=wxEXPAND, colspan=3)
        #sizer.Add(scroller, pos=(2,1),flag=wxEXPAND, colspan=3)
        sizer.Add(self.entry_box, pos=(3,1),flag=wxEXPAND, colspan=2)
        sizer.AddGrowableCol(1)
        sizer.AddGrowableRow(2)
        self.SetSizer(sizer)
        
    def append_text(self, text):
        #text = text.decode('iso-8859-1')
        if os.name == 'posix':
            #self.text_box.SetEditable(True)
            #ende = self.text_box.GetInsertionPoint()
            #self.text_box.ShowPosition(ende+len(text))
            self.text_box.AppendText(text)
            #self.text_box.SetInsertionPointEnd()
            #ende = self.text_box.GetInsertionPoint()
            #self.text_box.ShowPosition(ende+len(text))
            self.text_box.ScrollLines(2)
            #self.text_box.SetEditable(False)
        else:
            self.text_box.WriteText(text)
            self.text_box.ScrollLines(2)
        
    def clear_entry(self):
        self.entry_box.Clear()
        self.entry_box.SetInsertionPoint(0)
        
    def append_entry(self, text):
        self.entry_box.AppendText(text)
        
    def set_topic(self, text):
        self.nick_box.Clear()
        self.nick_box.AppendText(text)
        
    def get_text(self):
        return self.entry_box.GetValue()

class FriendList(wxFrame, PSYCPackage):
    def __init__(self, parent=None, ID=0, title='pyPSYC', center=None, config=None, pos=wxDefaultPosition, size=wxSize(190, 400), style=wxDEFAULT_FRAME_STYLE):
        # bei mir is friendlist, firendlist und maingui in einem
        # zumindestens sollte es das sein ob es so klappt weiss ich noch nicht
        self.global_config = config
        self.config = ConfigParser.ConfigParser()  
        self.config.read(CONFIG_FILE)
        
        if self.config:
            pos = split(self.config.get('gui', 'wx_friend_pos'), ',')
            size = split(self.config.get('gui', 'wx_friend_size'), ',')
            
        wxFrame.__init__(self, parent, ID, title, wxPoint(int(pos[0]), int(pos[1])) , wxSize(int(size[0]), int(size[1])), style)
        PSYCPackage.__init__(self)
        self.currentBuddy = None
        self.center = center
        self.model = None
        self.packagename = "Friends gui"
        # we have to register by ourselves
        # perhaps it's not the way to do it but it works
# no.. it's not working.. --lynX
#       self.center.register(FriendsPackage(self))

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
        # do something so that the buttons don't vanish in a too small window
        # this is h4x0r-style but does the job at the moment
        sizer.SetItemMinSize(self.BuddyList, 30, 10)
        sizer.SetMinSize(wxSize(200,280))
        self.SetSizer(sizer)
        self.SetAutoLayout(true)

        # event handling
        EVT_BUTTON( self, ID_EXIT, self.onExit )
        EVT_BUTTON( self, ID_MENU, self.doConnect )
        #EVT_BUTTON(self, ID_CONNECT, self.doConnect)
        #EVT_BUTTON(self, ID_CLOSECHATNOTE, self.closeChat)
        EVT_MENU( self, ID_EXIT, self.onExit)
        EVT_MENU(self, ID_CONNECT, self.doConnect)
        #EVT_LEFT_DCLICK(self.BuddyList,  self.onFriend)
        #EVT_LIST_ITEM_SELECTED(self, ID_BUDDY_LIST, self.OnBuddySelected)
        # ect_activated muss weg sonst wird zweimal nen chat geoeffnet ;]]
        ##EVT_LIST_ITEM_ACTIVATED(self, ID_BUDDY_LIST, self.onFriend)
    
    def received(self, source, mc, mmp, psyc):
        # muss ueberall sein, warum weiss ich noch nicht so genau
        # .._present .._absent versteh ich also is es da;]
        if mc == "_notice_friend_present":
            self.present(mmp.get_source())
        elif mc == "_notice_friend_absent":
            self.absent(mmp.get_source())
        elif mc == "_notice_link" or mc == "_notice_unlink" or mc == "_status_linked":
            self.set_status(mc)

    def set_model(self, model): 
        self.model = model
       
    def present(self, nick):
        """ do what has to be done if a friend turns up """
        # at the moment:
        pass
        #fuer das x muesste man wissen wie lang die buddy list bisher ist
        #sprich vllt doch wieder nen dict dafuer bauen or so
        #self.BuddyList.InsertStringItem(x ,'on')
        #self.BuddyList.SetStringItem(x, 1, nick)

    def absent(self, nick):
        """ do what has to be done if a friend leaves us """
        # at the moment also:
        pass

    def set_status(self, status):
        """ we should tell the user if the status changes """
        #print 'link status: ' + str(status)

    def OnBuddySelected(self, event):
        self.currentBuddy = event.m_itemIndex
        event.Skip()

    def doConnect(self, event, host = ''):
        self.center.connect(host)
        #print 'connecting...'
        event.Skip()

    def onExit(self, event):
        """ do stuff we have to do before exiting """
        #print 'exiting...'
        pos = str(self.GetPositionTuple()[0]) + ', ' + str(self.GetPositionTuple()[1])
        size = str(self.GetSizeTuple()[0]) + ', ' + str(self.GetSizeTuple()[1])
        self.config.set('gui', 'wx_friend_pos', pos)
        self.config.set('gui', 'wx_friend_size', size)
        config_file = file(CONFIG_FILE, 'w')
        self.config.write(config_file)
        config_file.close()
            
        self.model.set_mc("_request_execute")
        self.model.set_target(self.model.center.ME())
        self.model.set_text("/quit")
        self.model.send()
        self.Close(TRUE)
        #sys.exit(0)
        event.Skip()
        
class UeberGui(wxFrame):
    def __init__(self,  parent=NULL, ID=-1, title='uebergui teil', status_tab = 1, pos=wxDefaultPosition, size=wxDefaultSize, style=wxDEFAULT_FRAME_STYLE):
        self.config = ConfigParser.ConfigParser()  
        self.config.read(CONFIG_FILE)
        
        if self.config:
            pos = split(self.config.get('gui', 'wx_room_pos'), ',')
            size = split(self.config.get('gui', 'wx_room_size'), ',')
        wxFrame.__init__(self, parent, ID, title, wxPoint(int(pos[0]), int(pos[1])) , wxSize(int(size[0]), int(size[1])), style)
        #PSYCPackage.__init__(self)
        self.notebook = wxNotebook(self, ID_NOTEBOOK)
        
        self.tabs = [] # ein nummer zu context mapping
        self.querys = []
        self.buffers = {} # context : "chatter going on in this context"
        self.tab_inst = {} # context : tab instanz
        self.query_inst = {} # context : tab instanz
        self.members = {} # dictionary a la { 'PSYC' :  ['fippo', 'lethe', ...]}
            
        if status_tab == 1:
            self.addTab('status')
        EVT_TEXT_ENTER(self, ID_SAY, self.say)
        EVT_NOTEBOOK_PAGE_CHANGED(self, ID_NOTEBOOK, self.OnTabChange)
        EVT_CLOSE(self, self.onClose )
        EVT_TEXT(self, ID_SAY, self.EvtText)
        
    def EvtText(self, event):
        #print 'EvtText: %s' % event.GetString()
        event.Skip()
        
    def find_nick(self, wiesel):
        positve_members= []
        members = self.members[self.model.get_context()]
        for member in members:
            member = strip(member)
            if member.startswith(wiesel):
                positve_members.append(member)
        return positve_members
        
    def EvtChar(self, event):
        #print 'EvtChar: ' + str(event.GetKeyCode())
        if event.GetKeyCode() == 9:
            # hier muessen wir nick raten und so weiter
            wiesel = self.tab_inst[self.model.get_context()].get_text()
            wiesel2 = wiesel
            wiesel = split(wiesel, ' ')
            marder = self.find_nick(wiesel[-1])
            if len(marder) > 1:
                print 't1'
                self.tab_inst[self.model.get_context()].append_text(str(marder) + '\n')
            elif len(marder) == 1:
                print 't2'
                nick = marder[0]
                text = wiesel2
                pos = - len(wiesel[-1])
                text = text[:pos] + nick
                self.tab_inst[self.model.get_context()].clear_entry()
                self.tab_inst[self.model.get_context()].append_entry(text)
            else:
                print 't3'
        else:
            # hier passen wir einfach und reset'en den coutner
            self.dep_count = 0
            event.Skip()
            
    def onClose(self,event):
        print 'UeberGui.onCLose() worked'
        
    def say(self, event):
        """ wird gerufen wenn jmd enter drückt """
        text = event.GetString()
        #text = text.encode('iso-8859-1')
        if text != '' and text[0] == '/':
            # we have a command
            # if we know the command, we set the appropiate mc
            # else we do _request_execute
            if text.startswith("/join") and text.__len__() > 16:
                # 16 == len(/join psyc://h/@r)
                self.model.set_mc("_request_enter")
                self.model.set_target(text.split(" ")[1])
                self.model.send()
            elif text.startswith("/part"):
                # wie waers mit /part_logout, part_home, part_type, ...
                self.model.set_mc("_request_leave")
                self.model.set_target(self.model.get_context())
                self.model.send()

            elif text.startswith("/quit"):
                self.model.set_mc("_request_execute")
                self.model.set_target(self.model.center.ME())
                self.model.set_text("/quit")
                self.model.send()
                
            elif text.startswith('/me') and text[3] == ' ':
                self.model.set_target(self.model.get_context())
                self.model.set_mc('_message_public')
                self.model.set_psycvar('_action', text[4:])
                self.model.set_text('')
                self.model.send()
            
            elif text.startswith('/names'):
                self.model.set_target(self.model.get_context())
                self.model.set_mc('_request_members')
                self.model.set_text('')
                self.model.send()
                
            #elif text.startswith('/lnames'):
            #    context = self.model.get_context()
            #    self.tab_inst[context].append_text(self.members[context][0] + '\n')
            
            elif text.startswith("/connect"):
                foo = len(text.split(" "))
                if foo == 2:
                    self.model.center.connect(text.split(" ")[1])
                elif foo == 3:
                    self.model.center.connect(text.split(" ")[1], text.split(" ")[2])
            else:
                self.model.set_target(self.model.center.ME())
                self.model.set_mc("_request_execute")
                self.model.set_text(text)
                self.model.send()
        elif text != '' and text[0] == "#":
            self.model.set_target(self.model.center.ME())
            self.model.set_mc("_request_execute")
            self.model.set_text("/" + text[1:])
            self.model.send()
        elif text != '' and text[0] == "!":
            self.model.set_target(self.model.get_context())
            self.model.set_mc("_request_execute")
            self.model.set_text(text)
            self.model.send()
        elif text != '' and text[-1] == '?':
            self.model.set_target(self.model.get_context())
            self.model.set_mc("_message_public")
            self.model.set_text(text)
            self.model.send()
        elif text != '':
            #print "msg to", self.model.get_context()
            self.model.set_target(self.model.get_context())
            self.model.set_mc("_message_public")
            self.model.set_text(text)
            self.model.set_psycvar('_action', 'testet')
            self.model.send()
        self.tab_inst[self.model.context].clear_entry()
        event.Skip()
        
    def addTab(self, title):
        panel = Tab(title, self.notebook)
        if title != 'status':
            short_title= title[rfind(title, '@'):]
            self.model.set_context(title)
            panel.append_text('heading over to ' + title + '\n')
            self.model.set_target(self.model.get_context())
            self.model.set_mc("_request_members")
            self.model.set_text('')
            self.model.send()

        else:
            short_title = title
        self.notebook.AddPage(panel, short_title, select = 1)
        
        self.tab_inst[title] = panel
        self.SetTitle(title)
        EVT_CHAR(panel.entry_box, self.EvtChar)
        
        if title == 'status':
            motd = 'Welcome to ' + VERSION + '\n for Q&A go to psyc://ve.symlynx.com/@PSYC \n or contact tim@trash-media.de for GUI problems \n for all the other problems go and talk to fippo!'
            panel.append_text(motd)
            
        self.tabs.append(title)
        #self.buffers[title] = ''
    
    def addQuery(self, title):
        panel = Tab(title, self.notebook)
        if title != 'status':
            short_title= title[rfind(title, '~'):]
            #self.model.set_context(title)
            print dir(self.model)
            panel.append_text('talking to ' + short_title + '\n')
            #self.model.set_target(self.model.get_context())
            #self.model.set_mc("_request_members")
            #self.model.set_text('')
            #self.model.send()
        else:
            short_title = title
        self.notebook.AddPage(panel, short_title, select = 1)
        
        self.query_inst[title] = panel
        self.SetTitle(title)
        if title == 'status':
            motd = 'Welcome to ' + VERSION + '\n for Q&A go to psyc://ve.symlynx.com/@PSYC \n or contact tim@trash-media.de for GUI problems \n for all the other problems go and talk to fippo!'
            panel.append_text(motd)
            
        self.querys.append(title)
        self.source = self.querys[-1]
        #print (self.querys)
        #print '<<<<<<<<<<<<<<'
        #self.buffers[title] = ''
        
    def OnTabChange(self, event):
        old = event.GetOldSelection()
        new = event.GetSelection()
        self.SetTitle(self.tabs[new])
        self.model.set_context(self.tabs[new])
        #if self.buffers[self.model.context] != '':
        #    self.tab_inst[self.model.context].append_text(self.buffers[self.model.context])
        #    self.buffers[self.model.context] = ''
        event.Skip()
        
    def msg(self, text):
        """ mehr text! """

class UserGui(UeberGui, AbstractGui.UserGui, PSYCPackage):
    def __init__(self):
        """ das hier is fuer querys """
        PSYCPackage.__init__(self)
        UeberGui.__init__(self, status_tab = 0)
        self.model = None
        self.source = ''
        #pass
        
    def say(self, event):
        text = event.GetString()
        #source self.tabs[]
        source = self.source
        self.model.set_target(source)
        self.model.set_mc("_message_private")
        self.model.psyc._assign("_nick", get_user(self.model.center.ME()))
        
        #text = self.get_input(self.windows[source]["entryfield"])
        self.model.set_text(text.strip())
        #self.append_text(self.windows[source]["displayfield"], "Du sagst: " + text)
        self.model.send()
        self.query_inst[source].append_text('Du> ' + text + '\n')
        self.query_inst[source].clear_entry()
        event.Skip()


    def received(self, source, mc, mmp, psyc):
        context = 'status'
        if mmp._query("_source") != None:
            context = mmp._query("_source").lower()
        else:
            context = source.lower()
            
        if mc == "_internal_message_private_window_popup":
            # open a new tab
            self.Show(True)
            self.addQuery('test')
        
        elif mc == "_message_echo_private":
            self.Show(True)
            text = ''
            text += 'Du>'
            if context not in self.querys:
                self.addQuery(context)
            text += ' ' + parsetext(mmp, psyc)
            self.query_inst[context].append_text(text + '\n')
            
        elif mc =='_message_private':
            self.Show(True)
            text = ''
            text += 'Anderer_Nick>'
            if context not in self.querys:
                self.addQuery(context)
            text += ' ' + parsetext(mmp, psyc)
            self.query_inst[context].append_text(text + '\n')

    def set_model(self, model): 
        self.model = model
        
    def OnTabChange(self, event):
        old = event.GetOldSelection()
        new = event.GetSelection()
        self.SetTitle(self.querys[new])
        self.source = self.querys[new]
        #self.model.set_context(self.tabs[new])
        #if self.buffers[self.model.context] != '':
        #    self.tab_inst[self.model.context].append_text(self.buffers[self.model.context])
        #    self.buffers[self.model.context] = ''
        event.Skip()



class RoomGui(UeberGui, AbstractGui.RoomGui, PSYCPackage):
    def __init___(self):
        """ das hier is fuer raeume """
        PSYCPackage.__init__(self)
        UeberGui.__init__(self,pos=pos, size=size)
        self.model = None
        
        EVT_CLOSE(self, self.onClose)
        
    def onClose(self,event):
        #print 'RoomGui.onClose() worked'
        pos = str(self.GetPositionTuple()[0]) + ', ' + str(self.GetPositionTuple()[1])
        size = str(self.GetSizeTuple()[0]) + ', ' + str(self.GetSizeTuple()[1])
        self.config.set('gui', 'wx_room_pos', pos)
        self.config.set('gui', 'wx_room_size', size)
        config_file = file(CONFIG_FILE, 'w')
        self.config.write(config_file)
        config_file.close()
        #self.Show(False)
        event.Skip()

    def set_model(self, model): 
        self.model = model
        
    def received(self, source, mc, mmp, psyc):
        context = 'status'
        if mmp._query("_context") != None:
            context = mmp._query("_context").lower()
        else:
            context = source.lower()
        #if psyc._query('_nick_place') != None:
        #    context =  'psyc://ve.symlynx.com/@' + psyc._query('_nick_place').lower()
            #context = source.lower()
        if mc.startswith('_notice_place_leave'):
            if context not in self.tabs:
                self.addTab(context)
            text = parsetext(mmp, psyc)
            self.tab_inst[context].append_text(text + '\n')
            if self.members.has_key(context):
                nick = psyc._query('_nick')
                self.members[context].remove(nick)
        
        if mc.startswith('_notice_place_enter'):
            self.Show(true)
            if context not in self.tabs:
                self.addTab(context)
            text = parsetext(mmp, psyc)
            self.tab_inst[context].append_text(text + '\n')
            if self.members.has_key(context):
                nick = psyc._query('_nick')
                if nick not in self.members[context]:
                    self.members[context].append(nick)
            
        elif mc == '_message_public_question':
            text = ''
            text += str(psyc._query("_nick"))
            if context not in self.tabs:
                self.addTab(context)
            text += ' fragt ' + parsetext(mmp, psyc)
            self.tab_inst[context].append_text(text + '\n')
        
        elif mc.startswith('_status_place_topic') or mc.startswith('_notice_place_topic'):
            topic = psyc._query('_topic')
            context = source.lower()
            if context not in self.tabs:
                self.addTab(context)
            self.tab_inst[context].set_topic(topic)

        elif mc == '_message_public':
            text = ''
            text += str(psyc._query("_nick"))
            if context not in self.tabs:
                self.addTab(context)
            if psyc._query("_action"):
                ptext = parsetext(mmp, psyc)
                if ptext == '':
                    text += " " + psyc._query("_action")
                else:
                    text += " " + psyc._query("_action") + '> ' + ptext
            else:
                text += "> " + parsetext(mmp, psyc)
            #text = text.encode('iso-8859-1')
            self.tab_inst[context].append_text(text + '\n')
            #print '!!' + context + ': ' + text
            
        elif mc == '_status_place_members':
            text = parsetext(mmp, psyc)
            if context not in self.tabs:
                self.addTab(context)
            members = split(psyc._query('_members'), ', ')
            self.members[context] = members
            self.tab_inst[context].append_text(text + '\n')
        
        else:
            # everything we don't know goes into the status tab
            # hopefully parsetext doesn't crash with' bogus' pakets
            text = source.lower() + ' >>> '
            text += parsetext(mmp, psyc)
            self.tab_inst['status'].append_text(text + '\n')



class MainWindow(PSYCPackage):
    # eigentlich brauch das kein schwein oder???
    def __init__(self, argv):
        """ was ich hiermit mache weiss ich noch net genau, eigentlich brauch
            ich es net im moment lebt es für den devel handler"""
        self.center = None
        PSYCPackage.__init__(self)
    
    def title(self, text):
        pass

    def run(self):
        pass

    def quit(self):
        self.center.quit()
        sys.exit(0)

    def connect(self):
        pass

    def write(self, text):
        #print text
        pass

class MySplashScreen(wxSplashScreen):
    def __init__(self, argv, center, config):
        self.center = center
        self.argv = argv
        self.config = config
        bmp = wxImage(opj("GUI/wx/psych2o.jpg")).ConvertToBitmap()
        wxSplashScreen.__init__(self, bmp,
                                wxSPLASH_CENTRE_ON_SCREEN|wxSPLASH_TIMEOUT,
                                4000, None, -1,
                                style = wxFRAME_NO_TASKBAR|wxSTAY_ON_TOP)
        EVT_CLOSE(self, self.OnClose)

    def OnClose(self, evt):
        frame = FriendList(NULL, -1, "pyPSYC 0.0.0.0.0.1", center=self.center, config=self.config)
        frame.Show()
        evt.Skip()

class Application(wxApp):
    def __init__(self, argv, center, config):
        self.center = center
        self.argv = argv
        self.config = config
        wxApp.__init__(self,0)
        #print 'tt'
        
    def OnInit(self):
        #self.frame = FriendList(NULL, -1, "pyPSYC 0.0.0.0.0.1", center=self.center, config=self.config)
        #self.frame.Show(true)
        #sys.stdout = self.frame
        wxInitAllImageHandlers()
        splash = MySplashScreen(self.argv, self.center, self.config)
        self.SetTopWindow(splash)
        splash.Show()
        return True
##
##        self.timer = wxPyTimer(self.socket_check)
##        self.timer.Start(100) # alle 100 ms
##        #print 'ttt'
##
##    def socket_check(self):
##        asyncore.poll(timeout=0.0)
##
    def run(self):
        # blah mainloop
        #print 'tttt'

        from twisted.internet import wxsupport, reactor
        wxsupport.install(self)
        print "running reactor..."
        reactor.run()
