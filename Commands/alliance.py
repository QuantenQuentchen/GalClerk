from discord import Option, Member, SlashCommandGroup, PermissionOverwrite, guild
from Backend.Player import Alliance, PlayerManager
import sys
import os


#sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

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
                member1: Option(Member, name = "founding Member", description = "Members of the alliance", required = True), # type: ignore
                member2: Option(Member, name = "founding Member", description = "Members of the alliance", required = False), # type: ignore
                member3: Option(Member, name = "founding Member", description = "Members of the alliance", required = False), # type: ignore
                member4: Option(Member, name = "founding Member", description = "Members of the alliance", required = False) # type: ignore
                ):
    alliance = Alliance(name) #Name check
    await alliance.create_alliance(ctx.guild)

    members = [ctx.author, member1, member2, member3, member4]
    members = [member for member in members if member is not None]
    for member in members:
        alliance.add_member(member)

    member_mentions = format_mentions(members)

    eventString = f"{name} has been founded by {member_mentions}"

    await alliance.get_text_channel().send(f"The Alliance: {name} has been founded by {member_mentions}, welcome to our Facilities !")
    PlayerManager.get_manager(ctx.guild).add_alliance(alliance)
    await ctx.respond(eventString, ephemeral=True)


async def autocomplete_alliances(ctx):
    return [(alliance.name, alliance) for alliance in PlayerManager.get_player(ctx.author).get_alliances()]

@alliance.command(
    name="invite",
    description="Invite a Player to an alliance",
)
async def invite(ctx,
                alliance: Option(str, name = "alliances", description = "Name of the alliance", autocomplete=autocomplete_alliances), # type: ignore
                member: Option(Member, name = "member", description = "Member to invite", required = True) # type: ignore
                ):
    if alliance is None:
        await ctx.respond(f"You are not Member of an Aliiance (uff)", ephemeral=True)
        return
    alliance.add_member(member)
    await alliance.get_text_channel().send(f"{member.mention} has been invited to {alliance}")
    await ctx.respond(f"{member.mention} has been invited to {alliance}", ephemeral=True)

@alliance.command(
    name="leave",
    description="Leave an alliance",
)
async def leave(ctx,
                alliance: Option(str, name = "alliances", description = "Name of the alliance", autocomplete=autocomplete_alliances) # type: ignore
                ):
    if alliance is None:
        await ctx.respond(f"You are not Member of an Aliiance (uff)", ephemeral=True)
        return
    alliance.remove_member(ctx.author)
    await alliance.get_text_channel().send(f"{ctx.author.mention} has left the alliance")
    if len(alliance.members) == 0:
        await alliance.get_text_channel().send(f"The alliance has been disbanded")
        PlayerManager.get_manager(ctx.guild).remove_alliance(alliance)
    await ctx.respond(f"You have left the alliance", ephemeral=True)

@alliance.command(
    name="rename",
    description="Rename an alliance",
)
async def rename(ctx,
                alliance: Option(str, name = "alliances", description = "Name of the alliance", autocomplete=autocomplete_alliances), # type: ignore
                new_name: Option(str, name = "new name", description = "New name of the alliance") # type: ignore
                ):
    if alliance is None:
        await ctx.respond(f"You are not Member of an Aliiance (uff)", ephemeral=True)
        return
    PlayerManager.get_manager(ctx.guild).rename_alliance(alliance, new_name)
    
    await alliance.get_text_channel().edit(name=new_name)
    await ctx.respond(f"The alliance has been renamed to {new_name}", ephemeral=True)