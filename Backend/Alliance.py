from discord import Member, PermissionOverwrite, Guild, CategoryChannel

from Backend.GameManager import GameManager
from Backend.History import HistoryManager


class Alliance:

    @classmethod
    async def create(cls, name: str, guild):
        alliance = cls(name)
        await alliance._create_alliance(guild)
        return alliance

    def __init__(self, name: str):
        self.name = name
        self.guild: Guild | None = None
        self.members = []
        self.text_channel = None
        self.voice_channel = None
        self.category: CategoryChannel | None = None
        self.role = None

    async def _create_alliance(self, guild):
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

    async def rename(self, new_name: str):
        self.name = new_name
        await self.text_channel.edit(name=new_name)
        await self.voice_channel.edit(name=new_name)
        await self.category.edit(name=new_name)
        await self.role.edit(name=new_name)


    def get_category(self):
        return self.category
    
    def get_text_channel(self):
        return self.text_channel
    
    def get_voice_channel(self):
        return self.voice_channel
    
    def get_role(self):
        return self.role
    
    async def add_member(self, member: Member):
        gm = await GameManager.get_manager(member.guild)
        gm.get_player(member).add_alliance(self)
        await member.add_roles(self.role)
        self.members.append(member)
    
    async def invite_member(self, member: Member):
        await self.add_member(member)
        await self.text_channel.send(f"{member.mention} has been invited to {self.name}")
    
    async def remove_member(self, member):
        await self.text_channel.send(f"{member.mention} has left the alliance")
        gm = await GameManager.get_manager(member.guild)
        gm.get_player(member).remove_alliance(self)
        await member.remove_roles(self.role)
        self.members.remove(member)
        if len(self.members) >= 1:
            await self.text_channel.send(f"The alliance has been disbanded")
            await self.delete()

    async def delete(self):
        #TODO: Fails sometimes
        for member in self.members.copy():
            await self.remove_member(member)
        await self.role.delete()
        await self.category.delete()
        await self.voice_channel.delete()
        await HistoryManager.get_manager(self.guild).add_or_delete_text_channel(self.text_channel)