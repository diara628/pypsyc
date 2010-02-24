from PSYCState import PSYCState

from pypsyc.MMP import _isModifier
from pypsyc.MMP.MMPProtocol import MMPProtocol

class PSYCProtocol:
	def __init__(self, callback, socket):
		self.callback = callback
		self.state = PSYCState()
		self.mmp = MMPProtocol(self, socket)

	def sendPacket(self, mmp, psyc):
##		print "PSYCProtocol::sendPacket()"
		data = ''
		full = psyc.get_state() 
		for var in full:
			data += ":" + var + '\t' + full[var] + '\n'
		data += psyc.get_mc() + '\n'		
		data += psyc.get_text()
		self.mmp.sendPacket(mmp, data)

	def packetReceived(self, mmp, data):
		self.state.reset_state()
		state = 'psyc'
		for line in data:
			if _isModifier(line) and state == 'psyc':
				self.state.set_state(line)
				
				continue
			elif line.__len__() and line[0] == '_' and state != 'text':
##				print "mc:", line
##				print "source:", mmp.get_source()
				self.state.set_mc(line)
				state = 'text'
				continue
			elif state == 'text':
				self.state.append_text(line)
			else:
				print "unknown psyc stuff:", line

##		print "PSYCProtocol::packetReceived from", mmp.get_source()
##		print "=>PSYC :", self.state.get_state()
##		print "=>mc   :", self.state.get_mc()
##		print "=>text :", self.state.get_text()
##		print "----"				
		self.callback.handle(mmp, self.state)
		
