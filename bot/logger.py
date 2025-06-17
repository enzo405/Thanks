import discord
import os


class Logger:
    def __init__(self, bot: discord.Client):
        self.bot = bot

    async def setup(self):
        channel_id = os.getenv("LOG_CHANNEL_ID", "0")

        if len(channel_id) not in [17, 18, 19]:
            raise ValueError("Channel ID invalid.")

        self.channel = await self.bot.fetch_channel(channel_id)

    async def info(self, message: str):
        print(f"[INFO]: {message}")
        await self.channel.send(f"[INFO] {message}")

    async def warning(self, message: str):
        print(f"[WARNING]: {message}")
        await self.channel.send(f"[WARNING] {message}")

    async def error(self, message: str):
        print(f"[ERROR]: {message}")
        await self.channel.send(f"[ERROR] {message}")

    async def debug(self, message: str):
        print(f"[DEBUG]: {message}")
        await self.channel.send(f"[DEBUG] {message}")
