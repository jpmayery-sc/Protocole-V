# Environnement pour tests de physique

Instructions rapides (Windows PowerShell):

1. Créer le virtualenv et installer les dépendances (script fourni):

   PowerShell:

   C:/Users/jpmayery/AppData/Local/Programs/Python/Python313/python.exe -m venv .venv
   .\.venv\Scripts\Activate.ps1
   .venv\Scripts\pip.exe install --upgrade pip
   .venv\Scripts\pip.exe install -r requirements.txt

   Ou exécuter le script: .\setup_env.ps1

2. Lancer les tests:

   .\.venv\Scripts\pytest -q

Fichiers créés:
- 
equirements.txt : dépendances
- setup_env.ps1, setup_env.sh : scripts d'installation
- 	ests/test_physics.py : test d'exemple

## Ouvrir dans Colab

Vous pouvez ajouter un badge  Open in Colab pointant vers votre notebook GitHub. Remplacez OWNER, REPO et PATH par vos valeurs réelles :

[![Open in Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/OWNER/REPO/blob/main/PATH)

Pour automatiser le flux: committer et pousser les changements puis ouvrir Colab, utilisez les scripts fournis:

- scripts/open_in_colab.sh (Linux/macOS)
- scripts/open_in_colab.ps1 (Windows PowerShell)

Exemples d'utilisation:

`ash
# push current branch and open notebook in Colab
./scripts/open_in_colab.sh OWNER REPO path/to/notebook.ipynb
`

`powershell
# push current branch and open notebook in Colab
.\scripts\open_in_colab.ps1 -Owner OWNER -Repo REPO -Path path/to/notebook.ipynb
`

**Exécuter les tests localement et récupérer les résultats**

Linux/macOS:
`ash
./scripts/run_tests_and_collect.sh
ls -l results
`

Windows PowerShell:
`powershell
.\scripts\run_tests_and_collect.ps1
Get-ChildItem -Path results
`

Le workflow GitHub Actions .github/workflows/ci.yml exécute aussi pytest sur push/PR et publie les artefacts 
esults (vous pourrez les télécharger depuis la page Actions).
