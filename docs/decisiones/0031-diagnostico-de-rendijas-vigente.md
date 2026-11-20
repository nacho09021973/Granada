# 0031 — Rendijas del modelo vigente: diagnóstico en planta

**Estado:** diagnóstico, 2026-11-19. Sin cambio de geometría por defecto.

## Pregunta y criterio previo

La hoja de ruta pide revisar las rendijas visibles sobre fondo claro. El
informe anterior (`datos/cierres_campo.json`) usa A=2 lineal y no representa
el modelo vigente, A=3 raíz con borde octogonal.

Primero se comprueba si el recuento en planta es suficientemente estable
frente al refinamiento para orientar una corrección. Si cambia al refinar,
se descarta usar el número de componentes como criterio de reparación.
Esto no comprueba las juntas en alzado ni entre piezas de una misma banda.

## Reproducción

```bash
.venv/bin/python scripts/render_hilada_campo.py --hiladas todas --informe-cierres datos/cierres_campo_actual.json
.venv/bin/python scripts/render_hilada_campo.py --hiladas todas --paso-rejilla-cierres 1 --informe-cierres datos/cierres_campo_actual_fina.json
.venv/bin/python -m pytest tests/test_cierres_campo.py -q
```

El script conserva borde, paso, versiones y hashes de las fuentes locales.
Se mantiene el umbral físico de área de rendija: 0,0144 catetos², cuatro
nodos de la rejilla habitual o dieciséis de la fina. Se refina solo la
cobertura; el campo sigue a 0,03 catetos.

| Paso de cobertura (catetos) | Huecos para cierre | Componentes de rendija | Área total de rendija (catetos²) |
|---|---:|---:|---:|
| 0,06 | 65 | 69 | 7,2108 |
| 0,03 | 75 | 42 | 6,8175 |

El área incluye también componentes por debajo del umbral de recuento.
La clasificación morfológica entre hueco y rendija se recalcula en cada
rejilla; los componentes no son objetos emparejados entre ambas salidas.
Las filas 18, 25 y 26 concentran los componentes en ambas resoluciones.
Los cinco tests de cierres pasan.

## Conclusión y límite

El recuento depende de la rasterización: 69 pasa a 42 aun manteniendo el
área mínima. No hay base para convertir cada componente en un parche ni
para seguir citando las 48 rendijas del modelo anterior como estado vigente.

La cobertura usa las curvas de frente y fondo de cada banda, antes del
recorte de piezas por los marcos de los cupulines. No mide la malla final,
la impermeabilidad de los sólidos ni las aberturas que solo se ven en alzado.
Queda pendiente localizar las juntas visibles sobre el render y contrastar
sus bordes en 3D antes de modificar la colocación. No se declara arreglado.
