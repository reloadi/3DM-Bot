import time
import random
from discord_webhook import DiscordWebhook, DiscordEmbed
from datetime import datetime
import dateutil.relativedelta

DISCORD_HOOK  = 'https://discordapp.com/api/webhooks/773354048899383338/fww2kibytobkRzjoXRfHipKpvX5OLM4vOIQVQxScbDQtkEo9CuWrKSmL6mSjW_fbSI7l'
webhook       = DiscordWebhook(url=DISCORD_HOOK)

post = [  [ "Puro", "https://discordapp.com/channels/637075986726518794/762872025210421268/767187014709280778", "https://cdn.discordapp.com/attachments/762872025210421268/767189127941849108/DSC01416.JPG" ],
          [ "Howling Wolf", "https://discordapp.com/channels/637075986726518794/762872025210421268/771559295770296350", "https://cdn.discordapp.com/attachments/762872025210421268/771559357808640030/20201029_193425.jpg" ],
          [ "vaportrail", "https://discordapp.com/channels/637075986726518794/762872025210421268/771618605698908160", "https://cdn.discordapp.com/attachments/762872025210421268/771618824810266624/20201029_183222.jpg" ],
          [ "Lewis", "https://discordapp.com/channels/637075986726518794/762872025210421268/771701132387942411", "https://cdn.discordapp.com/attachments/762872025210421268/771701617539416094/20201030_114552.jpg" ],
          [ "DIY Jaad", "https://discordapp.com/channels/637075986726518794/762872025210421268/771858996940111892", "https://cdn.discordapp.com/attachments/637099044165910528/771828747204165652/PXL_20201030_200803374.jpg" ],
          [ "hughie1987", "https://discordapp.com/channels/637075986726518794/762872025210421268/772165574926139402", "https://cdn.discordapp.com/attachments/762872025210421268/772165562695549009/20201031_142652.jpg" ]
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
