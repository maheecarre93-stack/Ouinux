# Ouinux — notes pour Claude (session de test sur Windows)

Ce fichier passe le relais entre le Claude qui a développé Ouinux sous Linux (Bazzite) et le Claude qui va
le tester sur Windows 11, sur le même PC (dual-boot). Parle en français avec l'utilisatrice.

## Le projet en bref

Ouinux (« wee-nux » : *oui* + *Linux*) dit si un jeu fonctionne sous Linux ou s'il faut rester sur Windows,
et comment le PC de l'utilisateur s'en sortira. Verdict par règles (pas d'IA) : AreWeAntiCheatYet, ProtonDB,
Steam, Lutris, PCGamingWiki.

- `main.py` : lance un petit serveur local + une fenêtre pywebview (Edge WebView2 sous Windows) ;
  `--navigateur` ouvre dans le navigateur, `--diagnostic` affiche le matériel détecté en JSON puis quitte.
- `ouinux/materiel.py` : détection du matériel. **Sous Windows : registre** (`ProcessorNameString`, classe
  Display `{4d36e968-…}` → `DriverDesc` + `HardwareInformation.qwMemorySize`), `GlobalMemoryStatusEx` pour la RAM,
  build ≥ 22000 = Windows 11. Pas de PowerShell ni WMI.
- `ouinux/analyse.py` : verdict, perfs, cache dans `%LOCALAPPDATA%\Ouinux\cache`.
- `ouinux/langues.py` + `LANGUES` dans `ouinux/web/index.html` : textes source en anglais, traduction française.
- `.github/workflows/construire.yml` : construit `Ouinux-Windows.exe`, `Ouinux-Linux`, `Ouinux-macOS.zip`
  (PyInstaller) ; une tag `v*` les publie dans une Release.
- `docs/index.html` : page de téléchargement (GitHub Pages).

## Pourquoi ce test

**Rien n'a encore tourné sur un vrai Windows.** La détection Windows n'a été testée qu'avec un `winreg` simulé,
et le `.exe` n'a été construit que par GitHub Actions. Sous Linux tout est vérifié (5 distributions testées).

PC de test : Ryzen 5 2600X (un 5600X est commandé, il peut déjà être monté), Radeon RX 6600 8 Go, 16 Go de RAM,
Windows 11. Sous Linux, `--diagnostic` donne :
`gpu: AMD Radeon RX 6600`, `cpu: AMD Ryzen 5 2600X Six-Core Processor`, `vram_go: 8`, `ram_go: 16`,
`gpu_score: 100`, `cpu_score: 100`. Si le 5600X est monté, attendre `cpu_score: 140`.

## Plan de test (PowerShell)

### 1. L'exécutable publié

```powershell
$exe = "$env:USERPROFILE\Downloads\Ouinux-Windows.exe"
Invoke-WebRequest https://github.com/maheecarre93-stack/ouinux/releases/latest/download/Ouinux-Windows.exe -OutFile $exe
Start-Process $exe
```

Vérifier, et noter chaque point (OK / problème + message exact) :
- SmartScreen / Defender : avertissement ? bloqué ? (attendu : avertissement « éditeur inconnu », pas de blocage)
- temps avant l'ouverture de la fenêtre (un .exe PyInstaller « onefile » se décompresse : quelques secondes)
- une **fenêtre** s'ouvre (pas le navigateur) ; pas de fenêtre console noire en plus
- l'en-tête affiche `🪟 Windows 11 · <processeur> · <carte graphique> · 16 Go RAM` (interface en français
  si Windows est en français)
- analyser : **Elden Ring** (Linux, perfs + « Ton PC »), **Valorant** (Windows, anti-triche),
  **Counter-Strike 2** (Linux natif), **World of Warcraft** (hors Steam, via Lutris)
- le bouton Linux/Windows de « Ton PC pour ce jeu » ; Windows doit être sélectionné par défaut
- fermer la fenêtre, puis `Get-Process Ouinux -ErrorAction SilentlyContinue` → plus rien ne doit tourner

### 2. La détection depuis le code source

```powershell
winget install -e --id Python.Python.3.12      # si `py -3.12 --version` échoue ; rouvrir PowerShell ensuite
git clone https://github.com/maheecarre93-stack/ouinux C:\ouinux   # ou télécharger le zip de la branche main
cd C:\ouinux
py -3.12 -m venv .venv-win
.venv-win\Scripts\pip install -r requirements.txt
.venv-win\Scripts\python main.py --diagnostic
.venv-win\Scripts\python main.py              # l'app depuis le code, même vérifications qu'au 1.
```

Si la détection est fausse (carte graphique vide ou « Microsoft Basic Display Adapter », VRAM à 0 ou absurde,
RAM fausse) : regarder ce que contient vraiment le registre, par exemple
`Get-ItemProperty "HKLM:\SYSTEM\CurrentControlSet\Control\Class\{4d36e968-e325-11ce-bfc1-08002be10318}\0*" | Select DriverDesc, *MemorySize*`,
et proposer un correctif dans `ouinux/materiel.py` (fonction `_windows`).

### 3. La page de téléchargement

Ouvrir https://maheecarre93-stack.github.io/ouinux/ dans Edge : le gros bouton doit dire « Download for Windows » ;
le lien macOS doit ouvrir l'avertissement « never been tested on a real Mac » avant de télécharger.

### 4. Facultatif

`construire-windows.bat` (double-clic) : construit `dist\Ouinux.exe` en local et écrit `diagnostic.txt`.

## Règles

- **Ne pousse rien sur GitHub** et ne crée pas de tag sans l'accord explicite de l'utilisatrice.
  Les correctifs : les écrire dans le code de `C:\ouinux` et les décrire dans le rapport ; Claude côté Linux
  les reprendra.
- Ne modifie pas les réglages système de Windows pour « faire marcher » le test (ce serait masquer un problème
  que les autres utilisateurs auront aussi) : note-le plutôt dans le rapport.

## Le rapport : `C:\ouinux\RETOUR-WINDOWS.md`

Écris le rapport **à cet endroit précis** : depuis Linux, la partition C: est lisible (lecture seule), c'est
comme ça que le Claude côté Linux le récupérera. Contenu :

1. versions : Windows (build), Python, date
2. sortie complète de `python main.py --diagnostic`
3. chaque point du plan de test : OK / problème, avec les messages d'erreur **exacts**
4. les correctifs proposés (diff ou description), fichiers modifiés dans `C:\ouinux`
5. tout ce qui t'a surpris

À la fin, dire à l'utilisatrice d'éteindre Windows **complètement** pour que Linux voie le fichier à jour :
`shutdown /s /t 0` dans PowerShell (le démarrage rapide de Windows laisse sinon la partition dans un état figé).
