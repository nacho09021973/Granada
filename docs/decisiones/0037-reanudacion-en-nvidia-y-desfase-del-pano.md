# 0037 — Reanudación en NVIDIA y diagnóstico del paño 00

21 de noviembre de 2026. Se retoma `cierres-y-cupulines`, desde `2e83eb1`.
El plan de `main` terminaba el 17 de noviembre y dejaba pendientes trabajos
que esta rama ya incorpora. No se repiten los cierres ni la policromía.

Este registro corresponde al diagnóstico previo. La corrección posterior
del piloto se documenta en [0038](0038-encaje-del-pano-con-la-seccion.md).

## Equipo y comprobaciones

NVIDIA-SMI reconoce una RTX 5060 de 8151 MiB, controlador 620.67.01
(KMD 621.01). Blender 4.5.15 LTS solo enumera CPU sin la ruta de bibliotecas
de WSL; con `LD_LIBRARY_PATH=/usr/lib/wsl/lib` enumera la RTX como CUDA.
Se completan las tres vistas del OBJ auditado a 1400 px y 48 muestras.
Los tiempos de render registrados de visitante y sala son 43,57 y 36,48 s.
No se ha probado OptiX en esta sesión.

```bash
LD_LIBRARY_PATH=/usr/lib/wsl/lib ~/.local/opt/blender/blender -b -P scripts/render_cycles.py -- --obj renders/previas/cupula_campo_vigente_1400.obj --vistas cupula,visitante,sala --lado 1400 --muestras 48 --dispositivo cuda --salida renders/previas/2026-11-21_gpu --sufijo _cuda
```

Estas imágenes corresponden al OBJ de campo de 0032, **no** al GLB con los
detalles locales de 0035–0036. No validan el encaje de las nuevas hiladas.
Desde visitante siguen viéndose zonas negras y encuentros irregulares;
su causa no se determina por el color del render.

Los 784 tests pasan (`.venv/bin/python -m pytest -q`, 36,64 s).
La comprobación existente de la visita termina con éxito: sala, selección,
zoom, órbita, retorno, cupulín, hiladas y controles táctiles emulados.
Se inspecciona también la captura frontal de hiladas: persisten rendijas
negras en el encuentro superior. No equivale a una prueba en móvil físico.

```bash
npm install --prefix build/comprobacion-web --no-audit --no-fund puppeteer-core
python3 -m http.server 8765 --bind 127.0.0.1
# En otra terminal:
NODE_PATH=build/comprobacion-web/node_modules CHROME_PATH=/home/adnac/.cache/ms-playwright/chromium-1187/chrome-linux/chrome node scripts/comprobar_visita_web.cjs http://127.0.0.1:8765/web/visita.html#hiladas renders/previas/2026-11-21_web
```

## Desfase: reproducido, todavía sin corregir

El script permanente `scripts/diagnosticar_desfase_ventanas.py` conserva el
contraste en `datos/diagnostico_desfase_ventanas.json`, con hashes de las
entradas. Produce un recorte local con las lecturas superpuestas en
`renders/previas/2026-11-21_desfase_ventanas.png`. Se ha inspeccionado el
recorte sobre la imagen local de la sección AA-415_23, citada en 0036 como
página 1 del PDF. Aquí no se vuelve a verificar su extracción del PDF.

Con las lecturas manuales existentes, origen 2140 px, cúspide 2050 px y
472,488 px/m, la cúspide queda a +0,190481 m. El generador la sitúa a
−0,165 m: **−0,355481 m**. Una segunda formulación, usando la altura desde
el alféizar y cancelando el origen, da −0,355547 m; los 0,066 mm de diferencia
proceden del redondeo milimétrico del JSON de alzado. También coincide con
el desplazamiento guardado en la ficha del GLB.

La cota −0,165 m reproduce el arco supuesto de 0035: arranque −0,43 m
más radio 0,265 m (`tambor_con_vanos` en `scripts/detalle_visita.py`).
No es una cota medida de la sección. Además, la cúspide exterior del nicho
y la abertura luminosa son bordes diferentes en el recorte; no se debe
tratar el perfil exterior como una medición directa de la luz del vano.

Las 17 crestas superiores leídas quedan por encima del origen elegido.
`perfil_pano` fija el borde superior a cero y limita la junta intermedia
a −0,013 m. Por eso no basta con subir el ápice: hay que revisar juntos el
origen de arranque, el perfil del paño, la abertura y el encuentro con el
campo. Esta comprobación diagnostica las restricciones del generador;
no valida las lecturas manuales ni decide cuál debe cambiarse.

## Continuación acotada

Registrar en un mismo marco la sección y el arranque del modelo de campo,
separando cúspide exterior y borde de luz. Ensayar el encuentro en el sector
00 y comparar desde sala, frontal y lateral antes de repetirlo. Sigue
pendiente una vista oblicua registrada del mismo tramo para las profundidades.
La geometría de presentación no se modifica en esta sesión.
