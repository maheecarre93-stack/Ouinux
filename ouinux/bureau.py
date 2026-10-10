"""Intégration au bureau Linux : fenêtre d'application et raccourci dans le menu.

Sous Linux, l'exécutable n'embarque pas de moteur web (GTK/WebKit s'embarquent mal) :
- on ouvre l'interface dans une fenêtre d'application d'un navigateur Chromium (--app : ni onglets ni barre
  d'adresse), et à défaut dans un onglet du navigateur par défaut ;
- un exécutable Linux ne contient pas d'icône : le raccourci du menu (.desktop) la fournit.
"""
import os
import shutil
import subprocess
import sys

from . import prefs

# Navigateurs Chromium qui savent ouvrir une fenêtre d'application (--app)
BINAIRES = ["google-chrome-stable", "google-chrome", "chromium", "chromium-browser", "brave-browser", "brave",
            "microsoft-edge-stable", "microsoft-edge", "vivaldi-stable", "vivaldi"]
FLATPAKS = ["com.google.Chrome", "org.chromium.Chromium", "com.brave.Browser", "com.microsoft.Edge",
            "com.vivaldi.Vivaldi", "io.github.ungoogled_software.ungoogled_chromium"]

DONNEES = os.environ.get("XDG_DATA_HOME") or os.path.expanduser("~/.local/share")
RACCOURCI = os.path.join(DONNEES, "applications", "ouinux.desktop")
ICONE = os.path.join(DONNEES, "ouinux", "ouinux.png")


def _commande_chromium():
    for b in BINAIRES:
        chemin = shutil.which(b)
        if chemin:
            return [chemin]
    if shutil.which("flatpak"):
        for app in FLATPAKS:
            for base in ("/var/lib/flatpak/app", os.path.join(DONNEES, "flatpak", "app")):
                if os.path.isdir(os.path.join(base, app)):
                    return ["flatpak", "run", app]
    return None


def ouvrir_fenetre(url):
    """Ouvre l'interface dans une fenêtre d'application Chromium. Faux si aucun navigateur compatible."""
    cmd = _commande_chromium()
    if not cmd:
        return False
    try:
        subprocess.Popen(cmd + [f"--app={url}", "--window-size=560,860", "--class=Ouinux"],
                         stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
                         start_new_session=True)
        return True
    except OSError:
        return False


# ---------- Installation : copie du programme, menu des applications, lanceur sur le Bureau ----------
# Un exécutable Linux ne peut pas porter d'icône : sur le Bureau ou dans Dolphin il garde l'icône générique.
# Seuls les lanceurs .desktop en ont une. On installe donc une copie du programme à un endroit fixe,
# et ce sont les lanceurs (menu + Bureau) qui pointent vers elle.

INSTALLE = os.path.join(DONNEES, "ouinux", "Ouinux")
copie_faite = False  # vrai si ce lancement vient d'installer ou de mettre à jour la copie


def _dossier_bureau():
    """Dossier du Bureau (« Bureau », « Desktop »… selon la langue), d'après user-dirs.dirs."""
    config = os.environ.get("XDG_CONFIG_HOME") or os.path.expanduser("~/.config")
    try:
        with open(os.path.join(config, "user-dirs.dirs")) as f:
            for ligne in f:
                if ligne.startswith("XDG_DESKTOP_DIR="):
                    return ligne.split("=", 1)[1].strip().strip('"').replace("$HOME", os.path.expanduser("~"))
    except OSError:
        pass
    return os.path.expanduser("~/Desktop")


def _lanceur_bureau():
    return os.path.join(_dossier_bureau(), "ouinux.desktop")


def etat_raccourci():
    """None hors exécutable Linux ; sinon « present », « refuse » ou « absent » (à proposer)."""
    if not (getattr(sys, "frozen", False) and sys.platform.startswith("linux")):
        return None
    if os.path.exists(RACCOURCI):
        # déjà installé : si on lance un autre fichier (une version téléchargée), il remplace la copie installée
        _installer(bureau=os.path.realpath(sys.executable) != os.path.realpath(INSTALLE))
        return "present"
    return "refuse" if prefs.lire().get("raccourci") == "refuse" else "absent"


def _installer(bureau):
    global copie_faite
    os.makedirs(os.path.dirname(INSTALLE), exist_ok=True)
    if os.path.realpath(sys.executable) != os.path.realpath(INSTALLE):
        # fichier temporaire puis renommage : fonctionne même si l'ancienne copie est en cours d'exécution
        shutil.copyfile(sys.executable, INSTALLE + ".nouveau")
        os.chmod(INSTALLE + ".nouveau", 0o755)
        os.replace(INSTALLE + ".nouveau", INSTALLE)
        copie_faite = True
    shutil.copyfile(os.path.join(os.path.dirname(os.path.abspath(__file__)), "web", "icone.png"), ICONE)
    exe = INSTALLE.replace("\\", "\\\\").replace('"', '\\"')
    contenu = ("[Desktop Entry]\nType=Application\nName=Ouinux\n"
               "Comment=Will your games run on Linux?\nComment[fr]=Ce jeu tourne-t-il sous Linux ?\n"
               f'Exec="{exe}"\nIcon={ICONE}\nTerminal=false\nCategories=Game;Utility;\n'
               "StartupWMClass=Ouinux\n")
    lanceurs = [RACCOURCI] + ([_lanceur_bureau()] if bureau or os.path.exists(_lanceur_bureau()) else [])
    for chemin in lanceurs:
        if os.path.isdir(os.path.dirname(chemin)) or chemin == RACCOURCI:
            os.makedirs(os.path.dirname(chemin), exist_ok=True)
            with open(chemin, "w") as f:
                f.write(contenu)
            os.chmod(chemin, 0o755)  # KDE n'affiche (et ne lance) un lanceur du Bureau que s'il est exécutable


def repondre_raccourci(ajouter):
    if ajouter:
        _installer(bureau=True)
        return "present"
    prefs.ecrire(raccourci="refuse")
    return "refuse"
