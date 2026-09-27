"""Arma los HTML publicados a partir de las plantillas de src/, incrustando
fuentes, logos, sprites e imágenes como data URIs. Cada salida es un solo
archivo que funciona sin internet.

    python3 src/build.py

Salidas:
    index.html      pantalla del evento (src/template.html)
    ganadores.html  deck de premiación (src/template-ganadores.html)
    admin.html      panel para capturar equipos (src/template-admin.html)
    video.html      video de agradecimiento (src/template-video.html) → MP4 con src/video.mjs
"""
import base64, hashlib, json, os

SRC = os.path.dirname(os.path.abspath(__file__))
A = os.path.join(SRC, 'assets')
ROOT = os.path.dirname(SRC)

def uri(path, mime):
    return f'data:{mime};base64,' + base64.b64encode(open(path, 'rb').read()).decode()

def logo(name):
    return uri(os.path.join(A, 'logos', f'{name}.png'), 'image/png')

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

# logos que el deck de ganadores pinta en grande (patrocinador del premio)
LOGOS_GANADORES = ['n8n', 'clerk', 'elevenlabs', 'livinglab', 'talentland']

# contraseña de /admin: se guarda solo el hash en el HTML.
# Para cambiarla:  ADMIN_PASS='otra cosa' python3 src/build.py
ADMIN_PASS = os.environ.get('ADMIN_PASS', 'innovathon2026')
ADMIN_HASH = hashlib.sha256(ADMIN_PASS.encode()).hexdigest()

BLACKBIRD = uri(os.path.join(A, 'blackbird.otf'), 'font/otf')
JBM = uri(os.path.join(A, 'jetbrains-mono.woff2'), 'font/woff2')

sprites = json.load(open(os.path.join(A, 'sprites', 'sprites.json')))
SPRITE_CSS = ''.join(
    f".{cls}{{--fw:{cw + 16};--fh:{ch};background-image:url({uri(os.path.join(A, 'sprites', f'{c}_{n}_g.png'), 'image/png')});}}\n"
    for cls, (c, n, cw, ch) in sprites.items()
)
SPONSORS = json.dumps(
    [{'name': n, 'src': logo(f)} for n, f in PATROCINADORES],
    ensure_ascii=False,
)
LOGOS = json.dumps({n: logo(n) for n in LOGOS_GANADORES}, ensure_ascii=False)
# quienes organizan: van en grande en el video, aparte de los patrocinadores
ORGANIZADORES = json.dumps([
    {'name': 'INNOVA', 'desc': 'Comunidad de tecnología, IA e innovación de Chihuahua',
     'src': uri(os.path.join(A, 'organizadores', 'innova.png'), 'image/png')},
    {'name': 'Chihuahua Tech Week', 'desc': 'Chihuahua Tech Week 2026',
     'src': uri(os.path.join(A, 'organizadores', 'techweek.png'), 'image/png')},
], ensure_ascii=False)

COMUNES = {
    '{{BLACKBIRD}}': BLACKBIRD,
    '{{JBM}}': JBM,
    '{{SPRITE_CSS}}': SPRITE_CSS,
    '{{SPONSORS}}': SPONSORS,
    '{{LOGOS}}': LOGOS,
    '{{ORGANIZADORES}}': ORGANIZADORES,
    '{{ROBOTS}}': uri(os.path.join(A, 'robots.jpg'), 'image/jpeg'),
    '{{LOGO_N8N}}': logo('n8n'),
    '{{LOGO_CLERK}}': logo('clerk'),
    '{{LOGO_ELEVENLABS}}': logo('elevenlabs'),
    '{{ADMIN_HASH}}': ADMIN_HASH,
}

def render(plantilla, salida, titulo, corte='<div class="bg"></div>'):
    t = open(os.path.join(SRC, plantilla), encoding='utf-8').read()
    for k, v in COMUNES.items():
        t = t.replace(k, v)
    assert '{{' not in t, f'quedó un placeholder sin reemplazar en {plantilla}'
    # el <head> termina donde empieza el primer <div> del cuerpo
    full = ('<!doctype html>\n<html lang="es"><head><meta charset="utf-8">'
            '<meta name="viewport" content="width=device-width, initial-scale=1">\n'
            + t.replace(corte, '</head><body>\n' + corte, 1)
            + '\n</body></html>\n')
    open(os.path.join(ROOT, salida), 'w', encoding='utf-8').write(full)
    print(f'{salida} listo · {titulo} · {len(full) // 1024} KB')

render('template.html', 'index.html', f'{len(PATROCINADORES)} patrocinadores')
render('template-ganadores.html', 'ganadores.html', 'deck de premiación')
render('template-admin.html', 'admin.html', 'panel de captura')
render('template-video.html', 'video.html', 'video de agradecimiento', corte='<div id="frame">')
print(f'   contraseña de /admin: {ADMIN_PASS!r} (cámbiala con ADMIN_PASS=... antes de publicar)')
