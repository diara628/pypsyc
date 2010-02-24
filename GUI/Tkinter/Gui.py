import GUI.Abstract.Gui as AbstractGui
import Tkinter, asyncore, sys

from pypsyc.PSYC.PSYCRoom import  PSYCPackage
class FriendList(Tkinter.Listbox):
	def __init__(self):
		self.packagename = "Friends gui"

		root = Tkinter.Toplevel(height=480, width=150)
		root.title("friends online:")

		self.mapping = {}
		self.model = None
		
		Tkinter.Listbox.__init__(self, root)
		self.grid(row = 0, column = 0, sticky=Tkinter.E + Tkinter.W + Tkinter.N + Tkinter.S)

		self.bind("<Double-Button-1>", self.on_leftclick)
		self.bind("<Double-Button-3>", self.on_rightclick)

		bframe = Tkinter.Frame(root)
		bframe.grid(row=1, column = 0, sticky = Tkinter.W + Tkinter.E)
		self.linklabel = Tkinter.Label(bframe, text="unlinked")
		self.linklabel.grid(row=0, column = 0, sticky = Tkinter.W)
		#u = Tkinter.Button(bframe, text="update", command=self.update_friends)
		#u.grid(row=0, column = 1, sticky=Tkinter.E)	
		
	def set_model(self, model): self.model = model

	def set_status(self, status):
		if status == "_notice_link":
			self.linklabel["text"] = "link"
		elif status == "_notice_unlink":
			self.linklabel["text"] = "unlink"			
		
	def on_leftclick(self, event):
		if self.selection_get():
			self.model.set_target(self.selection_get())
			self.model.set_mc("_internal_message_private_window_popup")
			self.model.castmsg()

	def on_rightclick(self, event):
		if self.selection_get():
			#print "we should pop up a context menu for", self.selection_get()
			self.model.set_target(self.selection_get())
			self.model.set_mc("_request_examine")
			self.model.send()
	def received(self, source, mc, mmp, psyc):
		# das print-zeugs is doch nicht ganz so nutzlos!
		# muss es aber werden, oder?
		if mc == "_notice_friend_present":
			self.present(mmp.get_source())
		elif mc == "_notice_friend_absent":
			self.absent(mmp.get_source())
		elif mc == "_print_notice_friend_present":
			#print "friend present", psyc._query("_friends")
			pass
		elif mc == "_print_notice_friend_absent":
			#print "friend absent", psyc._query("_friends")
			pass
		elif mc == "_print_list_friends_present":
			#print "friends present", psyc._query("_friends")
			#print psyc.get_text()
			for friend in psyc._query("_friends").split(" "):
				print friend
			print "friends:", psyc.get_text()
		elif mc == "_notice_link" or mc == "_notice_unlink":
			self.set_status(mc)
		
	def present(self, nick):
		if not self.mapping.has_key(nick):
			self.mapping[nick] = self.size() # where we insert it
			self.insert(self.size(), nick)
			
	def absent(self, nick):
		if self.mapping.has_key(nick):
			self.delete(self.mapping[nick])


from pypsyc.PSYC import parsetext, get_user
class UserGui(AbstractGui.UserGui):
	def __init__(self):
		AbstractGui.UserGui.__init__(self)
		self.model = None
		self.windows = {}
		
	def makewindow(self, source):
		# better check it again...
		if self.windows.has_key(source):
			return
		
		win = Tkinter.Toplevel()
		win.title("Dialog with " + source)
		win.protocol("WM_DELETE_WINDOW", lambda: self.deletewindow(source))
		dframe = Tkinter.Frame(win)
		displayfield = Tkinter.Text(dframe, width=50, height=15,
					    state=Tkinter.DISABLED,
					    wrap=Tkinter.WORD)
		displayfield.grid(row=0, column=0)
		scrollbar = Tkinter.Scrollbar(dframe,
					      command=displayfield.yview)
		scrollbar.grid(row=0, column=1, sticky = Tkinter.N + Tkinter.S)
		displayfield.config(yscrollcommand=scrollbar.set)
		dframe.pack()
		
		entryfield = Tkinter.Text(win, width=54, height=5)
		entryfield.pack()
		frame = Tkinter.Frame(win)
		entrybutton = Tkinter.Button(frame, text="send",
					     command=lambda: self.say(source))
		
		entrybutton.grid(row = 0, column = 0)
		frame.pack()
		self.windows[source] = {"window" : win,
					"displayfield" : displayfield,
					"entryfield" : entryfield,
					"button" : entrybutton}

	def deletewindow(self, source):
		self.windows[source]["window"].destroy()
		del self.windows[source]

	def append_text(self, displayfield, text, encoding="iso-8859-1"):
		displayfield["state"] = Tkinter.NORMAL
		displayfield.insert(Tkinter.END,
				      text.strip().decode(encoding) + '\n')
		displayfield["state"] = Tkinter.DISABLED
		displayfield.yview(Tkinter.END)

	def get_input(self, entryfield, encoding="iso-8859-1"):
		text = entryfield.get(0.0, Tkinter.END).encode(encoding)
		entryfield.delete(0.0, Tkinter.END)
		return text

	def say(self, source):
		self.model.set_target(source)
		self.model.set_mc("_message_private")

		self.model.psyc._assign("_nick", get_user(self.model.center.ME()))
		
		text = self.get_input(self.windows[source]["entryfield"])
		self.model.set_text(text.strip())

		self.append_text(self.windows[source]["displayfield"], "Du sagst: " + text)
		self.model.send()
		
	def received(self, source, mc, mmp, psyc):
		if mc == "_message_private":
			source = mmp.get_source()
			if not self.windows.has_key(source):
				self.makewindow(source)
			self.append_text(self.windows[source]["displayfield"],
					 get_user(source)+":"+parsetext(mmp, psyc))
		elif mc == "_internal_message_private_window_popup":
			target = mmp._query("_target")
			print "target:", target
			if not self.windows.has_key(target):
				self.makewindow(target)
				
			
from pypsyc.PSYC import parsetext
class RoomGui(AbstractGui.RoomGui, Tkinter.Toplevel):
	def __init__(self):		
		Tkinter.Toplevel.__init__(self)
		self.model = None

		self.buffers = {}
		self.topics = {}
		
##		self.menu = Tkinter.Menu(self)
##		self.config(menu=self.menu)
		
##		options = Tkinter.Menu(self.menu)
##		options.add_command(label="show nicklist",
##				    command=self.show_nicklist)
##		options.add_command(label="hide nicklist",
##				    command=self.hide_nicklist)
##		self.menu.add_cascade(label ="Options", menu=options)

		self.topiclabel = Tkinter.Label(self, text="dummy topic")

		mainframe = Tkinter.Frame(self)				
		
		self.textfield = Tkinter.Text(mainframe,
					      wrap=Tkinter.WORD)
		self.textfield.config(state=Tkinter.DISABLED)
		self.textfield.grid(row=0, column=0,
				    sticky=Tkinter.W + Tkinter.N + Tkinter.S)

		scrollbar = Tkinter.Scrollbar(mainframe,
					      command = self.textfield.yview)
		scrollbar.grid(row=0, column=1, sticky = Tkinter.N + Tkinter.S)

		self.textfield.config(yscrollcommand=scrollbar.set)

		self.nicklist = Tkinter.Listbox(mainframe)

		entryframe = Tkinter.Frame(self)
		self.entryfield = Tkinter.Entry(entryframe)
		self.entryfield.grid(sticky = Tkinter.E + Tkinter.W)

		self.bleiste = Tkinter.Frame(self)
		self.placebuttons = {}

		l = Tkinter.Label(self.bleiste,
							text="|")
		l.grid(row = 0, column = 0, sticky = Tkinter.W)

		self.topiclabel.grid(row=0, sticky = Tkinter.W)
		mainframe.grid(row=1, sticky = Tkinter.W)
		entryframe.grid(row=2, sticky = Tkinter.W)
		self.bleiste.grid(row=3, sticky = Tkinter.W)

		self.bind("<Return>", self.say)

	def append_text(self, text, encoding="iso-8859-1"):
		self.textfield["state"] = Tkinter.NORMAL
		self.textfield.insert(Tkinter.END,
				      text.decode(encoding) + '\n')
		self.textfield["state"] = Tkinter.DISABLED
		self.textfield.yview(Tkinter.END)

	def received(self, source, mc, mmp, psyc):	
		## evil
		try:
			context = mmp._query("_context").lower()
##			print context
			if mc.startswith("_notice_place_enter"):
				## if _source == ME eigentlich...
				if not self.placebuttons.has_key(context):
					self.add_room(context)
				if not self.buffers.has_key(context):
					self.buffers[context] = ""
				self.buffers[context] += parsetext(mmp, psyc) + '\n'
				if self.model.get_context() == context:
					self.append_text(parsetext(mmp, psyc))
			elif mc.startswith("_notice_place_leave"):
				self.buffers[context] += parsetext(mmp, psyc) + '\n'
				if self.model.get_context() == context:
					self.append_text(parsetext(mmp, psyc))
			elif mc == '_message_public':
				text = psyc._query("_nick")
				if psyc._query("_action") != "":
					text += " " + psyc._query("_action")
				text += ": " + parsetext(mmp, psyc) 				
				if self.model.get_context() == context:
					self.append_text(text)
				self.buffers[context] += text	+ '\n'				
			elif mc == "_status_place_topic":
				self.topics[mmp.get_source().lower()] = parsetext(mmp, psyc)
		## evil
		except KeyError:
			print "KeyError:", context
			
	def get_input(self, encoding="iso-8859-1"):
		text = self.entryfield.get().encode(encoding)
		self.entryfield.delete(0, Tkinter.END)
		return text
	
	def say(self, event):
		text = self.get_input()
		if text and text[0] == '/':
			# we have a command
			# if we know the command, we set the appropiate mc
			# else we do _request_execute
			if text.startswith("/join") and text.__len__() > 16:
				# 16 == len(/join psyc://h/@r)
				self.model.set_mc("_request_enter")
				self.model.set_target(text.split(" ")[1])
				self.model.send()
			elif text.startswith("/part"):
				# wie waers mit /part_logout, part_home, part_type, ...
				self.model.set_mc("_request_leave")
				self.model.set_target(self.model.get_context())
				self.model.send()

			elif text.startswith("/quit"):
				self.model.set_mc("_request_execute")
				self.model.set_target(self.model.center.ME())
				self.model.set_text("/quit")
				self.model.send()
			elif text.startswith("/connect"):
				foo = len(text.split(" "))
				if foo == 2:
					self.model.center.connect(text.split(" ")[1])
				elif foo == 3:
					self.model.center.connect(text.split(" ")[1], text.split(" ")[2])
			else:
				self.model.set_target(self.model.center.ME())
				self.model.set_mc("_request_execute")
				self.model.set_text(text)
				self.model.send()
		elif text and text[0] == "#":
			self.model.set_target(self.model.center.ME())
			self.model.set_mc("_request_execute")
			self.model.set_text("/" + text[1:])
			self.model.send()
		elif text and text[0] == "!":
			self.model.set_target(self.model.get_context())
			self.model.set_mc("_request_execute")
			self.model.set_text(text)
			self.model.send()
		elif text:
##			print "msg to", self.model.get_context()
			self.model.set_target(self.model.get_context())
			self.model.set_mc("_message_public")
			self.model.set_text(text)
			self.model.send()

	def get_topic(self, context = None): 
		if not context: context = self.model.get_context()
		if self.topics.has_key(context):
			return self.topics[context]
		else: return ""
		
	def change_room(self, room):
		# gucken ob wir nicklist hatten, u.u. loeschen

		# dieses ding sollte eigentlich ne eigene Klasse haben...
		a = self.model.get_context()
		if a and self.placebuttons.has_key(a):
			self.placebuttons[a]["relief"] = Tkinter.RAISED
		self.placebuttons[room]["relief"] = Tkinter.SUNKEN
		self.model.set_context(room)
		self.title("on " + room)		
		short = room[room.rfind("@"):] # kurzform fuer raum... nicht ideal?		
		self.topiclabel["text"] = short + ":" + self.get_topic()
		
		self.textfield.config(state=Tkinter.NORMAL)
		self.textfield.delete(1.0, Tkinter.END)
		self.textfield.insert(Tkinter.END, self.buffers[room])
		self.textfield.config(state=Tkinter.DISABLED)
		self.textfield.yview(Tkinter.END)

	def add_room(self, room):
		short = room[room.rfind("@"):]
		button = Tkinter.Button(self.bleiste, text=short,
			       command=lambda: self.change_room(room))
		self.placebuttons[room] = button
		button.grid(row=0, column = len(self.placebuttons) - 1,
			    sticky = Tkinter.W)

	def delete_room(self, roomname):
		# delete the button?
		pass

##	def hide_nicklist(self):
##		self.nicklist.grid_forget()

##	def show_nicklist(self):
##		self.nicklist.grid(row=0, column=2,
##				   sticky = Tkinter.E + Tkinter.N + Tkinter.S)



from pypsyc.MMP.MMPState import MMPState
from pypsyc.PSYC.PSYCState import PSYCState
from pypsyc.MMP import _isModifier
class MainWindow(Tkinter.Tk):
	def __init__(self, center = None):
		Tkinter.Tk.__init__(self)
		self.center = center

		self.title("pyPSYCgui - simple psyc client - see http://www.psyc.eu")
		
		self.menu = Tkinter.Menu(self)
		self.config(menu=self.menu)
		
		filemenu = Tkinter.Menu(self.menu)
		filemenu.add_command(label="Quit", command=self.quit)
		self.menu.add_cascade(label ="File", menu=filemenu)

		connectionmenu = Tkinter.Menu(self.menu)
		connectionmenu.add_command(label="connect", command=self.connect)
		self.menu.add_cascade(label="Connections", menu=connectionmenu)
		frame = Tkinter.Frame(self)		
		self.displayField = Tkinter.Text(frame, height=20, width=60, state=Tkinter.DISABLED)
		self.displayField.grid(row=0, column=0)
		scrollbar = Tkinter.Scrollbar
		scrollbar = Tkinter.Scrollbar(frame,
					      command = self.displayField.yview)
		scrollbar.grid(row=0, column=1, sticky = Tkinter.N + Tkinter.S)
		self.displayField.config(yscrollcommand=scrollbar.set)
		frame.pack()
		# funzt eh net
##		self.scrollbar = Tkinter.Scrollbar(self)
##		self.scrollbar.pack(side=Tkinter.RIGHT, fill=Tkinter.Y)
##		self.scrollbar.config(command=self.displayField.yview)
		self.inputField = Tkinter.Text(self, height=5, width=60)
		self.inputField.pack()
		Tkinter.Button(self, text="send", command=self.input).pack(
			side=Tkinter.LEFT)		

	def connect(self, host = ''):
		self.center.connect(host)
		
	def write(self, string):
		self.displayField.config(state=Tkinter.NORMAL)
		self.displayField.insert(Tkinter.END, string)
		self.displayField.config(state = Tkinter.DISABLED)

	def input(self):
##		print "TkinterGui::MainWindow::input"
		cmd = self.inputField.get(1.0, Tkinter.END)
		self.inputField.delete(1.0, Tkinter.END)
		state = 'mmp'
		mmp = MMPState()
		psyc = PSYCState()
		for line in cmd.split('\n'):
			if line == ".":
				#end of packet
				break
			if line == "" or (not _isModifier(line)
					  and state == 'mmp'):
				state = 'psyc'
				
			if state == 'mmp':				
				mmp.set_state(line)
				continue
			if state == 'psyc':
				if _isModifier(line):
					psyc.set_state(line)
				elif line.__len__() and line[0] == '_':
					psyc.set_mc(line)
				else:
					psyc.append_text(line)

		self.center.send(mmp, psyc)


class Application(AbstractGui.MainGui):
	def __init__(self, argv, center):
		AbstractGui.MainGui.__init__(self, argv)
		
		self.mainWindow = MainWindow(center)
		
		## nah... das is eigentlich auch evil ;)
		sys.stdout = self.mainWindow
		
	def socket_check(self):
		asyncore.poll(timeout=0.0)
		# das hier is auch noch doof...
		self.mainWindow.after(100, self.socket_check)
	def run(self):
		self.socket_check()
		Tkinter.mainloop()


