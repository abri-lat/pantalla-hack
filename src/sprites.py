"""Necesita Pillow (pip install pillow). Tarda ~1 min.

    python3 src/sprites.py

Recorta las hojas de sprites por los huecos reales entre personajes (no por
una rejilla fija), quita las astillas del frame vecino y alinea cada frame por
los pies, para que la animación no brinque ni se vean cortes."""
from PIL import Image
from collections import deque
import os, json
HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, 'sprites-originales')
OUT = os.path.join(HERE, 'assets', 'sprites')
S, G = 0.6, 8

def key_sheet(im, lo, sat, enclosed):
    im = im.convert('RGB'); w, h = im.size; px = im.load()
    white = [[(lambda p: min(p) > lo and max(p) - min(p) < sat)(px[x, y]) for x in range(w)] for y in range(h)]
    bg = [[False] * w for _ in range(h)]; seen = [[False] * w for _ in range(h)]
    for y0 in range(h):
        for x0 in range(w):
            if not white[y0][x0] or seen[y0][x0]: continue
            comp, edge, q = [], False, deque([(x0, y0)]); seen[y0][x0] = True
            while q:
                x, y = q.popleft(); comp.append((x, y))
                if x in (0, w - 1) or y in (0, h - 1): edge = True
                for nx, ny in ((x+1, y), (x-1, y), (x, y+1), (x, y-1)):
                    if 0 <= nx < w and 0 <= ny < h and white[ny][nx] and not seen[ny][nx]:
                        seen[ny][nx] = True; q.append((nx, ny))
            if edge or (enclosed and len(comp) > 250):
                for x, y in comp: bg[y][x] = True
    out = Image.new('RGBA', (w, h)); op = out.load()
    for y in range(h):
        for x in range(w):
            if bg[y][x]: continue
            r, g, b = px[x, y]; a = 255
            if any(0 <= nx < w and 0 <= ny < h and bg[ny][nx] for nx, ny in ((x+1, y), (x-1, y), (x, y+1), (x, y-1))):
                m = min(r, g, b)
                if m > 200: a = max(0, min(255, (250 - m) * 6))
            op[x, y] = (r, g, b, a)
    return out

def components(a, w, h):
    """componentes conexas de pixeles opacos; devuelve lista de listas de (x,y)"""
    seen = [[False] * w for _ in range(h)]; comps = []
    for y0 in range(h):
        for x0 in range(w):
            if a[x0, y0] < 40 or seen[y0][x0]: continue
            comp, q = [], deque([(x0, y0)]); seen[y0][x0] = True
            while q:
                x, y = q.popleft(); comp.append((x, y))
                for nx, ny in ((x+1, y), (x-1, y), (x, y+1), (x, y-1), (x+1, y+1), (x-1, y-1), (x+1, y-1), (x-1, y+1)):
                    if 0 <= nx < w and 0 <= ny < h and not seen[ny][nx] and a[nx, ny] >= 40:
                        seen[ny][nx] = True; q.append((nx, ny))
            comps.append(comp)
    return comps

def process(char, name, file, lo, sat, enclosed, keep_y=False):
    sh = Image.open(os.path.join(SRC, file))
    sh = sh.resize((int(sh.width * S), int(sh.height * S)), Image.LANCZOS)
    k = key_sheet(sh, lo, sat, enclosed); w, h = k.size; A = k.getchannel('A').load()
    occ = [sum(1 for y in range(h) if A[x, y] > 40) for x in range(w)]
    cell = w / 8; cuts = [0]
    for i in range(1, 8):
        c = int(i * cell); r = int(cell * .28)
        cuts.append(min(range(c - r, c + r), key=lambda x: (occ[x], abs(x - c))))
    cuts.append(w)
    frames = []
    for i in range(8):
        f = k.crop((cuts[i], 0, cuts[i + 1], h)); fw = f.width; fa = f.getchannel('A').load()
        comps = components(fa, fw, h); total = sum(len(c) for c in comps)
        fp = f.load()
        for c in comps:
            touches = any(x in (0, fw - 1) for x, _ in c)
            if len(c) < total * .03 and (touches or len(c) < 30):
                for x, y in c: fp[x, y] = (0, 0, 0, 0)
        bb = f.getbbox(); f = f.crop(bb)
        # ancla: centro de los pies (el 30% inferior de la figura)
        fa = f.getchannel('A').load(); fw, fh = f.size
        xs = [x for y in range(int(fh * .7), fh) for x in range(fw) if fa[x, y] > 40]
        cx = (min(xs) + max(xs)) / 2 if xs else fw / 2
        frames.append((f, cx, bb[1]))
    left = max(cx for _, cx, _ in frames); right = max(f.width - cx for f, cx, _ in frames)
    CW = int(left + right) + 2
    if keep_y:
        top = min(t for _, _, t in frames); CH = max(t - top + f.height for f, _, t in frames)
    else:
        CH = max(f.height for f, _, _ in frames)
    strip = Image.new('RGBA', ((CW + 2 * G) * 8, CH))
    for i, (f, cx, t) in enumerate(frames):
        x = i * (CW + 2 * G) + G + int(left - cx)
        y = (t - top) if keep_y else CH - f.height
        strip.paste(f, (x, y), f)
    strip.save(os.path.join(OUT, f'{char}_{name}_g.png'), optimize=True)
    return CW, CH

meta = {}
for n in ['idle', 'walk', 'jump', 'spin', 'standup', 'wave']:
    meta[f's-{n}'] = ('nova', n) + process('nova', n, f'nova_{n}.png', 215, 30, True, keep_y=(n == 'jump'))
for n, f in [('idle', 'avon_idle.png'), ('jump', 'avon_jump.png'), ('walk', 'avon_walk2.png'), ('wave', 'avon_wave.png'), ('spin', 'avon_spin.png')]:
    meta[f'a-{n}'] = ('avon', n) + process('avon', n, f, 238, 16, False, keep_y=(n == 'jump'))
json.dump(meta, open(os.path.join(OUT, 'sprites.json'), 'w'), indent=1)
print(json.dumps(meta))
