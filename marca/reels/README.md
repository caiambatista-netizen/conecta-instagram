# Reels animados (Remotion)

`ConectaReel.tsx` roda dentro do `remotion-composer` do OpenMontage (precisa de `src/lib/localFonts.ts` com `loadNunito` e as fontes Nunito em `src/fonts/`).

Render: `npx remotion render src/index.tsx ConectaReel saida.mp4 --props=cenas.json`

Cenas: `theme` escuro|claro · `kind` title|list|price · `*palavra*` = destaque · `items` "01 Texto" vira lista numerada · `itemTimes` (segundos) sincroniza cada item com a narração. Narração: gerar no HeyGen com a "Voz 2" (pt), cortar cenas pelas pausas (ffmpeg silencedetect) e juntar com `-c:v copy`.
