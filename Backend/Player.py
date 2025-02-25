from typing import List
from discord import utils, Member, PermissionOverwrite

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
        PlayerManager.get_player(member).add_alliance(self)
        await member.add_role(self.role)
        self.members.append(member)
    
    async def remove_member(self, member):
        PlayerManager.get_player(member).remove_alliance(self)
        await member.remove_role(self.role)
        self.members.remove(member)

class Player:
    def __init__(self, name: str):
        self.name = name
        self.alliances = []
        self.memberID = None
        
    def add_alliance(self, alliance: Alliance):
        self.alliances.append(alliance)
        
    def remove_alliance(self, alliance: Alliance):
        self.alliances.remove(alliance)
        
    def get_alliance(self, alliance_name: str) -> Alliance:
        for alliance in self.alliances:
            if alliance.name == alliance_name:
                return alliance
        return None
    
    def get_alliances(self) -> List[Alliance]:
        return self.alliances

class PlayerManager:
    
    ManagerStore = {}

    def __init__(self):
        self.playerStore = {}
        self.allianceStore = {}
        self.marked_for_archive = []
    
    def get_manager(guildID):
        if guildID in PlayerManager.ManagerStore:
            return PlayerManager.ManagerStore[guildID]
        else:
            PlayerManager.ManagerStore[guildID] = PlayerManager()
            return PlayerManager.ManagerStore[guildID]

    def get_player(self, member) -> Player:
        player = self.playerStore.get(member.id)
        #Check if member is in 
        if player is None:
            self.playerStore[member.id] = Player(member.name)
            return []
        return player
    
    def add_alliance(self, alliance: Alliance):
        self.allianceStore[alliance.name] = alliance

    def get_alliance(self, name: str) -> Alliance:
        return self.allianceStore.get(name)
    
    def rename_alliance(self, alliance: Alliance, new_name: str):
        alliance.name = new_name
        self.allianceStore[new_name] = alliance
        del self.allianceStore[alliance.name]
    
    async def delete_alliance(self, alliance: Alliance):
        del self.allianceStore[alliance.name]
        for member in alliance.members:
            await member.remove_role(alliance.role)
        await alliance.role.delete()
        await alliance.category.delete()
        await alliance.voice_channel.delete()
        
        # Check the message history of the text channel
        async for message in alliance.text_channel.history(limit=100):
            if message.author != alliance.guild.me:
                # If any message is not written by the bot, do not delete the channel
                self.marked_for_archive.append(alliance.text_channel.id)
                await alliance.text_channel.edit(overwrites={
                    alliance.guild.default_role: PermissionOverwrite(view_channel=False)
                })
                return
        
        # If all messages are written by the bot, delete the channel
        await alliance.text_channel.delete()