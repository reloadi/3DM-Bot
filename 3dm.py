import discord
import subprocess
import signal
import re
from datetime import datetime
from currency_converter import CurrencyConverter as CConv

from check import Check
from include.linux_color import _c as ct
from include.my_google import Google
from include.twitter import MyTwitter

#Cogs
from Cogs.DiceCog import DiceCog

import configparser
config = configparser.ConfigParser()
config.read('config.cfg')

DEBUG  = True
PREFIX = "!3DM"
GCODE  = "!GCODE"

# currency converted config
my_cur = eval(config['currency']['use'])

# used to log tweets added/posted
TRACKING_TWEETS = int(config['twitter']['tracking_channel'])
POST_COLOR      = 0xa21d1d

# used to track posted images and logged in TRACKING_IMG channel
listen_channels = eval(config['img_log']['listen_channels'])
ignore_domain   = eval(config['img_log']['ignore_domain'])
TRACKING_IMG    = int(config['img_log']['tracking_channel'])

# used to help user unable to join the server
JOIN_CHANNEL    = 689574436302880843
WELCOME_MESSAGE = "https://discordapp.com/channels/637075986726518794/637076225843527690/637108901720096770"

t = MyTwitter()

#client = discord.Client()
bot = discord.ext.commands.Bot(command_prefix='!')
bot.add_cog(DiceCog(bot))

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
    output.add_field(name="!thing some text", value="Search thingiverse (using google for now) for some text and display first result", inline=False)
    output.add_field(name="!tweet link [user]", value="Link your discord user to a twitter account for tagging when posting. If [user] is ommited, display current link", inline=False)
    output.add_field(name="!tweet unlink [user]", value="Remove link between discord account and twitter account", inline=False)
    output.add_field(name="!tweet top", value="Show top twitted members", inline=False)
    output.add_field(name="!tweet [list|delete|ID] [pos] short text (restricted)", value="Post a user's message (ID) to the twitter account.", inline=False)
    return output

# used for local debugging
def __debug(msg):
    if DEBUG:
        print("{0} {1} sent {2} in #{3}".format(ct.dark(datetime.now().strftime('%Y-%m-%d %H:%M:%S')), ct.cyan(msg.author), ct.invert(msg.content), ct.red(msg.channel)))

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
                    post_link = 'https://discordapp.com/channels/637075986726518794/{0}/{1}'.format( msg.channel.id, msg.id )
                    out_emb = discord.Embed(title="New image from: {0}".format(msg.author.display_name), 
                                            description="Sent in <#{0}> - _[original post]({2})_\n\n>>> `{1}`".format(msg.channel.id, msg.content, post_link), color=0xffffff)
                    try:
                        out_emb.set_thumbnail(url=post_url)
                    except:
                        pass
                    out_emb.set_footer(text="!tweet {0}".format(msg.id))

                    cross_post = bot.get_channel(TRACKING_IMG)
                    info = await cross_post.send(embed=out_emb)
                    emoji_delete   = discord.utils.get(bot.emojis, name='dead_cat')
                    await info.add_reaction(emoji_delete)
                    t.tdb.add_image_log(msg.id, msg.channel.id, info.id, info.channel.id)

# this print out a message to a user in the join-help channel
async def noob(msg):
    out_emb = discord.Embed(title="Welcome to 3DMeltdown".format(msg.author.display_name), 
                                description="Hi <@{0}>! This room is only to help you join the server.\n\nPlease see [this message]({1}) to join the server, you need to react to gain access.\n\nIf for some reason, you can't join, please tag the mod using\n`@mod your message` someone should be able to help.".format(msg.author.id, WELCOME_MESSAGE), color=POST_COLOR)
    out_emb.set_footer(text="This message (and yours) will self-delete in 12 hours".format(msg.id))
    id = await msg.channel.send(embed=out_emb)
    await id.delete(delay=43200)
    await msg.delete(delay=43200)

    return True

@bot.event
async def on_ready():
    print('We have logged in as {0.user}'.format(bot))

@bot.event
async def on_raw_reaction_add(payload):
    if payload.user_id == bot.user.id:
        return

    # monitor the image log channel, if someone hit a reaction, remove it from channel
    if payload.channel_id in [TRACKING_IMG, JOIN_CHANNEL] and payload.emoji.name in ["dead_cat", "corona"]:
        t.tdb.del_image_log(payload.message_id, payload.channel_id)
        cross_post = bot.get_channel(payload.channel_id)
        image_post = await cross_post.fetch_message(payload.message_id)
        await image_post.delete()
        
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
        if "ANUS" in msg_content or re.search("ANAL(?!I|Y|O)", msg_content):
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
                roles   = [y.name.lower() for y in msg.author.roles]
                allowed = eval(config['twitter']['allowed_roles'])
                # Check if user is allowed to use this command
                if any( True for x in allowed if x in roles ) or sub_msg.startswith("TOP") or sub_msg.startswith("LINK") or sub_msg.startswith("UNLINK") or sub_msg.startswith("SHOW"):
                    emoji_twitter   = discord.utils.get(bot.emojis, name='twitter')
                    emoji_3dm       = discord.utils.get(bot.emojis, name='3dm2')
                    delete_post     = True
                    if sub_msg.startswith("LIST"):
                        out_msg += "DB contain {0} entry. Displaying lastest 5.".format(t.count())
                        for i in t.tdb.get_all():
                            out_msg += "```{0}\n```".format(i)
                        if not out_msg:
                            out_msg = "DB is empty"
                    elif sub_msg.startswith("DELETE"):
                        id = re.search('^ *(\d+)', msg.content[14:]).group(1)
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
                        gs = re.search('^ *(\d+) *(\d)? +(.*)', msg.content[7:]).groups()
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
                                        att = re.search('(http[^ ]+)', post_msg.content)
                                        # link was found
                                        if att:
                                            post_url = att.groups()[0]
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
                                        post_link = 'https://discordapp.com/channels/637075986726518794/{0}/{1}'.format( msg.channel.id, post_msg.id )
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

            cmd = re.search('^.CONVERT *([\.\d]+) *(.*)', msg_content)
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
                g = Google(**config['google']);

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
                    # emoji = discord.utils.get(bot.emojis, name='twitter')
                    # if emoji:
                    #     await msg.add_reaction(emoji)
                    # emoji = discord.utils.get(bot.emojis, name='3dm2')
                    # if emoji:
                    #     await msg.add_reaction(emoji)
                    output = "test cmd\nCommand trigger: {0}\nChannel: {1}".format(PREFIX, msg.channel)
                elif cmd[1] == "disboard":
                    check = Check("3DMeltdown 3D Printing")
                    check.load()
                    output = "Current ranking:\n"
                    for i in range(5):
                        output += "{0} - {1} ({2})\n".format(i+1, check.index_list[i], check.index_time[i])
                    output += "Last change: {1}\n".format(check.index_first, check.delta())
                else:
                    output = "unknown cmd: {0}".format(cmd[1])

                await msg.channel.send(output)

        # useless unit conversion
        elif msg_content.startswith("!MMS"):
            cmd = re.search('^!MMS *([\.\d]+)', msg_content)
            if cmd:
                nb = float(cmd.groups()[0])
                output = discord.Embed(description="American conversion: `{0:0.2f}` (mm/sec)".format(nb), color=POST_COLOR)
                output.add_field(name="inch/sec", value="{0:0.5f}".format(nb / 25.4), inline=True)
                output.add_field(name="foot/sec", value="{0:0.5f}".format(nb/305), inline=True)
                output.add_field(name="mph", value="{0:0.5f}".format(nb/447), inline=True)
                await msg.channel.send(embed=output)

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
                    desc = re.search('title: (.*)', content).group(1)
                    code = re.search('codes: \[ (.*?) ]', content).group(1)
                    link = "https://marlinfw.org/docs/gcode/{0}.html".format( re.search("b'(.*?).md'", str(g).replace(search_path,'')).group(1) )

                    output.add_field(name=code+": "+desc, value=link, inline=False)

                if output.fields:
                    await msg.channel.send(embed=output)
                else:
                    await msg.channel.send("no result found for `{0}`".format(search))


bot.run(config['discord']['token'])