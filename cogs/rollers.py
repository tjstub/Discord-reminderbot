from discord.ext import commands
from collections import Counter
from random import randint

# TODO: This is just a quick solution. For fun, we should write our own.
import xdice


class Rollers(commands.Cog):
    """
    This cog implements dice rollers for various systems.
    """

    @commands.command(name="mb")
    async def mistborn_roller(self, ctx, *, die_pool: str = ""):
        """
        This implements the dice system for the Mistborn RPG system.

        Attribution: This code is borrowed (with small modification)
        from https://github.com/3digitdev/discord-dicebot under the
        terms of GPLv3.
        """

        extra = "\n"
        pool = int(die_pool.strip())
        # Anything over 10 die gets converted into a nudge instead.
        if pool > 10:
            nudges = pool - 10
            pool = 10
            extra = (
                f"**NOTE:** Dice pool above 10 -- Rolling 10 dice instead.  "
                f"**Granting {nudges} extra Nudges** (_reflected below_)"
            )
        else:
            nudges = 0
            if pool < 2:
                pool = 2
                extra = (
                    f"**NOTE:** Dice pool below 2 -- Rolling 2 dice instead.  "
                    f"**Outcome worsens by 1 level!**"
                )
        # The result of a roll is anywhere between 1-5. Sixes are instead
        # counted as Nudges.
        rolls = sorted([randint(1, 6) for _ in range(pool)])
        frequency = Counter(rolls)
        nudges += frequency.pop(6)
        try:
            # You need a pair of values in order for it to count as a
            # result.
            result = max([k for k in frequency.keys() if frequency[k] > 1])
        except ValueError:
            result = 0

        await ctx.send(
            (
                f"{extra}\n"
                f"{ctx.author.nick} is rolling {pool} dice:\n"
                "```Markdown\n"
                f"{rolls}\n"
                "```\n"
                f"**Result:**  `{result}`\n"
                f"**Nudges:**  `{nudges}`\n"
            )
        )

    @commands.command(name="r")
    async def poly_roll(self, ctx, *, expression: str):
        result = xdice.roll(expression.strip())
        extra = "\n"

        await ctx.send(
            (
                f"{extra}\n"
                f"{ctx.author.nick} is rolling {expression.strip()}\n"
                "```\n"
                f"{result.format()}\n"
                "```\n"
                f"**Result:** `{str(result)}`\n"
            )
        )
