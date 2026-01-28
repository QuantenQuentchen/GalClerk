from discord import Bot


class BotManager:
    bot: Bot = None

    @staticmethod
    def setBot(bot: Bot):
        BotManager.bot = bot

    @staticmethod
    def getBot():
        return BotManager.bot
    