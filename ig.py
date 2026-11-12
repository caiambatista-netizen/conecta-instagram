"""Cliente mínimo da Instagram API (login do Instagram, graph.instagram.com).

Só biblioteca padrão. Os tokens vêm de variáveis de ambiente (GitHub Secrets):
  IG_TOKEN_PESSOAL  -> @caiambatista
  IG_TOKEN_CONECTA  -> @conecta_terapias_oficial
"""
import json
import os
import time
import urllib.error
import urllib.parse
import urllib.request

API = "https://graph.instagram.com/v25.0"
CONTAS = {"pessoal": "IG_TOKEN_PESSOAL", "conecta": "IG_TOKEN_CONECTA"}


class ErroIG(Exception):
    pass


def token(conta):
    var = CONTAS[conta]
    valor = os.environ.get(var, "").strip()
    if not valor:
        raise ErroIG(f"Secret {var} não configurado")
    return valor


def chamar(conta, caminho, metodo="GET", **params):
    params["access_token"] = token(conta)
    dados = urllib.parse.urlencode(params).encode()
    if metodo == "GET":
        req = urllib.request.Request(f"{API}/{caminho}?{dados.decode()}")
    else:
        req = urllib.request.Request(f"{API}/{caminho}", data=dados, method=metodo)
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            return json.loads(r.read())
    except urllib.error.HTTPError as e:
        corpo = e.read().decode(errors="replace")
        # nunca imprimir o token
        raise ErroIG(f"{metodo} {caminho} -> HTTP {e.code}: {corpo[:400]}") from None


def perfil(conta):
    return chamar(conta, "me", fields="user_id,username,followers_count,media_count")


def esperar_container(conta, cid, limite_s=600):
    """Vídeo/Reel processa de forma assíncrona: espera ficar FINISHED."""
    fim = time.time() + limite_s
    while time.time() < fim:
        st = chamar(conta, cid, fields="status_code,status").get("status_code")
        if st == "FINISHED":
            return
        if st in ("ERROR", "EXPIRED"):
            raise ErroIG(f"Container {cid} falhou: {st}")
        time.sleep(10)
    raise ErroIG(f"Container {cid} não terminou em {limite_s}s")


def _item(conta, ig_id, url, **extra):
    if url.lower().endswith((".mp4", ".mov")):
        extra.setdefault("media_type", "VIDEO")
        cid = chamar(conta, f"{ig_id}/media", "POST", video_url=url, **extra)["id"]
        esperar_container(conta, cid)
    else:
        cid = chamar(conta, f"{ig_id}/media", "POST", image_url=url, **extra)["id"]
    return cid


def publicar(conta, tipo, urls, legenda=""):
    """tipo: imagem | carrossel | reel | story. Devolve o id da mídia publicada."""
    ig_id = perfil(conta)["user_id"]
    if tipo == "imagem":
        cid = _item(conta, ig_id, urls[0], caption=legenda)
    elif tipo == "carrossel":
        if not 2 <= len(urls) <= 10:
            raise ErroIG("Carrossel precisa de 2 a 10 arquivos")
        filhos = [_item(conta, ig_id, u, is_carousel_item="true") for u in urls]
        cid = chamar(conta, f"{ig_id}/media", "POST", media_type="CAROUSEL",
                     children=",".join(filhos), caption=legenda)["id"]
        esperar_container(conta, cid)
    elif tipo == "reel":
        cid = chamar(conta, f"{ig_id}/media", "POST", media_type="REELS",
                     video_url=urls[0], caption=legenda)["id"]
        esperar_container(conta, cid)
    elif tipo == "story":
        campo = "video_url" if urls[0].lower().endswith((".mp4", ".mov")) else "image_url"
        cid = chamar(conta, f"{ig_id}/media", "POST", media_type="STORIES", **{campo: urls[0]})["id"]
        if campo == "video_url":
            esperar_container(conta, cid)
    else:
        raise ErroIG(f"Tipo desconhecido: {tipo}")
    return chamar(conta, f"{ig_id}/media_publish", "POST", creation_id=cid)["id"]
