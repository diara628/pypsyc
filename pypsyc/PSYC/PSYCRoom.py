from pypsyc.PSYC import parsetext

from pypsyc.MMP.MMPState import MMPState
from pypsyc.PSYC.PSYCState import PSYCState

class PSYCPackage:
    """see bitkoenig's java interface specification"""
    def __init__(self):
        self.packagename = "Abstract psycPackage interface"
        self.methods = []

        self.center = None        
        self.psyc = PSYCState()
        self.mmp = MMPState()        

    def registerCenter(self, center):
        self.center = center

    def getMethods(self):
        return self.methods

    def received(self, source, mc, mmp, psyc):
        print "<<<", source, "[", self.packagename, "]"
        print "mmp:", mmp.packetstate
        print "psyc:", psyc.packetstate
        print "mc:", mc
        print "text:", parsetext(mmp, psyc)
        print "----"
        
    def set_mc(self, mc): self.psyc.set_mc(mc)
    def set_target(self, target): self.mmp._assign("_target", target)
        
    def set_text(self, text):
        self.psyc.reset_text()
        self.psyc.append_text(text)
        
    def set_psycvar(self, var, value):
        self.psyc._assign(var, value)
        
    def send(self):
        self.center.send(self.mmp, self.psyc)
        self.mmp.reset_state()
        self.psyc.reset_state()

    def castmsg(self):
        self.center.castmsg(self.mmp, self.psyc)
        self.mmp.reset_state()
        self.psyc.reset_state()


class Devel(PSYCPackage):
    def __init__(self, view):
        PSYCPackage.__init__(self)
        self.packagename = "Debug package... dump out stuff"
        self.methods = ["devel"] # all unhandled methods
        self.view = view

    def received(self, source, mc, mmp, psyc):
        print >> self.view, "devel handler:"
        print >> self.view, "source=>", source
        print >> self.view, "target=>", mmp.get_target()
        print >> self.view, "mmp   =>", mmp.get_state()
        print >> self.view, "psyc  =>", psyc.get_state()
        print >> self.view, "mc    =>", mc
        print >> self.view, "text  =>", parsetext(mmp, psyc)
        print >> self.view, "----\n"


class Conferencing(PSYCPackage):
    # model for rooms. has to know its controller and view
    # the view is an instance of RoomGui (singleton in case of Qt GUI)
    def __init__(self, view):
        PSYCPackage.__init__(self)
        self.packagename = "package for rooms"
        self.view = view
        self.model = self
        self.view.set_model(self.model)        
        self.controller = self

        self.context = ''
        
        # ideal hier waere es wenn man auf _notice_place_enter* registern
        # koennte, oder?
        self.methods = ["_notice_place*",
                        "_notice_person_present_netburp",
                        "_notice_person_absent_netburp",
                        "_message*",
                        "_status_place*",
                        "_status_person_present_netburp",
                        "_print_status_place*"]

    def get_context(self): return self.context
    def set_context(self, context): self.context = context
    
    def received(self, source, mc, mmp, psyc):
        #if mc.startswith("_message_public"):
        #    self.view.received(source, mc, mmp, psyc)
        #elif mc == "_status_place_topic":
        #    self.view.received(source, mc, mmp, psyc)
        #elif mc.startswith("_notice_place_enter"):
        #    self.view.received(source, mc, mmp, psyc)
        #elif mc.startswith("_notice_place_leave"):
        #    self.view.received(source, mc, mmp, psyc)
        #elif mc == "_print_status_place_members":
        #    print parsetext(mmp, psyc)
        #else:
        #    PSYCPackage.received(self, source, mc, mmp, psyc)
        self.view.received(source, mc, mmp, psyc)
        PSYCPackage.received(self, source, mc, mmp, psyc)

class Friends(PSYCPackage):
    def __init__(self, view):
        PSYCPackage.__init__(self)
        self.packagename = "package for friends"
        self.view = view
        self.model = self
        self.view.set_model(self.model)    
        self.controller = self
        self.methods = ["_notice_friend_present",
                        "_notice_friend_absent",
                        "_list_friends_present", # create this!
#                        "_print_notice_friend_present", # _print family should be obsolete now
#                        "_print_notice_friend_absent", # _print family should be obsolete now
                        "_print_list_friends_present", # obsolete this!
                        "_notice_link",
                        "_notice_unlink",
                        "_status_linked"] # added by tim]

    def received(self, source, mc, mmp, psyc):
        self.view.received(source, mc, mmp, psyc)
        PSYCPackage.received(self, source, mc, mmp, psyc)


class User(PSYCPackage):
    def __init__(self, view):
        PSYCPackage.__init__(self)
        self.packagename = "package for user dialogues"
        self.view = view
        self.model = self

        self.view.set_model(self.model)
        
        self.controller = self

        self.methods = ["_internal_message_private_window_popup",
                        "_message*",
                        "_notice_query*"]


    def received(self, source, mc, mmp, psyc):
        self.view.received(source, mc, mmp, psyc)
        PSYCPackage.received(self, source, mc, mmp, psyc)

class Peer(User):
    # is das ueberhaupt sinnvoll _hier_?
    def __init__(self, view):
        User.__init__(self, view)
        self.packagename = "package for p2p dialogues"


from pypsyc.MMP.MMPState import MMPState
from pypsyc.PSYC.PSYCState import PSYCState
class Authentication(PSYCPackage):
    # das hier sollte noch das setzen von _identification regeln oder?
    def __init__(self, config):
        PSYCPackage.__init__(self)
        self.config = config
        self.methods = ["_query_password",
                        "_notice_circuit_established",
                        "_error_illegal_name",
                        "_error_illegal_password",
                        "_error_invalid_password"]

    def auth(self):
        psyc = PSYCState()
        mmp = MMPState()
        if self.center:
            # das hier ist sicher weils nur an die eigene uni geht
            mmp.set_state(":_target\t" + self.config.get("main", "uni"))
            psyc.set_state(":_password\t" + self.config.get("main",
                                   "password"))
            psyc.set_mc("_set_password")

            self.center.send(mmp, psyc)

    def register(self):
        psyc = PSYCState()
        mmp = MMPState()
        if self.center:
            mmp.set_state(":_target\t" + self.config.get("main", "uni"))
            psyc.set_mc("_request_link")
            self.center.send(mmp, psyc)

    def received(self, source, mc, mmp, psyc):
        if mc == "_query_password":    
            self.auth()
        elif mc == "_notice_circuit_established":
            self.register()
        else: PSYCPackage.received(self, source, mc, mmp, psyc)
