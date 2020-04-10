import time
import random
from discord_webhook import DiscordWebhook, DiscordEmbed
from datetime import datetime
import dateutil.relativedelta

DISCORD_HOOK  = 'ENTER_WEBHOOK_HERE'
webhook       = DiscordWebhook(url=DISCORD_HOOK)

post = [ [ "nsfbr", "https://discordapp.com/channels/637075986726518794/684966223502377013/687825286502547512", "https://cdn.discordapp.com/attachments/684966223502377013/687825297990483984/IMG_1026-2.jpg" ],
          [ "VisionOverload", "https://discordapp.com/channels/637075986726518794/684966223502377013/688131423139659918", "https://cdn.discordapp.com/attachments/684966223502377013/688131536473948289/20200313_1402401.jpg" ],
          [ "Derik", "https://discordapp.com/channels/637075986726518794/684966223502377013/688465094606454916", "https://cdn.discordapp.com/attachments/684966223502377013/688465353927688277/image0.jpg" ],
          [ "Coder76_", "https://discordapp.com/channels/637075986726518794/684966223502377013/688945972541259836", "https://cdn.discordapp.com/attachments/684966223502377013/688946256726458410/image2.jpg" ],
          [ "vincentWRX", "https://discordapp.com/channels/637075986726518794/684966223502377013/689176467544080485", "https://cdn.discordapp.com/attachments/684966223502377013/689176513425309700/DSC_1118.JPG" ],
          [ "AgentL3r", "https://discordapp.com/channels/637075986726518794/684966223502377013/689201716704313409", "https://cdn.discordapp.com/attachments/684966223502377013/689201723717582899/20200316_195206.jpg" ],
          [ "depark88", "https://discordapp.com/channels/637075986726518794/684966223502377013/691059356887810149", "https://cdn.discordapp.com/attachments/684966223502377013/691059650598273034/Vase2.jpg" ],
          [ "DePoRt_FiSh", "https://discordapp.com/channels/637075986726518794/684966223502377013/691135491311009864", "https://cdn.discordapp.com/attachments/684966223502377013/691135876008378399/IMG_20200321_224750242.jpg" ],
          [ "RenegadeAlpaca", "https://discordapp.com/channels/637075986726518794/684966223502377013/691778722214183017", "https://cdn.discordapp.com/attachments/684966223502377013/691786406397476864/IMG_20200323_185603_144.jpg" ],
          [ "DIY Jaad", "https://discordapp.com/channels/637075986726518794/684966223502377013/692082623962546277", "https://cdn.discordapp.com/attachments/684966223502377013/692082623756894318/IMG_20200324_132007.jpg" ],
          [ "Cdub3D", "https://discordapp.com/channels/637075986726518794/684966223502377013/692583558342246450", "https://cdn.discordapp.com/attachments/684966223502377013/692583926518120538/IMG_6779.jpg" ],
          [ "Jess", "https://discordapp.com/channels/637075986726518794/684966223502377013/694594761650208858", "https://cdn.discordapp.com/attachments/684966223502377013/694594783762448514/IMGP6391.jpg" ],
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


