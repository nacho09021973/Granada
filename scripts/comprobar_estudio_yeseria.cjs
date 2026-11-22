// Comprueba la revisión del encuadre: imágenes, deslizador y consola.
const assert = require("node:assert/strict");
const { createHash } = require("node:crypto");
const puppeteer = require("puppeteer-core");

async function main() {
  const navegador = await puppeteer.launch({executablePath: process.env.CHROME_PATH, headless: true});
  try {
    const pagina = await navegador.newPage();
    const errores = [];
    pagina.on("pageerror", e => errores.push(e.message));
    pagina.on("response", r => { if (r.status() >= 400 && !r.url().endsWith("favicon.ico")) errores.push(r.url()); });
    await pagina.setViewport({width: 1200, height: 1000});
    await pagina.goto(process.argv[2] || "http://127.0.0.1:8765/web/estudio-yeseria.html");
    await pagina.waitForFunction(() => [...document.images].every(im => im.complete && im.naturalWidth > 0));
    const zona = await pagina.$("#comparador");
    const hash = async () => createHash("sha256").update(await zona.screenshot()).digest("hex");
    async function extremo(valor) {
      await pagina.$eval("#corte", (e, v) => { e.value = v; e.dispatchEvent(new Event("input")); }, valor);
      return hash();
    }
    assert.notEqual(await extremo("0"), await extremo("100"), "el deslizador cambia la imagen dentro del encuadre");
    await pagina.setViewport({width: 390, height: 844});
    assert.ok(await pagina.$eval("#corte", e => e.getBoundingClientRect().height >= 44));
    assert.ok(await pagina.evaluate(() => document.documentElement.scrollWidth <= innerWidth));
    assert.deepEqual(errores, []);
    console.log("OK · imágenes, comparación, controles y ancho móvil");
  } finally { await navegador.close(); }
}
main().catch(e => { console.error(e); process.exitCode = 1; });
