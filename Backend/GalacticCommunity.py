from enum import Enum
from typing import List, Set
from discord import Member, PermissionOverwrite, Guild, Role, VoiceChannel, TextChannel, CategoryChannel

from Backend.History import HistoryManager
from Backend.Player import Player

class GC_State(Enum):
    NONE = 0,
    SENATE = 1,
    EMPIRE = 2


class GalacticCommunity:

    category_name = "🌌galactic-community"

    member = "👤Member"
    senator = "🏛️Councilor"
    custodian = "🛡️Custodian"
    emperor = "👑Emperor"

    announce_channel_name = "📃announcements"
    announce_channel_name_empire = "👑📃imperial-decrees"

    public_channel_name = "📑public-galactic"
    public_channel_name_empire = "👑📑imperial-public"

    news_channel_name = "📰xenonion-news"
    news_channel_name_empire = "👑📰imperial-news"

    lower_chamber = "🏛️galactic-assembly"
    lower_chamber_empire = "👑imperial-senate"

    upper_chamber = "🏛️galactic-council"
    upper_chamber_empire = "👑imperial-court"

    head_chamber = "🏛️custodian-office"
    head_chamber_empire = "👑emperor-throne-room"

    forum0 = "📜Galactic Forum"
    forum1 = "📜Galactic Forum"
    forum2 = "📜Galactic Forum"
    forum3 = "📜Galactic Forum"

    def getAnnounceName(self):
        if self.state == GC_State.EMPIRE: return GalacticCommunity.announce_channel_name_empire
        return GalacticCommunity.announce_channel_name

    def getPublicName(self):
        if self.state == GC_State.EMPIRE: return GalacticCommunity.public_channel_name_empire
        return GalacticCommunity.public_channel_name

    def getNewsName(self):
        if self.state == GC_State.EMPIRE: return GalacticCommunity.news_channel_name_empire
        return GalacticCommunity.news_channel_name

    def getLowerChamberName(self):
        if self.state == GC_State.EMPIRE: return GalacticCommunity.lower_chamber_empire
        return GalacticCommunity.lower_chamber

    def getUpperChamberName(self):
        if self.state == GC_State.EMPIRE: return GalacticCommunity.upper_chamber_empire
        return GalacticCommunity.upper_chamber

    def getHeadChamberName(self):
        if self.state == GC_State.EMPIRE: return GalacticCommunity.head_chamber_empire
        return GalacticCommunity.head_chamber

    @classmethod
    async def create(cls, guild):
        galcom = cls(guild)
        await galcom.found()
        return galcom

    def __init__(self, guild):
        self.state = GC_State.NONE
        self.guild: Guild = guild
        self.HM = HistoryManager.get_manager(guild)

        self.members: List[Member] = []
        self.memberRole: Role | None = None
        
        self.category: CategoryChannel | None = None
        self.announce_channel: TextChannel | None = None
        self.public_channel: TextChannel | None = None
        self.news_channel: TextChannel | None= None

        self.lower_chamber_text: TextChannel | None = None
        self.lower_chamber: VoiceChannel | None = None

        self.upper_chamber_text: TextChannel | None = None
        self.upper_chamber: VoiceChannel | None = None

        self.head_chamber_voice: VoiceChannel | None = None
        self.head_chamber_text: TextChannel | None = None

        self.forum0: VoiceChannel | None= None
        self.forum1: VoiceChannel | None = None
        self.forum2: VoiceChannel | None = None
        self.forum3: VoiceChannel | None = None

        self.custodianRole: Role | None = None
        self.custodian: Member | None = None

        self.emperorRole: Role | None = None
        self.emperor: Member | None = None

        self.senateRole: Role | None = None
        self.senateMembers: List[Member] = []
        self.forbiddenSet: Set[Member] = set()

    async def found(self):
        self.memberRole = await self.guild.create_role(name=GalacticCommunity.member)
        self.senateRole = await self.guild.create_role(name=GalacticCommunity.senator)
        self.custodianRole = await self.guild.create_role(name=GalacticCommunity.custodian)
        self.emperorRole = await self.guild.create_role(name=GalacticCommunity.emperor)

        self.category = await self.guild.create_category(GalacticCommunity.category_name, position=1)

        self.announce_channel = await self.category.create_text_channel(GalacticCommunity.announce_channel_name,
                                                                        overwrites=self.getOverwriteAnnounce())
        self.public_channel = await self.category.create_text_channel(GalacticCommunity.public_channel_name,
                                                                      overwrites=self.getOverwriteStandard())
        self.news_channel = await self.category.create_text_channel(GalacticCommunity.news_channel_name,
                                                                    overwrites=self.getOverwriteStandard())

        self.lower_chamber_text = await self.category.create_text_channel(GalacticCommunity.lower_chamber,
                                                                          overwrites=self.getOverwriteStandard())
        self.lower_chamber = await self.category.create_voice_channel(GalacticCommunity.lower_chamber,
                                                                      overwrites=self.getOverwriteStandard())

        self.upper_chamber_text = await self.category.create_text_channel(GalacticCommunity.upper_chamber,
                                                                          overwrites=self.getOverwriteSenate())
        self.upper_chamber = await self.category.create_voice_channel(GalacticCommunity.upper_chamber,
                                                                      overwrites=self.getOverwriteSenate())

        self.head_chamber_voice = await self.category.create_voice_channel(GalacticCommunity.head_chamber, overwrites=self.getOverwriteHead())
        self.head_chamber_text = await self.category.create_text_channel(GalacticCommunity.head_chamber, overwrites=self.getOverwriteHead())

        self.forum0 = await self.category.create_voice_channel(GalacticCommunity.forum0,
                                                               overwrites=self.getOverwriteForum())
        self.forum1 = await self.category.create_voice_channel(GalacticCommunity.forum1,
                                                               overwrites=self.getOverwriteForum())
        self.forum2 = await self.category.create_voice_channel(GalacticCommunity.forum2,
                                                               overwrites=self.getOverwriteForum())
        self.forum3 = await self.category.create_voice_channel(GalacticCommunity.forum3,
                                                               overwrites=self.getOverwriteForum())
        await self.category.edit(position=1)
        self.state = GC_State.SENATE

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
        if not self.is_member(player.member): return
        if self.is_councilor(player.member):
            await player.member.remove_roles(self.memberRole)
            self.senateMembers.remove(player.member)
            await player.member.remove_roles(self.senateRole)
            await self.announce_channel.send(f"{player.member.mention} has resigned from the Galactic Senate, and left the Galactic Community")
            self.members.remove(player.member)
            return
        if self.is_head(player.member):
            await self.announce_channel.send(f"{player.member.mention} tried to abandon their post as {'Emperor' if player.member == self.emperor else 'Custodian'}, but the Galaxy will not allow it!")
            return
        await self.announce_channel.send(f"{player.member.mention} has left the Galactic Community")
        await player.member.remove_roles(self.memberRole)
        self.members.remove(player.member)

    async def add_player(self, player: Player):
        await player.member.add_roles(self.memberRole)
        self.members.append(player.member)
        if not self.state == GC_State.EMPIRE:
            await self.announce_channel.send(f"{player.member.mention} has joined the Galactic Community")
            return
        await self.announce_channel.send(f"{player.member.mention} has joined the Galactic Empire")
        return

    def getOverwriteForum(self):
        return {
            self.guild.default_role: PermissionOverwrite(read_messages=True, send_messages=True, connect=True),
            self.memberRole: PermissionOverwrite(read_messages=True, send_messages=True, connect = True),
            self.senateRole: PermissionOverwrite(read_messages=True, send_messages=True, connect=True),
            self.emperorRole: PermissionOverwrite(read_messages=True, send_messages=True, connect=True, move_members=True, mute_members=True, deafen_members=True, manage_messages=True),
            self.custodianRole: PermissionOverwrite(read_messages=True, send_messages=True, connect=True, move_members=False)
        }

    def getOverwriteStandard(self):
        return {
            self.guild.default_role: PermissionOverwrite(read_messages=False, send_messages=False, connect=False),
            self.memberRole: PermissionOverwrite(read_messages=True, send_messages=True, connect = True),
            self.senateRole: PermissionOverwrite(read_messages=True, send_messages=True, connect=True),
            self.emperorRole: PermissionOverwrite(read_messages=True, send_messages=True, connect=True, move_members=True, mute_members=True, deafen_members=True, manage_messages=True),
            self.custodianRole: PermissionOverwrite(read_messages=True, send_messages=True, connect=True, move_members=True)
        }
    
    def getOverwriteSenate(self):
        return {
            self.guild.default_role: PermissionOverwrite(read_messages=False, send_messages=False, connect=False),
            self.memberRole: PermissionOverwrite(read_messages=False, send_messages=False, connect = False),
            self.senateRole: PermissionOverwrite(read_messages=True, send_messages=True, connect=True),
            self.emperorRole: PermissionOverwrite(read_messages=True, send_messages=True, connect=True, move_members=True, mute_members=True, deafen_members=True, manage_messages=True),
            self.custodianRole: PermissionOverwrite(read_messages=True, send_messages=True, connect=True, move_members=True),
            }
    
    def getOverwriteAnnounce(self):
        return {
            self.guild.default_role: PermissionOverwrite(read_messages=True, send_messages=False, connect=False),
            self.memberRole: PermissionOverwrite(read_messages=True, send_messages=False, connect = False),
            self.senateRole: PermissionOverwrite(read_messages=True, send_messages=False, connect=False),
            self.emperorRole: PermissionOverwrite(read_messages=True, send_messages=True, connect=True, move_members=True, mute_members=True, deafen_members=True, manage_messages=True),
            self.custodianRole: PermissionOverwrite(read_messages=True, send_messages=True, connect=True, move_members=True)
            }

    def getOverwriteHead(self):
        return {
            self.guild.default_role: PermissionOverwrite(read_messages=False, send_messages=False, connect=False),
            self.memberRole: PermissionOverwrite(read_messages=False, send_messages=False, connect = False),
            self.senateRole: PermissionOverwrite(read_messages=False, send_messages=False, connect=False),
            self.emperorRole: PermissionOverwrite(read_messages=True, send_messages=True, connect=True, move_members=True, mute_members=True, deafen_members=True, manage_messages=True),
            self.custodianRole: PermissionOverwrite(read_messages=True, send_messages=True, connect=True, move_members=True)
            }

    def getHiddenOverwrite(self):
        return {
            self.guild.default_role: PermissionOverwrite(read_messages=False, send_messages=False, connect=False)
        }

    async def setCustodian(self, member: Member):
        if self.custodian is None:
            self.custodian = member
            await self.custodian.add_roles(self.custodianRole)
            await self.announce_channel.send(
                f"{self.custodian.mention} has been elected as the first ever Galactic Custodian")
        else:
            await self.switch_custodian(member)

    async def removeCustodian(self):
        await self.custodian.remove_roles(self.custodianRole)
        self.custodian = None
        await self.announce_channel.send(f"{self.custodian.mention} has been removed as Custodian, and the Position abolished.")
    
    async def switch_custodian(self, member: Member):
        if self.custodian == member:
            await self.announce_channel.send(f"{member.mention} has been re-elected as the Custodian")
            return
        await self.custodian.remove_roles(self.custodianRole)
        await self.announce_channel.send(f"{self.custodian.mention} has failed to be re-elected. It seems like the Galaxy trusts {member.mention} more as Custodian.")
        self.custodian = member
        await self.custodian.add_roles(self.custodianRole)

    async def setEmpire(self):
        if self.state == GC_State.EMPIRE: return
        self.state = GC_State.EMPIRE
        await self.custodian.remove_roles(self.custodianRole)
        await self._rename_channels()
        self.emperor = self.custodian
        self.custodian = None
        await self.emperor.add_roles(self.emperorRole)
        await self.announce_channel.send(f"{self.emperor.mention} has proclaimed the Galactic Empire, in the Name of **PEACE**, **JUSTICE**, and **SECURITY**!")

    async def _rename_channels(self):
        await self.announce_channel.edit(name=self.getAnnounceName(), overwrites=self.getOverwriteAnnounce())
        await self.public_channel.edit(name=self.getPublicName(), overwrites=self.getOverwriteStandard())
        await self.news_channel.edit(name=self.getNewsName(), overwrites=self.getOverwriteStandard())

        await self.lower_chamber.edit(name=self.getLowerChamberName(), overwrites=self.getOverwriteStandard())
        await self.lower_chamber_text.edit(name=self.getLowerChamberName(), overwrites=self.getOverwriteStandard())

        await self.upper_chamber.edit(name=self.getUpperChamberName(), overwrites=self.getOverwriteSenate())
        await self.upper_chamber_text.edit(name=self.getUpperChamberName(), overwrites=self.getOverwriteSenate())

        await self.head_chamber_voice.edit(name=self.getHeadChamberName(), overwrites=self.getOverwriteHead())
        await self.head_chamber_text.edit(name=self.getHeadChamberName(), overwrites=self.getOverwriteHead())

    async def setSenate(self):
        if self.state == GC_State.SENATE: return
        self.state = GC_State.SENATE
        await self._rename_channels()
        if self.emperor:
            await self.emperor.remove_roles(self.emperorRole)
            await self.announce_channel.send(f"The tyranny of {self.emperor.mention}, has finally come to an end!")
            self.emperor = None

    async def disbandSenate(self):
        if len(self.senateMembers) == 0:
            return
        for member in self.senateMembers:
            await member.remove_roles(self.senateRole)
        self.senateMembers = []
        await self.announce_channel.send(f"The Galactic Senate has been disbanded")
    
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

    async def delete(self):
        await self.lower_chamber.delete()
        await self.upper_chamber.delete()
        await self.head_chamber_voice.delete()
        await self.forum0.delete()
        await self.forum1.delete()
        await self.forum2.delete()
        await self.forum3.delete()
        await self.HM.add_or_delete_text_channel(self.announce_channel)
        await self.HM.add_or_delete_text_channel(self.public_channel)
        await self.HM.add_or_delete_text_channel(self.news_channel)
        await self.HM.add_or_delete_text_channel(self.lower_chamber_text)
        await self.HM.add_or_delete_text_channel(self.upper_chamber_text)
        await self.HM.add_or_delete_text_channel(self.head_chamber_text)

        await self.category.delete()

        await self.memberRole.delete()
        await self.senateRole.delete()
        await self.custodianRole.delete()
        await self.emperorRole.delete()
