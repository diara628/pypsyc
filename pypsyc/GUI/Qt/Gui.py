import sys
import qt
from qt import SIGNAL, SLOT
import asyncore

import pypsyc.GUI.Abstract.Gui as AbstractGui

class MainDebugWidget(qt.QWidget):
    def __init__(self, parent = None, name = None, fl=0):
        qt.QWidget.__init__(self,parent,name,fl)

        self.textField = qt.QTextBrowser(self)
        self.textField.setGeometry(10, 5, 580, 350)

        self.inputField = qt.QMultiLineEdit(self)
        self.inputField.setGeometry(10, 360, 580 , 100)

        qt.QObject.connect(self.inputField, SIGNAL('returnPressed()'),
                           self.inputText)
        
        self.resize(qt.QSize(600,480).expandedTo(self.minimumSizeHint()))
        sys.stdout = self

    def inputText(self):
        if self.inputField.text().findRev('\n.\n') - self.inputField.text().length() == -3:
            data = self.inputField.text()
            print "packet entered"
            self.inputField.setText('')
    def write(self, string):
        self.textField.append(string)


class RoomWidget(qt.QWidget):
    def __init__(self, parent = None, name = None, fl = 0):
        qt.QWidget.__init__(self, parent, name, fl)
        self.name = name

        self.textField = qt.QTextBrowser(self)
        self.textField.setGeometry(qt.QRect(10, 35, 470, 350))

        self.topicField = qt.QLineEdit(self)
        self.topicField.setGeometry(qt.QRect(10, 5, 580, 25))

        self.nicklist = qt.QListBox(self)
        self.nicklist.setGeometry(qt.QRect(490, 35, 100, 350))

        self.inputField = qt.QLineEdit(self)
        self.inputField.setGeometry(qt.QRect(10, 390, 470, 20))

        qt.QObject.connect(self.inputField, SIGNAL('returnPressed()'),
                           self.inputText)
        qt.QObject.connect(self.topicField, SIGNAL('returnPressed()'),
                           self.inputTopic)

        self.resize(qt.QSize(600,550).expandedTo(self.minimumSizeHint()))
                    
    def inputText(self):
        print self.name + " input: " + self.inputField.text().stripWhiteSpace().latin1()
        self.inputField.setText('')

    def inputTopic(self):
        print self.name + " topic: " + self.topicField.text().stripWhiteSpace().latin1()
        
    def append(self, text): self.textField.append(text.strip() + '\n')
    def set_topic(self, text): self.topicField.setText(text)
    def inputNickCurrent(self):
        print self.name + " current nick:" + self.nickField.text().stripWhiteSpace().latin1()


from pypsyc.PSYC import parsetext        
class RoomGui(qt.QMainWindow, AbstractGui.RoomGui):
    """qt frontend for pyPSYC"""
    # better inherit from widget made with designer?
    def __init__(self):
        qt.QMainWindow.__init__(self)
        #AbstractGui.RoomGui.__init__(self) # attribute error?
        self.model = None
        
        self.rooms = {}
        self.topics = {}
        self.setCaption("Qt pyPSYC Frontend")
        self.menuBar = qt.QMenuBar(self)

        self.workspace = qt.QVBox(self)

        self.roombar = qt.QTabWidget(self.workspace)

        # only in debug mode
        self.roombar.addTab(MainDebugWidget(self.workspace), 'main')

        self.workspace.show()
        self.setCentralWidget(self.workspace)
        self.resize(qt.QSize(600, 500)) # fixed size is bad

        
        fileMenu = [("Exit the program", "Quit", 0, "quit")
                    ]
        connectionMenu = [("Link to your UNL", "Connect", 0, "connect")
                          ]
        self.menus = [("&File", fileMenu),
                 ("&Connection", connectionMenu)]
        self.menuActions = {}
        for menu in self.menus:
            popupMenu = qt.QPopupMenu(self)
            for entry in menu[1]:
                if entry:
                    helptxt, menutxt, accel, callbackName = entry
                    action = qt.QAction(helptxt, qt.QIconSet(qt.QPixmap("./green.gif")),
                                                          menutxt, accel, self)
                    action.addTo(popupMenu)
                    self.menuActions[callbackName] = action
                    callback = getattr(self, callbackName, None)
                    if callback:
                        qt.QObject.connect(action, SIGNAL("activated()"),
                                           callback)
                else:
                    popupMenu.insertSeparator()
            self.menuBar.insertItem(menu[0], popupMenu)
            
        self.show()
        
    def update(self, mc, mmp, psyc):
        context = mmp._query("_context")
        if mc.startswith("_notice_place_enter"):
                ## if _source == ME eigentlich...
                if not self.rooms.has_key(context):
                    self.add_room(context)
                self.rooms[context].append(parsetext(mmp, psyc))
                
#	elif mc == "_status_place_topic":
#		self.topics[context] = parsetext(mmp, psyc)
	elif mc == '_message_public':
            self.rooms[context].append(psyc._query("_nick") + ": " +
                                      parsetext(mmp, psyc))

    def add_room(self, room):
        if not self.rooms.has_key(room):
            self.rooms[room] = RoomWidget(self.workspace, room)
            short = room[room.rfind("@"):] # kurzform für raum... nicht ideal?
            self.roombar.addTab(self.rooms[room], short)
            
    def quit(self):
        self.app.quit()
        
    def connect(self, host = ''):
        self.model.center.connect(host)

class UserGui(qt.QMainWindow, AbstractGui.UserGui):
    pass

class MainGui(qt.QApplication, AbstractGui.MainGui):
    def __init__(self, argv, center):
        qt.QApplication.__init__(self, argv)
        AbstractGui.MainGui.__init__(self, argv)
        
        qt.QObject.connect(self, SIGNAL('lastWindowClosed()'),
                        self, SLOT('quit()'))
        self.timer = qt.QTimer()
        qt.QObject.connect(self.timer, SIGNAL("timeout()"),
                           self.socket_check)
        
    def socket_check(self):
	asyncore.poll(timeout=0.0)
        
    def run(self):       
        self.timer.start(100)
        self.exec_loop()
