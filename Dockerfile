# Dockerfile pour l'Assistant d'Aide à la Décision

FROM python:3.9-slim

# Installer curl pour le healthcheck
RUN apt-get update && apt-get install -y curl && rm -rf /var/lib/apt/lists/*

# Définir le répertoire de travail
WORKDIR /app

# Copier les fichiers de requirements
COPY LLM/requirements.txt .

# Installer les dépendances avec timeout plus long
RUN pip install --no-cache-dir --default-timeout=100 -r requirements.txt

# Copier l'application
COPY LLM/app ./app
COPY LLM/config ./config
COPY prediction ./prediction

# Exposer le port Streamlit
EXPOSE 8501

# Healthcheck
HEALTHCHECK CMD curl --fail http://localhost:8501/_stcore/health || exit 1

# Commande de démarrage
CMD ["streamlit", "run", "app/streamlit_app.py", "--server.port=8501", "--server.address=0.0.0.0"]
