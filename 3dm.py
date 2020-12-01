import discord
from discord.ext.commands import CommandNotFound
import subprocess
import signal
import re
import os
import asyncio
import urllib.request
import requests
from zipfile import ZipFile
from datetime import datetime
from currency_converter import CurrencyConverter as CConv

from include.linux_color import _c as ct
from include.my_google import Google
from include.twitter import MyTwitter

#Cogs
#from Cogs.DiceCog import DiceCog

import configparser
config = configparser.ConfigParser()
config.read('config.cfg')

VERSION= "1.1.24 - on aws"
DEBUG  = True
PREFIX = "!3DM"
GCODE  = "!GCODE"

SERVER_ID       = int(config['discord']['serer_id'])
BOT_CHANNEL_ID  = int(config['discord']['bot_channel_id'])

# currency converted config
my_cur = eval(config['currency']['use'])

# used to log tweets added/posted
DELETE_EMOJI    = "dead_cat"
TRACKING_TWEETS = int(config['twitter']['tracking_channel'])
POST_COLOR      = 0xa21d1d

# used to track posted images and logged in TRACKING_IMG channel
listen_channels = eval(config['img_log']['listen_channels'])
ignore_domain   = eval(config['img_log']['ignore_domain'])
TRACKING_IMG    = int(config['img_log']['tracking_channel'])

# used to help user unable to join the server
JOIN_CHANNEL    = 689574436302880843
WELCOME_MESSAGE = f"https://discordapp.com/channels/{SERVER_ID}/637076225843527690/637108901720096770"

COUNT_CHANNEL   = 732365559647174736

t = MyTwitter()

intents = discord.Intents().all()
#bot = discord.Client()
bot = discord.ext.commands.Bot(command_prefix='', case_insensitive=True, intents=intents)
#bot.add_cog(DiceCog(bot))

# fix some different way to type currency
class cc_arg():
    def __init__(self, nb, unit):
        self.amount = float(nb)
        self.curr = unit.upper().replace("EURO", "EUR").replace("CDN", "CAD").replace("YEN", "JPY")

# return a formated help page
def __help():
    output = discord.Embed(description="help screen", color=POST_COLOR)
    output.add_field(name="!gcode some_text", value="Return result from marlin documentation", inline=False)
    output.add_field(name="!convert 100 usd", value="Convert 100 usd to common currencies", inline=False)
    output.add_field(name="!google some text", value="Search google for some text and display first result", inline=False)
    output.add_field(name="!tweet link [user]", value="Link your discord user to a twitter account for tagging when posting. If [user] is ommited, display current link", inline=False)
    output.add_field(name="!tweet unlink", value="Remove link between discord account and twitter account", inline=False)
    output.add_field(name="!tweet top", value="Show top twitted members", inline=False)
    output.add_field(name="!tweet stat [user]", value="Show current twitter stats for [user] or yourself", inline=False)
    output.add_field(name="!tweet next", value="Display the next 5 tweets in queue", inline=False)
    output.add_field(name="!tweet [list|delete|ID] [pos] short text (restricted)", value="Post a user's message (ID) to the twitter account.", inline=False)
    output.add_field(name="Community",value="The following are community contributions", inline=False)
    output.add_field(name="/roll [xDn] (xDn...)",value="Where x is the number of dice and n is the number of sides on the dice. Ex: 1D6 2D8", inline=False)
    return output

# used for local debugging
def __debug(msg, text=False):
    if DEBUG:
        if not text:
            print("{0} {1} sent {2} in #{3}".format(ct.dark(datetime.now().strftime('%Y-%m-%d %H:%M:%S')), ct.cyan(msg.author), ct.invert(msg.content), ct.red(msg.channel)), flush=True)
        else:
            print("{0} debug: {1}".format(ct.dark(datetime.now().strftime('%Y-%m-%d %H:%M:%S')), ct.invert(msg)), flush=True)

# this method check if a message contain image and could be used for tweets
# if it does, post a copy/desc in a logging channel for manual processing
async def checkImgPost(msg):
    post_url = ""
    if msg.channel.id in listen_channels:
        # if the submitted message has attachments
        if msg.attachments:
            att = msg.attachments[0]
            post_url = att.url
        # check for link
        else:
            att = re.search('(http[^ ]+)', msg.content)
            # link was found
            if att:
                post_url = att.groups()[0]

        if post_url:
            if not any(xs in post_url for xs in ignore_domain):
                check = re.search('(http[^ ]+(:?jpg|png|jpeg))', post_url.lower())
                if check and not 'unknown.png' in post_url.lower():
                    post_link = 'https://discordapp.com/channels/{2}/{0}/{1}'.format( msg.channel.id, msg.id, SERVER_ID )
                    out_emb = discord.Embed(title="New image from: {0}".format(msg.author.display_name),
                                            description="Sent in <#{0}> - _[original post]({2})_\n\n>>> `{1}`".format(msg.channel.id, msg.content, post_link), color=0xffffff)
                    try:
                        out_emb.set_thumbnail(url=post_url)
                    except:
                        pass
                    out_emb.set_footer(text="!tweet {0}".format(msg.id))

                    cross_post = bot.get_channel(TRACKING_IMG)
                    info = await cross_post.send(embed=out_emb)
                    emoji_delete   = discord.utils.get(bot.emojis, name=DELETE_EMOJI)
                    await info.add_reaction(emoji_delete)
                    t.tdb.add_image_log(msg.id, msg.channel.id, info.id, info.channel.id)

# this print out a message to a user in the join-help channel
async def noob(msg):
    out_emb = discord.Embed(title="Welcome to 3DMeltdown",
                                description="Hi <@{0}>! This room is only to help you join the server.\n\n"\
                                    "Please see [this message]({1}) to join the server, you need to react to gain access.\n\n"\
                                    "If for some reason, you can't join, please tag the mod using\n"\
                                    "`@mod your message` someone should be able to help.".format(msg.author.id, WELCOME_MESSAGE), color=POST_COLOR)
    out_emb.set_footer(text="This message (and yours) will self-delete in 12 hours")
    id = await msg.channel.send(embed=out_emb)
    await id.delete(delay=43200)
    await msg.delete(delay=43200)

    return True

async def count_control(msg):
    roles   = [y.name.lower() for y in msg.author.roles]
    if re.match( r"I(?:'M| AM) A LO*SER" , msg.content.upper() ):
        __debug("line match", True)
        if "loser" in roles:
            __debug("role present", True)
            out_emb = discord.Embed(title="so.. you're a loser",
                                        description="Thanks for reconnizing it <@{0}>! We'll make it easy on you.\n\n"\
                                            "Your countdown started. You will get tagged once you can re-gain the role.\n\n"\
                                            "\n\nTHE DELAY IS CURRENTLY OFF, YOU GET THE ROLE BACK.\n\n"\
                                            "This message will self-delete in 30 sec. Yours in 1 hour".format(msg.author.id), color=POST_COLOR)
            #out_emb.set_footer(text="This message will self-delete in 30 sec. Yours in 12 hours")
            id = await msg.channel.send(embed=out_emb)
            await id.delete(delay=30)
            await msg.author.remove_roles(discord.utils.get(msg.author.guild.roles, name="Loser"))
            await msg.delete(delay=3600)
    else:
        await msg.delete()

    return True


async def my_background_task():
    me = bot.guild.members
    fixed = []
    for x in me:
        roles   = [y.name.lower() for y in x.roles]
        if x.bot or 'poop hitter' in roles:
            continue
        fixed.append(x)
        await x.add_roles(discord.utils.get(msg.author.guild.roles, name="poop hitter"))
    output = ""
    if fixed:
        output = "Fixed members: {0}\n".format(len(fixed))
        for x in fixed:
            output += "- {0} ({1})\n".format(x, x.display_name)
    else:
        output = "No member fixed"

    await client.wait_until_ready()
    counter = 0
    channel = discord.Object(id='channel_id_here')
    while not client.is_closed:
        counter += 1
        await client.send_message(channel, counter)
        await asyncio.sleep(60) # task runs every 60 seconds

async def play_voice(sound, ch):
    if not ch:
        ch = 637399140086710292

    print(f"ch: {ch}")
    vc = await bot.get_channel(int(ch)).connect()
    vc.play(discord.FFmpegPCMAudio("sound/" + sound.lower() + '.mp3'), after=lambda e: print('done', e))
    while vc.is_playing():
        await asyncio.sleep(1)
    vc.stop()
    await vc.disconnect()

@bot.event
async def on_ready():
    __debug(f"on_ready - We have logged in as {bot.user}", True)
    booted = bot.get_channel(BOT_CHANNEL_ID)
    await booted.send(f"I've been rebooted - v{VERSION}")
@bot.event
async def on_disconnect():
    __debug('on_disconnect', True)
@bot.event
async def on_connect():
    __debug('on_connect', True)
@bot.event
async def on_resumed():
    __debug("on_resumed", True)
# @bot.event
# async def on_error(event, *args, **kwargs):
#     __debug(f"on_error: {event}", True)
# Ignore command not found errors and don't print them to the output
@bot.event
async def on_command_error(ctx, error):
    __debug(f"on_command_error: {error}", True)
    if isinstance(error, CommandNotFound):
        return
    raise error

@bot.event
async def on_raw_reaction_add(payload):
    if payload.user_id == bot.user.id:
        return

    # monitor the image log channel, if someone hit a reaction, remove it from channel
    if payload.channel_id in [TRACKING_IMG, JOIN_CHANNEL] and payload.emoji.name in [DELETE_EMOJI]:
        guild   = bot.get_guild(payload.guild_id)
        member  = guild.get_member(int(payload.user_id))

        cross_post = bot.get_channel(payload.channel_id)
        #__debug(payload, True)
        image_post = await cross_post.fetch_message(payload.message_id)
        # check if member is allowed
        if t.allowed(member.roles):
            __debug(f"{payload.member.name} deleted {payload.message_id}", True)
            await image_post.delete()
            t.tdb.del_image_log(payload.message_id, payload.channel_id)
            t.tdb.add_clean(payload.user_id, payload.member.name)
        # not allowed, post a message
        else:
            out_emb = discord.Embed(title="Not allowed", description="Thanks for your interest <@{0}>!\n\n"\
                                                            "If you think you can help cleaning this, talk to a mod!".format(member.id), color=POST_COLOR)
            id = await cross_post.send(embed=out_emb)
            await id.delete(delay=8)

@bot.event
async def on_message(msg):
    if msg.author == bot.user:
        return

    msg_content = msg.content.upper()

    # don't react to anything from a bot/hook
    if not msg.author.bot:
        # If the message is in the join-issue channel
        if msg.channel.id == JOIN_CHANNEL:
            await noob(msg)
            return

        # check if it's a image for the image log (for twitter posts)
        await checkImgPost(msg)

        # some useless role tagging
        if "WEEB" in msg_content and not "HTTP" in msg_content:
            roles   = [y.name.lower() for y in msg.author.roles]
            if not "weeb" in roles:
                __debug(msg)
                await msg.author.add_roles(discord.utils.get(msg.author.guild.roles, name="weeb"))
                await msg.channel.send("{0} used the `w` word.. adding role.".format(msg.author.display_name))
        if re.search("ANUS", msg_content) or re.search("ANAL(?!I|Y|O)", msg_content):
            roles   = [y.name.lower() for y in msg.author.roles]
            if not "anal" in roles:
                __debug(msg)
                await msg.author.add_roles(discord.utils.get(msg.author.guild.roles, name="Anal"))
                await msg.channel.send("{0} used the `a` word.. adding role.".format(msg.author.display_name))

        # This handle all the twitter automation.
        if msg_content.startswith("!TWEET"):
            delete_delay = 8
            __debug(msg)
            if len(msg.content) < 10:
                await msg.channel.send(embed=__help())
            else:
                out_msg = ""
                out_emb = False
                sub_msg = msg.content[7:].upper()
                # Check if user is allowed to use this command
                if t.allowed(msg.author.roles) or sub_msg.startswith("TOP") or sub_msg.startswith("LINK") or sub_msg.startswith("UNLINK") \
                                or sub_msg.startswith("SHOW") or sub_msg.startswith("NEXT") or sub_msg.startswith("STAT"):
                    emoji_twitter   = discord.utils.get(bot.emojis, name='twitter')
                    emoji_3dm       = discord.utils.get(bot.emojis, name='3DM')
                    delete_post     = True
                    if sub_msg.startswith("LIST"):
                        out_msg += "DB contain {0} entry. Displaying lastest 5.".format(t.count())
                        for i in t.tdb.get_all():
                            out_msg += "```{0}\n```".format(i)
                        if not out_msg:
                            out_msg = "DB is empty"
                    elif sub_msg.startswith("DELETE"):
                        id = re.search(r'^ *(\d+)', msg.content[14:]).group(1)
                        track = t.delete(id)
                        try:
                            mm = await bot.get_channel(TRACKING_TWEETS).fetch_message(track)
                            await mm.delete()
                            mm = await msg.channel.fetch_message(id)
                            await mm.remove_reaction(emoji_3dm, bot.user)
                            await mm.remove_reaction(emoji_twitter, bot.user)
                        except:
                            pass

                        out_msg += "Tweet id {0} was deleted".format(id)
                    elif sub_msg.startswith("TOP_3DM"):
                        out_msg += "3DMeltdown top 3DM-twitters:\n"
                        for i in t.tdb.top_twitter():
                            out_msg += "**{0}** - {1} post(s)\n".format( (i[0] if i[0] else 'none'), i[1])
                        delete_post = False
                    elif sub_msg.startswith("TOP_CLEAN"):
                        out_msg += "3DMeltdown top cleaner:\n"
                        for i in t.tdb.top_clean():
                            out_msg += "**{0}** - {1} cleans\n".format( (i[0] if i[0] else 'none'), i[1])
                        delete_post = False
                    # !tweet stat [user]
                    elif sub_msg.startswith("STAT"):
                        # check if a user was provided
                        twho = re.search('^ *(.+)', msg.content[12:])
                        if not twho:
                            twho = msg.author.display_name
                        else:
                            twho = twho.group(1)
                        out_msg += "3DMeltdown twitter stats: (_<https://twitter.com/3DMeltdown>_)\n"
                        out_msg += f"Member: **{twho}**\n"
                        # get info about the user
                        infos = t.tdb.get_stat(twho)
                        if infos:
                            out_msg += f"Total queued tweets: **{infos[0][1]}**\n"
                            out_msg += f"Total posted tweets: **{infos[1][1]}**\n"
                        else:
                            out_msg += "No stats found"
                    elif sub_msg.startswith("TOP"):
                        out_msg += "3DMeltdown top 10 tweeted members: (_<https://twitter.com/3DMeltdown>_)\n"
                        x=1
                        for i in t.tdb.top_author(10):
                            out_msg += "#{3:>2} **{0}** - {1} post(s) {2}\n".format( (i[0] if i[0] else 'none'), i[1], ('' if i[2] else '   ---  **not linked**'), x)
                            x+=1
                        out_msg += "_link your twitter account to get tagged with_ `!tweet link your_twitter_account`"
                        delete_post = False
                    elif sub_msg.startswith("NEXT"):
                        out_emb = True
                        desc = "link your twitter account to get tagged with\n`!tweet link your_twitter_account`\n\n[Link to 3DMeltdown twitter](https://twitter.com/3DMeltdown)\n"
                        out_msg = discord.Embed(title="3DMeltdown next 5 tweets", description=desc, color=POST_COLOR)
                        x=1
                        for i in t.tdb.get_nexts(5):
                            who = "#{0:>2} {1} {2}".format( x, i[0], ('' if i[2] else '   ---  **not linked**'))
                            what = "_{0}_".format( i[1] )
                            out_msg.add_field(name=who, value=what, inline=False)
                            x+=1
                        out_msg.set_footer(text='3DMeltdown twitter queue size: {0}'.format(t.count()), icon_url="https://cdn.discordapp.com/emojis/673897582375993365.png")
                        delete_delay = 20

                    elif sub_msg.startswith("LINK"):
                        tname = re.search('^ *(.+)', msg.content[12:])
                        if tname:
                            out_msg += "Linked user [{0}] to twitter account [{1}]".format(msg.author, tname.group(1).replace('@',''))
                            t.link_author(str(msg.author), tname.group(1))
                        else:
                            tmp = t.get_link_author(str(msg.author))
                            if tmp:
                                out_msg += "[{0}] is currently linked to twitter account [{1}]".format(msg.author, tmp)
                            else:
                                out_msg += "[{0}] is currently not linked to any account".format(msg.author)
                    elif sub_msg.startswith("UNLINK"):
                        if t.unlink_author(str(msg.author)):
                            out_msg += "[{0}] was unlinked".format(msg.author)
                        else:
                            out_msg += "[{0}] is not currently linked".format(msg.author)

                    else:
                        gs = re.search(r'^ *(\d+) *(\d)? +(.*)', msg.content[7:]).groups()
                        # check if enough parametter
                        if len(gs) >= 2:
                            if len(gs[2]) <= 125:
                                post_msg = await msg.channel.fetch_message(gs[0])
                                # check if post already in db
                                if not t.count(post_msg.id):
                                    tweet_added = False
                                    post_url = ""
                                    # if the submitted message has attachments
                                    if post_msg.attachments:
                                        att = post_msg.attachments[int(gs[1])-1 if gs[1] else 0]
                                        post_url = att.url
                                        out_msg += "Tweet from {0} queued. Current position: {1}".format(post_msg.author.display_name, t.count())
                                        tweet_added = True
                                    # check for link
                                    else:
                                        att = re.findall('(http[^ \n]+)', post_msg.content)
                                        # link was found
                                        if att:
                                            post_url = att[int(gs[1])-1 if gs[1] else 0]
                                            out_msg += "Tweet from {0} queued. Current position: {1}".format(post_msg.author.display_name, t.count())
                                            tweet_added = True
                                        # no link found
                                        else:
                                            out_msg += "Link not found\n"
                                    if post_url:
                                        t.push(post_msg.id, post_msg.author.display_name, gs[2].replace('`', ''), post_url, str(msg.author), str(msg.channel), str(post_msg.author))

                                    # send info in log channel about this new tweet
                                    if tweet_added:
                                        await post_msg.add_reaction(emoji_3dm)
                                        await post_msg.add_reaction(emoji_twitter)
                                        cross_post = bot.get_channel(TRACKING_TWEETS)
                                        post_link = 'https://discordapp.com/channels/{2}/{0}/{1}'.format( msg.channel.id, post_msg.id, SERVER_ID )
                                        out_emb = discord.Embed(title="New tweet queued from: {0}".format(post_msg.author.display_name),
                                                                            description="Sent in <#{0}> - _[original post]({2})_\n\n>>> `{1}`".format(msg.channel.id, gs[2].replace('`', ''), post_link), color=0xffffff)
                                        #out_emb.set_author(name=post_link, url=post_link)
                                        out_emb.set_footer(text="added by {0}".format(msg.author.display_name), icon_url="https://cdn.discordapp.com/emojis/673897582375993365.png")
                                        out_emb.add_field(name="Current position", value="{0}\n".format(t.count()), inline=False)
                                        try:
                                            out_emb.set_thumbnail(url=post_url)
                                        except:
                                            pass

                                        cp_id = await cross_post.send(embed=out_emb)
                                        out_emb = False
                                        t.set_tracking(post_msg.id, cp_id.id)

                                        # check if the images was posted in log if so, delete it
                                        image_log = t.tdb.get_image_tracking(post_msg.id, msg.channel.id)
                                        if image_log:
                                            cross_post = bot.get_channel(image_log[1])
                                            image_post = await cross_post.fetch_message(image_log[0])
                                            t.tdb.del_image_log(image_post.id, image_post.channel.id)
                                            await image_post.delete()



                                # post already in db
                                else:
                                    out_msg += "Message id {0} is already in the DB".format(post_msg.id)
                            # msg too long
                            else:
                                out_msg += "Text too long: {0} max: 105".format(len(gs[2]))
                        # invalid params
                        else:
                            out_msg += "Invalid parameters `{0}`".format(msg.content[7:])
                else:
                    out_msg += "Sorry {0} you're not allowed to use this command".format(msg.author.display_name)

                my_msg = ""
                if out_emb:
                    my_msg = await msg.channel.send(embed=out_msg)
                else:
                    my_msg = await msg.channel.send(out_msg)

                if delete_post:
                    await msg.delete()
                    await my_msg.delete(delay=delete_delay)

        # This handle the currency conversion
        elif msg_content.startswith("!CONVERT") or msg_content.startswith("/CONVERT"):
            __debug(msg)

            cmd = re.search(r'^.CONVERT *([\.\d]+) *(.*)', msg_content)
            if not cmd:
                await msg.channel.send(embed=__help())
            else:
                nb = cmd.groups()[0]
                unit = cmd.groups()[1]

                my_conv = CConv(config['currency']['csv_file'])
                cc = cc_arg(nb, unit)
                output = discord.Embed(description="Currency convertion: `{0:0.2f}{1}` ({2})".format(cc.amount, my_cur[cc.curr], cc.curr), color=POST_COLOR)
                for cur in my_cur:
                    if cur != cc.curr:
                        tmpc = my_conv.convert(cc.amount, cc.curr, cur)
                        output.add_field(name=cur, value="{0:0.2f}{1}".format(tmpc, my_cur[cur]), inline=True)
                await msg.channel.send(embed=output)

        # Google search engine
        elif msg_content.startswith("!GOOGLE"):
            __debug(msg)
            if len(msg.content) < 11:
                await msg.channel.send(embed=__help())
            else:
                g = Google(**config['google'])

                result = g.search(msg.content[8:])

                if result:
                    title = "no title set"
                    snippet = "no description set"
                    if "title" in result:
                        title = result['title']
                    if "snippet" in result:
                        snippet = result['snippet'].replace('\n','')

                    output = discord.Embed(title=title, description=snippet, color=POST_COLOR)
                    output.set_author(name=result['link'], url=result['link'])
                    try:
                        output.set_thumbnail(url=result['pagemap']['cse_thumbnail'][0]['src'])
                    except:
                        pass
                    await msg.channel.send(embed=output)

                else:
                    await msg.channel.send("no result found for `{0}`".format(msg.content[8:]))

        # All the 3dm sub-command
        elif msg_content.startswith(PREFIX):
            output  = ""
            __debug(msg)
            if len(msg.content) < len(PREFIX) + 2 or msg.content == PREFIX + " help":
                await msg.channel.send(embed=__help())

            else:
                cmd = msg.content.split(" ")
                if cmd[1] == "fix_poop":
                    me = msg.guild.members
                    fixed = []
                    for x in me:
                        roles   = [y.name.lower() for y in x.roles]
                        if x.bot or 'poop hitter' in roles:
                            continue
                        fixed.append(x)
                        await x.add_roles(discord.utils.get(msg.author.guild.roles, name="poop hitter"))
                    output = ""
                    if fixed:
                        output = "Fixed members: {0}\n".format(len(fixed))
                        for x in fixed:
                            output += "- {0} ({1})\n".format(x, x.display_name)
                    else:
                        output = "No member fixed"

                elif cmd[1] == "test":
                    output = "test cmd\nCommand trigger: {0}\nChannel: {1}".format(PREFIX, msg.channel)
                else:
                    output = "unknown cmd: {0}".format(cmd[1])

                await msg.channel.send(output)

        # useless unit conversion
        elif msg_content.startswith("!MMS"):
            cmd = re.search(r'^!MMS *([\.\d]+)', msg_content)
            if cmd:
                nb = float(cmd.groups()[0])
                output = discord.Embed(description="American conversion: `{0:0.2f}` (mm/sec)".format(nb), color=POST_COLOR)
                output.add_field(name="inch/sec", value="{0:0.5f}".format(nb / 25.4), inline=True)
                output.add_field(name="foot/sec", value="{0:0.5f}".format(nb/305), inline=True)
                output.add_field(name="mph", value="{0:0.5f}".format(nb/447), inline=True)
                await msg.channel.send(embed=output)

        elif msg_content.startswith("!VC"):
            cmd = re.search(r'^!vc *(.*?) *(\d*)$', msg.content,  flags=re.IGNORECASE)
#            __debug("match: {}".format(cmd))
            if cmd:
                if cmd.groups()[0].upper().startswith("LIST"):
                    output = "Available sounds:\n"
                    for s in os.listdir("sound/"):
                        if s.upper().endswith("MP3"):
                            output += "- *{0}*\n".format(s.lower().replace(".mp3", ""))
                    output += "use: `!vc sound` to play it"
                    await msg.channel.send(output)
                elif cmd.groups()[0].upper().startswith("GET"):
                    url = re.search(r'GET *(HTTP[^ ]*) *(.*)', cmd.groups()[0], flags=re.IGNORECASE)
                    if url:
                        source_filename = re.search(r'/([^/]*?\.[^/]*)$', url.groups()[0]).groups()[0]
                        if url.groups()[1]:
                            source_filename = url.groups()[1] + ".mp3"
                        print("source url: {0} source filename: {1}".format(url.groups()[0], source_filename))

                        filename = "/tmp/" + source_filename
                        f = open(filename,'wb')
                        ua = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.123 Safari/537.36'
                        f.write(requests.get(url.groups()[0], headers={'User-Agent': ua}).content)
                        f.close()


                        #filename, headers = urllib.request.urlretrieve(url.groups()[0])


                        if source_filename.upper().endswith("ZIP"):
                            zf = ZipFile(filename, 'r')
                            zf.extractall('sound/')
                            zf.close()
                            os.remove(filename)
                        elif source_filename.upper().endswith("MP3"):
                            os.rename(filename, "sound/"+source_filename)

                        for s in os.listdir("sound/"):
                            if s.upper().endswith("MP3"):
                                if s != s.lower():
                                    os.rename("sound/"+s, "sound/"+s.lower())

                else:
                    await play_voice(cmd.groups()[0], cmd.groups()[1])


        # gcode/marlin search
        elif msg_content.startswith(GCODE):
            __debug(msg)
            if len(msg.content) < len(GCODE) + 2:
                await msg.channel.send(embed=__help())

            else:
                search_path = config['gcode']['path']
                search = msg.content[7:]
                output = discord.Embed(description="gcode search result for `{0}`".format(search), color=POST_COLOR)

                gcode = subprocess.check_output('grep -i '+search+' '+search_path+'* |sed \'s/:.*//\' |uniq -c |sort -r |awk \'{print $2}\' |head -n 5', shell=True).splitlines()
                for g in gcode:
                    content = open(g, "r").read()
                    desc = re.search(r'title: (.*)', content).group(1)
                    code = re.search(r'codes: \[ (.*?) ]', content).group(1)
                    link = "https://marlinfw.org/docs/gcode/{0}.html".format( re.search("b'(.*?).md'", str(g).replace(search_path,'')).group(1) )

                    output.add_field(name=code+": "+desc, value=link, inline=False)

                if output.fields:
                    await msg.channel.send(embed=output)
                else:
                    await msg.channel.send("no result found for `{0}`".format(search))
#        else:
#            await bot.process_commands(msg)


bot.run(config['discord']['token'])
