import random
import discord

# Collection de funfacts sur la mythologie
FUNFACTS = [
    {
        "fact": "Zeus s'est transformé en cygne, taureau, pluie d'or et même en fourmi pour séduire des mortelles !",
        "category": "Zeus",
        "emoji": "⚡"
    },
    {
        "fact": "Athéna est née tout armée de la tête de Zeus après qu'Héphaïstos lui ait fendu le crâne avec une hache.",
        "category": "Naissance",
        "emoji": "🦉"
    },
    {
        "fact": "Le talon d'Achille était son seul point faible car sa mère Thétis le tenait par là en le plongeant dans le Styx.",
        "category": "Héros",
        "emoji": "🦶"
    },
    {
        "fact": "Hermès a inventé la lyre le jour de sa naissance en utilisant une carapace de tortue !",
        "category": "Inventions",
        "emoji": "🎵"
    },
    {
        "fact": "Poséidon a créé le premier cheval en frappant un rocher avec son trident.",
        "category": "Créations",
        "emoji": "🐴"
    },
    {
        "fact": "Dionysos est le seul dieu olympien né d'une mère mortelle (Sémélé).",
        "category": "Dionysos",
        "emoji": "🍇"
    },
    {
        "fact": "Héphaïstos a été jeté de l'Olympe deux fois : une fois par Héra, une fois par Zeus !",
        "category": "Tragédie",
        "emoji": "🔨"
    },
    {
        "fact": "Cerbère, le chien des Enfers, avait non seulement trois têtes mais aussi une queue de serpent.",
        "category": "Créatures",
        "emoji": "🐕"
    },
    {
        "fact": "Aphrodite est née de l'écume de la mer, formée autour des parties génitales d'Ouranos jetées dans l'océan.",
        "category": "Naissance",
        "emoji": "🌊"
    },
    {
        "fact": "Les Amazones étaient des guerrières qui se coupaient un sein pour mieux tirer à l'arc.",
        "category": "Guerriers",
        "emoji": "🏹"
    },
    {
        "fact": "Prométhée a non seulement volé le feu, mais il a aussi créé les premiers hommes à partir d'argile.",
        "category": "Titans",
        "emoji": "🔥"
    },
    {
        "fact": "Héraclès a étranglé deux serpents dans son berceau alors qu'il n'était qu'un bébé !",
        "category": "Héros",
        "emoji": "💪"
    },
    {
        "fact": "Narcisse était si beau que même les nymphes des rivières tombaient amoureuses de lui.",
        "category": "Beauté",
        "emoji": "🪞"
    },
    {
        "fact": "Le Minotaure mangeait 7 jeunes hommes et 7 jeunes femmes athéniens chaque année.",
        "category": "Créatures",
        "emoji": "🐂"
    },
    {
        "fact": "Pégase, le cheval ailé, est né du sang de Méduse quand Persée lui a tranché la tête.",
        "category": "Créatures",
        "emoji": "🦄"
    },
    {
        "fact": "Hadès possédait un casque d'invisibilité forgé par les Cyclopes.",
        "category": "Objets",
        "emoji": "👻"
    },
    {
        "fact": "Artémis a demandé à Zeus de rester vierge pour toujours à l'âge de 3 ans.",
        "category": "Artémis",
        "emoji": "🌙"
    },
    {
        "fact": "Le cheval de Troie contenait entre 23 et 50 guerriers grecs selon les sources.",
        "category": "Guerre de Troie",
        "emoji": "🐎"
    },
    {
        "fact": "Apollon a accidentellement tué son amant Hyacinthe avec un disque, et de son sang naquit la fleur.",
        "category": "Tragédie",
        "emoji": "🌺"
    },
    {
        "fact": "Tantale a été condamné à avoir faim et soif éternellement pour avoir servi son fils aux dieux.",
        "category": "Châtiments",
        "emoji": "😫"
    }
]


def get_random_funfact() -> dict:
    """Retourne un funfact aléatoire."""
    return random.choice(FUNFACTS)


def get_funfact_embed(funfact: dict) -> discord.Embed:
    """Construit l'embed pour un funfact."""
    emoji = funfact.get('emoji', '🏛️')
    
    embed = discord.Embed(
        title=f"{emoji} Le saviez-vous ?",
        description=funfact['fact'],
        color=discord.Color.gold()
    )
    
    embed.add_field(
        name="📁 Catégorie",
        value=funfact.get('category', 'Mythologie'),
        inline=True
    )
    
    embed.set_footer(text="🏛️ Mythologie Grecque • /funfact pour un autre fait")
    
    return embed


def get_funfacts_by_category(category: str) -> list[dict]:
    """Retourne les funfacts d'une catégorie donnée."""
    return [ff for ff in FUNFACTS if ff.get('category', '').lower() == category.lower()]