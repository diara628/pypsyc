import gtk
from pypsyc.objects import PSYCObject

class RSSTab(gtk.Frame, PSYCObject):
  	def __init__(self, netname, center):
		import gobject 
		gtk.Frame.__init__(self, label = netname)
  		PSYCObject.__init__(self, netname, center)
  		
  		vbox = gtk.VPaned()
  		self.add(vbox)
		
		self.label = gtk.Label()
		self.model = gtk.ListStore(str, str, str)
 		self.tree = gtk.TreeView(self.model)
		
		# demos
  		self.model.append(['Handy-Flatrate von DoCoMo in Japan'.encode('utf-8'),
				   'http://heise.de/newsticker/meldung/44883',
				   'Ab Sommer 2004 will auch DoCoMo den Japanern für umgerechnet 31 Euro im Monat eine mobile Flatrate anbieten. mehr...' ])


		renderer = gtk.CellRendererText()
  		column = gtk.TreeViewColumn("Headline", renderer, text=0)
  		self.tree.append_column(column)
  	
		self.tree.connect('row-activated', self.preview)
  
		s1 = gtk.ScrolledWindow()
  		s1.add(self.tree)
  		s1.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
		vbox.pack1(s1, gtk.TRUE)
               
		self.textview = gtk.TextView()
                self.textview.set_cursor_visible(gtk.FALSE)
                self.textview.set_wrap_mode(gtk.WRAP_WORD)
                self.textview.set_editable(gtk.FALSE)
		self.textbuf = self.textview.get_buffer()

		s2 = gtk.ScrolledWindow()
  		s2.add(self.textview)
  		s2.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
  		vbox.pack2(s2) 
  
		#vbox.pack_end(self.textview, gtk.FALSE)
		self.show_all()
  	def msg(self, vars, mc, data, caller):
		if mc == '_status_place_description_news_rss':
			self.label.set_label(data)
  			self.show_all()
			return
		if mc == '_notice_news_headline_rss':
			renderer = gtk.CellRendererText()
  			text = vars.get('_news_headline').encode('utf-8')
  			column = gtk.TreeViewColumn(vars.get('_news_headline'), renderer, text=1)
			self.tree.append_column(column)
			self.show_all()
			return
		PSYCObject.msg(self, vars, mc, data, caller)
  	def preview(self, widget, path, column):
                model, iter = self.tree.get_selection().get_selected()
		self.set_text(model.get_value(iter, 1) + '\n' + model.get_value(iter, 2))	
        def set_text(self, text):
                text = text.encode('utf-8')
                self.textbuf.set_text(text)
