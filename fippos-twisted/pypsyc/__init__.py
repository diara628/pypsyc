"""common methods and constants for pyPSYC"""

# URL parsing functions modelled after psycMUVE parseURL
def parseURL(url):
    u = { 'scheme' : '',
        'user' : '',
        'pass' : '',
        'host' : '',
        'port' : '4404',
        'transport' : '',
        'string' : url,
        'body' : '',
        'userAtHost' : '',
        'hostPort' : '',
        'root' : '',
        'circuit' : '',
        'size' : ''
    }
    if url.find(':') == -1: return u
    u['scheme'], t = url.split(':', 1)
    if t[0:2] == '//': t = t[2:]
    u['body'] = t[:]
    if t.find('/') != -1:
        t, u['resource'] = t.split('/', 1)
    else:
        u['resource'] = ''
    if u.has_key('resource') and u['resource'].find('#') != -1:
        u['resource'], u['fragment'] = u['resource'].split('#', 1)
    u['userAtHost'] = t[:]
    if t.find('@') != -1:
        s, t = t.split('@', 1)
        if s.find(':') != -1:
            u['user'], u['pass'] = s.split(':', 1)
        else:
            u['user'] = s
    u['hostPort'] = t[:]
    u['root'] = u['scheme'] + '://' + u['hostPort']
    if t.find(':') != -1:
            t, s = t.split(':', 1)
            # TODO: split s in Port (numeric), Transport
            if s and s[-1] in ['c', 'd', 'm']: 
                u['transport'] = s[-1]
                u['port'] = s[:-1]  or '4404'
            else: 
                u['port'] = s or '4404'
    u['host'] = t[:]
#   print "parseurl(%s)"%url, u
    return u


def parseUNL(unl): return parseURL(unl) # alias

def UNL2Location(unl):
    # if we did not have the user@host syntax this would
    # reduce to a simple splitting in front of #
    u = parseUNL(unl)
    short = u['scheme'] + '://' + u['host']
    if u['port'] != '4404':
        short += ':' + u['port']
    if u['resource']:
        return short + '/' + u['resource']
    return short


def netLocation(unl):
    u = parseURL(unl)
    return u['root']

def parsetext(vars, mc, data, caller=None):
    pstring = data
    #print '---'
    #print type(data)
    #print '---'
    try:
        for (varname, value) in vars.items():
            if type(value) == list:
                no_list = u''
                for x in value:
                    no_list += x + ', '
                pstring = pstring.replace(u'[' + varname + u']', no_list[:-2])
            else:
                pstring = pstring.replace(u'[' + varname + u']', value)
    except:
        print 'Error in parsetext() for vars'
    return pstring

# debugging helper
def dump_packet(banner, vars, mc, data):
    print banner + ' ',
    for key in vars.keys():
        try:
            print key + '=' + vars[key] + ' ',
        except:
            pass
    print mc,
    print '[' + parsetext(vars, mc, data) + ']'

    
# constants
GLYPHS = [':', '=', '+', '-', '?', ' ', '\t' ] 
MMPVARS = ["_source", "_target", "_context"]
