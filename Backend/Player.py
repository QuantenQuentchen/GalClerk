from typing import List, Set
from discord import utils, Member, PermissionOverwrite, Guild, Role, VoiceChannel, TextChannel, CategoryChannel
from datetime import datetime as dt
from enum import Enum

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
        PlayerManager.get_manager(member.guild).get_player(member).add_alliance(self)
        await member.add_roles(self.role)
        self.members.append(member)
    
    async def invite_member(self, member: Member):
        await self.add_member(member)
        await self.text_channel.send(f"{member.mention} has been invited to {self.name}")
    
    async def remove_member(self, member):
        await self.text_channel.send(f"{member.mention} has left the alliance")
        PlayerManager.get_manager(member.guild).get_player(member).remove_alliance(self)
        await member.remove_roles(self.role)
        self.members.remove(member)
        if len(self.members) >= 1:
            await self.text_channel.send(f"The alliance has been disbanded")
            await PlayerManager.get_manager(member.guild).delete_alliance(self)

class Player:
    def __init__(self, member: Member):
        self.name = member.name
        self.guild = member.guild
        self.member = member
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

class GalacticCommunity:

    category_name = "🌌galactic-community"

    member = "👤Member"
    senator = "🏛️Councilor"
    custodian = "🛡️Custodian"
    emperor = "👑Emperor"

    announce_channel_name = "📃announcements"
    public_channel_name = "📑public-galactic"
    news_channel_name = "📰xenonion-news"

    lower_chamber = "🏛️galactic-assembly"
    lower_chamber_empire = "👑imperial-senate"

    upper_chamber = "🏛️galactic-council"
    upper_chamber_empire = "👑imperial-court"

    forum0 = "📜Galactic Forum"
    forum1 = "📜Galactic Forum"
    forum2 = "📜Galactic Forum"
    forum3 = "📜Galactic Forum"


    def __init__(self, guild):
        self.guild: Guild = guild

        self.members: List[Member] = []
        self.memberRole: Role = None
        
        self.category: CategoryChannel = None
        self.announce_channel: TextChannel = None
        self.public_channel: TextChannel = None
        self.news_channel: TextChannel = None

        self.lower_chamber_text: TextChannel = None
        self.lower_chamber: VoiceChannel = None

        self.upper_chamber_text: TextChannel = None
        self.upper_chamber: VoiceChannel = None

        self.forum0: VoiceChannel = None
        self.forum1: VoiceChannel = None
        self.forum2: VoiceChannel = None
        self.forum3: VoiceChannel = None

        self.custodianRole: Role = None
        self.custodian: Member = None

        self.emperorRole: Role = None
        self.emperor: Member = None

        self.senateRole: Role = None
        self.senateMembers: List[Member] = []
        self.forbiddenSet: Set[Member] = {}
    
    def add_forbidden(self, member: Member):
        self.forbiddenSet.add(member)
    
    def remove_forbidden(self, member: Member):
        self.forbiddenSet.remove(member)
    
    def clear_forbidden(self):
        self.forbiddenSet.clear()
    
    def get_forbidden(self):
        return self.forbiddenSet
    
    def is_forbidden(self, member: Member):
        return member in self.forbiddenSet

    def is_member(self, member: Member):
        return member in self.members

    def is_councilor(self, member: Member):
        return member in self.senateMembers
    
    def is_head(self, member: Member):
        return member == self.emperor or member == self.custodian

    async def remove_player(self, player: Player):
        await self.announce_channel.send(f"{player.member.mention} has left the Galactic Community")
        player.member.remove_roles(self.memberRole)
        self.players.remove(player)

    async def add_player(self, player: Player):
        await player.member.add_roles(self.memberRole)
        self.players.append(player)
        await self.announce_channel.send(f"{player.member.mention} has joined the Galactic Community")

    def getOverwriteStandard(self):
        return {
            self.guild.default_role: PermissionOverwrite(read_messages=False, send_messages=False, connect=False),
            self.memberRole: PermissionOverwrite(read_messages=True, send_messages=True, connect = True),
            self.senateRole: PermissionOverwrite(read_messages=True, send_messages=True, connect=True),
            self.emperorRole: PermissionOverwrite(read_messages=True, send_messages=True, connect=True, move_members=True, mute_members=True, deafen_members=True),
            self.custodianRole: PermissionOverwrite(read_messages=True, send_messages=True, connect=True, move_members=True, mute_members=True)
        }
    
    def getOverwriteSenate(self):
        return {
            self.guild.default_role: PermissionOverwrite(read_messages=False, send_messages=False, connect=False),
            self.memberRole: PermissionOverwrite(read_messages=False, send_messages=False, connect = False),
            self.senateRole: PermissionOverwrite(read_messages=True, send_messages=True, connect=True),
            self.emperorRole: PermissionOverwrite(read_messages=True, send_messages=True, connect=True, move_members=True, mute_members=True, deafen_members=True),
            self.custodianRole: PermissionOverwrite(read_messages=True, send_messages=True, connect=True, move_members=True, mute_members=True),
            }
    
    def getHeadOverwrite(self):
        return {
            self.guild.default_role: PermissionOverwrite(read_messages=False, send_messages=False, connect=False),
            self.memberRole: PermissionOverwrite(read_messages=False, send_messages=False, connect = False),
            self.senateRole: PermissionOverwrite(read_messages=False, send_messages=False, connect=False),
            self.emperorRole: PermissionOverwrite(read_messages=True, send_messages=True, connect=True, move_members=True, mute_members=True, deafen_members=True),
            self.custodianRole: PermissionOverwrite(read_messages=True, send_messages=True, connect=True, move_members=True, mute_members=True)
            }
    
    def getHiddenOverwrite(self):
        return {
            self.guild.default_role: PermissionOverwrite(read_messages=False, send_messages=False, connect=False)
        }

    async def found(self):
        
        self.memberRole = await self.guild.create_role(name=GalacticCommunity.member)
        self.senateRole = await self.guild.create_role(name=GalacticCommunity.senator)
        self.custodianRole = await self.guild.create_role(name=GalacticCommunity.custodian)
        self.emperorRole = await self.guild.create_role(name=GalacticCommunity.emperor)

        self.category = await self.guild.create_category(GalacticCommunity.category_name, position=1)

        self.announce_channel = await self.category.create_text_channel(GalacticCommunity.announce_channel_name, overwrites=self.getHeadOverwrite())
        self.public_channel = await self.category.create_text_channel(GalacticCommunity.public_channel_name, overwrites=self.getOverwriteStandard())
        self.news_channel = await self.category.create_text_channel(GalacticCommunity.news_channel_name, overwrites=self.getOverwriteStandard())

        self.lower_chamber_text = await self.category.create_text_channel(GalacticCommunity.lower_chamber, overwrites=self.getOverwriteStandard())
        self.lower_chamber = await self.category.create_voice_channel(GalacticCommunity.lower_chamber, overwrites=self.getOverwriteStandard())
        
        self.upper_chamber_text = await self.category.create_text_channel(GalacticCommunity.upper_chamber, overwrites=self.getHiddenOverwrite())
        self.upper_chamber = await self.category.create_voice_channel(GalacticCommunity.upper_chamber, overwrites=self.getHiddenOverwrite())

        self.forum0 = await self.category.create_voice_channel(GalacticCommunity.forum0, overwrites=self.getOverwriteStandard())
        self.forum1 = await self.category.create_voice_channel(GalacticCommunity.forum1, overwrites=self.getOverwriteStandard())
        self.forum2 = await self.category.create_voice_channel(GalacticCommunity.forum2, overwrites=self.getOverwriteStandard())
        self.forum3 = await self.category.create_voice_channel(GalacticCommunity.forum3, overwrites=self.getOverwriteStandard())
        await self.category.edit(position=1)

    async def set_custodian(self, member: Member):
        self.custodian = member
        await self.custodian.add_roles(self.custodianRole)
        await self.announce_channel.send(f"{self.custodian.mention} has been elected as Custodian")
    
    async def remove_custodian(self):
        await self.custodian.remove_roles(self.custodianRole)
        self.custodian = None
        await self.announce_channel.send(f"{self.custodian.mention} has been removed as Custodian")
    
    async def switch_custodian(self, member: Member):
        await self.senate()
        if self.custodian == member:
            await self.announce_channel.send(f"{member.mention} has been re-elected as the Custodian")
            return
        await self.custodian.remove_roles(self.custodianRole)
        await self.announce_channel.send(f"{self.custodian.mention} has been removed as Custodian")
        self.custodian = member
        await self.announce_channel.send(f"{self.custodian.mention} has been elected as Custodian")
        await self.custodian.add_roles(self.custodianRole)

    async def senate(self):
        await self.upper_chamber.edit(name=GalacticCommunity.upper_chamber, overwrites=self.getOverwriteSenate())
        await self.upper_chamber_text.edit(name=GalacticCommunity.upper_chamber, overwrites=self.getOverwriteSenate())

    async def empire(self):
        await self.custodian.remove_roles(self.custodianRole)
        self.emperor = self.custodian
        self.custodian = None
        await self.emperor.add_roles(self.emperorRole)

        await self.upper_chamber.edit(name=GalacticCommunity.upper_chamber_empire, overwrites=self.getOverwriteSenate())
        await self.upper_chamber_text.edit(name=GalacticCommunity.upper_chamber_empire, overwrites=self.getOverwriteSenate())

        await self.lower_chamber.edit(name=GalacticCommunity.lower_chamber_empire, overwrites=self.getOverwriteStandard())
        await self.lower_chamber_text.edit(name=GalacticCommunity.lower_chamber_empire, overwrites=self.getOverwriteStandard())
    
    async def disbandEmpire(self):
        if not self.emperor:
            return
        await self.emperor.remove_roles(self.emperorRole)
        self.emperor = None

        await self.upper_chamber.edit(name=GalacticCommunity.upper_chamber, overwrites=self.getOverwriteSenate())
        await self.upper_chamber_text.edit(name=GalacticCommunity.upper_chamber, overwrites=self.getOverwriteSenate())
    
    async def disbandSenate(self):
        if len(self.senateMembers) == 0:
            return
        await self.upper_chamber.edit(overwrites=self.getHiddenOverwrite())
        await self.upper_chamber_text.edit(overwrites=self.getHiddenOverwrite())
        for member in self.senateMembers:
            await member.remove_roles(self.senateRole)
        self.senateMembers = []
    
    async def set_senate(self, members: List[Member]):
        verb = "elected"
        if self.emperor:
            verb = "appointed"
        
        for member in self.senateMembers:
            if member not in members:
                await self.announce_channel.send(f"{member.mention} has been removed from the Galactic Senate")
                self.senateMembers.remove(member)
                await member.remove_roles(self.senateRole)
        
        for member in members:
            if member not in self.senateMembers:
                await self.announce_channel.send(f"{member.mention} has been {verb} to the Galactic Senate")
            else:
                await self.announce_channel.send(f"{member.mention} has been re-{verb} to the Galactic Senate")
            await member.add_roles(self.senateRole)
        self.senateMembers = members

class GameState(Enum):
    ENDED = 0
    STARTED = 1,
    STOPPED = 2,

class PlayerManager:
    
    ManagerStore = {}

    def __init__(self, guild):
        self.playerStore = {}
        self.allianceStore = {}
        self.galcom = None
        self.marked_for_archive = []
        self.guild = guild
        self.gameState: GameState = GameState.ENDED
        self.is_init = False
        self.gameName = dt.now().strftime("%Y-%m-%d %H-%M-%S")
        print("PlayerManager created")
    
    @staticmethod
    def get_manager(guild: Guild):
        if guild.id in PlayerManager.ManagerStore:
            print("Returning existing manager")
            return PlayerManager.ManagerStore[guild.id]
        else:
            print("Creating new manager")
            PlayerManager.ManagerStore[guild.id] = PlayerManager(guild)
            return PlayerManager.ManagerStore[guild.id]
    
    def init(self, name: str):
        self.gameName = name
        self.is_init = True
        self.gameState = GameState.STARTED

    def start(self):
        self.gameState = GameState.STARTED
    
    def stop(self):
        self.gameState = GameState.STOPPED

    def get_gameState(self):
        return self.gameState

    async def found_galcom(self):
        self.galcom = GalacticCommunity(self.guild)
        await self.galcom.found()
    
    def get_galcom(self) -> GalacticCommunity:
        return self.galcom

    def get_player(self, member) -> Player:
        player = self.playerStore.get(member.id, None)
        #Check if member is in 
        if player is None:
            self.playerStore[member.id] = Player(member)
            return self.playerStore[member.id]
        return player
    
    def add_alliance(self, alliance: Alliance):
        self.allianceStore[alliance.name] = alliance
        print(self.allianceStore)

    def get_alliance(self, name: str) -> Alliance:
        return self.allianceStore.get(name)
    
    async def rename_alliance(self, alliance: Alliance, new_name: str):
        del self.allianceStore[alliance.name]
        await alliance.rename(new_name)
        self.allianceStore[alliance.name] = alliance
    
    async def delete_alliance(self, alliance: Alliance):
        del self.allianceStore[alliance.name]
        for member in alliance.members:
            await member.remove_roles(alliance.role)
        await alliance.role.delete()
        await alliance.category.delete()
        await alliance.voice_channel.delete()
        
        # Check the message history of the text channel
        async for message in alliance.text_channel.history(limit=100):
            if message.author != alliance.guild.me:
                # If any message is not written by the bot, do not delete the channel
                self.marked_for_archive.append(alliance.text_channel)
                await alliance.text_channel.edit(overwrites={
                    alliance.guild.default_role: PermissionOverwrite(view_channel=False)
                })
                return
        
        # If all messages are written by the bot, delete the channel
        await alliance.text_channel.delete()

    async def conclude(self):

        if self.galcom:
            await self.galcom.disbandEmpire()
            await self.galcom.disbandSenate()
            await self.galcom.lower_chamber.delete()
            await self.galcom.upper_chamber.delete()
            await self.galcom.forum0.delete()
            await self.galcom.forum1.delete()
            await self.galcom.forum2.delete()
            await self.galcom.forum3.delete()
            await self.conditionalDelete(self.galcom.announce_channel)
            await self.conditionalDelete(self.galcom.public_channel)
            await self.conditionalDelete(self.galcom.news_channel)
            await self.conditionalDelete(self.galcom.lower_chamber_text)
            await self.conditionalDelete(self.galcom.upper_chamber_text)
            
            await self.galcom.category.delete()
            
            await self.galcom.memberRole.delete()
            await self.galcom.senateRole.delete()
            await self.galcom.custodianRole.delete()
            await self.galcom.emperorRole.delete()

            self.galcom = None

        for alliance in self.allianceStore.values():
            await self.delete_alliance(alliance)
        if len(self.marked_for_archive) <= 0:
            self.gameState = GameState.ENDED
            return
        category = await self.guild.create_category(f"Archive {self.gameName}")



        for channel in self.marked_for_archive:
            await channel.edit(category=category)
        self.marked_for_archive = []
        self.gameState = GameState.ENDED
        return
    
    async def conditionalDelete(self, channel: TextChannel):
        async for message in channel.history(limit=100):
            if message.author != self.guild.me:
                # If any message is not written by the bot, do not delete the channel
                await channel.edit(overwrites={
                    self.guild.default_role: PermissionOverwrite(view_channel=False)
                })
                self.marked_for_archive.append(channel)
                return
        await channel.delete()
        return