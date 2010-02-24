class PSYCReceiver:
    def msg(self, vars, mc, data):
        'called when a message is received'
        # method inheritance
        if mc.count('_') > 10:
            # considered abusive
            return

        l = len(mc)
        while l > 0:
            method = getattr(self, 'msg%s'%(mc[:l]), None)
            if method is not None:
		# could this method return the next methodname
		# to be called? freaky!
		# actually, this a much more flexible fallthrough 
		# than switch/case provides.
		# yet it is more expensive to evaluate
                method(vars, mc, data)
                break
            l = mc.rfind('_', 0, l)
        else:
            self.msgUnknownMethod(vars, mc, data)
    def msgUnknownMethod(self, vars, mc, data):
        print 'unknown %s'%mc


class PSYCObject(PSYCReceiver):
    """generic PSYC object"""
    def __init__(self, netname, center):
        self.center = center
        self.netname = netname.lower()
        self.center.register_object(netname, self)
    def url(self):
        return self.netname
    def str(self):
        return self.netname
    def sendmsg(self, vars, mc, data):
        'called to send a message'
        l = len(mc)
        while l > 0:
            method = getattr(self, 'sendmsg%s'%(mc[:l]), None)
            if method is not None:
                method(vars, mc, data)
                break
            l = mc.rfind('_', 0, l)
        else:
            self.center.sendmsg(vars, mc, data)
    def castmsg(self, vars, mc, data):
        'called to send a message to a group'
