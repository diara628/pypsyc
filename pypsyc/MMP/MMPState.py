from pypsyc.MMP import Glyphs

SEPARATOR = '\t'

class MMPState:
	"""state object for MMP"""
	ModifierFunctions = None
	def __init__(self):
		self.thisState = {} # all states in current packet
		self.persistent = {} # persistent per connection
		self.packetstate = {} # per-packet stuff set with ':'
		self.update = {} # persistent stuff not sent yet, send it,
		# then update persistent stuff with this and reset

		self.lastvar = None

		# why has this to be initalized here?
		if not MMPState.ModifierFunctions:
			MMPState.ModifierFunctions = {
			      '=' : MMPState._assign,
			      '+' : MMPState._augment,
			      '-' : MMPState._diminish,
			      ':' : MMPState._set,
			      '?' : MMPState._query
			}

	def _assign(self, varname, value):
		# persistent within tcp connection
		self.thisState[varname] = value
		self.update[varname] = value
		return 0
	
	def _augment(self, varname, value):		
		# das hier is noch falsch, eh?
		#self.update[varname] += value
		print "we should augment a variable"
		return None 

	def _diminish(self, varname, value):
		# maybe using string.replace?
		print "we should diminish a variable"
		return None

	def _set(self, varname, value):
		# temporary within this packet
		# reset current with every new packet
		self.thisState[varname] = value
		self.packetstate[varname] = value
		return None

	def _query(self, varname, value = ''):
		if self.packetstate.has_key(varname):
			return self.packetstate[varname]
		elif self.update.has_key(varname):
			return self.update[varname]
		elif self.persistent.has_key(varname):
			return self.persistent[varname]
		else:
##			print self.packetstate
##			print self.update
##			print self.persistent
			return None

	def set_variable(self, modifier, varname, value):
		"""see http://www.psyc.eu/modifiers.html"""
		# name of this will change		
		if MMPState.ModifierFunctions.has_key(modifier):
			func = MMPState.ModifierFunctions[modifier]
			return apply(func, [self, varname, value])
		else:
			# unknown glyphs should be silently ignored
			return None

	def set_state(self, state):
		"""expects a string with one MMP header line"""
		if state.find(SEPARATOR) == -1:
			# print "strange MMP line encountered:", state
			self.set_variable(state[0], state[1:], "")
			return

		glyph, (varname, value) = state[0], state[1:].split(SEPARATOR)
		
		# watch out, this is unstable and not compilant with
		# lynxos new way of multiline-vars
#		if varname == '':
#			varname = self.lastvarname
#		else:
#			self.lastvarname = varname
			
		self.set_variable(glyph, varname, value)

	def get_state(self):
		temp = {}
		temp.update(self.persistent)
		temp.update(self.update)
		temp.update(self.packetstate)
		return temp

	def reset_state(self):
		self.thisState.clear()
		self.packetstate.clear()
		self.persistent.update(self.update)
		self.update.clear()
		self.lastvar = None

	def plain(self):
		packetheader = ""
		# only send updates someday...
		for (varname, value) in self.packetstate.items():
			packetheader += ":" + varname + SEPARATOR + value + "\n"
		# fippo, i don't understand this mess, but if i don't activate
		# the following lines, and change "=" into ":", then it just
		# doesn't work at all!
		for (varname, value) in self.update.items():
			packetheader += ":" + varname + SEPARATOR + value + "\n"
		# modified by lynX 2007

		#print packetheader
		self.reset_state()
		return packetheader
	
	def get_source(self): return self._query("_source")
	def get_target(self): return self._query("_target")
	def get_context(self): return self._query("_context")
