from .quiz_cog import QuizCog

async def setup(bot):
    await bot.add_cog(QuizCog(bot))