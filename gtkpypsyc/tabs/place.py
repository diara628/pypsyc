import gtk
from pypsyc.objects import PSYCObject

class PlaceTab(gtk.Frame, PSYCObject):
	def __init__(self, netname, center):
  		gtk.Frame.__init__(self, label = netname)
		PSYCObject.__init__(self, netname, center)

                vbox = gtk.VBox()
                self.add(vbox)

                self.textview = gtk.TextView()
                self.textview.set_cursor_visible(gtk.FALSE)
                self.textview.set_wrap_mode(gtk.WRAP_WORD)
                self.textview.set_editable(gtk.FALSE)
                self.textbuf = self.textview.get_buffer()

		hbox = gtk.HPaned()
  		hbox.pack1(self.textview)
                vbox.pack_start(hbox)
	
  		# uni, nick
		self.nicklist = gtk.ListStore(str, str)
  		self.nicklist.set_sort_column_id(1, gtk.SORT_ASCENDING)
  		nickview = gtk.TreeView()
  		nickview.set_model(self.nicklist)
		nickview.set_headers_visible(gtk.FALSE)
		
  		col = gtk.TreeViewColumn('Nick', gtk.CellRendererText(), text = 1)
		col.set_resizable(gtk.FALSE)
  		nickview.append_column(col)

		hbox.pack2(nickview, shrink=gtk.FALSE, resize=gtk.FALSE)

		self.entry = gtk.Entry()
                self.entry.set_text('')
                self.entry.connect('activate', self.onEntry)
                vbox.pack_end(self.entry, gtk.FALSE)
                self.show_all()
        def append_text(self, text):
                iter = self.textbuf.get_end_iter()
                text = text.encode('utf-8') + '\n'
                self.textbuf.insert(iter, text)
                iter = self.textbuf.get_end_iter()
                self.textbuf.place_cursor(iter)
                mark = self.textbuf.get_insert()
                self.textview.scroll_mark_onscreen(mark)
	def onEntry(self, widget):
                text = self.entry.get_text()
                #print self.netname, '>>', text
                self.entry.set_text('')
		# handle a command... yes this should not be done that way
		if text and text[0] == '/':
			cmd = text[1:].upper()
			if cmd == 'PART':
				self.sendmsg({'_target' : self.netname},
					     {},
					     '_request_leave',
					     '')
			return
  		self.sendmsg({'_target' : self.netname},
			     {},
			     '_message_public',
			     text)
	def msg(self, vars, mc, data, caller):
		if mc == '_message_public':
			self.append_text('%s: %s'%(vars['_nick'], data))
			return
		if mc == '_message_public_question':
			self.append_text('%s %s: %s'%(vars['_nick'],
						      'fragt', 
						      data))
			return
		if mc == '_message_public_text_action':
			self.append_text('%s %s: %s'%(vars['_nick'], 
						      vars['_action'], 
						      data))
			return
		if mc == '_status_place_members':
  			# _list_members, _list_members_nicks
			for i in range(0, len(vars['_list_members'])):
				self.nicklist.append((vars['_list_members'][i], 
						      vars['_list_members_nicks'][i]))
			return
		if mc.startswith('_notice_place_leave'):
  			return
		if mc.startswith('_notice_place_enter'):
  			self.nicklist.append((vars['_source'], vars['_nick']))
			return
		PSYCObject.msg(self, vars, mc, data, caller)


