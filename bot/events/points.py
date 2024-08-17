import discord
import datetime
import random

from bot.database import db, TableName

class Points:
	"""
	This class is used for processing message.
	"""

	def __init__(self, bot:discord.Client):
		self.bot = bot

	async def process_message(self, message:discord.Message):
		"""
		Process the message.
		"""
		# Check if the message contains either "ty" or "tyvm" or "tyty" or "tysm" or "thank you" or "thanks" or "thx" or "thnx" or "merci" or "gracias" or "danke" or "arigato" or "obrigado" or "grazie" or "dank"
		if not any([i in message.content.lower().split() for i in ["ty", "tyvm", "tyty", "tysm", "thank", "thanks", "thx", "thnx"]]):
			return

		# Check if the message contains a mention or a reply
		if message.reference and message.reference.resolved and isinstance(message.reference.resolved, discord.Message):
			mentionned_users_id = [message.reference.resolved.author.id]
		elif len(message.mentions) > 0:
			mentionned_users_id = [user.id for user in message.mentions]
		else:
			return

		user_id = random.choice(mentionned_users_id)

		# Check if the mention/answer isn't to himself
		if message.author.id == user_id:
			return

		date_now = datetime.datetime.now()
		user = db.select(TableName.POINTS.value, where={"guild_id": message.guild.id, "discord_user_id": message.author.id})

		if not user:
			db.insert(TableName.POINTS.value, {"guild_id": message.guild.id, "discord_user_id": message.author.id, "last_thanks": date_now, "num_of_thanks": 1})
			user = db.select(TableName.POINTS.value, where={"guild_id": message.guild.id, "discord_user_id": message.author.id})
		else:
			if user[0]["last_thanks"] > date_now - datetime.timedelta(minutes=2) and message.author.id != 382930544385851392:
				return
			db.update(TableName.POINTS.value, {"last_thanks": date_now, "num_of_thanks": user[0]["num_of_thanks"] + 1}, {"guild_id": message.guild.id, "discord_user_id": message.author.id})

		target = db.select(TableName.POINTS.value, where={"guild_id": message.guild.id, "discord_user_id": user_id})

		if not target:
			db.insert(TableName.POINTS.value, {"guild_id": message.guild.id, "discord_user_id": user_id, "points": 1})
		else:
			db.update(TableName.POINTS.value, {"points": target[0]["points"] + 1}, {"guild_id": message.guild.id, "discord_user_id": user_id})
		
		# Send a message to the channel
		embed = discord.Embed(title="", description=f"<@{user_id}> has received a point!", color=0x1e1f22)
		await message.channel.send(embed=embed)