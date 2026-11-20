import * as THREE from "three";
import { OrbitControls } from "./vendor/OrbitControls.js";
import { GLTFLoader } from "./vendor/loaders/GLTFLoader.js";
import { iluminar, aplicarYeseria } from "./yeseria.js";

const canvas = document.querySelector("canvas");
const estado = document.querySelector("#carga");

async function cargar(url) {
  const respuesta = await fetch(url);
  if (!respuesta.ok) throw new Error(`${respuesta.status} · ${url}`);
  return respuesta;
}

async function visita() {
  const renderer = new THREE.WebGLRenderer({ canvas, antialias: true, powerPreference: "high-performance" });
  renderer.setPixelRatio(Math.min(window.devicePixelRatio, 1.75));
  renderer.setClearColor(0x292623);
  renderer.toneMapping = THREE.ACESFilmicToneMapping;
  const scene = new THREE.Scene();
  const camera = new THREE.PerspectiveCamera(46, 1, 0.005, 60);
  const controls = new OrbitControls(camera, canvas);
  controls.minDistance = 0.12;
  controls.maxDistance = 24;
  iluminar(scene);
  const [ficha, archivo] = await Promise.all([
    cargar("modelos/dos-hermanas.json").then(r => r.json()),
    cargar("modelos/dos-hermanas.glb.gz").then(r => r.arrayBuffer()),
  ]);
  // Algunos servidores descomprimen al enviar, otros sirven el gzip tal cual.
  const comprimido = new Uint8Array(archivo)[0] === 0x1f;
  const glb = comprimido ? await new Response(new Blob([archivo]).stream()
    .pipeThrough(new DecompressionStream("gzip"))).arrayBuffer() : archivo;
  const { scene: modelo } = await new GLTFLoader().parseAsync(glb, "");
  await aplicarYeseria(modelo, renderer);
  scene.add(modelo);
  modelo.updateMatrixWorld(true);
  const cupulin = modelo.getObjectByName("cupulin_00");
  const raycaster = new THREE.Raycaster();
  const origen = new THREE.Vector3(0, ficha.suelo_m + 1.6, 0.8);
  const centro = new THREE.Vector3(0, 2, 0);
  const dibujar = () => renderer.render(scene, camera);
  controls.addEventListener("change", dibujar);

  function inicio() {
    camera.position.copy(origen);
    controls.target.copy(centro);
    controls.update();
  }
  // Encuadre del paño +X en coordenadas del visor (Y vertical).
  function verHiladas() {
    camera.position.set(1.75, -1.38, -0.48);
    controls.target.set(ficha.sector_00.apotema_m - 0.16, -0.26, -0.30);
    controls.update();
  }
  function enfocar(punto, distancia) {
    const direccion = camera.position.clone().sub(punto).normalize();
    camera.position.copy(punto).addScaledVector(direccion, distancia);
    controls.target.copy(punto);
    controls.update();
  }
  function acercar(factor) {
    const distancia = THREE.MathUtils.clamp(camera.position.distanceTo(controls.target) * factor,
      controls.minDistance, controls.maxDistance);
    enfocar(controls.target, distancia);
  }
  function enfocarEnPantalla(x, y) {
    const rect = canvas.getBoundingClientRect();
    raycaster.setFromCamera(new THREE.Vector2(
      2 * (x - rect.left) / rect.width - 1, 1 - 2 * (y - rect.top) / rect.height), camera);
    const impacto = raycaster.intersectObject(modelo)[0];
    if (impacto) enfocar(impacto.point, THREE.MathUtils.clamp(impacto.distance, 0.12, 0.8));
  }
  // El mismo gesto con ratón o dedo. Arrastrar y pellizcar no eligen pieza.
  const dedos = new Set();
  let toque;
  canvas.addEventListener("pointerdown", e => {
    dedos.add(e.pointerId);
    toque = dedos.size === 1 && e.button === 0 ? [e.clientX, e.clientY] : null;
  });
  canvas.addEventListener("pointermove", e => {
    if (toque && Math.hypot(e.clientX - toque[0], e.clientY - toque[1]) > 6) toque = null;
  });
  canvas.addEventListener("pointercancel", e => { dedos.delete(e.pointerId); toque = null; });
  canvas.addEventListener("pointerup", e => {
    dedos.delete(e.pointerId);
    if (toque && !dedos.size) enfocarEnPantalla(e.clientX, e.clientY);
    toque = null;
  });
  document.querySelector("#inicio").onclick = inicio;
  document.querySelector("#hiladas").onclick = verHiladas;
  document.querySelector("#acercar").onclick = () => acercar(0.65);
  document.querySelector("#alejar").onclick = () => acercar(1 / 0.65);
  document.querySelector("#cupulin").onclick = () => {
    inicio();
    const punto = new THREE.Box3().setFromObject(cupulin).getCenter(new THREE.Vector3());
    enfocar(punto, 1.8);
  };
  function ajustar() {
    const { clientWidth: w, clientHeight: h } = canvas;
    camera.aspect = w / h;
    // Al abrir en vertical, conservar la anchura de la bóveda en el encuadre.
    camera.fov = THREE.MathUtils.radToDeg(2 * Math.atan(Math.tan(THREE.MathUtils.degToRad(23)) /
      Math.min(1, camera.aspect)));
    camera.updateProjectionMatrix();
    renderer.setSize(w, h, false);
    dibujar();
  }
  inicio();
  if (location.hash === "#hiladas" && ficha.sector_00) verHiladas();
  ajustar();
  new ResizeObserver(ajustar).observe(canvas);
  document.querySelectorAll("button").forEach(b => { b.disabled = false; });
  document.querySelector("#cupulin").disabled = !cupulin;
  document.querySelector("#hiladas").disabled = !ficha.sector_00;
  estado.hidden = true;
}

visita().catch(error => {
  console.error(error);
  estado.textContent = "No se pudo abrir la visita 3D. Comprueba la conexión y que el navegador admite WebGL 2.";
});
