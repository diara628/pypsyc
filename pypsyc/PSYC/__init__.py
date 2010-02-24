def parsetext(mmp, psyc):
	"""string with variables of the form '[_varname]' to be substituted
	   by the value dictVariables['_varname']"""
	pstring = psyc.get_text()
	for (varname, value) in mmp.get_state().items():
		pstring = pstring.replace('[' + varname + ']', value)
	for (varname, value) in psyc.get_state().items():
		pstring = pstring.replace('[' + varname + ']', value)
	return pstring

def get_host(uni):
	import re
	
	m = re.match("^psyc:\/\/(.+)?\/~(.+)?\/?$", uni)
	if m: return m.group(1)

	m = re.match("^psyc:\/\/([^\/@]+)\@(.+?)\/?$", uni)
	if m: return m.group(2)
	
  	m =  re.match("^psyc:\/\/(.+)?\/\@(.+)?\/?$", uni)
	if m: return m.group(1)

	m = re.match("^psyc:\/\/(.+)$", uni)
	if m: return m.group(1)

def get_place(uni):
	import re
	m =  re.match("^psyc:\/\/(.+)?\/\@(.+)?\/?$", uni)
	if m: return m.group(2)

def get_user(uni):
	import re
	m = re.match("^psyc:\/\/(.+)?\/~(.+)?\/?$", uni)
	if m: return m.group(2)

	m = re.match("^psyc:\/\/([^\/@]+)\@(.+?)\/?$", uni)
	if m: return m.group(1)

