import time
import random
from discord_webhook import DiscordWebhook, DiscordEmbed
from datetime import datetime
import dateutil.relativedelta

end_contest = datetime.fromisoformat('2020-07-05 22:00:00.000')
dt2 = datetime.fromtimestamp(time.time())

rd = dateutil.relativedelta.relativedelta (end_contest, dt2)

DISCORD_IDEX = 1
DESC_INDEX = 1

DISCORD_HOOK   =[ [ 'https://discordapp.com/api/webhooks/673352384822378511/jJpS3G87pDvSZyUoFYhu5i24ZvoFB7eg7Sje_BoA4uqWoYPYu9eXIfAD3YanJ4IXffVy',
                    'https://discordapp.com/api/webhooks/681991573390622752/Tp8j8ABuSSoktvp1WYotKgEcAccvJl9dN_Zh-1OTwkSExrQsBcTdlObvKY-UbbWd5pMl',
                    'https://discordapp.com/api/webhooks/673352065807941702/NhKZwFIC5JONfFZgNzmIQlX_JqUZND9WYJXIQatCJ-IXzWszp7rwb0-ysC6PPIUu_eiB',
                    'https://discordapp.com/api/webhooks/681992174358757387/_VcPefyyZHt-KoYea4GSOJxExBMTkb-jdg_e6I5pGZ3D3Ya3SNDiS6gyVHHwulx-lnXB',
                    'https://discordapp.com/api/webhooks/681991884100468823/0aJCwepjMzplaDFKCt0UgoIGo0VPT25VfeVF1HDU_eYbiiuO_I7dN62WpPZaDXm1-z1P',
                    'https://discordapp.com/api/webhooks/681992056389763093/baDkYEqFZRyxQN5HlDHLQhiklTSntkFDxPOOeBlrDN6b3v_DRGIflBYrJFKWt3Hqa2ng'
                  ],
                  [ 'https://discordapp.com/api/webhooks/673352384822378511/jJpS3G87pDvSZyUoFYhu5i24ZvoFB7eg7Sje_BoA4uqWoYPYu9eXIfAD3YanJ4IXffVy', # 3dprint, community and support1
                    'https://discordapp.com/api/webhooks/673352065807941702/NhKZwFIC5JONfFZgNzmIQlX_JqUZND9WYJXIQatCJ-IXzWszp7rwb0-ysC6PPIUu_eiB',
                    'https://discordapp.com/api/webhooks/681991884100468823/0aJCwepjMzplaDFKCt0UgoIGo0VPT25VfeVF1HDU_eYbiiuO_I7dN62WpPZaDXm1-z1P'
                  ],
                  [ 'https://discordapp.com/api/webhooks/681988092542189569/AdbhKMhrvILT_hasenxDlAtpKCz7VcgXmGsbcIdzmwJoKNRrsXvj3_JMTJJkSvAkj2kD' #test
                  ],
                  [ 'https://discordapp.com/api/webhooks/706193521446748259/F8i9_A_5SA_fHhYZ0aON3vN5lVJ4hUH_kOifYWDrI2hp4UszaviPnYdE9sYSmfG6h4bc', #announce
                    'https://discordapp.com/api/webhooks/706191608504385638/O54XqGz7QEWXaH5aDudsORUH9PtdLvFZmjmg-DEDPS-g9apoAwGhiDXK6iCdnsXThgp5' #news
                  ] ]


rule = 'https://discordapp.com/channels/637075986726518794/651199972221517824/719599252166279288'
post = [ 'https://media.discordapp.net/attachments/719616999902150737/727532843839914034/20200630_012308.jpg',
            'https://cdn.discordapp.com/attachments/719616999902150737/727390157539508294/20200630_005018.jpg',
            'https://cdn.discordapp.com/attachments/719616999902150737/725599175009370202/IMG_5289.JPG',
            'https://cdn.discordapp.com/attachments/719616999902150737/727359082453008414/IMG_20200629_204725.jpg',
            'https://cdn.discordapp.com/attachments/719616999902150737/724664420525146243/IMG_20200622_063247.jpg',
            'https://media.discordapp.net/attachments/719616999902150737/723521342179115148/DSC01608.JPG',
            'https://cdn.discordapp.com/attachments/719616999902150737/727648952077254766/image3.jpg',
            'https://cdn.discordapp.com/attachments/674431530562748419/722868663027499028/image0.jpg',
            'https://media.discordapp.net/attachments/719616999902150737/724650780912779264/c6fc0980-ed14-48d1-8850-b62e29729b25.png',
            'https://cdn.discordapp.com/attachments/719616999902150737/726797262549942273/DSC01067.jpg'
]
post_link = 'https://discordapp.com/channels/637075986726518794/719616999902150737/722868805411274824'
vote_link = 'https://discordapp.com/channels/637075986726518794/727872214371926076/727873608491204678'
left = "{0} days and {1} hours".format(rd.days, rd.hours)

desc = [ "Our 3D Printing contest is almost over!\n\nAnyone can submit a print!\nYou have {0} left before deadline!\n\n[See full contest rules]({1})\n[See posted prints]({2})\n".format(left, rule, post_link),
         "Our 3D Printing contest is now over it's now time to vote!\n\nAnyone can vote!\nYou have {0} left before deadline!\n\n[See submited prints]({1})\n\n[See full rules]({2})\n".format(left, vote_link, rule),
         "Our 3D Printing contest is now over it's now time to vote!\n\nAnyone can vote!\n\n[See submited prints]({1})\n\n[See full rules]({2})\n".format(left, vote_link, rule)
       ]

#print(desc)

embed = DiscordEmbed(title="3DMeltdown 3D Printing contest reminder!", description=desc[DESC_INDEX], color=0xa21d1d)
#    embed.set_author(name='3DMeltdown - Contest reminder!', url='https://discordapp.com/channels/637075986726518794/651199972221517824/674832873857220618')
embed.set_footer(text='3DMeltdown contest friendly reminder every 6h', icon_url="https://cdn.discordapp.com/emojis/673897582375993365.png")

for h in DISCORD_HOOK[DISCORD_IDEX]:
    embed.set_thumbnail(url=random.choice(post))
    webhook = DiscordWebhook(url=h)
    webhook.add_embed(embed)
    webhook.execute()
    webhook.remove_embed(0)
    time.sleep(1)

