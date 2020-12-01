import time
import random
from discord_webhook import DiscordWebhook, DiscordEmbed
from datetime import datetime
import dateutil.relativedelta

end_contest = datetime.fromisoformat('2020-09-30 23:59:00.000')
dt2 = datetime.fromtimestamp(time.time())

rd = dateutil.relativedelta.relativedelta (end_contest, dt2)

DISCORD_IDEX = 0 #test: 2
DESC_INDEX = 0
DISCORD_HOOK   =[ [ 'https://discordapp.com/api/webhooks/673352384822378511/jJpS3G87pDvSZyUoFYhu5i24ZvoFB7eg7Sje_BoA4uqWoYPYu9eXIfAD3YanJ4IXffVy',
                    'https://discordapp.com/api/webhooks/673352065807941702/NhKZwFIC5JONfFZgNzmIQlX_JqUZND9WYJXIQatCJ-IXzWszp7rwb0-ysC6PPIUu_eiB',
                    'https://discordapp.com/api/webhooks/681991884100468823/0aJCwepjMzplaDFKCt0UgoIGo0VPT25VfeVF1HDU_eYbiiuO_I7dN62WpPZaDXm1-z1P',
                    'https://discordapp.com/api/webhooks/681991573390622752/Tp8j8ABuSSoktvp1WYotKgEcAccvJl9dN_Zh-1OTwkSExrQsBcTdlObvKY-UbbWd5pMl', #showoff
                    'https://discordapp.com/api/webhooks/681992174358757387/_VcPefyyZHt-KoYea4GSOJxExBMTkb-jdg_e6I5pGZ3D3Ya3SNDiS6gyVHHwulx-lnXB', # support-3
                    'https://discordapp.com/api/webhooks/681992056389763093/baDkYEqFZRyxQN5HlDHLQhiklTSntkFDxPOOeBlrDN6b3v_DRGIflBYrJFKWt3Hqa2ng'  # support-2
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


rule = 'https://discordapp.com/channels/637075986726518794/651199972221517824/755186852750950421'
post = [ 'https://cdn.discordapp.com/attachments/637075986726518796/759941463940923422/unknown.png',
            'https://cdn.discordapp.com/attachments/755183696176480306/757736934180388915/image0.jpg',
            'https://cdn.discordapp.com/attachments/755183696176480306/757736934448824350/image1.jpg',
            'https://cdn.discordapp.com/attachments/755183696176480306/757736934931169310/image3.jpg',
            'https://cdn.discordapp.com/attachments/755183696176480306/758876516578361375/0924202213.jpg',
            'https://cdn.discordapp.com/attachments/755183696176480306/758876637919051816/0924201834f.jpg',
            'https://cdn.discordapp.com/attachments/755183696176480306/759468887225270272/20200925_222548.jpg',
            'https://cdn.discordapp.com/attachments/755183696176480306/759468910994522136/20200925_171138.jpg',
            'https://cdn.discordapp.com/attachments/755183696176480306/759894989177880595/IMG_3005.jpg',
            'https://cdn.discordapp.com/attachments/755183696176480306/759894994831015936/D826012-sRGB_4096.JPG'
]
post_link = 'https://discordapp.com/channels/637075986726518794/755183696176480306/755705401613221908'
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
