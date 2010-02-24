from pypsyc.PSYC.PSYCProtocol import PSYCProtocol
from pypsyc.PSYC import get_host, get_place
from socket import gethostbyname


import asyncore, socket
# socket listener
class PSYCSocketListener(asyncore.dispatcher):
	def __init__(self, callback, localip = '', localport = 4404, protocol = socket.SOCK_STREAM):
		asyncore.dispatcher.__init__(self)
		self.create_socket(socket.AF_INET, protocol)
		self.set_reuse_addr()		
		self.bind((localip, localport))
		
		self.callback = callback

		self.listen(5)
	def handle_accept(self):
		conn, addr = self.accept()
		PSYCProtocol(self.callback, conn)


# das hier ist ne Abstraction die Clients/ne Verbindung connectet
class PSYCConnector(asyncore.dispatcher):
    def __init__(self, callback, host, port):
        asyncore.dispatcher.__init__(self)
        self.create_socket(socket.AF_INET, socket.SOCK_STREAM)
        self.set_reuse_addr()
        self.host = host
        self.callback = callback
        
        self.connect((host, port))
    def handle_read(self):
        pass
    def handle_write(self):
        pass
    def handle_connect(self):
        self.send(".\n")
	# The protocol begins with a dot on a line by itself.
	p = PSYCProtocol(self.callback, self.socket)
        self.callback.connected(p, self.host)


class PSYCMessagecenter:
    def __init__(self, config):
        self.config = config
        self.clients = {}
        self.handlers = {}

    def ME(self):
        return self.config.get("main", "uni")

    def DEFAULT_HOST(self):
        return get_host(self.ME())
    
    def connect(self, uni = '', port = 4404):
        # eigentlich sollte port via uni
        if uni == '':
            uni = self.config.get("main", "uni")
        print uni
        host = gethostbyname(get_host(uni))
        # hier muessen die auch noch richtig rein
        if not self.clients.has_key(host):
            # not sure if this works...
            # das hier muss umgestrickt werden
            # irgendwie per callback setzen
            PSYCConnector(self, host, port)

    def connected(self, client, host):
        self.clients[host] = client 

    def send(self, mmp, psyc):
        # route to the right host
        target = mmp.get_target()
        if not target.startswith("psyc://") and (
            target.startswith("@") or target.startswith("~")):
            target = "psyc://" + self.DEFAULT_HOST() + "/" + target
            mmp._set("_target", target)
#        print ">>>", target
#        print "mmp :", mmp.get_state()
#        print "psyc:", psyc.get_state()
#        print "mc  :", psyc.get_mc()
#        print "text:", psyc.get_text()
#        #print "get_host(" + unl + "):", get_host(unl)
#        print "---"
        
        host = gethostbyname(get_host(target))
        if not self.clients.has_key(host):
##            print "Error: we are not yet connected to ", host
            self.connect(host)
            # put the current packet in a queue,
            # connect and auth before sending
        else:
            # wait... we have to register before sending?
            # print "sending..."
            # print "client is:", self.clients[hostpart]
            self.clients[host].sendPacket(mmp, psyc)
        
    def quit(self):
        # "unlink" waer der bessere name?
        print "unlinking world..."
        for host in self.connections.keys():
            # auch nicht grade grateful... request unlink
            # waer schoener
            del self.clients[host]
            
    def register(self, psycPackage, methods = []):
        """see bitkoenigs psycpackage interface... that's the way to
           do it"""
        if methods == []:
            methods = psycPackage.getMethods()
        for method in methods:
            # jetzt auch support fuer mehrere packages pro mc
            if not self.handlers.has_key(method):
                self.handlers[method] = [ psycPackage ]
            else:
                self.handlers[method] += [ psycPackage ]
        psycPackage.registerCenter(self)
        
    def castmsg(self, mmp, psyc):
        # ob das noch/ueberhaupt noetig ist...
        """for internal packets"""
        self.handle(mmp, psyc)

    def handle(self, mmp, psyc):
        context = mmp._query("_context")
        if context:
            if not context.startswith("psyc://") and context.startswith("@"):
                context = "psyc://" + self.DEFAULT_HOST()+"/"+context
                mmp._set("_context", context)

        #if self.handlers.has_key(psyc.get_mc()):
        #    for package in self.handlers[psyc.get_mc()]:
        #        package.received(mmp.get_source(),
        #             psyc.get_mc(),
        #             mmp, psyc)
       
        method = psyc.get_mc()
        source = mmp.get_source()
        found = 0 
        for handler in self.handlers.keys():
            if handler.endswith("*"):
                tmp = handler.replace("*", "")
                if method.startswith(tmp):
                    found = 1
                    for package in self.handlers[handler]:
                        package.received(source, method, mmp, psyc)
            else:
                if handler == method:
                    found = 1
                    for package in self.handlers[method]:
                        package.received(source, method, mmp, psyc)
        
        if not found:        
            if self.handlers.has_key("devel"):      #(an) was elif
                for package in self.handlers["devel"]:
                    package.received(source, method, mmp, psyc)



class PSYCServercenter:
	def __init__(self):
		self.clients = {}
	
	def handle(self, mmp, psyc):
		# das problem ist, dass wir die Klasse von der 
		# das kommt auch kennen muessen 
		print mmp.get_target()
  
