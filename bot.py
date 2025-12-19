import discord
import os
from discord.ext import commands
from discord import app_commands
from dotenv import load_dotenv
import wikipedia
import random

load_dotenv()

bot = discord.Client(intents=discord.Intents.all())
tree = app_commands.CommandTree(bot)

# Questions de mythologie avec réponses
mythology_questions = [
    {
        "question": "Qui est le roi des dieux dans la mythologie grecque ?",
        "answer": "zeus",
        "alternatives": ["jupiter"]
    },
    {
        "question": "Qui est le dieu des enfers dans la mythologie grecque ?",
        "answer": "hadès",
        "alternatives": ["hades", "pluton"]
    },
    {
        "question": "Qui est le dieu de la mer dans la mythologie grecque ?",
        "answer": "poséidon",
        "alternatives": ["poseidon", "neptune"]
    },
    {
        "question": "Qui est la déesse de la sagesse et de la guerre ?",
        "answer": "athéna",
        "alternatives": ["athena", "minerve"]
    },
    {
        "question": "Quel héros a tué la Méduse ?",
        "answer": "persée",
        "alternatives": ["persee", "perseus"]
    },
    {
        "question": "Qui est le dieu de la guerre dans la mythologie grecque ?",
        "answer": "arès",
        "alternatives": ["ares", "mars"]
    },
    {
        "question": "Quel héros a accompli les 12 travaux ?",
        "answer": "héraclès",
        "alternatives": ["heracles", "hercule"]
    },
    {
        "question": "Qui est la déesse de l'amour dans la mythologie grecque ?",
        "answer": "aphrodite",
        "alternatives": ["vénus", "venus"]
    },
    {
        "question": "Quel est le nom du chien à trois têtes gardant les enfers ?",
        "answer": "cerbère",
        "alternatives": ["cerbere", "cerberus"]
    },
    {
        "question": "Qui est le dieu messager avec des sandales ailées ?",
        "answer": "hermès",
        "alternatives": ["hermes", "mercure"]
    }
]

# Stockage des quiz en cours par utilisateur
active_quizzes = {}

@bot.event
async def on_ready():
    print(f'We have logged in as {bot.user}')
    await tree.sync()

@bot.event
async def on_member_join(member):
    channel = bot.get_channel(1450078155304865855)
    await channel.send(f"{member.mention} nous a rejoints.")

def get_mythology_link(figure_name: str) -> str:
    """
    Fetches the Wikipedia link for a mythological figure.
    Returns the URL or an error message.
    """
    try:
        wikipedia.set_lang("fr")
        # Utiliser search pour trouver la bonne page
        search_results = wikipedia.search(figure_name + " mythologie")
        if not search_results:
            search_results = wikipedia.search(figure_name)
        
        if search_results:
            page = wikipedia.page(search_results[0], auto_suggest=False)
            return page.url
        else:
            return f"Aucune page Wikipedia trouvée pour '{figure_name}'."
    except wikipedia.exceptions.PageError:
        return f"Aucune page Wikipedia trouvée pour '{figure_name}'."
    except wikipedia.exceptions.DisambiguationError as e:
        # Prendre la première option en cas d'ambiguïté
        try:
            page = wikipedia.page(e.options[0], auto_suggest=False)
            return page.url
        except:
            return f"Plusieurs résultats trouvés : {', '.join(e.options[:5])}"

@tree.command(name="mythology", description="Get Wikipedia link for a mythological figure")
async def mythology(interaction: discord.Interaction, figure: str):
    """
    Discord slash command to get mythology figure Wikipedia link.
    """
    link = get_mythology_link(figure)
    await interaction.response.send_message(f"**{figure}**: {link}")

@tree.command(name="quiz", description="Réponds à une question sur la mythologie !")
async def quiz(interaction: discord.Interaction):
    """
    Pose une question de mythologie à l'utilisateur.
    """
    question_data = random.choice(mythology_questions)
    active_quizzes[interaction.user.id] = question_data
    
    embed = discord.Embed(
        title="🏛️ Quiz Mythologie",
        description=question_data["question"],
        color=discord.Color.gold()
    )
    embed.set_footer(text="Utilisez /answer pour répondre !")
    
    await interaction.response.send_message(embed=embed)

@tree.command(name="answer", description="Réponds à la question du quiz")
async def answer(interaction: discord.Interaction, reponse: str):
    """
    Vérifie la réponse de l'utilisateur.
    """
    user_id = interaction.user.id
    
    if user_id not in active_quizzes:
        await interaction.response.send_message(
            "❌ Tu n'as pas de quiz en cours ! Utilise `/quiz` pour commencer.",
            ephemeral=True
        )
        return
    
    question_data = active_quizzes[user_id]
    user_answer = reponse.lower().strip()
    correct_answer = question_data["answer"]
    alternatives = question_data.get("alternatives", [])
    
    # Vérifier si la réponse est correcte
    all_valid_answers = [correct_answer] + alternatives
    is_correct = user_answer in all_valid_answers
    
    if is_correct:
        embed = discord.Embed(
            title="✅ Bonne réponse !",
            description=f"Bravo ! La réponse était bien **{correct_answer.capitalize()}** !",
            color=discord.Color.green()
        )
    else:
        embed = discord.Embed(
            title="❌ Mauvaise réponse !",
            description=f"La bonne réponse était **{correct_answer.capitalize()}**.",
            color=discord.Color.red()
        )
    
    # Supprimer le quiz actif
    del active_quizzes[user_id]
    
    embed.set_footer(text="Utilise /quiz pour une nouvelle question !")
    await interaction.response.send_message(embed=embed)

bot.run(os.getenv('DISCORD_TOKEN'))