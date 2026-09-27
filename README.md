# pantalla-hack

Pantalla que se proyecta durante el **INNOVATHON 2.0** (sábado 26 de septiembre de 2026, Parque Tecnológico Orión, Chihuahua). Muestra la cuenta regresiva, la agenda en vivo, los patrocinadores y a Nova y Avon animados.

- En vivo: https://pantalla-hack.vercel.app
- Sitio del evento: https://innovathon2026.innovacuu.xyz

Es **un solo HTML autocontenido**: fuentes, logos, sprites e imágenes van incrustados como data URIs. Funciona abierto desde la laptop sin internet, que es el plan B si falla el WiFi de la sede.

## Estructura

```
index.html                 ← pantalla del evento. NO se edita a mano: lo genera src/build.py
ganadores.html             ← deck de premiación. Tampoco se edita a mano.
admin.html                 ← panel privado para capturar los equipos. Tampoco.
vercel.json                ← rutas limpias: /primer, /segun, /tercer, /n8n, /clerk, /elevenlabs
kickoff/                   ← logos y QR públicos que usan las slides del kickoff (Apps Script)
src/
  template.html            ← el código real: CSS, HTML y JS, con placeholders {{...}}
  template-ganadores.html  ← el deck de premiación
  template-admin.html      ← el panel de captura
  build.py                 ← incrusta los assets en las tres plantillas y escribe los tres HTML
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

**Premios** (los que salen en el deck de premiación):

| | 3er lugar | 2do lugar | 1er lugar |
|---|---|---|---|
| Chihuahua Living Lab | 1 mes | 2 meses | 3 meses |
| Talent Land 2027 | becas | becas | becas |
| ElevenLabs | 3 meses Pro | 3 meses Pro | 3 meses Pro |
| Clerk | swag box | swag box | swag box |
| n8n | — | swag box | swag box |
| Vuelos a Talent Land | — | — | $10K |

**Menciones especiales** (un ganador cada una):
- Mejor integración n8n: n8n Cloud Pro + swag oficial.
- Mejor integración Clerk: plan Pro de Clerk + swag especial.
- Mejor integración ElevenLabs: 3 meses de Scale, 1.8M créditos al mes por miembro.

Los canjes viven en https://innovathon2026.innovacuu.xyz/perks.

## Premiación

Tres páginas más, construidas por el mismo `build.py`, con la misma identidad y los mismos sprites.

| Ruta | Qué es |
|---|---|
| `/ganadores` | el deck completo, desde la portada |
| `/n8n` `/clerk` `/elevenlabs` | el ganador de esa mejor integración, ya revelado |
| `/tercer` `/segun` `/primer` | ese lugar general, ya revelado, con sus premios |
| `/admin` | panel privado para escribir los equipos y controlar el deck (con contraseña) |

Entrar por una ruta directa muestra el slide **completo**, sin pasos: sirve para proyectar un solo premio. Entrar por `/ganadores` arranca en la portada y avanza paso por paso.

### Orden del deck

1. **Portada** — "Estos son los ganadores"
2. **Mejor integración n8n** — un ganador
3. **Mejor integración Clerk** — un ganador
4. **Mejor integración ElevenLabs** — un ganador
5. **Tercer lugar general** + premios
6. **Segundo lugar general** + premios
7. **Primer lugar general** + premios (incluye los $10K de vuelos y el swag de n8n)
8. **Cierre** — "Gracias por construir"

Cada slide se revela por pasos con la flecha: primero el encabezado, luego el nombre del equipo, al final el premio. Cuando cae el nombre, hay confeti.

### Controles

| Tecla | Hace |
|---|---|
| `→` `espacio` `clic` | siguiente paso |
| `←` `clic derecho` | paso anterior |
| `↑` `↓` | slide completo, sin pasos |
| `1`–`8` | saltar a ese slide |
| `c` | confeti |
| `a` | abrir `/admin` |
| `f` | pantalla completa |

### Cómo se sincroniza

`/admin` y `/ganadores` hablan por **BroadcastChannel**, y los nombres viven en `localStorage`. No hay backend: todo pasa dentro del mismo navegador, así que funciona con el WiFi caído.

Eso significa que **las dos pestañas tienen que estar en la misma laptop y el mismo navegador**. El flujo en el evento:

1. Abrir `/admin` en la laptop.
2. Apretar **Abrir /ganadores**, arrastrar esa ventana al proyector y ponerla en pantalla completa.
3. Escribir los equipos en `/admin` conforme el jurado decide — se guarda con cada tecla y la pantalla se actualiza sola.
4. Presentar desde las flechas del deck, o desde los botones de `/admin`.

`/admin` también trae **Copiar respaldo (JSON)** y **Pegar respaldo**, por si hay que mover los nombres a otra laptop.

### Contraseña de /admin

La contraseña por defecto es `innovathon2026`. Para cambiarla:

```bash
ADMIN_PASS='la que quieras' python3 src/build.py
```

En el HTML solo queda el **SHA-256**, nunca el texto plano, así que la palabra no se ve en el código fuente. Una vez que entras, el navegador te recuerda hasta que aprietes **Cerrar sesión**.

⚠️ **Esto no es seguridad real.** La página es estática: todo se descarga al navegador y quien sepa leer el código puede saltarse la puerta. Sirve para que nadie entre de curioso durante el evento, no para proteger nada valioso. Si algún día hace falta de verdad, va por Deployment Protection de Vercel o por un backend.

El candado también funciona abierto con doble clic (`file://`), donde no existe `crypto.subtle`: hay un SHA-256 propio de respaldo.

Las 6 claves que guarda son `primer`, `segun`, `tercer`, `n8n`, `clerk` y `elevenlabs`.

### Premios

Los textos viven en el arreglo `DECK` de `src/template-ganadores.html`, cada premio con el logo de su patrocinador (`LOGOS_GANADORES` en `build.py`). Para cambiar un premio se edita ahí y se corre `python3 src/build.py`.
