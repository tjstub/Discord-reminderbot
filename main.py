#!/usr/bin/env python3
import logging
from logging.handlers import RotatingFileHandler
import os
import sys

from discord import Client
from discord.ext import commands
from cogs import Attendance, Rollers

# A cog is discord's lingo for a collection of commands and tasks.
# They must inherit from the Cogs class. Add them here to be loaded.
COGS = (Attendance, Rollers)
bot = commands.Bot(command_prefix="/")


def setup_logger(level: int) -> logging.Logger:
    logger = logging.getLogger("discord")
    logger.setLevel(level)

    setup_logger_to_stdout(logger)
    setup_logger_to_file(logger)

    return logger


def setup_logger_to_file(logger: logging.Logger) -> None:
    handler = RotatingFileHandler(
        filename="discord.log", encoding="utf-8", mode="a", maxBytes=5 * 1024 * 1024
    )
    handler.setFormatter(
        logging.Formatter("%(asctime)s:%(levelname)s:%(name)s: %(message)s")
    )
    logger.addHandler(handler)


def setup_logger_to_stdout(logger: logging.Logger) -> None:
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(
        logging.Formatter("%(asctime)s:%(levelname)s:%(name)s: %(message)s")
    )
    logger.addHandler(handler)


def setup(bot: Client) -> None:
    setup_logger(level=logging.DEBUG)
    for cog in COGS:
        bot.add_cog(cog(bot))


if __name__ == "__main__":

    try:
        token = os.environ["DISCORD_TOKEN"]
        os.environ["DISCORD_BROADCAST_CHANNEL"]
    except KeyError:
        logging.error(
            "You must define 'DISCORD_TOKEN' and 'DISCORD_BROADCAST_CHANNEL' in your environment!"
        )
        exit(1)

    setup(bot)
    bot.run(token)