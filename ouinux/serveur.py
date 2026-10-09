"""Petit serveur HTTP local (127.0.0.1 seulement) qui sert l'interface et l'API."""
import json
import os
import threading
import time
import urllib.parse
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

from . import analyse, bureau, materiel, prefs

WEB = os.path.join(os.path.dirname(os.path.abspath(__file__)), "web")


class Etat:
    pc = None
    pret = threading.Event()
    dernier_ping = None  # signe de vie de la page (pour s'arrêter quand elle est fermée)
    debut = time.monotonic()
    quitter_demande = None


def detecter_en_fond():
    Etat.pc = materiel.detecter()
    Etat.pret.set()
    analyse.base_anticheat()  # télécharge la base anti-triche pendant que l'utilisateur tape


class Handler(BaseHTTPRequestHandler):
    def log_message(self, *a):
        pass

    def envoyer(self, code, data, ctype="application/json"):
        body = data if isinstance(data, bytes) else json.dumps(data, ensure_ascii=False).encode()
        self.send_response(code)
        self.send_header("Content-Type", ctype + "; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(body)

    def do_POST(self):
        if self.path == "/api/quitter":  # onglet fermé (ou rechargé : le ping suivant annule l'arrêt)
            Etat.quitter_demande = time.monotonic()
        elif self.path in ("/api/langue?l=fr", "/api/langue?l=en"):
            try:
                prefs.ecrire(langue=self.path[-2:])
            except OSError:
                pass  # pas mémorisée, mais la page change quand même de langue
        elif self.path in ("/api/raccourci?ajouter=1", "/api/raccourci?ajouter=0"):
            try:
                self.envoyer(200, {"raccourci": bureau.repondre_raccourci(self.path.endswith("1"))})
            except OSError as e:
                self.envoyer(500, {"erreur": str(e)})
            return
        self.envoyer(204, b"")

    def do_GET(self):
        url = urllib.parse.urlparse(self.path)
        p = {k: v[0] for k, v in urllib.parse.parse_qs(url.query).items()}
        try:
            if url.path in ("/", "/index.html"):
                with open(os.path.join(WEB, "index.html"), encoding="utf-8") as f:
                    langue = prefs.lire().get("langue")  # choisie avec le bouton FR/EN ; sinon celle du système
                    page = f.read().replace("const LANGUE_CHOISIE = null;", f"const LANGUE_CHOISIE = {json.dumps(langue)};")
                    self.envoyer(200, page.encode(), "text/html")
            elif url.path == "/icone.png":
                with open(os.path.join(WEB, "icone.png"), "rb") as f:
                    self.envoyer(200, f.read(), "image/png")
            elif url.path == "/api/ping":
                Etat.dernier_ping = time.monotonic()
                Etat.quitter_demande = None
                self.envoyer(200, {})
            elif url.path == "/api/pc":
                Etat.pret.wait(20)
                self.envoyer(200, {**(Etat.pc or {}), "version": analyse.VERSION, "raccourci": bureau.etat_raccourci()})
            elif url.path == "/api/suggestions":
                self.envoyer(200, analyse.suggestions(p.get("q", ""), p.get("lang", "en")))
            elif url.path == "/api/analyse":
                Etat.pret.wait(20)
                appid = int(p["appid"]) if p.get("appid", "").isdigit() else None
                self.envoyer(200, analyse.analyser(Etat.pc, p.get("nom", ""), appid, p.get("slug") or None,
                                                          p.get("lang", "en")))
            else:
                self.envoyer(404, {"erreur": "introuvable"})
        except Exception as e:
            self.envoyer(500, {"erreur": str(e)})


def demarrer(port=0):
    """Démarre le serveur dans un thread ; port 0 = un port libre au hasard. Renvoie l'adresse."""
    threading.Thread(target=detecter_en_fond, daemon=True).start()
    srv = ThreadingHTTPServer(("127.0.0.1", port), Handler)
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    return f"http://127.0.0.1:{srv.server_address[1]}/"


def page_fermee():
    """Vrai si la page a été fermée : arrêt demandé il y a plus de 3 s, ou plus de signe de vie depuis 3 min
    (un onglet en arrière-plan peut être ralenti à un ping par minute)."""
    now = time.monotonic()
    if Etat.quitter_demande and now - Etat.quitter_demande > 3:
        return True
    if Etat.dernier_ping is None:  # la page ne s'est jamais ouverte (navigateur introuvable…) : on n'attend pas indéfiniment
        return now - Etat.debut > 120
    return now - Etat.dernier_ping > 180
