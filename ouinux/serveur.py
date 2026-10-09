"""Petit serveur HTTP local (127.0.0.1 seulement) qui sert l'interface et l'API."""
import json
import os
import threading
import time
import urllib.parse
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

from . import analyse, materiel

WEB = os.path.join(os.path.dirname(os.path.abspath(__file__)), "web")


class Etat:
    pc = None
    pret = threading.Event()
    dernier_ping = None  # signe de vie de la page (pour s'arrêter quand elle est fermée)
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
        self.envoyer(204, b"")

    def do_GET(self):
        url = urllib.parse.urlparse(self.path)
        p = {k: v[0] for k, v in urllib.parse.parse_qs(url.query).items()}
        try:
            if url.path in ("/", "/index.html"):
                with open(os.path.join(WEB, "index.html"), "rb") as f:
                    self.envoyer(200, f.read(), "text/html")
            elif url.path == "/api/ping":
                Etat.dernier_ping = time.monotonic()
                Etat.quitter_demande = None
                self.envoyer(200, {})
            elif url.path == "/api/pc":
                Etat.pret.wait(20)
                self.envoyer(200, {**(Etat.pc or {}), "version": analyse.VERSION})
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
    return Etat.dernier_ping is not None and now - Etat.dernier_ping > 180
