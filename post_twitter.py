from instapy_cli import client
from discord_webhook import DiscordWebhook, DiscordEmbed
import praw

import configparser
config = configparser.ConfigParser()
config.read('config.cfg')

DISCORD_HOOK    = config['twitter']['hook']

reddit = praw.Reddit(**config['reddit'])


from include.twitter import MyTwitter

t = MyTwitter()
if t.fetch_next():
#        print("{0} - {1}".format(t.tweet['author'], t.tweet['text_tag']))
    try:
        reddit.subreddit('3dmeltdown').submit_image( "{0} - {1}".format(t.tweet['author'], t.tweet['text_tag']), t.tweet['file'], send_replies=False)
    except:
        pass
    t.post()


    # image = "/home/pi/3dmeltdown/"+t.tweet['file'] #here you can put the image directory
    # text = "{0} - {1}".format(t.tweet['author'], t.tweet['text'])
    # print(image)
    # print(text)
    # cli = client(username, password, cookie_file='insta_cookie.json')
    # cli.upload(image, text)

    webhook = DiscordWebhook(url=DISCORD_HOOK)
    embed = DiscordEmbed(title="By :{0}".format(t.tweet['author'].replace('@', '')), description="`{0}`\n\n[Link to tweet](https://twitter.com/3DMeltdown)".format(t.tweet['text_tag'].replace('`', '')), color=0xa21d1d)
    embed.set_author(name='3DMeltdown - New tweet!', url='https://twitter.com/3DMeltdown')
    embed.set_image(url=t.tweet['url'])
    embed.set_footer(text='3DMeltdown twitter: https://twitter.com/3DMeltdown', icon_url="https://cdn.discordapp.com/emojis/673897582375993365.png")
    webhook.add_embed(embed)
    webhook.execute()

#    print("hello")
