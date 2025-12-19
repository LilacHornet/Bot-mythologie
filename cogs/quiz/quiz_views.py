import discord
from discord import ui


class QuizQCMView(ui.View):
    """Vue avec les boutons pour le mode QCM."""
    
    BUTTON_STYLES = [
        discord.ButtonStyle.primary,
        discord.ButtonStyle.success,
        discord.ButtonStyle.secondary,
        discord.ButtonStyle.danger
    ]
    BUTTON_LABELS = ["A", "B", "C", "D"]
    
    def __init__(self, choices: list[str], channel_id: int, quiz_cog, timeout: float = 30):
        super().__init__(timeout=timeout)
        self.channel_id = channel_id
        self.quiz_cog = quiz_cog
        self.choices = choices
        self._create_buttons()
    
    def _create_buttons(self):
        """Crée les boutons dynamiquement."""
        for i, choice in enumerate(self.choices[:4]):
            button = ui.Button(
                label=f"{self.BUTTON_LABELS[i]}) {choice}",
                style=self.BUTTON_STYLES[i],
                custom_id=f"qcm_{i}"
            )
            button.callback = self._create_callback(i)
            self.add_item(button)
    
    def _create_callback(self, choice_index: int):
        """Crée un callback pour un bouton."""
        async def callback(interaction: discord.Interaction):
            await self._handle_answer(interaction, choice_index)
        return callback
    
    async def _handle_answer(self, interaction: discord.Interaction, choice_index: int):
        """Gère la réponse d'un utilisateur."""
        error = self._validate_answer(interaction.user.id)
        if error:
            await interaction.response.send_message(error, ephemeral=True)
            return
        
        is_correct, _, difficulty, points = self.quiz_cog.quiz_service.check_qcm_answer(
            self.channel_id, choice_index
        )
        
        self._record_answer(interaction.user.id, interaction.user.name, is_correct, difficulty, points)
        embed = self._build_response_embed(is_correct, difficulty, points)
        
        await interaction.response.send_message(embed=embed, ephemeral=True)
    
    def _validate_answer(self, user_id: int) -> str | None:
        """Valide une réponse. Retourne le message d'erreur ou None."""
        if not self.quiz_cog.quiz_service.has_active_quiz(self.channel_id):
            return "❌ Ce quiz est terminé !"
        if self.quiz_cog.quiz_service.has_user_answered(self.channel_id, user_id):
            return "⚠️ Tu as déjà répondu !"
        return None
    
    def _record_answer(self, user_id: int, username: str, is_correct: bool, difficulty: str, points: int):
        """Enregistre une réponse."""
        self.quiz_cog.quiz_service.mark_user_answered(
            self.channel_id, user_id, username, is_correct, points
        )
        self.quiz_cog.stats_service.update_user_stats(
            user_id, username, is_correct, difficulty, points
        )
    
    def _build_response_embed(self, is_correct: bool, difficulty: str, points: int) -> discord.Embed:
        """Construit l'embed de réponse."""
        diff_config = self.quiz_cog.quiz_service.get_difficulty_config(difficulty)
        remaining = self.quiz_cog.quiz_service.get_remaining_time(self.channel_id)
        answered = self.quiz_cog.quiz_service.get_answered_count(self.channel_id)
        
        if is_correct:
            embed = discord.Embed(title="✅ Bonne réponse !", color=discord.Color.green())
            embed.add_field(name="Points", value=f"⭐ +{points}", inline=True)
        else:
            embed = discord.Embed(title="❌ Mauvaise réponse !", color=discord.Color.red())
            embed.add_field(name="Points", value="⭐ +0", inline=True)
        
        embed.add_field(name="Difficulté", value=f"{diff_config['emoji']} {diff_config['name']}", inline=True)
        embed.add_field(name="⏱️ Restant", value=f"**{remaining}** sec", inline=True)
        embed.set_footer(text=f"👥 {answered} personne(s) ont répondu")
        
        return embed
    
    async def on_timeout(self):
        """Désactive les boutons après le timeout."""
        for item in self.children:
            item.disabled = True