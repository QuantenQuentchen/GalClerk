from typing import List
from discord import Member

from Backend.Alliance import Alliance


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