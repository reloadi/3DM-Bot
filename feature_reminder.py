import time
import random
from discord_webhook import DiscordWebhook, DiscordEmbed
from datetime import datetime
import dateutil.relativedelta
import configparser
config = configparser.ConfigParser()
config.read('config.cfg')


DISCORD_HOOK    = eval(config['feature_reminder']['hooks'])
#print(desc)

embed = DiscordEmbed(title="3DMeltdown - Did you know?", color=0xa21d1d)
#    embed.set_author(name='3DMeltdown - Contest reminder!', url='https://discordapp.com/channels/637075986726518794/651199972221517824/674832873857220618')
#embed.set_footer(text='3DMeltdown feature reminder (every 12h)', icon_url="https://cdn.discordapp.com/emojis/673897582375993365.png")
embed.set_footer(text='3DMeltdown feature reminder (every 12h)')


post = [ [ "#octorant", "Octorant is a small octoprint plug-in that will send a screenshot of your print at set interval to the <#679793445526568999> channel allowing you to share your prints live!\n\nReally nice feature!\n[Check here to add yours](https://discordapp.com/channels/637075986726518794/637098805526790176/679860826290782221)" ],
         [ "#octorant", "Octorant is a small octoprint plug-in that will send a screenshot of your print at set interval to the <#679793445526568999> channel allowing you to share your prints live!\n\nReally nice feature!\n[Check here to add yours](https://discordapp.com/channels/637075986726518794/637098805526790176/679860826290782221)" ],
         [ "Twitter!", "Any images posted on 3DMeltdown may end up on our [twitter](https://twitter.com/3DMeltdown)!\n\nLink your twitter account with your discord user to get tagged when one of your masterpiece gets twitted with\n`!tweet link your_twitter_account_name`"],
         [ "3D Printing Contest", "Every month, we have a 3d printing with prize for the winner!\nSee <#651199972221517824> for more details!\n\n[See previous contest winners](https://discordapp.com/channels/637075986726518794/663124219147583489/663124922624638981)"],
         [ "3D Printing Contest", "Every month, we have a 3d printing with prize for the winner!\nSee <#651199972221517824> for more details!\n\n[See previous contest winners](https://discordapp.com/channels/637075986726518794/663124219147583489/663124922624638981)"],
         [ "3DM-bot", "We are constantly adding new features to the bot. Type `!3dm` in any channels to see available commands"],
         [ "Roles", "All community members should select the printer(s) they use to help smooth the talk and support!\n\nCheck out <#637459709947019266> to select yours!"],
         [ "Roles", "All community members should select the printer(s) they use to help smooth the talk and support!\n\nCheck out <#637459709947019266> to select yours!"],
         [ "Roles", "All community members should select the printer(s) they use to help smooth the talk and support!\n\nCheck out <#637459709947019266> to select yours!"],
         [ "Stay informed", "We are always trying to improve the community and we let you what's happening in <#637098805526790176>. Make sure you check it often! Also, make sure you look at the pinned messages in all the channels!"],
         [ "knowledge-base", "We have a very rich <#645828645578866718>!\n\nYou can find all kind of useful information like [esteps and flow calibration](https://discordapp.com/channels/637075986726518794/645828645578866718/647609534424023040), [bmg load script](https://discordapp.com/channels/637075986726518794/645828645578866718/647064065058799636), [belt tension](https://discordapp.com/channels/637075986726518794/645828645578866718/652330646919708692), [X axis alignement](https://discordapp.com/channels/637075986726518794/645828645578866718/646352392975286272), etc.. "],
         [ "Hardware build", "Building a new printer and want some live help?\nMaking an upgrade and want to share it?\n\nTake picture and upload them as you go in <#650473912127324190>"],
         [ "Hardware build", "Building a new printer and want some live help?\nMaking an upgrade and want to share it?\n\nTake picture and upload them as you go in <#650473912127324190>"],
         [ "Showoff and fail", "All members likes to see nice prints, share your pictures in <#637099044165910528> (please include a note explaining what it is!).\n\nOr.. Did the print fail?\nDon't throw it away before sharing your fail in <#666808946870190081>"],
         [ "Showoff and fail", "All members likes to see nice prints, share your pictures in <#637099044165910528> (please include a note explaining what it is!).\n\nOr.. Did the print fail?\nDon't throw it away before sharing your fail in <#666808946870190081>"],
         [ "MOD", "You need to talk to a mod? Just type:\n\n`@mod your message`\n\n_yes, this will notify the mods_\n\n**YOU DO NOT NEED TO TEST THIS, IT WORKS**"]
       ]

hook = random.choice(DISCORD_HOOK)
one = random.choice(post)
embed.add_embed_field(name=one[0], value=one[1], inline=False)
webhook = DiscordWebhook(url=hook, username="3DMeldown-features")
webhook.add_embed(embed)
webhook.execute()




