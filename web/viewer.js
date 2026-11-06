import * as THREE from "three";
import { OrbitControls } from "./vendor/OrbitControls.js";

const COLORS = [
  0xd8ddd8, 0x9ab7a5, 0x65a6a6, 0x4c82a6,
  0x6e6aa6, 0xa05e8c, 0xbf665e, 0xd69a4a,
];
const RING_TONES = [0xf0e8da, 0xe7ddcc, 0xddd0bd, 0xd2c2ab, 0xc7b49a];
const DEFAULT_PLASTER = "#e8e4da";
// Los colores rotulan el nivel topologico inferido. La ALTURA no sale de ahi:
// viene calibrada contra la seccion medida (decision 0009) dentro del OBJ. El
// escenario 7/8 colorea la sensibilidad, no decide la cota. El acabado por
// defecto es yeso blanco: ningun pigmento se asigna a una pieza sin fuente.

const container = document.querySelector("#viewer");
const renderer = new THREE.WebGLRenderer({
  antialias: true,
  alpha: false,
  preserveDrawingBuffer: true,
});
renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
renderer.setSize(container.clientWidth, container.clientHeight);
renderer.setClearColor(0xe9e4da, 1);
renderer.shadowMap.enabled = true;
renderer.shadowMap.type = THREE.PCFShadowMap;
renderer.outputColorSpace = THREE.SRGBColorSpace;
renderer.toneMapping = THREE.ACESFilmicToneMapping;
renderer.toneMappingExposure = 1.08;
container.prepend(renderer.domElement);

const scene = new THREE.Scene();
scene.fog = new THREE.Fog(0xe9e4da, 14, 28);

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
controls.maxPolarAngle = Math.PI * 0.92;
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
  new THREE.MeshStandardMaterial({ color: 0xded9cf, roughness: 1 })
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
let colorMode = "plaster";
let plasterColor = DEFAULT_PLASTER;
let viewMode = "historical";
let syntheticOrder = 16;
let currentViewpoint = "overview";

// La geometria es la MISMA malla que exporta scripts/exportar_malla.py. No se
// reconstruye aqui: si el visor la levantara por su cuenta, la pagina y el OBJ
// derivarian sin que nada lo detectase.
const [levelsData, meshText, meshReport, syntheticData] = await Promise.all([
  fetchProjectJson("../datos/niveles_aproximados.json"),
  fetchProjectText("../renders/cupula_aproximada.obj"),
  fetchProjectJson("../datos/malla_cupula.json"),
  fetchProjectJson("../datos/ordenes_sinteticos.json"),
]);
const levels = new Map(levelsData.caras.map(face => [face.id, face]));
// La plantilla de cada cara y su procedencia: la ficha tiene que decir que el
// reparto entre bandas se DECIDIO (decision 0013), porque en el modelo no se
// distingue de lo documentado.
const templates = new Map(meshReport.caras.map(row => [row.id, row]));
const assignment = meshReport.modelo.asignacion;
const cells = parseObj(meshText);
const syntheticOrders = new Map(
  syntheticData.ordenes.map(row => [row.orden, row])
);

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

function rational([numerator, denominator]) {
  return numerator / denominator;
}

function steppedCellGeometry(points, top, bottom, scale = 0.76) {
  const positions = [];
  const point = (index, z) => [
    points[index][0] * scale,
    points[index][1] * scale,
    z * scale,
  ];
  const triangle = (a, b, c) => positions.push(...a, ...b, ...c);
  for (let i = 1; i < points.length - 1; i++) {
    triangle(point(0, top), point(i, top), point(i + 1, top));
    triangle(point(0, bottom), point(i + 1, bottom), point(i, bottom));
  }
  for (let i = 0; i < points.length; i++) {
    const next = (i + 1) % points.length;
    triangle(point(i, bottom), point(next, bottom), point(next, top));
    triangle(point(i, bottom), point(next, top), point(i, top));
  }
  const geometry = new THREE.BufferGeometry();
  geometry.setAttribute(
    "position",
    new THREE.BufferAttribute(new Float32Array(positions), 3)
  );
  geometry.computeVertexNormals();
  return geometry;
}

function clearModel() {
  for (const mesh of meshes) {
    mesh.material.dispose();
    if (mesh.userData.ownsGeometry) mesh.geometry.dispose();
    model.remove(mesh);
  }
  meshes = [];
  hovered = null;
}

function buildHistoricalModel() {
  for (const cell of cells) {
    const info = levels.get(cell.id);
    const level = scenario === 7 ? info.nivel : info.nivel_8;
    const uncertain = !info.estable_7_8;
    const analyticalColor = colorMode === "levels";
    const highlightUncertainty = analyticalColor && uncertain && showUncertainty;
    const color = analyticalColor
      ? new THREE.Color(COLORS[level])
      : new THREE.Color(plasterColor);
    if (highlightUncertainty) color.lerp(new THREE.Color(0xf0c85b), 0.28);
    const material = new THREE.MeshStandardMaterial({
      color,
      roughness: 0.72,
      metalness: 0.02,
      side: THREE.DoubleSide,
      transparent: highlightUncertainty,
      opacity: highlightUncertainty ? 0.80 : 1,
    });
    const mesh = new THREE.Mesh(cell.geometry, material);
    mesh.castShadow = true;
    mesh.receiveShadow = true;
    mesh.userData = {
      ...info,
      ...templates.get(cell.id),
      viewMode: "historical",
      level,
      uncertain,
    };
    model.add(mesh);
    meshes.push(mesh);
  }
}

function buildSyntheticModel() {
  const order = syntheticOrders.get(syntheticOrder);
  for (const cell of order.celdas) {
    const top = rational(cell.cota_superior);
    const bottom = rational(cell.cota_inferior);
    const geometry = steppedCellGeometry(cell.vertices_xy, top, bottom);
    const color = new THREE.Color(plasterColor).lerp(
      new THREE.Color(RING_TONES[cell.corona - 1]),
      0.48
    );
    if (cell.sector % 2 === 0) color.lerp(new THREE.Color(0xb7a891), 0.035);
    const material = new THREE.MeshStandardMaterial({
      color,
      roughness: 0.74,
      metalness: 0.01,
      side: THREE.DoubleSide,
    });
    const mesh = new THREE.Mesh(geometry, material);
    mesh.castShadow = true;
    mesh.receiveShadow = true;
    mesh.userData = {
      ...cell,
      viewMode: "synthetic",
      ownsGeometry: true,
      orden: order.orden,
      nombre: order.nombre,
      numeroSectores: order.numero_sectores,
      numeroCoronas: order.numero_coronas,
      angulo: order.angulo_celda_grados,
      top,
      bottom,
    };
    model.add(mesh);
    meshes.push(mesh);
  }
}

function buildModel() {
  clearModel();
  if (viewMode === "historical") buildHistoricalModel();
  else buildSyntheticModel();
}

function updateLegend() {
  const legend = document.querySelector("#legend-swatches");
  legend.replaceChildren();
  if (viewMode === "synthetic") {
    const order = syntheticOrders.get(syntheticOrder);
    document.querySelector("#legend-title").textContent = "Coronas";
    for (let i = 0; i < order.numero_coronas; i++) {
      const swatch = document.createElement("span");
      const color = new THREE.Color(plasterColor).lerp(
        new THREE.Color(RING_TONES[i]),
        0.48
      );
      swatch.className = "swatch ring";
      swatch.style.background = `#${color.getHexString()}`;
      swatch.textContent = i + 1;
      legend.append(swatch);
    }
    return;
  }
  if (colorMode === "plaster") {
    document.querySelector("#legend-title").textContent = "Acabado";
    const swatch = document.createElement("span");
    swatch.className = "swatch plaster";
    swatch.style.background = plasterColor;
    swatch.textContent = plasterColor === DEFAULT_PLASTER ? "yeso" : "tono";
    legend.append(swatch);
    return;
  }
  document.querySelector("#legend-title").textContent = "Nivel";
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
  if (viewMode === "synthetic") {
    const order = syntheticOrders.get(syntheticOrder);
    document.querySelector("#face-id").textContent = order.nombre;
    document.querySelector("#face-level").textContent =
      `${order.numero_coronas} coronas · ${order.numero_sectores} sectores · ${order.numero_celdas} paños`;
    document.querySelector("#face-status").textContent =
      `Composición comparativa contemporánea · abertura de ${order.angulo_celda_grados}° · unidades relativas`;
    return;
  }
  document.querySelector("#face-id").textContent = "Lectura general";
  document.querySelector("#face-level").textContent = "105 regiones de planta · seis bandas";
  const acabado = colorMode === "levels"
    ? `color analítico por nivel inferido 0–${scenario}`
    : plasterColor === DEFAULT_PLASTER
      ? "yeso blanco de obra nueva · sin pigmentos asignados"
      : "tono de visualización personalizado · sin atribución histórica";
  document.querySelector("#face-status").textContent =
    `Altura calibrada · ${acabado} · ` +
    `${assignment.caras_por_plantilla.menor} perfiles menores y ` +
    `${assignment.caras_por_plantilla.mayor} mayores; reparto propuesto`;
}

function setReadout(mesh) {
  const info = mesh.userData;
  if (info.viewMode === "synthetic") {
    document.querySelector("#face-id").textContent =
      `Corona ${info.corona} · sector ${info.sector} de ${info.numeroSectores}`;
    document.querySelector("#face-level").textContent =
      `${info.tipo} · cota relativa ${info.top.toFixed(2)}–${info.bottom.toFixed(2)}`;
    document.querySelector("#face-status").textContent =
      `Paño de una composición contemporánea · no atribuido a una fábrica histórica`;
    return;
  }
  document.querySelector("#face-id").textContent = `Región ${info.id}`;
  document.querySelector("#face-level").textContent =
    `Hilada ${info.hilada} · ${info.altura_m.toFixed(2)} m` +
    ` · banda ${info.capa_desde_borde} · plantilla ${info.plantilla}`;
  const acabado = colorMode === "levels"
    ? info.uncertain
      ? `Sensible: intervalo ${info.intervalo_nivel[0]}–${info.intervalo_nivel[1]}`
      : "Estable entre los escenarios 7 y 8"
    : plasterColor === DEFAULT_PLASTER
      ? "Yeso blanco de obra nueva · sin pigmentos asignados"
      : "Tono de visualización personalizado · sin atribución histórica";
  document.querySelector("#face-status").textContent =
    `${acabado} · perfil documentado; reparto por bandas propuesto en la decisión 0013`;
}

function updateColorControls() {
  const historical = viewMode === "historical";
  const analytical = colorMode === "levels";
  document.querySelector("#finish-control").hidden = !historical;
  document.querySelector("#order-control").hidden = historical;
  document.querySelector("#scenario-control").hidden = !(historical && analytical);
  document.querySelector("#uncertainty-control").hidden = !(historical && analytical);
  document.querySelector("#plaster-control").hidden = historical && analytical;
}

function updateViewCopy() {
  const synthetic = viewMode === "synthetic";
  document.querySelector("#view-title").textContent = synthetic
    ? "Tres familias de trazado"
    : "Cúpula de las Dos Hermanas";
  document.querySelector("#view-subtitle").textContent = synthetic
    ? "Comparación espacial contemporánea · ocho, diez y doce sectores"
    : "Hipótesis tridimensional · estado de la evidencia";
  document.querySelector("#context-kicker").textContent = synthetic
    ? "Comparación de trazados"
    : "Estado de la evidencia";
  document.querySelector("#context-copy").textContent = synthetic
    ? "Las tres cúpulas comparten cinco coronas y el mismo perfil. Solo cambia el ritmo angular, para que la comparación sea legible sin confundirla con una restitución."
    : "La planta procede de un dibujo publicado. Las cotas se calibran contra una sección medida; el reparto entre los dos perfiles es una hipótesis declarada.";
  document.querySelector("#method-copy").textContent = synthetic
    ? "Es una composición contemporánea en unidades relativas. No reproduce un edificio ni atribuye esta organización a un taller histórico. La planta se genera con geometría exacta; las coordenadas decimales solo sirven para dibujarla."
    : "Cada región conserva su procedencia. El modelo aproxima seis bandas, no las 23 hiladas de la fábrica, y no constituye una restitución histórica verificada.";
  document.querySelector("#scope-note").textContent = synthetic
    ? "Comparación contemporánea · no reproduce un monumento histórico"
    : "Modelo de trabajo · no es una restitución histórica verificada";
  container.setAttribute(
    "aria-label",
    synthetic
      ? "Comparación tridimensional de tres familias contemporáneas de trazado"
      : "Modelo tridimensional interpretativo de la cúpula de las Dos Hermanas"
  );
}

function frameCurrentView() {
  const intrados = currentViewpoint === "intrados";
  ground.visible = !intrados;
  if (viewMode === "synthetic") {
    controls.minDistance = 5;
    controls.maxDistance = 22;
    camera.position.set(7.6, -9.0, intrados ? -4.4 : 7.0);
    controls.target.set(0, 0, 2.15);
  } else {
    controls.minDistance = 7;
    controls.maxDistance = 24;
    camera.position.set(9.5, -10.5, intrados ? -4.8 : 9.2);
    controls.target.set(0, 0, intrados ? 2.2 : 1.7);
  }
  controls.update();
}

function setViewpoint(viewpoint) {
  currentViewpoint = viewpoint;
  document.querySelectorAll("[data-viewpoint]").forEach(button => {
    const active = button.dataset.viewpoint === viewpoint;
    button.classList.toggle("active", active);
    button.setAttribute("aria-pressed", String(active));
  });
  frameCurrentView();
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
document.querySelector("#view-mode").addEventListener("change", event => {
  viewMode = event.target.value;
  updateColorControls();
  updateViewCopy();
  buildModel();
  updateLegend();
  resetReadout();
  setViewpoint("overview");
});
document.querySelector("#synthetic-order").addEventListener("change", event => {
  syntheticOrder = Number(event.target.value);
  buildModel();
  updateLegend();
  resetReadout();
});
document.querySelector("#color-mode").addEventListener("change", event => {
  colorMode = event.target.value;
  updateColorControls();
  buildModel();
  updateLegend();
  resetReadout();
});
document.querySelector("#plaster-color").addEventListener("input", event => {
  plasterColor = event.target.value.toLowerCase();
  buildModel();
  updateLegend();
  resetReadout();
});
document.querySelector("#autorotate").addEventListener("change", event => {
  controls.autoRotate = event.target.checked;
  controls.autoRotateSpeed = 0.75;
});
document.querySelectorAll("[data-viewpoint]").forEach(button => {
  button.addEventListener("click", () => setViewpoint(button.dataset.viewpoint));
});
document.querySelector("#reset").addEventListener("click", () => {
  frameCurrentView();
});

window.addEventListener("resize", () => {
  const width = container.clientWidth;
  const height = container.clientHeight;
  camera.aspect = width / height;
  camera.updateProjectionMatrix();
  renderer.setSize(width, height);
});

buildModel();
updateColorControls();
updateViewCopy();
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
