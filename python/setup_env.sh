#!/usr/bin/env bash
PYTHON=${PYTHON:-python3}

# Usage: ./setup_env.sh [start_colab_runtime]
if [ "$1" = "start_colab_runtime" ]; then
	echo "Starting Jupyter server for Colab local runtime..."
	jupyter notebook --NotebookApp.allow_origin='https://colab.research.google.com' --port=8888 --NotebookApp.token='' --NotebookApp.disable_check_xsrf=True
	exit 0
fi

$PYTHON -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
# Ensure jupyter and the websocket bridge are available for Colab local runtime
pip install jupyter jupyter_http_over_ws
jupyter serverextension enable --py jupyter_http_over_ws || true

echo "Virtualenv créé dans .venv et dépendances installées. Activez-le avec: source .venv/bin/activate"
echo "Pour démarrer un serveur Jupyter utilisable par Colab: ./setup_env.sh start_colab_runtime"
