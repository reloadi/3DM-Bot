import discord
from discord.ext.commands import CommandNotFound
import re
import os
import asyncio
from datetime import datetime

from countbot import CountBot
from include.debug import __debug

import configparser
config = configparser.ConfigParser()
config.read('config.cfg')

COUNTCONTROL_CHANNEL    = int(config['count_bot']['countcontrol_channel'])
COUNT_CHANNEL           = int(config['count_bot']['count_channel'])

intents = discord.Intents().all()
bot = discord.ext.commands.Bot(command_prefix='', case_insensitive=True, intents=intents)

#bot = discord.Client()
countbot = CountBot(bot)

CONECT_HELLO = False
DEBUG  = True


@bot.event
async def on_ready():
    __debug(f"on_ready - We have logged in as {bot.user}", True)
    if CONECT_HELLO:
        booted = bot.get_channel(COUNT_CHANNEL)
        await booted.send(f"I've been rebooted - v{countbot.version}")
        await booted.send(countbot.boot_screen())

@bot.event
async def on_disconnect():
    __debug('on_disconnect', True)
@bot.event
async def on_connect():
    __debug('on_connect', True)
@bot.event
async def on_resumed():
    __debug("on_resumed", True)
@bot.event
async def on_command_error(ctx, error):
    __debug(f"on_command_error: {error}", True)
    if isinstance(error, CommandNotFound):
        return
    raise error

@bot.event
async def on_message_edit(old, newmsg):
    if not old.channel.id in [ COUNT_CHANNEL ] or old.author == bot.user or newmsg.author == bot.user:
        return

    __debug(f"on_message_edit: {old.author.display_name} edited {old.content} to {newmsg.content}", True)
    await countbot.edited_msg(old, newmsg)




@bot.event
async def on_message(msg):
    if msg.author == bot.user:
        return
    if not msg.channel.id in [ COUNT_CHANNEL, COUNTCONTROL_CHANNEL ]:
        return

    # don't react to anything from a bot/hook
    if not msg.author.bot:
        if msg.channel.id in [ COUNTCONTROL_CHANNEL ]:
            __debug(msg)
            await countbot.count_control(msg)

        elif msg.channel.id in [ COUNT_CHANNEL ]:
            __debug(msg)
            await countbot.count_msg(msg)
            return



bot.run(config['count_bot']['token'])
