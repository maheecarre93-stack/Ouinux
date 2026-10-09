"""Préférences de l'utilisateur (langue, raccourci refusé…), gardées d'un lancement à l'autre."""
import json
import os
import platform


def _fichier():
    systeme = platform.system()
    if systeme == "Windows":
        base = os.path.join(os.environ.get("APPDATA") or os.path.expanduser("~"), "Ouinux")
    elif systeme == "Darwin":
        base = os.path.expanduser("~/Library/Application Support/Ouinux")
    else:
        base = os.path.join(os.environ.get("XDG_CONFIG_HOME") or os.path.expanduser("~/.config"), "ouinux")
    return os.path.join(base, "prefs.json")


FICHIER = _fichier()


def lire():
    try:
        with open(FICHIER) as f:
            return json.load(f)
    except (OSError, ValueError):
        return {}


def ecrire(**valeurs):
    os.makedirs(os.path.dirname(FICHIER), exist_ok=True)
    with open(FICHIER, "w") as f:
        json.dump({**lire(), **valeurs}, f)
