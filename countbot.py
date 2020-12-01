import discord
import re
import os
import sqlite3
import random
from datetime import datetime
import humanize
import random
import configparser

from fuzzywuzzy import fuzz

COUNTBOT_VERSION = "0.1.43"

config = configparser.ConfigParser()
config.read('config.cfg')

POST_COLOR      = 0xa21d1d

KICK_REPOST = 0
KICK_MATH   = 1
KICK_BAD    = 2
KICK_EDIT   = 3

KICK_BADACT = 4

KICK_NOTLAST= 5
KICK_NOBAL  = 6

KICK_BADKICK = 7
KICK_GOODKICK = 8

ACTION_LIST =   { 
                'd': 5, # DUPE action
                'k': 50, # KICK action
                }

class CountBot():
    def __init__(self, bot, start=0):
        self.version = COUNTBOT_VERSION
        self.bot = bot                      # the bot itself
        self.DEBUG = 0

        # misc configurations for count flow
        self.allow_duplicate = False
        self.auto_clean = True
        self.auto_clean_delay = 10
        self.direction = 1
        self.auto_stats = True
        self.auto_stats_delay = 50

        self.control_channel = int(config['count_bot']['countcontrol_channel'])

        if not os.path.exists(config['count_bot']['localdb']):
            self.mprint("db doesn't exist -- creating")
            self.init_db(config['count_bot']['localdb'])
        self.conn = sqlite3.connect(config['count_bot']['localdb'], detect_types=sqlite3.PARSE_DECLTYPES | sqlite3.PARSE_COLNAMES)
        if self.DEBUG:
            self.conn.set_trace_callback(print)

    # core count system
    async def count_msg(self, msg):
        self.mprint(f"msg_content {msg.content}",2)
        bonus_score = 0

        # check if message is numbers
        snb = re.search(r'^(-?[\d\(\)\+\-\*\/\^ ]+) ?([\w])?$', msg.content)
        if snb:
            self.mprint(f"in snb received count: {snb.group(1)}")
            # make sur the game is started
            if self.started(msg):
                self.mprint(f"snb - it's stated started {snb.group(1)}")
                try:
                    nb = eval(snb.group(1).replace('^', '**').replace(' ', ''))
                except:
                    nb = -99999

                self.mprint(f"after eval: {nb}")
                # check if number is valid
                (nextnb, last_counter) = self.next(msg)
                if nb == nextnb:
                    self.mprint("snb - it's stated started - next")
                    user_action = {}

                    # check if an action was used
                    if snb.group(2):
                        user_action = await self.action(msg, snb.group(2), last_counter)

                    self.mprint(f"snb - it's stated started - user_action: {user_action}")


                    # make sure it's not a dupe (unless allowed)
                    if 'kick' not in user_action.keys() \
                            and (self.allow_duplicate \
                                    or (not self.allow_duplicate and last_counter != msg.author.id) \
                                    or (not self.allow_duplicate and last_counter == msg.author.id and 'd' in user_action.keys())):
                        self.mprint("snb - it's stated started - next - number is good")
                        # we're good, add the count
                        score = self.score_msg(msg, nb)
                        self.db_add_count(msg, 1, score)
                        if score > 5:
                            gj = discord.utils.get(self.bot.emojis, name='countbot')
                            self.mprint(f"snb - high score entry - adding reaction {gj}")
                            await msg.add_reaction(gj)

                        self.mprint("snb - it's stated started - next - number is good - done adding number")

                        # if auto-stats if on and we reached the limit, send some stats
                        if self.auto_stats and self.db_get_count(msg, 1) % self.auto_stats_delay == 0:
                            self.mprint("snb - it's stated started - next - number is good - sending autostats")
                            await msg.channel.send(self.stats(msg))

                    # user tried to use action but failed, kick him
                    elif 'kick' in user_action.keys():
                        self.db_add_count(msg, 0)
                        await msg.channel.send(self.get_msg(msg, user_action['kick']))
                        await self.kick(msg)
                        await msg.delete(delay=1)


                    # user trying to double-post, kick him
                    else:
                        self.db_add_count(msg, 0)
                        await msg.channel.send(self.get_msg(msg, KICK_REPOST))
                        await self.kick(msg)
                        await msg.delete(delay=1)

                # user can't count, kick him 
                else:
                    self.db_add_count(msg, 0)
                    await msg.channel.send(self.get_msg(msg, KICK_MATH))
                    await self.kick(msg)
                    await msg.delete(delay=1)

            # gane ins't stated
            else:
                id = await msg.channel.send(f"<@{msg.author.id}> - dafuq? it's not even started.. Not booting you")
                await msg.delete(delay=1)
                await id.delete(delay=self.auto_clean_delay)


        # check for commands
        else:
            # check for action request
            isaction = await self.check_action(msg)

            # if not, check for commands
            clean_bot = False
            if not isaction: 
                clean_bot = await self.check_command(msg)

            if not clean_bot and not isaction: # not something we understand, assume the worst and nuke him
                self.db_add_count(msg, 0)
                await msg.channel.send(self.get_msg(msg, KICK_BAD))
                await self.kick(msg)

            if self.auto_clean: # delete message
                await msg.delete(delay=self.auto_clean_delay)
                if clean_bot:
                    await clean_bot.delete(delay=self.auto_clean_delay)

    async def check_command(self, msg):
        clean_bot = False
        msg_content = msg.content.upper()
        if msg_content.startswith("POS"):
            clean_bot = await msg.channel.send(self.stats(msg))
        elif msg_content.startswith("HELP"):
            clean_bot = await msg.channel.send(embed = self.help(msg))
        elif msg_content.startswith("DEB"):
            if self.DEBUG:
                self.conn.set_trace_callback(False)
                self.DEBUG = 0
            else:
                self.conn.set_trace_callback(print)
                self.DEBUG = 9
            clean_bot = await msg.channel.send(f"DEBUG: {self.DEBUG}")
        elif msg_content.startswith("VERSION"):
            clean_bot = await msg.channel.send(f"Current version: {self.version}")
        elif msg_content.startswith("DUP"):
            if self.allow_duplicate == True:
                self.allow_duplicate = False
            else:
                self.allow_duplicate = True
            clean_bot = await msg.channel.send(f"Allow duplicate: {self.allow_duplicate}")
        elif msg_content.startswith("DIR"):
            changedir = re.search(r"DIR *([+-]?\d+)", msg_content)
            if changedir:
                self.direction = eval(changedir.group(1))
            await msg.channel.send(f"current direction: {self.direction}")
        elif msg_content.startswith("LEAD"):
            sgood = self.db_get_leader(msg)
            pos=1
            desc=""
            for item in sgood:
                desc += "#{0:>02} **{1}** - {2} pts (life: {3} used: {4})\n".format(pos, self.getName(msg, item[0]), int(item[1])-int(item[2]), item[1], item[2])
                pos += 1

            if desc:
                out_emb = discord.Embed(title="top leader counter for current round",
                                            description=desc)
                clean_bot = await msg.channel.send(embed=out_emb)
        elif msg_content.startswith("TOP"):
            sgood = self.db_get_top(msg, 1)
            pos=1
            desc=""
            for item in sgood:
                desc += "#{0:>2} **{1}** - with {2} counts\n".format(pos, self.getName(msg, item[0]), item[1])
                pos += 1
            if desc:
                out_emb = discord.Embed(title="top counter for current round",
                                            description=desc + f"\nTotal count: {self.db_get_count(msg, 1)}")
                clean_bot = await msg.channel.send(embed=out_emb)
        elif msg_content.startswith("FAIL"):
            sgood = self.db_get_top(msg, 0)
            desc = ""
            pos = 1
            for item in sgood:
                desc += "#{0:>2} **{1}** - with {2} fails\n".format(pos, self.getName(msg, item[0]), item[1])
                pos += 1
            if len(desc) > 1:
                out_emb = discord.Embed(title="top loser for current round",
                                            description=desc + f"\nTotal fails: {self.db_get_count(msg,0)}")
                clean_bot = await msg.channel.send(embed=out_emb)
        elif msg_content.startswith("START"):
            if self.start(msg):
                await msg.channel.send(f"```diff\n- New count started```\n"\
                                f"```Direction: {self.direction}\n"\
                                f"Auto-clean: {self.auto_clean} ({self.auto_clean_delay} sec)\n"\
                                f"Auto-stats: {self.auto_stats} ({self.auto_stats_delay} sec)\n"\
                                f"Allow duplicate: {self.allow_duplicate}\n"\
                                f"Next number: {self.next(msg)}```")
            else:
                clean_bot = await msg.channel.send(f"nope.. can't do that.. there's already a game running")
            
        return clean_bot

    async def count_control(self, msg):
        roles   = [y.name.lower() for y in msg.author.roles]
        #self.mprint(f"msg sent: {msg}\n")
        if re.match( r"I CAN.T COUNT" , msg.content.upper() ):
            #self.mprint(f"it matches I can't count RE\n")
            if "icantcount" in roles:
                #self.mprint(f"user has icantcount role\n")
                desc = ""
                ran = random.randrange(5)
                if ran == 0:
                    desc = "You got lucky this time.."
                else:
                    desc = "Using a very advanced random(5) algorithm, I have decided that I won't give you back the role this time.. Feel free to retry."


                out_emb = discord.Embed(title="so.. you can't count uh?", description=desc, color=POST_COLOR)
                #out_emb.set_footer(text="This message will self-delete in 30 sec. Yours in 12 hours")
                id = await msg.channel.send(embed=out_emb)
                await id.delete(delay=30)
                if ran == 0:
                    await msg.author.remove_roles(discord.utils.get(msg.author.guild.roles, name="icantcount"))
                    await msg.author.add_roles(discord.utils.get(msg.author.guild.roles, name="3DMCounter"))

                await msg.delete(delay=900)
            #else:
                #self.mprint(f"user doesnt have icantcount role\n")

        else:
            #self.mprint(f"doesn't match i can't count\n")
            await msg.delete()

        return True

    async def check_action(self, msg):
        self.mprint("| in check_action",2)
        action = False
        dokick = False

        kick = re.search(r"^kick <@!(.+)>$", msg.content, re.IGNORECASE)
        if kick:
            action = True
            self.mprint(f"+ in check_action kick request {kick.group(1)}",2)
            if self.db_user_in_last(msg, kick.group(1), 20)[0]:
                if self.db_add_action(msg, 'k', ACTION_LIST['k']):
                    await msg.channel.send(self.get_msg(msg, KICK_GOODKICK, f"<@!{kick.group(1)}>", ACTION_LIST['k']))
                    await self.kick(msg, kick.group(1))
                else:
                    dokick = KICK_NOBAL
            # not a valid request, KICK!
            else:
                dokick = KICK_BADKICK

        if dokick:
            await msg.channel.send(self.get_msg(msg, dokick))
            await self.kick(msg)
            await msg.delete(delay=1)

        return action

    def help(self, msg):
        return discord.Embed(title="count-bot help",
                                description="The goal is simple: just count.\n"\
                                            "ANY valid count will give you 1 point.\n\n"\
                                            "You can earn extra points by using math. Valid caracters are:\n"\
                                            "`0-9 ( ) + - * / ^ **`\n\n"\
                                            "- Usage of +, - or () gives 1 pt each\n"\
                                            "- Usage of * or / gives 2 pts each\n"\
                                            "- Usage of ^ or ** gives 5 pts each\n"\
                                            "- + - * / ^ with 0 or 1 are ignored\n"\
                                            "- Max of 2 scoring per type per count\n"\
                                            "- No current position in formula\n"\
                                            "- > 30% formula differnce for math bonus\n\n"\

                                            "valid commands:\n"\
                                            "```top, lead, fail, pos, help, version```\n\n"\
                                            "valid action:\n"\
                                            "```d (5 pts):\n"\
                                            "allow you to multiple-post in a row\n"\
                                            "   exemple: 600 d```\n"\
                                            "```kick (50 pts):\n"\
                                            "allow you to kick someone from the count. User must have a count in previous 20.\n"\
                                            "   exemple: kick @puro```\n"\
                                            )

    def start(self, msg):
        self.mprint("in start",2)
        if self.db_start(msg):
            self.mprint("there's a game running")
            self.__started = datetime.now()
            return True
        else:
            self.mprint("no game running")
            return False

    def started(self, msg):
        self.mprint("in started",2)
        return self.db_get_game(msg)

    def getName(self, msg, memberid):
        return self.bot.get_guild(msg.author.guild.id).get_member(memberid).display_name

    def stats(self, msg):
        self.mprint("in start",2)
        game = self.started(msg)
        tmps = ""
        if game:

            sleader = self.db_get_leader(msg)[0]
            sgood = self.db_get_top(msg, 1)[0]
            sbad = self.db_get_top(msg, 0)[0]


            last_post = self.db_get_pos(msg)
            last_post_time = humanize.naturaltime(datetime.now() - last_post[2])

            tmps = humanize.naturaltime(datetime.now() - game[1])
            tmpnext = self.next(msg)
            tmps =  f"```diff\n- current round stats (auto-stats) (version {self.version}) ``````"\
                    f"Auto-clean: {self.auto_clean} ({self.auto_clean_delay} sec)\n"\
                    f"Auto-stats: {self.auto_stats} ({self.auto_stats_delay} counts)\n"\
                    f"Allow duplicate: {self.allow_duplicate}\n"\
                    f"Started: {tmps}\n"\
                    f"Total count: {self.db_get_count(msg, 1)}\n"\
                    f"Total fail: {self.db_get_count(msg, 0)}\n"\
                    f"Top leader: {self.getName(msg, sleader[0])} ({sleader[1]} points)\n"\
                    f"Top counter: {self.getName(msg, sgood[0])} ({sgood[1]} counts)\n"\
                    f"Worst counter: {self.getName(msg, sbad[0])} ({sbad[1]} fails)\n"\
                    f"Direction: {self.direction}\n"\
                    f"Last counter: {self.getName(msg, last_post[1])} ({last_post_time})\n"\
                    f"Current number: {last_post[0]}\n"\
                    f"Next number: {self.next(msg)[0]}"\
                    f"```\ncommand: pos, lead, top, fail, help\nsee <#732365559647174736> to gain/regain access"
        else:
            self.mprint("no game found",3)
            tmps = "No game stated."
        
        return tmps

    async def action(self, msg, act, last_counter):
        self.mprint(f"| in action action: {act} last_counter: {last_counter}",2)

        this_action = {}
        # make sure it's valid
        if act in ACTION_LIST.keys():
            self.mprint(f"+ in action action: action is valid",3)
            if act == 'd':
                # make sure it's needed
                if last_counter == msg.author.id:
                    self.mprint(f"+ in action action DUPE: action is valid",3)
                    # try making action
                    if self.db_add_action(msg, act, ACTION_LIST[act]):
                        gj = discord.utils.get(self.bot.emojis, name='countbot')
                        await msg.add_reaction(gj)

                        self.mprint(f"+ in action action DUPE: action is valid action successful ",3)
                        this_action[act] = True
                        self.mprint(f"+ in action action DUPE: action is valid action successful this_action: {this_action}",3)
                    # Nope, user can't do that, kick
                    else:
                        self.mprint(f"+ in action action DUPE: action is valid but user has no balance ",3)
                        this_action['kick'] = KICK_NOBAL

                # dumbass had me check, kick him
                else:
                    this_action['kick'] = KICK_NOTLAST
        # unknown action, kick
        else:
            this_action['kick'] = KICK_BADACT
        
        return this_action

    def next(self, msg):
        tmp = self.db_get_pos(msg)
        return (tmp[0] + self.direction, tmp[1] )

    def get_msg(self, msg, msgType, p1="", p2=""):
        msg = [ 
                [
                    f"<@{msg.author.id}> - KICKED: you're not alone buddy.. _(join me <#{self.control_channel}>)_",
                    f"<@{msg.author.id}> - slow down dude! _(join me <#{self.control_channel}>)_",
                    f"<@{msg.author.id}> - double-post not allowed, **KICKED** _(join me <#{self.control_channel}>)_",
                ],
                [
                    f"<@{msg.author.id}> - BOOTED: math is hard uh? _(see <#{self.control_channel}>)_",
                    f"<@{msg.author.id}> - Previous post + {self.direction} shouldn't be that hard **BOOTED** _(see <#{self.control_channel}>)_",
                    f"<@{msg.author.id}> - **BOOTED** for not following the count _(see <#{self.control_channel}>)_",
                    f"**BOOTING** <@{msg.author.id}> - You can't just send random numbers _(see <#{self.control_channel}>)_",
                ],
                [
                    f"<@{msg.author.id}> not a valid number dumbass _(see <#{self.control_channel}>)_",
                    f"<@{msg.author.id}> I don't know what you posted _(see <#{self.control_channel}>)_",
                    f"<@{msg.author.id}> Math expressions only _(see <#{self.control_channel}>)_",
                ],
                [
                    f"KICKING <@{msg.author.id}> - attempted at messing up the count  _(see <#{self.control_channel}>)_",
                    f"<@{msg.author.id}> - editing messages uh? **KICK** _(see <#{self.control_channel}>)_",
                ],
                [
                    f"<@{msg.author.id}> - tried to use non-existing action **BYE**  _(see <#{self.control_channel}>)_",
                    f"**KICK** <@{msg.author.id}> - trying to hack the count? This one doesn't work  _(see <#{self.control_channel}>)_",
                    f"<@{msg.author.id}> - Bad action, goodbye! _(see <#{self.control_channel}>)_",
                ],
                [
                    f"Dude.. <@{msg.author.id}> action is good but you're not last **KICK**  _(see <#{self.control_channel}>)_",
                    f"<@{msg.author.id}> - you're not even last.. you had me check pff.. **BOOM**  _(see <#{self.control_channel}>)_",
                    f"That's kinda dumb trying to waste an action <@{msg.author.id}> **BOOTED** _(see <#{self.control_channel}>)_",
                ],
                [
                    f"**KICKING** <@{msg.author.id}> not enough points to do that!  _(see <#{self.control_channel}>)_",
                    f"<@{msg.author.id}> - you're too poor for that.. **KICK**  _(see <#{self.control_channel}>)_",
                    f"Nice try <@{msg.author.id}> I do check, not enought points **BOOTED** _(see <#{self.control_channel}>)_",
                ],
                [
                    f"<@{msg.author.id}> Trying to kick a user who didn't post recently uh?  **NOPE** _(see <#{self.control_channel}>)_",
                    f"**KICK** <@{msg.author.id}> - That user didn't post ^^ _(see <#{self.control_channel}>)_",
                    f"Nice try <@{msg.author.id}> The user has to be active rencently! **BYE** _(see <#{self.control_channel}>)_",
                ],
                [
                    f"<@{msg.author.id}> Performed **KICK** action on {p1} for {p2} pts  _(see <#{self.control_channel}>)_",
                    f"KICK by <@{msg.author.id}> - See ya {p1} (cost: {p2} pts) _(see <#{self.control_channel}>)_",
                ]
            ]
        return random.choice(msg[msgType])

    def score_msg(self, msg, nb):
        self.mprint(f"| in score_msg: {msg.content} - with {nb}",2)
        nb_basic1 = 0
        nb_basic2 = 0
        nb_basic3 = 0
        score = 1
        ratio = 0

        # check previous post from user
        prev = self.db_get_pos(msg, msg.author.id)
        if prev[0]:
            self.mprint(f"+ in score_msg: previous post: {prev[3]}",2)
            self.mprint(f"+ in score_msg: current  post: {msg.content.replace('^', '**')}",2)
            ratio = fuzz.ratio(msg.content.replace('^', '**'), prev[3])
            self.mprint(f"+ in score_msg: {ratio}% similar",2)

        val = msg.content.replace('**', '^')
        if ratio < 70 and not re.search('^\d+$', val) and not re.search('[\^\*\/][01]', val) and not re.search(str(int(nb)), val):
            val = re.sub('[\^\+\-\/][01]', '', val).replace('((', '(')

            for ch in val:
                if ch in [ '+', '-', '(' ] and nb_basic1 < 2:
                    score+=1
                    nb_basic1+=1
                elif ch in [ '*', '/'] and nb_basic2 < 2:
                    score+=2
                    nb_basic2+=1
                elif ch == '^' and nb_basic3 < 2:
                    score+=5
                    nb_basic3+=1

        self.mprint(f"+ in score_msg score: {score}",2)
        return score

    def boot_screen(self):
        return "Commands: `pos, fail, top, lead, help`\n"\
                    "Valid characters: `0-9 ( ) + - * / ^ **`\n"\
                    "```v0.1.42\n"\
                    "- CHANGE: min point for valid count is now 1 pt\n"\
                    "- NEW first draft action system\n"\
                    "    action 'd': use 5 pts to re-post (ex: 954 d)\n"\
                    "v0.1.43\n"\
                    "- action 'kick': kick someone (50pt) (ex: kick @puro)\n"\
                    "- new command: help\n"\
                    "```"
                    # "- First draft of scorring system (v0.1.35):\n"\
                    # "    Usage of +, - or () gives 1 pt each\n"\
                    # "    Usage of * or / gives 2 pts each\n"\
                    # "    Usage of ^ or ** gives 5 pts each\n"\
                    # "    +1/-1/*1//1/^1 are ignored\n"\
                    # "    Max of 2 scoring per type per count\n"\
                    # "- Reaction added for 5pt+ counts\n"\
                    # "- New command: leader (v0.1.38)\n"\
                    # "- fixed a bug in random response (v0.1.39)\n"\
                    # "- Reaction for high scorring counts increased to 7pt+ (v0.1.39)\n"\
                    # "- Added top leader to pos output (v0.1.39)\n"\
                    # "- Usage of ^, * and / with 0 or 1 auto gives 0 pt (v0.1.39)\n"\
                    # "v0.1.40\n"\
                    # "- fixed some floating points output\n"\
                    # "- Usage of current position in a formula auto gives 0 pt\n"\

    async def kick(self, msg, id_user=False):
        member = msg.author
        if id_user:
            member = self.bot.get_guild(msg.author.guild.id).get_member(int(id_user))
        await member.add_roles(discord.utils.get(msg.author.guild.roles, name="icantcount"))
        await member.remove_roles(discord.utils.get(msg.author.guild.roles, name="3DMCounter"))

    async def edited_msg(self, old, new):
        await old.channel.send(self.get_msg(old, KICK_EDIT))
        await self.kick(old)

    def db_start(self, msg):
        self.mprint("| in db_start",2)
        # check if there's a running game
        if self.db_get_game(msg):
            self.mprint("+- game found",3)
            return True
        # we're go, create a game
        else:
            self.mprint("+- creating new game",3)
            c = self.conn.cursor()
            c.execute('insert into games (id_server, id_channel, starttime, id_user) values (?, ?, datetime("now", "localtime"), ?)', 
                            (msg.author.guild.id, msg.channel.id, msg.author.id))
            id = c.lastrowid
            self.conn.commit()
            self.mprint(f"+- new game id: {id}")
            return id

    def db_get_pos(self, msg, id_user=False):

        sql_user = ""
        if id_user:
            sql_user = f" and counts.id_user = {id_user}"

        self.mprint(f"| in db_get_pos",2)
        entry = self.conn.execute("select entry, id_user, entrytime from counts where id_count = ( "\
                                        "select max(id_count) "\
                                        "from counts "\
                                        "inner join games on games.id_game = counts.id_game "\
                                            "and games.id_server= ? "\
                                            "and games.id_channel = ? "\
                                            "and games.endtime is NULL "\
                                        f"where good = 1 {sql_user})", 
                                        (msg.author.guild.id, msg.channel.id, )).fetchone()
        if entry:
            self.mprint(f"+- found pos: {entry[0]}", 3)
            return (int(eval(entry[0])), int(entry[1]), datetime.strptime(entry[2], '%Y-%m-%d %H:%M:%S'), entry[0])
        else:
            self.mprint(f"+- ERR: no game found",3)
            return (0,)

    def db_get_count(self, msg, good):
        self.mprint(f"| in db_get_count",2)
        nbcount = self.conn.execute("select count(id_count) from counts "\
                                        "inner join games on games.id_game = counts.id_game " \
                                            "and games.id_server = ? " \
                                            "and games.id_channel = ? " \
                                            "and games.endtime is null " \
                                        "where good = ?",   (msg.author.guild.id, msg.channel.id, good, )).fetchone()
        if nbcount:
            return nbcount[0]
        else:
            return 0

    def db_get_top(self, msg, good, limit=10):
        tmpg = self.db_get_game(msg)
        top = False
        if tmpg:
            top = self.conn.execute("select id_user, count(entry) from counts where id_game = ? and good = ? group by id_user order by 2 desc limit ?", 
                                    (tmpg[0], good, limit, )).fetchall()
        return top

    def db_user_in_last(self, msg, id_user, limit=20):
        self.mprint(f"| in db_user_in_last",2)
        return self.conn.execute("select count(id_count) "\
                                    "from counts "\
                                    "inner join games on games.id_game = counts.id_game "\
                                        "and games.id_server= ? "\
                                        "and games.id_channel = ? "\
                                        "and games.endtime is NULL "\
                                    f"where counts.id_user = ?"\
                                    "and id_count > (select min(id_count) "\
                                                "from (select id_count "\
                                                        "from counts where good = 1 order by id_count desc limit ?)) ", 
                                        (msg.author.guild.id, msg.channel.id, id_user, limit, )).fetchone()

    def db_get_leader(self, msg, id_user=False):
        self.mprint(f"| in db_get_leader",2)

        sql_user = ""
        if id_user:
            self.mprint(f"+ in db_get_leader using id_user: {id_user}",2)
            sql_user = f"and counts.id_user = {id_user} "

        return self.conn.execute("select counts.id_user, sum(score) as tscore, "\
                                        "(select case when sum(actions.points) is null then 0 else sum(actions.points) end "\
                                            "from actions where actions.id_game=counts.id_game and actions.id_user=counts.id_user) as taction "\
                                    "from counts "\
                                    "inner join games on games.id_game = counts.id_game "\
                                        "and games.id_server= ? "\
                                        "and games.id_channel = ? "\
                                        "and games.endtime is NULL "\
                                    f"where 1=1 {sql_user}"\
                                    "group by counts.id_user "\
                                    "having tscore - taction > 0 "\
                                    "order by tscore - taction desc "\
                                    "limit 10", (msg.author.guild.id, msg.channel.id, )).fetchall()

    def db_add_count(self, msg, valid, score=0):
        self.mprint(f"| in db_add_count",2)
        # removing commands and replacing ^ with **
        msg_content = re.sub(' [a-zA-Z]$', '', msg.content).replace('^', '**')
        
        self.conn.execute("insert into counts (id_game, id_user, entrytime, entry, good, score) values "\
                            "( (SELECT id_game FROM games WHERE id_server = ? AND id_channel = ? AND endtime is NULL) , ?, datetime('now', 'localtime'), ?, ?, ?)", 
                                    (msg.author.guild.id, msg.channel.id, msg.author.id, msg_content, valid, score))
        self.conn.commit()

    def db_get_game(self, msg):
        # get the current id_game from the DB using the current context
        self.mprint(f"in db_get_game {msg.author.guild.id} -- {msg.channel.id}", 2)
        id_game = self.conn.execute("SELECT id_game, starttime FROM games WHERE id_server = ? AND id_channel = ? AND endtime is NULL", 
                                (msg.author.guild.id, msg.channel.id, )).fetchone()
        self.mprint(f"id_game: {id_game}",3)
        if id_game:
            self.mprint(f"found the id_game: {id_game[0]}",3)
            return (int(id_game[0]), datetime.strptime(id_game[1], '%Y-%m-%d %H:%M:%S'))
        else:
            return False

    def db_get_points(self, msg):
        self.mprint(f"| in db_get_points",2)
        points = self.conn.execute("select sum(counts.score), "\
                                        "(select case when sum(actions.points) is null then 0 else sum(actions.points) end "\
                                            "from actions where actions.id_game=counts.id_game and actions.id_user=counts.id_user) "\
                                    "from counts  " \
                                    "inner join games on games.id_game = counts.id_game " \
                                        "and games.id_server = ? " \
                                        "and games.id_channel = ? " \
                                        "and games.endtime is null " \
                                    "where counts.id_user = ?",   (msg.author.guild.id, msg.channel.id, msg.author.id, )).fetchone()
        if points:
            self.mprint(f"+ in db_get_points found points: {points[0]} used: {points[1]}",3)
            return (int(points[0]) - int(points[1]), int(points[0]), int(points[1]),)
        else:
            self.mprint(f"+ in db_get_points no points found",3)
            return False

    def db_add_action(self, msg, action_type, points):
        self.mprint(f"| in db_add_action action_type: {action_type} points: {points}",2)
        added = False
        balance = self.db_get_points(msg)
        if balance:
            if balance[0] >= int(points):
                self.mprint(f"+ in db_add_action user has enough to use action",2)
                self.conn.execute("insert into actions (id_game, id_user, actiontime, action_type, points) values "\
                                    "( (SELECT id_game FROM games WHERE id_server = ? AND id_channel = ? AND endtime is NULL) , ?, datetime('now', 'localtime'), ?, ?)", 
                                            (msg.author.guild.id, msg.channel.id, msg.author.id, action_type, points))
                self.conn.commit()
                added = True
        return added

    def init_db(self, dbpath):
        self.conn = sqlite3.connect(dbpath)
        self.conn.execute("CREATE TABLE counts ("\
                            "id_count INTEGER PRIMARY KEY AUTOINCREMENT,"\
                            "id_game  INTEGER NOT NULL,"\
                            "id_user INTEGER NOT NULL,"\
                            "entrytime TEXT NOT NULL,"\
                            "entry TEXT,"\
                            "good INTEGER DEFAULT 0, "\
                            "score INTEGER DEFAULT 0);")
        self.conn.execute("CREATE TABLE games ("\
                            "id_game INTEGER PRIMARY KEY AUTOINCREMENT,"\
                            "id_server INTEGER NOT NULL,"\
                            "id_channel INTEGER NOT NULL,"\
                            "starttime TEXT NOT NULL,"\
                            "id_user INTEGER NOT NULL,"\
                            "endtime TEXT);")
        self.conn.execute("CREATE TABLE actions ("\
                            "id_action INTEGER PRIMARY KEY AUTOINCREMENT,"\
                            "id_game INTEGER NOT NULL,"\
                            "id_user INTEGER NOT NULL,"\
                            "actiontime TEXT NOT NULL,"\
                            "action_type TEXT NOT NULL,"\
                            "action_param TEXT,"\
                            "points INTEGER NOT NULL);")
        self.conn.commit()
        self.conn.close()

    def mprint(self, txt, lvl=1):
        if lvl <= self.DEBUG:
            print(f"*** {txt}")

