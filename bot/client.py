from discord.ext import commands
import discord
import os

from bot.events.points import *
from bot.config.cogs_list import *
from bot.database import db, TableName

class Client(commands.Bot):
	def __init__(self):
		intents = discord.Intents.all()
		super().__init__(intents=intents, command_prefix="s!", help_command=None)

		try:
			db.connect()
		except Exception as e:
			print("Error while connecting to the database: ", e)

		self.db = db
		self.points_event = Points(self)

	async def setup_hook(self):
		"""
		This function is a coroutine.\n
		A coroutine to be called to setup the bot, by default this is blank.\n
		To perform asynchronous setup after the bot is logged in but before it has connected to the Websocket, overwrite this coroutine.\n
		This is only called once, in login(), and will be called before any events are dispatched, making it a better solution than doing such setup in the on_ready() event.
		"""
		print("Setting up the bot...")
		
		self.fetch_guilds_config()

		await load_cogs(self, cogs)

	def fetch_guilds_config(self):
		self.guilds_config = {}
		all_guilds = [guild["guild_id"] for guild in self.db.select(TableName.GUILDS.value, ["guild_id"])]
		for guild in all_guilds:
			blacklisted_channel = self.db.select(TableName.CHANNELS.value, ["channel_id"], {"guild_id": guild})
			self.guilds_config[guild] = {"blacklisted_channel": blacklisted_channel}
		print("Guilds config fetched")

	async def on_ready(self):
		await self.wait_until_ready()

		for guild in self.guilds:
			if guild.id not in self.guilds_config.keys():
				self.db.insert(TableName.GUILDS.value, {"guild_id": guild.id})
			await self.tree.sync(guild=guild)
		await self.tree.sync()
		
		print("-----------------------------------------")
		print(f'{self.user} is ready')
		print("ID: " + str(self.user.id))
		print("Prefix: " + self.command_prefix)
		print("Version de Discord: " + str(discord.__version__))
		print(f'In {len(self.guilds)} server: {", ".join([guild.name for guild in self.guilds])}')
		print("-----------------------------------------")
	
	async def on_message(self, message: discord.Message):
		if message.author.bot:
			return
		
		if message.channel.id not in [channel["channel_id"] for channel in self.guilds_config[message.guild.id]["blacklisted_channel"]]:
			await self.points_event.process_message(message)