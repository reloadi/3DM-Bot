class BotResponseHandler():
    def __init__(self,send_dm_responses=False):
        self.send_dm_responses = send_dm_responses        

    def setSendDMResponses(self,send_dm_responses):
        self.send_dm_responses=send_dm_responses
        return self

    async def sendResponseMessage(self, ctx, message):      
        if self.send_dm_responses:
            return  await self._sendDMToUser(ctx,message)
        else:
            return await self._sendChannelResponse(ctx,message)

    async def _sendChannelResponse(self,ctx,message):
        return await ctx.send(message)

    async def _sendDMToUser(self, ctx, message):
        if ctx.author.dm_channel is None:            
            await ctx.author.create_dm()

        await ctx.author.dm_channel.send(message)

    async def deleteMessage(self, ctx):
        await ctx.message.delete(delay=5)
        return self