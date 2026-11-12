# Conecta Instagram

Agente na nuvem para **@caiambatista** (pessoal) e **@conecta_terapias_oficial** (Conecta), via API oficial do Instagram.

| Workflow | Quando | O que faz |
|---|---|---|
| Publicar fila | toda hora | publica os posts de `fila/` aprovados cujo horário chegou |
| Métricas semanais | segunda 07:41 | salva `data/metricas/` (o Claude usa na análise) |
| Renovar tokens | dias 1 e 15 | renova os tokens de 60 dias |

## Como um post entra na fila
Pasta `fila/AAAA-MM-DD_conta_assunto/` com `post.json` + mídias (veja `fila/exemplo-*`).
Só publica com `"aprovado": true`. Tipos: `imagem`, `carrossel` (2–10), `reel` (.mp4), `story`.

## Secrets (Settings → Secrets and variables → Actions)
- `IG_TOKEN_PESSOAL` e `IG_TOKEN_CONECTA`: token do app Meta (login do Instagram)
- `GH_PAT`: token do GitHub com permissão de Secrets neste repo (para renovar sozinho)

Repo público porque a Meta só aceita mídia em URL pública. **Nada de leads ou dados pessoais aqui** (isso fica no conecta-prospeccao, privado).

Prospecção por DM e automação comentário→DM continuam fora daqui (Chrome e Business Suite).
