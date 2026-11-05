# Contraste de la cúpula por piezas con la ortoimagen (2026-11-05)

Script: `scripts/contrastar_ortoimagen.py`. Datos: `datos/contraste_ortoimagen.json`.
Imagen: `renders/contraste_ortoimagen.png` (ortoimagen | modelo | mezcla).

El render cenital del modelo se pone a la escala (472,2 px/m, supuesta), centro
(2048, 2035) y orientación de la ortoimagen de AA-415_23, con luz vertical
simétrica. A las dos imágenes se les aplica el mismo código: espectro angular
por zonas (fracción de potencia sobre k ≥ 1) y correlación de Pearson de las
imágenes desenrolladas en polares, en crudo y suavizadas a 0,15 m, girando el
modelo de 0 a 45°.

## Resultados

| zona (m) | k8 foto / modelo | k16 foto / modelo | k32 foto / modelo | r suavizada a 0° | máximo | media con giro |
|---|---|---|---|---|---|---|
| estrella central (0,2–0,9) | 4,7 / 7,0 | 7,4 / 18,7 | 0,9 / 9,0 | −0,68 | −0,67 a 22,5° | −0,68 |
| cuerpo (0,9–2,7) | 5,3 / 8,1 | 5,7 / 4,1 | 1,7 / 6,8 | **0,27** | 0,27 a 0,5° | 0,18 |
| anillo exterior (2,7–3,5) | 2,2 / 4,0 | 22,5 / 4,4 | 3,0 / 4,9 | −0,25 | 0,29 a 12° | 0,01 |

Lectura:

- **Cuerpo**: en fase con la foto (máximo a 0,5°), pero la correlación es
  modesta. El modelo tiene más orden 8 y mucho más k = 32 que la foto: sus
  hiladas estrelladas son más regulares y angulosas que la cúpula real.
- **Estrella central**: anticorrelación fuerte que no depende del giro, luego
  es radial, no angular: en la foto el centro es oscuro y en el modelo la
  cupulilla sale clara. Además el modelo concentra k = 16 y k = 32 que la foto
  no tiene: su estrella es demasiado aguda.
- **Anillo exterior**: anticorrelado a 0°. **Control**: con los cupulines
  oscurecidos al 40 % (solo para la medida; el acabado elegido sigue siendo
  claro) pasa a r = 0,74 a 0° y k16 = 22,6 %. El signo lo pone el brillo de los
  cupulines. Esto **no** valida su posición: se midió en esta misma imagen
  (`scripts/medir_cupulines.py`).
- **Correlación cruda**: |r| < 0,13 en todas las zonas. La textura fina del
  modelo no se parece a la real, y esa medida no discrimina.

## Controles del método

- La ortoimagen reproduce el patrón de la entrada 7 de `fuentes.md`: k16
  dominante en el anillo exterior, k8 ≈ k16 en el cuerpo. Las cifras difieren
  porque la normalización y las zonas no son las de allí.
- Con luz simétrica, los giros de 0° y 45° dan la misma correlación en las tres
  zonas, como exige el orden 8. Con las luces laterales del render no ocurría,
  y por eso el contraste se hace con luz vertical.

## Lo que no mide

Fotometría, no geometría: compara manchas de luz y sombra, no aristas. No dice
qué piezas hay en cada sitio ni la altura de nada. La escala de la planta sigue
siendo un supuesto.
