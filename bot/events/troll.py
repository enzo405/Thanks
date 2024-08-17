import discord
import random

from bot.database import db, TableName

class Troll:
	"""
	This class is used for trolling.
	"""

	def __init__(self, bot:discord.Client):
		self.bot = bot
		self.troll_sentence = [
			"you are the reason why power rangers scream their color",
			"you must be the square root of -1 because you can't be real",
			"you are the reason why the gene pool needs a lifeguard",
			"you are the reason why the middle finger was invented",
			"you are the reason why the soap has instructions",
			"you use the light switch to turn off the sun",
			"calendars fear the day you were born",
			"discord should add a dislike button just for you",
			"your dad should have pulled out",
			"you are the reason why the average life expectancy is decreasing",
			"you are the reason why the aliens won't talk to us",
			"maybe you should eat some makeup so you can be pretty on the inside",
			"the only thing you are good at is being a waste of oxygen",
			"why don't you slip into something more comfortable? Like a coma",
			"some people are like slinkies, they are not really good for anything but they bring a smile to your face when you push them down the stairs",
			"your birth certificate is an apology letter from the condom factory",
			"the only way you will ever get laid is if you crawl up a chicken"
			"you are the best at being the worst",
			"somebody call animal control, we have a wild pig on the loose",
			"that's a nice face, too bad it's not yours",
			"apple should make a device that can make you disappear",
			"you look like someone that knows marker's taste",
			"you're IQ is lower than your shoe size",
			"it was a good idea to go school, but don't stop at the portal",
			"your family tree looks like a cirlce",
			"the nurse when you were born mistaken the cradle with the microwave",
			"you were cradled too close to the wall when you were a baby",
			"you look like someone that tried to peel a rock",
			"you're as usefull as a paperclip in a swimming pool",
			"your cradle was in fire and the nurse put it out with a fork",
			"ven insulting you would direspect the insult",
			"Luckily the speed of light is faster than the speed of sound, so you finally have a chance to look bright before you open your mouth",
			"if one day it's raining, you'll be the one to get out with a fork"
		]

	async def process_message(self, message:discord.Message):
		"""
		Process the message.
		"""
		
		choosen_troll = self.troll_sentence[random.randint(0, len(self.troll_sentence) - 1)]

		await message.reply(content=choosen_troll)