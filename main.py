#!/usr/bin/env python3
"""Lance Ouinux dans sa propre fenêtre (ou dans le navigateur si pywebview manque).

Options :  --navigateur   ouvrir dans le navigateur au lieu d'une fenêtre
           --port N       port fixe (par défaut : un port libre au hasard)
           --diagnostic   afficher le matériel détecté (JSON) puis quitter
"""
import os
import sys
import time
import webbrowser

from ouinux import serveur

# Exécutable PyInstaller sous Linux : il impose ses propres bibliothèques (LD_LIBRARY_PATH) aux programmes
# qu'il lance. Le navigateur, kde-open, vulkaninfo… doivent retrouver celles du système, sinon ils plantent.
if getattr(sys, "frozen", False) and sys.platform.startswith("linux"):
    if "LD_LIBRARY_PATH_ORIG" in os.environ:
        os.environ["LD_LIBRARY_PATH"] = os.environ["LD_LIBRARY_PATH_ORIG"]
    else:
        os.environ.pop("LD_LIBRARY_PATH", None)


def main():
    if "--diagnostic" in sys.argv:
        import json
        import platform
        from ouinux import materiel
        print(platform.platform(), platform.python_version())
        print(json.dumps(materiel.detecter(), ensure_ascii=False, indent=1))
        return
    port = int(sys.argv[sys.argv.index("--port") + 1]) if "--port" in sys.argv else 0
    url = serveur.demarrer(port)
    if "--navigateur" not in sys.argv:
        try:
            import webview
            webview.create_window("Ouinux", url, width=560, height=820, min_size=(380, 520))
            # Linux : GTK + WebKit (présent sur presque tous les bureaux) ; Windows : Edge WebView2 par défaut
            webview.start(gui="gtk" if sys.platform.startswith("linux") else None)
            return
        except Exception as e:  # pas de moteur web disponible : on se rabat sur le navigateur
            print(f"No window available ({e}), opening in the browser.", file=sys.stderr)
    print(f"Ouinux: {url}  (close the tab or press Ctrl+C to quit)")
    webbrowser.open(url)
    try:
        while not serveur.page_fermee():
            time.sleep(1)
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    main()
