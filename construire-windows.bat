@echo off
rem Construit dist\Ouinux.exe (a lancer sur Windows : double-clic).
rem PyInstaller ne sait pas compiler pour Windows depuis Linux, d'ou ce script.
setlocal
cd /d "%~dp0"

rem Python 3.12 : pythonnet (utilise par pywebview sous Windows) ne suit pas toujours la derniere version
py -3.12 --version >nul 2>nul
if errorlevel 1 (
    echo Python 3.12 introuvable, installation via winget...
    winget install -e --id Python.Python.3.12 --accept-package-agreements --accept-source-agreements
    if errorlevel 1 goto erreur
    echo.
    echo Python installe. Ferme cette fenetre et relance le script.
    pause
    exit /b
)

if not exist .venv-win\Scripts\python.exe (
    py -3.12 -m venv .venv-win || goto erreur
)
.venv-win\Scripts\python -m pip install --upgrade pip >nul
.venv-win\Scripts\python -m pip install -r requirements.txt pyinstaller || goto erreur

echo.
echo === Materiel detecte (copie aussi dans diagnostic.txt) ===
.venv-win\Scripts\python main.py --diagnostic > diagnostic.txt 2>&1
type diagnostic.txt
echo.

.venv-win\Scripts\pyinstaller --noconfirm --clean --onefile --windowed --name Ouinux ^
    --add-data "ouinux\web;ouinux\web" main.py || goto erreur

echo.
echo Termine : dist\Ouinux.exe
pause
exit /b

:erreur
echo.
echo ECHEC de la construction (voir les messages ci-dessus).
pause
exit /b 1
