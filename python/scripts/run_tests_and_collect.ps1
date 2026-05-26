<#
Usage: .\scripts\run_tests_and_collect.ps1
Installe les dépendances (si besoin), exécute pytest et place les résultats dans .\results
#>

if (Test-Path .venv) {
    . .\.venv\Scripts\Activate.ps1
}

python -m pip install --upgrade pip
& .venv\Scripts\pip.exe install -r requirements.txt -ErrorAction SilentlyContinue

New-Item -ItemType Directory -Path results -Force | Out-Null
pytest --junitxml=results/junit.xml -q

Write-Host "Tests exécutés. Résultats disponibles dans .\results (junit.xml)."
