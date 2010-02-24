import gtk
import ConfigParser
import os, sys
import encodings.iso8859_1, encodings.ascii, encodings.cp1250, encodings.utf_8, encodings.utf_16

from pypsyc.center import Client

from tabs.place import PlaceTab
from tabs.user import UserTab
from tabs.rss import RSSTab


class GTKClient(Client):
	def __init__(self, config):
		Client.__init__(self, config)
		self.places_window = gtk.Window(gtk.WINDOW_TOPLEVEL)
		self.places_window.connect('delete_event', 
					   lambda w, e: gtk.main_quit())	
                self.notebook = gtk.Notebook()
                self.notebook.set_tab_pos(gtk.POS_BOTTOM)
                self.places_window.add(self.notebook)
		#self.places_window.show_all()
	def show(self):
		self.places_window.show_all()
  		return gtk.FALSE
	def create_place(self, netname):
		place = PlaceTab(netname, self)
		self.notebook.append_page(place, gtk.Label(netname))
		self.notebook.show_all()
		return place	

def poll():
        import asyncore
        asyncore.poll(timeout = 0.0)
        gtk.timeout_add(250, poll) # 0.25 secs

  
if __name__ == '__main__':
	import sys
	config = ConfigParser.ConfigParser()
  	if sys.platform == 'win32':
		os.environ['PATH'] += ';lib;'
		config.read('.pypsycrc')
	else:
		config.read(os.getenv('HOME') + '/.pypsycrc')
	center = GTKClient(config)	
	
  	splash = gtk.Window()
  	splash.set_decorated(gtk.FALSE)
  	img = gtk.Image()
  	img.set_from_file(config.get('interface',
				     'splashscreen'))
	splash.add(img)
	img.show()
	splash.show()
  	gtk.timeout_add(3500, splash.hide)
  	gtk.timeout_add(4000, center.show)

	rsstab = RSSTab('psyc://adamantine.aquarium/@heise', center)
	center.notebook.append_page(rsstab, gtk.Label('heise rss'))	
	usertab = UserTab('psyc://adamantine.aquarium/~fool', center)
	center.notebook.append_page(usertab, gtk.Label('user dialog'))

        center.online()
	poll()
	gtk.main()
