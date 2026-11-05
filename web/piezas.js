import * as THREE from "three";
import { OrbitControls } from "./vendor/OrbitControls.js";

// Muestra las mismas mallas que exportan scripts/render_piezas.py y
// scripts/render_hilada.py. No reconstruye geometria por su cuenta.
const ESCENAS = {
  piezas: {
    url: "../renders/piezas_alfabeto.obj",
    subtitulo: "Las siete piezas de la lámina X",
    camara: [0, 11, 3.2], objetivo: [0, 0, 1.6],
  },
  hilada: {
    url: "../renders/hilada_a1a2.obj",
    subtitulo: "Una hilada: 64 piezas A1 y A2 alternas",
    camara: [0, -2.5, -4.5], objetivo: [0, 4, 1.6],
  },
  cupula: {
    url: "../renders/cupula_piezas.obj",
    subtitulo: "18 hiladas, 1792 piezas, sobre el cono medido",
    camara: [0, -6, -14], objetivo: [0, 0, 9],
  },
};
const ARISTA = Math.cos(THREE.MathUtils.degToRad(35));

const container = document.querySelector("#viewer");
const renderer = new THREE.WebGLRenderer({ antialias: true });
renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
renderer.setSize(container.clientWidth, container.clientHeight);
renderer.setClearColor(0x1c1a19, 1);
renderer.outputColorSpace = THREE.SRGBColorSpace;
container.prepend(renderer.domElement);

const scene = new THREE.Scene();
const camera = new THREE.PerspectiveCamera(45, container.clientWidth / container.clientHeight, 0.05, 200);
camera.up.set(0, 0, 1);
const controls = new OrbitControls(camera, renderer.domElement);
controls.enableDamping = true;
controls.dampingFactor = 0.07;

scene.add(new THREE.HemisphereLight(0xfff6e8, 0x3a3430, 1.4));
const key = new THREE.DirectionalLight(0xfff1dc, 2.4);
// Luz de las ventanas del tambor: de lado y desde abajo.
key.position.set(-4, 6, -5);
scene.add(key);
const fill = new THREE.DirectionalLight(0xd8e2ff, 0.8);
fill.position.set(5, -3, 6);
scene.add(fill);

const material = new THREE.MeshStandardMaterial({
  color: 0xeee4d2, roughness: 0.85, metalness: 0, side: THREE.DoubleSide,
});
const modelo = new THREE.Group();
scene.add(modelo);
const cache = new Map();

/** Lee el OBJ y devuelve una geometria por grupo, con normales de arista. */
function leerObj(texto) {
  const v = [];
  const grupos = [];
  let actual = null;
  for (const linea of texto.split("\n")) {
    if (linea.startsWith("v ")) v.push(linea.slice(2).trim().split(/\s+/).map(Number));
    else if (linea.startsWith("g ")) grupos.push(actual = { caras: [] });
    else if (linea.startsWith("f ") && actual) {
      actual.caras.push(linea.slice(2).trim().split(/\s+/).map(t => Number(t.split("/")[0]) - 1));
    }
  }
  return grupos.map(g => geometria(v, g.caras));
}

function geometria(v, caras) {
  const n = caras.length;
  const pos = new Float32Array(n * 9);
  const nor = new Float32Array(n * 9);
  const normal = [];
  const porVertice = new Map();
  caras.forEach((f, i) => {
    const [a, b, c] = f.map(k => new THREE.Vector3(...v[k]));
    const m = new THREE.Vector3().crossVectors(b.clone().sub(a), c.clone().sub(a));
    normal.push(m);
    f.forEach((k, j) => {
      pos.set(v[k], i * 9 + j * 3);
      if (!porVertice.has(k)) porVertice.set(k, []);
      porVertice.get(k).push(i);
    });
  });
  const unidad = normal.map(m => m.clone().normalize());
  caras.forEach((f, i) => {
    f.forEach((k, j) => {
      const s = new THREE.Vector3();
      for (const g of porVertice.get(k)) {
        if (unidad[g].dot(unidad[i]) > ARISTA) s.add(normal[g]);
      }
      s.normalize();
      nor.set([s.x, s.y, s.z], i * 9 + j * 3);
    });
  });
  const geo = new THREE.BufferGeometry();
  geo.setAttribute("position", new THREE.BufferAttribute(pos, 3));
  geo.setAttribute("normal", new THREE.BufferAttribute(nor, 3));
  return geo;
}

async function mostrar(nombre) {
  const escena = ESCENAS[nombre];
  const carga = document.querySelector("#loading");
  carga.classList.remove("done");
  if (!cache.has(nombre)) {
    const r = await fetch(escena.url);
    if (!r.ok) throw new Error(`${r.status} ${r.url}`);
    cache.set(nombre, leerObj(await r.text()));
  }
  modelo.clear();
  for (const geo of cache.get(nombre)) modelo.add(new THREE.Mesh(geo, material));
  document.querySelector("#subtitulo").textContent = escena.subtitulo;
  document.querySelectorAll("[data-escena]").forEach(b => {
    const activo = b.dataset.escena === nombre;
    b.classList.toggle("active", activo);
    b.setAttribute("aria-pressed", String(activo));
  });
  encuadrar(escena);
  carga.classList.add("done");
}

let escenaActual = "piezas";
function encuadrar(escena) {
  camera.position.set(...escena.camara);
  controls.target.set(...escena.objetivo);
  controls.update();
}

document.querySelectorAll("[data-escena]").forEach(b =>
  b.addEventListener("click", () => mostrar(escenaActual = b.dataset.escena)));
document.querySelector("#reset").addEventListener("click", () => encuadrar(ESCENAS[escenaActual]));
document.querySelector("#autorotate").addEventListener("change", e => {
  controls.autoRotate = e.target.checked;
});
window.addEventListener("resize", () => {
  camera.aspect = container.clientWidth / container.clientHeight;
  camera.updateProjectionMatrix();
  renderer.setSize(container.clientWidth, container.clientHeight);
});

await mostrar("piezas");
renderer.setAnimationLoop(() => {
  controls.update();
  renderer.render(scene, camera);
});
