import discord
from discord import app_commands
from typing import Optional

from data.questions import DIFFICULTY_CONFIG


class StatsCommands:
    """Commandes pour les statistiques."""
    
    @app_commands.command(name="stats", description="Affiche tes statistiques de quiz ou celles d'un autre joueur")
    @app_commands.describe(utilisateur="L'utilisateur dont tu veux voir les stats (optionnel)")
    async def stats(self, interaction: discord.Interaction, utilisateur: Optional[discord.Member] = None):
        """Affiche les statistiques de l'utilisateur."""
        await interaction.response.defer()
        
        # Si aucun utilisateur spécifié, afficher les stats de l'auteur
        target_user = utilisateur or interaction.user
        user_stats = self.stats_service.get_user_stats(target_user.id)
        
        if not user_stats:
            if target_user == interaction.user:
                await interaction.followup.send(
                    "📊 Tu n'as pas encore répondu à un quiz ! Utilise `/quiz` pour commencer.",
                    ephemeral=True
                )
            else:
                await interaction.followup.send(
                    f"📊 **{target_user.name}** n'a pas encore répondu à un quiz !",
                    ephemeral=True
                )
            return
        
        correct = user_stats["correct"]
        wrong = user_stats["wrong"]
        total = user_stats["total"]
        points = user_stats.get("points", 0)
        percentage = (correct / total * 100) if total > 0 else 0
        
        # Déterminer le rang
        rank = self.stats_service.get_user_rank(target_user.id)
        rank_text = f"#{rank}" if rank else "Non classé"
        
        # Déterminer le titre en fonction des points
        title_emoji, title_name = self._get_title(points)
        
        embed = discord.Embed(
            title=f"📊 Statistiques de {target_user.name}",
            description=f"{title_emoji} **{title_name}**",
            color=discord.Color.blue()
        )
        embed.set_thumbnail(url=target_user.display_avatar.url)
        
        embed.add_field(name="🏆 Classement", value=rank_text, inline=True)
        embed.add_field(name="⭐ Points", value=str(points), inline=True)
        embed.add_field(name="📈 Taux de réussite", value=f"{percentage:.1f}%", inline=True)
        
        embed.add_field(name="✅ Bonnes réponses", value=str(correct), inline=True)
        embed.add_field(name="❌ Mauvaises réponses", value=str(wrong), inline=True)
        embed.add_field(name="📝 Total", value=str(total), inline=True)
        
        # Stats par difficulté
        by_diff = user_stats.get("by_difficulty", {})
        diff_stats = ""
        for diff, config in DIFFICULTY_CONFIG.items():
            diff_data = by_diff.get(diff, {"correct": 0, "wrong": 0})
            diff_total = diff_data["correct"] + diff_data["wrong"]
            if diff_total > 0:
                diff_pct = (diff_data["correct"] / diff_total * 100)
                diff_stats += f"{config['emoji']} {config['name']}: {diff_data['correct']}/{diff_total} ({diff_pct:.0f}%)\n"
        
        if diff_stats:
            embed.add_field(name="📋 Par difficulté", value=diff_stats, inline=False)
        
        # Prochain titre
        next_title = self._get_next_title(points)
        if next_title:
            embed.set_footer(text=f"Prochain titre: {next_title[1]} à {next_title[2]} points")
        
        await interaction.followup.send(embed=embed)
    
    def _get_title(self, points: int) -> tuple[str, str]:
        """Retourne le titre en fonction des points."""
        titles = [
            (0, "🌱", "Néophyte"),
            (10, "📚", "Apprenti"),
            (25, "🎓", "Érudit"),
            (50, "🏛️", "Sage"),
            (100, "⚡", "Champion"),
            (200, "👑", "Maître"),
            (500, "🔱", "Légende"),
            (1000, "🌟", "Dieu de l'Olympe")
        ]
        
        current_title = titles[0]
        for threshold, emoji, name in titles:
            if points >= threshold:
                current_title = (threshold, emoji, name)
            else:
                break
        
        return current_title[1], current_title[2]
    
    def _get_next_title(self, points: int) -> tuple[int, str, int] | None:
        """Retourne le prochain titre à atteindre."""
        titles = [
            (10, "📚 Apprenti", 10),
            (25, "🎓 Érudit", 25),
            (50, "🏛️ Sage", 50),
            (100, "⚡ Champion", 100),
            (200, "👑 Maître", 200),
            (500, "🔱 Légende", 500),
            (1000, "🌟 Dieu de l'Olympe", 1000)
        ]
        
        for threshold, name, required in titles:
            if points < threshold:
                return (threshold, name, required)
        
        return None
    
    @app_commands.command(name="leaderboard", description="Affiche le classement des meilleurs joueurs")
    @app_commands.describe(page="Numéro de la page (10 joueurs par page)")
    async def leaderboard(self, interaction: discord.Interaction, page: Optional[int] = 1):
        """Affiche le classement des joueurs."""
        await interaction.response.defer()
        
        # Validation de la page
        if page < 1:
            page = 1
        
        per_page = 10
        offset = (page - 1) * per_page
        
        all_users = self.stats_service.get_leaderboard(100, sort_by="points")
        total_users = len(all_users)
        total_pages = max(1, (total_users + per_page - 1) // per_page)
        
        if page > total_pages:
            page = total_pages
            offset = (page - 1) * per_page
        
        sorted_users = all_users[offset:offset + per_page]
        
        if not sorted_users:
            await interaction.followup.send(
                "📊 Aucune statistique disponible pour le moment.\nUtilisez `/quiz` pour commencer !",
                ephemeral=True
            )
            return
        
        embed = discord.Embed(
            title="🏆 Classement Mythologie",
            description=f"Page {page}/{total_pages} • {total_users} joueur(s) au total",
            color=discord.Color.gold()
        )
        
        medals = ["🥇", "🥈", "🥉"]
        description_lines = []
        
        for i, (user_id, user_stats) in enumerate(sorted_users):
            rank = offset + i + 1
            
            if rank <= 3:
                rank_display = medals[rank - 1]
            else:
                rank_display = f"`{rank}.`"
            
            points = user_stats.get("points", 0)
            correct = user_stats["correct"]
            total = user_stats["total"]
            percentage = (correct / total * 100) if total > 0 else 0
            
            # Marquer l'utilisateur actuel
            username = user_stats['username']
            if str(user_id) == str(interaction.user.id):
                username = f"**{username}** ← toi"
            
            description_lines.append(
                f"{rank_display} {username}\n"
                f"   ⭐ {points} pts • ✅ {correct}/{total} ({percentage:.0f}%)"
            )
        
        embed.description = f"Page {page}/{total_pages} • {total_users} joueur(s)\n\n" + "\n".join(description_lines)
        
        # Ajouter le rang de l'utilisateur actuel s'il n'est pas dans la page
        user_rank = self.stats_service.get_user_rank(interaction.user.id)
        if user_rank and (user_rank <= offset or user_rank > offset + per_page):
            user_stats = self.stats_service.get_user_stats(interaction.user.id)
            if user_stats:
                embed.add_field(
                    name="📍 Ta position",
                    value=f"#{user_rank} avec ⭐ {user_stats.get('points', 0)} points",
                    inline=False
                )
        
        embed.set_footer(text=f"Utilisez /leaderboard page:{page+1} pour la page suivante")
        
        await interaction.followup.send(embed=embed)
    
    @app_commands.command(name="resetstats", description="Réinitialise tes statistiques (irréversible !)")
    async def reset_stats(self, interaction: discord.Interaction):
        """Réinitialise les statistiques de l'utilisateur."""
        user_stats = self.stats_service.get_user_stats(interaction.user.id)
        
        if not user_stats:
            await interaction.response.send_message(
                "📊 Tu n'as pas de statistiques à réinitialiser !",
                ephemeral=True
            )
            return
        
        # Confirmation avec un bouton
        embed = discord.Embed(
            title="⚠️ Confirmation",
            description=f"Es-tu sûr de vouloir réinitialiser tes statistiques ?\n\n"
                        f"Tu perdras :\n"
                        f"• ⭐ **{user_stats.get('points', 0)}** points\n"
                        f"• ✅ **{user_stats['correct']}** bonnes réponses\n"
                        f"• 📝 **{user_stats['total']}** quiz joués\n\n"
                        f"**Cette action est irréversible !**",
            color=discord.Color.red()
        )
        
        view = ResetConfirmView(self.stats_service, interaction.user.id)
        await interaction.response.send_message(embed=embed, view=view, ephemeral=True)


class ResetConfirmView(discord.ui.View):
    """Vue pour confirmer la réinitialisation des stats."""
    
    def __init__(self, stats_service, user_id: int):
        super().__init__(timeout=30)
        self.stats_service = stats_service
        self.user_id = user_id
    
    @discord.ui.button(label="Confirmer", style=discord.ButtonStyle.danger, emoji="🗑️")
    async def confirm(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.user_id:
            await interaction.response.send_message("Ce n'est pas ton bouton !", ephemeral=True)
            return
        
        self.stats_service.reset_user_stats(self.user_id)
        
        embed = discord.Embed(
            title="🗑️ Statistiques réinitialisées",
            description="Tes statistiques ont été remises à zéro. Bonne chance pour ton nouveau départ !",
            color=discord.Color.green()
        )
        
        await interaction.response.edit_message(embed=embed, view=None)
    
    @discord.ui.button(label="Annuler", style=discord.ButtonStyle.secondary, emoji="❌")
    async def cancel(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.user_id:
            await interaction.response.send_message("Ce n'est pas ton bouton !", ephemeral=True)
            return
        
        embed = discord.Embed(
            title="❌ Annulé",
            description="Tes statistiques n'ont pas été modifiées.",
            color=discord.Color.grey()
        )
        
        await interaction.response.edit_message(embed=embed, view=None)
    
    async def on_timeout(self):
        self.clear_items()