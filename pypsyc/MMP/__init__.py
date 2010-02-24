# modifier glyphs as defined in the whitepaper
Glyphs = ['=', '+', '-', ':', '?']

def _isModifier(str):
	# W A R N I N G: duplicated code
	# this is a hack... first part makes sure that name[0] is
	# valid, second part does the actual check
	return (len(str) and str[0] in Glyphs)
