import discord
import re
from datetime import datetime, timedelta
from typing import List, Optional

from bot.database import db, TableName
from enum import Enum


class PointsConfig:
    """Configuration for the points system."""

    cooldown_minutes: int = 60
    daily_limit: int = 5
    thank_words: List[str] = [
        # English thank words
        "ty",
        "tyvm",
        "tysm",
        "tyty",
        "thank",
        "thanks",
        "thx",
        "thnx",
        # French thank words
        "merci",
        # Spanish thank words
        "gracias",
        "grax",
        # Russian thank words
        "спс",
        "спасибо",
        "спасиб",
        "благодарю",
        "спасибочки",
        "благодарствую",
        # Romanian thank words
        "mersi",
        "multumesc",
        "mulțumesc",
        # Ukrainian thank words
        "дякую",
        "спасибі",
        "дяк",
        # German thank words
        "danke",
    ]
    embed_color: int = 0x1E1F22
    message_timeout: int = 30  # seconds


class DailyLimitEnum(Enum):
    LIMIT_EXCEEDED = 0
    LIMIT_NOT_EXCEEDED = 1
    FIRST_POINT_OF_THE_DAY = 2


class PointsManager:
    """Manages points-related database operations."""

    def __init__(self, db, validator, bot):
        self.db = db
        self.bot = bot
        self.validator: PointsValidator = validator

    def get_user_points(self, guild_id: int, user_id: int) -> Optional[dict]:
        """Get a user's points record."""
        result = self.db.select(
            TableName.POINTS.value,
            where={"guild_id": guild_id, "discord_user_id": user_id},
        )
        return result[0] if result else None

    async def check_role_threshold(
        self, user_id: int, points: int, guild_id: int
    ) -> None:
        """Check if a user has reached the role threshold."""
        autoroles = self.db.select(
            TableName.AUTOROLES.value, where={"guild_id": guild_id}
        )
        if not autoroles or len(autoroles) == 0:
            return
        for autorole in autoroles:
            if points == autorole["threshold"]:
                role = self.bot.get_guild(guild_id).get_role(autorole["role_id"])
                if role:
                    await self.give_role(guild_id, user_id, role, autorole["threshold"])

    async def give_role(
        self, guild_id: int, user_id: int, role: discord.Role, threshold: int
    ) -> None:
        """Give a role to a user."""
        guild = self.bot.get_guild(guild_id)
        member = guild.get_member(user_id)
        if member and role not in member.roles:
            try:
                await member.add_roles(role)
                await member.send(
                    embed=discord.Embed(
                        title="Role Granted",
                        description=f"You have been given the role {role.name} for reaching {threshold} points!",
                        color=discord.Color.random(),
                    )
                )
            except Exception as e:
                await self.bot.logger.error(
                    f"Guild: {guild_id}\nFailed to add role {role.name} to {member.name}: {e}"
                )
                print(f"[ERROR] Failed to add role {role.name} to {member.name}: {e}")

    def create_user_points(self, guild_id: int, user_id: int, points: int = 0) -> None:
        """Create a new points record for a user."""
        self.db.insert(
            TableName.POINTS.value,
            {
                "guild_id": guild_id,
                "discord_user_id": user_id,
                "points": points,
                "last_thanks": datetime.now(),
                "num_of_thanks": 0,
                "last_received_points_date": datetime.now(),
                "current_day_received_points": 1,
            },
        )

    async def update_user_points(
        self, guild_id: int, user_id: int, points_delta: int = 1
    ) -> None:
        """Update a user's points."""
        current = self.get_user_points(guild_id, user_id)
        if current:
            match self.validator.can_receive_points(current):
                case DailyLimitEnum.LIMIT_EXCEEDED:
                    return
                case DailyLimitEnum.FIRST_POINT_OF_THE_DAY:
                    self.db.update(
                        TableName.POINTS.value,
                        {
                            "last_received_points_date": datetime.now(),
                            "points": current["points"] + points_delta,
                            "current_day_received_points": 1,
                        },
                        {"guild_id": guild_id, "discord_user_id": user_id},
                    )
                case DailyLimitEnum.LIMIT_NOT_EXCEEDED:
                    previous_amount = current["current_day_received_points"]
                    self.db.update(
                        TableName.POINTS.value,
                        {
                            "current_day_received_points": previous_amount + 1,
                            "points": current["points"] + points_delta,
                        },
                        {"guild_id": guild_id, "discord_user_id": user_id},
                    )

            await self.check_role_threshold(
                user_id, current["points"] + points_delta, guild_id
            )
        else:
            self.create_user_points(guild_id, user_id, points_delta)

    def update_has_thanked_user(
        self, guild_id: int, user_id: int, user: Optional[dict] = None
    ) -> None:
        """Update the last thanked time for a user."""
        date_now = datetime.now()

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

    def can_receive_points(self, user: Optional[dict]) -> DailyLimitEnum:
        """Check if the user has been receiving more than x points in the last 24h."""
        current_day_received_points = user["current_day_received_points"]
        last_received_points_date = user["last_received_points_date"]
        today_timestamp = datetime.now()

        if (today_timestamp - last_received_points_date) <= timedelta(
            hours=24
        ) and current_day_received_points > 0:
            if current_day_received_points >= self.config.daily_limit:
                return DailyLimitEnum.LIMIT_EXCEEDED
            return DailyLimitEnum.LIMIT_NOT_EXCEEDED
        else:
            return DailyLimitEnum.FIRST_POINT_OF_THE_DAY

    def is_valid_thank_message(self, message: discord.Message) -> bool:
        """Check if a message contains a valid thank word."""
        words = re.findall(r"[\w/]+", message.content.lower())
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

    def is_on_cooldown(self, last_thanks: datetime) -> bool:
        """Check if a user is on cooldown or has received too many points recently."""
        if not last_thanks:
            return False
        return last_thanks > datetime.now() - timedelta(
            minutes=self.config.cooldown_minutes
        )


class Points:
    """Main points system class."""

    def __init__(self, bot: discord.Client, config: Optional[PointsConfig] = None):
        self.bot = bot
        self.config = config or PointsConfig()
        self.validator = PointsValidator(self.config)
        self.manager = PointsManager(db, self.validator, bot)

    async def process_message(self, message: discord.Message) -> None:
        """Process a message and handle points if applicable."""
        if not self.validator.is_valid_thank_message(message):
            return

        try:
            await self.bot.logger.info(
                f"Processing message for points: {message.jump_url}```{message.content.replace('`', '&#96;')}```"
            )
        except Exception as e:
            print(f"[ERROR] Error logging message: {e}")

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
            await self.manager.update_user_points(message.guild.id, user_id)
            valid_users_string += f"<@{user_id}>, "

        valid_users_string = valid_users_string[:-2]
        embed = discord.Embed(
            title="",
            description=f"{valid_users_string} received a point! Thanks for helping this community!",
            color=self.config.embed_color,
        )
        await message.channel.send(
            embed=embed, delete_after=self.config.message_timeout
        )
