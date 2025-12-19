import discord
from discord.ext import commands


class QuizListeners:
    """Listeners pour le quiz."""
    
    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        """Écoute les messages pour détecter les réponses (mode texte)."""
        if message.author.bot:
            return
        
        if not self._should_process_message(message):
            return
        
        await self._process_quiz_answer(message)
    
    def _should_process_message(self, message: discord.Message) -> bool:
        """Vérifie si le message doit être traité."""
        channel_id = message.channel.id
        
        if not self.quiz_service.has_active_quiz(channel_id):
            return False
        if self.quiz_service.is_qcm_mode(channel_id):
            return False
        if self.quiz_service.has_user_answered(channel_id, message.author.id):
            return False
        if len(message.content) > 50:
            return False
        if message.content.startswith(('/', '!')):
            return False
        
        return True
    
    async def _process_quiz_answer(self, message: discord.Message):
        """Traite une réponse de quiz."""
        channel_id = message.channel.id
        user_id = message.author.id
        
        is_correct, _, difficulty, points = self.quiz_service.check_answer(channel_id, message.content)
        
        self.quiz_service.mark_user_answered(channel_id, user_id, message.author.name, is_correct, points)
        self.stats_service.update_user_stats(user_id, message.author.name, is_correct, difficulty, points)
        
        await self._send_dm_feedback(message.author, is_correct, points, channel_id)
    
    async def _send_dm_feedback(self, user: discord.User, is_correct: bool, points: int, channel_id: int):
        """Envoie un feedback en DM."""
        try:
            embed = self._build_dm_embed(is_correct, points, channel_id)
            await user.send(embed=embed)
        except discord.Forbidden:
            pass  # DMs désactivés
    
    def _build_dm_embed(self, is_correct: bool, points: int, channel_id: int) -> discord.Embed:
        """Construit l'embed de feedback DM."""
        remaining = self.quiz_service.get_remaining_time(channel_id)
        answered = self.quiz_service.get_answered_count(channel_id)
        
        if is_correct:
            embed = discord.Embed(title="✅ Bonne réponse !", color=discord.Color.green())
            embed.add_field(name="Points", value=f"⭐ +{points}", inline=True)
        else:
            embed = discord.Embed(title="❌ Mauvaise réponse !", color=discord.Color.red())
            embed.add_field(name="Points", value="⭐ +0", inline=True)
        
        embed.add_field(name="⏱️ Restant", value=f"**{remaining}** sec", inline=True)
        embed.set_footer(text=f"👥 {answered} personne(s) ont répondu")
        
        return embed