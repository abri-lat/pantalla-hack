# pantalla-hack

Pantalla que se proyecta durante el **INNOVATHON 2.0** (sábado 26 de septiembre de 2026, Parque Tecnológico Orión, Chihuahua). Muestra la cuenta regresiva, la agenda en vivo, los patrocinadores y a Nova y Avon animados.

- En vivo: https://pantalla-hack.vercel.app
- Sitio del evento: https://innovathon2026.innovacuu.xyz

Es **un solo HTML autocontenido**: fuentes, logos, sprites e imágenes van incrustados como data URIs. Funciona abierto desde la laptop sin internet, que es el plan B si falla el WiFi de la sede.

## Estructura

```
index.html                 ← lo que se publica. NO se edita a mano: lo genera src/build.py
kickoff/                   ← logos y QR públicos que usan las slides del kickoff (Apps Script)
src/
  template.html            ← el código real: CSS, HTML y JS, con placeholders {{...}}
  build.py                 ← incrusta los assets en template.html y escribe index.html
  sprites.py               ← corta las hojas de sprites originales en tiras limpias
  assets/
    blackbird.otf          ← fuente display (Projekt Blackbird)
    jetbrains-mono.woff2   ← fuente mono (variable, pesos 100–800)
    robots.jpg             ← render de Nova y Avon con la laptop
    logos/*.png            ← logos de patrocinadores, blancos, fondo transparente, 160 px de alto
    sprites/*_g.png        ← tiras de 8 frames ya procesadas + sprites.json con sus medidas
  sprites-originales/      ← hojas originales de Nova y Avon (fondo blanco, 8 frames c/u)
```

## Flujo de trabajo

```bash
# editar src/template.html (o agregar assets), luego:
python3 src/build.py      # regenera index.html
open index.html           # probar local
git push                  # Vercel publica solo
```

Una rama que no sea `main` genera una **URL de preview** en Vercel, así que una variación puede vivir en su rama sin tocar la pantalla del evento.

## Identidad (la misma del sitio INNOVATHON 2.0)

La interfaz es **estrictamente bicolor: neón sobre negro**. Los colores de los personajes (rosa, azul y amarillo) viven solo en las ilustraciones, nunca en la UI.

| Token | Valor | Uso |
|---|---|---|
| `--neon` | `#7CFF00` | acento: cuenta regresiva, etiquetas `>`, bordes activos |
| `--ink` | `#050505` | fondo |
| `--grid` | `#0B1008` | rejilla del fondo, relleno de barras |
| `--white` | `#FFFFFF` | texto principal |
| `--dim` | `#5f7a52` | texto secundario, bloques "suaves" de la agenda |
| `--line` | `#1c2b16` | bordes de tarjetas |
| `--code` | `#1b241b` | fondo de las etiquetas tipo `git commit -m "final"` |

- **Tipografía:** Blackbird para lo gigante (cuenta regresiva, títulos de celebración), siempre en mayúsculas. JetBrains Mono para todo lo demás. Las etiquetas van en mayúsculas con `letter-spacing` amplio.
- **Recursos del sitio que se repiten:** rejilla de 48 px de fondo, el tablero pixelado de la esquina superior derecha, scanlines CRT muy tenues, el kicker `40 PRINT "…"`, el `>` neón antes de cada etiqueta y los comandos de git como chips (`git status`, `git commit -m "final"`).
- **Escala:** todo se mide en múltiplos de `--k`, que vale `min(100vh/900, 100vw/1600)`. En 1920×1080 es 1.2 px. Para agregar un elemento, usa `calc(N * var(--k))` y escala solo en cualquier proyector.
- Esquinas rectas, sin sombras ni radios.

## Qué hace la pantalla

Todo depende de la **hora de la computadora**, no de la fecha.

| Hora | Cuenta regresiva |
|---|---|
| antes de 09:30 | ARRANCA EL HACKING EN |
| 09:30 – 19:45 | ÚLTIMO COMMIT EN (parpadea los últimos 10 min) |
| 19:45 – 20:00 | PITCHES EN |
| 20:00 – 20:40 | PITCHES |
| 20:40 – 20:50 | DELIBERACIÓN |
| desde 20:50 | PREMIACIÓN |

- **Header:** WiFi (constante `WIFI` en el bloque CONFIG), contador de las 12 horas del evento (9:00 a 21:00, un segmento por hora) y reloj.
- **Agenda:** "AHORA" y "SIGUIENTE" salen del arreglo `AGENDA`. Un `1` en la tercera columna atenúa el bloque (registro, comida) y la cuarta columna agrega un chip de comando.
- **Patrocinadores:** tarjeta que rota cada 8 s (todos con el mismo tiempo) y cinta infinita abajo. Los logos se pintan blancos con `filter: brightness(0) invert(1)`, así que cualquier PNG con fondo transparente funciona.
- **Nova y Avon en la esquina:** se turnan el globo de tips (`TIPS`) cada 20 s, y cada 45 s hacen un gesto.
- **Eventos que se disparan por minuto** (`onMinute`):
  - hitos en `HITOS` (09:30, café, pizza, faltan 60/30/10 min, 19:45, 20:00) → celebración a pantalla completa con los dos brincando
  - cada hora cerrada durante el hack → "Una hora menos"
  - cada 12 min → escena con el render de Nova y Avon (`SCENES`)
  - cada 3 min → cruza caminando Nova, luego Avon, luego los dos

### Controles de prueba

| Tecla | Hace |
|---|---|
| `→` / `←` | mueve la hora simulada ±15 min |
| `0` | regresa a la hora real |
| `p` | celebración |
| `s` | escena de Nova y Avon |
| `w` | caminata |
| clic | pantalla completa + evita que se apague la pantalla |

## Sprites

Hay dos personajes. **Nova** es el robot verde, mascota de INNOVA. **Avon** es la robot blanca de pelo rosa y azul.

| Clase | Animación |
|---|---|
| `s-idle` | Nova tecleando en la laptop |
| `s-walk` | Nova caminando a la derecha |
| `s-jump` | Nova brincando de gusto |
| `s-spin` | Nova girando en la silla |
| `s-standup` | Nova levantándose |
| `s-wave` | Nova saludando |
| `a-idle` | Avon parada |
| `a-walk` | Avon caminando a la derecha |
| `a-jump` | Avon brincando |
| `a-wave` | Avon saludando |
| `a-spin` | Avon dando una vuelta |

Para usar uno basta con `<div class="sprite s-jump"></div>`. `--dur` controla la velocidad del loop (default `.9s`).

**Cómo están hechas las tiras.** `src/sprites.py`:
1. Quita el fondo blanco. En Nova también borra los huecos blancos encerrados; en Avon no, porque su cuerpo es blanco.
2. Corta cada frame por los huecos reales entre dibujos, no por una rejilla fija.
3. Borra astillas del frame vecino.
4. Alinea todos los frames por los pies. El brinco conserva su altura.
5. Deja 8 px transparentes a cada lado de cada frame.

⚠️ **Dos detalles que causaban glitches:**
- El tamaño de `.sprite` se redondea a pixel entero con `round()`. Con fracciones, el navegador deja ver el borde del frame de al lado.
- El margen transparente entre frames es la segunda protección. Si agregas un sprite nuevo, pásalo por `sprites.py` y no lo cortes a mano.

`avon_walk.png` (camina a la izquierda) está en los originales pero no se usa. Si una animación necesita que alguien entre por la derecha, se agrega a la lista de `sprites.py`.

## Patrocinadores

Son 12, en este orden (definido en `src/build.py`):

n8n · AWS User Group Chihuahua · ElevenLabs · Zavu · Clerk · CAFFENIO · Ethereum México · Startup Chihuahua · Escuelita Maker · Talent Land México · Chihuahua Living Lab · Tec de Monterrey · Parque Tecnológico Orión

- INNOVA no va en la lista porque es la organizadora.
- Chihuahua Tech Week tampoco, porque el evento ya no es parte de la Tech Week.

**Para agregar uno:**
1. PNG con fondo transparente en `src/assets/logos/`, de 160 px de alto.
2. Una línea en `PATROCINADORES` en `build.py`.
3. `python3 src/build.py`.

## Beneficios de los patrocinadores (para referencia)

| Aliado | Beneficio | Para |
|---|---|---|
| n8n | 1 mes Cloud Pro | todos |
| ElevenLabs | 1 mes Creator | participantes |
| Cursor | créditos | participantes |
| Zavu | 3 meses Plan Pro (vence el domingo) | participantes |
| AWS UG Chihuahua | créditos | se entregan en el stand |
| Clerk | plan gratuito | todos |

**Premios:**
- **Ganador #1:** n8n Cloud Pro + swag box de n8n por integrante.
- **Ganadores #2 y #3:** swag box de n8n por integrante.
- **Menciones especiales:**
  - Best n8n Integration: swag box n8n.
  - Best Clerk Integration: swag de Clerk + plan Pro.
  - Best ElevenLabs Project: 3 meses Scale tier por miembro.

Los canjes viven en https://innovathon2026.innovacuu.xyz/perks.

## Idea para la variación de ganadores

La pieza que más se acerca es la **celebración** (`.party` y la función `party()`): overlay negro a pantalla completa, Nova y Avon brincando, un título gigante en Blackbird y una línea abajo. Una pantalla de ganadores podría:
- reusar ese overlay con un paso por premio, avanzando con una tecla para que quien presenta controle el ritmo: menciones especiales → #3 → #2 → #1
- revelar el nombre con suspenso: `> Y EL GANADOR ES…`, pausa, nombre en neón
- mostrar el logo del patrocinador de cada premio con el mismo filtro blanco de la tarjeta de patrocinadores
- cerrar con los dos personajes cruzando juntos (`walk()` con `both`) y un "gracias" con la cinta de patrocinadores

Conviene hacerla en su propia rama y, si crece, en su propio `template-ganadores.html` con una segunda salida en `build.py`, para no romper la pantalla del evento.
