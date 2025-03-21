from discord import Option, Member, SlashCommandGroup, PermissionOverwrite, guild, AutocompleteContext

from Backend.GameManager import GameManager
from Backend.Alliance import Alliance


from discordBackend.BotManager import BotManager


alliance = BotManager.getBot().create_group("alliance", "Found, join and manage alliances")


def format_mentions(members):
    if len(members) > 1:
        return ', '.join([member.mention for member in members[:-1]]) + f", and {members[-1].mention}"
    elif members:
        return members[0].mention
    return ""

@alliance.command(
    name="found",
    description="Found an alliance",
)
async def found(ctx,
                name: Option(str, name = "name", description = "Name of the alliance"), # type: ignore
                member1: Option(Member, name = "member", description = "Members of the alliance", required = True), # type: ignore
                member2: Option(Member, name = "member1", description = "Members of the alliance", required = False), # type: ignore
                member3: Option(Member, name = "member2", description = "Members of the alliance", required = False), # type: ignore
                member4: Option(Member, name = "member3", description = "Members of the alliance", required = False) # type: ignore
                ):
    PlayMan: GameManager = GameManager.get_manager(ctx.guild)
    if PlayMan.can_act() is False:
        await ctx.respond(f"The Game is Paused", ephemeral=True)
        return
    if PlayMan.get_alliance(name) is not None:
        await ctx.respond(f"An alliance with the name {name} already exists", ephemeral=True)
        return
    
    alliance = Alliance(name) #Name check
    await alliance.create_alliance(ctx.guild)

    members = [ctx.author, member1, member2, member3, member4]
    members = [member for member in members if member is not None]
    for member in members:
        await alliance.add_member(member)

    member_mentions = format_mentions(members)

    eventString = f"{name} has been founded by {member_mentions}"

    await alliance.get_text_channel().send(f"The Alliance: {name} has been founded by {member_mentions}, welcome to our Facilities !")
    PlayMan.add_alliance(alliance)
    await ctx.respond(eventString, ephemeral=True)


async def autocomplete_alliances(ctx: AutocompleteContext):
    return [alliance.name for alliance in GameManager.get_manager(ctx.interaction.guild).get_player(ctx.interaction.user).get_alliances()]

@alliance.command(
    name="invite",
    description="Invite a Player to an alliance",
)
async def invite(ctx,
                alliance: Option(str, name = "alliances", description = "Name of the alliance", autocomplete=autocomplete_alliances), # type: ignore
                member: Option(Member, name = "member", description = "Member to invite", required = True) # type: ignore
                ):
    PlayMan: GameManager = GameManager.get_manager(ctx.guild)
    if PlayMan.can_act() is False:
        await ctx.respond(f"The Game is Paused", ephemeral=True)
        return
    if alliance is None:
        await ctx.respond(f"You are not Member of an Aliiance (uff)", ephemeral=True)
        return
    alliance: Alliance = GameManager.get_manager(ctx.guild).get_alliance(alliance)
    await alliance.invite_member(member)
    await ctx.respond(f"{member.mention} has been invited to {alliance}", ephemeral=True)

@alliance.command(
    name="leave",
    description="Leave an alliance",
)
async def leave(ctx,
                alliance: Option(str, name = "alliances", description = "Name of the alliance", autocomplete=autocomplete_alliances) # type: ignore
                ):
    PlayMan = GameManager.get_manager(ctx.guild)
    if PlayMan.can_act() is False:
        await ctx.respond(f"The Game is Paused", ephemeral=True)
        return
    if alliance is None:
        await ctx.respond(f"You are not Member of an Aliiance (uff)", ephemeral=True)
        return
    PlayMan = GameManager.get_manager(ctx.guild)
    alliance = PlayMan.get_alliance(alliance)
    await alliance.remove_member(ctx.author)
    await ctx.respond(f"You have left the alliance", ephemeral=True)

@alliance.command(
    name="rename",
    description="Rename an alliance",
)
async def rename(ctx,
                alliance: Option(str, name = "alliances", description = "Name of the alliance", autocomplete=autocomplete_alliances), # type: ignore
                new_name: Option(str, name = "new", description = "New name of the alliance") # type: ignore
                ):
    PlayMan: GameManager = GameManager.get_manager(ctx.guild)
    if PlayMan.can_act() is False:
        await ctx.respond(f"You are not allowed to found an alliance", ephemeral=True)
        return
    if PlayMan.get_alliance(new_name) is not None:
        await ctx.respond(f"An alliance with the name {new_name} already exists", ephemeral=True)
        return
    if alliance is None:
        await ctx.respond(f"You are not Member of an Aliiance (uff)", ephemeral=True)
        return
    await PlayMan.rename_alliance(PlayMan.get_alliance(alliance), new_name)
    await ctx.respond(f"The alliance has been renamed to {new_name}", ephemeral=True)