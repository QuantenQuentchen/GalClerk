from discord import Option, Member, SlashCommandGroup, PermissionOverwrite, guild, AutocompleteContext
from Backend.Player import Alliance, PlayerManager, GalacticCommunity, GameState
import sys
import os

from discordBackend.BotManager import BotManager


gm = BotManager.getBot().create_group("gm", "Game Master commands")

@gm.command(
    name="conclude",
    description="Conclude the current game",
)
async def conclude(ctx):
    if not ctx.author.guild_permissions.administrator:
        await ctx.respond("Nope not your command", ephemeral=True)
        return
    PlayMan: PlayerManager = PlayerManager.get_manager(ctx.guild)
    await PlayMan.conclude()
    await ctx.respond("The game has been concluded", ephemeral=True)

@gm.command(
    name="foundgalcom",
    description="Found the Galactic Community",
)
async def foundgalcom(ctx):
    if not ctx.author.guild_permissions.administrator:
        await ctx.respond("Nope not your command", ephemeral=True)
        return
    PlayMan: PlayerManager = PlayerManager.get_manager(ctx.guild)
    await PlayMan.found_galcom()
    await ctx.respond("The Galactic Community has been founded", ephemeral=True)

@gm.command(
        name="setcouncilors",
        description="Set the councilors of the Galactic Community",
)
async def setcouncilors(ctx,
                        councilor1: Option(Member, name = "councilor1", description = "Councilor of the Galactic Community", required = True), # type: ignore
                        councilor2: Option(Member, name = "councilor2", description = "Councilor of the Galactic Community", required = False), # type: ignore
                        councilor3: Option(Member, name = "councilor3", description = "Councilor of the Galactic Community", required = False), # type: ignore
                        councilor4: Option(Member, name = "councilor4", description = "Councilor of the Galactic Community", required = False), # type: ignore
                        councilor5: Option(Member, name = "councilor5", description = "Councilor of the Galactic Community", required = False), # type: ignore
    ):
    councilors = [councilor1, councilor2, councilor3, councilor4, councilor5]
    councilors = [councilor for councilor in councilors if councilor is not None]
    PlayMan: PlayerManager = PlayerManager.get_manager(ctx.guild)
    galCom: GalacticCommunity = PlayMan.get_galcom()
    if galCom is None:
        await ctx.respond("The Galactic Community has not been founded, Aborted!", ephemeral=True)
        return
    for councilor in councilors:
        if not galCom.is_member(councilor):
            await ctx.respond(f"{councilor.mention} is not a member of the Galactic Community, Aborted!", ephemeral=True)
            return
        if galCom.is_head(councilor):
            await ctx.respond(f"{councilor.mention} is the head of the Galactic Community, Aborted!", ephemeral=True)
            return
    galCom.set_councilors(councilors)
    await ctx.respond("The councilors have been set", ephemeral=True)

@gm.command(
    name="setcustodian",
    description="Set the custodian of the Galactic Community",
)
async def setcustodian(ctx,
                        custodian: Option(Member, name = "custodian", description = "Custodian of the Galactic Community", required = True) # type: ignore
    ):
    PlayMan: PlayerManager = PlayerManager.get_manager(ctx.guild)
    galCom = PlayMan.get_galcom()
    if galCom is None:
        await ctx.respond("The Galactic Community has not been founded, Aborted!", ephemeral=True)
        return
    if not galCom.is_member(custodian):
        await ctx.respond(f"{custodian.mention} is not a member of the Galactic Community, Aborted!", ephemeral=True)
        return
    if galCom.custodian is None:
        await galCom.set_custodian(custodian)
    else:
        await galCom.switch_custodian(custodian)
    await ctx.respond("The custodian has been set", ephemeral=True)


@gm.command(
    name="start",
    description="Start the game",
)
async def start(ctx):
    if not ctx.author.guild_permissions.administrator:
        await ctx.respond("Nope not your command", ephemeral=True)
        return
    PlayMan: PlayerManager = PlayerManager.get_manager(ctx.guild)
    if not PlayMan.is_stopped():
        await ctx.respond("The game has already started", ephemeral=True)
        return
    await PlayMan.start(ctx.guild)
    await ctx.respond("The game has been started", ephemeral=True)

@gm.command(
    name="pause",
    description="Pause the game",
)
async def pause(ctx):
    if not ctx.author.guild_permissions.administrator:
        await ctx.respond("Nope not your command", ephemeral=True)
        return
    PlayMan: PlayerManager = PlayerManager.get_manager(ctx.guild)
    if PlayMan.is_stopped():
        await ctx.respond("The game has already been paused", ephemeral=True)
        return
    await PlayMan.pause(ctx.guild)
    await ctx.respond("The game has been paused", ephemeral=True)

@gm.command(
    name="init",
    description="Initializes a new Game"
)
async def init(ctx, 
            name: Option(str, name="game_name", description="Name of the Game", required=False)): #type: ignore
    if not ctx.author.guild_permissions.administrator:
        await ctx.respond("Nope not your command", ephemeral=True)
        return
    PlayMan: PlayerManager = PlayerManager.get_manager(ctx.guild)
    if PlayMan.is_init or PlayMan.get_gameState == GameState.STARTED:
        await ctx.respond("Game has already been initialized please conclude before restarting")
        return
    PlayMan.init(name)
    return