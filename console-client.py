#!/usr/bin/env python

#
# broken - fix this some 
#
import asyncore
import ConfigParser
import os
import sys
# here we start importing our own modules
from pypsyc.PSYC.PSYCMessagecenter import PSYCMessagecenter
from pypsyc.PSYC import parsetext
# import packages
from pypsyc.PSYC.PSYCRoom import Authentication as AuthenticationPackage
#import Listener

debug=0

class stdin_channel (asyncore.file_dispatcher):
    def __init__(self):
        asyncore.file_dispatcher.__init__(self, 0)
        self.buffer = ""
    def handle_read(self):
        data = self.recv(512)
        self.buffer += data
        lines = self.buffer.split("\n")
        for line in lines[:-1]:
            self.lineReceived(line)
        self.buffer = lines[-1]
    def handle_close(self):
        try:
            self.close()
        except:
            pass
    def lineReceived(self, line):
        print "line:", line # overridden
    def writable(self):
        return 0
    def log(self, *ignore):
        pass

from pypsyc.PSYC.PSYCRoom import PSYCPackage
class stdin_client(stdin_channel, PSYCPackage):
    def __init__(self):
        stdin_channel.__init__(self)
        PSYCPackage.__init__(self)
        self.methods = ["devel"]
        self.packagename = "pyPSYC console client"
    def received(self, source, mc, mmp, psyc):
	if debug:
	    #print self.packagename, "handling", mc, "from", source
	    print ""
	    print "mc:", mc
	    for (key, val) in mmp.thisState.items():
		print "MMP:", key, "=>", val
	    for (key, val) in psyc.thisState.items():
		print "PSYC:", key, "=>", val
	print parsetext(mmp, psyc)
	if mc == "_echo_logoff" or mc == "_status_unlinked":
	    print "Bye bye."
	    # eh? shouldn't this clean up and exit?  --lynX
	    sys.exit()
		
    def set_mc(self, mc): self.psyc.set_mc(mc)
    def set_target(self, target): self.mmp._assign("_target", target)
    
    def set_text(self, text):
        self.psyc.reset_text()
        self.psyc.append_text(text)
		
    def send(self):
        self.center.send(self.mmp, self.psyc)
	# this shouldn't need to be done here
        self.mmp.reset_state()
        self.psyc.reset_state()
	# after each send the temporary vars must be reset
	# to the permanent var state automatically. -lynX
    def lineReceived(self, line):
        self.mmp._set("_source_identification", self.center.ME())
        self.set_target(self.center.ME())
        self.set_mc("_request_input")
        self.set_text(line)
        self.send()


config = ConfigParser.ConfigParser()
config.read(os.getenv("HOME") + "/.pypsyc/config")

console = stdin_client()

center = PSYCMessagecenter(config)

center.register(AuthenticationPackage(config))
center.register(console)

center.connect()

asyncore.loop()

