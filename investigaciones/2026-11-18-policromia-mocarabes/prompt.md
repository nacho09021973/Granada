# Encargo dirigido: policromía original de la cúpula de mocárabes de la Sala de Dos Hermanas

2026-11-18. Preparado por Claude (claude-opus-5-5). Permiso del usuario para
encargar a `investigacion-gemini` dado el 2026-11-18 («Sí», a condición de
enseñarle el encargo antes de enviarlo). Vía dirigida: lleva lo que ya
tenemos. La vía abierta (`prompt_abierto.md`) lleva solo la pregunta.

Objetivo: localizar fuentes primarias sobre qué colores tenía y cómo se
repartían en los mocárabes de la cúpula de Dos Hermanas (Alhambra) al
acabarse, hacia 1354-1359, o en cúpulas nazaríes de mocárabes comparables.
Resultado esperado: lista de fuentes con referencia completa, página o
figura y cita breve, clasificadas como ANÁLISIS (estratigrafía o pigmentos
medidos), REGISTRO (descripción o dibujo del estado visto) o RESTITUCIÓN
(propuesta de cómo era), y una lista explícita de lo no encontrado.
Rondas: una ejecución por vía. Cierre: cada fuente comprobada en el original
y anotada en `comprobacion.md`. El informe localiza, no prueba; no se
concluye que algo no exista porque la búsqueda no lo encuentre.

Uso del resultado: elegir colores para un modelo 3D. El criterio del usuario
es estético («reluciente como el día de la inauguración, colores apagados y
artísticos»), declarando lo supuesto; las fuentes orientan.

Lanzar: `investigacion-gemini investigaciones/2026-11-18-policromia-mocarabes`
y `investigacion-gemini investigaciones/2026-11-18-policromia-mocarabes prompt_abierto.md`.

---
You are helping with a literature search in architectural history and
conservation science. You have Google Search. Your job is to LOCATE primary
sources, not to judge them. Do not invent citations; if you cannot find
something, write "not found". For every source give authors, title, year,
journal or publisher, DOI or URL, the page/figure/plate, and a verbatim
quotation of at most 30 words in the original language. Mark anything you
could not open in full text as "not read in full". Sources in Spanish,
English, French, German or Arabic are all welcome.

Subject. The muqarnas dome of the Hall of the Two Sisters (Sala de Dos
Hermanas), Palace of the Lions, Alhambra, Granada, built under Muhammad V
around 1354-1359; and, for comparison, the muqarnas domes of the Hall of the
Abencerrajes and other Nasrid muqarnas vaults.

Question. What was the original polychromy of these muqarnas: which
pigments and gilding, and how were the colours distributed by element
(concave cell backs, cell walls, flat faces, the small cupolas, the keystone
area, the windows' drum)? Distinguish carefully:
- ANALYSIS: pigment or stratigraphic analysis on samples from these vaults
  (XRF, Raman, SEM-EDX, polarized light microscopy, cross sections), with the
  sample location;
- RECORD: descriptions or drawings of the colours that were actually seen,
  with date;
- RESTITUTION: proposed reconstructions of the original appearance.

Already known to us (say whether a source goes further; do not just repeat):
- Owen Jones and Jules Goury, "Plans, Elevations, Sections and Details of
  the Alhambra" (London, 1842-1845): vol. II, plate XXXIX, colour of the
  muqarnas of the cornice of the window in this hall; vol. I, plate 38,
  "present state of the colours".
- A 19th-century plaster model attributed to Rafael Contreras showing red,
  gilding and grey-blue ribs (we only have photographs; seek its catalogue
  record and any study of it).
- General statement by the Patronato de la Alhambra y Generalife: mineral
  pigments showing blue, red, black and green, with gold and silver.
- Studies on Alhambra plasterwork (yeserías) identifying lazurite, cinnabar
  or vermilion, minium and carbon black, and 19th-century synthetic blue
  from restorations. We lack exact references: find them.
- Ferrer-Pérez-Blanco, Gámiz-Gordo and Reinoso-Gordo on the geometry of
  this dome (2019, 2023) and Ferrer's PhD thesis (2023): geometry, not
  colour, as far as we know. Say if they discuss colour.

Also look for: restoration reports of the Patronato or the IAPH on this hall
or the Abencerrajes (conservation campaigns, especially any after 2000);
the journal "Cuadernos de la Alhambra"; works by Antonio Fernández-Puertas,
Carmen Rallo Gruss, Ramón Rubio Domene, Carolina Cardell and colleagues
(University of Granada), and Leopoldo Torres Balbás where they touch on
colour of muqarnas.

Output, in this order:
1. Table: source | class (ANALYSIS / RECORD / RESTITUTION) | which vault and
   which element | colours or pigments stated | page/figure | quotation.
2. For each colour (blue, red, green, black, gold, silver, white/plaster):
   which element it is reported on, and by which sources.
3. Explicit list of what you searched for and did not find.
