import discord
from discord import app_commands
from discord.ext import commands, tasks
import os
import sys
from datetime import datetime

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
        print("✅ DailyMythCog initialisé - Tâche de vérification démarrée")
    
    def cog_unload(self):
        """Arrête la tâche lors du déchargement du cog."""
        self.check_daily_myth.cancel()
        print("🛑 DailyMythCog déchargé - Tâche arrêtée")
    
    # ==================== FONCTIONS UTILITAIRES ====================
    
    def _is_time_to_send(self, current_hour: int, current_minute: int, configured_hour: int, configured_minute: int) -> bool:
        """Vérifie si c'est l'heure d'envoyer le mythe."""
        return current_hour == configured_hour and current_minute == configured_minute
    
    def _was_sent_today(self, last_sent: str | None, now: datetime) -> bool:
        """Vérifie si le mythe a déjà été envoyé aujourd'hui."""
        if not last_sent:
            return False
        try:
            last_sent_date = datetime.fromisoformat(last_sent).date()
            return last_sent_date == now.date()
        except ValueError:
            return False
    
    async def _get_channel(self, channel_id: int) -> discord.TextChannel | None:
        """Récupère un channel par son ID."""
        channel = self.bot.get_channel(channel_id)
        if channel:
            return channel
        
        try:
            return await self.bot.fetch_channel(channel_id)
        except discord.NotFound:
            print(f"❌ Channel {channel_id} non trouvé")
        except discord.Forbidden:
            print(f"❌ Pas d'accès au channel {channel_id}")
        except Exception as e:
            print(f"❌ Erreur lors de la récupération du channel {channel_id}: {e}")
        
        return None
    
    async def _send_myth_to_channel(self, channel: discord.TextChannel, guild_id: int, prefix: str = "🌅 **Mythe du jour !**") -> bool:
        """Envoie un mythe dans un channel. Retourne True si succès."""
        try:
            myth = get_random_myth()
            embed = get_myth_embed(myth)
            await channel.send(prefix, embed=embed)
            self.daily_myth_service.update_last_sent(guild_id)
            print(f"✅ Mythe envoyé dans le channel {channel.id} (serveur {guild_id})")
            return True
        except discord.Forbidden:
            print(f"❌ Impossible d'envoyer dans le channel {channel.id} (permissions)")
        except Exception as e:
            print(f"❌ Erreur lors de l'envoi du mythe: {e}")
        return False
    
    async def _process_guild(self, guild_id: str, guild_config: dict, now: datetime) -> None:
        """Traite un serveur pour l'envoi du mythe quotidien."""
        if not guild_config.get("enabled"):
            return
        
        channel_id = guild_config.get("channel_id")
        if not channel_id:
            return
        
        configured_hour = guild_config.get("hour", DAILY_MYTH_HOUR)
        configured_minute = guild_config.get("minute", DAILY_MYTH_MINUTE)
        
        # Debug log
        print(f"[{now.strftime('%H:%M')}] Vérification serveur {guild_id}: configuré pour {configured_hour:02d}:{configured_minute:02d}")
        
        # Vérifier si c'est l'heure d'envoyer
        if not self._is_time_to_send(now.hour, now.minute, configured_hour, configured_minute):
            return
        
        # Vérifier si déjà envoyé aujourd'hui
        if self._was_sent_today(guild_config.get("last_sent"), now):
            print(f"[{now.strftime('%H:%M')}] Mythe déjà envoyé aujourd'hui pour {guild_id}")
            return
        
        # Récupérer le channel et envoyer
        channel = await self._get_channel(channel_id)
        if channel:
            await self._send_myth_to_channel(channel, int(guild_id))
    
    # ==================== TÂCHE PLANIFIÉE ====================
    
    @tasks.loop(minutes=1)
    async def check_daily_myth(self):
        """Vérifie chaque minute s'il faut envoyer un mythe à un serveur."""
        now = datetime.now()
        
        # Recharger la config
        self.daily_myth_service.reload_config()
        configs = self.daily_myth_service.get_all_configs()
        
        if not configs:
            return
        
        for guild_id, guild_config in configs.items():
            await self._process_guild(guild_id, guild_config, now)
    
    @check_daily_myth.before_loop
    async def before_check_daily_myth(self):
        """Attend que le bot soit prêt avant de lancer la tâche."""
        await self.bot.wait_until_ready()
        print("✅ Bot prêt - Vérification du mythe quotidien active")
    
    # ==================== COMMANDES ====================
    
    @app_commands.command(name="testmyth", description="Teste l'envoi du mythe quotidien (Admin)")
    @app_commands.default_permissions(administrator=True)
    async def test_myth(self, interaction: discord.Interaction):
        """Teste l'envoi du mythe quotidien."""
        channel_id = self.daily_myth_service.get_channel(interaction.guild_id)
        
        if not channel_id:
            await interaction.response.send_message(
                "❌ Aucun channel configuré. Utilisez `/setmythchannel` d'abord.",
                ephemeral=True
            )
            return
        
        channel = await self._get_channel(channel_id)
        if not channel:
            await interaction.response.send_message(
                f"❌ Impossible de trouver le channel configuré (ID: {channel_id})",
                ephemeral=True
            )
            return
        
        success = await self._send_myth_to_channel(channel, interaction.guild_id, "🧪 **Test du mythe quotidien !**")
        
        if success:
            await interaction.response.send_message(
                f"✅ Mythe de test envoyé dans {channel.mention} !",
                ephemeral=True
            )
        else:
            await interaction.response.send_message(
                f"❌ Impossible d'envoyer le mythe dans {channel.mention}",
                ephemeral=True
            )
    
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
        embed.set_footer(text="Utilisez /setmythtime pour changer l'heure • /testmyth pour tester")
        
        await interaction.response.send_message(embed=embed)
    
    @app_commands.command(name="setmythtime", description="Définit l'heure d'envoi du mythe quotidien")
    @app_commands.describe(
        heure="L'heure d'envoi (0-23)",
        minute="Les minutes (0-59)"
    )
    @app_commands.default_permissions(administrator=True)
    async def set_myth_time(self, interaction: discord.Interaction, heure: int, minute: int = 0):
        """Définit l'heure d'envoi du mythe quotidien."""
        if not (0 <= heure <= 23):
            await interaction.response.send_message("❌ L'heure doit être entre 0 et 23.", ephemeral=True)
            return
        
        if not (0 <= minute <= 59):
            await interaction.response.send_message("❌ Les minutes doivent être entre 0 et 59.", ephemeral=True)
            return
        
        if not self.daily_myth_service.get_channel(interaction.guild_id):
            await interaction.response.send_message(
                "❌ Aucun channel n'est configuré. Utilisez `/setmythchannel` d'abord.",
                ephemeral=True
            )
            return
        
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
        
        if not channel_id:
            await interaction.response.send_message(
                "❌ Aucun channel n'a été configuré.\nUtilisez `/setmythchannel` pour définir un channel.",
                ephemeral=True
            )
            return
        
        if self.daily_myth_service.is_enabled(interaction.guild_id):
            await interaction.response.send_message("⚠️ Le mythe quotidien est déjà activé !", ephemeral=True)
            return
        
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
        if not self.daily_myth_service.is_enabled(interaction.guild_id):
            await interaction.response.send_message("⚠️ Le mythe quotidien est déjà désactivé !", ephemeral=True)
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
        embed = self._build_status_embed(interaction.guild_id)
        await interaction.response.send_message(embed=embed, ephemeral=True)
    
    def _build_status_embed(self, guild_id: int) -> discord.Embed:
        """Construit l'embed de statut."""
        channel_id = self.daily_myth_service.get_channel(guild_id)
        is_enabled = self.daily_myth_service.is_enabled(guild_id)
        now = datetime.now()
        
        if not channel_id:
            embed = discord.Embed(
                title="📊 Statut du mythe quotidien",
                description="❌ **Non configuré**",
                color=discord.Color.red()
            )
            embed.set_footer(text="Utilisez /setmythchannel pour configurer")
            return embed
        
        channel = self.bot.get_channel(channel_id)
        channel_mention = channel.mention if channel else f"ID: {channel_id}"
        hour, minute = self.daily_myth_service.get_time(guild_id)
        
        status = "✅ **Activé**" if is_enabled else "⏸️ **Désactivé** (configuration conservée)"
        color = discord.Color.green() if is_enabled else discord.Color.orange()
        
        embed = discord.Embed(title="📊 Statut du mythe quotidien", description=status, color=color)
        embed.add_field(name="📍 Channel", value=channel_mention, inline=True)
        embed.add_field(name="⏰ Heure d'envoi", value=f"**{hour:02d}:{minute:02d}**", inline=True)
        embed.add_field(name="🕐 Heure actuelle", value=f"**{now.strftime('%H:%M')}**", inline=True)
        embed.set_footer(text="/setmythtime pour changer l'heure • /testmyth pour tester")
        
        return embed
    
    @app_commands.command(name="myth", description="Affiche un mythe aléatoire maintenant")
    async def random_myth(self, interaction: discord.Interaction):
        """Affiche un mythe aléatoire."""
        await interaction.response.defer()
        myth = get_random_myth()
        embed = get_myth_embed(myth)
        await interaction.followup.send(embed=embed)


async def setup(bot: commands.Bot):
    await bot.add_cog(DailyMythCog(bot))