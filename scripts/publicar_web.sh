#!/usr/bin/env bash
# Prepara la visita 3D para GitHub Pages (rama gh-pages).
#
# Uso:  scripts/publicar_web.sh            # construye y enseña que se subiria
#       scripts/publicar_web.sh --preparar # deja una copia estática en build/, sin tocar git
#       scripts/publicar_web.sh --subir    # ademas fuerza la rama gh-pages en origin
#
# La rama gh-pages no comparte historia con el resto: cada publicacion la
# sustituye por un unico commit con el sitio, para que las teselas (decenas de
# MB) no se acumulen en el historial. master y las ramas de trabajo no llevan
# las teselas (web/zoom/ esta en .gitignore).
#
# La entrada es la visita 3D autocontenida. Si hay teselas locales, conserva
# también la vista cenital en zoom.html.
set -euo pipefail

raiz="$(git rev-parse --show-toplevel)"
cd "$raiz"
[[ -s web/modelos/dos-hermanas.glb.gz && -s web/modelos/dos-hermanas.json ]] || {
    echo "Falta el modelo de la visita: scripts/exportar_visita_web.py" >&2; exit 1;
}
[[ -s web/modelos/yeso.png ]] || { echo "Falta web/modelos/yeso.png (scripts/textura_yeso_visita.py)" >&2; exit 1; }
if [[ ${1:-} == --preparar ]]; then
    mkdir -p build
    sitio="$(mktemp -d "$raiz/build/visita-XXXXXX")"
else
    sitio="$(mktemp -d)"
    indice="$(mktemp)"
    trap 'rm -rf "$sitio" "$indice"' EXIT
fi
cp web/visita.html "$sitio/index.html"
cp web/visita.js web/yeseria.js web/visita.css "$sitio/"
cp -r web/vendor web/modelos "$sitio/"
if [[ -f web/zoom/cupula_cenital.dzi ]]; then
    cp web/zoom.html web/styles.css "$sitio/"
    cp -r web/zoom "$sitio/zoom"
fi
touch "$sitio/.nojekyll"
if [[ ${1:-} == --preparar ]]; then
    echo "$sitio"
    exit 0
fi

origen="$(git rev-parse --short HEAD)"
echo "sitio: $(find "$sitio" -type f | wc -l) ficheros, $(du -sh "$sitio" | cut -f1); desde $origen"

# Commit huerfano con el arbol del sitio, sin tocar el indice ni el arbol de trabajo del repo.
rm -f "$indice"
export GIT_INDEX_FILE="$indice"
git --work-tree="$sitio" add -A
arbol="$(git write-tree)"
commit="$(git commit-tree "$arbol" -m "Visita 3D de la cúpula, desde $origen")"
unset GIT_INDEX_FILE
git update-ref refs/heads/gh-pages "$commit"
echo "rama gh-pages -> $commit"

if [[ "${1:-}" == "--subir" ]]; then
    git push --force origin gh-pages
    echo "subido. https://$(gh api user -q .login).github.io/$(basename "$raiz")/"
else
    echo "no subido (anadir --subir)"
fi
