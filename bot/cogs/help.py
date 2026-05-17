import discord

from discord import app_commands
from discord.ext import commands


class Help(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    @app_commands.command(name="help", description="Show all available commands")
    async def help(self, interaction: discord.Interaction):
        embed = discord.Embed(
            title="Thanks Bot (prefix: `t!`)",
            description=(
                "This bot tracks **thank you** messages and rewards helpful members "
                "with points and roles.\n​"
            ),
            color=0x5865F2,
        )

        embed.add_field(
            name="General",
            value=(
                "`/stats_thanks` — View your points & thanks count (or another member's)\n"
                "`/leaderboard_thanks` — See the top 10 most helpful members\n"
                "`/help` — Show this message"
            ),
            inline=False,
        )

        embed.add_field(
            name="Admin  🔒",
            value=(
                "`/channel_whitelist` — Re-enable thank tracking in a channel\n"
                "`/channel_blacklist` — Disable thank tracking in a channel\n"
                "`/add_autorole` — Assign a role when a member reaches a point threshold\n"
                "`/remove_autorole` — Remove an autorole\n"
                "`/show_autoroles` — List all configured autoroles"
            ),
            inline=False,
        )

        embed.set_footer(
            text="Want a new feature? Open an issue on [GitHub](https://github.com/enzo405/Thanks/issues) 🙌",
        )

        await interaction.response.send_message(embed=embed, ephemeral=True)


async def setup(bot):
    await bot.add_cog(Help(bot))
