from discord import Option, Member, SlashCommandGroup, PermissionOverwrite, guild, AutocompleteContext
from Backend.Player import Alliance, PlayerManager, GalacticCommunity
import sys
import os

from discordBackend.BotManager import BotManager


galcom = BotManager.getBot().create_group("galcom", "Galactic Community commands")

@galcom.command(
    name="leave",
    description="Leave the Galactic Community",
)
async def leave(ctx):
    PlayMan: PlayerManager = PlayerManager.get_manager(ctx.guild)
    galCom: GalacticCommunity = PlayMan.get_galcom()
    if galCom is None:
        await ctx.respond("The Galactic Community has not been founded", ephemeral=True)
        return
    if not galCom.is_member(ctx.author):
        await ctx.respond("You are not a member of the Galactic Community", ephemeral=True)
        return
    if galCom.is_councilor(ctx.author):
        await ctx.respond("You are a councilor, you cannot leave the Galactic Community", ephemeral=True)
        return
    if galCom.is_head(ctx.author):
        await ctx.respond("Your position is too important, you cannot leave the Galactic Community", ephemeral=True)
        return
    
    await galCom.remove_player(PlayMan.get_player(ctx.author))
    await ctx.respond("You have left the Galactic Community", ephemeral=True)

@galcom.command(
    name = "join",
    description = "Join the Galactic Community"
)
async def join(ctx):
    PlayMan: PlayerManager = PlayerManager.get_manager(ctx.guild)
    galcom: GalacticCommunity = PlayMan.get_galcom()
    if galcom == None:
        await ctx.respond("The Galactic Community has not been created")
        return
    if galcom.is_forbidden(ctx.author):
        await ctx.respond("You are forbidden from joining the Galactic Community")
        return
    await galcom.add_player(PlayMan.get_player(ctx.author))
    return