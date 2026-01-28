from discord import Option, Member

from Backend.GalacticCommunity import GalacticCommunity
from Backend.GameManager import GameManager
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
    PlayMan: GameManager = await GameManager.get_manager(ctx.guild)
    await ctx.respond("The game is being concluded... (due to callback delay no further reporting may happen for this command)", ephemeral=True)
    await PlayMan.end()
    await ctx.respond("The game has been concluded", ephemeral=True)

@gm.command(
    name="foundgalcom",
    description="Found the Galactic Community",
)
async def foundgalcom(ctx):
    if not ctx.author.guild_permissions.administrator:
        await ctx.respond("Nope not your command", ephemeral=True)
        return
    PlayMan: GameManager = await GameManager.get_manager(ctx.guild)
    if PlayMan.get_galcom() is not None:
        await ctx.respond("The Galactic Community has already been founded", ephemeral=True)
        return
    await ctx.respond("The Galactic Community is being founded... (due to callback delay no further reporting may happen for this command)", ephemeral=True)
    await PlayMan.found_galcom()

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
    if not ctx.author.guild_permissions.administrator:
        await ctx.respond("Nope not your command", ephemeral=True)
        return
    councilors = [councilor1, councilor2, councilor3, councilor4, councilor5]
    councilors = [councilor for councilor in councilors if councilor is not None]
    PlayMan: GameManager = await GameManager.get_manager(ctx.guild)
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
    await galCom.set_senate(councilors)
    await ctx.respond("The councilors have been set", ephemeral=True)

@gm.command(
    name="setcustodian",
    description="Set the custodian of the Galactic Community",
)
async def setcustodian(ctx,
                        custodian: Option(Member, name = "custodian", description = "Custodian of the Galactic Community", required = True) # type: ignore
    ):
    if not ctx.author.guild_permissions.administrator:
        await ctx.respond("Nope not your command", ephemeral=True)
        return
    PlayMan: GameManager = await GameManager.get_manager(ctx.guild)
    galCom = PlayMan.get_galcom()

    if galCom is None:
        await ctx.respond("The Galactic Community has not been founded, Aborted!", ephemeral=True)
        return
    if not galCom.is_member(custodian):
        await ctx.respond(f"{custodian.mention} is not a member of the Galactic Community, Aborted!", ephemeral=True)
        return

    await galCom.setCustodian(custodian)
    await ctx.respond("The custodian has been set", ephemeral=True)

@gm.command(
    name="removecustodian",
    description="Remove the custodian of the Galactic Community",
)
async def removecustodian(ctx):
    if not ctx.author.guild_permissions.administrator:
        await ctx.respond("Nope not your command", ephemeral=True)
        return
    PlayMan: GameManager = await GameManager.get_manager(ctx.guild)
    galCom = PlayMan.get_galcom()

    if galCom is None:
        await ctx.respond("The Galactic Community has not been founded, Aborted!", ephemeral=True)
        return

    await galCom.removeCustodian()
    await ctx.respond("The custodian has been removed", ephemeral=True)


@gm.command(
    name="disbandsenate",
    description="Disband the senate of the Galactic Community",
)
async def disbandsenate(ctx):
    if not ctx.author.guild_permissions.administrator:
        await ctx.respond("Nope not your command", ephemeral=True)
        return
    PlayMan: GameManager = await GameManager.get_manager(ctx.guild)
    galCom = PlayMan.get_galcom()

    if galCom is None:
        await ctx.respond("The Galactic Community has not been founded!", ephemeral=True)
        return
    await galCom.disbandSenate()

    await ctx.respond("The senate has been disbanded", ephemeral=True)

@gm.command(
    name="setempire",
    description="Set the emperor of the Galactic Empire",
)
async def setempire(ctx):
    if not ctx.author.guild_permissions.administrator:
        await ctx.respond("Nope not your command", ephemeral=True)
        return
    PlayMan: GameManager = await GameManager.get_manager(ctx.guild)
    galCom = PlayMan.get_galcom()

    if galCom is None:
        await ctx.respond("The Galactic Community has not been founded!", ephemeral=True)
        return
    await galCom.setEmpire()

    await ctx.respond("The emperor has been set", ephemeral=True)

@gm.command(
    name="setsenate",
    description="Set the emperor of the Galactic Empire",
)
async def setsenate(ctx):
    if not ctx.author.guild_permissions.administrator:
        await ctx.respond("Nope not your command", ephemeral=True)
        return
    PlayMan: GameManager = await GameManager.get_manager(ctx.guild)
    galCom = PlayMan.get_galcom()

    if galCom is None:
        await ctx.respond("The Galactic Community has not been founded!", ephemeral=True)
        return

    await galCom.setSenate()
    await ctx.respond("The Emperor has been bloodily deposed", ephemeral=True)


@gm.command(
    name="start",
    description="Start the game",
)
async def start(ctx):
    if not ctx.author.guild_permissions.administrator:
        await ctx.respond("Nope not your command", ephemeral=True)
        return
    PlayMan: GameManager = await GameManager.get_manager(ctx.guild)
    if PlayMan.is_created():
        await ctx.respond("The game has been started", ephemeral=True)
        await PlayMan.start()
        return

    if PlayMan.is_stopped():
        await ctx.respond("The game has been continued", ephemeral=True)
        await PlayMan.start()
        return
    await ctx.respond("The game is already running", ephemeral=True)

@gm.command(
    name="pause",
    description="Pause the game",
)
async def pause(ctx):
    if not ctx.author.guild_permissions.administrator:
        await ctx.respond("Nope not your command", ephemeral=True)
        return
    PlayMan: GameManager = await GameManager.get_manager(ctx.guild)
    if PlayMan.is_stopped():
        await ctx.respond("The game has already been paused", ephemeral=True)
        return
    await PlayMan.pause()
    await ctx.respond("The game has been paused", ephemeral=True)