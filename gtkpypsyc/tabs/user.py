import gtk
from pypsyc.objects import PSYCObject

class UserTab(gtk.Frame):
	def __init__(self, netname, center):
		gtk.Frame.__init__(self, label = netname)
		self.textview = gtk.TextView()
                self.textview.set_cursor_visible(gtk.FALSE)
                self.textview.set_wrap_mode(gtk.WRAP_WORD)
                self.textview.set_editable(gtk.FALSE)
                self.textbuf = self.textview.get_buffer()
		s = gtk.ScrolledWindow()
  		s.set_policy(gtk.POLICY_NEVER, gtk.POLICY_AUTOMATIC)
  		s.add(self.textview)
	
		pane = gtk.VPaned()
		#pane.pack1(s)
		
		h = gtk.VBox()
		pane.pack2(h, shrink=gtk.FALSE, resize = gtk.FALSE)
		pane.pack1(s)
		box = gtk.HBox()
  		box.pack_start(gtk.Button(label='spacing'), expand=gtk.FALSE)
  		h.pack_start(box, expand=gtk.FALSE)

  		self.entryfield = gtk.Entry()
 		h.pack_start(self.entryfield, expand=gtk.FALSE) 
	
		self.add(pane)
		self.show_all()
