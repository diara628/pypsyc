# -*- coding: latin-1 -*-

def print_psyc(vars, mc, data, caller = ''):
    print '------ ' + str(caller)
    print '-- mc:'
    print mc
    print '-- vars:'
    print str(vars.items())
    print '-- data:'
    print str([data])
    print '------'


class Context:
    class __impl:
        #from extras import Config
        #def __init__(self):
        #	self.config = Config()
        #	self.hust = 'hallo garrit'
        hust = 'hallo garrit'
        def spam(self):
            return id(self)
    __instance = __impl()
    
    def __getattr__(self, attr):
        return getattr(self.__instance, attr)
    
    def __setattr__(self, attr, value):
        return setattr(self.__instance, attr, value)


class DevNull:
    def __init__(self):
        pass
    def write(self, text):
        pass

class Config(dict):
    def __init__(self, file = None):
        self[u'uni'] = u'psyc://ve.symlynx.com/~betatim'
        self[u'password'] = u'tim0914'
        self[u'action'] = u'brabbel'
        self[u'bgcolour'] = (255, 236, 191)
        self[u'fontcolour'] = (34, 63, 92)
        self[u'fontsize'] = 8
        self[u'prompt'] = u'* '

    
class Display(dict):
    """ this dict like object organises multiple displays """
    def __init__(self, display = None):
        if display:
            self['default'] = display
    
    def append1(self, text):
        self['default'].append1(text)
    
    t = """def __setitem__(key = None, item = None):
        if key and item:
            dict.__setitem__(key, item)
        elif item:
            if self['default']:
                print 'Overwrite default display explicitly'
            else:
                self['default'] = item"""

