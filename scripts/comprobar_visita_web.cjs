// Con el servidor local en marcha. Dependencias de prueba: puppeteer-core,
// @sparticuz/chromium para Linux o CHROME_PATH para otro Chrome instalado.
const assert = require("node:assert/strict");
const { createHash } = require("node:crypto");
const { mkdirSync } = require("node:fs");
const path = require("node:path");
const puppeteer = require("puppeteer-core");

async function main() {
  const chrome = process.env.CHROME_PATH ? null : require("@sparticuz/chromium").default;
  const navegador = await puppeteer.launch({
    executablePath: process.env.CHROME_PATH || await chrome.executablePath(),
    headless: true,
    args: chrome ? chrome.args : [],
  });
  try {
    const pagina = await navegador.newPage();
    // Para cotejar geometrías con la misma cámara, el cuarto argumento puede
    // indicar el GLB anterior. La ficha y el visor son los del encuadre actual.
    const control = process.argv[4];
    if (control) {
      const archivo = new URL(control);
      await pagina.setRequestInterception(true);
      pagina.on("request", peticion => peticion.continue(
        peticion.url().endsWith("/modelos/dos-hermanas.glb.gz") ? {url: archivo.href} : {}
      ));
    }
    const errores = [];
    pagina.on("pageerror", e => errores.push(e.message));
    pagina.on("console", e => {
      if (e.type() === "error" && !e.location().url?.endsWith("favicon.ico")) errores.push(e.text());
    });
    pagina.on("response", r => { if (r.status() >= 400 && !r.url().endsWith("favicon.ico")) errores.push(r.url()); });
    await pagina.setViewport({width: 900, height: 740});
    await pagina.goto(process.argv[2] || "http://127.0.0.1:8765/web/visita.html");
    await pagina.waitForSelector("#carga[hidden]", {timeout: 120000});
    const destino = path.resolve(process.argv[3] || "renders/previas");
    mkdirSync(destino, {recursive: true});
    const imagen = async (nombre) => {
      const captura = await pagina.screenshot({
        clip: {x: 160, y: 140, width: 580, height: 380},
        path: nombre && path.join(destino, nombre),
      });
      return createHash("sha256").update(captura).digest("hex");
    };
    const entradaHiladas = new URL(pagina.url()).hash === "#hiladas" ? await imagen() : null;
    if (entradaHiladas) await pagina.click("#inicio");
    const general = await imagen("web_3d_sala.png");
    await pagina.mouse.click(420, 340);
    const pieza = await imagen("web_3d_pieza.png");
    assert.notEqual(pieza, general, "elegir una pieza acerca la cámara");
    await pagina.mouse.wheel({deltaY: -140});
    const cerca = await imagen();
    assert.notEqual(cerca, pieza, "la rueda cambia el encuadre de la pieza");
    await pagina.mouse.move(410, 350);
    await pagina.mouse.down();
    await pagina.mouse.move(475, 375, {steps: 6});
    await pagina.mouse.up();
    assert.notEqual(await imagen(), cerca, "arrastrar cambia la perspectiva");
    await pagina.click("#inicio");
    assert.equal(await imagen(), general, "volver a la sala recupera la cámara");
    await pagina.click("#cupulin");
    assert.notEqual(await imagen("web_3d_cupulin.png"), general, "cupulín accesible");
    await pagina.mouse.move(440, 375);
    await pagina.mouse.down();
    await pagina.mouse.move(477, 361, {steps: 5});
    await pagina.mouse.up();
    await imagen("web_3d_cupulin_oblicuo.png");
    await pagina.screenshot({path: path.join(destino, "web_3d_cupulin_entorno.png")});
    if (await pagina.$("#hiladas")) {
      assert.ok(await pagina.$("#hiladas:not([disabled])"), "el modelo carga las hiladas");
      await pagina.click("#hiladas");
      const pano = await imagen("web_3d_hiladas.png");
      if (entradaHiladas) assert.equal(pano, entradaHiladas, "enlace directo al mismo paño");
      await pagina.screenshot({path: path.join(destino, "web_3d_pano.png")});
      assert.notEqual(pano, general, "el acceso a las hiladas encuadra los dos vanos");
      await pagina.mouse.move(460, 360);
      await pagina.mouse.down();
      await pagina.mouse.move(493, 349, {steps: 6});
      await pagina.mouse.up();
      assert.notEqual(await imagen("web_3d_hiladas_lateral.png"), pano);
      await pagina.click("#acercar");
      await imagen("web_3d_hiladas_detalle.png");
    }
    await pagina.setViewport({width: 390, height: 844, isMobile: true, hasTouch: true});
    await pagina.waitForSelector("#carga[hidden]", {timeout: 120000});
    await pagina.click("#inicio");
    async function movil() {
      return createHash("sha256").update(await pagina.screenshot({
        clip: {x: 12, y: 150, width: 350, height: 480},
      })).digest("hex");
    }
    const inicioMovil = await movil();
    await pagina.touchscreen.tap(195, 400);
    const tactil = await movil();
    assert.notEqual(tactil, inicioMovil, "toque sobre la bóveda en pantalla vertical");
    await pagina.tap("#acercar");
    assert.notEqual(await movil(), tactil, "acercamiento táctil");
    const antesPellizco = await movil();
    const sesion = await pagina.createCDPSession();
    for (const [type, dx] of [["touchStart", 35], ["touchMove", 55], ["touchMove", 72]]) {
      await sesion.send("Input.dispatchTouchEvent", {type, touchPoints: [
        {x: 195 - dx, y: 380, id: 0}, {x: 195 + dx, y: 380, id: 1},
      ]});
    }
    await sesion.send("Input.dispatchTouchEvent", {type: "touchEnd", touchPoints: []});
    assert.notEqual(await movil(), antesPellizco, "el pellizco amplía la malla");
    assert.deepEqual(errores, []);
    console.log("OK · sala, selección, zoom, órbita, retorno y controles táctiles");
  } finally {
    await navegador.close();
  }
}
main().catch(e => { console.error(e); process.exitCode = 1; });
