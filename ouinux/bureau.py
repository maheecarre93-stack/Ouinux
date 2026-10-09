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


# ---------- Raccourci dans le menu des applications ----------

def etat_raccourci():
    """None hors exécutable Linux ; sinon « present », « refuse » ou « absent » (à proposer)."""
    if not (getattr(sys, "frozen", False) and sys.platform.startswith("linux")):
        return None
    if os.path.exists(RACCOURCI):
        _ecrire_raccourci()  # l'exécutable a pu être déplacé : on remet le chemin à jour
        return "present"
    return "refuse" if prefs.lire().get("raccourci") == "refuse" else "absent"


def _ecrire_raccourci():
    os.makedirs(os.path.dirname(ICONE), exist_ok=True)
    os.makedirs(os.path.dirname(RACCOURCI), exist_ok=True)
    shutil.copyfile(os.path.join(os.path.dirname(os.path.abspath(__file__)), "web", "icone.png"), ICONE)
    exe = sys.executable.replace("\\", "\\\\").replace('"', '\\"')
    with open(RACCOURCI, "w") as f:
        f.write("[Desktop Entry]\nType=Application\nName=Ouinux\n"
                "Comment=Will your games run on Linux?\nComment[fr]=Ce jeu tourne-t-il sous Linux ?\n"
                f'Exec="{exe}"\nIcon={ICONE}\nTerminal=false\nCategories=Game;Utility;\n'
                "StartupWMClass=Ouinux\n")
    os.chmod(RACCOURCI, 0o755)


def repondre_raccourci(ajouter):
    if ajouter:
        _ecrire_raccourci()
        return "present"
    prefs.ecrire(raccourci="refuse")
    return "refuse"
