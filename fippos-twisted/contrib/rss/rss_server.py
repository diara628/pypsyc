# usage: twistd -noy rss_server.py
from twisted.application import service, internet
from twisted.internet import reactor
from pypsyc.center import ServerCenter
from pypsyc.net import PSYCServerFactory
from pypsyc.objects.server import Place

from pypsyc import parseUNL

try:
    from rss import FeederFactory
except ImportError:
    print 'error while importing rss.py'
    print 'make sure you have rss.py from ',
    print 'from http://aspn.activestate.com/ASPN/Cookbook/Python/Recipe/277099'
    print 'and feedparser.py from ',
    print 'http://diveintomark.org/projects/feed_parser/'
    

class PlaceFeeder(FeederFactory):
    def getFeeds(self):
        return []


class Feedplace(Place):
    channel = None
    silent = True
    def __init__(self, netname, center, feed):
        Place.__init__(self, netname, center)
        self.feed = feed
        self.error = 0 # number of times that we didnt succeed
        self.fetched = 0 # number of times we fetched sucessfully
        self.fetched_items = 0 # the average number of new items per fetch

        self.fetch_interval = 15 * 60 # initial feed interval

        self.feeder = PlaceFeeder(False)
        self.news = []
        reactor.callLater(5, self.fetchFeed)
    def fetchFeed(self):
        d = self.feeder.start([(self.feed, '')])
        d.addCallback(self.gotFeed)
        d.addErrback(self.gotError)
    def gotError(self, error):
        self.error += 1
        # TODO: react on feeds that are temp/perm unreachable
        reactor.callLater(self.fetch_interval, self.fetchFeed)
        print 'looks as if feed %s is unreachable'%self.feed
        print error
    def gotFeed(self, data):
        self.fetched += 1
        new = []
        items = {}
        if self.channel is None:
            self.channel = data['channel']
            self.castmsg({ '_nick' : self.netname,
                         '_topic' : self.showTopic()}, 
                         '_status_place_topic', 
                         'Topic by [_nick]: [_topic]') 
        for item in data['items']:
            # diff by url
            href = item['link']
            new.append(href)
            items[href] = item
        
        diff = filter(lambda x: x not in self.news, new)
        for href in diff:
            item = items[href]
            v = {'_news_headline' : item['title_detail']['value'],
                '_page_news' :  href,
                '_channel_title' : data['channel']['title'] }
            self.castmsg(v, '_notice_news_headline_rss', 
                         '([_channel_title]) [_news_headline]\n[_page_news]')

        self.news = new

        # feeds whose average number of new items is < x 
        # can be polled with less frequency
        self.fetched_items += len(diff)
        avg = float(self.fetched_items) / self.fetched 
        print 'avg no of new items per fetch for %s is %f'%(self.feed, avg)
        if avg < 1.5: # x
            # lower frequency
            self.fetch_interval *= avg
        elif avg > 4.5 and self.fetched > 10: # y
            # increase frequenzy
            self.fetch_interval /= 2
        print 'callLater in %d'%(self.fetch_interval)
        reactor.callLater(self.fetch_interval, self.fetchFeed)
    def showMembers(self):
        return []
    def showTopic(self):
        if self.channel is not None:
            return 'feed \'%s\' available from %s'%(self.channel['title'], 
                                                    self.feed)
        else:
            return 'stand by while fetching feed %s'%self.feed
    def msg_message_public(self, vars, mc, data):
        pass # they're not for talking


class MyServerCenter(ServerCenter):
    feeds = {}
    def create_user(self, netname):
	return False
    def create_place(self, netname):
        u = parseUNL(netname)
        res = u['resource'][1:]
        if self.feeds.has_key(res):
            return Feedplace(netname, center, self.feeds[res])
        return False
    def create_context(self, netname):
        return False
    def setFeeds(self, feeds):
        self.feeds = feeds
    def getFeeds(self):
        return self.feeds


root = 'psyc://ente'
application = service.Application('psyc news distributor')

center = MyServerCenter(root)
factory = PSYCServerFactory(center, None, root)
psycServer = internet.TCPServer(4404, factory)

center.setFeeds({ 'heise' : 'http://www.heise.de/newsticker/heise.rdf' })

myService = service.IServiceCollection(application)
psycServer.setServiceParent(myService)

