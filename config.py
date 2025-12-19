import os
from dotenv import load_dotenv

load_dotenv()

DISCORD_TOKEN = os.getenv('DISCORD_TOKEN')
STATS_FILE = "user_stats.json"
DAILY_MYTH_FILE = "daily_myth_config.json"

# Heure d'envoi du mythe quotidien (format 24h)
DAILY_MYTH_HOUR = 14
DAILY_MYTH_MINUTE = 00
