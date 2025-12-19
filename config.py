import os
from dotenv import load_dotenv

load_dotenv()

DISCORD_TOKEN = os.getenv('DISCORD_TOKEN')
STATS_FILE = "user_stats.json"
WELCOME_CHANNEL_ID = 1450078155304865855