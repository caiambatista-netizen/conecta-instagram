"""Gera carrossel 1080x1350 na identidade visual Conecta Terapias.
Uso: python slides.py <pasta_saida> <slides.json>
slides.json: [{"tema":"escuro"|"claro","titulo":"... <em>destaque</em> ...","texto":"...","cta":"QUERO"(opcional)}]
"""
import asyncio, json, sys
from pathlib import Path
from playwright.async_api import async_playwright

M = Path(__file__).parent
import base64
FONT = "".join(f"@font-face{{font-family:Nunito;font-weight:{w};src:url(data:font/woff2;base64,{base64.b64encode((M/f'nunito-latin-{w}-normal.woff2').read_bytes()).decode()}) format('woff2')}}" for w in (500,700,800))
LOGO = """<svg viewBox="0 0 200 206" width="{w}" height="{h}"><defs><linearGradient id="b" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#4FCAF2"/><stop offset="1" stop-color="#1888CB"/></linearGradient><linearGradient id="g" x1="1" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#95DA46"/><stop offset="1" stop-color="#4CA527"/></linearGradient></defs><circle cx="44" cy="26" r="18" fill="url(#b)"/><circle cx="156" cy="26" r="18" fill="url(#g)"/><path fill="url(#b)" fill-rule="evenodd" d="M100 68 C93 53 78 40 58 40 C34 40 12 58 12 86 C12 118 38 150 100 196 Z M100 76 C96 67 88 60 77 60 C64 60 52 70 52 86 C52 104 66 122 100 150 Z"/><path fill="url(#g)" fill-rule="evenodd" d="M100 68 C107 53 122 40 142 40 C166 40 188 58 188 86 C188 118 162 150 100 196 Z M100 76 C104 67 112 60 123 60 C136 60 148 70 148 86 C148 104 134 122 100 150 Z"/></svg>"""
CSS = FONT + """
*{margin:0;box-sizing:border-box}
body{width:1080px;height:1350px;font-family:Nunito,sans-serif;padding:96px 92px;display:flex;flex-direction:column;justify-content:space-between;position:relative;overflow:hidden}
.escuro{background:#12263A;color:#fff}.claro{background:#FBF7F1;color:#12263A}
.lock{display:flex;align-items:center;gap:16px}.word{line-height:1.02}
.word b{display:block;font-weight:800;font-size:34px;letter-spacing:-.8px}.word small{display:block;font-weight:800;font-size:26px;letter-spacing:-.5px}
.escuro .word b{color:#fff}.escuro .word small{color:#7AC943}.claro .word b{color:#12263A}.claro .word small{color:#4CA527}
.top{display:flex;justify-content:space-between;align-items:center}
.n{font-weight:800;font-size:26px;letter-spacing:2px}.escuro .n{color:rgba(255,255,255,.55)}.claro .n{color:#6B6259}
.bar{height:12px;width:150px;border-radius:8px;background:linear-gradient(90deg,#4FCAF2,#1888CB 45%,#95DA46 55%,#4CA527)}
h1{font-weight:800;font-size:88px;line-height:1.08;letter-spacing:-2px;margin-top:44px}
.escuro em{font-style:normal;color:#7AC943}.claro em{font-style:normal;color:#1888CB}
p{font-weight:500;font-size:42px;line-height:1.38;margin-top:44px}.escuro p{color:rgba(255,255,255,.82)}.claro p{color:#4a4440}
.cta{display:inline-block;margin-top:52px;font-weight:800;font-size:46px;padding:22px 44px;border-radius:999px;color:#12263A;background:linear-gradient(90deg,#95DA46,#7AC943)}
.foot{display:flex;justify-content:space-between;font-weight:800;font-size:22px;letter-spacing:2px;text-transform:uppercase}
.escuro .foot{color:rgba(255,255,255,.55)}.claro .foot{color:#6B6259}
.ghost{position:absolute;right:-120px;bottom:-60px;opacity:.06}
"""
async def main(out, data):
    out = Path(out); out.mkdir(parents=True, exist_ok=True)
    total = len(data)
    async with async_playwright() as p:
        b = await p.chromium.launch(executable_path="/usr/bin/google-chrome")
        pg = await b.new_page(viewport={"width": 1080, "height": 1350})
        for i, s in enumerate(data, 1):
            cta = f"<div class='cta'>Comenta {s['cta']}</div>" if s.get("cta") else ""
            html = f"""<html><head><style>{CSS}</style></head><body class='{s["tema"]}'>
<div class='ghost'>{LOGO.format(w=620,h=639)}</div>
<div class='top'><div class='lock'>{LOGO.format(w=58,h=60)}<span class='word'><b>Conecta</b><small>Terapias</small></span></div><span class='n'>{i:02d}/{total:02d}</span></div>
<div><div class='bar'></div><h1>{s['titulo']}</h1>{f"<p>{s['texto']}</p>" if s.get('texto') else ''}{cta}</div>
<div class='foot'><span>@conecta_terapias_oficial</span><span>Nós somos a ponte</span></div></body></html>"""
            await pg.set_content(html); await pg.evaluate('document.fonts.ready'); await pg.wait_for_timeout(300)
            await pg.screenshot(path=str(out / f"{i}.png"))
        await b.close()

if __name__ == "__main__":
    asyncio.run(main(sys.argv[1], json.loads(Path(sys.argv[2]).read_text())))
