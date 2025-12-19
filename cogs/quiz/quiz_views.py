import discord
from discord import ui


class QuizQCMView(ui.View):
    """Vue avec les boutons pour le mode QCM."""
    
    def __init__(self, choices: list[str], channel_id: int, quiz_cog, timeout: float = 30):
        super().__init__(timeout=timeout)
        self.channel_id = channel_id
        self.quiz_cog = quiz_cog
        self.choices = choices
        
        # Créer les boutons dynamiquement
        button_styles = [
            discord.ButtonStyle.primary,
            discord.ButtonStyle.success,
            discord.ButtonStyle.secondary,
            discord.ButtonStyle.danger
        ]
        button_labels = ["A", "B", "C", "D"]
        
        for i, choice in enumerate(choices[:4]):
            button = ui.Button(
                label=f"{button_labels[i]}) {choice}",
                style=button_styles[i],
                custom_id=f"qcm_{i}"
            )
            button.callback = self.create_callback(i)
            self.add_item(button)
    
    def create_callback(self, choice_index: int):
        """Crée un callback pour un bouton spécifique."""
        async def callback(interaction: discord.Interaction):
            await self.handle_answer(interaction, choice_index)
        return callback
    
    async def handle_answer(self, interaction: discord.Interaction, choice_index: int):
        """Gère la réponse d'un utilisateur."""
        user_id = interaction.user.id
        channel_id = self.channel_id
        
        # Vérifier si le quiz est toujours actif
        if not self.quiz_cog.quiz_service.has_active_quiz(channel_id):
            await interaction.response.send_message(
                "❌ Ce quiz est terminé !",
                ephemeral=True
            )
            return
        
        # Vérifier si l'utilisateur a déjà répondu
        if self.quiz_cog.quiz_service.has_user_answered(channel_id, user_id):
            await interaction.response.send_message(
                "⚠️ Tu as déjà répondu à ce quiz !",
                ephemeral=True
            )
            return
        
        # Vérifier la réponse
        is_correct, correct_answer, difficulty, points = self.quiz_cog.quiz_service.check_qcm_answer(
            channel_id, choice_index
        )
        diff_config = self.quiz_cog.quiz_service.get_difficulty_config(difficulty)
        remaining_time = self.quiz_cog.quiz_service.get_remaining_time(channel_id)
        
        # Marquer l'utilisateur comme ayant répondu
        self.quiz_cog.quiz_service.mark_user_answered(
            channel_id, user_id, interaction.user.name, is_correct, points
        )
        
        # Sauvegarder les stats
        self.quiz_cog.stats_service.update_user_stats(
            user_id,
            interaction.user.name,
            is_correct,
            difficulty,
            points
        )
        
        # Nombre de participants
        answered_count = self.quiz_cog.quiz_service.get_answered_count(channel_id)
        
        # Créer l'embed de réponse
        if is_correct:
            embed = discord.Embed(
                title="✅ Bonne réponse !",
                description=f"Bravo ! Tu as choisi la bonne réponse !",
                color=discord.Color.green()
            )
            embed.add_field(
                name="Points gagnés",
                value=f"⭐ +{points} points",
                inline=True
            )
        else:
            embed = discord.Embed(
                title="❌ Mauvaise réponse !",
                description=f"Ce n'est pas la bonne réponse... La réponse sera révélée à la fin !",
                color=discord.Color.red()
            )
            embed.add_field(
                name="Points gagnés",
                value="⭐ +0 points",
                inline=True
            )
        
        embed.add_field(
            name="Difficulté",
            value=f"{diff_config['emoji']} {diff_config['name']}",
            inline=True
        )
        embed.add_field(
            name="⏱️ Temps restant",
            value=f"**{remaining_time}** secondes",
            inline=True
        )
        embed.set_footer(text=f"👥 {answered_count} personne(s) ont répondu")
        
        await interaction.response.send_message(embed=embed, ephemeral=True)
    
    async def on_timeout(self):
        """Désactive les boutons quand le temps est écoulé."""
        for item in self.children:
            item.disabled = True