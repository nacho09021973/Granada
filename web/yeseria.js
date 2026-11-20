import * as THREE from "three";

// Entorno de reflexión de la sala en HDR lineal. La luz más intensa se concentra
// a la altura de las ventanas del tambor. La iluminación es una elección de escena.
function reflejosDelTambor() {
  const w = 256, h = 128;
  const pixels = new Float32Array(w * h * 4);
  for (let j = 0; j < h; j++) {
    const elevacion = ((j + 0.5) / h - 0.5) * Math.PI;
    for (let i = 0; i < w; i++) {
      const azimut = ((i + 0.5) / w - 0.5) * 2 * Math.PI;
      const sector = azimut - Math.round(azimut / (Math.PI / 4)) * Math.PI / 4;
      const ventana = Math.exp(-Math.pow((Math.abs(sector) - 0.14) / 0.065, 4)
        - Math.pow((elevacion + 0.44) / 0.13, 4));
      const rebote = 0.14 + 0.18 * Math.max(0, -Math.sin(elevacion));
      const dia = ventana * (2.4 + 1.6 * Math.cos(azimut + 0.8));
      pixels.set([rebote * 1.07 + dia, rebote + dia * 0.97, rebote * 0.9 + dia * 0.90, 1],
        4 * (j * w + i));
    }
  }
  const env = new THREE.DataTexture(pixels, w, h, THREE.RGBAFormat, THREE.FloatType);
  env.mapping = THREE.EquirectangularReflectionMapping;
  env.needsUpdate = true;
  return env;
}

export function iluminar(scene) {
  scene.environment = reflejosDelTambor();
  scene.environmentIntensity = 0.85;
  scene.add(new THREE.HemisphereLight(0xc7d0d6, 0xf4e9d9, 0.48));
  for (const [position, color, power] of [
    [[-4, -1.5, 2.2], 0xffefdc, 2.35],
    [[3.5, -1, -2.8], 0xdfedff, 0.62],
  ]) {
    const light = new THREE.DirectionalLight(color, power);
    light.position.set(...position);
    scene.add(light);
  }
}

export async function aplicarYeseria(modelo, renderer) {
  const tile = await new THREE.TextureLoader().loadAsync("modelos/yeso.png");
  tile.wrapS = tile.wrapT = THREE.RepeatWrapping;
  tile.anisotropy = Math.min(renderer.capabilities.getMaxAnisotropy(), 8);
  const materiales = new Set();
  modelo.traverse(o => {
    if (o.isMesh) for (const m of [].concat(o.material)) materiales.add(m);
  });
  for (const m of materiales) {
    if (m.emissiveIntensity > 0 && m.emissive?.getHex() !== 0) continue;
    const oro = m.metalness > 0.3;
    m.onBeforeCompile = shader => {
      shader.uniforms.granoYeso = { value: tile };
      shader.vertexShader = shader.vertexShader.replace("#include <common>",
        "#include <common>\nvarying vec3 posYeso;").replace("#include <begin_vertex>",
        "#include <begin_vertex>\nposYeso = (modelMatrix * vec4(transformed, 1.)).xyz;");
      shader.fragmentShader = shader.fragmentShader.replace("#include <common>",
        "#include <common>\nuniform sampler2D granoYeso;\nvarying vec3 posYeso;")
        .replace("#include <normal_fragment_maps>", `#include <normal_fragment_maps>
          vec3 nMundo = inverseTransformDirection(normal, viewMatrix);
          vec3 pesos = pow(abs(nMundo),vec3(4.));
          pesos /= max(dot(pesos,vec3(1.)), 0.0001);
          vec3 p = posYeso / 0.32;
          vec3 a = texture2D(granoYeso,p.yz).rgb;
          vec3 b = texture2D(granoYeso,p.zx + vec2(0.37,0.51)).rgb;
          vec3 c = texture2D(granoYeso,p.xy + vec2(0.63,0.19)).rgb;
          vec3 grad = pesos.x * vec3(0.,a.r-.5,.5-a.g)
                    + pesos.y * vec3(.5-b.g,0.,b.r-.5)
                    + pesos.z * vec3(c.r-.5,.5-c.g,0.);
          vec3 g = mat3(viewMatrix)*grad;
          normal = normalize(normal - ${oro ? "0.48" : "1.15"} * (g - normal*dot(normal,g)));
          float motas = dot(pesos,vec3(a.b,b.b,c.b))-.5;
          diffuseColor.rgb *= 1. + ${oro ? "0.12" : "0.26"} * motas;
          roughnessFactor = clamp(roughnessFactor + motas*0.08,0.12,1.0);
        `);
    };
    m.customProgramCacheKey = () => oro ? "metal-metrico" : "yeso-metrico";
    m.needsUpdate = true;
  }
}
