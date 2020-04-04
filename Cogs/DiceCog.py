import os
import random
from discord.ext import commands
from Cogs.BotCog import BotCog


class DiceCog(BotCog):

    @commands.command()
    async def roll(self, ctx, *dice: str):

        to_roll = self.parseRollRequest(dice)

        if len(to_roll) <= 0:
            await self.sendResponse(ctx, "Unkown Format. Expecting something like: 1D6")
            return

        rolls = self.rollDice(to_roll)

        if len(rolls) > 1:
            await self.sendResponse(ctx, (" + ".join("{0}".format(n) for n in rolls)) + " = "+str(sum(rolls)))
            return

        await self.sendResponse(ctx, (" + ".join("{0}".format(n) for n in rolls)))

    def parseRollRequest(self, params):
        to_roll = []
        for p in params:
            if 'd' not in p.lower():
                continue

            if p.lower().count('d') > 1:
                continue

            to_roll.append(p.lower().split('d'))

        return to_roll

    def rollDice(self, dice):
        rolls = []
        for d in dice:
            for _ in range(int(d[0])):  # num dice
                # roll dice with 1 => n sides
                rolls.append(random.choice(range(1, int(d[1])+1)))

        return rolls
