# 0005 — Caras del teselado y vecindades sin firmar

**Estado:** aceptada — 2026-08-25

## Contexto

La decisión 0004 dejó la red de medinas completa: 323 nudos, 427 aristas, una
componente conexa. Conectividad no es teselado. Para poder hablar de teselas
—y más adelante de niveles— hacía falta convertir el grafo de líneas en las
**caras** que esas líneas delimitan, y decir de cada una qué figura plana es
*si es que hay evidencia para decirlo*.

El bloqueo `BLOCKED_MISSING_SIGNED_LEVEL_CONSTRAINTS` sigue en pie: la figura
128 no trae flechas ni cotas. Esta decisión no lo levanta; prepara el dato
sobre el que ese bloqueo se podrá levantar el día que haya evidencia del signo.

## Decisión

1. **Extraer las caras por rotación de semiaristas** (`granada/caras.py`).
   Cada arista se recorre una vez en cada sentido y la siguiente semiarista es
   la primera en sentido horario alrededor del nudo de llegada. Sin
   dependencias fuera de la biblioteca estándar.
2. **Comprobar la planaridad antes de llamar caras a las regiones.**
   `cruces_de_aristas` busca pares de aristas que se cortan sin compartir
   nudo: hay **0** en los 90 951 pares. Además el recuento tiene que cumplir Euler,
   y si no lo cumple la extracción falla en vez de devolver regiones falsas.
3. **Clasificar solo contra las plantillas documentadas** y solo dentro de una
   tolerancia que no es un parámetro libre: la que impone la resolución del
   dibujo, `2 · resolución / lado más corto`, con la resolución heredada de la
   simplificación Ramer-Douglas-Peucker de 2 px con la que se extrajo la red.
   Lo que no ajusta queda `SIN_CLASIFICAR`, sin figura.
4. **Separar la figura plana de la topología de la pieza.** De una planta se
   lee la figura (A, C, D, cuadrado, octógono). La topología —A1, A2, A3, B4,
   C1, C2, D3— **no** se lee de la planta, y este módulo nunca la asigna.
5. **Representar la vecindad con el salto explícitamente sin firmar.**
   `RelacionVecindad` en `granada/niveles.py` nace con `salto = None`, firmar
   un salto exige citar la evidencia, y `restricciones_firmadas` falla si
   queda una sola sin firmar: no hay conversión parcial. En
   `datos/caras_red.json` las **227** vecindades llevan `"salto": null`.

## Resultado

| medida | valor |
|---|---:|
| caras interiores | **105** |
| Euler `V − E + F` | **2** |
| cruces de aristas | **0** |
| área de las caras / área del contorno | 30,690 / 30,690 m² |
| caras clasificadas | **25** |
| de ellas confirmadas | **9** |
| caras sin clasificar | **80** |

Clasificación: **8 medios cuadrados** (figura A), **1 octógono regular**
central y **16 cuadrados** pequeños. Ni una sola media jaira ni jaira: el
dibujo no las resuelve a esta escala.

Las ocho medios cuadrados rodean el octógono central y forman con él la
estrella de ocho puntas del centro de la cúpula. Sus azimuts son 0,4°, 45,7°,
90,5°, 134,8°, 179,4°, 224,1°, 269,4° y 315,0°: una órbita C8 exacta. Los 16
cuadrados forman otras dos órbitas C8. **La extracción solo impuso simetría de
espejo** (mitad superior reflejada), de modo que la periodicidad de 45° no es
un artefacto del procedimiento: sale del dibujo.

## Cuántas instancias independientes hay detrás de cada órbita

La mitad inferior de la red se generó por reflexión (decisión 0004), de modo
que la réplica impuesta es de orden 2. La periodicidad de 45° es observada,
pero el número de digitalizaciones independientes detrás de cada familia es
menor que el número de caras:

Contando por los **vértices** de cada polígono, no por su centroide —una cara
que cruza el eje tiene parte del contorno generada por el reflejo, y su
existencia depende del pegado—:

| familia | caras | digitalizadas | reflejadas | cruzan el eje | **N estricto** |
|---|---:|---:|---:|---:|---:|
| medio cuadrado | 8 | 3 | 3 | 2 | **3** |
| cuadrado | 16 | 8 | 8 | 0 | **8** |
| octógono | 1 | 0 | 0 | 1 | **0** |

La afirmación de órbita C8 no necesita el reflejo para nada: **la periodicidad
se observa dentro de la mitad digitalizada sola.** Los ocho cuadrados
digitalizados forman dos órbitas de cuatro, con pasos de 45,0°, 45,1° y 45,2°
la primera y 45,0°, 45,1° y 45,3° la segunda. Los tres medios cuadrados
digitalizados están a 224,1°, 269,4° y 315,0°: pasos de 45,3° y 45,6°. Eso es
la evidencia, y es la que hay que citar.

El octógono central **no es una instancia independiente**: cruza el eje, con 4
vértices digitalizados y 4 reflejados, de modo que su simetría respecto del eje
está impuesta. Lo observado es la regularidad de su mitad superior — el espejo
impone simetría, no regularidad, pero no puede confirmarla.

Y una consecuencia que no hay que perder de vista: como el espejo se impuso,
**la red no puede usarse nunca como evidencia a favor de la simetría especular
de la cúpula.** Sería circular. La simetría D8 se midió aparte, sobre la
policromía de la ortoimagen, y es esa medición la que autoriza el reflejo, no
al revés.

## Controles

- **Plantillas de control.** Siete figuras ajenas al sistema documentado, dos
  de ellas escogidas para compartir ángulos (rectángulo 1:1,4, octógono de
  lados alternos) o lados (rombo de 60°) con las buenas. Ninguna gana a la
  plantilla documentada en ninguna cara. Una sola cara —un medio cuadrado—
  admite además un triángulo isósceles de 100° dentro de su ventana, y aun así
  su plantilla ajusta 3,9 veces mejor.
- **Margen de discriminación** (cuántas veces peor ajusta la mejor plantilla
  ajena): octógono **6,5×**, medios cuadrados **≥ 3,9×**, cuadrados **1,16×**.
- **Firmeza.** Solo se da por confirmada la cara con lado mínimo ≥ 10 px de la
  figura y margen ≥ 2. Los 16 cuadrados fallan las dos condiciones: su lado
  mide 8,1–9,5 px, del orden del propio grosor de cruce del esqueleto, y su
  ventana de tolerancia llega a 28°. Quedan etiquetados
  `al_limite_de_resolucion`. **No son un cuadrado medido; son una región del
  tamaño del error.**
- **Barrido de resolución.** Con 1, 1,5, 2 y 3 px el recuento es idéntico
  (8 / 16 / 1). Solo baja a 0,5 px, por debajo de la resolución real.
- **Las 80 caras sin clasificar tampoco son ruido**: se agrupan por área en
  familias de 16, 24, 8, 8, 8 y 16 copias. Dentro de una familia el número de
  lados varía (7, 8 o 9 para la de 0,85 m²) porque el trazado digitaliza cada
  copia con un vértice de más o de menos; el área no.
- **51 de las 80 ni siquiera son convexas.** Las figuras del sistema
  occidental tienen ángulos internos fijos y son convexas: una cara con un
  ángulo de 270° no es una pieza, es una región que el dibujo no subdivide.

## Techo de afirmación

Una cara es una **región del dibujo**, no una pieza colocada en la cúpula.
Que 8 caras ajusten al medio cuadrado sostiene que la propuesta publicada
dibuja ahí ocho medios cuadrados; no sostiene que la cúpula real los tenga en
esa posición, ni con qué topología (A1, A2 o A3), ni a qué cota.

De las 105 caras, **80 no reciben figura**. Eso no es un fallo de la
clasificación: la corona interior de esta cúpula tiene subdivisiones más finas
que las que la figura 128 dibuja, cosa ya advertida en `docs/teselado.md`. Un
teselado completo de Dos Hermanas exige una planta que las traiga, no una
tolerancia más generosa.

Sobre los dos recuentos que aparecen en la documentación: **227** vecindades
cuenta también las 16 adyacencias contra el nodo-contorno; **211** son las
vecindades entre caras interiores. La diferencia es exactamente 16, el número
de caras que tocan el borde. Los dos números son correctos y describen objetos
distintos: el contorno es un nodo artificial y por eso queda fuera de todo
razonamiento sobre ciclos.

Las 227 vecindades dicen qué toca con qué. **Ninguna dice si sube, descansa o
baja.** Mientras siga así, `restricciones_firmadas` no deja propagar, y los 24
terminales de borde siguen siendo anclas candidatas y no niveles.

`BLOCKED_MISSING_SIGNED_LEVEL_CONSTRAINTS` continúa.

## Alternativas rechazadas

- **Ensanchar la tolerancia hasta clasificar más caras.** A 10° entran 16
  cuadrados más, pero también dejan de discriminarse las plantillas de
  control. La tolerancia sale de la resolución, no del resultado que apetezca.
- **Fusionar caras pequeñas con sus vecinas para que salgan figuras
  documentadas.** Sería construir el teselado deseado a partir de la hipótesis
  que se quería comprobar.
- **Dar por buena la clasificación de los 16 cuadrados.** Su lado está en el
  suelo de resolución del dibujo. Se conservan etiquetados y marcados.
- **Firmar los saltos por la posición radial de cada cara** (más cerca del
  centro, más alto). Es la propagación por coronas que la decisión 0003 ya
  rechazó, con otro nombre.

## Reproducción

- `scripts/extraer_caras.py` → `datos/caras_red.json`
- `scripts/dibujar_caras.py` → `renders/caras_red.svg`
- Núcleo: `granada/caras.py`; vecindades sin firmar: `granada/niveles.py`
- Pruebas: `tests/test_caras.py` (30), `tests/test_caras_red.py` (15) y las
  nuevas de `tests/test_niveles.py`
