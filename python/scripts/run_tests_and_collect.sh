#!/usr/bin/env bash
set -euo pipefail

# Usage: ./scripts/run_tests_and_collect.sh
# Installe les dépendances (si nécessaire), exécute pytest et place les résultats dans ./results

if [ -d .venv ]; then
  source .venv/bin/activate
fi

python -m pip install --upgrade pip
pip install -r requirements.txt || true

mkdir -p results
pytest --junitxml=results/junit.xml -q

echo "Tests exécutés. Résultats disponibles dans ./results (junit.xml)."
