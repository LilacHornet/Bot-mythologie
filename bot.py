import discord
import os
from discord.ext import commands
from discord import app_commands
from dotenv import load_dotenv
import wikipedia
import random
import json

load_dotenv()

bot = discord.Client(intents=discord.Intents.all())
tree = app_commands.CommandTree(bot)

STATS_FILE = "user_stats.json"

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

def load_stats() -> dict:
    """Charge les statistiques depuis le fichier JSON."""
    if os.path.exists(STATS_FILE):
        try:
            with open(STATS_FILE, "r", encoding="utf-8") as f:
                content = f.read()
                if content.strip():  # Vérifier que le fichier n'est pas vide
                    return json.loads(content)
        except (json.JSONDecodeError, IOError):
            # Si le fichier est corrompu, on retourne un dict vide
            pass
    return {}

def save_stats(stats: dict):
    """Sauvegarde les statistiques dans le fichier JSON."""
    with open(STATS_FILE, "w", encoding="utf-8") as f:
        json.dump(stats, f, indent=4, ensure_ascii=False)

def update_user_stats(user_id: int, username: str, is_correct: bool):
    """Met à jour les statistiques d'un utilisateur."""
    stats = load_stats()
    user_id_str = str(user_id)
    
    if user_id_str not in stats:
        stats[user_id_str] = {
            "username": username,
            "correct": 0,
            "wrong": 0,
            "total": 0
        }
    
    stats[user_id_str]["username"] = username  # Mettre à jour le nom
    stats[user_id_str]["total"] += 1
    
    if is_correct:
        stats[user_id_str]["correct"] += 1
    else:
        stats[user_id_str]["wrong"] += 1
    
    save_stats(stats)

def get_user_stats(user_id: int) -> dict | None:
    """Récupère les statistiques d'un utilisateur."""
    stats = load_stats()
    return stats.get(str(user_id))

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
    
    # Sauvegarder les stats
    update_user_stats(user_id, interaction.user.name, is_correct)
    
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

@tree.command(name="stats", description="Affiche tes statistiques de quiz")
async def stats(interaction: discord.Interaction):
    """Affiche les statistiques de l'utilisateur."""
    user_stats = get_user_stats(interaction.user.id)
    
    if not user_stats:
        await interaction.response.send_message(
            "📊 Tu n'as pas encore répondu à un quiz ! Utilise `/quiz` pour commencer.",
            ephemeral=True
        )
        return
    
    correct = user_stats["correct"]
    wrong = user_stats["wrong"]
    total = user_stats["total"]
    percentage = (correct / total * 100) if total > 0 else 0
    
    embed = discord.Embed(
        title=f"📊 Statistiques de {interaction.user.name}",
        color=discord.Color.blue()
    )
    embed.add_field(name="✅ Bonnes réponses", value=str(correct), inline=True)
    embed.add_field(name="❌ Mauvaises réponses", value=str(wrong), inline=True)
    embed.add_field(name="📝 Total", value=str(total), inline=True)
    embed.add_field(name="📈 Taux de réussite", value=f"{percentage:.1f}%", inline=False)
    
    await interaction.response.send_message(embed=embed)

@tree.command(name="leaderboard", description="Affiche le classement des meilleurs joueurs")
async def leaderboard(interaction: discord.Interaction):
    """Affiche le classement des joueurs."""
    stats = load_stats()
    
    if not stats:
        await interaction.response.send_message(
            "📊 Aucune statistique disponible pour le moment.",
            ephemeral=True
        )
        return
    
    # Trier par nombre de bonnes réponses
    sorted_users = sorted(
        stats.items(),
        key=lambda x: x[1]["correct"],
        reverse=True
    )[:10]
    
    embed = discord.Embed(
        title="🏆 Classement Mythologie",
        color=discord.Color.gold()
    )
    
    medals = ["🥇", "🥈", "🥉"]
    description = ""
    
    for i, (user_id, user_stats) in enumerate(sorted_users):
        medal = medals[i] if i < 3 else f"**{i+1}.**"
        percentage = (user_stats["correct"] / user_stats["total"] * 100) if user_stats["total"] > 0 else 0
        description += f"{medal} {user_stats['username']} - {user_stats['correct']} ✅ ({percentage:.1f}%)\n"
    
    embed.description = description
    await interaction.response.send_message(embed=embed)

bot.run(os.getenv('DISCORD_TOKEN'))