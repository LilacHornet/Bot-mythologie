import discord

# Configuration des difficultés
DIFFICULTY_CONFIG = {
    "easy": {
        "name": "Facile",
        "emoji": "🟢",
        "color": discord.Color.green()
    },
    "medium": {
        "name": "Moyen",
        "emoji": "🟠",
        "color": discord.Color.orange()
    },
    "hard": {
        "name": "Difficile",
        "emoji": "🔴",
        "color": discord.Color.red()
    }
}

# Points par difficulté
DIFFICULTY_POINTS = {
    "easy": 1,
    "medium": 2,
    "hard": 3
}

# Questions de mythologie avec choix multiples pour le mode QCM
mythology_questions = {
    "easy": [
        {
            "question": "Qui est le roi des dieux dans la mythologie grecque ?",
            "answer": "zeus",
            "alternatives": ["jupiter"],
            "choices": ["Zeus", "Poséidon", "Hadès", "Apollon"]
        },
        {
            "question": "Quel est le nom du dieu de la mer ?",
            "answer": "poséidon",
            "alternatives": ["poseidon", "neptune"],
            "choices": ["Poséidon", "Zeus", "Arès", "Hermès"]
        },
        {
            "question": "Qui est la déesse de l'amour ?",
            "answer": "aphrodite",
            "alternatives": ["venus"],
            "choices": ["Aphrodite", "Athéna", "Héra", "Artémis"]
        },
        {
            "question": "Quel héros a tué Méduse ?",
            "answer": "persée",
            "alternatives": ["persee", "perseus"],
            "choices": ["Persée", "Héraclès", "Thésée", "Achille"]
        },
        {
            "question": "Combien de travaux Héraclès a-t-il dû accomplir ?",
            "answer": "12",
            "alternatives": ["douze"],
            "choices": ["12", "10", "7", "15"]
        },
        {
            "question": "Qui est le dieu des Enfers ?",
            "answer": "hadès",
            "alternatives": ["hades", "pluton"],
            "choices": ["Hadès", "Thanatos", "Cronos", "Éros"]
        },
        {
            "question": "Quel est le nom de la déesse de la sagesse ?",
            "answer": "athéna",
            "alternatives": ["athena", "minerve"],
            "choices": ["Athéna", "Héra", "Déméter", "Hestia"]
        },
        {
            "question": "Qui est le messager des dieux ?",
            "answer": "hermès",
            "alternatives": ["hermes", "mercure"],
            "choices": ["Hermès", "Apollon", "Arès", "Dionysos"]
        },
        {
            "question": "Quel animal est sacré pour Athéna ?",
            "answer": "chouette",
            "alternatives": ["hibou"],
            "choices": ["Chouette", "Aigle", "Serpent", "Paon"]
        },
        {
            "question": "Qui a offert le feu aux hommes ?",
            "answer": "prométhée",
            "alternatives": ["promethee", "prometheus"],
            "choices": ["Prométhée", "Zeus", "Héphaïstos", "Hermès"]
        }
    ],
    "medium": [
        {
            "question": "Qui est la mère d'Achille ?",
            "answer": "thétis",
            "alternatives": ["thetis"],
            "choices": ["Thétis", "Héra", "Aphrodite", "Déméter"]
        },
        {
            "question": "Quel monstre vivait dans le labyrinthe de Crète ?",
            "answer": "minotaure",
            "alternatives": ["le minotaure"],
            "choices": ["Minotaure", "Méduse", "Chimère", "Hydre"]
        },
        {
            "question": "Qui a construit le labyrinthe du Minotaure ?",
            "answer": "dédale",
            "alternatives": ["dedale", "daedalus"],
            "choices": ["Dédale", "Icare", "Minos", "Thésée"]
        },
        {
            "question": "Quel est le nom du passeur des Enfers ?",
            "answer": "charon",
            "alternatives": ["caron"],
            "choices": ["Charon", "Cerbère", "Hadès", "Thanatos"]
        },
        {
            "question": "Qui sont les trois Gorgones ?",
            "answer": "méduse, sthéno et euryale",
            "alternatives": ["meduse stheno euryale", "méduse sthéno euryale"],
            "choices": ["Méduse, Sthéno, Euryale", "Clotho, Lachésis, Atropos", "Hécate, Séléné, Éos", "Némésis, Thémis, Dikè"]
        },
        {
            "question": "Qui est le père de Zeus ?",
            "answer": "cronos",
            "alternatives": ["kronos", "saturne"],
            "choices": ["Cronos", "Ouranos", "Gaïa", "Rhéa"]
        },
        {
            "question": "Quelle pomme a déclenché la guerre de Troie ?",
            "answer": "pomme de la discorde",
            "alternatives": ["pomme d'or", "la pomme de la discorde"],
            "choices": ["Pomme de la discorde", "Pomme d'Éden", "Pomme d'Hespérides", "Pomme sacrée"]
        },
        {
            "question": "Quel héros a vaincu le Minotaure ?",
            "answer": "thésée",
            "alternatives": ["thesee", "theseus"],
            "choices": ["Thésée", "Persée", "Héraclès", "Jason"]
        },
        {
            "question": "Combien de têtes avait l'Hydre de Lerne ?",
            "answer": "9",
            "alternatives": ["neuf"],
            "choices": ["9", "7", "5", "12"]
        },
        {
            "question": "Qui est la femme de Zeus ?",
            "answer": "héra",
            "alternatives": ["hera", "junon"],
            "choices": ["Héra", "Déméter", "Aphrodite", "Athéna"]
        }
    ],
    "hard": [
        {
            "question": "Quel titan porte le monde sur ses épaules ?",
            "answer": "atlas",
            "alternatives": [],
            "choices": ["Atlas", "Prométhée", "Cronos", "Hypérion"]
        },
        {
            "question": "Quel est le nom du fleuve de l'oubli dans les Enfers ?",
            "answer": "léthé",
            "alternatives": ["lethe", "le léthé"],
            "choices": ["Léthé", "Styx", "Achéron", "Phlégéthon"]
        },
        {
            "question": "Qui sont les Érinyes ?",
            "answer": "déesses de la vengeance",
            "alternatives": ["les furies", "furies", "déesses vengeance"],
            "choices": ["Déesses de la vengeance", "Déesses du destin", "Déesses de la mort", "Déesses de la nuit"]
        },
        {
            "question": "Quel héros a rapporté la Toison d'or ?",
            "answer": "jason",
            "alternatives": [],
            "choices": ["Jason", "Persée", "Héraclès", "Bellérophon"]
        },
        {
            "question": "Qui a tué le dragon Python ?",
            "answer": "apollon",
            "alternatives": ["apollo"],
            "choices": ["Apollon", "Zeus", "Arès", "Hermès"]
        },
        {
            "question": "Quel est le nom de l'épée de Persée ?",
            "answer": "harpé",
            "alternatives": ["harpe", "la harpé"],
            "choices": ["Harpé", "Excalibur", "Durandal", "Égide"]
        },
        {
            "question": "Qui sont les parents d'Hermès ?",
            "answer": "zeus et maïa",
            "alternatives": ["zeus et maia"],
            "choices": ["Zeus et Maïa", "Zeus et Héra", "Cronos et Rhéa", "Zeus et Léto"]
        },
        {
            "question": "Quel monstre Bellérophon a-t-il vaincu avec Pégase ?",
            "answer": "chimère",
            "alternatives": ["la chimère", "chimera"],
            "choices": ["Chimère", "Hydre", "Méduse", "Sphinx"]
        },
        {
            "question": "Comment s'appellent les trois Moires ?",
            "answer": "clotho, lachésis et atropos",
            "alternatives": ["clotho lachesis atropos"],
            "choices": ["Clotho, Lachésis, Atropos", "Méduse, Sthéno, Euryale", "Alecto, Mégère, Tisiphone", "Aglaé, Euphrosyne, Thalie"]
        },
        {
            "question": "Quel dieu a été élevé par des nymphes sur le mont Ida ?",
            "answer": "zeus",
            "alternatives": ["jupiter"],
            "choices": ["Zeus", "Dionysos", "Apollon", "Hermès"]
        }
    ]
}