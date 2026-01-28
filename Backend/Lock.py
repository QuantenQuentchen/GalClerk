from discord import Guild, CategoryChannel, TextChannel, VoiceChannel, PermissionOverwrite


class Lock:

    def __init__(self, guild: Guild):
        self.guild: Guild = guild
        self.lockable = []

        self.FAQ_category: CategoryChannel | None = None
        self.FAQ_text: TextChannel | None = None
        self.FAQ_voice: VoiceChannel | None = None
        self.isInit = False

    async def init(self):
        self.FAQ_category = await self.guild.create_category("FAQ")
        self.FAQ_text = await self.FAQ_category.create_text_channel("faq-text")
        self.FAQ_voice = await self.FAQ_category.create_voice_channel("faq-voice")
        await self.FAQ_category.edit(position=50)
        self.isInit = True

    @classmethod
    async def create(cls, guild: Guild) -> 'Lock':
        lock = cls(guild)
        #await lock.init()
        return lock

    async def lock(self):
        if not self.isInit: await self.init()
        await self._lock()

    async def _lock(self):
        for channel in self.lockable:
            await self._lockChannel(channel)

    async def unlock(self):
        if not self.isInit: await self.init()
        await self._unlock()

    async def _unlock(self):
        for channel in self.lockable:
            await self._unlockChannel(channel)

    async def delete(self):
        if self.FAQ_text:
            await self.FAQ_text.delete()
        if self.FAQ_voice:
            await self.FAQ_voice.delete()
        if self.FAQ_category:
            await self.FAQ_category.delete()
        await self._unlock()

    async def addLockableChannel(self, channel):
        self.lockable.append(channel)

    async def _lockChannel(self, channel):
        await channel.edit(overwrites={
            self.guild.default_role: PermissionOverwrite(send_messages=False, connect=False),
        })

    async def _unlockChannel(self, channel):
        try:
            await channel.edit(overwrites={
                self.guild.default_role: PermissionOverwrite(send_messages=None, connect=None),
            })
        except Exception as e:
            print(f"Exception occurred while attempting to unlock channel: {e}")
            pass
