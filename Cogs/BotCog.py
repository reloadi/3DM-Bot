from discord.ext import commands
from Cogs.BotResponseHandler import BotResponseHandler

class BotCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.response_handler = BotResponseHandler()        

    async def sendResponse(self, ctx, message):
        await self.response_handler.sendResponseMessage(ctx, message)
        return self

    async def deleteCommandMessage(self, ctx):
        await self.response_handler.deleteMessage(ctx)
        return self
