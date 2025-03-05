from enum import Enum
from datetime import datetime as dt
from discord import Guild, PermissionOverwrite, TextChannel

from Backend.Alliance import Alliance
from Backend.GalacticCommunity import GalacticCommunity
from Backend.Player import Player

class GameState(Enum):
    ENDED = 0
    STARTED = 1,
    STOPPED = 2,

class GameManager:
    
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
        if guild.id in GameManager.ManagerStore:
            print("Returning existing manager")
            return GameManager.ManagerStore[guild.id]
        else:
            print("Creating new manager")
            GameManager.ManagerStore[guild.id] = GameManager(guild)
            return GameManager.ManagerStore[guild.id]
    
    def init(self, name: str):
        self.gameName = name
        self.is_init = True
        self.gameState = GameState.STARTED

    def start(self):
        self.gameState = GameState.STARTED
    
    def stop(self):
        self.gameState = GameState.STOPPED
    
    def can_act(self):
        return self.gameState == GameState.STARTED

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