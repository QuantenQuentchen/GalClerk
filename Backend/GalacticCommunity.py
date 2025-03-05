from typing import List, Set
from discord import Member, PermissionOverwrite, Guild, Role, VoiceChannel, TextChannel, CategoryChannel

from Backend.Player import Player

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
