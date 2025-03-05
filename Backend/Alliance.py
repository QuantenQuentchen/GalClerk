from typing import List, Set
from discord import Member, PermissionOverwrite, Guild, Role, VoiceChannel, TextChannel, CategoryChannel, utils

from Backend.Player import Player
from Backend.GameManager import GameManager

class Alliance:
    def __init__(self, name: str):
        #self.id = #generateID
        self.name = name
        self.guild = None
        self.members = []
        self.text_channel = None
        self.voice_channel = None
        self.category = None
        self.role = None

    async def rename(self, new_name: str):
        self.name = new_name
        await self.text_channel.edit(name=new_name)
        await self.voice_channel.edit(name=new_name)
        await self.category.edit(name=new_name)
        await self.role.edit(name=new_name)

    async def create_alliance(self, guild):
        self.guild = guild
        
        self.role = await guild.create_role(name=self.name)
        
        overwrites = {
            guild.default_role: PermissionOverwrite(read_messages=False, send_messages=False, connect=False),
            guild.me: PermissionOverwrite(read_messages=True, send_messages = True, connect = True),
            self.role: PermissionOverwrite(read_messages=True, send_messages=True, connect=True, move_members=True)
        }

        self.category = await guild.create_category(self.name)
        await self.category.set_permissions(self.role, read_messages=True, send_messages=True)
        self.text_channel = await self.category.create_text_channel(self.name, overwrites=overwrites)
        self.voice_channel = await self.category.create_voice_channel(self.name, overwrites=overwrites)
    
    async def recreate_alliance(self, guild, roleID, categoryID, textChannelID, voiceChannelID, memberIDs):
        self.guild = guild
        self.role = utils.get(guild.roles, id=roleID)
        self.category = utils.get(guild.categories, id=categoryID)
        self.text_channel = utils.get(guild.text_channels, id=textChannelID)
        self.voice_channel = utils.get(guild.voice_channels, id=voiceChannelID)
        self.members = [utils.get(guild.members, id=memberID) for memberID in memberIDs]

    def get_category(self):
        return self.category
    
    def get_text_channel(self):
        return self.text_channel
    
    def get_voice_channel(self):
        return self.voice_channel
    
    def get_role(self):
        return self.role
    
    async def add_member(self, member: Member):
        GameManager.get_manager(member.guild).get_player(member).add_alliance(self)
        await member.add_roles(self.role)
        self.members.append(member)
    
    async def invite_member(self, member: Member):
        await self.add_member(member)
        await self.text_channel.send(f"{member.mention} has been invited to {self.name}")
    
    async def remove_member(self, member):
        await self.text_channel.send(f"{member.mention} has left the alliance")
        GameManager.get_manager(member.guild).get_player(member).remove_alliance(self)
        await member.remove_roles(self.role)
        self.members.remove(member)
        if len(self.members) >= 1:
            await self.text_channel.send(f"The alliance has been disbanded")
            await GameManager.get_manager(member.guild).delete_alliance(self)
