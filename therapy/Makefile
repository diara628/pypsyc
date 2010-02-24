fix: pypsyc therapy
	expand therapy >therapy-big-big-big
	-mv -f therapy /tmp
	-mv -f therapy-big-big-big therapy
	python -tt therapy

# paranoid check of syntax
jack: pypsyc therapy
	python -tt therapy

pypsyc:
	@echo I will presume you have also checked out pypsyc.
	ln -s ../pypsyc/pypsyc .

it: jack

