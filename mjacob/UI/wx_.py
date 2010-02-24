#!/usr/bin/env python
# -*- coding: utf-8 -*-

import wx

from base import Module
from lib import psyctext
from twisted_client import install_wx


class Tab(wx.Panel):
    def __init__(self, parent, name):
        self.name = name
        wx.Panel.__init__(self, parent, -1)
        self.textctrl = wx.TextCtrl(self, -1, style = wx.TE_MULTILINE|wx.TE_READONLY)
        self.users = []

        def OnResize(event):
            self.textctrl.SetSize(event.GetSize())
        self.Bind(wx.EVT_SIZE, OnResize, self)


class MainWindow(Module, wx.Frame):
    methods = ['_message*']
    def __init__(self, ui):
        wx.Frame.__init__(self, None, -1, size = (800, 600))

        self.Bind(wx.EVT_CLOSE, self.OnClose, self)

        self.ui = ui

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
        self.add_tab("psyc://%s" % self.ui.base.config.host)

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
                self.center.input(pagename, value)
                self.input.SetValue('')

        event.Skip()

    def OnChangeTab(self, event):
        self.userlist.Set(self.nb.GetCurrentPage().users)

    def OnConnect(self, event):
        self.center.connect(self.center.config.host)
        self.ui.connected = True

    def OnOpenDebugWindow(self, event):
        # open or close window:
        if not self.ui.debugwindow.Show(True): self.ui.debugwindow.Show(False)

    def OnClose(self, event):
        pass

    def add_tab(self, name):
        self.tabs[name] = Tab(self.nb, name)
        self.nb.AddPage(self.tabs[name], name)

    def handle_message_public(self, packet, physsource):
        self._print(packet.mmpvars['_context'], "%s: %s" % (packet.psycvars['_nick'], psyctext(packet)))

    handle_message_echo_public = handle_message_public

    def _print(self, window, text):
        if window not in self.tabs:
            self.add_tab(window)
        self.tabs[window].textctrl.AppendText(text + '\n')



class UI:
    def __init__(self, base):
        self.base = base
        self.gui = wx.PySimpleApp()
        self.mainwindow = MainWindow(self)
        self.base.register_module(self.mainwindow)
        install_wx(self.gui)
