#!/usr/bin/env bash
# Publica el visor de zoom profundo en GitHub Pages (rama gh-pages).
#
# Uso:  scripts/publicar_web.sh            # construye y enseña que se subiria
#       scripts/publicar_web.sh --subir    # ademas fuerza la rama gh-pages en origin
#
# La rama gh-pages no comparte historia con el resto: cada publicacion la
# sustituye por un unico commit con el sitio, para que las teselas (decenas de
# MB) no se acumulen en el historial. master y las ramas de trabajo no llevan
# las teselas (web/zoom/ esta en .gitignore).
#
# Se publica solo el visor de zoom: las otras paginas de web/ leen ../datos y
# ../renders, que no forman parte del sitio.
#
# Requisito: teselas en web/zoom/ (scripts/teselar_dzi.py).
set -euo pipefail

raiz="$(git rev-parse --show-toplevel)"
cd "$raiz"
[[ -f web/zoom/cupula_cenital.dzi ]] || { echo "faltan las teselas: scripts/teselar_dzi.py" >&2; exit 1; }

sitio="$(mktemp -d)"
indice="$(mktemp)"
trap 'rm -rf "$sitio" "$indice"' EXIT

mkdir -p "$sitio/vendor"
cp web/zoom.html "$sitio/index.html"
cp web/styles.css "$sitio/"
cp web/vendor/openseadragon.min.js "$sitio/vendor/"
cp -r web/zoom "$sitio/zoom"
touch "$sitio/.nojekyll"

origen="$(git rev-parse --short HEAD)"
echo "sitio: $(find "$sitio" -type f | wc -l) ficheros, $(du -sh "$sitio" | cut -f1); desde $origen"

# Commit huerfano con el arbol del sitio, sin tocar el indice ni el arbol de trabajo del repo.
rm -f "$indice"
export GIT_INDEX_FILE="$indice"
git --work-tree="$sitio" add -A
arbol="$(git write-tree)"
commit="$(git commit-tree "$arbol" -m "Visor de zoom de la cupula, desde $origen")"
unset GIT_INDEX_FILE
git update-ref refs/heads/gh-pages "$commit"
echo "rama gh-pages -> $commit"

if [[ "${1:-}" == "--subir" ]]; then
    git push --force origin gh-pages
    echo "subido. https://$(gh api user -q .login).github.io/$(basename "$raiz")/"
else
    echo "no subido (anadir --subir)"
fi
