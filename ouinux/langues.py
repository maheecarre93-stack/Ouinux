"""Traductions des textes produits par le moteur (l'anglais sert de clé et de langue par défaut).

Pour ajouter une langue : copier le dictionnaire FR, traduire les valeurs, l'ajouter à LANGUES.
Les {noms} entre accolades sont remplacés par les valeurs ; il faut les garder tels quels.
"""

FR = {
    # Jeux hors Steam connus
    "R5Reloaded (community version of Apex Legends season 3, not on Steam) doesn't use EA's "
    "anti-cheat: its Windows launcher runs on Linux through Proton/Wine. It requires the EA App "
    "running (a secondary account is recommended) with Apex Legends in the library.":
        "R5Reloaded (Apex Legends saison 3 en version communautaire, hors Steam) n'utilise pas "
        "l'anti-triche EA : son launcher Windows tourne sous Linux via Proton/Wine. Il exige l'EA App "
        "ouverte (compte secondaire conseillé) avec Apex Legends dans la bibliothèque.",
    "Minecraft Java Edition has a native Linux version (for example with Prism Launcher).":
        "Minecraft Java Edition a une version Linux native (par exemple avec Prism Launcher).",

    # Estimation des performances
    "Vulkan runs directly, without translation: almost identical.":
        "Vulkan tourne directement, sans traduction : quasi identique.",
    "DXVK translates DirectX 11 to Vulkan very efficiently on AMD cards.":
        "DXVK traduit DirectX 11 en Vulkan très efficacement sur carte AMD.",
    "AMD's OpenGL drivers on Windows are weak; Linux's (Mesa) are much better.":
        "Les pilotes OpenGL d'AMD sous Windows sont faibles, ceux de Linux (Mesa) bien meilleurs.",
    "VKD3D translates DirectX 12 to Vulkan with a small performance loss.":
        "VKD3D traduit DirectX 12 en Vulkan avec une petite perte de performances.",
    "DXVK translates DirectX 11 to Vulkan; slightly less efficient on Nvidia than on AMD.":
        "DXVK traduit DirectX 11 en Vulkan ; un peu moins efficace sur Nvidia que sur AMD.",
    "Nvidia uses the same OpenGL driver on Windows and Linux.":
        "Nvidia utilise le même pilote OpenGL sous Windows et Linux.",
    "VKD3D translates DirectX 12 to Vulkan: this is the weak spot of Nvidia cards on Linux.":
        "VKD3D traduit DirectX 12 en Vulkan : c'est le point faible des cartes Nvidia sous Linux.",
    "Vulkan runs directly, without translation.": "Vulkan tourne directement, sans traduction.",
    "DXVK translates DirectX 11 to Vulkan; Intel's drivers are younger, the gap varies between games.":
        "DXVK traduit DirectX 11 en Vulkan ; les pilotes Intel sont plus jeunes, l'écart varie selon les jeux.",
    "Linux's OpenGL driver (Mesa) is often better.": "Le pilote OpenGL de Linux (Mesa) est souvent meilleur.",
    "VKD3D translates DirectX 12 to Vulkan with a performance loss.":
        "VKD3D traduit DirectX 12 en Vulkan avec une perte de performances.",
    " (Graphics card brand not detected: estimate made for an AMD card.)":
        " (Marque de carte graphique non détectée : estimation faite pour une carte AMD.)",
    "Native Linux version. ": "Version Linux native. ",
    "On Linux, pick {api} in the game's settings rather than DirectX 12.":
        "Sous Linux, choisis {api} dans les options du jeu plutôt que DirectX 12.",
    "With ray tracing on, the gap grows (~10% more in favour of Windows).":
        "Avec le ray tracing activé, l'écart grandit (~10 % de plus pour Windows).",
    "Almost identical performance ({api}).": "Performances quasi identiques ({api}).",
    "Linux probably ~{n}% smoother ({api}).": "Linux probablement ~{n} % plus fluide ({api}).",
    "Windows probably ~{n}% smoother ({api}).": "Windows probablement ~{n} % plus fluide ({api}).",

    # Verdicts
    "Removed from the Steam store, available on Epic: on Linux, use Heroic Games Launcher.":
        "Retiré de la boutique Steam, disponible sur Epic : sous Linux, passe par Heroic Games Launcher.",
    "Third-party platforms blocked on Linux: {liste}. If you play through one of them, you'll need Windows.":
        "Plateformes tierces bloquées sous Linux : {liste}. Si tu joues via l'une d'elles, il faudra Windows.",
    "On Linux, install it with {outils} (launcher: {lanceurs}).":
        "Sous Linux, installe-le avec {outils} (launcher : {lanceurs}).",
    " or ": " ou ",
    "The anti-cheat ({ac}) deliberately blocks Linux: online play won't work on Linux.":
        "L'anti-triche ({ac}) refuse volontairement Linux : le jeu en ligne ne marchera pas sous Linux.",
    "The anti-cheat ({ac}) doesn't work on Linux: online play won't work on Linux.":
        "L'anti-triche ({ac}) ne fonctionne pas sous Linux : le jeu en ligne ne marchera pas sous Linux.",
    "The game has a native Linux version on Steam.": "Le jeu a une version Linux native sur Steam.",
    "ProtonDB: {tier}, the game runs very well through Proton.": "ProtonDB : {tier}, le jeu tourne très bien via Proton.",
    "ProtonDB: Silver, playable on Linux with possible minor issues.":
        "ProtonDB : Silver, jouable sous Linux avec de petits soucis possibles.",
    "ProtonDB: {tier}, but Valve rates it \"{deck}\" on Steam Deck: worth trying on Linux.":
        "ProtonDB : {tier}, mais Valve le classe « {deck} » sur Steam Deck : ça vaut le coup d'essayer sous Linux.",
    "ProtonDB: {tier}, too many problems on Linux.": "ProtonDB : {tier}, trop de problèmes sous Linux.",
    "Lutris offers a Linux install for this game (native version or community launcher) and the "
    "anti-cheat is compatible. A community launcher isn't official: check that the publisher "
    "tolerates it.":
        "Lutris propose une installation Linux pour ce jeu (version native ou launcher communautaire) et "
        "l'anti-triche est compatible. Un launcher communautaire n'est pas officiel : vérifie qu'il est "
        "toléré par l'éditeur.",
    "Lutris offers a Linux install for this game (native version or community launcher). A community "
    "launcher isn't official: check that the publisher tolerates it.":
        "Lutris propose une installation Linux pour ce jeu (version native ou launcher communautaire). "
        "Un launcher communautaire n'est pas officiel : vérifie qu'il est toléré par l'éditeur.",
    "Not on Steam, so no ProtonDB rating, but Lutris offers {n} Linux install script(s) and the "
    "anti-cheat is compatible.":
        "Pas sur Steam, donc pas de note ProtonDB, mais Lutris propose {n} script(s) d'installation pour "
        "Linux et l'anti-triche est compatible.",
    "Not on Steam, so no ProtonDB rating, but Lutris offers {n} Linux install script(s): worth testing.":
        "Pas sur Steam, donc pas de note ProtonDB, mais Lutris propose {n} script(s) d'installation pour Linux : à tester.",
    "No ProtonDB rating, but \"{deck}\" on Steam Deck.": "Pas de note ProtonDB, mais « {deck} » sur Steam Deck.",
    "The anti-cheat is Linux-compatible.": "L'anti-triche est compatible Linux.",
    "Game not found on Steam or in the anti-cheat database. If it's only on Epic or another "
    "launcher, there's no reliable data about it.":
        "Jeu introuvable sur Steam et dans la base anti-triche. S'il n'existe que sur Epic ou un autre "
        "launcher, il n'y a pas de données fiables dessus.",
    "No reliable data: worth testing on Linux, keep Windows as a fallback.":
        "Aucune donnée fiable : à tester sous Linux, garde Windows en solution de secours.",
    "I can't find \"{nom}\" on Steam (it may have been removed). The closest result is \"{proche}\".":
        "Je ne trouve pas « {nom} » sur Steam (il a peut-être été retiré). Le résultat le plus proche est « {proche} ».",
    "playable": "jouable", "verified": "vérifié", "unsupported": "non supporté", "unknown": "inconnu",

    # Comparaison avec le PC
    "Well below minimum": "Bien sous le minimum", "May be unplayable or very choppy.": "Risque d'être injouable ou très saccadé.",
    "Slightly below minimum": "Un peu sous le minimum",
    "Playable on low settings, with possible frame drops.": "Jouable en réglages bas, avec des baisses de fluidité possibles.",
    "Right at minimum": "Juste au minimum", "Playable on low settings, 1080p or lower.": "Jouable en réglages bas, 1080p ou moins.",
    "Between minimum and recommended": "Entre minimum et recommandé", "Low to medium settings at 1080p.": "Réglages bas à moyens en 1080p.",
    "Recommended reached": "Recommandé atteint", "Usually high settings at 1080p.": "Réglages élevés en 1080p en général.",
    "Above recommended": "Au-dessus du recommandé",
    "Very comfortable at 1080p, maybe 1440p.": "Très à l'aise en 1080p, peut-être 1440p.",
    "Graphics card": "Carte graphique", "Processor": "Processeur", "RAM": "RAM", "Video memory": "Mémoire vidéo",
    "{pct}% of recommended": "{pct} % du recommandé", "{pct}% of minimum": "{pct} % du minimum",
    "{a} GB / {b} GB recommended": "{a} Go / {b} Go recommandés", "{a} GB / {b} GB minimum": "{a} Go / {b} Go minimum",
    "{a} GB / {b} GB required": "{a} Go / {b} Go demandés",
    "processor": "processeur", "graphics card": "carte graphique",
    "Same level on both systems: the processor is the limit, and Linux doesn't change that.":
        "Même niveau sur les deux systèmes : c'est le processeur qui limite, et Linux n'y change rien.",
    "Same level on both systems for this game.": "Même niveau sur les deux systèmes pour ce jeu.",
    "Not on Steam": "Hors Steam",
}

LANGUES = {"fr": FR}


def T(lang, texte, **valeurs):
    """Traduit une phrase anglaise (si une traduction existe) puis remplace les {valeurs}."""
    texte = LANGUES.get(lang, {}).get(texte, texte)
    return texte.format(**valeurs) if valeurs else texte
