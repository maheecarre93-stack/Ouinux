"""Détecte le matériel du PC (Windows, Linux ou macOS) et le compare à la configuration demandée par un jeu (Steam).

Les scores sont des performances relatives approximatives en jeu (1080p) :
GPU : Radeon RX 6600 = 100.  CPU : Ryzen 5 2600X = 100.
C'est un ordre de grandeur, pas un benchmark.
"""
import glob
import json
import platform
import re
import shutil
import subprocess

from .langues import T

GPU = {
    # NVIDIA
    "gtx 750 ti": 20, "gtx 950": 27, "gtx 960": 32, "gtx 970": 48, "gtx 980 ti": 72, "gtx 980": 58,
    "gtx 1050 ti": 33, "gtx 1050": 26, "gtx 1060 3gb": 50, "gtx 1060": 55, "gtx 1070 ti": 77, "gtx 1070": 68,
    "gtx 1080 ti": 110, "gtx 1080": 82, "gtx 1650 super": 55, "gtx 1650": 40, "gtx 1660 super": 65,
    "gtx 1660 ti": 66, "gtx 1660": 58, "gtx 680": 30, "gtx 780": 40, "gtx 670": 27, "gtx 660": 22,
    "rtx 2060 super": 92, "rtx 2060": 82, "rtx 2070 super": 108, "rtx 2070": 97, "rtx 2080 super": 120,
    "rtx 2080 ti": 140, "rtx 2080": 115, "rtx 3050": 68, "rtx 3060 ti": 125, "rtx 3060": 97,
    "rtx 3070 ti": 150, "rtx 3070": 140, "rtx 3080 ti": 185, "rtx 3080": 170, "rtx 3090": 190,
    "rtx 4060 ti": 135, "rtx 4060": 112, "rtx 4070 ti super": 225, "rtx 4070 ti": 210,
    "rtx 4070 super": 195, "rtx 4070": 170, "rtx 4080": 255, "rtx 4090": 310,
    "rtx 5060 ti": 150, "rtx 5060": 130, "rtx 5070 ti": 255, "rtx 5070": 205, "rtx 5080": 285, "rtx 5090": 390,
    # AMD
    "hd 7850": 22, "hd 7870": 26, "hd 7950": 33, "hd 7970": 38, "r9 270x": 29, "r9 270": 27, "r9 280x": 40,
    "r9 280": 35, "r9 290x": 50, "r9 290": 46, "r9 380x": 42, "r9 380": 38, "r9 390x": 58, "r9 390": 55,
    "r9 fury": 62, "rx 460": 20, "rx 470": 46, "rx 480": 51, "rx 550": 14, "rx 560": 24, "rx 570": 49,
    "rx 580": 54, "rx 590": 60, "vega 56": 75, "vega 64": 82, "rx 5500 xt": 55, "rx 5600 xt": 85,
    "rx 5700 xt": 110, "rx 5700": 95, "rx 6400": 33, "rx 6500 xt": 42, "rx 6600 xt": 112, "rx 6650 xt": 118,
    "rx 6600": 100, "rx 6700 xt": 135, "rx 6750 xt": 142, "rx 6700": 125, "rx 6800 xt": 190, "rx 6800": 165,
    "rx 6900 xt": 205, "rx 6950 xt": 215, "rx 7600 xt": 122, "rx 7600": 118, "rx 7700 xt": 165,
    "rx 7800 xt": 195, "rx 7900 gre": 215, "rx 7900 xtx": 290, "rx 7900 xt": 250,
    "rx 9060 xt": 150, "rx 9070 xt": 255, "rx 9070": 225,
    # Apple (puces M : très approximatif, les jeux Windows y passent par une couche de traduction)
    "apple m1 max": 85, "apple m1 pro": 50, "apple m1": 28, "apple m2 max": 105, "apple m2 pro": 62, "apple m2": 36,
    "apple m3 max": 140, "apple m3 pro": 70, "apple m3": 45, "apple m4 max": 165, "apple m4 pro": 90, "apple m4": 55,
    "radeon pro 5300m": 45, "radeon pro 5500m": 52, "radeon pro 5600m": 70, "radeon pro 560x": 25,
    # Intel
    "arc a380": 35, "arc a580": 85, "arc a750": 95, "arc a770": 105, "arc b570": 110, "arc b580": 125,
    # Graphismes intégrés (portables, mini PC, consoles portables)
    "uhd graphics": 8, "iris xe": 15, "vega 8": 18, "vega 7": 16, "680m": 40, "760m": 38, "780m": 45,
    "890m": 55, "van gogh": 25, "hd 4000": 6, "hd 4600": 9, "hd 6570": 8, "hd 6950": 22, "gtx 560": 15,
    "9600 gt": 5, "r5 200": 6, "r7 370": 30, "vangogh": 25, "custom gpu 0405": 25, "custom gpu 0932": 27,
}

CPU = {
    # Intel
    "core 2 quad": 18, "i5 750": 30, "i5-750": 30, "i5 760": 31, "i5-760": 31, "i7 860": 36, "i7-860": 36,
    "i7 920": 35, "i7-920": 35, "i7 930": 36, "i7-930": 36, "i7 950": 37, "i7-950": 37, "i3-2100": 30, "i5-2500": 45, "i7-2600": 48, "i3-3220": 35, "i5-3470": 50,
    "i5-3570": 52, "i7-3770": 57, "i3-4130": 42, "i3-4160": 43, "i5-4460": 55, "i5-4590": 58, "i5-4670": 60,
    "i5-4690": 62, "i7-4770": 70, "i7-4790": 75, "i3-6100": 55, "i5-6400": 60, "i5-6500": 63, "i5-6600": 67,
    "i7-6700": 80, "i5-7400": 66, "i5-7500": 70, "i7-7700": 87, "i3-8100": 72, "i5-8400": 90, "i5-8600": 98,
    "i7-8700": 107, "i3-9100": 75, "i5-9400": 92, "i5-9600": 102, "i7-9700": 115, "i9-9900": 120,
    "i3-10100": 80, "i5-10400": 100, "i5-10600": 112, "i7-10700": 122, "i9-10900": 128, "i5-11400": 110,
    "i5-11600": 120, "i7-11700": 128, "i3-12100": 115, "i5-12400": 130, "i5-12600": 145, "i7-12700": 152,
    "i9-12900": 162, "i5-13400": 140, "i5-13600": 165, "i7-13700": 175, "i9-13900": 185, "i5-14400": 142,
    "i5-14600": 168, "i7-14700": 180, "i9-14900": 190, "ultra 5 245": 160, "ultra 7 265": 172, "ultra 9 285": 180,
    # AMD
    "fx-4300": 28, "fx-6300": 35, "fx-8320": 40, "fx-8350": 42, "ryzen 3 1200": 60, "ryzen 3 1300": 63,
    "ryzen 5 1400": 65, "ryzen 5 1500": 70, "ryzen 5 1600": 82, "ryzen 7 1700": 83, "ryzen 7 1800": 88,
    "ryzen 3 2200": 62, "ryzen 5 2400": 70, "ryzen 5 2500": 85, "ryzen 5 2600x": 100, "ryzen 5 2600": 95,
    "ryzen 7 2700x": 105, "ryzen 7 2700": 98, "ryzen 3 3100": 88, "ryzen 3 3300": 105, "ryzen 5 3400": 80,
    "ryzen 5 3500": 102, "ryzen 5 3600": 113, "ryzen 7 3700": 118, "ryzen 7 3800": 120, "ryzen 9 3900": 122,
    "ryzen 5 4500": 110, "ryzen 5 5500": 125, "ryzen 5 5600x3d": 165, "ryzen 5 5600": 140,
    "ryzen 7 5700x3d": 170, "ryzen 7 5700": 145,
    "ryzen 7 5800x3d": 175, "ryzen 7 5800": 150, "ryzen 9 5900": 152, "ryzen 9 5950": 155, "ryzen 5 7500": 160,
    "ryzen 5 7600": 165, "ryzen 7 7700": 175, "ryzen 7 7800x3d": 205, "ryzen 9 7900": 178, "ryzen 9 7950": 182,
    "ryzen 5 9600": 180, "ryzen 7 9700": 185, "ryzen 7 9800x3d": 230, "ryzen 9 9900": 190, "ryzen 9 9950": 195,
    # Portables (ordres de grandeur, limités par la chauffe) et consoles portables
    "i5-10300h": 85, "i7-10750h": 95, "i5-11400h": 105, "i7-11800h": 120, "i5-12450h": 115, "i5-12500h": 125,
    "i7-12700h": 140, "i5-13420h": 120, "i5-13500h": 135, "i7-13620h": 140, "i7-13700h": 150, "i9-13900h": 160,
    "ryzen 5 4600h": 100, "ryzen 7 4800h": 110, "ryzen 5 5600h": 120, "ryzen 7 5800h": 130, "ryzen 5 6600h": 130,
    "ryzen 7 6800h": 140, "ryzen 5 7535hs": 130, "ryzen 7 7735hs": 140, "ryzen 7 7840hs": 160, "ryzen 7 8845hs": 160,
    "core 2 duo": 15, "athlon 200ge": 40, "i3-530": 20, "a6-3650": 18, "i5-3300": 45, "i3-3225": 33, "i5-7300u": 45,
    "apple m1 max": 125, "apple m1 pro": 125, "apple m1": 115, "apple m2 max": 140, "apple m2 pro": 140,
    "apple m2": 130, "apple m3 max": 165, "apple m3 pro": 155, "apple m3": 150, "apple m4 max": 185,
    "apple m4 pro": 180, "apple m4": 170,
    "ryzen 3 3300u": 50, "custom apu 0405": 75, "custom apu 0932": 78, "ryzen z1 extreme": 140, "ryzen z1": 110,
}


def _norm(s):
    s = re.sub(r"\((r|tm|c)\)", " ", s.lower())  # « Intel(R) Core(TM) » de Windows
    s = re.sub(r"[®™()]", " ", s)
    s = s.replace("geforce", "").replace("radeon", "").replace("intel", "").replace("amd", "")
    s = re.sub(r"\bcore\s+i(\d)\s*[- ]\s*", r"i\1-", s)  # « Core i5 10400 » → « i5-10400 »
    s = re.sub(r"\b(i\d)\s+(\d{4,5})", r"\1-\2", s)
    return re.sub(r"\s+", " ", s)


def _trouver(texte, table):
    """Scores de tous les modèles cités dans le texte (le plus long motif gagne)."""
    t = _norm(texte)
    trouves, pris = [], []
    suffixe = r"(?:k|f|kf|ks|x|xt|g|ge|t)?" if table is CPU else ""
    for cle in sorted(table, key=len, reverse=True):
        for m in re.finditer(r"(?<![\w-])" + re.escape(cle) + suffixe + r"(?![\w])", t):
            if not any(a <= m.start() < b for a, b in pris):
                pris.append((m.start(), m.end()))
                trouves.append((m.start(), cle, table[cle]))
    return [(c, s) for _, c, s in sorted(trouves)]  # dans l'ordre du texte


def score(texte, table):
    """Score du premier modèle cité (« RX 6600/6600 XT/6650 XT » → RX 6600)."""
    t = _trouver(texte, table)
    if not t:
        return None
    if table is GPU and re.search(r"laptop|mobile|max-q", texte, re.I):
        return round(t[0][1] * 0.8)  # version portable : moins puissante que la carte de bureau
    return t[0][1]


def marque_gpu(nom):
    n = nom.lower()
    if re.search(r"nvidia|geforce|gtx|rtx|quadro", n):
        return "nvidia"
    if re.search(r"amd|radeon|ati\b|rx \d|vega|navi|van gogh|\d{3}m\b", n):
        return "amd"
    if re.search(r"intel|arc|iris|uhd", n):
        return "intel"
    return "inconnue"


def _meilleur_gpu(noms):
    """Plusieurs cartes (ex. graphismes intégrés + carte dédiée) : on garde la plus puissante."""
    noms = [n for n in dict.fromkeys(noms) if n and not re.search(r"llvmpipe|basic (display|render)|virtual|parsec", n, re.I)]
    if not noms:
        return ""
    return max(noms, key=lambda n: score(n, GPU) or 0)


# ---------- Détection Linux ----------

def _sh(cmd):
    try:
        return subprocess.run(cmd, capture_output=True, text=True, timeout=8).stdout
    except (OSError, subprocess.SubprocessError):
        return ""


def _linux():
    cpu = ""
    try:
        with open("/proc/cpuinfo") as f:
            cpu = next((l.split(":", 1)[1].strip() for l in f if l.startswith("model name")), "")
    except OSError:
        pass
    gpus = []
    if shutil.which("vulkaninfo"):
        gpus = re.findall(r"deviceName\s*=\s*(.+?)(?:\s*\(.*)?$", _sh(["vulkaninfo", "--summary"]), re.M)
    if not [g for g in gpus if "llvmpipe" not in g.lower()] and shutil.which("lspci"):
        for l in _sh(["lspci"]).splitlines():
            if re.search(r"vga|3d|display", l, re.I):
                nom = l.split(": ", 1)[-1]
                m = re.search(r"\[([^\]]*(?:Radeon|GeForce|Arc)[^\]]*)\]", nom)  # « Navi 23 [Radeon RX 6600/6600 XT] »
                gpus.append((m.group(1) if m else nom).split("/")[0])
    vram = 0
    for f in glob.glob("/sys/class/drm/card*/device/mem_info_vram_total"):
        try:
            vram = max(vram, int(open(f).read()) / 2**30)
        except (OSError, ValueError):
            pass
    ram = None
    try:
        with open("/proc/meminfo") as f:
            ram = int(next(l.split()[1] for l in f if l.startswith("MemTotal"))) / 2**20
    except (OSError, StopIteration, ValueError):
        pass
    os_nom = "Linux"
    try:
        with open("/etc/os-release") as f:
            info = dict(l.rstrip().split("=", 1) for l in f if "=" in l)
            os_nom = info.get("PRETTY_NAME", info.get("NAME", "Linux")).strip('"')
    except OSError:
        pass
    return cpu, _meilleur_gpu(gpus), vram or None, ram, os_nom


# ---------- Détection Windows (registre + API Windows, sans PowerShell) ----------

def _windows():
    import ctypes
    import winreg

    def lire(cle, valeur, racine=winreg.HKEY_LOCAL_MACHINE):
        try:
            with winreg.OpenKey(racine, cle) as k:
                return winreg.QueryValueEx(k, valeur)[0]
        except OSError:
            return None

    cpu = (lire(r"HARDWARE\DESCRIPTION\System\CentralProcessor\0", "ProcessorNameString") or "").strip()
    # Cartes graphiques : la classe « Display » du gestionnaire de périphériques
    classe = r"SYSTEM\CurrentControlSet\Control\Class\{4d36e968-e325-11ce-bfc1-08002be10318}"
    cartes = []
    try:
        with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, classe) as k:
            for i in range(winreg.QueryInfoKey(k)[0]):
                sous = winreg.EnumKey(k, i)
                if not sous.isdigit():
                    continue
                nom = lire(classe + "\\" + sous, "DriverDesc")
                mem = lire(classe + "\\" + sous, "HardwareInformation.qwMemorySize") \
                    or lire(classe + "\\" + sous, "HardwareInformation.MemorySize")
                if isinstance(mem, bytes):
                    mem = int.from_bytes(mem, "little")
                if nom:
                    cartes.append((nom, (mem or 0) / 2**30))
    except OSError:
        pass
    gpu = _meilleur_gpu([n for n, _ in cartes])
    vram = next((m for n, m in cartes if n == gpu), 0)

    class MEMORYSTATUSEX(ctypes.Structure):
        _fields_ = [("dwLength", ctypes.c_ulong), ("dwMemoryLoad", ctypes.c_ulong),
                    ("ullTotalPhys", ctypes.c_ulonglong), ("ullAvailPhys", ctypes.c_ulonglong),
                    ("ullTotalPageFile", ctypes.c_ulonglong), ("ullAvailPageFile", ctypes.c_ulonglong),
                    ("ullTotalVirtual", ctypes.c_ulonglong), ("ullAvailVirtual", ctypes.c_ulonglong),
                    ("ullAvailExtendedVirtual", ctypes.c_ulonglong)]
    st = MEMORYSTATUSEX()
    st.dwLength = ctypes.sizeof(st)
    ram = st.ullTotalPhys / 2**30 if ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(st)) else None
    # Windows 11 se déclare « 10.0 » : on regarde le numéro de build
    build = int(lire(r"SOFTWARE\Microsoft\Windows NT\CurrentVersion", "CurrentBuildNumber") or 0)
    os_nom = "Windows 11" if build >= 22000 else "Windows 10" if build else "Windows"
    return cpu, gpu, vram or None, ram, os_nom


# ---------- Détection macOS ----------

def _macos():
    cpu = _sh(["sysctl", "-n", "machdep.cpu.brand_string"]).strip()
    try:
        ram = int(_sh(["sysctl", "-n", "hw.memsize"])) / 2**30
    except ValueError:
        ram = None
    cartes = []
    try:
        for c in json.loads(_sh(["system_profiler", "SPDisplaysDataType", "-json"]) or "{}").get("SPDisplaysDataType", []):
            m = re.search(r"(\d+)\s*([GM])B", c.get("spdisplays_vram", "") or c.get("spdisplays_vram_shared", ""))
            cartes.append((c.get("sppci_model", ""), int(m.group(1)) / (1 if m.group(2) == "G" else 1024) if m else 0))
    except ValueError:
        pass
    gpu = _meilleur_gpu([n for n, _ in cartes])
    vram = next((v for n, v in cartes if n == gpu), 0)
    # puces Apple : mémoire unifiée, pas de mémoire vidéo séparée
    return cpu, gpu, None if gpu.startswith("Apple") else vram or None, ram, ("macOS " + platform.mac_ver()[0]).strip()


def detecter():
    """Matériel réel du PC."""
    systeme = platform.system()
    os_court = {"Windows": "windows", "Darwin": "macos"}.get(systeme, "linux")
    try:
        cpu, gpu, vram, ram, os_nom = {"windows": _windows, "macos": _macos}.get(os_court, _linux)()
    except Exception:
        cpu, gpu, vram, ram, os_nom = platform.processor(), "", None, None, systeme
    return {"os": os_court, "os_nom": os_nom,
            "gpu": gpu or "Unknown graphics card", "cpu": cpu or "Unknown processor",
            "marque_gpu": marque_gpu(gpu or ""),
            "vram_go": round(vram) if vram else None, "ram_go": round(ram) if ram else None,
            "gpu_score": score(gpu or "", GPU), "cpu_score": score(cpu or "", CPU)}


# ---------- Comparaison avec la config Steam du jeu ----------

def _gpu_selon_vram(vram):
    """Aucun modèle cité (ex. CS2 : « 1 GB, compatible DirectX 11 ») : niveau estimé d'après la mémoire vidéo demandée."""
    if not vram:
        return None
    v = max(int(x) for x in vram)
    return next((s for seuil, s in ((1, 12), (2, 22), (3, 32), (4, 42), (6, 58), (8, 80)) if v <= seuil), 100)


def lire_config(html):
    """Extrait GPU / CPU / RAM / VRAM d'un bloc de configuration Steam."""
    t = re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", html or ""))

    def section(nom):
        m = re.search(nom + r"\s*:\s*(.*?)(?=\b(?:OS|Processor|Memory|Graphics|DirectX|Network|Storage|Sound Card|Additional Notes|VR Support)\s*:|$)", t, re.I)
        return m.group(1) if m else ""
    gfx, proc, mem = section("Graphics"), section("Processor"), section("Memory")
    g, c = _trouver(gfx, GPU), _trouver(proc, CPU)
    ram = re.search(r"(\d+)\s*GB", mem, re.I)
    vram = re.findall(r"(\d+)\s*GB", gfx, re.I)
    return {
        "gpu_txt": gfx.strip()[:120], "cpu_txt": proc.strip()[:120],
        # les modèles listés sont censés être équivalents : on prend la moyenne
        "gpu": round(sum(s for _, s in g) / len(g)) if g else _gpu_selon_vram(vram),
        "cpu": round(sum(s for _, s in c) / len(c)) if c else None,
        "ram": int(ram.group(1)) if ram else None,
        "vram": max(int(v) for v in vram) if vram else None,
    }


def _position(score_pc, mini, reco):
    """Place un score sur une échelle 0-100 : <25 sous le minimum, 25-60 entre min et reco, >60 au-dessus."""
    if not score_pc or not (mini or reco):
        return None
    mini = mini or reco * 0.6
    reco = reco or mini  # recommandé inconnu : atteindre le minimum suffit
    if reco <= mini:
        reco = mini * 1.3 if reco == mini and mini else mini
    if score_pc < mini:
        return max(2, 25 - 50 * (1 - score_pc / mini))
    if score_pc < reco:
        return max(25 + 35 * (score_pc - mini) / (reco - mini), 60 - 100 * (1 - score_pc / reco))
    return min(98, 60 + 38 * min(1, (score_pc / reco - 1) / 1.0))


NIVEAUX = [
    (15, "Well below minimum", "May be unplayable or very choppy."),
    (25, "Slightly below minimum", "Playable on low settings, with possible frame drops."),
    (40, "Right at minimum", "Playable on low settings, 1080p or lower."),
    (60, "Between minimum and recommended", "Low to medium settings at 1080p."),
    (80, "Recommended reached", "Usually high settings at 1080p."),
    (101, "Above recommended", "Very comfortable at 1080p, maybe 1440p."),
]


def comparer(pc, mini_html, reco_html, ecart_linux, natif, bloque_linux, lang="en"):
    mini, reco = lire_config(mini_html), lire_config(reco_html)
    if not pc["gpu_score"] or not (mini["gpu"] or reco["gpu"]):
        return None
    details = []

    def ligne(nom, perso, m, r):
        cible = r or m
        if perso and cible:
            pct = round(100 * perso / cible)
            etat = "✅" if perso >= cible else ("⚠️" if (m and perso >= m) else "❌")
            details.append({"nom": T(lang, nom), "etat": etat,
                            "texte": T(lang, "{pct}% of recommended" if r else "{pct}% of minimum", pct=pct)})

    ligne("Graphics card", pc["gpu_score"], mini["gpu"], reco["gpu"])
    ligne("Processor", pc["cpu_score"], mini["cpu"], reco["cpu"])
    if pc["ram_go"] and (reco["ram"] or mini["ram"]):
        c = reco["ram"] or mini["ram"]
        details.append({"nom": T(lang, "RAM"), "etat": "✅" if pc["ram_go"] >= c else ("⚠️" if mini["ram"] and pc["ram_go"] >= mini["ram"] else "❌"),
                        "texte": T(lang, "{a} GB / {b} GB recommended" if reco["ram"] else "{a} GB / {b} GB minimum",
                                   a=pc["ram_go"], b=c)})
    if pc["vram_go"] and (reco["vram"] or mini["vram"]):
        c = reco["vram"] or mini["vram"]
        details.append({"nom": T(lang, "Video memory"), "etat": "✅" if pc["vram_go"] >= c else "⚠️",
                        "texte": T(lang, "{a} GB / {b} GB required", a=pc["vram_go"], b=c)})

    def pour_os(facteur):
        pos_gpu = _position(pc["gpu_score"] * facteur, mini["gpu"], reco["gpu"])
        # l'écart Linux (traduction DXVK/VKD3D) porte surtout sur le GPU : le CPU reste inchangé
        pos_cpu = _position(pc["cpu_score"], mini["cpu"], reco["cpu"]) if pc["cpu_score"] else None
        # le CPU plafonne les FPS mais ne force pas à baisser les graphismes : il pèse moins que le GPU
        pos = pos_gpu if pos_cpu is None else min(pos_gpu, pos_cpu + 15)
        if pc["ram_go"] and mini["ram"] and pc["ram_go"] < mini["ram"]:
            pos = min(pos, 20)
        titre, texte = next((t, x) for seuil, t, x in NIVEAUX if pos < seuil)
        limite = "processor" if pos_cpu is not None and pos_cpu + 15 < pos_gpu else "graphics card"
        return {"position": round(pos), "niveau": T(lang, titre), "texte": T(lang, texte), "limite": T(lang, limite),
                "cpu_limite": limite == "processor"}

    res = {"windows": pour_os(1.0), "details": details}
    if bloque_linux:
        res["linux"] = None
    else:
        res["linux"] = pour_os(1 + (0 if natif else ecart_linux) / 100)
        if res["linux"]["position"] == res["windows"]["position"] and res["windows"]["cpu_limite"]:
            res["note"] = T(lang, "Same level on both systems: the processor is the limit, and Linux doesn't change that.")
        elif res["linux"]["position"] == res["windows"]["position"]:
            res["note"] = T(lang, "Same level on both systems for this game.")
    return res
