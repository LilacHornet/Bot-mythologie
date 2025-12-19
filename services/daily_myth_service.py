import json
import os
from datetime import datetime

from config import DAILY_MYTH_FILE, DAILY_MYTH_HOUR, DAILY_MYTH_MINUTE


class DailyMythService:
    """Service pour gérer la configuration du mythe quotidien."""
    
    def __init__(self):
        self.config_file = DAILY_MYTH_FILE
        self.config = self._load_config()
    
    def _load_config(self) -> dict:
        """Charge la configuration depuis le fichier JSON."""
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except (json.JSONDecodeError, IOError):
                return {}
        return {}
    
    def _save_config(self):
        """Sauvegarde la configuration dans le fichier JSON."""
        with open(self.config_file, 'w', encoding='utf-8') as f:
            json.dump(self.config, f, indent=4, ensure_ascii=False)
    
    def set_channel(self, guild_id: int, channel_id: int):
        """Définit le channel pour le mythe quotidien d'un serveur."""
        existing_config = self.config.get(str(guild_id), {})
        self.config[str(guild_id)] = {
            "channel_id": channel_id,
            "enabled": True,
            "last_sent": existing_config.get("last_sent"),
            "hour": existing_config.get("hour", DAILY_MYTH_HOUR),
            "minute": existing_config.get("minute", DAILY_MYTH_MINUTE)
        }
        self._save_config()
    
    def remove_channel(self, guild_id: int):
        """Supprime le channel du mythe quotidien d'un serveur."""
        if str(guild_id) in self.config:
            del self.config[str(guild_id)]
            self._save_config()
    
    def get_channel(self, guild_id: int) -> int | None:
        """Récupère le channel_id pour un serveur."""
        guild_config = self.config.get(str(guild_id))
        if guild_config:
            return guild_config.get("channel_id")
        return None
    
    def get_all_configs(self) -> dict:
        """Récupère toutes les configurations des serveurs."""
        return self.config
    
    def get_all_channels(self) -> list[int]:
        """Récupère tous les channels configurés et activés."""
        channels = []
        for guild_id, guild_config in self.config.items():
            if guild_config.get("enabled") and guild_config.get("channel_id"):
                channels.append(guild_config["channel_id"])
        return channels
    
    def is_enabled(self, guild_id: int) -> bool:
        """Vérifie si le mythe quotidien est activé pour un serveur."""
        guild_config = self.config.get(str(guild_id))
        return guild_config is not None and guild_config.get("enabled", False)
    
    def enable(self, guild_id: int):
        """Active le mythe quotidien pour un serveur."""
        if str(guild_id) in self.config:
            self.config[str(guild_id)]["enabled"] = True
            self._save_config()
    
    def disable(self, guild_id: int):
        """Désactive le mythe quotidien pour un serveur."""
        if str(guild_id) in self.config:
            self.config[str(guild_id)]["enabled"] = False
            self._save_config()
    
    def toggle(self, guild_id: int) -> bool:
        """Active/désactive le mythe quotidien. Retourne le nouvel état."""
        if str(guild_id) in self.config:
            self.config[str(guild_id)]["enabled"] = not self.config[str(guild_id)].get("enabled", False)
            self._save_config()
            return self.config[str(guild_id)]["enabled"]
        return False
    
    def set_time(self, guild_id: int, hour: int, minute: int) -> bool:
        """Définit l'heure d'envoi du mythe quotidien pour un serveur."""
        if str(guild_id) not in self.config:
            return False
        
        # Validation
        if not (0 <= hour <= 23) or not (0 <= minute <= 59):
            return False
        
        self.config[str(guild_id)]["hour"] = hour
        self.config[str(guild_id)]["minute"] = minute
        self._save_config()
        return True
    
    def get_time(self, guild_id: int) -> tuple[int, int]:
        """Récupère l'heure d'envoi pour un serveur. Retourne (hour, minute)."""
        guild_config = self.config.get(str(guild_id))
        if guild_config:
            return (
                guild_config.get("hour", DAILY_MYTH_HOUR),
                guild_config.get("minute", DAILY_MYTH_MINUTE)
            )
        return (DAILY_MYTH_HOUR, DAILY_MYTH_MINUTE)
    
    def update_last_sent(self, guild_id: int):
        """Met à jour la date du dernier envoi."""
        if str(guild_id) in self.config:
            self.config[str(guild_id)]["last_sent"] = datetime.now().isoformat()
            self._save_config()