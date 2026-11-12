"""Renova os tokens longos (valem 60 dias) e grava de volta nos GitHub Secrets.

Precisa do secret GH_PAT (token do GitHub com permissão de Secrets neste repo).
Nunca imprime o token.
"""
import json
import os
import subprocess
import sys
import urllib.parse
import urllib.request

import ig

falhas = 0
for conta, var in ig.CONTAS.items():
    try:
        atual = ig.token(conta)
    except ig.ErroIG as e:
        print(f"{conta}: {e}")
        continue
    url = "https://graph.instagram.com/refresh_access_token?" + urllib.parse.urlencode(
        {"grant_type": "ig_refresh_token", "access_token": atual})
    try:
        with urllib.request.urlopen(url, timeout=60) as r:
            novo = json.loads(r.read())
    except Exception as e:  # noqa: BLE001
        falhas += 1
        print(f"{conta}: falhou ao renovar ({type(e).__name__})")
        continue
    print(f"::add-mask::{novo['access_token']}")
    subprocess.run(["gh", "secret", "set", var, "--body", novo["access_token"]], check=True,
                   env={**os.environ, "GH_TOKEN": os.environ["GH_PAT"]})
    print(f"{conta}: renovado, vale mais {novo.get('expires_in', 0) // 86400} dias")
sys.exit(1 if falhas else 0)
