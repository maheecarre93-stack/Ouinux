# Ouinux

Ce jeu fonctionne-t-il sous Linux, ou faut-il rester sur Windows ? Et comment **mon** PC s'en sortira ?

- Verdict calculé par des règles (anti-triche AreWeAntiCheatYet, version native Steam, notes ProtonDB, Steam Deck) : pas d'IA, donc pas d'invention.
- Détecte le matériel de l'utilisateur (Windows ou Linux) et le compare à la configuration demandée sur Steam.
- Estime l'écart de performances Linux/Windows selon l'API graphique du jeu (PCGamingWiki) et la marque de la carte graphique.

## Télécharger

Dans la page **Releases** du dépôt, prendre le fichier de son système :

| Système | Fichier | Lancement |
|---|---|---|
| Windows 10/11 | `Ouinux-Windows.exe` | double-clic. SmartScreen peut se méfier d'un programme non signé : « Informations complémentaires » → « Exécuter quand même ». |
| Linux | `Ouinux-Linux.zip` | dézipper, puis double-clic sur `Ouinux`. S'ouvre dans une fenêtre d'application si Chrome, Chromium, Brave, Edge ou Vivaldi est installé, sinon dans un onglet du navigateur ; l'app s'arrête quand on ferme la fenêtre. Au premier lancement, elle propose un raccourci avec son icône dans le menu des applications. |
| macOS (puce Apple) | `Ouinux-macOS.zip` | dézipper, puis clic droit sur l'app → « Ouvrir » la première fois (app non signée). |

L'interface est en français si le système l'est, en anglais sinon.

## Page de téléchargement

`docs/index.html` est publiée par GitHub Pages (Settings → Pages → « Deploy from a branch » → `main` / `/docs`).
Ses boutons pointent vers la dernière Release, donc rien à modifier quand une nouvelle version sort.

## Publier une nouvelle version

Chaque push sur `main` construit les trois fichiers sur GitHub (onglet Actions → « Artifacts »).
Pour les publier dans une Release : changer `VERSION` dans `ouinux/analyse.py`, puis

```
git tag v0.2.0 && git push --tags
```

## Traductions

Les textes source sont en anglais. Les traductions sont dans `ouinux/langues.py` (moteur) et dans `LANGUES` en haut du script de `ouinux/web/index.html` (interface).

## Lancer (développement)

```
python -m venv .venv
.venv/bin/pip install -r requirements.txt      # Windows : .venv\Scripts\pip ...
.venv/bin/python main.py                       # --navigateur pour l'ouvrir dans le navigateur
```

Les données sont mises en cache dans `~/.cache/ouinux` (Linux) `%LOCALAPPDATA%\Ouinux\cache` (Windows) ou `~/Library/Caches/ouinux` (macOS).

## Tester sur un vrai Windows sans GitHub

Double-cliquer `construire-windows.bat` : il installe Python 3.12 si besoin (winget), affiche le matériel détecté (aussi enregistré dans `diagnostic.txt`) puis produit `dist\Ouinux.exe`.
