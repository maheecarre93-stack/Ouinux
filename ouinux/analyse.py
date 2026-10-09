"""Analyse d'un jeu : fonctionne-t-il sous Linux, ou faut-il rester sur Windows ?

Le verdict est calculé par des règles (AreWeAntiCheatYet + Steam + ProtonDB), jamais par une IA :
ainsi il est reproductible et ne peut pas « inventer ».
"""
import json
import os
import platform
import re
import ssl
import time
import unicodedata
import urllib.parse
import urllib.request

from . import materiel
from .langues import T

VERSION = "0.1.0"


def dossier_cache():
    if platform.system() == "Windows":
        base = os.environ.get("LOCALAPPDATA") or os.path.expanduser("~")
        d = os.path.join(base, "Ouinux", "cache")
    elif platform.system() == "Darwin":
        d = os.path.expanduser("~/Library/Caches/ouinux")
    else:
        d = os.path.join(os.environ.get("XDG_CACHE_HOME") or os.path.expanduser("~/.cache"), "ouinux")
    os.makedirs(d, exist_ok=True)
    return d


CACHE = dossier_cache()
TIERS = {"borked": 0, "bronze": 1, "silver": 2, "gold": 3, "platinum": 4, "native": 5}
DECK = {0: "unknown", 1: "unsupported", 2: "playable", 3: "verified"}


# ---------- Accès réseau ----------

_http = {}
try:  # certificats embarqués : l'exécutable ne dépend pas de leur emplacement, qui varie selon la distribution
    import certifi
    SSL = ssl.create_default_context(cafile=certifi.where())
except ImportError:
    SSL = ssl.create_default_context()


def get_json(url, timeout=15, ttl=900):
    """Requête JSON avec un cache mémoire de 15 min (moins de requêtes vers les sites, réaffichage instantané)."""
    if url in _http and time.time() - _http[url][0] < ttl:
        return _http[url][1]
    req = urllib.request.Request(url, headers={"User-Agent": f"ouinux/{VERSION}"})
    with urllib.request.urlopen(req, timeout=timeout, context=SSL) as r:
        d = json.loads(r.read().decode())
    _http[url] = (time.time(), d)
    return d


def cache_json(nom, defaut):
    try:
        with open(os.path.join(CACHE, nom), encoding="utf-8") as f:
            return json.load(f)
    except (OSError, json.JSONDecodeError):
        return defaut


def sauver_json(nom, data):
    chemin = os.path.join(CACHE, nom)
    with open(chemin + ".tmp", "w", encoding="utf-8") as f:
        json.dump(data, f)
    os.replace(chemin + ".tmp", chemin)


def base_anticheat():
    chemin = os.path.join(CACHE, "anticheat.json")
    if not os.path.exists(chemin) or time.time() - os.path.getmtime(chemin) > 86400:
        try:
            sauver_json("anticheat.json", get_json(
                "https://raw.githubusercontent.com/AreWeAntiCheatYet/AreWeAntiCheatYet/master/games.json", 30))
        except Exception:
            pass  # hors ligne : on garde l'ancienne copie s'il y en a une
    return cache_json("anticheat.json", [])


# ---------- Noms de jeux ----------

def normaliser(s):
    s = unicodedata.normalize("NFKD", re.sub("[™®©'’]", "", s)).encode("ascii", "ignore").decode().lower()
    return re.sub(r"[^a-z0-9]+", " ", s).strip()


EDITIONS = (r"\b(ultimate|definitive|deluxe|complete|enhanced|remastered|goty|game of the year|digital|standard|gold|"
            r"special|anniversary|legacy|version amelioree|edition|online|directors? cut)\b")


def sans_edition(nom):
    return re.sub(r"\s+", " ", re.sub(EDITIONS, " ", normaliser(nom))).strip()


def meme_jeu(nom_trouve, nom_demande):
    """« The Elder Scrolls V: Skyrim Special Edition » = « Skyrim », mais « Minecraft Dungeons » ≠ « Minecraft »."""
    cible = sans_edition(nom_demande)
    parties = re.split(r"\s*[:—–]\s*|\s+-\s+", nom_trouve) + [nom_trouve]
    return any(sans_edition(p) == cible for p in parties)


# Jeux absents de Steam qu'on sait quand même juger
R5 = ("R5Reloaded", "Linux",
      "R5Reloaded (community version of Apex Legends season 3, not on Steam) doesn't use EA's "
      "anti-cheat: its Windows launcher runs on Linux through Proton/Wine. It requires the EA App "
      "running (a secondary account is recommended) with Apex Legends in the library.", "moyenne")
MC = ("Minecraft", "Linux", "Minecraft Java Edition has a native Linux version (for example with Prism Launcher).", "haute")
HORS_STEAM = {"minecraft": MC, "minecraft java edition": MC, "r5 reloaded": R5, "r5reloaded": R5}

# Configurations officielles (sites des éditeurs) des gros jeux absents de Steam, au format des fiches Steam
CONFIGS_HORS_STEAM = {
    "valorant": {"minimum": "Processor: Intel Core 2 Duo E8400 / AMD Athlon 200GE Graphics: Intel HD 4000 / Radeon R5 200 Memory: 4 GB RAM",
                 "recommended": "Processor: Intel i5-9400F / AMD Ryzen 5 2600X Graphics: GeForce GTX 1050 Ti / Radeon RX 570 Memory: 4 GB RAM"},
    "league of legends": {"minimum": "Processor: Intel Core i3-530 / AMD A6-3650 Graphics: GeForce 9600 GT / Radeon HD 6570 Memory: 4 GB RAM",
                          "recommended": "Processor: Intel Core i5-3300 / AMD Ryzen 3 1200 Graphics: GeForce GTX 560 / Radeon HD 6950 Memory: 4 GB RAM"},
    "fortnite": {"minimum": "Processor: Intel Core i3-3225 Graphics: Intel HD 4000 / Radeon Vega 8 Memory: 8 GB RAM",
                 "recommended": "Processor: Intel Core i5-7300U / AMD Ryzen 3 3300U Graphics: GeForce GTX 960 / Radeon R9 280 Memory: 8 GB RAM"},
}


# ---------- Autres launchers (via l'API publique de Lutris) ----------
LANCEURS = [  # (motif dans le nom du script Lutris, nom affiché, outil conseillé sous Linux)
    (r"battle\.?net|blizzard", "Battle.net", "Lutris"),
    (r"ubisoft|uplay", "Ubisoft Connect", "Lutris"),
    (r"\bea app|origin", "EA App", "Lutris"),
    (r"epic", "Epic Games Store", "Heroic Games Launcher"),
    (r"\bgog", "GOG", "Heroic Games Launcher"),
    (r"amazon|prime gaming", "Amazon Games", "Heroic Games Launcher"),
    (r"rockstar", "Rockstar Games Launcher", "Lutris"),
]
_memo = {}


def lutris(chemin, params=None, ttl=3600):
    """Appel à l'API Lutris avec un petit cache mémoire (pour ne pas la marteler pendant la frappe)."""
    url = "https://lutris.net/api/" + chemin + ("?" + urllib.parse.urlencode(params) if params else "")
    if url in _memo and time.time() - _memo[url][0] < ttl:
        return _memo[url][1]
    d = get_json(url, 8)
    _memo[url] = (time.time(), d)
    return d


def ressemblance(nom, texte):
    """0 = identique, plus grand = moins proche (pour trier la recherche Lutris, peu pertinente seule)."""
    n, t = normaliser(nom), normaliser(texte)
    return (n != t, not n.startswith(t), t not in n, len(n))


def jeux_lutris(texte):
    try:
        res = lutris("games", {"search": texte}).get("results", [])
    except Exception:
        return []
    pc = [g for g in res if any(p["name"] in ("Windows", "Linux") for p in g.get("platforms") or [])]
    return sorted(pc, key=lambda g: ressemblance(g["name"], texte))


def infos_lutris(slug=None, nom=None, appid=None):
    """Fiche Lutris : ID Steam/GOG, scripts d'installation (launcher, version Linux)."""
    try:
        if slug:
            g = lutris(f"games/{slug}")
        else:
            res = lutris("games", {"search": nom}).get("results", [])
            g = next((x for x in res if appid and any(p["service"] == "steam" and p["slug"] == str(appid)
                                                     for p in x.get("provider_games") or [])), None) \
                or next((x for x in res if normaliser(x["name"]) == normaliser(nom)), None)
        if not g:
            return None
        inst = lutris(f"installers/{g['slug']}", ttl=86400)
        inst = inst.get("results", []) if isinstance(inst, dict) else inst
    except Exception:
        return None
    services = {p["service"]: p["slug"] for p in g.get("provider_games") or []}
    lanceurs = []
    for i in inst:
        for motif, nom_l, outil in LANCEURS:
            if re.search(motif, i.get("version") or "", re.I) and nom_l not in [l[0] for l in lanceurs]:
                lanceurs.append((nom_l, outil))
    if "gog" in services and "GOG" not in [l[0] for l in lanceurs]:
        lanceurs.append(("GOG", "Heroic Games Launcher"))
    return {"nom": g["name"], "slug": g["slug"], "steam": services.get("steam"), "lanceurs": lanceurs,
            "scripts": len(inst), "linux": any(i.get("runner") == "linux" for i in inst),
            "wine": any(i.get("runner") == "wine" for i in inst),
            "lien": f"https://lutris.net/games/{g['slug']}/"}


BRUIT = re.compile(r"soundtrack|bande originale|season pass|artbook|\bost\b|\bdlc\b|\bpack\b|demo\b|\bbundle\b", re.I)


def suggestions(texte, lang="en"):
    """Propositions pendant la frappe : jeux hors Steam connus + recherche Steam."""
    n = normaliser(texte)
    if len(n) < 2:
        return []
    res = [{"nom": v[0], "appid": None, "image": None} for k, v in HORS_STEAM.items()
           if k.startswith(n) or n in k]
    res = list({r["nom"]: r for r in res}.values())
    try:
        d = get_json("https://store.steampowered.com/api/storesearch/?"
                     + urllib.parse.urlencode({"term": texte, "l": "french" if lang == "fr" else "english",
                                              "cc": "FR" if lang == "fr" else "US"}), 8)
        res += [{"nom": i["name"], "appid": i["id"], "image": i.get("tiny_image"), "source": "Steam"}
                for i in d.get("items", []) if i.get("type") == "app" and not BRUIT.search(i["name"])][:6]
    except Exception:
        pass
    # Jeux hors Steam (Battle.net, Epic, Ubisoft…) connus de Lutris
    deja = {str(r["appid"]) for r in res if r["appid"]} | {sans_edition(r["nom"]) for r in res}
    ajoutes = 0
    for g in jeux_lutris(texte):
        steam = next((p["slug"] for p in g.get("provider_games") or [] if p["service"] == "steam"), None)
        base = re.split(r"\s*:\s*", g["name"])[0]
        # même jeu qu'un résultat déjà listé (autre édition), ou sous-entrée « Jeu: Saison 2 » / serveur privé
        if steam in deja or sans_edition(g["name"]) in deja or (":" in g["name"] and sans_edition(base) in deja) \
                or BRUIT.search(g["name"]):
            continue
        deja.add(sans_edition(g["name"]))
        ajoutes += 1
        if ajoutes > 4:
            break
        res.append({"nom": g["name"], "appid": None, "slug": g["slug"], "image": g.get("banner_url"), "source": T(lang, "Not on Steam")})
    return res[:9]


def recherche_steam(nom):
    d = get_json("https://store.steampowered.com/api/storesearch/?"
                 + urllib.parse.urlencode({"term": nom, "l": "french", "cc": "FR"}))
    items = [i for i in d.get("items", []) if i.get("type") == "app"]
    if not items:
        return None
    n = normaliser(nom)
    for i in items:
        if normaliser(i["name"]) == n:
            return i
    for i in items:  # même jeu, simple édition (ex. « Control Ultimate Edition »)
        if sans_edition(i["name"]) == n:
            return i
    return items[0]


def chercher_anticheat(nom, appid):
    principal, variantes = None, []
    n = normaliser(nom)
    for g in base_anticheat():
        steam = (g.get("storeIds") or {}).get("steam")
        gn = normaliser(g["name"])
        if (appid and steam == str(appid)) or gn == n or ("(" not in g["name"] and sans_edition(gn) == sans_edition(n)):
            principal = principal or g
        elif gn.startswith(n + " ") and "(" in g["name"]:
            variantes.append(g)  # ex. « Counter-Strike 2 (FACEIT) »
    return principal, variantes


def infos_steam(appid):
    res = {"linux_natif": False, "deck": 0, "config": {}, "image": None}
    try:
        d = get_json(f"https://store.steampowered.com/api/appdetails?appids={appid}&l=english")[str(appid)]["data"]
        res["linux_natif"] = bool(d["platforms"].get("linux"))
        res["image"] = d.get("header_image")
        if isinstance(d.get("pc_requirements"), dict):
            res["config"] = d["pc_requirements"]
    except Exception:
        pass
    try:
        d = get_json(f"https://store.steampowered.com/saleaction/ajaxgetdeckappcompatibilityreport?nAppID={appid}")
        res["deck"] = d["results"]["resolved_category"]
    except Exception:
        pass
    return res


def protondb(appid):
    try:
        return get_json(f"https://www.protondb.com/api/v1/reports/summaries/{appid}.json")
    except Exception:
        return None


# ---------- Estimation des performances (PCGamingWiki) ----------
# Écart estimé Linux vs Windows selon la marque de carte graphique, en % : positif = Linux plus fluide.
# (clé, nom, centre, bas, haut, explication). Ordre = préférence sous Linux quand le jeu propose plusieurs API.
PROFILS = {
    "amd": [
        ("vulkan", "Vulkan", 0, -5, 5, "Vulkan runs directly, without translation: almost identical."),
        ("dx11", "DirectX 9/10/11", 0, -7, 7, "DXVK translates DirectX 11 to Vulkan very efficiently on AMD cards."),
        ("opengl", "OpenGL", 10, 0, 20, "AMD's OpenGL drivers on Windows are weak; Linux's (Mesa) are much better."),
        ("dx12", "DirectX 12", -10, -18, -3, "VKD3D translates DirectX 12 to Vulkan with a small performance loss."),
    ],
    "nvidia": [
        ("vulkan", "Vulkan", 0, -5, 5, "Vulkan runs directly, without translation: almost identical."),
        ("dx11", "DirectX 9/10/11", -5, -12, 2, "DXVK translates DirectX 11 to Vulkan; slightly less efficient on Nvidia than on AMD."),
        ("opengl", "OpenGL", 0, -5, 5, "Nvidia uses the same OpenGL driver on Windows and Linux."),
        ("dx12", "DirectX 12", -18, -28, -8, "VKD3D translates DirectX 12 to Vulkan: this is the weak spot of Nvidia cards on Linux."),
    ],
    "intel": [
        ("vulkan", "Vulkan", 0, -8, 8, "Vulkan runs directly, without translation."),
        ("dx11", "DirectX 9/10/11", 0, -10, 10, "DXVK translates DirectX 11 to Vulkan; Intel's drivers are younger, the gap varies between games."),
        ("opengl", "OpenGL", 5, -5, 15, "Linux's OpenGL driver (Mesa) is often better."),
        ("dx12", "DirectX 12", -12, -22, -2, "VKD3D translates DirectX 12 to Vulkan with a performance loss."),
    ],
}


def pcgw(params):
    return get_json("https://www.pcgamingwiki.com/w/api.php?" + urllib.parse.urlencode(params), 15)


def apis_pcgw(nom, appid):
    """Technologies graphiques du jeu d'après PCGamingWiki (avec cache disque)."""
    cache = cache_json("pcgw.json", {})
    if str(appid) in cache:
        return cache[str(appid)]
    res = None
    try:
        propre = re.sub("[™®©]", "", nom).strip()
        simple = re.sub(r"\s*(:.*|online|edition|remastered|goty)$", "", propre, flags=re.I).strip()
        titres = []
        for q in dict.fromkeys([propre, simple]):
            titres += pcgw({"action": "opensearch", "search": q, "limit": 10, "namespace": 0, "format": "json"})[1]
        n = normaliser(propre)
        titres = sorted(dict.fromkeys(titres), key=lambda t: (normaliser(t) != n,
                        not normaliser(t).startswith(normaliser(simple)), len(t)))
        pages = [(t, pcgw({"action": "parse", "page": t, "prop": "wikitext", "format": "json",
                           "redirects": 1}).get("parse", {}).get("wikitext", {}).get("*", "")) for t in titres[:6]]
        # priorité à la fiche qui cite le bon ID Steam, sinon celle au titre identique
        bonnes = [p for p in pages if re.search(r"\|steam appid\s*=[^\n]*\b%s\b" % appid, p[1])]
        bonnes += [p for p in pages if p[1] and normaliser(p[0]) in (n, normaliser(simple))]
        for t, w in bonnes[:1]:
            def champ(k):
                return (re.search(r"\|" + k + r"\s*=\s*([^\n|]*)", w) or [None, ""])[1].strip().lower()
            d3d = champ("direct3d versions")
            res = {"page": t,
                   "vulkan": champ("vulkan versions") not in ("", "false"),
                   "dx12": "12" in d3d,
                   "dx11": bool(re.search(r"\b(9|10|11)\b", d3d)),
                   "opengl": champ("opengl versions") not in ("", "false"),
                   "rt": champ("ray tracing") == "true"}
    except Exception:
        return None  # réseau : on ne met pas en cache, on réessaiera
    cache[str(appid)] = res
    sauver_json("pcgw.json", cache)
    return res


def perf_estimee(r, natif, marque, lang="en"):
    if not r["appid"]:
        return None
    apis = apis_pcgw(r["jeu"], r["appid"])
    if not apis:
        return None
    profils = PROFILS.get(marque, PROFILS["amd"])
    dispo = [p for p in profils if apis.get(p[0])]
    if not dispo:
        return None
    cle, nom_api, centre, bas, haut, pourquoi = dispo[0]
    p = {"api": nom_api, "centre": centre, "bas": bas, "haut": haut, "explication": T(lang, pourquoi),
         "source": f"https://www.pcgamingwiki.com/wiki/{urllib.parse.quote(apis['page'].replace(' ', '_'))}"}
    if marque == "inconnue":
        p["explication"] += T(lang, " (Graphics card brand not detected: estimate made for an AMD card.)")
    if natif:
        p["explication"] = T(lang, "Native Linux version. ") + p["explication"]
    if len(dispo) > 1 and cle != "dx12" and apis.get("dx12"):
        p["conseil"] = T(lang, "On Linux, pick {api} in the game's settings rather than DirectX 12.", api=nom_api)
    if apis.get("rt"):
        p["rt"] = T(lang, "With ray tracing on, the gap grows (~10% more in favour of Windows).")
    if abs(centre) <= 5:
        p["resume"] = T(lang, "Almost identical performance ({api}).", api=nom_api)
    elif centre > 0:
        p["resume"] = T(lang, "Linux probably ~{n}% smoother ({api}).", n=centre, api=nom_api)
    else:
        p["resume"] = T(lang, "Windows probably ~{n}% smoother ({api}).", n=-centre, api=nom_api)
    return p


# ---------- Règles de décision ----------

def verdict_jeu(nom, appid=None, slug=None, lang="en"):
    """Verdict structuré pour un jeu. Si appid/slug est fourni (choisi dans les suggestions), pas de recherche."""
    lu = infos_lutris(slug=slug) if slug else None
    if lu and lu["steam"] and not appid:
        appid = int(lu["steam"])  # jeu Lutris qui existe aussi sur Steam : on profite de ProtonDB
    if normaliser(nom) in HORS_STEAM:
        jeu, verdict, raison, conf = HORS_STEAM[normaliser(nom)]
        return {"demande": nom, "jeu": jeu, "appid": None, "verdict": verdict, "confiance": conf,
                "raisons": [T(lang, raison)], "liens": [], "steam_deck": "unknown"}
    r = {"demande": nom, "jeu": nom, "appid": None, "verdict": None, "confiance": None, "raisons": [], "liens": []}
    app = {"name": nom, "id": appid} if appid else None
    if not app and not lu:
        try:
            app = recherche_steam(nom)
        except Exception:
            app = None
        if app and normaliser(app["name"]) != normaliser(nom):
            # Steam n'a pas trouvé le titre exact : si la base anti-triche le connaît, elle a priorité
            if any(normaliser(g["name"]) == normaliser(nom) for g in base_anticheat()):
                app = None
        if app and not meme_jeu(app["name"], nom):
            r["approx"] = app["name"]  # « Evolve » → ARK: Survival Evolved : ce n'est pas le même jeu
    if lu:
        r["jeu"] = lu["nom"]
    if app:
        r["jeu"], r["appid"] = (app["name"] if not lu else lu["nom"]), int(app["id"])
        r["liens"].append(f"https://www.protondb.com/app/{app['id']}")

    ac, variantes = chercher_anticheat(r["jeu"], r["appid"])
    if not ac and r["jeu"] != nom:
        ac, variantes = chercher_anticheat(nom, None)
    if ac and not r["appid"] and (ac.get("storeIds") or {}).get("steam"):
        # Jeu retiré de la boutique Steam (ex. Rocket League) : l'ID vient de la base anti-triche
        r["appid"] = int(ac["storeIds"]["steam"])
        r["liens"].append(f"https://www.protondb.com/app/{r['appid']}")
        if (ac.get("storeIds") or {}).get("epic"):
            r["raisons"].append(T(lang, "Removed from the Steam store, available on Epic: on Linux, use Heroic Games Launcher."))
    if ac:
        r["jeu"] = r["jeu"] if app else ac["name"]
        r["anticheat"] = {"statut": ac["status"], "systemes": ac.get("anticheats", []),
                          "notes": [n[0] for n in ac.get("notes", [])][:3]}
    bloquees = [v["name"] for v in variantes if v["status"] in ("Denied", "Broken")]
    if bloquees:
        r["raisons"].append(T(lang, "Third-party platforms blocked on Linux: {liste}. If you play through one of them, you'll need "
                                    "Windows.", liste=", ".join(bloquees[:5])))

    steam = infos_steam(r["appid"]) if r["appid"] else {"linux_natif": False, "deck": 0, "config": {}, "image": None}
    if not steam["config"]:
        steam["config"] = CONFIGS_HORS_STEAM.get(normaliser(r["jeu"]), {})
    r["_natif"], r["_config"], r["image"] = steam["linux_natif"], steam["config"], steam["image"]
    pdb = protondb(r["appid"]) if r["appid"] else None
    r["steam_deck"] = DECK.get(steam["deck"], "unknown")
    if pdb:
        r["protondb"] = {k: pdb.get(k) for k in ("tier", "trendingTier", "bestReportedTier", "confidence", "total")}

    if not lu and app:
        lu = infos_lutris(nom=r["jeu"], appid=r["appid"])
    plateformes = (["Steam"] if r["appid"] else []) + ([l for l, _ in lu["lanceurs"]] if lu else [])
    if ac and (ac.get("storeIds") or {}).get("epic") and "Epic Games Store" not in plateformes:
        plateformes.append("Epic Games Store")
    r["plateformes"] = list(dict.fromkeys(plateformes))
    if lu:
        r["liens"].append(lu["lien"])

    def fin(verdict, confiance, raison):
        r["verdict"], r["confiance"] = verdict, confiance
        r["raisons"].insert(0, raison)
        if verdict == "Linux" and lu and lu["lanceurs"] and not r["appid"]:
            outils = list(dict.fromkeys(o for _, o in lu["lanceurs"]))
            r["raisons"].append(T(lang, "On Linux, install it with {outils} (launcher: {lanceurs}).",
                                  outils=T(lang, " or ").join(outils), lanceurs=", ".join(l for l, _ in lu["lanceurs"])))
        return r

    # 1. L'anti-triche passe avant tout
    if ac and ac["status"] in ("Denied", "Broken"):
        modele = ("The anti-cheat ({ac}) deliberately blocks Linux: online play won't work on Linux."
                  if ac["status"] == "Denied" else
                  "The anti-cheat ({ac}) doesn't work on Linux: online play won't work on Linux.")
        return fin("Windows", "haute", T(lang, modele, ac=", ".join(ac.get("anticheats", [])) or "?"))
    # 2. Version Linux native
    if steam["linux_natif"]:
        return fin("Linux", "haute", T(lang, "The game has a native Linux version on Steam."))
    # 3. Notes ProtonDB (la meilleure entre note globale et tendance récente)
    if pdb and pdb.get("tier") in TIERS:
        t = max(TIERS.get(pdb.get("tier"), 0), TIERS.get(pdb.get("trendingTier"), 0))
        nom_t = [k for k, v in TIERS.items() if v == t][0].capitalize()
        peu = pdb.get("total", 0) < 10 or pdb.get("confidence") in ("low", "inadequate")
        if t >= 3:
            return fin("Linux", "moyenne" if peu else "haute", T(lang, "ProtonDB: {tier}, the game runs very well through Proton.", tier=nom_t))
        if t == 2:
            return fin("Linux", "moyenne", T(lang, "ProtonDB: Silver, playable on Linux with possible minor issues."))
        if steam["deck"] >= 2:
            return fin("Linux", "moyenne", T(lang, "ProtonDB: {tier}, but Valve rates it \"{deck}\" on Steam Deck: worth trying on Linux.", tier=nom_t, deck=T(lang, r["steam_deck"])))
        return fin("Windows", "moyenne" if peu else "haute", T(lang, "ProtonDB: {tier}, too many problems on Linux.", tier=nom_t))
    # 4. Jeu hors Steam : scripts d'installation Lutris
    if lu and not r["appid"]:
        compatible = ac and ac["status"] in ("Supported", "Running")
        if lu["linux"]:
            return fin("Linux", "moyenne", T(lang,
                       "Lutris offers a Linux install for this game (native version or community launcher) and the "
                       "anti-cheat is compatible. A community launcher isn't official: check that the publisher "
                       "tolerates it." if compatible else
                       "Lutris offers a Linux install for this game (native version or community launcher). A community "
                       "launcher isn't official: check that the publisher tolerates it."))
        if lu["wine"]:
            return fin("Linux", "moyenne" if compatible else "basse",
                       T(lang, "Not on Steam, so no ProtonDB rating, but Lutris offers {n} Linux install script(s) and the "
                               "anti-cheat is compatible." if compatible else
                               "Not on Steam, so no ProtonDB rating, but Lutris offers {n} Linux install script(s): worth "
                               "testing.", n=lu["scripts"]))
    # 5. Pas de note ProtonDB
    if steam["deck"] in (2, 3):
        return fin("Linux", "moyenne", T(lang, "No ProtonDB rating, but \"{deck}\" on Steam Deck.", deck=T(lang, r["steam_deck"])))
    if ac and ac["status"] in ("Supported", "Running"):
        return fin("Linux", "moyenne", T(lang, "The anti-cheat is Linux-compatible."))
    if not app and not ac and not lu:
        return fin("Inconnu", "basse", T(lang, "Game not found on Steam or in the anti-cheat database. If it's only on Epic or another "
                                               "launcher, there's no reliable data about it."))
    return fin("Linux", "basse", T(lang, "No reliable data: worth testing on Linux, keep Windows as a fallback."))


def analyser(pc, nom, appid=None, slug=None, lang="en"):
    """Verdict + estimation des performances + comparaison avec le PC, dans la langue demandée."""
    r = verdict_jeu(nom, appid, slug, lang)
    config = r.pop("_config", {})
    natif = r.pop("_natif", False)
    if r.get("approx"):
        # Steam a renvoyé un AUTRE jeu : on ne montre pas ses infos, on propose de le choisir
        return {"demande": nom, "jeu": nom, "appid": None, "verdict": "Inconnu", "confiance": "basse",
                "suggestion": r["approx"], "liens": [], "steam_deck": "unknown", "perf": None, "materiel": None,
                "raisons": [T(lang, "I can't find \"{nom}\" on Steam (it may have been removed). The closest result is \"{proche}\".", nom=nom, proche=r["approx"])]}
    try:
        r["perf"] = perf_estimee(r, natif, pc["marque_gpu"], lang)
    except Exception:
        r["perf"] = None
    try:
        bloque = r.get("anticheat", {}).get("statut") in ("Denied", "Broken")
        r["materiel"] = materiel.comparer(pc, config.get("minimum"), config.get("recommended"),
                                          (r["perf"] or {}).get("centre", 0), natif, bloque, lang) if config else None
    except Exception:
        r["materiel"] = None
    return r
