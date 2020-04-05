import time
import urllib.request
import os.path
import html

from htmldom import htmldom
from discord_webhook import DiscordWebhook
from datetime import datetime
from humanfriendly import format_timespan

import configparser
config = configparser.ConfigParser()
config.read('config.cfg')

class Check():
    """server_name: the name of our server
    discord_hook: the API uri to use for discord notification"""
    def __init__(self, server_name, discord_hook=""):
        self.index_url   = config['disboard']['url']
        self.file_name   = config['disboard']['status_file']
        self.server_name = server_name
        self.discord_hook= discord_hook
        self.ts          = time.time()
        self.server      = []
        self.index_first = ""
        self.index_list  = []
        self.index_time  = []
        self.index_online= []
        self.my_last_bump= ""
        self.read_file()

    def check(self):
        self.update(self.load())
        # self.update("fake")

    def load(self):
        req = urllib.request.Request(self.index_url)
        req.add_header('User-Agent', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.123 Safari/537.36')
        page = str(urllib.request.urlopen(req).read())
        dom = htmldom.HtmlDom().createDom(page)

        for entry in dom.find("div.server-name"):
            self.index_list.append(html.unescape(str(entry.text()).replace('\\n', '').rstrip()))

        for entry in dom.find("div.server-bumped-at"):
            self.index_time.append(str(entry.text()).replace('\\n', '').rstrip())

        for entry in dom.find("div.server-online"):
            self.index_time.append(str(entry.text()).replace('\\n', '').rstrip())

        for i in range(len(self.index_list)):
            if self.index_list[i] == self.server_name:
                self.my_last_bump = self.index_time[i]


#        self.index_first = str(dom.find("div.server-name")[0].text()).replace('\\n', '').rstrip()
        return self.index_list[0]


    def update(self, server):
        """update tracking with new infos"""
        # no change, update counter
        if server == self.server[0]:
            self.server[2] = str(int(self.server[2]) + 1)
        # new server is now #1
        else:
            self.server = [ server, self.ts, 1 ]
        # print("server: {0} ts: {1} count {2}".format( self.server[0], self.server[1], self.server[2] ))
        self.write_file( self.server[0], self.server[1], self.server[2] )

    def read_file(self):
        """get info from file"""
        # make sure file exist
        if not os.path.isfile(self.file_name): 
            self.write_file(self.server_name, self.ts, 0)
        self.server = open(self.file_name, "r").read().split("||")
        
    def write_file(self, server, ttime, count):
        """output new info to file"""
        f = open(self.file_name, "w")
        f.write( "{0}||{1}||{2}".format(server, ttime, count) )
        f.close()

    def notify(self, msg):
        """send notification to discord"""
        DiscordWebhook(url=self.discord_hook, content=msg).execute()

    def delta(self):
        """Get the time difference between current check and last check"""
        return format_timespan((datetime.fromtimestamp(self.ts) - datetime.fromtimestamp(float(self.server[1]))).total_seconds())

    def count(self):
        """Get the number of time the same server was checked"""
        return int(self.server[2])

    def is_us(self):
        """if the index 1st position is our server return true"""
        if self.server[0] == self.server_name:
            return True
        return False

    def is_ok_second(self):
        """if the index 1st position is not us but we don't care about that"""
        if self.server[0] == "thallia's tree" and self.index_list[1] == self.server_name:
            return True
        return False


    def first(self):
        """return the first position server name"""
        return self.server[0]
