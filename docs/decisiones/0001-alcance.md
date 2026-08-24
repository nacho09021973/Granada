# 0001 — Alcance del núcleo aritmético

Fecha: 2026-08-24
Estado: aceptada

## Contexto

Primer paso de un proyecto a un año: un generador de cúpulas de mocárabes con
geometría algebraicamente exacta, parametrizado por el orden de simetría. Esta
decisión fija qué se construye ahora y sobre qué estructura algebraica.

## Decisión 1: los vértices viven en Z[ζ_m], no en Z² ni en Z[√2]²

El requisito de fondo es que el conjunto de vértices sea **cerrado bajo las
simetrías del mocárabe**: rotaciones de 2π/m y reflexiones. Si no lo es, la
composición de dos operaciones exactas produce un punto que hay que redondear,
y el redondeo destruye la exactitud que justifica todo el enfoque.

- **Z² (pares de enteros)** no sirve: rotar (1,0) un ángulo de 2π/m produce
  (cos(2π/m), sin(2π/m)), que no es entero salvo para m ∈ {1, 2, 4}.

- **Z[√2]² (pares de la forma a + b√2)** tampoco: rotar (1,0) 45° da
  (√2/2, √2/2). Los coeficientes son semienteros — 1/2 · √2 — y quedan fuera
  de Z[√2]. El anillo no es cerrado bajo la rotación que precisamente se
  necesita en un mocárabe de orden 8.

- **Z[ζ_m]** sí es cerrado, por construcción. La rotación de 2π/m es la
  multiplicación por ζ_m, que es un elemento del propio anillo; la reflexión
  es el automorfismo ζ → ζ^(−1). Ambas son operaciones internas y exactas. El
  precio es que el rango sobre Z es φ(m) en vez de 2, y que las coordenadas
  cartesianas solo aparecen al final, vía el embedding numérico.

Consecuencia adicional útil: |z|² cae automáticamente en el subanillo real
Z[2·cos(2π/m)], así que las longitudes al cuadrado también son exactas y
comparables sin tolerancia.

## Decisión 2: aritmética exacta, sin coma flotante en el núcleo

Un mocárabe se construye por composición repetida de simetrías y por
intersección de elementos generados así. Con floats, la pregunta «¿estos dos
vértices son el mismo?» pasa a depender de un epsilon, y ese epsilon se
convierte en un parámetro oculto que gobierna la topología de la malla. Con
aritmética entera exacta la pregunta tiene una respuesta binaria y estable.

Los floats quedan confinados a las funciones `numeric_embedding_*`, al final
de `cyclotomic.py`. El prefijo del nombre es deliberado: hace visible el cruce
de frontera en cualquier fichero que las use. Un test estructural recorre el
AST del módulo y falla si un float, `math` o `float()` aparecen fuera de ellas.

Excepción registrada: el cambio de base al subanillo real usa
`fractions.Fraction` para la eliminación gaussiana. Es aritmética racional
exacta, no coma flotante, y el resultado se exige entero antes de devolverse.

## Decisión 3: cero dependencias en el núcleo

Solo biblioteca estándar de Python 3.11+. `pytest` únicamente para tests.

El núcleo son polinomios enteros y álgebra lineal sobre Q en dimensiones
pequeñas (φ(m) es 8 para m=16, 16 para m=32). No hay nada aquí que justifique
arrastrar sympy o numpy: ni el rendimiento lo pide ni el volumen de código lo
pide. A cambio, el repositorio se instala y se audita sin fricción, sobrevive
a los cambios de API de terceros, y — dado que se publicará abierto — cualquiera
puede leer la implementación completa de la exactitud que el proyecto afirma,
en un solo fichero, sin seguir la pista a una dependencia.

Si más adelante hace falta una dependencia para geometría o exportación, irá en
un extra opcional, nunca en el núcleo.

## Fuera de alcance en esta fase

Explícitamente **no** se implementa, porque no está decidido todavía:

- Geometría 3D de cualquier tipo.
- Perfiles de celda de mocárabe.
- Funciones de nivel / estratificación de la cúpula.
- Exportación de mallas (OBJ, STL, glTF, o cualquier otro formato).
- Fidelidad a cualquier cúpula histórica concreta — la afirmación (B) del
  README. Requiere fuentes verificadas y un margen de error explícito.
- Bibliografía. `docs/fuentes.md` queda vacío hasta tener fuentes comprobadas
  de primera mano.

## Corrección al enunciado original del test de m=16

El enunciado original pedía comprobar que existe un elemento con módulo al
cuadrado igual a 2 − √2 y que ese elemento **no existe en m=8**. La segunda
mitad es falsa: en Z[ζ₈] el elemento ζ − 1 tiene
|ζ − 1|² = 2 − 2·cos(45°) = 2 − √2, y el subanillo real de Z[ζ₈] es Z[√2], que
contiene esa cantidad. Además 2·sin(π/8) = 0.7653… es la cuerda de 45°, no la
de 22.5°.

La cantidad que sí separa m=16 de m=8 es la cuerda de 22.5° = 2π/16:
|ζ₁₆ − 1|² = 2 − √(2 + √2) ≈ 0.1522, con raíz 2·sin(π/16) = 0.3902…, que no
pertenece a Z[√2].

Se han escrito los tres tests: el de 2 − √2 en m=16 tal como se pidió (sin
afirmar no-existencia en m=8), uno que documenta que 2 − √2 también se realiza
en m=8, y el test de separación correcto.

## Decisión 4: m=16 es el orden natural del sistema andalusí

Resuelto el 2026-08-24. Sostenido por la entrada 1 de `docs/fuentes.md`
(Ferrer-Pérez-Blanco, Gámiz-Gordo y Reinoso-Gordo, *Sustainability* 11(2) 316,
2019, CC BY 4.0), que describe el sistema occidental de mocárabes a partir de
los manuscritos del siglo XVII de Fray Andrés de San Miguel y Diego López de
Arenas, y afirma que los ángulos interiores se reducen a cuatro: **45°, 67.5°,
90° y 135°**.

Los cuatro son múltiplos de 22.5° = 2π/16. Un conjunto de direcciones cerrado
bajo giros de 22.5° es el de las raíces 16-ésimas de la unidad, luego **Z[ζ₁₆]
es el anillo natural del sistema andalusí** y la cuerda de 22.5° es su longitud
primitiva. El 67.5° = 3·22.5° es el que lo fija: sin él bastaría con orden 8.

Esto confirma que el test de separación relevante es el corregido — el de
2 − √(2 + √2) — y no el del enunciado original, que corresponde al octógono
intermedio.

La misma fuente da la motivación histórica del proyecto de forma más directa
de lo esperado: el oficio usaba **7/5 = 1.4 como aproximación de √2**
(«a rectangle with ratio 5 to 7, rounded to 5 root of 2»). Ese redondeo es
exactamente lo que el núcleo elimina: aquí √2 no es un decimal, es el elemento
ζ + ζ⁻¹, y su cuadrado es el entero 2.

Nada de esto cambia el código: el núcleo ya es genérico en m. Cambia qué
órdenes priorizar en la fase geométrica, y por qué.

**TODO pendiente**: si la cúpula de las Dos Hermanas *en concreto* es de orden
16. El informe preliminar lo afirma (cuadrado → octógono → hexadecágono) pero
no está verificado, y otras descripciones hablan de base octogonal con 16
cupulines. Esto solo afecta a la afirmación (B); la decisión de anillo se
sostiene sin ello.

## Decisión pendiente: sistema oriental u occidental

La tesis de Ferrer Pérez-Blanco (entrada 2 de `fuentes.md`) distingue la
tradición **oriental** (al-Kāshī, siglo XV) de la **occidental o andalusí**
(López de Arenas, Fray Andrés de San Miguel). Son sistemas formalmente
distintos y Granada no se compromete hoy con ninguno.

La Decisión 4 se apoya en el sistema occidental. Si más adelante se quisiera
generar mocárabes orientales, habría que revisar el conjunto de ángulos y, con
él, el orden del anillo. Merece su propio ADR cuando se aborden los perfiles
de celda.
