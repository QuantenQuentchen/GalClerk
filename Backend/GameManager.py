from datetime import datetime as dt
from enum import Enum

from discord import Guild

# from Backend.Alliance import Alliance
from Backend.GalacticCommunity import GalacticCommunity
from Backend.History import HistoryManager
from Backend.Lock import Lock
from Backend.Player import Player


class GameState(Enum):
    ENDED = 0
    STARTED = 1,
    STOPPED = 2,
    PAUSED = 3,
    CREATED = 4

class GameManager:
    
    ManagerStore = {}

    @classmethod
    async def create(cls, guild: Guild):
        manager = cls(guild)
        await manager.init()
        return manager

    def __init__(self, guild):
        self.playerStore = {}
        self.allianceStore = {}
        self.galcom = None
        self.guild = guild
        self.gameState: GameState = GameState.CREATED
        self.gameName = dt.now().strftime("%Y-%m-%d %H-%M-%S")
        self.HM: HistoryManager = HistoryManager.get_manager(guild)
        self.lock: Lock | None = None
        print("PlayerManager created")
    
    @staticmethod
    async def get_manager(guild: Guild):
        if guild.id in GameManager.ManagerStore:
            return GameManager.ManagerStore[guild.id]
        else:
            GameManager.ManagerStore[guild.id] = await GameManager.create(guild)
            return GameManager.ManagerStore[guild.id]
    
    async def init(self):
        self.lock = await Lock.create(self.guild)

    async def start(self):
        self.gameState = GameState.STARTED
        for ch in self.guild.channels:
            await self.lock.addLockableChannel(ch)
        await self.lock.lock()

    async def pause(self):
        self.gameState = GameState.STOPPED
        await self.lock.unlock()
    
    async def end(self):
        await self.lock.delete()
        self.lock = None
        if self.galcom: await self.galcom.delete()
        self.galcom = None

        for alliance in self.allianceStore.values():
            await alliance.delete()
        self.allianceStore = {}
        await self.HM.writeHistory(self.gameName)
        self.ManagerStore.pop(self.guild.id, None)
    
    def can_act(self):
        return self.gameState == GameState.STARTED

    def get_gameState(self):
        return self.gameState

    async def found_galcom(self):
        self.galcom = await GalacticCommunity.create(self.guild)

    def get_galcom(self) -> GalacticCommunity:
        return self.galcom

    def get_player(self, member) -> Player:
        player = self.playerStore.get(member.id, None)
        if player is None:
            self.playerStore[member.id] = Player(member)
            return self.playerStore[member.id]
        return player
    
    def add_alliance(self, alliance: 'Alliance'):
        self.allianceStore[alliance.name] = alliance
        print(self.allianceStore)

    def get_alliance(self, name: str) -> 'Alliance':
        return self.allianceStore.get(name)
    
    async def rename_alliance(self, alliance: 'Alliance', new_name: str):
        del self.allianceStore[alliance.name]
        await alliance.rename(new_name)
        self.allianceStore[alliance.name] = alliance

    def is_stopped(self):
        return self.gameState == GameState.STOPPED

    def is_created(self): return self.gameState == GameState.CREATED

    def is_started(self): return self.gameState == GameState.STARTED