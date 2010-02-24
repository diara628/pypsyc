# toplevel makefile
clean : 
	find . -name "*~" | xargs rm
	find . -name "*.pyc" | xargs rm
