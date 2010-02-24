from pypsyc.MMP import Glyphs

#obsolete?
class MMPPacket:
	"""encapsulates a set of MMP state variables and data within a
	   MMP packet. See http://www.psyc.eu/mmp.html"""
	# do subclassing for binary data packets and fragmented packets
	
	delimiter = '.\n' # end of packet delimiter	
	def generate(self, MMPModifiers, data):
		"""Expects a (emtpy) dictionary of MMP Modifiers and
		 a (empty) string of data. Does nothing with the data itself"""	
		packet = ""
		packet += MMPModifiers.plain()
		data = data.strip()
		
		# take a look data the first character of data. If it is no glyph
		# we may leave out the newline before data
		if data.__len__() and _isModifier(data[0]):
			packet += '\n'
		else:
			# keys may be empty (so we either have an empty packet or we
			# set default variables for communication
			pass

		
		# append data and EOP delimiter
		return packet + data + '\n' + MMPPacket.delimiter
