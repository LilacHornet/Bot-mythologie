import discord
from discord.ext import commands


class QuizListeners:
    """Listeners pour le quiz."""
    
    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        """Écoute les messages pour détecter les réponses au quiz."""
        # Ignorer les messages du bot
        if message.author.bot:
            return
        
        channel_id = message.channel.id
        user_id = message.author.id
        
        # Vérifier s'il y a un quiz en cours dans ce channel
        if not self.quiz_service.has_active_quiz(channel_id):
            return
        
        # Vérifier si l'utilisateur a déjà répondu
        if self.quiz_service.has_user_answered(channel_id, user_id):
            return
        
        # Vérifier la réponse
        reponse = message.content
        
        # Ignorer les messages trop longs ou les commandes
        if len(reponse) > 50 or reponse.startswith('/') or reponse.startswith('!'):
            return
        
        is_correct, correct_answer, difficulty, points = self.quiz_service.check_answer(channel_id, reponse)
        diff_config = self.quiz_service.get_difficulty_config(difficulty)
        remaining_time = self.quiz_service.get_remaining_time(channel_id)
        
        # Marquer l'utilisateur comme ayant répondu
        self.quiz_service.mark_user_answered(channel_id, user_id, message.author.name, is_correct, points)
        
        # Sauvegarder les stats
        self.stats_service.update_user_stats(
            user_id, 
            message.author.name, 
            is_correct, 
            difficulty, 
            points
        )
        
        # Nombre de participants
        answered_count = self.quiz_service.get_answered_count(channel_id)
        
        # Envoyer un message privé de confirmation
        try:
            if is_correct:
                embed = discord.Embed(
                    title="✅ Bonne réponse !",
                    description=f"Bravo ! Tu as trouvé la bonne réponse !",
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
                name="⏱️ Temps restant",
                value=f"**{remaining_time}** secondes",
                inline=True
            )
            embed.set_footer(text=f"👥 {answered_count} personne(s) ont répondu")
            await message.author.send(embed=embed)
        except discord.Forbidden:
            # L'utilisateur a les DMs désactivés
            pass