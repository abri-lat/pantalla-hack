"""Arma index.html a partir de src/template.html, incrustando fuentes, logos,
sprites e imagen como data URIs. El resultado es un solo archivo que funciona
sin internet.

    python3 src/build.py
"""
import base64, json, os

SRC = os.path.dirname(os.path.abspath(__file__))
A = os.path.join(SRC, 'assets')
ROOT = os.path.dirname(SRC)

def uri(path, mime):
    return f'data:{mime};base64,' + base64.b64encode(open(path, 'rb').read()).decode()

# patrocinadores: [nombre visible, archivo en assets/logos]. El orden es el de rotación.
PATROCINADORES = [
    ('n8n', 'n8n'),
    ('AWS User Group Chihuahua', 'awsug'),
    ('ElevenLabs', 'elevenlabs'),
    ('Zavu', 'zavu'),
    ('Clerk', 'clerk'),
    ('CAFFENIO', 'caffenio'),
    ('Ethereum México', 'ethereum'),
    ('Startup Chihuahua', 'startupcuu'),
    ('Escuelita Maker', 'escuelita'),
    ('Talent Land México', 'talentland'),
    ('Chihuahua Living Lab', 'livinglab'),
    ('Tec de Monterrey · Parque Tecnológico Orión', 'orion'),
]

sprites = json.load(open(os.path.join(A, 'sprites', 'sprites.json')))
css = ''.join(
    f".{cls}{{--fw:{cw + 16};--fh:{ch};background-image:url({uri(os.path.join(A, 'sprites', f'{c}_{n}_g.png'), 'image/png')});}}\n"
    for cls, (c, n, cw, ch) in sprites.items()
)
spons = json.dumps(
    [{'name': n, 'src': uri(os.path.join(A, 'logos', f'{f}.png'), 'image/png')} for n, f in PATROCINADORES],
    ensure_ascii=False,
)

t = open(os.path.join(SRC, 'template.html'), encoding='utf-8').read()
t = (t.replace('{{BLACKBIRD}}', uri(os.path.join(A, 'blackbird.otf'), 'font/otf'))
      .replace('{{JBM}}', uri(os.path.join(A, 'jetbrains-mono.woff2'), 'font/woff2'))
      .replace('{{SPRITE_CSS}}', css)
      .replace('{{ROBOTS}}', uri(os.path.join(A, 'robots.jpg'), 'image/jpeg'))
      .replace('{{SPONSORS}}', spons))
assert '{{' not in t, 'quedó un placeholder sin reemplazar en template.html'

full = ('<!doctype html>\n<html lang="es"><head><meta charset="utf-8">'
        '<meta name="viewport" content="width=device-width, initial-scale=1">\n'
        + t.replace('<div class="bg"></div>', '</head><body>\n<div class="bg"></div>', 1)
        + '\n</body></html>\n')
open(os.path.join(ROOT, 'index.html'), 'w', encoding='utf-8').write(full)
print(f'index.html listo · {len(PATROCINADORES)} patrocinadores · {len(full) // 1024} KB')
