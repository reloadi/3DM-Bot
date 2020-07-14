import time
import random
from discord_webhook import DiscordWebhook, DiscordEmbed
from datetime import datetime
import dateutil.relativedelta

DISCORD_HOOK  = 'https://discordapp.com/api/webhooks/717043301852905562/JtkMAun4Mjn6jHWCcMz-eZf2sRbLK7ZWFsxFEp-9grxlNidpzBW87QV0xMi9mVsTacMa'
webhook       = DiscordWebhook(url=DISCORD_HOOK)

post = [  [ "bruh", "https://discordapp.com/channels/637075986726518794/708483892679802922/710719015898710096", "https://cdn.discordapp.com/attachments/674431530562748419/710718630521864292/image0.jpg" ],
          [ "Derik", "https://discordapp.com/channels/637075986726518794/708483892679802922/713915116139053136", "https://cdn.discordapp.com/attachments/708483892679802922/713915345836179466/image0.jpg" ],
          [ "VincentWRX", "https://discordapp.com/channels/637075986726518794/708483892679802922/715078726798540827", "https://cdn.discordapp.com/attachments/708483892679802922/715078748642213928/DSC_1328.JPG" ],
          [ "Puro 😾", "https://discordapp.com/channels/637075986726518794/708483892679802922/715707754337271819", "https://cdn.discordapp.com/attachments/708483892679802922/715708001800945665/20200528_191108.jpg" ],
          [ "depark88", "https://discordapp.com/channels/637075986726518794/708483892679802922/716455871051464716", "https://cdn.discordapp.com/attachments/708483892679802922/716455902118543490/4.jpg" ],
          [ "nsfbr", "https://discordapp.com/channels/637075986726518794/708483892679802922/716774680412815482", "https://cdn.discordapp.com/attachments/708483892679802922/716774829008617542/D825976-sRGB_4096.JPG" ],
          [ "Cdub3D", "https://discordapp.com/channels/637075986726518794/708483892679802922/716798257392517190", "https://cdn.discordapp.com/attachments/708483892679802922/716798358584557628/IMG_7162.JPG" ],
          [ "hetile❄", "https://discordapp.com/channels/637075986726518794/708483892679802922/716811636278820936", "https://cdn.discordapp.com/attachments/708483892679802922/716811697863655444/20200531_201141.jpg" ]
       ]

embed = DiscordEmbed(title="3DMeltdown - Voting", color=0xa21d1d)
random.shuffle(post)
for p in post:
    embed = DiscordEmbed(title=f"By :{p[0]}", description=f"[See full post]({p[1]})", color=0xa21d1d)
    embed.set_image(url=p[2])
    webhook.add_embed(embed)
    webhook.execute()
    webhook.remove_embed(0)
    time.sleep(1)
