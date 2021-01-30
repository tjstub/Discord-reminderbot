from discord.ext import commands, tasks
import datetime
import os
import logging


class Attendance(commands.Cog):
    """
    This cog implements some rudimentary features for automatically implementing
    reminders and tracking a week's attendance.

    TODO: Eventually, take historical attendance.
    TODO: Re-implement this to use CRON syntax.
    """

    def __init__(self, bot):
        self.canceled = False
        self.logger = logging.getLogger("discord")

        if not hasattr(bot, "attending"):
            bot.attending = set()
        if not hasattr(bot, "skipping"):
            bot.skipping = {}
        self.bot = bot

        self.logger.debug("Attendance Cog initialized.")

    @commands.command()
    async def cancel(self, ctx, args):
        if "GMs" in (role.name for role in ctx.author.roles):
            self.canceled = True
            self._clear_attendance()
            self.logger.debug(f"Game canceled by {ctx.author.name}.")
            await ctx.send("Game canceled. All reservations canceled.")
        else:
            self.logger.debug.debug(
                f"{ctx.author.name} tried to cancel game, but lacked GMs permission."
            )
            await ctx.send("Only GMs can cancel games!")

    @commands.command()
    async def schedule(self, ctx):
        if "GMs" in (role.name for role in ctx.author.roles):
            self.canceled = True
            await ctx.send("Game on for Monday!")

        await ctx.send(",".join(role.name for role in ctx.author.roles))

    @commands.command()
    async def attending(self, ctx, *args):
        if ctx.author.name in self.bot.skipping:
            self.bot.skipping.pop(ctx.author.name)
        self.bot.attending.add(ctx.author.name)

        self.logger.debug(f"{ctx.author.name} is attending.")
        await ctx.send(f"{ctx.author.name} is attending!")

    @commands.command()
    async def skipping(self, ctx, *, reason: str = ""):
        if ctx.author.name in self.bot.attending:
            self.bot.attending.remove(ctx.author.name)
        self.bot.skipping[ctx.author.name] = reason

        self.logger.debug(f"{ctx.author.name} is skipping.")
        await ctx.send(f"{ctx.author.name} will not be attending. Reason: {reason}")

    @commands.command()
    async def clear(self, ctx, *args):
        if "GMs" in (role.name for role in ctx.author.roles):
            self._clear_attendance()
            self.logger.debug(f"{ctx.author.name} has cleared attendance.")
            await ctx.send("Records cleared.")
        else:
            self.logger.debug(f"{ctx.author.name} has failed to cleared attendance.")
            await ctx.send("Only GMs can clear all attendance.")

    def _clear_attendance(self):
        """Clear all records of attendance."""
        self.bot.attending = set()
        self.bot.skipping = {}

    def _tally_skipping(self) -> str:
        """
        Build a string telling of people who have made a note that they will
        not be attending.
        """

        return "\n".join(
            [
                f"{user} -- Note: {note if note else 'Unspecified'}"
                for user, note in self.bot.skipping.items()
            ]
        )

    def _tally_unaccounted_for(self, ctx) -> str:
        """
        Build a string of people who are unaccounted for. i.e., no communication.
        """
        return ", ".join(
            [
                member
                for member in ctx.guild.members
                if "Players" in member.roles
                and member.name not in self.bot.attending
                and member.name not in self.bot.skipping
            ]
        )

    @commands.command()
    async def rollcall(self, ctx, *args):
        """Issue a basic roll-call. i.e., who has chimed in."""
        self.logger.debug(f"{ctx.author.name} has called a rollcall.")
        roster = ", ".join(self.bot.attending)
        skipping = self._tally_skipping()
        unaccounted_for = self._tally_unaccounted_for(ctx)

        await ctx.send(
            (
                "Roll Call! Here is what I know: \n\n"
                f"Confirmed attendance: {roster if roster else 'None.'}\n"
                f"Confirmed not in attendance: {skipping if skipping else 'None.'}\n"
                f"Unaccounted for: {unaccounted_for if unaccounted_for else 'None. Thanks everyone!'}"
            )
        )

    @tasks.loop(hours=24.0)
    async def reset(self):
        """Reset attendance automatically every Tuesday. Games are on Mondays."""
        # Monday = 0, so 1 == Tuesday
        if 1 == datetime.datetime.today().weekday():
            self.logger.debug(f"Bot is resetting for the week...")
            self._clear_attendance()

    @reset.before_loop
    async def before_reset(self):
        self.logger.debug("waiting...")
        await self.bot.wait_until_ready()

    @tasks.loop(hours=24.0)
    async def nagging_reminder(self):
        """
        This task sits and waits to remind people about the game.
        """
        channel = self.bot.get_channel(os.environ["DISCORD_BROADCAST_CHANNEL"])

        day = datetime.datetime.today().weekday()
        # remind everyone monday that the game has been canceled.
        if self.canceled and 0 == day:
            await channel.send(
                (
                    "REMINDER: The bot has been told that Monday's game has been canceled.\n\n"
                    "Have a good week everyone."
                )
            )
            self.logger.debug(f"Bot is reminding everyone that the game is canceled")
            self.canceled = False
            return

        # remind everyone monday that there is a game.
        if not self.canceled and day == 0:
            self.logger.debug(
                f"Bot is reminding everyone that there is a game on Monday."
            )
            await channel.send(
                "REMINDER: The bot believes that there is a game tonight!"
            )
            return

        # remind everyone friday to signal attendance.
        if not self.canceled and day == 4:
            self.logger.debug(
                f"Bot is reminding everyone on friday to signal attendance."
            )
            await channel.send(
                (
                    "REMINDER: The bot believes that there is a game scheduled for monday.\n"
                    "To signal attendance: !attending\n"
                    "To signal missing: !skipping [note]\n"
                    "To see attendance status: !rollcall"
                )
            )

    @nagging_reminder.before_loop
    async def before_nagging_reminder(self):
        print("waiting...")
        await self.bot.wait_until_ready()
