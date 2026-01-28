import asyncio

import discord
from discord.ext import commands
import dotenv
import os

try:
    asyncio.get_running_loop()
except RuntimeError:
    asyncio.set_event_loop(asyncio.new_event_loop())

from discordBackend.BotManager import BotManager
dotenv.load_dotenv()  # Load environment variables from .env file

intents = discord.Intents.all()

bot = commands.Bot(command_prefix='!', intents=intents)


BotManager.setBot(bot)


import Commands.alliance
import Commands.gm
import Commands.galcom

@bot.event
async def on_ready():
    print(f'We have logged in as {bot.user}')

# Get the DISCORD_TOKEN from the environment variables
discord_token = os.getenv('DISCORD_TOKEN')
bot.run(discord_token)