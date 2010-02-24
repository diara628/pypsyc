#!/usr/bin/env python
from pypsyc import parseUNL, UNL2Location, netLocation

from pypsyc.objects.PSYCObject import PSYCQueueObject, PSYCObject, PSYCUNI, PSYCPlace, PSYCClient, ClientUser, ClientPlace, AdvancedManager, AdvancedPlace

from pypsyc.net import PSYCUDPSender

from pypsyc.center import ServerCenter, ClientCenter

import asyncore

if __name__ == '__main__':
	import sys
	type = sys.argv[1]
	location = 'psyc://adamantine.aquarium'
  	center = None
	if type == "server":
		# tcp only server
		center = ServerCenter([location + ':c'])
		PSYCPlace(location + '/@place', center)
		PSYCUNI(location + '/~fippo', center)
	
	if type == "server2":
		# tcp and udp server on non-standard port
		center = ServerCenter([location + ':4405'])
		center.connect(location)
	if type == "udpserver":
		center = ServerCenter([location + ':4405d'])
		PSYCUNI(location + ':4405/~fool', center)
	if type == "udpclient": 
		# this should better be done via a Center which can parse 
		# URLs and them handle according to their transport
		# but for a quick udp sender this is okay...
		q = PSYCUDPSender(location + ':4405d')
		q.msg({'_target' : 'psyc://adamantine.aquarium:d/~fippo'}, 
		      {'_nick' : 'udpclient'}, 
		      '_message_private', 
		      'hallo udp welt')
	if type == "client":
		center = ClientCenter()
  		PSYCObject('psyc://adamantine.aquarium', center)
		# maybe add config information here?
		# and let this thing connect as well?
  		me = PSYCClient('psyc://adamantine.aquarium/~fippo', center)
		me.online()
  		# but thats the fast way to do it
		me.sendmsg({'_target' : 'psyc://adamantine.aquarium/~fippo'}, 
			   {'_password' : 'xfippox'}, 
			   '_request_link', 
			   '')
	
	
	while center:
		asyncore.poll(timeout=0.5)
