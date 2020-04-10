import time
import random
from discord_webhook import DiscordWebhook, DiscordEmbed
from datetime import datetime
import dateutil.relativedelta

end_contest = datetime.fromisoformat('2020-02-29 21:00:00.000')
dt2 = datetime.fromtimestamp(time.time())

rd = dateutil.relativedelta.relativedelta (end_contest, dt2)


DISCORD_HOOK    = [ 
                  ]

rule = 'https://discordapp.com/channels/637075986726518794/651199972221517824/674832873857220618'
post = [ 'https://cdn.discordapp.com/attachments/673381582551121920/678064291961765898/DSC00430.jpg, ''https://cdn.discordapp.com/attachments/673381582551121920/675935542516645928/FebruaryContestPic1.png',
            'https://cdn.discordapp.com/attachments/673381582551121920/676181694587338762/1060950.png', 'https://cdn.discordapp.com/attachments/673381582551121920/676187298001584128/IMG_6378.jpg',
            'https://media.discordapp.net/attachments/673381582551121920/681560905661546620/DSC_1046.JPG', 'https://cdn.discordapp.com/attachments/673381582551121920/676849507694149672/20200211_185453.JPG',
            'https://cdn.discordapp.com/attachments/673381582551121920/678064810197254154/20200210_165219.jpg', 'https://cdn.discordapp.com/attachments/673381582551121920/681754598406357020/image1.jpg',
            'https://cdn.discordapp.com/attachments/673381582551121920/681754599199342612/image3.jpg', 'https://cdn.discordapp.com/attachments/673381582551121920/678064291961765898/DSC00430.jpg',
            'https://cdn.discordapp.com/attachments/673381582551121920/682043411557384243/image2.jpg', 'https://cdn.discordapp.com/attachments/673381582551121920/682043408986144769/image0.jpg',
            'https://cdn.discordapp.com/attachments/673381582551121920/682050629555847198/IMG_1095.JPEG', 'https://cdn.discordapp.com/attachments/673381582551121920/682050653928816910/IMG_1098.JPEG',
             'https://cdn.discordapp.com/attachments/673381582551121920/682054538361831426/20200225_212329.jpg', 'https://cdn.discordapp.com/attachments/673381582551121920/682054548063518768/20200225_213117.jpg' ]

post_link = 'https://discordapp.com/channels/637075986726518794/673381582551121920/674800800429768714'

left = "{0} days and {1} hours".format(rd.days, rd.hours)
desc = "Our 3D Printing contest is almost over!\n\nFirst prize:\n**- 1x EZAbl Kit  Sponsored by TH3D Studio**\n(value of 68$USD shipping is free)\n\nAnyone can submit a print!\nYou have {0} left before deadline!\n\n[See full contest rules]({1})\n[See posted prints]({2})\n".format(left, rule, post_link)

#print(desc)

embed = DiscordEmbed(title="3DMeltdown 3D Printing contest reminder!", description=desc, color=0xa21d1d)
#    embed.set_author(name='3DMeltdown - Contest reminder!', url='https://discordapp.com/channels/637075986726518794/651199972221517824/674832873857220618')
embed.set_footer(text='3DMeltdown contest friendly reminder every 6h', icon_url="https://cdn.discordapp.com/emojis/673897582375993365.png")

for hook in DISCORD_HOOK:
    embed.set_thumbnail(url=random.choice(post))
    webhook = DiscordWebhook(url=hook)
    webhook.add_embed(embed)
    webhook.execute()
    time.sleep(15)


