import discord
import os
from discord.ext import commands
from discord import app_commands
from dotenv import load_dotenv
import wikipedia

load_dotenv()

bot = discord.Client(intents=discord.Intents.all())
tree = app_commands.CommandTree(bot)

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

bot.run(os.getenv('DISCORD_TOKEN'))