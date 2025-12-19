import random
import discord

myths_collection = [
    {
        "title": "La naissance de Zeus",
        "story": "Cronos, craignant d'être renversé par ses enfants comme il avait renversé son père, dévorait chacun de ses enfants à leur naissance. Rhéa, désespérée, cacha le petit Zeus en Crète et donna à Cronos une pierre emmaillotée. Zeus grandit en secret, nourri par la chèvre Amalthée, jusqu'au jour où il revint défier son père.",
        "moral": "La ruse peut triompher de la force brute.",
        "category": "Origines",
        "color": 0xFFD700
    },
    {
        "title": "Prométhée et le feu",
        "story": "Prométhée, le Titan ami des hommes, vola le feu sacré de l'Olympe pour l'offrir à l'humanité. Zeus, furieux, le condamna à être enchaîné sur le mont Caucase où un aigle lui dévorait le foie chaque jour. Ce supplice dura des millénaires jusqu'à ce qu'Héraclès le libère.",
        "moral": "Le sacrifice pour le bien commun a un prix, mais aussi une récompense.",
        "category": "Titans",
        "color": 0xFF6347
    },
    {
        "title": "Persée et Méduse",
        "story": "Le jeune Persée, fils de Zeus et Danaé, fut envoyé par le roi Polydecte pour rapporter la tête de Méduse, la seule Gorgone mortelle. Avec l'aide d'Athéna et d'Hermès, il obtint des sandales ailées, un casque d'invisibilité et une besace magique. Il trancha la tête de Méduse en la regardant dans son bouclier poli comme un miroir.",
        "moral": "Avec l'aide des dieux et de la ruse, même l'impossible devient possible.",
        "category": "Héros",
        "color": 0x4169E1
    },
    {
        "title": "Thésée et le Minotaure",
        "story": "Athènes devait envoyer chaque année sept jeunes hommes et sept jeunes femmes en sacrifice au Minotaure, monstre enfermé dans le labyrinthe de Crète. Thésée se porta volontaire et, grâce au fil d'Ariane, put retrouver son chemin après avoir tué le monstre. Mais il oublia de changer ses voiles noires, causant le suicide de son père Égée.",
        "moral": "La victoire peut avoir un goût amer si on néglige ceux qu'on aime.",
        "category": "Héros",
        "color": 0x2E8B57
    },
    {
        "title": "Orphée et Eurydice",
        "story": "Orphée, le plus grand musicien, perdit sa bien-aimée Eurydice, mordue par un serpent. Fou de douleur, il descendit aux Enfers et charma Hadès avec sa lyre. Le dieu accepta de libérer Eurydice à condition qu'Orphée ne se retourne pas avant d'atteindre la surface. Mais au dernier moment, il se retourna et la perdit à jamais.",
        "moral": "L'impatience peut nous faire perdre ce que nous chérissons le plus.",
        "category": "Amour",
        "color": 0x9370DB
    },
    {
        "title": "La boîte de Pandore",
        "story": "Zeus créa Pandore, la première femme, pour punir les hommes d'avoir reçu le feu de Prométhée. Elle reçut une jarre (souvent appelée boîte) qu'elle ne devait jamais ouvrir. Cédant à la curiosité, elle l'ouvrit et libéra tous les maux sur le monde. Seule l'espérance resta au fond de la jarre.",
        "moral": "La curiosité peut avoir des conséquences terribles, mais l'espoir demeure toujours.",
        "category": "Origines",
        "color": 0x8B4513
    },
    {
        "title": "Les douze travaux d'Héraclès",
        "story": "Héraclès, rendu fou par Héra, tua sa femme et ses enfants. Pour se purifier, il dut accomplir douze travaux impossibles : tuer le lion de Némée, l'hydre de Lerne, capturer Cerbère, et bien d'autres. Ces épreuves firent de lui le plus grand des héros et lui valurent l'immortalité.",
        "moral": "La rédemption est possible à travers le courage et la persévérance.",
        "category": "Héros",
        "color": 0xB8860B
    },
    {
        "title": "Le jugement de Pâris",
        "story": "Lors du mariage de Thétis et Pélée, Éris lança une pomme d'or 'pour la plus belle'. Héra, Athéna et Aphrodite se disputèrent ce titre. Zeus choisit le prince troyen Pâris pour juger. Chaque déesse tenta de le corrompre. Pâris choisit Aphrodite qui lui promit l'amour de la plus belle femme : Hélène, déclenchant la guerre de Troie.",
        "moral": "Un choix impulsif peut avoir des conséquences désastreuses pour tous.",
        "category": "Guerre de Troie",
        "color": 0xFFD700
    },
    {
        "title": "Icare et Dédale",
        "story": "Dédale, architecte du labyrinthe, fut emprisonné en Crète avec son fils Icare. Il fabriqua des ailes avec des plumes et de la cire pour s'échapper. Il avertit Icare de ne pas voler trop près du soleil. Mais le jeune homme, grisé par le vol, ignora les conseils de son père. La cire fondit et il tomba dans la mer.",
        "moral": "L'orgueil et la désobéissance mènent à la chute.",
        "category": "Tragédie",
        "color": 0x87CEEB
    },
    {
        "title": "L'Odyssée d'Ulysse",
        "story": "Après la guerre de Troie, Ulysse mit dix ans à rentrer chez lui à Ithaque. Il affronta le cyclope Polyphème, résista aux sirènes, échappa à Charybde et Scylla, et déjoua les pièges de Circé et Calypso. Pendant ce temps, sa fidèle Pénélope repoussait les prétendants en tissant et défaisant un linceul.",
        "moral": "La ruse, la patience et la fidélité triomphent de tous les obstacles.",
        "category": "Héros",
        "color": 0x4682B4
    },
    {
        "title": "La colère d'Achille",
        "story": "Pendant le siège de Troie, Agamemnon prit Briséis, la captive d'Achille. Furieux, le héros refusa de combattre. Sans lui, les Grecs subirent défaite sur défaite. Ce n'est qu'après la mort de son ami Patrocle qu'Achille reprit les armes pour venger celui qu'il aimait, tuant le prince Hector.",
        "moral": "La colère aveugle mène au malheur, seul l'amour peut nous pousser à agir.",
        "category": "Guerre de Troie",
        "color": 0xDAA520
    },
    {
        "title": "Narcisse et Écho",
        "story": "Narcisse était un jeune homme d'une beauté exceptionnelle mais cruel envers ceux qui l'aimaient. La nymphe Écho, condamnée à répéter les paroles des autres, tomba amoureuse de lui mais fut rejetée. Némésis punit Narcisse en le faisant tomber amoureux de son propre reflet. Il dépérit en contemplant son image dans l'eau.",
        "moral": "L'orgueil et l'égoïsme mènent à la solitude et à la destruction.",
        "category": "Amour",
        "color": 0x00CED1
    }
]


def get_random_myth() -> dict:
    """Retourne un mythe aléatoire."""
    return random.choice(myths_collection)


def get_myth_embed(myth: dict) -> discord.Embed:
    """Construit l'embed pour un mythe."""
    embed = discord.Embed(
        title=f"📜 {myth['title']}",
        description=myth['story'],
        color=myth.get('color', 0xFFD700)
    )
    
    embed.add_field(
        name="💡 Morale",
        value=myth['moral'],
        inline=False
    )
    
    embed.add_field(
        name="📁 Catégorie",
        value=myth.get('category', 'Mythologie'),
        inline=True
    )
    
    embed.set_footer(text="🏛️ Mythologie Grecque")
    
    return embed


def get_myths_by_category(category: str) -> list[dict]:
    """Retourne les mythes d'une catégorie donnée."""
    return [myth for myth in myths_collection if myth.get('category', '').lower() == category.lower()]


def get_all_categories() -> list[str]:
    """Retourne toutes les catégories uniques."""
    categories = set()
    for myth in myths_collection:
        if myth.get('category'):
            categories.add(myth['category'])
    return sorted(list(categories))