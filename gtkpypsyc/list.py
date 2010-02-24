#!/usr/bin/envv python

import gtk
import gobject 


class ListWindow:
	def __init__(self):
		self.window = gtk.Window(gtk.WINDOW_TOPLEVEL)
		self.netobjects = {}

		self.model = gtk.TreeStore(gtk.gdk.Pixbuf, 
					   str, # _nick_place
					   str, # _source/target/context
					   gobject.TYPE_BOOLEAN)
		self.view = gtk.TreeView(self.model)
		self.view.set_headers_visible(gtk.FALSE)
	
		pxrenderer = gtk.CellRendererPixbuf()
	        renderer = gtk.CellRendererText()
	        column = gtk.TreeViewColumn()
		column.pack_start(pxrenderer, gtk.FALSE)
		column.pack_end(renderer, gtk.TRUE)
		column.set_attributes(pxrenderer, pixbuf=0, visible=3)
		column.set_attributes(renderer, text=1)
	        self.view.append_column(column)

		self.view.show()
  
		vbox = gtk.VBox()
		vbox.show()
		vbox.pack_start(self.view)

		combo = gtk.Combo()
		# TODO: disable editing of current entry, even cursor
		# combobox may be false
		combo.set_popdown_strings(['Offline', 'Online'])
		combo.entry.set_editable(gtk.FALSE)
		combo.show()
		vbox.pack_end(combo, gtk.FALSE)
  		
		self.friendstree = self.model.insert(None, 0, [None, 'Friends', '', False])
 		self.placetree = self.model.insert(None, 1, [None, 'Places', '', False])
		
		#gtk.timeout_add(1000, self.change_icon, 1)
	
		self.view.expand_all()
		
		self.window.add(vbox)
		self.window.show()
		#self.window.connect('delete_event', lambda e, w: gtk.main_quit())
#	def change_icon(self, image):
#		return gtk.FALSE # call only once
	def msg(self, vars, mc, data, caller):
		if mc.startswith('_notice_place_enter'):
			# only if source == self!
			image = gtk.Image()
  			image.set_from_file('./pix/place/icon_f01.png')
			self.netobjects[vars['_context']] = self.model.insert(self.placetree, -1, 
									    [image.get_pixbuf(), 
									     vars['_nick_place'],
									     vars['_context'], True])
			return
		if mc.startswith('_notice_friend_present'):
			image = gtk.Image()
  			image.set_from_file('./pix/friend/present.png')
			self.netobjects[vars['_source']] = self.model.insert(self.friendstree, -1,
									    [image.get_pixbuf(),
									     vars['_nick'], 
									     vars['_source'], True])
			return
