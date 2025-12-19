import discord
from discord import app_commands
from discord.ext import commands, tasks
import os
import sys
from datetime import datetime, time

# Ajouter le chemin parent pour les imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.daily_myth_service import DailyMythService
from data.myths import get_random_myth, get_myth_embed
from config import DAILY_MYTH_HOUR, DAILY_MYTH_MINUTE


class DailyMythCog(commands.Cog):
    """Cog pour le mythe quotidien."""
    
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.daily_myth_service = DailyMythService()
        self.send_daily_myth.start()
    
    def cog_unload(self):
        """Arrête la tâche lors du déchargement du cog."""
        self.send_daily_myth.cancel()
    
    @tasks.loop(time=time(hour=DAILY_MYTH_HOUR, minute=DAILY_MYTH_MINUTE))
    async def send_daily_myth(self):
        """Envoie le mythe quotidien à tous les channels configurés."""
        myth = get_random_myth()
        embed = get_myth_embed(myth)
        
        channels = self.daily_myth_service.get_all_channels()
        
        for channel_id in channels:
            try:
                channel = self.bot.get_channel(channel_id)
                if channel:
                    await channel.send("🌅 **Mythe du jour !**", embed=embed)
                    # Trouver le guild_id pour ce channel
                    if hasattr(channel, 'guild'):
                        self.daily_myth_service.update_last_sent(channel.guild.id)
            except discord.Forbidden:
                print(f"Impossible d'envoyer dans le channel {channel_id}")
            except Exception as e:
                print(f"Erreur lors de l'envoi du mythe: {e}")
    
    @send_daily_myth.before_loop
    async def before_daily_myth(self):
        """Attend que le bot soit prêt avant de lancer la tâche."""
        await self.bot.wait_until_ready()
    
    @app_commands.command(name="setmythchannel", description="Définit le channel pour le mythe quotidien")
    @app_commands.describe(channel="Le channel où envoyer le mythe quotidien")
    @app_commands.default_permissions(administrator=True)
    async def set_myth_channel(self, interaction: discord.Interaction, channel: discord.TextChannel):
        """Définit le channel pour le mythe quotidien."""
        self.daily_myth_service.set_channel(interaction.guild_id, channel.id)
        
        embed = discord.Embed(
            title="✅ Channel configuré !",
            description=f"Le mythe quotidien sera envoyé dans {channel.mention} chaque jour à **{DAILY_MYTH_HOUR:02d}:{DAILY_MYTH_MINUTE:02d}**.",
            color=discord.Color.green()
        )
        embed.set_footer(text="Utilisez /disablemyth pour désactiver")
        
        await interaction.response.send_message(embed=embed)
    
    @app_commands.command(name="disablemyth", description="Désactive le mythe quotidien")
    @app_commands.default_permissions(administrator=True)
    async def disable_myth(self, interaction: discord.Interaction):
        """Désactive le mythe quotidien."""
        self.daily_myth_service.remove_channel(interaction.guild_id)
        
        embed = discord.Embed(
            title="🔕 Mythe quotidien désactivé",
            description="Le mythe quotidien ne sera plus envoyé sur ce serveur.",
            color=discord.Color.orange()
        )
        embed.set_footer(text="Utilisez /setmythchannel pour réactiver")
        
        await interaction.response.send_message(embed=embed)
    
    @app_commands.command(name="mythstatus", description="Affiche le statut du mythe quotidien")
    async def myth_status(self, interaction: discord.Interaction):
        """Affiche le statut du mythe quotidien."""
        channel_id = self.daily_myth_service.get_channel(interaction.guild_id)
        is_enabled = self.daily_myth_service.is_enabled(interaction.guild_id)
        
        if is_enabled and channel_id:
            channel = self.bot.get_channel(channel_id)
            channel_mention = channel.mention if channel else f"ID: {channel_id}"
            
            embed = discord.Embed(
                title="📊 Statut du mythe quotidien",
                description="✅ **Activé**",
                color=discord.Color.green()
            )
            embed.add_field(
                name="📍 Channel",
                value=channel_mention,
                inline=True
            )
            embed.add_field(
                name="⏰ Heure d'envoi",
                value=f"{DAILY_MYTH_HOUR:02d}:{DAILY_MYTH_MINUTE:02d}",
                inline=True
            )
        else:
            embed = discord.Embed(
                title="📊 Statut du mythe quotidien",
                description="❌ **Désactivé**",
                color=discord.Color.red()
            )
            embed.set_footer(text="Utilisez /setmythchannel pour activer")
        
        await interaction.response.send_message(embed=embed, ephemeral=True)
    
    @app_commands.command(name="myth", description="Affiche un mythe aléatoire maintenant")
    async def random_myth(self, interaction: discord.Interaction):
        """Affiche un mythe aléatoire."""
        await interaction.response.defer()
        
        myth = get_random_myth()
        embed = get_myth_embed(myth)
        
        await interaction.followup.send(embed=embed)


async def setup(bot: commands.Bot):
    await bot.add_cog(DailyMythCog(bot))