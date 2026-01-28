from discord import TextChannel, Guild, PermissionOverwrite

from Backend.Util import hasUserText

class HistoryManager:

    HistoryStore = {}

    def __init__(self, guild: Guild):
        self.archive = []
        self.guild = guild
        self.HistoryStore[guild.id] = self
        self.category = None

    async def add_or_delete_text_channel(self, text_channel: TextChannel):
        if await hasUserText(text_channel, self.guild):
            self.archive.append(text_channel)
            await text_channel.edit(overwrites={
                self.guild.default_role: PermissionOverwrite(view_channel=False)
            })
        else:
            await text_channel.delete()

    async def writeHistory(self, name: str):
        if not self.archive: return
        self.category = await self.guild.create_category(f"Archive {name}")
        for channel in self.archive:
            await channel.edit(category=self.category, overwrites={self.guild.default_role: PermissionOverwrite(view_channel=True, read_message_history=True, send_messages=False)})

    @classmethod
    def get_manager(cls, guild: Guild) -> 'HistoryManager':
        manager = cls.HistoryStore.get(guild.id)
        if manager is None:
            manager = HistoryManager(guild)
        return manager
