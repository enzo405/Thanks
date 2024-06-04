import discord

from bot.database import db, TableName

class Counter:
	"""
	This class is used for processing counter message.
	"""

	def __init__(self, bot:discord.Client):
		self.bot = bot

	async def process_counter(self, message:discord.Message):
		"""
		Process the counter message.
		"""

		await message.channel.send(content="Counter message received!")