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
        self.check_daily_myth.start()
    
    def cog_unload(self):
        """Arrête la tâche lors du déchargement du cog."""
        self.check_daily_myth.cancel()
    
    @tasks.loop(minutes=1)
    async def check_daily_myth(self):
        """Vérifie chaque minute s'il faut envoyer un mythe à un serveur."""
        now = datetime.now()
        current_hour = now.hour
        current_minute = now.minute
        
        configs = self.daily_myth_service.get_all_configs()
        
        for guild_id, guild_config in configs.items():
            if not guild_config.get("enabled"):
                continue
            
            channel_id = guild_config.get("channel_id")
            if not channel_id:
                continue
            
            # Récupérer l'heure configurée pour ce serveur
            configured_hour = guild_config.get("hour", DAILY_MYTH_HOUR)
            configured_minute = guild_config.get("minute", DAILY_MYTH_MINUTE)
            
            # Vérifier si c'est l'heure d'envoyer
            if current_hour == configured_hour and current_minute == configured_minute:
                # Vérifier si on n'a pas déjà envoyé aujourd'hui
                last_sent = guild_config.get("last_sent")
                if last_sent:
                    last_sent_date = datetime.fromisoformat(last_sent).date()
                    if last_sent_date == now.date():
                        continue  # Déjà envoyé aujourd'hui
                
                # Envoyer le mythe
                try:
                    channel = self.bot.get_channel(channel_id)
                    if channel:
                        myth = get_random_myth()
                        embed = get_myth_embed(myth)
                        await channel.send("🌅 **Mythe du jour !**", embed=embed)
                        self.daily_myth_service.update_last_sent(int(guild_id))
                except discord.Forbidden:
                    print(f"Impossible d'envoyer dans le channel {channel_id}")
                except Exception as e:
                    print(f"Erreur lors de l'envoi du mythe: {e}")
    
    @check_daily_myth.before_loop
    async def before_check_daily_myth(self):
        """Attend que le bot soit prêt avant de lancer la tâche."""
        await self.bot.wait_until_ready()
    
    @app_commands.command(name="setmythchannel", description="Définit le channel pour le mythe quotidien")
    @app_commands.describe(channel="Le channel où envoyer le mythe quotidien")
    @app_commands.default_permissions(administrator=True)
    async def set_myth_channel(self, interaction: discord.Interaction, channel: discord.TextChannel):
        """Définit le channel pour le mythe quotidien."""
        self.daily_myth_service.set_channel(interaction.guild_id, channel.id)
        hour, minute = self.daily_myth_service.get_time(interaction.guild_id)
        
        embed = discord.Embed(
            title="✅ Channel configuré !",
            description=f"Le mythe quotidien sera envoyé dans {channel.mention} chaque jour à **{hour:02d}:{minute:02d}**.",
            color=discord.Color.green()
        )
        embed.set_footer(text="Utilisez /setmythtime pour changer l'heure • /disablemyth pour désactiver")
        
        await interaction.response.send_message(embed=embed)
    
    @app_commands.command(name="setmythtime", description="Définit l'heure d'envoi du mythe quotidien")
    @app_commands.describe(
        heure="L'heure d'envoi (0-23)",
        minute="Les minutes (0-59)"
    )
    @app_commands.default_permissions(administrator=True)
    async def set_myth_time(self, interaction: discord.Interaction, heure: int, minute: int = 0):
        """Définit l'heure d'envoi du mythe quotidien."""
        # Validation
        if not (0 <= heure <= 23):
            await interaction.response.send_message(
                "❌ L'heure doit être entre 0 et 23.",
                ephemeral=True
            )
            return
        
        if not (0 <= minute <= 59):
            await interaction.response.send_message(
                "❌ Les minutes doivent être entre 0 et 59.",
                ephemeral=True
            )
            return
        
        # Vérifier si un channel est configuré
        if not self.daily_myth_service.get_channel(interaction.guild_id):
            await interaction.response.send_message(
                "❌ Aucun channel n'est configuré. Utilisez `/setmythchannel` d'abord.",
                ephemeral=True
            )
            return
        
        # Définir l'heure
        success = self.daily_myth_service.set_time(interaction.guild_id, heure, minute)
        
        if success:
            channel_id = self.daily_myth_service.get_channel(interaction.guild_id)
            channel = self.bot.get_channel(channel_id)
            channel_mention = channel.mention if channel else f"ID: {channel_id}"
            
            embed = discord.Embed(
                title="⏰ Heure modifiée !",
                description=f"Le mythe quotidien sera envoyé à **{heure:02d}:{minute:02d}** dans {channel_mention}.",
                color=discord.Color.green()
            )
            embed.set_footer(text="L'heure est en format 24h (heure du serveur)")
            
            await interaction.response.send_message(embed=embed)
        else:
            await interaction.response.send_message(
                "❌ Impossible de modifier l'heure. Vérifiez la configuration.",
                ephemeral=True
            )
    
    @app_commands.command(name="enablemyth", description="Réactive le mythe quotidien")
    @app_commands.default_permissions(administrator=True)
    async def enable_myth(self, interaction: discord.Interaction):
        """Réactive le mythe quotidien."""
        channel_id = self.daily_myth_service.get_channel(interaction.guild_id)
        
        # Vérifier si un channel a déjà été configuré
        if not channel_id:
            await interaction.response.send_message(
                "❌ Aucun channel n'a été configuré pour le mythe quotidien.\n"
                "Utilisez `/setmythchannel` pour définir un channel.",
                ephemeral=True
            )
            return
        
        # Vérifier si déjà activé
        if self.daily_myth_service.is_enabled(interaction.guild_id):
            await interaction.response.send_message(
                "⚠️ Le mythe quotidien est déjà activé !",
                ephemeral=True
            )
            return
        
        # Activer
        self.daily_myth_service.enable(interaction.guild_id)
        channel = self.bot.get_channel(channel_id)
        channel_mention = channel.mention if channel else f"ID: {channel_id}"
        hour, minute = self.daily_myth_service.get_time(interaction.guild_id)
        
        embed = discord.Embed(
            title="✅ Mythe quotidien réactivé !",
            description=f"Le mythe quotidien sera envoyé dans {channel_mention} chaque jour à **{hour:02d}:{minute:02d}**.",
            color=discord.Color.green()
        )
        embed.set_footer(text="Utilisez /disablemyth pour désactiver")
        
        await interaction.response.send_message(embed=embed)
    
    @app_commands.command(name="disablemyth", description="Désactive le mythe quotidien")
    @app_commands.default_permissions(administrator=True)
    async def disable_myth(self, interaction: discord.Interaction):
        """Désactive le mythe quotidien."""
        # Vérifier si configuré
        if not self.daily_myth_service.is_enabled(interaction.guild_id):
            await interaction.response.send_message(
                "⚠️ Le mythe quotidien est déjà désactivé !",
                ephemeral=True
            )
            return
        
        self.daily_myth_service.disable(interaction.guild_id)
        
        embed = discord.Embed(
            title="🔕 Mythe quotidien désactivé",
            description="Le mythe quotidien ne sera plus envoyé sur ce serveur.",
            color=discord.Color.orange()
        )
        embed.set_footer(text="Utilisez /enablemyth pour réactiver")
        
        await interaction.response.send_message(embed=embed)
    
    @app_commands.command(name="mythstatus", description="Affiche le statut du mythe quotidien")
    async def myth_status(self, interaction: discord.Interaction):
        """Affiche le statut du mythe quotidien."""
        channel_id = self.daily_myth_service.get_channel(interaction.guild_id)
        is_enabled = self.daily_myth_service.is_enabled(interaction.guild_id)
        
        if channel_id:
            channel = self.bot.get_channel(channel_id)
            channel_mention = channel.mention if channel else f"ID: {channel_id}"
            hour, minute = self.daily_myth_service.get_time(interaction.guild_id)
            
            if is_enabled:
                embed = discord.Embed(
                    title="📊 Statut du mythe quotidien",
                    description="✅ **Activé**",
                    color=discord.Color.green()
                )
            else:
                embed = discord.Embed(
                    title="📊 Statut du mythe quotidien",
                    description="⏸️ **Désactivé** (configuration conservée)",
                    color=discord.Color.orange()
                )
            
            embed.add_field(
                name="📍 Channel",
                value=channel_mention,
                inline=True
            )
            embed.add_field(
                name="⏰ Heure d'envoi",
                value=f"**{hour:02d}:{minute:02d}**",
                inline=True
            )
            embed.set_footer(text="/setmythtime pour changer l'heure • /setmythchannel pour changer le channel")
        else:
            embed = discord.Embed(
                title="📊 Statut du mythe quotidien",
                description="❌ **Non configuré**",
                color=discord.Color.red()
            )
            embed.set_footer(text="Utilisez /setmythchannel pour configurer")
        
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