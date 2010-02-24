#!/usr/bin/envv python

import gtk
import gobject 

class UI:
	def __init__(self):
		self.window = gtk.Window(gtk.WINDOW_TOPLEVEL)
		self.netobjects = {}

		self.model = gtk.TreeStore(gtk.gdk.Pixbuf, 
					   gobject.TYPE_STRING, 
					   gobject.TYPE_BOOLEAN)
		self.view = gtk.TreeView(self.model)
		self.view.set_headers_visible(gtk.FALSE)
  		
	
		pxrenderer = gtk.CellRendererPixbuf()
	        renderer = gtk.CellRendererText()
	        column = gtk.TreeViewColumn()
		column.pack_start(pxrenderer, gtk.FALSE)
		column.pack_end(renderer, gtk.TRUE)
		column.set_attributes(pxrenderer, pixbuf=0, visible=2)
		column.set_attributes(renderer, text=1)
	        self.view.append_column(column)

		self.view.show()
  
		vbox = gtk.VBox()
		vbox.show()
		vbox.pack_start(self.view)

		combo = gtk.Combo()
		# TODO: disable editing of current entry, even cursor
		combo.set_popdown_strings(['Offline', 'Online'])
		combo.entry.set_editable(gtk.FALSE)
		combo.show()
		vbox.pack_end(combo, gtk.FALSE)
  		
		self.friendstree = self.model.insert(None, 0, [None, 'Friends', False])
 		self.placetree = self.model.insert(None, 1, [None, 'Places', False])
		
		self.append_person('fippo')
		self.append_place('PSYC')	

		gtk.timeout_add(1000, self.change_icon, 1)
		gtk.timeout_add(3000, self.change_icon, 2)
		gtk.timeout_add(5000, self.change_icon, 3)
	
		self.view.expand_all()
		
		self.window.add(vbox)
		self.window.show()
  		self.window.connect('delete_event', lambda e, w: gtk.main_quit())
	def append_person(self, name):
		self.model.insert(self.friendstree, -1, [None, name, True])
	def append_place(self, name):
		image = gtk.Image()
  		image.set_from_file('./pix/place/icon_f01.png')
		pxbuf = image.get_pixbuf()
		self.netobjects[name] = self.model.insert(self.placetree, -1, [pxbuf, name, True])
	def change_icon(self, image):
		print 'change', image
		return gtk.FALSE # call only once

u = UI()
gtk.mainloop()
