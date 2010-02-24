#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Licensed under the MIT license
# http://opensource.org/licenses/mit-license.php

# <C> Copyright 2007, Manuel Jacob

import wx

from twisted.internet import reactor

from UI import base
from PSYC.PSYCPacket import PSYCPacket

class Tab(wx.Panel):
    def __init__(self, parent, name):
        self.name = name
        wx.Panel.__init__(self, parent, -1)
        self.textctrl = wx.TextCtrl(self, -1, style = wx.TE_MULTILINE|wx.TE_READONLY)
        self.users = []

        def OnResize(event):
            self.textctrl.SetSize(event.GetSize())
        self.Bind(wx.EVT_SIZE, OnResize, self)


class MainWindow(wx.Frame):
    def __init__(self, ui):
        wx.Frame.__init__(self, None, -1, size = (800, 600))

        self.Bind(wx.EVT_CLOSE, self.OnClose, self)

        self.ui = ui
        self.factory = self.ui.factory

        self.tabs = {}
        splitter = wx.SplitterWindow(self, -1)

        self.pl = wx.Panel(splitter, -1)
        sizer = wx.GridBagSizer(0, 0)

        self.nb = wx.Notebook(self.pl, -1, style = wx.NB_TOP)
        sizer.Add(self.nb, (0, 0), (1, 1), wx.EXPAND)
        sizer.AddGrowableCol(0)
        sizer.AddGrowableRow(0)

        self.input = wx.TextCtrl(self.pl, -1)
        sizer.Add(self.input, (1, 0), (1, 1), wx.EXPAND)
        self.pl.SetSizerAndFit(sizer)
        self.add_tab('Server')

        self.pr = wx.Panel(splitter, -1) # right panel
        self.userlist = wx.ListBox(self.pr, -1, (0, 5), style = wx.SUNKEN_BORDER)

        self.nb.Bind(wx.EVT_NOTEBOOK_PAGE_CHANGED, self.OnChangeTab, self.nb)

        def OnResize(event):
            size = event.GetSize()
            self.userlist.SetSize((size[0], size[1] - 10))
        self.pr.Bind(wx.EVT_SIZE, OnResize, self.pr)

        splitter.SplitVertically(self.pl, self.pr, self.GetSize()[0] * 0.7)
        splitter.SetSashGravity(1)

        mainmenu = wx.Menu()

        menuitem = mainmenu.Append(-1, '&Connect', 'Connect to the server')
        self.Bind(wx.EVT_MENU, self.OnConnect, menuitem)

        menuitem = mainmenu.Append(-1, '&Debug window',
                                   'Open or close debug window')
        self.Bind(wx.EVT_MENU, self.OnOpenDebugWindow, menuitem)

        mainmenu.AppendSeparator()

        menuitem = mainmenu.Append(-1, '&Exit', 'Exit pyPSYC')
        self.Bind(wx.EVT_MENU, self.OnClose, menuitem)

        menubar = wx.MenuBar()
        menubar.Append(mainmenu, '&pyPSYC')

        self.SetMenuBar(menubar)

        self.input.Bind(wx.EVT_KEY_DOWN, self.OnKeyDown)

        self.Show(True)

    def OnKeyDown(self, event):
        if event.GetKeyCode() in (wx.WXK_RETURN, wx.WXK_NUMPAD_ENTER):
            pagename = self.nb.GetCurrentPage().name
            value = self.input.GetValue()
            if value:
                if pagename == 'Server' or value.startswith('/'):
                    self.ui.server_command(value, self.nb.GetCurrentPage().name)

                elif '@' in pagename:
                    self.factory.sc.castmsg(pagename, '_message_public',
                                        value, {})

                elif '~' in pagename:
                    self.factory.sc.sendmsg(pagename, '_message_private',
                                        value, {})

                self.input.SetValue('')

        event.Skip()

    def OnChangeTab(self, event):
        self.userlist.Set(self.nb.GetCurrentPage().users)

    def OnConnect(self, event):
        self.factory.connect()
        self.ui.connected = True

    def OnOpenDebugWindow(self, event):
        # open or close window:
        if not self.ui.debugwindow.Show(True): self.ui.debugwindow.Show(False)

    def OnClose(self, event):
        if self.ui.connected:
            self.ui.server_command('/quit', None)
        else:
            reactor.stop()

    def add_tab(self, name):
        self.tabs[name] = Tab(self.nb, name)
        self.nb.AddPage(self.tabs[name], name)


class DebugWindow(wx.Frame):
    def __init__(self, factory):
        wx.Frame.__init__(self, parent = None, id = -1,
                          title = 'pyPSYC debug window', size = (800, 600),
                          style = wx.DEFAULT_FRAME_STYLE|
                          wx.NO_FULL_REPAINT_ON_RESIZE)
        self.Bind(wx.EVT_CLOSE, self.OnClose, self)

        self.tree = wx.TreeCtrl(self, -1, wx.DefaultPosition, (-1,-1),
                                wx.TR_HIDE_ROOT|wx.TR_HAS_BUTTONS)
        self.treeroot = self.tree.AddRoot('Programmer')

    def OnClose(self, event):
        self.Show(False)


class Interface(base.BaseUI):
    def __init__(self, factory):
        self.factory = factory
        self.gui = wx.PySimpleApp()
        self.mainwindow = MainWindow(self)
        self.debugwindow = DebugWindow(self)

    def _print(self, window, text):
        if window not in self.mainwindow.tabs:
            self.mainwindow.add_tab(window)
        self.mainwindow.tabs[window].textctrl.AppendText(text + '\n')

    def pre_print(self, packet):
        print ('recv', packet)
        tmp = self.debugwindow.tree.AppendItem(self.debugwindow.treeroot,
                                               'Incoming Packet %s'
                                               % self.inpacketcount)
        self.debugwindow.tree.AppendItem(tmp, "MMPVars: %s" % packet.mmpvars)
        self.debugwindow.tree.AppendItem(tmp, "PSYCVars: %s" % packet.psycvars)
        self.debugwindow.tree.AppendItem(tmp, "Method: %s" % packet.mc)
        self.debugwindow.tree.AppendItem(tmp, "Text: %s" % packet.text)
    
    def pre_send(self, packet):
        print ('send', packet)
        tmp = self.debugwindow.tree.AppendItem(self.debugwindow.treeroot,
                                               'Outgoing Packet %s'
                                               % self.outpacketcount)
        self.debugwindow.tree.AppendItem(tmp, "MMPVars: %s" % packet.mmpvars)
        self.debugwindow.tree.AppendItem(tmp, "PSYCVars: %s" % packet.psycvars)
        self.debugwindow.tree.AppendItem(tmp, "Method: %s" % packet.mc)
        self.debugwindow.tree.AppendItem(tmp, "Text: %s" % packet.text)

    def handle_echo_place_enter_login(self, packet):
        self._print(packet.vars['_source_relay'], packet.text)
        self.mainwindow.tabs[packet.vars['_source_relay']].users = packet.vars['_list_members']

    def handle_echo_place_enter(self, packet):
        self._print(packet.vars['_nick_place'], packet.text)
        self.mainwindow.tabs[packet.vars['_nick_place']].users = packet.vars['_list_members']
    

if __name__ == '__main__':
    app = wx.PySimpleApp()
    MainWindow()
    app.MainLoop()

##class Tab(wx.Panel):
##    def __init__(self, name, main):
##        self.name = name
##        self.main = main
##        self.ui = self.main.ui
##        self.factory = self.ui.factory
##        wx.Panel.__init__(self, main.nb, -1)
##        self.textbox = wx.TextCtrl(self, -1, style = wx.TE_MULTILINE|
##                                                     wx.TE_READONLY,)
##        self.input = wx.TextCtrl(self, -1)
##        #self.input.SetFocus()
##        self.input.Bind(wx.EVT_KEY_DOWN, self.OnKeyDown)
##
##    def OnKeyDown(self, event):
##        if event.GetKeyCode() in (wx.WXK_RETURN, wx.WXK_NUMPAD_ENTER):
##            if self.input.GetValue():
##                self.factory.sc.castmsg(self.name, '_message_public',
##                                        self.input.GetValue(), {})
##                self.input.SetValue('')
##
##        event.Skip()
#
#
#class Tab(wx.Panel):
#    def __init__(self, name, main):
#        self.name = name
#        self.main = main
#        self.ui = self.main.ui
#        if hasattr(self.ui, 'factory'):
#            self.factory = self.ui.factory
#        wx.Panel.__init__(self, main.nb, -1, size = wx.DefaultSize)
#        #wx.Frame.__init__(self, None, -1, size = wx.DefaultSize)
#
#        #splitter = wx.SplitterWindow(self, -1)
#        #pl = wx.Panel(splitter, -1, size = wx.DefaultSize) # panel left
#        ##pls = wx.BoxSizer(wx.VERTICAL)
#        #wx.TextCtrl(pl, -1, style = wx.TE_MULTILINE|wx.TE_READONLY, size = wx.DefaultSize)
#
#        #pr = wx.Panel(splitter, -1, size = wx.DefaultSize) # panel right
#        #wx.ListCtrl(pr, -1, size = wx.DefaultSize)
#
#        #splitter.SplitVertically(pl, pr)
#
#        splitter = wx.SplitterWindow(self, -1)
#        panel1 = wx.Panel(splitter, -1)
#        wx.StaticText(panel1, -1,
#                    "Whether you think that you can, or that you can't, you are usually right."
#                    "\n\n Henry Ford",
#            (100,100), style=wx.ALIGN_CENTRE)
#        panel1.SetBackgroundColour(wx.LIGHT_GREY)
#        panel2 = wx.Panel(splitter, -1)
#        panel2.SetBackgroundColour(wx.WHITE)
#        splitter.SplitVertically(panel1, panel2)
#        self.Centre()
#
#
#class MainWindow(wx.Frame):
#    def __init__(self, ui):
#        wx.Frame.__init__(self, parent = None, id = -1, title = 'pyPSYC',
#                          size = (800, 600),
#        style = wx.DEFAULT_FRAME_STYLE | wx.NO_FULL_REPAINT_ON_RESIZE)
#
#        self.Bind(wx.EVT_CLOSE, self.OnClose, self)
#
#        self.ui = ui
#        if hasattr(self.ui, 'factory'):
#            self.factory = self.ui.factory
#
#        self.CreateStatusBar()
#
#        # Set up and create the menu
#        mainmenu = wx.Menu()
#
#        menuitem = mainmenu.Append(-1, '&Connect', 'Connect to the server')
#        self.Bind(wx.EVT_MENU, self.OnConnect, menuitem)
#
#        menuitem = mainmenu.Append(-1, '&Debug window',
#                                   'Open or close debug window')
#        self.Bind(wx.EVT_MENU, self.OnOpenDebugWindow, menuitem)
#
#        mainmenu.AppendSeparator()
#
#        menuitem = mainmenu.Append(-1, '&Exit', 'Exit pyPSYC')
#        self.Bind(wx.EVT_MENU, self.OnClose, menuitem)
#
#        menubar = wx.MenuBar()
#        menubar.Append(mainmenu, '&pyPSYC')
#        self.SetMenuBar(menubar)
#
#        self.nb = wx.Notebook(self, -1, style=wx.NB_BOTTOM)
#
#        self.tabs = {}
#
#        self.Show(True)
#
#    def OnConnect(self, event):
#        self.factory.connect()
#
#    def OnOpenDebugWindow(self, event):
#        # open or close window:
#        if not self.ui.debugwindow.Show(True): self.ui.debugwindow.Show(False)
#
#    def OnClose(self, event):
#        reactor.stop()
#
#
#class DebugWindow(wx.Frame):
#    def __init__(self, factory):
#        wx.Frame.__init__(self, parent = None, id = -1,
#                          title = 'pyPSYC debug window', size = (800, 600),
#                          style = wx.DEFAULT_FRAME_STYLE|
#                          wx.NO_FULL_REPAINT_ON_RESIZE)
#        self.Bind(wx.EVT_CLOSE, self.OnClose, self)
#
#        self.tree = wx.TreeCtrl(self, -1, wx.DefaultPosition, (-1,-1),
#                                wx.TR_HIDE_ROOT|wx.TR_HAS_BUTTONS)
#        self.treeroot = self.tree.AddRoot('Programmer')
#
#    def OnClose(self, event):
#        self.Show(False)
#
#
#class Interface:#(base.BaseUI):
#    def __init__(self, factory):
#        self.gui = wx.PySimpleApp()
#        if factory:
#            self.factory = factory
#            reactor.registerWxApp(self.gui)
#        self.mainwindow = MainWindow(self)
#        self.debugwindow = DebugWindow(self)
#        window = 'Server'
#        self.mainwindow.tabs[window] = Tab(window, self.mainwindow)
#        self.mainwindow.nb.AddPage(self.mainwindow.tabs[window], window)
#
#    def _print(self, window, text):
#        if window not in self.mainwindow.tabs:
#            self.mainwindow.tabs[window] = Tab(window, self.mainwindow)
#
#            #def OnOvrSize(event, tab=self.mainwindow.tabs[window]):
#            #    size = event.GetSize()
#            #    textboxsize = (size[0], size[1] - 24)
#            #    inputpos = (0, size[1] - 24)
#            #    tab.textbox.SetSize(textboxsize)
#            #    tab.input.SetPosition(inputpos)
#            #    tab.input.SetSize((size[0], 21))
#
#            #wx.EVT_SIZE(self.mainwindow.tabs[window], OnOvrSize)
#
#            self.mainwindow.nb.AddPage(self.mainwindow.tabs[window], window)
#
#        self.mainwindow.tabs[window].textbox.AppendText(text)
#
#
#    def pre_print(self, packet):
#        tmp = self.debugwindow.tree.AppendItem(self.debugwindow.treeroot,
#                                               'Incoming Packet %s'
#                                               % self.inpacketcount)
#        self.debugwindow.tree.AppendItem(tmp, "MMPVars: %s" % packet.mmpvars)
#        self.debugwindow.tree.AppendItem(tmp, "PSYCVars: %s" % packet.psycvars)
#        self.debugwindow.tree.AppendItem(tmp, "Method: %s" % packet.mc)
#        self.debugwindow.tree.AppendItem(tmp, "Text: %s" % packet.text)
#    
#    def pre_send(self, packet):
#        tmp = self.debugwindow.tree.AppendItem(self.debugwindow.treeroot,
#                                               'Outgoing Packet %s'
#                                               % self.outpacketcount)
#        self.debugwindow.tree.AppendItem(tmp, "MMPVars: %s" % packet.mmpvars)
#        self.debugwindow.tree.AppendItem(tmp, "PSYCVars: %s" % packet.psycvars)
#        self.debugwindow.tree.AppendItem(tmp, "Method: %s" % packet.mc)
#        self.debugwindow.tree.AppendItem(tmp, "Text: %s" % packet.text)
#
#if __name__ == '__main__':
#    interface = Interface(None)
#    interface.gui.MainLoop()
