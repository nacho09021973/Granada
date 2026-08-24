# Fuentes

Solo entra aquí lo que se ha consultado directamente y cuyos campos se han
comprobado uno a uno. Cada entrada indica **qué se verificó**, **qué no**, y
qué afirmación del proyecto sostiene: (A) matemática o (B) empírica, según la
distinción del README.

Verificación realizada el 2026-08-24. El material descartado y el informe del
que salió esta pista bibliográfica están en `investigacion-preliminar.md`,
marcado como no verificado.

---

## 1. Ferrer-Pérez-Blanco, Gámiz-Gordo y Reinoso-Gordo (2019)

**New Drawings of the Alhambra: Deformations of Muqarnas in the Pendentives of
the Sala de la Barca.** *Sustainability* 11(2), 316.
DOI [10.3390/su11020316](https://doi.org/10.3390/su11020316).

- Autores y afiliaciones: Ignacio Ferrer-Pérez-Blanco (Laboratory of Digital
  Culture for Architectural Projects, EPFL), Antonio Gámiz-Gordo (Expresión
  Gráfica Arquitectónica, Universidad de Sevilla), Juan Francisco
  Reinoso-Gordo (Expresión Gráfica Arquitectónica y en la Ingeniería,
  Universidad de Granada).
- Recibido 27-11-2018, aceptado 27-12-2018, publicado 09-01-2019.
- **Licencia CC BY 4.0** (leída en la página 15 del PDF). Reutilizable con
  atribución.
- **Verificado**: portada, abstract, afiliaciones, fechas, licencia, y el
  contenido de la página 2, leídos directamente del PDF.

### Por qué es la fuente más importante para este repositorio

La página 2 describe el sistema **occidental o andalusí** de mocárabes según
los dos manuscritos de carpintería del siglo XVII que cita — Fray Andrés de
San Miguel y Diego López de Arenas — y da los tres perfiles planos básicos:

- un rectángulo de proporción **5 a 7, «redondeada a 5·√2»**;
- un triángulo rectángulo isósceles de catetos 5 e hipotenusa 7 («también
  redondeada»);
- un triángulo isósceles con ángulo de 45° y lados mayores de 5.

Y, literalmente:

> «Theoretically, the layout of the muqarnas' inner angles are reduced to
> four: 45°, 67.5°, 90°, and 135°.»

Dos consecuencias directas, ambas de tipo (A):

1. **Los cuatro ángulos son múltiplos de 22.5° = 2π/16.** Un conjunto de
   direcciones cerrado bajo giros de 22.5° es exactamente el de las raíces
   16-ésimas de la unidad. Eso hace de **Z[ζ₁₆] el anillo natural del sistema
   andalusí**, y de la cuerda de 22.5° su longitud primitiva. El 67.5° = 3·22.5°
   es el que lo fija: sin él bastaría con orden 8.
2. **El oficio histórico usaba 7/5 = 1.4 como aproximación de √2 = 1.41421…**
   La fuente lo dice sin rodeos: «rounded to 5 root of 2». Ese redondeo es
   precisamente lo que el núcleo de Granada elimina — en Z[ζ₈] ⊂ Z[ζ₁₆], √2 no
   es un decimal sino el elemento ζ + ζ⁻¹, y su cuadrado es exactamente 2.

**Objeto de estudio**: las pechinas de la **Sala de la Barca** (Palacio de
Comares). **No** la Sala de las Dos Hermanas. Ver la nota de la sección 6.

---

## 2. Ferrer Pérez-Blanco, tesis doctoral (2023)

**Mocárabes de La Alhambra. Forma, dibujo y configuración arquitectónica.**
Universidad de Sevilla, 2023. Director: Antonio Gámiz Gordo. 491 páginas.

- **Verificado** vía Dialnet (código de tesis 312651): título, autor, director,
  universidad, año, extensión y resumen.
- El resumen confirma la distinción entre la tradición **oriental**
  (al-Kāshī, matemático del siglo XV) y la **occidental** (López de Arenas,
  Fray Andrés de San Miguel), y documenta composiciones asimétricas.
- **NO verificado**: el handle de idUS `11441/143321` que da el informe
  preliminar. El repositorio devolvió HTTP 403 a la consulta automática.
  Pendiente de comprobar a mano.

Sostiene (B), y es la referencia a leer antes de abordar los perfiles de celda.

---

## 3. Almagro Gorbea — plano AA-415_23 (RABASF)

**Casa Real de la Alhambra (Granada) — Sección y techo sala de las Dos
Hermanas.** Real Academia de Bellas Artes de San Fernando, serie *Arquitectura
de Al-Andalus*, inventario [AA-415_23](https://www.academiacolecciones.com/arquitectura/inventario.php?id=AA-415_23).

- **Verificado** campo a campo en la ficha de inventario: autor (Almagro
  Gorbea, Antonio; Barcelona, 1948), escala **1/25 (A0)**, formato
  planimetría vectorial, **PDF de 4.7 MB**, observaciones «Sección y planta
  del techo de la sala de las Dos Hermanas con ortoimagenes», procedencia
  «Fondo gráfico donado por el Académico D. Antonio Almagro Gorbea».
- **NO verificado**: la fecha «enero 2021» del cajetín. Procede del informe
  preliminar, no de la ficha; la ficha no da fecha.
- **NO verificado**: la ficha **no menciona** geometría poligonal de la cúpula
  ni número de lados. El informe preliminar atribuía a este plano cosas que la
  ficha no dice.

**Aviso de licencia**: es material de la RABASF. Derivar geometría de él para
un repositorio MIT exige revisar sus condiciones de uso **antes**, no después.

---

## 4. APAG — plano P-000831

**Habitaciones altas de la Sala de las Dos Hermanas. Proyecto de reparación.**
Archivo del Patronato de la Alhambra y Generalife, Colección de Planos,
[handle 10514/4364](https://www.alhambra-patronato.es/ria/handle/10514/4364).

- **Verificado** campo a campo: delineante Manuel López Bueno; arquitecto
  conservador Leopoldo Torres Balbás; agosto de 1927, Granada; escala 1/50;
  papel cianotipo; 62 × 49 cm; nº de plano de archivo técnico 664; sección A-B.
- Coincide exactamente con la fila correspondiente de la tabla del informe
  preliminar. Es el único registro de esa tabla que se ha comprobado; **las
  otras nueve filas siguen sin verificar.**

---

## 5. Gámiz Gordo, Ferrer Pérez-Blanco y Reinoso Gordo (2023)

**A Deformed Muqarnas Dome at the Sala de los Reyes in the Alhambra: Graphic
Analysis of Architectural Heritage.** *Heritage* 6(12), 7400–7426.

- **Verificada la existencia** y los datos bibliográficos; depositado también
  en DigiBUG (UGR, handle 10481/91060).
- **Contenido NO leído**: MDPI devolvió HTTP 403. Según los resúmenes
  disponibles, dibuja digitalmente por primera vez cerca de dos mil piezas de
  esa cúpula y documenta deformaciones significativas mediante escáner láser 3D.
- Pendiente de lectura directa antes de usarse para nada.

---

## 6. Nota sobre las deformaciones: corrección de atribución

El informe preliminar presenta el hallazgo de deformaciones por escáner láser
dentro de su discusión sobre la Sala de las Dos Hermanas. **Eso no se
sostiene.** Los dos trabajos publicados que se han localizado son:

- las **pechinas de la Sala de la Barca**, Palacio de Comares (entrada 1);
- la **cúpula de la Sala de los Reyes**, Palacio de los Leones (entrada 5).

No se ha localizado ninguna medición publicada de deformaciones de la cúpula
de las Dos Hermanas.

Aun así, el hallazgo general sostiene la afirmación (B) del README con más
fuerza de la que se le había dado. Si en los elementos medidos los alarifes
deformaron la malla teórica y los asentamientos hicieron el resto, entonces
para cualquier cúpula histórica la afirmación (B) solo puede formularse como
*«ajusta dentro de una tolerancia medida»*, nunca como *«reproduce»*. La
geometría exacta es la del modelo, no la del monumento.

---

## Pendiente de verificar

- Orden de simetría de la cúpula de las Dos Hermanas en concreto. El informe
  preliminar afirma cuadrado → octógono → **hexadecágono**. Otras fuentes
  divulgativas describen base octogonal, dos estrellas de ocho puntas y 16
  cupulines. **No resuelto**: la página del Patronato agotó el tiempo de
  espera. La entrada 1 fija el orden 16 para el *sistema* andalusí, que es lo
  que necesita el generador; el dato de esta cúpula concreta sigue abierto.
- Recuento de piezas de la cúpula de las Dos Hermanas: circulan 5.416 piezas y
  «104 adarajas en forma de estrella» (IAPH / Paseos Matemáticos). Sin
  comprobar, y de tipo (B).
- Fecha del cajetín de AA-415_23.
- Las otras nueve filas de la tabla de planos del APAG.
- Owen Jones y Jules Goury, *Plans, Elevations, Sections and Details of the
  Alhambra* (1842–1845). Citada de segunda mano en las entradas 1 y 5, que la
  usan como referencia de contraste. Merece consulta directa.
- Enrique Nuere, análisis gráfico de las piezas componentes de los mocárabes,
  citado como precursor de los estudios CAD en la entrada 1.
- Los manuscritos del siglo XVII: Fray Andrés de San Miguel y Diego López de
  Arenas. Son la fuente primaria del sistema occidental y la raíz de la
  entrada 1.
