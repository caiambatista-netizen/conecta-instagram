"""Publica os posts da fila cujo horário já chegou.

Cada post é uma pasta em fila/ com um post.json e as mídias:
  {
    "conta": "pessoal" | "conecta",
    "quando": "2026-11-17 12:30",      # horário de Brasília
    "tipo": "imagem" | "carrossel" | "reel" | "story",
    "midia": ["1.png", "2.png"],
    "legenda": "texto...",
    "aprovado": true                   # só publica se o Caiam aprovou
  }
Registro em data/publicados.csv (evita publicar duas vezes).

Uso: python publicar.py            -> publica o que venceu
     python publicar.py --simular  -> só mostra o que publicaria
"""
import csv
import json
import os
import sys
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

import ig

TZ = ZoneInfo("America/Sao_Paulo")
RAIZ = Path(__file__).parent
REGISTRO = RAIZ / "data" / "publicados.csv"
REPO = os.environ.get("GITHUB_REPOSITORY", "caiambatista-netizen/conecta-instagram")
RAW = f"https://raw.githubusercontent.com/{REPO}/main"


def ja_publicados():
    if not REGISTRO.exists():
        return set()
    with REGISTRO.open() as f:
        return {l["pasta"] for l in csv.DictReader(f) if l["status"] == "ok"}


def registrar(pasta, conta, status, detalhe):
    REGISTRO.parent.mkdir(exist_ok=True)
    novo = not REGISTRO.exists()
    with REGISTRO.open("a", newline="") as f:
        w = csv.writer(f)
        if novo:
            w.writerow(["data", "pasta", "conta", "status", "detalhe"])
        w.writerow([datetime.now(TZ).strftime("%Y-%m-%d %H:%M"), pasta, conta, status, detalhe])


def main():
    simular = "--simular" in sys.argv
    agora = datetime.now(TZ)
    feitos = ja_publicados()
    vencidos = []
    for pj in sorted((RAIZ / "fila").glob("*/post.json")):
        pasta = pj.parent.name
        if pasta in feitos or pasta.startswith("exemplo"):
            continue
        p = json.loads(pj.read_text())
        quando = datetime.strptime(p["quando"], "%Y-%m-%d %H:%M").replace(tzinfo=TZ)
        if quando <= agora and p.get("aprovado"):
            vencidos.append((pasta, p))

    if not vencidos:
        print("Nada para publicar agora.")
        return

    falhas = 0
    for pasta, p in vencidos:
        urls = [f"{RAW}/fila/{pasta}/{m}" for m in p["midia"]]
        print(f"→ {pasta} ({p['conta']}, {p['tipo']}, {len(urls)} mídia)")
        if simular:
            continue
        try:
            mid = ig.publicar(p["conta"], p["tipo"], urls, p.get("legenda", ""))
            registrar(pasta, p["conta"], "ok", mid)
            print(f"  publicado: {mid}")
        except ig.ErroIG as e:
            falhas += 1
            registrar(pasta, p["conta"], "erro", str(e)[:300])
            print(f"  ERRO: {e}")
    sys.exit(1 if falhas else 0)


if __name__ == "__main__":
    main()
