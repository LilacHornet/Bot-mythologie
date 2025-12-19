import discord
import random

# Collection de funfacts sur la mythologie
FUNFACTS = [
    {
        "fact": "Zeus s'est transformé en cygne, taureau, pluie d'or, et même en fourmi pour séduire des mortelles et des déesses !",
        "category": "Zeus",
        "emoji": "⚡"
    },
    {
        "fact": "Athéna est née directement de la tête de Zeus, après qu'il eut avalé sa mère Métis. Héphaïstos dut lui fendre le crâne pour la libérer !",
        "category": "Naissance divine",
        "emoji": "🦉"
    },
    {
        "fact": "Hermès a volé le troupeau de vaches d'Apollon le jour même de sa naissance, alors qu'il n'était qu'un bébé !",
        "category": "Hermès",
        "emoji": "👟"
    },
    {
        "fact": "Le mot 'panique' vient du dieu Pan, dont le cri effrayait les voyageurs dans les forêts.",
        "category": "Étymologie",
        "emoji": "😱"
    },
    {
        "fact": "Dionysos est le seul dieu olympien à avoir une mère mortelle (Sémélé). Zeus l'a porté dans sa cuisse pour terminer sa gestation !",
        "category": "Dionysos",
        "emoji": "🍷"
    },
    {
        "fact": "Le talon d'Achille était sa seule faiblesse car sa mère Thétis le tenait par là quand elle l'a plongé dans le Styx.",
        "category": "Achille",
        "emoji": "🦶"
    },
    {
        "fact": "Poséidon a créé le cheval pour impressionner Déméter, qui lui avait demandé de créer le plus bel animal du monde.",
        "category": "Poséidon",
        "emoji": "🐴"
    },
    {
        "fact": "Le mot 'écho' vient de la nymphe Écho, condamnée par Héra à ne répéter que les derniers mots des autres.",
        "category": "Étymologie",
        "emoji": "🔊"
    },
    {
        "fact": "Hadès n'est pas un dieu maléfique ! Il était considéré comme juste et équitable dans son rôle de gardien des morts.",
        "category": "Hadès",
        "emoji": "💀"
    },
    {
        "fact": "Les Amazones se coupaient le sein droit pour mieux tirer à l'arc. 'Amazone' signifierait 'sans sein' en grec.",
        "category": "Amazones",
        "emoji": "🏹"
    },
    {
        "fact": "Aphrodite est née de l'écume de la mer, formée quand les parties génitales d'Ouranos furent jetées dans l'océan !",
        "category": "Aphrodite",
        "emoji": "🐚"
    },
    {
        "fact": "Le mot 'titanesque' vient des Titans, les géants qui régnaient avant les dieux de l'Olympe.",
        "category": "Étymologie",
        "emoji": "💪"
    },
    {
        "fact": "Arès, dieu de la guerre, était détesté par presque tous les autres dieux, y compris ses propres parents Zeus et Héra !",
        "category": "Arès",
        "emoji": "⚔️"
    },
    {
        "fact": "Le chien à trois têtes Cerbère adorait les gâteaux au miel. C'est ainsi qu'Orphée et Énée ont pu passer devant lui !",
        "category": "Créatures",
        "emoji": "🐕"
    },
    {
        "fact": "Héphaïstos a fabriqué des femmes robots en or pour l'aider dans sa forge. C'étaient les premiers 'androïdes' de l'histoire !",
        "category": "Héphaïstos",
        "emoji": "🤖"
    },
    {
        "fact": "Le mot 'océan' vient du titan Océanos, qui personnifiait le fleuve mondial entourant la Terre.",
        "category": "Étymologie",
        "emoji": "🌊"
    },
    {
        "fact": "Artémis a transformé le chasseur Actéon en cerf parce qu'il l'avait vue nue par accident. Ses propres chiens l'ont dévoré !",
        "category": "Artémis",
        "emoji": "🦌"
    },
    {
        "fact": "Le narcissisme tire son nom de Narcisse, qui est tombé amoureux de son propre reflet dans l'eau.",
        "category": "Étymologie",
        "emoji": "🪞"
    },
    {
        "fact": "Héra a envoyé deux serpents pour tuer Héraclès bébé, mais il les a étranglés à mains nues dans son berceau !",
        "category": "Héraclès",
        "emoji": "🐍"
    },
    {
        "fact": "Le cheval de Troie n'apparaît pas dans l'Iliade d'Homère ! On le trouve dans l'Odyssée et l'Énéide.",
        "category": "Guerre de Troie",
        "emoji": "🐎"
    },
    {
        "fact": "Apollon a perdu un concours musical contre le satyre Marsyas. Furieux, il l'a écorché vif !",
        "category": "Apollon",
        "emoji": "🎵"
    },
    {
        "fact": "Le mot 'morphine' vient de Morphée, le dieu des rêves, fils d'Hypnos (le sommeil).",
        "category": "Étymologie",
        "emoji": "💤"
    },
    {
        "fact": "Persée a utilisé la tête de Méduse pour transformer le titan Atlas en montagne, créant ainsi la chaîne de l'Atlas au Maroc.",
        "category": "Persée",
        "emoji": "🏔️"
    },
    {
        "fact": "Le labyrinthe du Minotaure était si complexe que même son créateur Dédale a eu du mal à en sortir !",
        "category": "Dédale",
        "emoji": "🌀"
    },
    {
        "fact": "Sisyphe était si rusé qu'il a réussi à enchaîner Thanatos (la Mort) lui-même, empêchant quiconque de mourir pendant un temps !",
        "category": "Sisyphe",
        "emoji": "⛓️"
    }
]


def get_random_funfact() -> dict:
    """Retourne un funfact aléatoire."""
    return random.choice(FUNFACTS)


def get_funfact_embed(funfact: dict) -> discord.Embed:
    """Crée un embed pour un funfact."""
    embed = discord.Embed(
        title=f"{funfact['emoji']} Le saviez-vous ?",
        description=funfact["fact"],
        color=discord.Color.random()
    )
    embed.add_field(
        name="📂 Catégorie",
        value=funfact["category"],
        inline=True
    )
    embed.set_footer(text="🏛️ Fun Fact Mythologie • /funfact pour un autre")
    return embed