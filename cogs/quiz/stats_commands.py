import discord
from discord import app_commands
from typing import Optional

from data.questions import DIFFICULTY_CONFIG

# Titres basés sur les points
TITLES = [
    (0, "🌱", "Néophyte"),
    (10, "📚", "Apprenti"),
    (25, "🎓", "Érudit"),
    (50, "🏛️", "Sage"),
    (100, "⚡", "Champion"),
    (200, "👑", "Maître"),
    (500, "🔱", "Légende"),
    (1000, "🌟", "Dieu de l'Olympe")
]


class StatsCommands:
    """Commandes pour les statistiques."""
    
    @app_commands.command(name="stats", description="Affiche tes statistiques")
    @app_commands.describe(utilisateur="L'utilisateur (optionnel)")
    async def stats(self, interaction: discord.Interaction, utilisateur: Optional[discord.Member] = None):
        """Affiche les statistiques de l'utilisateur."""
        await interaction.response.defer()
        
        target = utilisateur or interaction.user
        user_stats = self.stats_service.get_user_stats(target.id)
        
        if not user_stats:
            msg = "📊 Tu n'as pas encore joué !" if target == interaction.user else f"📊 **{target.name}** n'a pas encore joué !"
            await interaction.followup.send(msg, ephemeral=True)
            return
        
        embed = self._build_stats_embed(target, user_stats)
        await interaction.followup.send(embed=embed)
    
    def _build_stats_embed(self, user: discord.Member, stats: dict) -> discord.Embed:
        """Construit l'embed des statistiques."""
        points = stats.get("points", 0)
        title_emoji, title_name = self._get_title(points)
        rank = self.stats_service.get_user_rank(user.id)
        percentage = (stats["correct"] / stats["total"] * 100) if stats["total"] > 0 else 0
        
        embed = discord.Embed(
            title=f"📊 Statistiques de {user.name}",
            description=f"{title_emoji} **{title_name}**",
            color=discord.Color.blue()
        )
        embed.set_thumbnail(url=user.display_avatar.url)
        
        embed.add_field(name="🏆 Rang", value=f"#{rank}" if rank else "N/A", inline=True)
        embed.add_field(name="⭐ Points", value=str(points), inline=True)
        embed.add_field(name="📈 Réussite", value=f"{percentage:.1f}%", inline=True)
        
        embed.add_field(name="✅ Bonnes", value=str(stats["correct"]), inline=True)
        embed.add_field(name="❌ Mauvaises", value=str(stats["wrong"]), inline=True)
        embed.add_field(name="📝 Total", value=str(stats["total"]), inline=True)
        
        diff_stats = self._format_difficulty_stats(stats.get("by_difficulty", {}))
        if diff_stats:
            embed.add_field(name="📋 Par difficulté", value=diff_stats, inline=False)
        
        next_title = self._get_next_title(points)
        if next_title:
            embed.set_footer(text=f"Prochain: {next_title[1]} à {next_title[2]} pts")
        
        return embed
    
    def _format_difficulty_stats(self, by_diff: dict) -> str:
        """Formate les statistiques par difficulté."""
        lines = []
        for diff, config in DIFFICULTY_CONFIG.items():
            data = by_diff.get(diff, {"correct": 0, "wrong": 0})
            total = data.get("correct", 0) + data.get("wrong", 0)
            if total > 0:
                pct = (data["correct"] / total * 100)
                lines.append(f"{config['emoji']} {config['name']}: {data['correct']}/{total} ({pct:.0f}%)")
        return "\n".join(lines)
    
    def _get_title(self, points: int) -> tuple[str, str]:
        """Retourne le titre en fonction des points."""
        current = TITLES[0]
        for threshold, emoji, name in TITLES:
            if points >= threshold:
                current = (threshold, emoji, name)
        return current[1], current[2]
    
    def _get_next_title(self, points: int) -> tuple | None:
        """Retourne le prochain titre."""
        for threshold, emoji, name in TITLES:
            if points < threshold:
                return (threshold, f"{emoji} {name}", threshold)
        return None
    
    @app_commands.command(name="leaderboard", description="Affiche le classement")
    @app_commands.describe(page="Numéro de page")
    async def leaderboard(self, interaction: discord.Interaction, page: Optional[int] = 1):
        """Affiche le classement des joueurs."""
        await interaction.response.defer()
        
        page = max(1, page)
        per_page = 10
        
        all_users = self.stats_service.get_leaderboard(100)
        total_pages = max(1, (len(all_users) + per_page - 1) // per_page)
        page = min(page, total_pages)
        
        if not all_users:
            await interaction.followup.send("📊 Aucun joueur pour le moment !", ephemeral=True)
            return
        
        embed = self._build_leaderboard_embed(all_users, page, per_page, total_pages, interaction.user.id)
        await interaction.followup.send(embed=embed)
    
    def _build_leaderboard_embed(self, users: list, page: int, per_page: int, total_pages: int, current_user_id: int) -> discord.Embed:
        """Construit l'embed du classement."""
        offset = (page - 1) * per_page
        page_users = users[offset:offset + per_page]
        
        embed = discord.Embed(
            title="🏆 Classement Mythologie",
            color=discord.Color.gold()
        )
        
        lines = []
        medals = ["🥇", "🥈", "🥉"]
        
        for i, (user_id, stats) in enumerate(page_users):
            rank = offset + i + 1
            rank_display = medals[rank - 1] if rank <= 3 else f"`{rank}.`"
            
            name = stats['username']
            if str(user_id) == str(current_user_id):
                name = f"**{name}** ← toi"
            
            pct = (stats["correct"] / stats["total"] * 100) if stats["total"] > 0 else 0
            lines.append(f"{rank_display} {name}\n   ⭐ {stats.get('points', 0)} pts • ✅ {stats['correct']}/{stats['total']} ({pct:.0f}%)")
        
        embed.description = f"Page {page}/{total_pages} • {len(users)} joueur(s)\n\n" + "\n".join(lines)
        
        user_rank = self.stats_service.get_user_rank(current_user_id)
        if user_rank and (user_rank <= offset or user_rank > offset + per_page):
            user_stats = self.stats_service.get_user_stats(current_user_id)
            if user_stats:
                embed.add_field(name="📍 Ta position", value=f"#{user_rank} • ⭐ {user_stats.get('points', 0)} pts", inline=False)
        
        embed.set_footer(text=f"/leaderboard page:{page + 1}")
        return embed
    
    @app_commands.command(name="resetstats", description="Réinitialise tes statistiques")
    async def reset_stats(self, interaction: discord.Interaction):
        """Réinitialise les statistiques de l'utilisateur."""
        user_stats = self.stats_service.get_user_stats(interaction.user.id)
        
        if not user_stats:
            await interaction.response.send_message("📊 Pas de stats à réinitialiser !", ephemeral=True)
            return
        
        embed = discord.Embed(
            title="⚠️ Confirmation",
            description=f"Tu perdras:\n• ⭐ **{user_stats.get('points', 0)}** points\n• ✅ **{user_stats['correct']}** bonnes réponses\n\n**Irréversible !**",
            color=discord.Color.red()
        )
        
        view = ResetConfirmView(self.stats_service, interaction.user.id)
        await interaction.response.send_message(embed=embed, view=view, ephemeral=True)


class ResetConfirmView(discord.ui.View):
    """Vue de confirmation pour reset."""
    
    def __init__(self, stats_service, user_id: int):
        super().__init__(timeout=30)
        self.stats_service = stats_service
        self.user_id = user_id
    
    @discord.ui.button(label="Confirmer", style=discord.ButtonStyle.danger, emoji="🗑️")
    async def confirm(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.user_id:
            await interaction.response.send_message("❌ Ce n'est pas ton bouton !", ephemeral=True)
            return
        
        self.stats_service.reset_user_stats(self.user_id)
        embed = discord.Embed(title="🗑️ Stats réinitialisées", color=discord.Color.green())
        await interaction.response.edit_message(embed=embed, view=None)
    
    @discord.ui.button(label="Annuler", style=discord.ButtonStyle.secondary, emoji="❌")
    async def cancel(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.user_id:
            await interaction.response.send_message("❌ Ce n'est pas ton bouton !", ephemeral=True)
            return
        
        embed = discord.Embed(title="❌ Annulé", color=discord.Color.grey())
        await interaction.response.edit_message(embed=embed, view=None)
    
    async def on_timeout(self):
        self.clear_items()