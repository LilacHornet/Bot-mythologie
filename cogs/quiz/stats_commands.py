import discord
from discord import app_commands

from data.questions import DIFFICULTY_CONFIG


class StatsCommands:
    """Commandes pour les statistiques."""
    
    @app_commands.command(name="stats", description="Affiche tes statistiques de quiz")
    async def stats(self, interaction: discord.Interaction):
        """Affiche les statistiques de l'utilisateur."""
        await interaction.response.defer()
        
        user_stats = self.stats_service.get_user_stats(interaction.user.id)
        
        if not user_stats:
            await interaction.followup.send(
                "📊 Tu n'as pas encore répondu à un quiz ! Utilise `/quiz` pour commencer.",
                ephemeral=True
            )
            return
        
        correct = user_stats["correct"]
        wrong = user_stats["wrong"]
        total = user_stats["total"]
        points = user_stats.get("points", 0)
        percentage = (correct / total * 100) if total > 0 else 0
        
        embed = discord.Embed(
            title=f"📊 Statistiques de {interaction.user.name}",
            color=discord.Color.blue()
        )
        embed.add_field(name="⭐ Points", value=str(points), inline=True)
        embed.add_field(name="✅ Bonnes réponses", value=str(correct), inline=True)
        embed.add_field(name="❌ Mauvaises réponses", value=str(wrong), inline=True)
        embed.add_field(name="📝 Total", value=str(total), inline=True)
        embed.add_field(name="📈 Taux de réussite", value=f"{percentage:.1f}%", inline=True)
        
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
        
        await interaction.followup.send(embed=embed)
    
    @app_commands.command(name="leaderboard", description="Affiche le classement des meilleurs joueurs")
    async def leaderboard(self, interaction: discord.Interaction):
        """Affiche le classement des joueurs."""
        await interaction.response.defer()
        
        sorted_users = self.stats_service.get_leaderboard(10, sort_by="points")
        
        if not sorted_users:
            await interaction.followup.send(
                "📊 Aucune statistique disponible pour le moment.",
                ephemeral=True
            )
            return
        
        embed = discord.Embed(
            title="🏆 Classement Mythologie",
            color=discord.Color.gold()
        )
        
        medals = ["🥇", "🥈", "🥉"]
        description = ""
        
        for i, (user_id, user_stats) in enumerate(sorted_users):
            medal = medals[i] if i < 3 else f"**{i+1}.**"
            points = user_stats.get("points", 0)
            correct = user_stats["correct"]
            description += f"{medal} {user_stats['username']} - ⭐ {points} pts ({correct} ✅)\n"
        
        embed.description = description
        await interaction.followup.send(embed=embed)