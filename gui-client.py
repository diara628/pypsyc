#!/usr/bin/env python

# get stuff above at twistedmatrix.com
import ConfigParser
import os
import sys
# here we start importing our own modules
from pypsyc.PSYC.PSYCMessagecenter import PSYCMessagecenter
# import packages
from pypsyc.PSYC.PSYCRoom import Conferencing as ConferencingPackage
from pypsyc.PSYC.PSYCRoom import Friends as FriendsPackage
from pypsyc.PSYC.PSYCRoom import User as UserPackage
from pypsyc.PSYC.PSYCRoom import Authentication as AuthenticationPackage
from pypsyc.PSYC.PSYCRoom import Devel as DevelPackage
#import Listener

# for linux/posix this should work
CONFIG_FILE = os.getenv("HOME") + "/.pypsyc/config"

# windows users should uncomment the next line and comment the one above
# CONFIG_FILE  = 'config'

config = ConfigParser.ConfigParser()    
config.read(CONFIG_FILE)	

center = PSYCMessagecenter(config)

gui = None
Gui = None

try:
    guitype = config.get("gui", "type")
    if guitype == "Tkinter":
        import GUI.Tkinter.Gui as Gui
    elif guitype == "Qt":
        import GUI.Qt.Gui as Gui
    elif guitype == 'wx':
        import GUI.wx.devGui as Gui

    if Gui:
        if guitype == 'wx':
            gui = Gui.Application(sys.argv, center, config)
        else:
            gui = Gui.Application(sys.argv, center)
    ## hier muss man besser entscheiden, was ein Toplevel() und was ein Tk() ist!
    if config.get("packages", "conferencing") == "enabled":
        conferencing_gui = Gui.RoomGui()
	center.register(ConferencingPackage(conferencing_gui))

    if config.get("packages", "friends") == "enabled":
        friendlist = Gui.FriendList()
        center.register(FriendsPackage(friendlist))

    if config.get("packages", "user") == "enabled":
        usergui = Gui.UserGui()
        center.register(UserPackage(usergui))

    if config.get("packages", "devel") == "enabled":
        debuggui = Gui.MainWindow(center)
        debuggui.title("debug window")
        center.register(DevelPackage(debuggui))
	
  	## hier was in der Art von setMainWindow()
except ConfigParser.NoSectionError:
    print "Error reading config file"

center.register(AuthenticationPackage(config))

gui.run()

