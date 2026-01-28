async def hasUserText(text_channel, guild) -> bool:
    async for message in text_channel.history(limit=100):
        if message.author != guild.me:
            return True
    return False