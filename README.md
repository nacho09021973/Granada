# Granada

Generador de cúpulas de mocárabes (muqarnas) con geometría algebraicamente
exacta, parametrizado por el orden de simetría.

**Estado actual.** El núcleo aritmético exacto está sólido, la red de medinas
propuesta para Dos Hermanas ya es un grafo conexo completo (323 nudos, 427
aristas), sus **105 caras** están extraídas, medidas y clasificadas donde hay
evidencia (`granada/caras.py`: 9 figuras confirmadas, 16 al límite de
resolución, 80 sin figura) y existe una representación topológica de niveles
(`granada/niveles.py`). Las 227 vecindades entre caras llevan el salto
explícitamente **sin firmar**: aún faltan las restricciones firmadas que
permitirían propagar niveles desde el borde. Los perfiles de celda `cuna` y
`rombo` siguen vigentes. La antigua estratificación por coronas, `trapecio` y
el perfil de cónica única se conservan marcados como obsoletos hasta que exista
sustituto.
No hay todavía una planta histórica con niveles validada, geometría 3D
aceptada ni exportación de mallas. El estado operativo está en
[`PROXIMOS-PASOS.md`](PROXIMOS-PASOS.md).

---

## Dos afirmaciones que este proyecto no mezcla

Conviene fijarlo antes que nada, porque son de naturaleza distinta y se
confunden con facilidad.

**(A) Generación sintética.** El proyecto genera cúpulas de orden de simetría
arbitrario cuya geometría es exacta por construcción. Es una afirmación
**matemática**: se sostiene o se refuta con una demostración o con un
contraejemplo, y los tests de este repositorio son parte de su verificación.
Que el módulo de un vértice sea exactamente `2 - sqrt(2)` es una igualdad en
un anillo, no una medida.

**(B) Fidelidad a una cúpula histórica concreta.** Que una salida del
generador reproduzca una cúpula real determinada es una afirmación
**empírica**. Depende de las fuentes disponibles sobre ese monumento, de su
precisión, y de las deformaciones reales documentadas: asentamientos,
reparaciones, tolerancias de ejecución, reconstrucciones. Una afirmación de
tipo (B) exige evidencia externa y no se deriva de (A).

**(B) no está implementado.** Nada en este repositorio, ni ahora ni de forma
implícita, sostiene fidelidad a ninguna cúpula concreta. Cuando se aborde,
irá acompañada de sus fuentes y de un margen de error explícito.

**El objetivo declarado sobre Dos Hermanas es aproximado.** Desde la
[decisión 0008](docs/decisiones/0008-objetivo-reconstruccion-aproximada.md) el
proyecto no persigue la reconstrucción *exacta* de esa cúpula, sino la mejor
posible con los datos que hay. La razón es que las fuentes no coinciden entre
sí —23 hiladas medidas, 24 en un recuento comunicado, 7 niveles en la
divulgación— y no existe tabla pública que asocie cada pieza a una cota. La
distinción (A)/(B) sigue intacta: lo que baja es el techo declarado de (B), no
el listón de la evidencia. Cada salida declara qué parte está medida, cuál
inferida y cuál es un parámetro.

Este README no afirma originalidad ni novedad frente a la literatura
existente sobre mocárabes o sobre geometría islámica. La bibliografía se
recoge en [`docs/fuentes.md`](docs/fuentes.md), donde cada entrada lleva su
verificación y su techo de afirmación.

---

## Qué hay ahora: el núcleo aritmético

Los vértices del plano de un mocárabe con simetría de orden `m` viven en el
anillo de enteros ciclotómicos **Z[ζ_m]**, visto como subconjunto de
C = R², donde ζ_m = exp(2πi/m).

Un elemento es un polinomio con coeficientes enteros módulo el m-ésimo
polinomio ciclotómico Φ_m(x). El rango sobre Z es φ(m), y la base es
1, ζ, ζ², …, ζ^(φ(m)−1).

El módulo implementa:

1. **Φ_m(x)** con coeficientes enteros exactos, a partir de
   `x^m − 1 = ∏_{d|m} Φ_d(x)` mediante divisiones exactas en Z[x].
2. **Aritmética en Z[x]/Φ_m(x)**: suma, resta, producto con reducción, potencia.
3. **Multiplicación por ζ**: la rotación de 2π/m, exacta.
4. **Conjugación compleja** ζ → ζ^(−1) = ζ^(m−1): la reflexión.
5. **Norma al cuadrado** |z|² = z·conj(z), que cae en el subanillo real
   Z[2·cos(2π/m)] y se devuelve en representación exacta.
6. **Embedding numérico** a coordenadas (x, y) en coma flotante.

### Cero coma flotante en el núcleo

Toda la aritmética es entera y exacta. Los únicos floats del paquete están en
las dos funciones cuyo nombre empieza por `numeric_embedding_`, aisladas al
final de `cyclotomic.py` tras un separador explícito. El prefijo es
deliberado: hace visible de un vistazo cualquier punto del código que cruce
esa frontera.

Hay un test estructural que recorre el AST del módulo y falla si un literal
float, una llamada a `math` o el constructor `float` aparecen en cualquier
otra función.

---

## Uso

Requiere **Python 3.11 o superior**. El núcleo no tiene ninguna dependencia:
solo biblioteca estándar. `pytest` hace falta únicamente para los tests.

```python
from granada import CyclotomicRing, numeric_embedding_xy

R = CyclotomicRing(16)          # simetría de orden 16
z = R.zeta                      # rotación de 2π/16, exacta

z ** 16 == R.one                # True, igualdad de enteros
R.zeta_power(5).norm_squared() == 1   # True

# La cuerda de 45°: 2·sin(π/8), cuyo cuadrado es 2 − √2
cuerda = R.zeta_power(2) - 1
cuerda.norm_squared()           # 4 − λ², con λ = 2·cos(π/8)
cuerda.norm_squared().coeffs    # (4, 0, -1, 0), enteros exactos

# Solo al final, y a la vista:
numeric_embedding_xy(cuerda)    # (-0.2928932188134524, 0.7071067811865475)
```

`√2` no es un número en coma flotante aquí. Es el elemento `ζ + ζ⁷` de
Z[ζ₈], y su cuadrado es exactamente el entero `2`.

### Tests

```bash
python -m pytest
```

---

## Estructura

```
granada/cyclotomic.py       núcleo aritmético completo
tests/test_cyclotomic.py    suite de tests
docs/decisiones/            registro de decisiones de diseño
docs/fuentes.md             bibliografía (vacío hasta tener fuentes verificadas)
```

## Licencia

MIT. Ver [`LICENSE`](LICENSE).
