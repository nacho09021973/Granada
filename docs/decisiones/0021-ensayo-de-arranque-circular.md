# 0021 — Ensayo de condición de borde circular

**Estado:** candidato opcional, 2026-11-17. Solo primera fila B; no sustituye
la colocación ni valida el modelo histórico.

## Pregunta y descarte previo

¿Puede la primera fila conectar con un círculo de arranque de radio
`RADIO_BASE`, sin subir H ni invertir su banda auxiliar? Se descarta el
transporte radial si alguna trayectoria muestreada sube más de 1e-8 catetos
por segmento o si aparecen triángulos invertidos. La cota interpolada del
borde debe quedar a menos de `PENDIENTE * resolucion` de cero y el contorno
H=0 a menos de una celda del círculo. Se contrasta el cono A=0 y se refina
rejilla, número de trayectorias y capas.

## Elección explícita

`campo(borde="circular")` fija el dominio arquitectónico r≤RADIO_BASE.
Después del suavizado multiplica el relieve de la red por
`t²(3−2t)`, con `t=clip((RADIO_BASE−r)/ancho, 0, 1)` y
`ancho=PASO_VERTICAL/PENDIENTE`: un paso horizontal de hilada completa,
independiente de su subdivisión B. Es una elección previa al ensayo, no
una anchura calibrada contra estos resultados.

Así, la fórmula evaluada directamente vale cero en el círculo y conserva
el campo anterior a más de ese ancho del borde. Fuera del dominio se
prolonga el cono con signo negativo únicamente para interpolar y localizar
el nivel cero; esa prolongación no representa piezas ni arquitectura.

El defecto sigue siendo `borde="libre"`. La condición se conserva en
`Campo.borde`. No se ha conectado esta variante al renderizador ni al visor.
No se han modificado A, el color ni la configuración B.

Ni la circularidad completa ni la atenuación proceden de una nueva lectura
de la cúpula. El radio reutiliza el parámetro existente; su imposición como
frontera completa es decisión contemporánea. Los cupulines y sus encuentros
con este dominio siguen pendientes. Una planta de arranque documentada que
contradiga este círculo obliga a retirarlo o reformularlo.

## Resultado reproducido

`scripts/diagnosticar_arranque_campo.py` interpola puntos por longitud de arco
en el primer frente y conecta cada uno radialmente con el círculo. Evalúa
H bilinealmente en la banda y cuenta inversiones incluyendo la junta
periódica. Esto es un ensayo de transporte, no una malla de piezas.

| Campo A=2 | Rejilla, catetos | Trayectorias / capas | Suben H | Triángulos invertidos | Error máximo del radio H=0, m |
|---|---:|---:|---:|---:|---:|
| libre | 0,03 | 129 / 200 | 0 | 0 | 0,399875 |
| libre | 0,015 | 257 / 400 | 5 | 4000 | 0,404515 |
| circular | 0,03 | 129 / 200 | 0 | 0 | 0,000062825 |
| circular | 0,015 | 257 / 400 | 0 | 0 | 0,000015847 |

El campo libre tiene doce contornos H=0. En el muestreo fino, cinco puntos
del primer frente quedan fuera del círculo: conectarlos hacia él invierte
la banda. Se descarta ese transporte radial del campo libre hacia el círculo.
El candidato circular tiene un contorno H=0, ningún inicio fuera del dominio
y todos los extremos radiales sobre el círculo (tolerancia 1e-9 catetos).
El error máximo de H interpolada en el borde baja de 0,000307710 a
0,000085340 catetos al refinar.

El control A=0 circular reproduce el cono con signo evaluado por fórmula;
su error de radio H=0 baja de 1,526e-6 a 3,851e-7 m. Las pruebas contrastan
también que el interior se conserva y el exterior es la prolongación del
cono. El campo libre por defecto conserva sus resultados anteriores.

La reducción del error respalda la consistencia numérica de este ensayo;
dos rejillas no prueban convergencia ni fidelidad histórica. Tampoco se han
estudiado otras anchuras de atenuación, las siete paradas interiores,
intersecciones 3D o los encuentros con los 16 cupulines.

## Reproducción y siguiente paso

```bash
/tmp/granada-venv/bin/python scripts/diagnosticar_arranque_campo.py
/tmp/granada-venv/bin/python -m pytest -q
```

El JSON `datos/diagnostico_arranque_campo.json` conserva criterios,
parámetros, ocho casos, versiones y hashes de código e insumos.
Suite verificada: **766 tests pasan**; `git diff --check` sin errores.

Siguiente: mantener este candidato separado y ensayar el transporte interior
con una derivada compatible con H interpolada, contrastando con la rejilla
más fina. No aplicar el criterio circular a filas interiores ni declarar
resueltas las conexiones de 0019.
