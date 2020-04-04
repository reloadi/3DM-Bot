import os
import re
import random
import urllib.request
import tweepy       # https://tweepy.readthedocs.io/en/latest/index.html
import configparser
import sqlite3

import mysql.connector
from mysql.connector import errorcode

from PIL import Image, ExifTags
#import ExifTags

config = configparser.ConfigParser()
config.read('3dm.cfg')

tag_phrase = ['Need some help? Want to share your latest print? Join us! We have a #3dprint contest!',
                'Join our #3dprinting discord to share your latest print! #3dprinter',
                'Have questions on #3dprinting or want to show your latest print? Join us! #3dprinters',
                "Become a member of our discord and share your prints! #ENDER3 #3dprinting #3dprinter",
                "Have some print you want to show? You need some help with #3dprinter ? Join our #3Dprinting discord! #3dprinter",
                "Need some #help or #support with your #3dprinter ? Join us! #ENDER3 #3dprinting",
                "Looking for help or advice ? 3D printing is your hobby ? #3DPrinter drives you crazy? Join our discord! It's free! :)",
                "Got a very nice print you want to show us? Need some help or advices ? Become part of our great #Discord #3DPrinter #3DModeling community!",
                "Interested in #3Dprinting #3DPrinter ? join us on our discord server!"
            ]
tag_head = [ 'Post by {0} on our discord community:\n\n',
             '{0} shared this on our discord server!\n\n',
             'Our community member {0} posted this on our discord:\n\n' ]

class TweetDB():
    def __init__(self):

        self.conn = mysql.connector.connect( host=config['database']['host'], user=config['database']['user'], passwd=config['database']['passwd'] )
        cursor = self.conn.cursor()

        try:
            cursor.execute("USE {}".format(config['database']['database']))
        except mysql.connector.Error as err:
            print("Database {} does not exists.".format(config['database']['database']))
            if err.errno == errorcode.ER_BAD_DB_ERROR:
                self.init_db(cursor, config['database']['database'])
                print("Database {} created successfully.".format(config['database']['database']))
                self.conn.database = config['database']['database']
            else:
                print(err)
                exit(1)


        #mycursor = mydb.cursor()

        #print(mydb)
        # if not os.path.exists(config['twitter']['localdb']):
        #     print("db doesn't exist -- creating")
        #     self.init_db(config['twitter']['localdb'])
        # self.conn = sqlite3.connect(config['twitter']['localdb'])

    def __del__(self):
        self.conn.close()

    def add(self, id, author, url, text, addedby, channel):
        try:
            self.conn.execute('insert into tweets (id, author, url, msg, datetime, posted, addedby, channel) values (?, ?, ?, ?, datetime("now"), 0, ?, ?)', (id, author, url, text, addedby, channel))
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

    def top_author(self):
        return self.conn.execute("select author, count(*) from tweets group by addedby order by count(*) desc").fetchall()


    def get_next(self):
        return self.conn.execute("select * from tweets where posted = 0 order by datetime limit 1").fetchall()


    def init_db(self, cursor, dbname):
        print("creating {0}".format(dbname))
        cursor.execute("CREATE DATABASE {0}".format(dbname))
        cursor.execute("use {0}".format(dbname))
        cursor.execute("CREATE TABLE `tweets` ("
                        "	`id` INT(10) UNSIGNED NOT NULL,"
                        "	`pos` INT(11) NOT NULL DEFAULT b'0',"
                        "	`author` VARCHAR(100) NOT NULL DEFAULT '',"
                        "	`url` VARCHAR(1000) NOT NULL DEFAULT '',"
                        "	`msg` VARCHAR(300) NOT NULL DEFAULT '',"
                        "	`datetime` DATETIME NOT NULL DEFAULT current_timestamp(),"
                        "	`posted` BIT(1) NOT NULL DEFAULT b'0',"
                        "	`addedby` VARCHAR(100) NOT NULL DEFAULT '',"
                        "	`channel` VARCHAR(100) NOT NULL DEFAULT ''"
                        ")"
                        "COLLATE='utf8mb4_general_ci'"
                        "ENGINE=InnoDB")

        # self.conn = sqlite3.connect(dbpath)
        # self.conn.execute("CREATE TABLE tweets ( id INTEGER, author TEXT NOT NULL, url TEXT NOT NULL, msg TEXT NOT NULL, datetime TEXT NOT NULL, posted INTEGER DEFAULT 0, addedby TEXT NOT NULL DEFAULT '', channel TEXT NOT NULL DEFAULT '' );")
        # self.conn.commit()
        # self.conn.close()

    def mod_db(self):
#        self.conn.execute("UPDATE tweets set posted = 0 where id = 672977207852793896")
#        self.conn.execute("ALTER TABLE tweets RENAME TO _tweets;")
#        self.conn.execute("CREATE TABLE tweets ( id INTEGER, author TEXT NOT NULL, url TEXT NOT NULL, msg TEXT NOT NULL, datetime TEXT NOT NULL, posted INTEGER DEFAULT 0, addedby TEXT NOT NULL DEFAULT '', channel TEXT NOT NULL DEFAULT '' );")
#        self.conn.execute("insert into tweets (id, author, url, msg, datetime) select id, author, url, msg, datetime from _tweets")
#        self.conn.execute("ALTER TABLE tweets ADD COLUMN channel TEXT;")
#        self.conn.execute("ALTER TABLE tweets ADD COLUMN posted INTEGER, addedby TEXT );")
        self.conn.commit()


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
            image=Image.open(self.tweet['file'])
            if hasattr(image, '_getexif'): # only present in JPEGs
                for orientation in ExifTags.TAGS.keys(): 
                    if ExifTags.TAGS[orientation]=='Orientation':
                        break 
                e = image._getexif()       # returns None if no EXIF data
                if e is not None:
                    exif=dict(e.items())
                    orientation = exif[orientation] 

                    if orientation == 3:   image = image.transpose(Image.ROTATE_180)
                    elif orientation == 6: image = image.transpose(Image.ROTATE_270)
                    elif orientation == 8: image = image.transpose(Image.ROTATE_90)

            basewidth = 2048
            if image.size[0] > basewidth:
                wpercent = (basewidth / float(image.size[0]))
                hsize = int((float(image.size[1]) * float(wpercent)))
                image = image.resize((basewidth, hsize), Image.ANTIALIAS)

            image.save(self.tweet['file'])




    def count(self, id=0):
        return self.tdb.count(id)

    def fetch_next(self):
        if self.tdb.count():
            post = self.tdb.get_next()[0]
            self.tweet['id'] = post[0]
            self.set_text(post[1], post[2])
            self.set_img(post[3])
            return True
        else:
            return False

    def set_text(self, author, text):
        self.tweet['author'] = author
        self.tweet['text'] = random.choice(tag_head).format(self.tweet['author']) + text + "\n\n" + random.choice(tag_phrase)
    
    def push(self, id, author, text, url, addedby, channel):
        self.tdb.add(id, author, text, url, addedby, channel)
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
            tmptweet = self.api.update_with_media(self.tweet['file'], self.tweet['text'])
            try:
                self.tdb.posted(self.tweet['id'])
                self.api.update_status(status = tmptweet)
            except:
                pass
        try:
            if os.path.exists(self.tweet['file'] ):
                os.remove(self.tweet['file'] )
        except:
            pass


#MyTwitter().push(672253211666808836, "someone", "some text", 'https://cdn.discordapp.com/attachments/666808946870190081/671043246260224001/DSC_0952.JPG')
#t.post()

db = TweetDB()

#db.mod_db()
#db.show_all()


# str = "vincentWRX https://cdn.discordapp.com/attachments/666808946870190081/671043246260224001/DSC_0952.JPG Found this hanging on my hotend"

# gs = re.search('^(.*) (http[^ ]+) (.*)', str).groups()

# print(len(gs))

# for i in gs:
#     print(i)



