import * as THREE from "three";
import { OrbitControls } from "./vendor/OrbitControls.js";

const COLORS = [
  0xd8ddd8, 0x9ab7a5, 0x65a6a6, 0x4c82a6,
  0x6e6aa6, 0xa05e8c, 0xbf665e, 0xd69a4a,
];
// Los colores rotulan el nivel topologico inferido. La ALTURA no sale de ahi:
// viene calibrada contra la seccion medida (decision 0009) dentro del OBJ. El
// escenario 7/8 colorea la sensibilidad, no decide la cota.

const container = document.querySelector("#viewer");
const renderer = new THREE.WebGLRenderer({
  antialias: true,
  alpha: false,
  preserveDrawingBuffer: true,
});
renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
renderer.setSize(container.clientWidth, container.clientHeight);
renderer.setClearColor(0xecece8, 1);
renderer.shadowMap.enabled = true;
renderer.shadowMap.type = THREE.PCFShadowMap;
renderer.outputColorSpace = THREE.SRGBColorSpace;
container.prepend(renderer.domElement);

const scene = new THREE.Scene();
scene.fog = new THREE.Fog(0xecece8, 12, 24);

const camera = new THREE.PerspectiveCamera(
  38, container.clientWidth / container.clientHeight, 0.1, 60
);
camera.up.set(0, 0, 1);
camera.position.set(9.5, -10.5, 9.2);

const controls = new OrbitControls(camera, renderer.domElement);
controls.enableDamping = true;
controls.dampingFactor = 0.06;
controls.minDistance = 7;
controls.maxDistance = 24;
controls.maxPolarAngle = Math.PI * 0.49;
controls.target.set(0, 0, 1.7);

scene.add(new THREE.HemisphereLight(0xf8faf7, 0x6f7773, 2.1));
const key = new THREE.DirectionalLight(0xffffff, 3.3);
key.position.set(-5, -7, 12);
key.castShadow = true;
key.shadow.mapSize.set(2048, 2048);
key.shadow.camera.left = -8;
key.shadow.camera.right = 8;
key.shadow.camera.top = 8;
key.shadow.camera.bottom = -8;
scene.add(key);
const fill = new THREE.DirectionalLight(0xb8d5d0, 1.2);
fill.position.set(8, 4, 5);
scene.add(fill);

const ground = new THREE.Mesh(
  new THREE.CircleGeometry(6.2, 96),
  new THREE.MeshStandardMaterial({ color: 0xdfe1dc, roughness: 1 })
);
ground.receiveShadow = true;
ground.position.z = -0.035;
scene.add(ground);

const model = new THREE.Group();
scene.add(model);
const raycaster = new THREE.Raycaster();
const pointer = new THREE.Vector2(2, 2);
let meshes = [];
let hovered = null;
let scenario = 7;
let showUncertainty = true;

// La geometria es la MISMA malla que exporta scripts/exportar_malla.py. No se
// reconstruye aqui: si el visor la levantara por su cuenta, la pagina y el OBJ
// derivarian sin que nada lo detectase.
const [levelsData, meshText] = await Promise.all([
  fetchProjectJson("../datos/niveles_aproximados.json"),
  fetchProjectText("../renders/cupula_aproximada.obj"),
]);
const levels = new Map(levelsData.caras.map(face => [face.id, face]));
const cells = parseObj(meshText);

function checkResponse(response) {
  if (!response.ok) throw new Error(`${response.status} ${response.url}`);
  return response;
}

async function fetchProjectText(url) {
  return (checkResponse(await fetch(url))).text();
}

/** Lee el OBJ: vertices globales y un grupo de triangulos por cara. */
function parseObj(text) {
  const positions = [];
  const groups = [];
  let current = null;
  for (const line of text.split("\n")) {
    if (line.startsWith("v ")) {
      const [x, y, z] = line.slice(2).trim().split(/\s+/).map(Number);
      positions.push([x, y, z]);
    } else if (line.startsWith("o ")) {
      current = { id: line.slice(2).trim().replace(/^cara_/, ""), indices: [] };
      groups.push(current);
    } else if (line.startsWith("f ") && current) {
      for (const token of line.slice(2).trim().split(/\s+/)) {
        current.indices.push(Number(token.split("/")[0]) - 1);
      }
    }
  }
  return groups.map(group => {
    const array = new Float32Array(group.indices.length * 3);
    group.indices.forEach((index, slot) => {
      const [x, y, z] = positions[index];
      // La escena es Z arriba, como el OBJ. Solo se invierte Y, igual que hacia
      // el levantado anterior con shape.moveTo(x, -y).
      array[slot * 3] = x;
      array[slot * 3 + 1] = -y;
      array[slot * 3 + 2] = z;
    });
    const geometry = new THREE.BufferGeometry();
    geometry.setAttribute("position", new THREE.BufferAttribute(array, 3));
    geometry.computeVertexNormals();
    return { id: group.id, geometry };
  });
}

async function fetchProjectJson(url) {
  const response = checkResponse(await fetch(url));
  const text = await response.text();
  return JSON.parse(text.replace(/\b(?:NaN|-?Infinity)\b/g, "null"));
}

function buildModel() {
  for (const mesh of meshes) {
    // La geometria se reutiliza entre reconstrucciones; solo cambia el material.
    mesh.material.dispose();
    model.remove(mesh);
  }
  meshes = [];

  for (const cell of cells) {
    const info = levels.get(cell.id);
    const level = scenario === 7 ? info.nivel : info.nivel_8;
    const uncertain = !info.estable_7_8;
    const color = new THREE.Color(COLORS[level]);
    if (uncertain && showUncertainty) color.lerp(new THREE.Color(0xf0c85b), 0.28);
    const material = new THREE.MeshStandardMaterial({
      color,
      roughness: 0.72,
      metalness: 0.02,
      side: THREE.DoubleSide,
      transparent: uncertain && showUncertainty,
      opacity: uncertain && showUncertainty ? 0.80 : 1,
    });
    const mesh = new THREE.Mesh(cell.geometry, material);
    mesh.castShadow = true;
    mesh.receiveShadow = true;
    mesh.userData = { ...info, level, uncertain };
    model.add(mesh);
    meshes.push(mesh);
  }
}

function updateLegend() {
  const legend = document.querySelector("#legend-swatches");
  legend.replaceChildren();
  const max = scenario;
  for (let i = 0; i <= max; i++) {
    const swatch = document.createElement("span");
    swatch.className = "swatch";
    swatch.style.background = `#${new THREE.Color(COLORS[Math.min(i, 7)]).getHexString()}`;
    swatch.textContent = i;
    legend.append(swatch);
  }
}

function resetReadout() {
  document.querySelector("#face-id").textContent = "Modelo completo";
  document.querySelector("#face-level").textContent = "105 caras · 227 vecindades";
  document.querySelector("#face-status").textContent =
    `105 celdas · alturas calibradas · color por nivel inferido 0–${scenario}`;
}

function setReadout(mesh) {
  const info = mesh.userData;
  document.querySelector("#face-id").textContent = info.id;
  document.querySelector("#face-level").textContent =
    `Hilada ${info.hilada} · ${info.altura_m.toFixed(2)} m · banda ${info.capa_desde_borde}`;
  document.querySelector("#face-status").textContent = info.uncertain
    ? `Sensible: intervalo ${info.intervalo_nivel[0]}–${info.intervalo_nivel[1]}`
    : "Estable entre los escenarios 7 y 8";
}

renderer.domElement.addEventListener("pointermove", event => {
  const rect = renderer.domElement.getBoundingClientRect();
  pointer.x = ((event.clientX - rect.left) / rect.width) * 2 - 1;
  pointer.y = -((event.clientY - rect.top) / rect.height) * 2 + 1;
});
renderer.domElement.addEventListener("pointerleave", () => pointer.set(2, 2));

document.querySelectorAll("[data-scenario]").forEach(button => {
  button.addEventListener("click", () => {
    scenario = Number(button.dataset.scenario);
    document.querySelectorAll("[data-scenario]").forEach(candidate => {
      const active = candidate === button;
      candidate.classList.toggle("active", active);
      candidate.setAttribute("aria-pressed", String(active));
    });
    buildModel();
    updateLegend();
    resetReadout();
  });
});

document.querySelector("#uncertainty").addEventListener("change", event => {
  showUncertainty = event.target.checked;
  buildModel();
});
document.querySelector("#autorotate").addEventListener("change", event => {
  controls.autoRotate = event.target.checked;
  controls.autoRotateSpeed = 0.75;
});
document.querySelector("#reset").addEventListener("click", () => {
  camera.position.set(9.5, -10.5, 9.2);
  controls.target.set(0, 0, 1.7);
  controls.update();
});

window.addEventListener("resize", () => {
  const width = container.clientWidth;
  const height = container.clientHeight;
  camera.aspect = width / height;
  camera.updateProjectionMatrix();
  renderer.setSize(width, height);
});

buildModel();
updateLegend();
resetReadout();
document.querySelector("#loading").classList.add("done");

function animate() {
  requestAnimationFrame(animate);
  controls.update();
  raycaster.setFromCamera(pointer, camera);
  const hit = raycaster.intersectObjects(meshes, false)[0]?.object ?? null;
  if (hit !== hovered) {
    if (hovered) hovered.scale.setScalar(1);
    hovered = hit;
    if (hovered) {
      hovered.scale.setScalar(1.012);
      setReadout(hovered);
      renderer.domElement.style.cursor = "crosshair";
    } else {
      resetReadout();
      renderer.domElement.style.cursor = "grab";
    }
  }
  renderer.render(scene, camera);
}
animate();
