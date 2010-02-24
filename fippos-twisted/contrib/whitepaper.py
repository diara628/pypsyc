"""p2p manager and client as described in the old PSYC whitepaper at
http://psyc.pages.de/whitepaper/
probably broken currently"""
from pypsyc.center import ServerCenter, ClientCenter
from pypsyc.objects.PSYCObject import PSYCClient
from pypsyc.objects.Advanced import AdvancedManager, AdvancedPlace
import sys
import asyncore

location = 'psyc://adamantine.aquarium'

type = sys.argv[1]
if type == 'manager':
        center = ServerCenter([location + ':4405/', location + ':4406',
                                       location + ':4407', location + ':4408'])
        center2 = ServerCenter([location])
        AdvancedManager(location + '/@advanced', center2)
if type == 'client':
        center = ClientCenter()
        me = PSYCClient(location + '/~fippo', center)
        me.online()
        AdvancedPlace(location + "/@advanced", center)
        me.sendmsg({'_target' : location + '/@advanced',
		    '_source' : location + '/~fippo'},
		   '_request_enter', '')

while center:
	asyncore.poll(timeout=0.5)
