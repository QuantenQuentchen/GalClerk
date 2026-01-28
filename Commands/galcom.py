from Backend.GalacticCommunity import GalacticCommunity
from Backend.GameManager import GameManager

from discordBackend.BotManager import BotManager


galcom = BotManager.getBot().create_group("galcom", "Galactic Community commands")

@galcom.command(
    name="leave",
    description="Leave the Galactic Community",
)
async def leave(ctx):
    PlayMan: GameManager = await GameManager.get_manager(ctx.guild)
    if PlayMan.can_act() is False:
        await ctx.respond(f"You are not allowed to found an alliance", ephemeral=True)
        return
    galCom: GalacticCommunity = PlayMan.get_galcom()
    if galCom is None:
        await ctx.respond("The Galactic Community has not been founded", ephemeral=True)
        return
    
    await galCom.remove_player(PlayMan.get_player(ctx.author))
    await ctx.respond("You have left the Galactic Community", ephemeral=True)

@galcom.command(
    name = "join",
    description = "Join the Galactic Community"
)
async def join(ctx):
    PlayMan: GameManager = await GameManager.get_manager(ctx.guild)
    if PlayMan.can_act() is False:
        await ctx.respond(f"You are not allowed to found an alliance", ephemeral=True)
        return
    galCom: GalacticCommunity = PlayMan.get_galcom()
    if galCom is None:
        await ctx.respond("The Galactic Community has not been created")
        return
    if galCom.is_forbidden(ctx.author):
        await ctx.respond("You are forbidden from joining the Galactic Community")
        return
    await galCom.add_player(PlayMan.get_player(ctx.author))
    await ctx.respond("You have joined the Galactic Community")
    return