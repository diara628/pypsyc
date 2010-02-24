import asynchat, asyncore, socket
from pypsyc.MMP import Glyphs, _isModifier
from pypsyc.MMP.MMPState import MMPState

debug=0

class MMPProtocol(asynchat.async_chat):
	"""modular message protocol
	   see http://www.psyc.eu/mmp.html for details."""
	def __init__(self, callback, connection):
		asynchat.async_chat.__init__(self, connection)
		self.set_terminator('\n')
		self.buffer = ''
		self.mmp = MMPState()
		self.state = 'mmp'
		self.data = []

		self.callback = callback

	def handle_connect(self):
		# dead code neuerdings, eh?
		print "connected... but this is dead code"

	def handle_close(self):
		s = MMPState()
		if self.addr[1] != 4404:
			s._set('_source', "psyc://%s:%d/"%self.addr)
		else:
			s._set('_source', "psyc://%s/"%self.addr[0])
		self.packetReceived(s, "_notice_circuit_broken\nYour TCP connection to [_source] was broken by the bull from the china shop\n.\n")
		self.close()
		
	def collect_incoming_data(self, data):
		self.buffer += data

	def found_terminator(self):
		# hierfuer siehe asyncchat.py... das setzt
		# terminator auf 0 zurueck wenns nen int als terminator
		# hat und den findet (line 111)
		if self.get_terminator() == 0:
			self.set_terminator("\n")
		line = self.buffer
		self.buffer = ''		
		self.lineReceived(line)

	def lineReceived(self, line):
		# kind of state machine
		line = line.strip()
		if line == ".":
##			print "<<EOP>>"
			self.packetReceived(self.mmp, self.data)
			# reset state, clear temporary variables, etc
			self.mmp.reset_state()
			self.data = []
			self.state = 'mmp'
			return
		
		if (line == '' or not _isModifier(line)) and self.state == 'mmp':
			# if we have _length for data then
			# binary support
			if self.mmp._query('_length'):
				self.set_terminator(self.mmp._query('_length'))
			self.state = "data"
##		print "<<" + self.state + ">> " + line 	## comment out
		if self.state == 'mmp':
		# maybe else with the above could also work...		  
			self.mmp.set_state(line)			
			return
		elif line != '':
			self.data += [line]
			
	def packetReceived(self, mmp, data):
##		print "MMPProtocol::packetReceived"
##	         print "=>MMP :", mmp.get_state()
##		print "=>data:", data
		self.callback.packetReceived(mmp, data)

	def sendPacket(self, mmp, data):
##		print "calling MMPProtocol::sendPacket()"
		packet = mmp.plain()
		packet += '\n'+ data +'\n.\n'
		if debug:
		    print ">>send>>\n", packet, "<<send<<\n"
		self.push(packet)
