import os
import re
import random
import urllib.request
import tweepy       # https://tweepy.readthedocs.io/en/latest/index.html
import configparser
import sqlite3
from PIL import Image, ExifTags
#import ExifTags

config = configparser.ConfigParser()
config.read('config.cfg')

discord_link = "discord.gg/fPmuqzQ"
# tag_phrase = [  'Sponsor needed for our next #3dprint #3dprinting contest!(parts/fila) #3dmodeling'
#              ]


tag_phrase = ['Need #3dprinting help? Want to share your latest #3dprint? Join us:',
                'Join our #3dprinting #3dprinter community and share with us:',
                'Questions #3dprinting #3dprinter ? Join us:',
                "Share your #3dprinting #3dprinter journey with us:",
                "Need some #help or #support with your #3dprinter ? Join us:",
                "#3dprinting is your hobby/drive you crazy? Join our discord: ",
                "Become part of our great #Discord #3DPrinting #3DModeling community: ",
                "Interested in #3Dprinting #3DPrinter ? join us on our discord server :"
            ]
tag_head = [ '#3dprint post by {0} on our discord:\nJoin us: {1}\n\n',
             'Shared by {0} #3dprint on our discord:\nJoin us: {1}\n\n',
             'Posted by {0} #3dprint on our discord:\nJoin us: {1}\n\n' ]

class TweetDB():
    def __init__(self):
        if not os.path.exists(config['twitter']['localdb']):
            print("db doesn't exist -- creating")
            self.init_db(config['twitter']['localdb'])
        self.conn = sqlite3.connect(config['twitter']['localdb'])

    def __del__(self):
        self.conn.close()

    def add(self, id, author, url, text, addedby, channel, author_id):
        try:
            self.conn.execute('insert into tweets (id, author, url, msg, datetime, posted, addedby, channel, author_id) values (?, ?, ?, ?, datetime("now"), 0, ?, ?, ?)', (id, author, url, text, addedby, channel, author_id))
            self.conn.commit()
        except:
            pass

    def delete(self, id):
        try:
            self.conn.execute('delete from tweets where id = ?', (id,))
            self.conn.commit()
        except:
            pass


    def posted(self, id):
        try:
            self.conn.execute('update tweets set posted = 1 where id = ?', (id,))
            self.conn.commit()
        except:
            pass

    def count(self, id=0):
        if not id:
            return self.conn.execute("select count(*) from tweets where posted = 0").fetchone()[0]
        else:
            return self.conn.execute("select count(*) from tweets where id=?", (id,)).fetchone()[0]

    def get_all(self):
        return self.conn.execute("select * from tweets where posted <> 1 order by datetime desc limit 5").fetchall()

    def top_twitter(self):
        return self.conn.execute("select addedby, count(*) from tweets group by addedby order by count(*) desc").fetchall()

    def top_clean(self):
        return self.conn.execute("select author, count from image_log_count order by count desc").fetchall()

    def top_author(self, limit=-1):
        return self.conn.execute("select author, count(id), twitter_name from tweets left join twitter_account on tweets.author_id = twitter_account.id_user group by author order by count(id) desc limit ?", (limit,)).fetchall()

    def get_next(self):
        return self.conn.execute("select id, author, substr(url,0,105), msg, channel, author_id from tweets where posted = 0 order by datetime limit 1").fetchall()

    def get_nexts(self, limit=-1):
        return self.conn.execute("select author, substr(url,0,105), twitter_name from tweets left join twitter_account on tweets.author_id = twitter_account.id_user where posted = 0 order by datetime limit ?", (limit,)).fetchall()


    def create_link(self, author, twitter_account):
        self.remove_link(author)
        self.conn.execute("insert into twitter_account (id_user, twitter_name) values (?, ?)", (author, twitter_account))
        self.conn.commit()

    def remove_link(self, author):
        self.conn.execute("delete from twitter_account where id_user = ?", (author,))
        self.conn.commit()

    def get_link(self, author):
        link = self.conn.execute("select twitter_name from twitter_account where id_user = ?", (author,)).fetchone()
        if link:
            return link[0]
        else:
            return False

    def get_tracking(self, id):
        tracking = self.conn.execute("select track_id from tweets where id = ?", (id,)).fetchone()
        if tracking:
            return tracking[0]
        else:
            return False

    def set_tracking(self, id, track_id):
        self.conn.execute("update tweets set track_id = ? where id = ?", (track_id, id,))
        self.conn.commit()

    def add_image_log(self, id, channel, tracking_id, tracking_channel):
        self.conn.execute("insert into image_log (id, channel, tracking_id, tracking_channel) values (?, ?, ?, ?)", (id, channel, tracking_id, tracking_channel))
        self.conn.commit()

    def del_image_log(self, tracking_id, tracking_channel):
        self.conn.execute("delete from image_log where tracking_id = ? and tracking_channel = ?", (tracking_id, tracking_channel,))
        self.conn.commit()

    def add_clean(self, id_author, author):
        count = self.conn.execute("select count from image_log_count where id_author = ?", (id_author,)).fetchone()
        if count:
            self.conn.execute("update image_log_count set count = count + 1 where id_author = ?", (id_author,))
            self.conn.commit()
        else:
            self.conn.execute("insert into image_log_count (id_author, author, count) values (?, ?, 1)", (id_author,author, ))
            self.conn.commit()


    def get_image_tracking(self, id, channel):
        return self.conn.execute("select tracking_id, tracking_channel from image_log where id = ? and channel = ?", (id,channel,)).fetchone()


    def init_db(self, dbpath):
        self.conn = sqlite3.connect(dbpath)
        self.conn.execute("CREATE TABLE tweets ( id INTEGER, author TEXT NOT NULL, url TEXT NOT NULL, msg TEXT NOT NULL, datetime TEXT NOT NULL, posted INTEGER DEFAULT 0, addedby TEXT NOT NULL DEFAULT '', channel TEXT NOT NULL DEFAULT '' , author_id TEXT NOT NULL DEFAULT '', track_id INTEGER NOT NULL DEFAULT 0);")
        self.conn.execute("CREATE TABLE image_log ( id INTEGER, channel INTEGER, tracking_id INTEGER, tracking_channel INTEGER);")
        self.conn.execute("CREATE TABLE image_log_count ( id_author INTEGER, author TEXT NOT NULL, count INTEGER);")
        self.conn.commit()
        self.conn.close()

class MyTwitter():
    def __init__(self):
        self.tweet = {}
        # Authenticate to Twitter
        self.auth = tweepy.OAuthHandler(config['twitter']['api_key'], config['twitter']['api_secret'])
        self.auth.set_access_token(config['twitter']['token'], config['twitter']['token_secret'] )
        self.api = tweepy.API(self.auth)
        self.tdb = TweetDB()
    
    def set_img(self, url):
        self.tweet['url'] = url
        self.tweet['file'] = str(random.randrange(1,100))+".jpg"
        req = urllib.request.Request(url)
        req.add_header('User-Agent', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.123 Safari/537.36')

        try:
            f = open(self.tweet['file'], "wb")
            f.write(urllib.request.urlopen(req).read())
        except:
            print('something went wrong while fetching image {0}'.format(url))
        finally:
            f.close()

        self.resize_img()

    def resize_img(self):
        if os.path.exists(self.tweet['file'] ):
            if re.search('(?:jpg|jpeg)$', self.tweet['url']):
                image=Image.open(self.tweet['file'])
                if hasattr(image, '_getexif'): # only present in JPEGs
                    for orientation in ExifTags.TAGS.keys():
                        if ExifTags.TAGS[orientation]=='Orientation':
                            break 
                    e = image._getexif()       # returns None if no EXIF data
                    if e:
                        exif=dict(e.items())
                        orientation = exif[orientation] 

                        if orientation == 3:   image = image.transpose(Image.ROTATE_180)
                        elif orientation == 6: image = image.transpose(Image.ROTATE_270)
                        elif orientation == 8: image = image.transpose(Image.ROTATE_90)

                # print("{0} x {1}".format(image.size[0], image.size[1]))
                basewidth = 2048
                if image.size[0] > basewidth:
                    wpercent = (basewidth / float(image.size[0]))
                    hsize = int((float(image.size[1]) * float(wpercent)))
                    image = image.resize((basewidth, hsize), Image.ANTIALIAS)
                # print("{0} x {1}".format(image.size[0], image.size[1]))
                if image.size[1] > basewidth:
                    wpercent = (basewidth / float(image.size[1]))
                    hsize = int((float(image.size[0]) * float(wpercent)))
                    image = image.resize((hsize, basewidth), Image.ANTIALIAS)
                # print("{0} x {1}".format(image.size[0], image.size[1]))


                image.save(self.tweet['file'])




    def count(self, id=0):
        return self.tdb.count(id)

    def fetch_next(self):
        if self.tdb.count():
            post = self.tdb.get_next()[0]
            self.tweet['id'] = post[0]
            self.set_text(post[1], post[2], post[5])
            self.set_img(post[3])
            return True
        else:
            return False

    def set_text(self, author, text, author_id):
        self.tweet['author'] = author
        if author_id and self.tdb.get_link(author_id):
            self.tweet['author'] = "@{0}".format(self.tdb.get_link(author_id))
        self.tweet['text_tag'] = text
        self.tweet['text'] = random.choice(tag_head).format(self.tweet['author'],discord_link) + text + "\n\n" + random.choice(tag_phrase)
    
    def link_author(self, id, name):
        self.tdb.create_link(id, name)

    def unlink_author(self, id):
        if self.get_link_author(id):
            self.tdb.remove_link(id)
            return True
        return False

    def get_link_author(self, id):
        if self.tdb.get_link(id):
            return self.tdb.get_link(id)
        else:
            return False

    def set_tracking(self, id, track_id):
        self.tdb.set_tracking(id, track_id)

    def delete(self, id):
        track = self.tdb.get_tracking(id)
        self.tdb.delete(id)
        return track

    def push(self, id, author, text, url, addedby, channel, author_id):
        self.tdb.add(id, author, text, url, addedby, channel, author_id)
        self.tweet['author'] =  author
        self.tweet['url'] = url
        self.tweet['text'] = text

    def post(self):
        try:
            self.api.verify_credentials()
            #print("Authentication OK")
            self.tweet['auth'] = 1
        except:
            print("Error during authentication")

        if { 'auth', 'text', 'file' } <= set(self.tweet):
            try:
                tmptweet = self.api.update_with_media(self.tweet['file'], self.tweet['text'])
    #            media = self.api.media_upload(self.tweet['file'])
                self.api.update_status(status = tmptweet)
            except:
                pass
            finally:
                self.tdb.posted(self.tweet['id'])


        try:
            if os.path.exists(self.tweet['file'] ):
                os.remove(self.tweet['file'] )
        except:
            pass



# t = MyTwitter()

# a = t.tdb.get_next()[0]

#print("0: {0}\n1: {1}\n2: {2}\n3: {3}\n4: {4}\n5: {5}".format(a[0], a[1], a[2], a[3], a[4], a[5]))
#print("0: {0}\n1: {1}\n2: {2}\n3: {3}\n4: {4}".format(a[0], a[1], a[2], a[3], a[4]))

