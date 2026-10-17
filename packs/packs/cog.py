import random
import discord
from discord import app_commands
from discord.ext import commands

from ballsdex.core.utils.permissions import is_admin

class AdminPacksCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="givepack", description="1-100 only.")
    @app_commands.describe(
        user="Im being nice to..",
        amount="Verities for christmas"
    )
    @is_admin()
    async def give_pack(self, interaction: discord.Interaction, user: discord.Member, amount: int = 1):
        # Import models dynamically at runtime when command runs
        from ballsdex.core.models import Ball, BallInstance, Player

        if not (1 <= amount <= 100):
            await interaction.response.send_message(
                "INFINITY PACKS GLITCHED PATCHED?! #dexnews", 
                ephemeral=True
            )
            return

        await interaction.response.defer(ephemeral=False)

        # Get all enabled balls/kerns from database
        enabled_balls = await Ball.filter(enabled=True).all()
        if not enabled_balls:
            await interaction.followup.send("tf you mean you have no balls in your database")
            return

        # Fetch weights based on rarity
        weights = [getattr(ball, "rarity", 1.0) or 1.0 for ball in enabled_balls]

        # Ensure target player exists in database
        player, _ = await Player.get_or_create(discord_id=user.id)

        # Pick 5 objects per pack based on rarity weights
        total_objects_needed = amount * 5
        selected_balls = random.choices(enabled_balls, weights=weights, k=total_objects_needed)

        # Bulk create instances into player's inventory
        instances = [
            BallInstance(ball=ball, player=player)
            for ball in selected_balls
        ]
        await BallInstance.bulk_create(instances)

        total_given = len(instances)
        
        if amount == 1:
            items_str = "\n".join([f"• {ball.name}" for ball in selected_balls])
            await interaction.followup.send(
                f"**{user.mention} received a gun for christmas!**\n"
                f"The balls were:\n{items_str}"
            )
        else:
            await interaction.followup.send(
                f"**{user.mention} received {amount} verities!** ({total_given} battle cats added to their inventory"
            )