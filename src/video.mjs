/**
 * Renderiza video.html a MP4, cuadro por cuadro.
 *
 *   python3 src/build.py
 *   node src/video.mjs            → video-gracias.mp4 (1080x1350, 30 fps)
 *
 * Necesita ffmpeg y el paquete `playwright` (npm i -D playwright). Usa el
 * Chrome instalado en la Mac, así que no hace falta bajar navegadores.
 */
import { spawn } from "child_process";
import { mkdtempSync, rmSync } from "fs";
import { tmpdir } from "os";
import path from "path";
import { fileURLToPath, pathToFileURL } from "url";
import { chromium } from "playwright";

const ROOT = path.dirname(path.dirname(fileURLToPath(import.meta.url)));
const FPS = 30;
const SALIDA = path.join(ROOT, process.argv[2] ?? "video-gracias.mp4");
const CHROME = process.env.CHROME ?? "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome";

const tmp = mkdtempSync(path.join(tmpdir(), "video-gracias-"));
const browser = await chromium.launch({ executablePath: CHROME });
const page = await browser.newPage({ viewport: { width: 1080, height: 1350 } });
await page.goto(pathToFileURL(path.join(ROOT, "video.html")).href + "?render");
await page.evaluate(() => document.fonts.ready);
const frame = page.locator("#frame");

const dur = await page.evaluate(() => window.DUR);
const total = Math.round(dur * FPS);
for (let n = 0; n < total; n++) {
  await page.evaluate((t) => window.draw(t), n / FPS);
  await frame.screenshot({ path: path.join(tmp, `${String(n).padStart(5, "0")}.png`) });
  if (n % FPS === 0) process.stdout.write(`\r${Math.round((n / total) * 100)}%`);
}
await browser.close();
process.stdout.write("\r100%\n");

// H.264 + pista de audio en silencio: Instagram y LinkedIn aceptan mejor
// un MP4 con audio, y así se le puede poner música encima al publicar.
await new Promise((ok, mal) => {
  const ff = spawn("ffmpeg", [
    "-y", "-loglevel", "error",
    "-framerate", String(FPS), "-i", path.join(tmp, "%05d.png"),
    "-f", "lavfi", "-i", "anullsrc=channel_layout=stereo:sample_rate=44100",
    "-shortest", "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "16", "-preset", "slow",
    "-c:a", "aac", "-movflags", "+faststart", SALIDA,
  ], { stdio: "inherit" });
  ff.on("exit", (c) => (c === 0 ? ok() : mal(new Error(`ffmpeg ${c}`))));
});
rmSync(tmp, { recursive: true, force: true });
console.log(`listo: ${SALIDA}`);
