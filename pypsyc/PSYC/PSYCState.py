from pypsyc.MMP.MMPState import MMPState

class PSYCState(MMPState):
	def __init__(self):
		self.mc = ''
		self.text = ''
		MMPState.__init__(self)
	def set_mc(self, mc):		
		self.mc = mc
	def get_mc(self):
		return self.mc
	def reset_mc(self):
		self.mc = ''
	def append_text(self, text):
		if self.text != '':
			self.text += '\n'
		self.text += text
	def get_text(self):
		return self.text
	def reset_text(self):
		self.text = ''
	def reset_state(self):
		self.mc = ''
		self.text = ''
		MMPState.reset_state(self)
	def get_source(self): raise "Meep. No source in PSYC Layer"
	def get_target(self): raise "Meep. No target in PSYC Layer"
	def get_context(self): raise "Meep. No context in PSYC Layer"
	def get_length(self): raise "Meep. No length in PSYC Layer"
