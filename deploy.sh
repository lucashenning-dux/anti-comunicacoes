#!/usr/bin/env bash
# Gera o site (site.py) e publica site/ na branch gh-pages, que é o que o
# GitHub Pages serve em https://lucashenning-dux.github.io/anti-comunicacoes/
#
#   ./deploy.sh              gera, publica, mostra o resultado
#   ./deploy.sh --sem-build  pula o site.py e publica o site/ que já está no disco
#
# Idempotente: se nada mudou desde o último deploy, avisa e sai sem criar
# commit vazio nem tocar no branch remoto.
set -euo pipefail
cd "$(dirname "$0")"

URL="https://lucashenning-dux.github.io/anti-comunicacoes/"
WT="$(mktemp -d)/gh-pages-deploy"
trap 'git worktree remove "$WT" --force >/dev/null 2>&1 || true; rm -rf "$(dirname "$WT")"' EXIT

if [[ "${1:-}" != "--sem-build" ]]; then
  echo "==> gerando site/ com site.py"
  python3 site.py
fi

echo "==> preparando worktree da branch gh-pages"
git fetch origin gh-pages --quiet
git worktree add "$WT" gh-pages --quiet

# troca o conteúdo do worktree pelo site/ atual, preservando o git da branch
find "$WT" -mindepth 1 -maxdepth 1 -not -name ".git" -exec rm -rf {} +
cp -R site/. "$WT/"
touch "$WT/.nojekyll"

cd "$WT"
git add -A
if git diff --cached --quiet; then
  echo "==> nada mudou desde o último deploy — nenhum commit criado"
  exit 0
fi

MSG="Deploy: $(date '+%Y-%m-%d %H:%M') — $(cd - >/dev/null && git rev-parse --short HEAD)"
git commit -m "$MSG" --quiet
git push origin gh-pages --quiet

echo "==> publicado: $URL"
echo "    (o GitHub leva alguns segundos para rebuildar; se o link ainda"
echo "    mostrar a versão antiga, aguarde e recarregue)"
