# 0007 — Nivelación aproximada para continuar el modelo

**Estado:** aceptada como reconstrucción operativa — 2026-08-28

## Decisión

Se levanta el bloqueo para la **generación aproximada**, no para la afirmación
de fidelidad histórica. El dato original `datos/caras_red.json` conserva sus
227 saltos sin firmar y el estado `BLOCKED_MISSING_SIGNED_LEVEL_CONSTRAINTS`.
En paralelo, `datos/niveles_aproximados.json` proporciona una hipótesis completa
y trazable con estado `APPROXIMATE_LEVELS_AVAILABLE`.

La cota topológica de cada cara parte de su distancia mínima, en el grafo dual,
a las 16 caras del borde. Hay cinco capas hasta el centro. Se escalan a siete
niveles operativos, cifra atribuida a Martínez Sevilla en la divulgación del
PMAA pero sin método publicado; ocho niveles actúan como sensibilidad. Cada
cara y salto declara si permanece estable al cambiar entre ambos.

Los 23 escalones medidos sobre la sección de Almagro y el recuento rápido de 24
comunicado por Ferrer se conservan como **hiladas del alzado físico**, no se
identifican con los niveles topológicos del grafo. La sección fija además radio
3,64 m, altura 4,67 m, paso horizontal 15,8 cm y paso vertical 20,3 cm.

## Garantías y límites

- Los 227 saltos cierran todos los ciclos por construcción: son diferencias
  de cotas absolutas, no decisiones independientes.
- La salida cubre las 105 caras y permite continuar el levantamiento 3D.
- Todos los saltos inferidos tienen valor absoluto máximo 2, conforme a las
  piezas ordinarias de un nivel, los descansos y las piezas especiales de dos.
- La estabilidad 7/8 mide sensibilidad al número topológico global, no
  exactitud histórica.
- La distancia de grafo es un prior topológico. No identifica tipologías,
  orientaciones ni flechas observadas y puede equivocarse localmente,
  especialmente en piezas mixtas, descansos y piezas de dos niveles.
- Una futura observación fotográfica sustituirá la inferencia correspondiente;
  nunca se presentará esta salida como una restricción firmada.

Reproducción:

```bash
python3 scripts/inferir_niveles_aproximados.py
```
