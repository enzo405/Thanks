import discord
import random


class Troll:
	"""
	This class is used for trolling.
	"""

	def __init__(self, bot:discord.Client):
		self.bot = bot
		self.troll_sentence = [
			"You are the reason why power rangers scream their color",
			"You must be the square root of -1 because you can't be real",
			"You are the reason why the gene pool needs a lifeguard",
			"You are the reason why the middle finger was invented",
			"You are the reason why the soap has instructions",
			"You use the light switch to turn off the sun",
			"Calendars fear the day you were born",
			"Discord should add a dislike button just for you",
			"Your dad should have pulled out",
			"You are the reason why the average life expectancy is decreasing",
			"You are the reason why the aliens won't talk to us",
			"Maybe you should eat some makeup so you can be pretty on the inside",
			"The only thing you are good at is being a waste of oxygen",
			"Why don't you slip into something more comfortable? Like a coma",
			"Some people are like slinkies, they are not really good for anything but they bring a smile to your face when you push them down the stairs",
			"Your birth certificate is an apology letter from the condom factory",
			"The only way you will ever get laid is if you crawl up a chicken",
			"You are the best at being the worst",
			"Somebody call animal control, we have a wild pig on the loose",
			"That's a nice face, too bad it's not yours",
			"Apple should make a device that can make you disappear",
			"You look like someone that knows marker's taste",
			"You're IQ is lower than your shoe size",
			"Going to school was a great idea, but next time don't stop in front of the portal",
			"Your family tree looks like a cirlce",
			"The nurse when you were born mistaken the cradle with the microwave",
			"You were cradled too close to the wall when you were a baby",
			"You look like someone that tried to peel a rock",
			"You're as usefull as a paperclip in a swimming pool",
			"Your cradle was in fire and the nurse put it out with a fork",
			"When insulting you would direspect the insult",
			"Luckily the speed of light is faster than the speed of sound, so you finally have a chance to look bright before you open your mouth",
			"If one day it's raining soup, you'll be the one to get out with a fork",
			"It's hard to underestimate you",
			"You're the kind of person who would move the piano closer to the drummer",
			"You're the kind of person who would shake their head in front of a fan",
			"You put the cereal before the bowl",
			"When you put a seashell against your ear, it's the seashell that hears the sea",
			"You have two neurons fighting for third place",
		]

	async def process_message(self, message:discord.Message):
		"""
		Process the message.
		"""
		
		choosen_troll = self.troll_sentence[random.randint(0, len(self.troll_sentence) - 1)]

		await message.reply(content=choosen_troll)