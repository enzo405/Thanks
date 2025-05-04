import discord
import datetime
from typing import List, Optional

from bot.database import db, TableName


class PointsConfig:
    """Configuration for the points system."""

    cooldown_minutes: int = 2
    daily_limit: int = 5
    thank_words: List[str] = [
        "ty",
        "tyvm",
        "tysm",
        "tyty",
        "thank",
        "thanks",
        "thx",
        "thnx",
    ]
    embed_color: int = 0x1E1F22
    message_timeout: int = 120  # seconds


class PointsManager:
    """Manages points-related database operations."""

    def __init__(self, db):
        self.db = db

    def get_user_points(self, guild_id: int, user_id: int) -> Optional[dict]:
        """Get a user's points record."""
        result = self.db.select(
            TableName.POINTS.value,
            where={"guild_id": guild_id, "discord_user_id": user_id},
        )
        return result[0] if result else None

    def create_user_points(self, guild_id: int, user_id: int, points: int = 0) -> None:
        """Create a new points record for a user."""
        self.db.insert(
            TableName.POINTS.value,
            {
                "guild_id": guild_id,
                "discord_user_id": user_id,
                "points": points,
                "last_thanks": datetime.datetime.now(),
                "num_of_thanks": 0,
            },
        )

    def update_user_points(
        self, guild_id: int, user_id: int, points_delta: int = 1
    ) -> None:
        """Update a user's points."""
        current = self.get_user_points(guild_id, user_id)
        if current:
            self.db.update(
                TableName.POINTS.value,
                {"points": current["points"] + points_delta},
                {"guild_id": guild_id, "discord_user_id": user_id},
            )
        else:
            self.create_user_points(guild_id, user_id, points_delta)

    def update_has_thanked_user(
        self, guild_id: int, user_id: int, user: Optional[dict] = None
    ) -> None:
        """Update the last thanked time for a user."""
        date_now = datetime.datetime.now()

        if not user:
            db.insert(
                TableName.POINTS.value,
                {
                    "guild_id": guild_id,
                    "discord_user_id": user_id,
                    "last_thanks": date_now,
                    "num_of_thanks": 1,
                },
            )
        else:
            db.update(
                TableName.POINTS.value,
                {
                    "last_thanks": date_now,
                    "num_of_thanks": user["num_of_thanks"] + 1,
                },
                {"guild_id": guild_id, "discord_user_id": user_id},
            )


class PointsValidator:
    """Handles validation of points-related operations."""

    def __init__(self, config: PointsConfig):
        self.config = config

    def get_daily_user_stat(self) -> int:
        """Get the daily limit for points."""
        return self.config.daily_limit

    def is_valid_thank_message(self, message: discord.Message) -> bool:
        """Check if a message contains a valid thank word."""
        words = message.content.lower().split()
        return any(word in words for word in self.config.thank_words)

    def get_mentioned_users(self, message: discord.Message) -> List[int]:
        """Get the list of valid mentioned users from a message."""
        users = []

        if (
            message.reference
            and message.reference.resolved
            and isinstance(message.reference.resolved, discord.Message)
        ):
            users.append(message.reference.resolved.author.id)

        users.extend(user.id for user in message.mentions)

        users = list(set(users))
        if message.author.id in users:
            users.remove(message.author.id)

        return users

    def is_on_cooldown(self, last_thanks: datetime.datetime) -> bool:
        """Check if a user is on cooldown or has received too many points recently."""
        if not last_thanks:
            return False
        return last_thanks > datetime.datetime.now() - datetime.timedelta(
            minutes=self.config.cooldown_minutes
        )


class Points:
    """Main points system class."""

    def __init__(self, bot: discord.Client, config: Optional[PointsConfig] = None):
        self.bot = bot
        self.config = config or PointsConfig()
        self.manager = PointsManager(db)
        self.validator = PointsValidator(self.config)

    async def process_message(self, message: discord.Message) -> None:
        """Process a message and handle points if applicable."""
        if not self.validator.is_valid_thank_message(message):
            return

        mentioned_users = self.validator.get_mentioned_users(message)
        if not mentioned_users:
            return

        sender_record = self.manager.get_user_points(
            message.guild.id, message.author.id
        )

        if sender_record and self.validator.is_on_cooldown(
            sender_record["last_thanks"]
        ):
            return

        valid_users_string = ""
        self.manager.update_has_thanked_user(
            message.guild.id, message.author.id, sender_record
        )

        for user_id in mentioned_users:
            self.manager.update_user_points(message.guild.id, user_id)
            valid_users_string += f"<@{user_id}>, "

        valid_users_string = valid_users_string[:-2]
        embed = discord.Embed(
            title="",
            description=f"{valid_users_string} received a point!",
            color=self.config.embed_color,
        )
        await message.channel.send(
            embed=embed, delete_after=self.config.message_timeout
        )
