import discord
import traceback
import psutil
import os

from datetime import datetime
from discord.ext.commands import errors
from utils import default


async def send_cmd_help(ctx):
    if ctx.invoked_subcommand:
        _help = await ctx.bot.formatter.format_help_for(ctx, ctx.invoked_subcommand)
    else:
        _help = await ctx.bot.formatter.format_help_for(ctx, ctx.command)

    for page in _help:
        await ctx.send(page)


class Events:
    def __init__(self, bot):
        self.bot = bot
        self.config = default.get("config.json")
        self.process = psutil.Process(os.getpid())

    async def on_command_error(self, ctx, err):
        if isinstance(err, errors.MissingRequiredArgument) or isinstance(err, errors.BadArgument):
            await send_cmd_help(ctx)

        elif isinstance(err, errors.CommandInvokeError):
            err = err.original

            _traceback = traceback.format_tb(err.__traceback__)
            _traceback = ''.join(_traceback)
            error = '```py\n{2}{0}: {3}\n```'.format(type(err).__name__, ctx.message.content, _traceback, err)
            logchannel = self.bot.get_channel(499327315088769025)

            await logchannel.send(f"`ERROR`\n{error}")
            await ctx.send("There was an error in processing the command, our staff have been notified and will be in contact soon.")

        elif isinstance(err, errors.CheckFailure):
            pass

        elif isinstance(err, errors.CommandOnCooldown):
            await ctx.send(f"This command is on cooldown... try again in {err.retry_after:.0f} seconds.")

        elif isinstance(err, errors.CommandNotFound):
            pass

    async def on_ready(self):
        if not hasattr(self.bot, 'uptime'):
            self.bot.uptime = datetime.utcnow()

        print(f'Ready: {self.bot.user} | Servers: {len(self.bot.guilds)}')
        await self.bot.change_presence(activity=discord.Game(type=0, name=self.config.playing), status=discord.Status.online)

    async def on_member_join(self, member):
        joinleave = self.bot.get_channel(445819554640429067)

        await joinleave.send(f"Welcome {member} to the society!")

    async def on_member_remove(self, member):
        joinleave = self.bot.get_channel(445819554640429067)

        await joinleave.send(f"{member} left the society..")

def setup(bot):
    bot.add_cog(Events(bot))
