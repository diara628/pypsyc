"""Client API for PSYC objects"""

class IPSYCClientObject:
    def msg(self, vars, mc, data):
        """receive a message"""
    def sendmsg(self, vars, mc, data):
        """send a message to a single person or a group manager
        use this make requests to the other side that should not be 
        distributed in an unchangend fashion"""
    def castmsg(self, vars, mc, data):
        """send a message that is destined to be delivered to a group
        Note that you should use this for all communication with the
        group, as it enables transparent distribution for both centralistic
        and peer2peer scenarios"""
