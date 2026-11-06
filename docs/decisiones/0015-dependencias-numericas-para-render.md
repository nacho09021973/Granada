# 0015 — Dependencias numéricas para el render

Fecha: 2026-11-06
Estado: aceptada. Modifica la decisión 0001 («Solo biblioteca estándar»).

## Contexto

La 0001 dejó el proyecto en biblioteca estándar más `pytest`, porque el
núcleo es aritmética exacta en Z[ζ_m] y nada justificaba numpy ni sympy.

La rama `cupula-por-piezas`, fusionada en `main` el 2026-11-06, añade
geometría numérica y render: `granada/cupula.py` y `granada/render3d.py`
importan numpy, y varios scripts usan numpy, Pillow, SciPy y scikit-image.
Ninguna decisión lo registraba, y el repo no declaraba dependencias.

## Decisión

1. Se aceptan numpy, Pillow, SciPy y scikit-image, con versiones fijadas en
   `requirements.txt`, **solo** para geometría numérica, render y análisis de
   imagen.
2. La parte exacta (`granada/cyclotomic.py` y los módulos de malla, caras,
   niveles y perfil) sigue en biblioteca estándar. Lo que la 0001 protegía
   —que la exactitud se pueda leer entera sin seguir la pista a una
   dependencia— se mantiene ahí.
3. El render físico usa Blender con Cycles, instalado fuera de pip; en la
   máquina local, GPU NVIDIA (`--dispositivo optix` o `cuda`).

## Consecuencias

- Instalar el repo completo pide `pip install -r requirements.txt`.
- Un módulo del núcleo exacto que importe numpy rompe esta decisión.
