import discord
import random

# Collection de mythes pour l'envoi quotidien
DAILY_MYTHS = [
    {
        "title": "La naissance de Zeus",
        "content": "Cronos, le titan, dévorait tous ses enfants à leur naissance car une prophétie annonçait qu'un de ses fils le détrônerait. Rhéa, son épouse, réussit à sauver Zeus en le cachant en Crète et en donnant à Cronos une pierre emmaillotée à avaler. Zeus grandit en secret et revint plus tard pour libérer ses frères et sœurs.",
        "figure": "Zeus",
        "category": "Origine des dieux",
        "color": discord.Color.gold()
    },
    {
        "title": "Les douze travaux d'Héraclès",
        "content": "Pour expier le meurtre de sa famille commis sous l'emprise de la folie envoyée par Héra, Héraclès dut accomplir douze travaux impossibles : tuer le lion de Némée, l'hydre de Lerne, capturer la biche de Cérynie, le sanglier d'Érymanthe, nettoyer les écuries d'Augias, tuer les oiseaux du lac Stymphale, capturer le taureau de Crète, les juments de Diomède, la ceinture d'Hippolyte, les bœufs de Géryon, les pommes d'or des Hespérides, et capturer Cerbère.",
        "figure": "Héraclès",
        "category": "Héros",
        "color": discord.Color.red()
    },
    {
        "title": "Persée et Méduse",
        "content": "Persée, fils de Zeus et Danaé, fut envoyé par le roi Polydecte pour tuer Méduse, la seule Gorgone mortelle. Avec l'aide d'Athéna et d'Hermès, il reçut des sandales ailées, le casque d'invisibilité d'Hadès et une besace magique. Il trancha la tête de Méduse en la regardant dans son bouclier poli comme un miroir, évitant ainsi son regard pétrifiant.",
        "figure": "Persée",
        "category": "Héros",
        "color": discord.Color.purple()
    },
    {
        "title": "L'enlèvement de Perséphone",
        "content": "Hadès, dieu des Enfers, tomba amoureux de Perséphone et l'enleva pour en faire sa reine. Sa mère Déméter, déesse des moissons, plongea le monde dans un hiver éternel. Zeus intervint et un accord fut trouvé : Perséphone passerait six mois avec Hadès et six mois avec sa mère, créant ainsi le cycle des saisons.",
        "figure": "Perséphone",
        "category": "Origine des saisons",
        "color": discord.Color.dark_green()
    },
    {
        "title": "Prométhée et le feu",
        "content": "Prométhée, le titan ami des hommes, vola le feu aux dieux de l'Olympe pour l'offrir aux mortels. En punition, Zeus le fit enchaîner au mont Caucase où un aigle lui dévorait le foie chaque jour, celui-ci se régénérant chaque nuit. Il fut finalement libéré par Héraclès.",
        "figure": "Prométhée",
        "category": "Titans",
        "color": discord.Color.orange()
    },
    {
        "title": "Orphée et Eurydice",
        "content": "Orphée, le plus grand musicien de la mythologie, descendit aux Enfers pour ramener sa bien-aimée Eurydice, morte d'une morsure de serpent. Sa musique charma Hadès qui accepta de la laisser partir, à condition qu'Orphée ne se retourne pas avant d'avoir quitté les Enfers. Au dernier moment, il se retourna et perdit Eurydice à jamais.",
        "figure": "Orphée",
        "category": "Amour tragique",
        "color": discord.Color.blue()
    },
    {
        "title": "Le jugement de Pâris",
        "content": "Lors du mariage de Pélée et Thétis, Éris, déesse de la discorde, lança une pomme d'or portant l'inscription 'À la plus belle'. Héra, Athéna et Aphrodite se disputèrent le fruit. Zeus désigna Pâris, prince troyen, comme juge. Chaque déesse lui offrit un présent : Héra le pouvoir, Athéna la sagesse, Aphrodite l'amour de la plus belle femme. Pâris choisit Aphrodite, déclenchant la guerre de Troie.",
        "figure": "Pâris",
        "category": "Guerre de Troie",
        "color": discord.Color.magenta()
    },
    {
        "title": "Thésée et le Minotaure",
        "content": "Chaque année, Athènes devait envoyer sept jeunes hommes et sept jeunes femmes en sacrifice au Minotaure, monstre mi-homme mi-taureau enfermé dans le labyrinthe de Crète. Thésée se porta volontaire et, grâce au fil d'Ariane, réussit à tuer le monstre et à retrouver la sortie du labyrinthe.",
        "figure": "Thésée",
        "category": "Héros",
        "color": discord.Color.teal()
    },
    {
        "title": "La boîte de Pandore",
        "content": "Pandore fut la première femme mortelle, créée par les dieux sur ordre de Zeus pour punir les hommes après le vol du feu par Prométhée. Elle reçut une jarre (souvent appelée boîte) qu'elle ne devait jamais ouvrir. Poussée par la curiosité, elle l'ouvrit et libéra tous les maux sur l'humanité. Seule l'espérance resta au fond de la jarre.",
        "figure": "Pandore",
        "category": "Origine des maux",
        "color": discord.Color.dark_purple()
    },
    {
        "title": "Icare et Dédale",
        "content": "Dédale, l'architecte du labyrinthe, fut emprisonné en Crète avec son fils Icare. Il fabriqua des ailes avec des plumes et de la cire pour s'échapper. Il avertit Icare de ne pas voler trop près du soleil. Mais Icare, grisé par le vol, monta trop haut. La cire fondit et il tomba dans la mer qui porte désormais son nom.",
        "figure": "Icare",
        "category": "Leçons de vie",
        "color": discord.Color.gold()
    },
    {
        "title": "Narcisse et Écho",
        "content": "Narcisse était un jeune homme d'une beauté extraordinaire qui rejetait tous ses prétendants. La nymphe Écho, condamnée à ne répéter que les derniers mots des autres, tomba amoureuse de lui mais fut repoussée. En punition, Némésis fit que Narcisse tombe amoureux de son propre reflet dans l'eau, où il resta jusqu'à sa mort, se transformant en la fleur qui porte son nom.",
        "figure": "Narcisse",
        "category": "Métamorphoses",
        "color": discord.Color.light_grey()
    },
    {
        "title": "La colère d'Achille",
        "content": "Pendant la guerre de Troie, Agamemnon prit Briséis, la captive d'Achille, provoquant la colère du héros qui refusa de combattre. Sans lui, les Grecs subirent de lourdes défaites. Ce n'est qu'après la mort de son ami Patrocle, tué par Hector, qu'Achille reprit les armes pour venger son compagnon.",
        "figure": "Achille",
        "category": "Guerre de Troie",
        "color": discord.Color.dark_red()
    },
    {
        "title": "L'Odyssée d'Ulysse",
        "content": "Après la guerre de Troie, Ulysse mit dix ans à rentrer chez lui à Ithaque. Il affronta le cyclope Polyphème, résista aux chants des Sirènes, échappa à Charybde et Scylla, et passa sept ans captif de la nymphe Calypso. Finalement rentré, il dut éliminer les prétendants qui courtisaient sa femme Pénélope.",
        "figure": "Ulysse",
        "category": "Épopée",
        "color": discord.Color.dark_blue()
    },
    {
        "title": "Apollon et Daphné",
        "content": "Apollon, frappé par une flèche d'Éros, tomba éperdument amoureux de la nymphe Daphné, qui elle fut touchée par une flèche de plomb la rendant insensible à l'amour. Poursuivie par Apollon, elle supplia son père, le dieu-fleuve Pénée, de la sauver. Il la transforma en laurier, arbre qu'Apollon adopta comme symbole sacré.",
        "figure": "Apollon",
        "category": "Métamorphoses",
        "color": discord.Color.yellow()
    },
    {
        "title": "La forge d'Héphaïstos",
        "content": "Héphaïstos, dieu du feu et de la forge, fut jeté de l'Olympe par sa mère Héra à cause de sa laideur. Recueilli par les nymphes marines, il devint le plus habile des artisans divins. Il forgea les armes des dieux, le trident de Poséidon, l'égide de Zeus, et même des automates de bronze pour le servir.",
        "figure": "Héphaïstos",
        "category": "Dieux Olympiens",
        "color": discord.Color.dark_orange()
    }
]


def get_random_myth() -> dict:
    """Retourne un mythe aléatoire."""
    return random.choice(DAILY_MYTHS)


def get_myth_embed(myth: dict) -> discord.Embed:
    """Crée un embed pour un mythe."""
    embed = discord.Embed(
        title=f"📜 {myth['title']}",
        description=myth["content"],
        color=myth["color"]
    )
    embed.add_field(
        name="👤 Figure principale",
        value=myth["figure"],
        inline=True
    )
    embed.add_field(
        name="📂 Catégorie",
        value=myth["category"],
        inline=True
    )
    embed.set_footer(text="🏛️ Mythe du jour • Utilisez /learn pour en savoir plus")
    return embed