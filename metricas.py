"""Puxa as métricas dos dois perfis e salva em data/metricas/AAAA-MM-DD.json + resumo.md.

O Claude lê esses arquivos para a análise semanal e o calendário seguinte.
"""
import json
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

import ig

TZ = ZoneInfo("America/Sao_Paulo")
PASTA = Path(__file__).parent / "data" / "metricas"
METRICAS_POST = "reach,views,likes,comments,saved,shares,total_interactions"


def conta_insights(conta):
    try:
        r = ig.chamar(conta, "me/insights", metric="reach,views,profile_links_taps,accounts_engaged,total_interactions",
                      period="day", metric_type="total_value", since=_dias_atras(28), until=_dias_atras(0))
        return {m["name"]: m.get("total_value", {}).get("value") for m in r.get("data", [])}
    except ig.ErroIG as e:
        return {"erro": str(e)[:200]}


def _dias_atras(n):
    return int(datetime.now(TZ).timestamp()) - n * 86400


def posts(conta, limite=25):
    r = ig.chamar(conta, "me/media", fields="id,caption,media_type,media_product_type,timestamp,permalink", limit=limite)
    saida = []
    for m in r.get("data", []):
        try:
            ins = ig.chamar(conta, f"{m['id']}/insights", metric=METRICAS_POST)
            m["insights"] = {i["name"]: i["values"][0]["value"] for i in ins.get("data", [])}
        except ig.ErroIG as e:
            m["insights"] = {"erro": str(e)[:150]}
        m["caption"] = (m.get("caption") or "")[:120]
        saida.append(m)
    return saida


def main():
    PASTA.mkdir(parents=True, exist_ok=True)
    hoje = datetime.now(TZ).strftime("%Y-%m-%d")
    tudo, linhas = {}, [f"# Métricas Instagram — {hoje}\n"]
    for conta in ig.CONTAS:
        try:
            p = ig.perfil(conta)
        except ig.ErroIG as e:
            linhas.append(f"## {conta}\nERRO: {e}\n")
            continue
        dados = {"perfil": p, "conta_28d": conta_insights(conta), "posts": posts(conta)}
        tudo[conta] = dados
        c = dados["conta_28d"]
        linhas.append(f"## @{p['username']} — {p.get('followers_count')} seguidores")
        linhas.append(f"28 dias: alcance {c.get('reach')}, views {c.get('views')}, "
                      f"engajadas {c.get('accounts_engaged')}, cliques no link {c.get('profile_links_taps')}\n")
        linhas.append("| data | tipo | alcance | salvos | compart. | coment. | legenda |\n|---|---|---|---|---|---|---|")
        for m in dados["posts"][:10]:
            i = m["insights"]
            linhas.append(f"| {m['timestamp'][:10]} | {m.get('media_product_type')} | {i.get('reach')} | "
                          f"{i.get('saved')} | {i.get('shares')} | {i.get('comments')} | {m['caption'][:50]!r} |")
        linhas.append("")
    (PASTA / f"{hoje}.json").write_text(json.dumps(tudo, ensure_ascii=False, indent=1))
    (PASTA / "resumo.md").write_text("\n".join(linhas))
    print("\n".join(linhas))


if __name__ == "__main__":
    main()
