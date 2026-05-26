$python = 'C:/Users/jpmayery/AppData/Local/Programs/Python/Python313/python.exe'

# Usage: .\setup_env.ps1 [start_colab_runtime]
if ($args.Count -ge 1 -and $args[0] -eq 'start_colab_runtime') {
	Write-Host 'Starting Jupyter server for Colab local runtime...'
	jupyter notebook --NotebookApp.allow_origin='"https://colab.research.google.com"' --port=8888 --NotebookApp.token='' --NotebookApp.disable_check_xsrf=True
	exit
}

& $python -m venv .venv
$pip = Join-Path -Path (Resolve-Path .venv\Scripts) -ChildPath pip.exe
& $pip install --upgrade pip
& $pip install -r requirements.txt
& $pip install jupyter jupyter_http_over_ws
try {
	jupyter serverextension enable --py jupyter_http_over_ws
} catch {
	# ignore if enabling fails
}

Write-Host "Virtualenv créé dans .venv et dépendances installées. Activez-le avec: .\.venv\Scripts\Activate.ps1"
Write-Host "Pour démarrer un serveur Jupyter utilisable par Colab: .\setup_env.ps1 start_colab_runtime"
