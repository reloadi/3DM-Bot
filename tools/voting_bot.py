import time
import random
from discord_webhook import DiscordWebhook, DiscordEmbed
from datetime import datetime
import dateutil.relativedelta

DISCORD_HOOK  = 'https://discordapp.com/api/webhooks/706167771633025065/gVQ7nZzuB5qlevw23ehh6napKHhCBmGjeQmGU-ruZc5xr1P19tHe4B0VPCQ2TAlJSFT1'
webhook       = DiscordWebhook(url=DISCORD_HOOK)

post = [ [ "vincentWRX", "https://discordapp.com/channels/637075986726518794/697648144628056144/700330442741514300", "https://cdn.discordapp.com/attachments/697648144628056144/700330548681244722/DSC_1243.JPG" ],
          [ "bruh", "https://discordapp.com/channels/637075986726518794/697648144628056144/703387236107812865", "https://cdn.discordapp.com/attachments/697648144628056144/703390570869031093/image0.jpg" ],
          [ "hughie1987", "https://discordapp.com/channels/637075986726518794/684966223502377013/694681706330062849", "https://cdn.discordapp.com/attachments/684966223502377013/694681894843056148/20200331_185323.jpg" ]
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


