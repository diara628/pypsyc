# $Id: ui.py,v 1.7 2003/09/23 18:04:27 an Exp $
# $Revision

import gc

import os, sys, time, string
import asyncore
import gtk, pango
import ConfigParser

main_window = None
tab_windows = [] 

nl = "\r\n"

class Window:

    vbox = None
    hbox = None
    scrollwin = None
    textview = None
    textbuf = None
    label = None
    infobar = None
    target = ""
    view = None

    def __init__(self, target, label):
        global tab_windows

        self.vbox = gtk.VBox(gtk.FALSE, 0)
        self.vbox.show()
        
        self.hbox = gtk.HBox(gtk.FALSE, 0)
        self.hbox.show()
        
        self.vbox.pack_start(self.hbox, gtk.FALSE, gtk.FALSE, 0)

        self.infobar = gtk.Button(target)
        self.hbox.pack_start(self.infobar, gtk.TRUE, gtk.TRUE, 0)
        self.infobar.show()

        self.closer = gtk.Button("close")
        self.hbox.pack_start(self.closer, gtk.FALSE, gtk.FALSE, 0)
        self.closer.show()
        self.closer.connect("clicked", self.delete)

        self.scrollwin = gtk.ScrolledWindow()
        self.scrollwin.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_ALWAYS)

        self.textview = gtk.TextView()
        self.textview.set_cursor_visible(gtk.FALSE)
        self.textview.set_wrap_mode(gtk.WRAP_WORD)
        self.textview.set_editable(gtk.FALSE)
        self.textbuf = self.textview.get_buffer()

        self.scrollwin.add(self.textview)
        self.scrollwin.show()

        font = pango.FontDescription('courier Medium 12')
        self.textview.modify_font(font)
        self.textview.show()

        self.target = target

        if label == None:
            if target.find("@") != -1:
                label = target[target.rfind("@"):]
            elif target.find("~") != -1:
                label = target[target.rfind("~")+1:]
            else:
                label = target

        self.label = gtk.Label(label)

        self.vbox.pack_start(self.scrollwin, gtk.TRUE, gtk.TRUE, 0)

        main_window.notebook.append_page(self.vbox, self.label)

        tab_windows.append(self)

    def __del__(self):
        pass

    def set_view(self, view):
        self.view = view

    def delete(self, foo):
        global tab_windows

        num = main_window.notebook.page_num(self.vbox)
        main_window.notebook.remove_page(num)
        self.view.delete(self.target)
        tab_windows.remove(self)
        
        #gc.collect()

    def append_text(self, text):
        try:
            iter = self.textbuf.get_end_iter()
            # sieht krank aus, funktioniert aber
            text = text.decode("iso-8859-1").encode("utf-8")
            text += nl
            self.textbuf.insert(iter, text)
            iter = self.textbuf.get_end_iter()
            self.textbuf.place_cursor(iter)
            mark = self.textbuf.get_insert()
            #mark = self.textbuf.get_mark_at_iter(iter)
            self.textview.scroll_mark_onscreen(mark)

            cur_page = main_window.notebook.get_current_page()
            win = None
            for w in tab_windows:
                if main_window.notebook.page_num(w.vbox) == cur_page:
                    win = w
            if win != self:
                self.label.modify_fg(gtk.STATE_NORMAL,
                            self.label.get_colormap().alloc_color('darkred'))
        except:
            pass

class MainWindow:
    
    window = None
    vbox = None
    notebook = None
    entry = None
    statusbar = None
    font = None
    entry_handler = None
 
    def __init__(self, config, entry_handler):
        global main_window

        self.entry_handler = entry_handler

        # create a new window
        self.window = gtk.Window(gtk.WINDOW_TOPLEVEL)
        self.window.set_size_request(350, 400)
        self.window.set_title("theraPY")
        self.window.connect("delete_event", gtk.mainquit)

        self.vbox = gtk.VBox(gtk.FALSE, 0)
        self.window.add(self.vbox)
        self.vbox.show()

        self.notebook = gtk.Notebook()
        self.notebook.set_tab_pos(gtk.POS_BOTTOM)
        # window.add(notebook)        
        self.vbox.pack_start(self.notebook, gtk.TRUE, gtk.TRUE, 0)
        self.notebook.show()

        self.entry = gtk.Entry()
        self.entry.set_max_length(256)
        #self.entry.set_flags(gtk.HAS_DEFAULT)
        self.entry.connect("activate", self.enter_callback, self.entry)
        self.entry.set_text("")
        # entry.insert_text(" world", len(entry.get_text()))
        # entry.select_region(0, len(entry.get_text()))
        self.vbox.pack_start(self.entry, gtk.FALSE, gtk.FALSE, 0)
        self.font = pango.FontDescription('courier Medium 12')
        self.entry.modify_font(self.font)
        self.entry.show()

        self.statusbar = gtk.Statusbar()
        self.vbox.pack_start(self.statusbar, gtk.FALSE, gtk.FALSE, 0)
        self.statusbar.show()

        self.window.connect('key_press_event', self.key_press_callback)
        self.window.show()

        main_window = self

    def key_press_callback(self, widget, event, *args):
        key = event.keyval
        if event.state & gtk.gdk.MOD1_MASK:
            if key > 47 and key < 58:
                if key == 48:
                    key += 10
                key -= 49
                try:
                    self.notebook.set_current_page(key)
                except:
                    pass
                return 1
            elif key == 110:
                self.notebook.next_page()
                return 1
            elif key == 112:
                self.notebook.prev_page()
        return 0

    def enter_callback(self, widget, entry):
        global tab_windows

        text = entry.get_text()

        cur_page = main_window.notebook.get_current_page()
        target = None
        for w in tab_windows:
            if main_window.notebook.page_num(w.vbox) == cur_page:
                target = w.target
                win = w

        self.entry_handler(win, target, text)

        entry.set_text("")

def update_notebook_tabs():
    cur_page = main_window.notebook.get_current_page()
    win = None
    for w in tab_windows:
        if main_window.notebook.page_num(w.vbox) == cur_page:
            win = w
    if not win:
        return

    win.label.modify_fg(gtk.STATE_NORMAL,
                    win.label.get_colormap().alloc_color('black'))

    if not main_window.entry.flags() & gtk.HAS_FOCUS:
        i1 = win.textbuf.get_iter_at_mark(win.textbuf.get_insert())
        i2 = win.textbuf.get_iter_at_mark(win.textbuf.get_selection_bound())
        if not i1.compare(i2):
            main_window.entry.grab_focus()
            p = main_window.entry.get_text().__len__()
            main_window.entry.select_region(p, p)
    

def poll():
    asyncore.poll(timeout = 0.0)
    gtk.timeout_add(250, poll)
    update_notebook_tabs()

def mainloop():
    poll() 
    gtk.main()
