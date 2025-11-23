# 📊 Assistant d'Aide à la Décision - Prédictions Géospatiales

> Système intelligent d'analyse de demande pour produits électroniques avec IA (OpenAI GPT-4 + Streamlit)

**Dernière mise à jour** : 23 novembre 2025 à 10h00

---

## 🚀 Démarrage Rapide

### Installation Locale (Recommandé)

```bash
# 1. Aller dans le dossier LLM
cd LLM

# 2. Installer les dépendances
pip install -r requirements.txt

# 3. Créer le fichier .env avec votre clé API OpenAI
echo "OPENAI_API_KEY=sk-votre-cle-api-ici" > .env
# Ou copier depuis la racine si déjà configuré
cp ../.env .env

# 4. Lancer l'application
cd app
streamlit run streamlit_app.py
```

**Accès** : `http://localhost:8501`

> ⚠️ **Important** : Remplacez `sk-votre-cle-api-ici` par votre vraie clé API OpenAI

### Alternative Docker

```bash
# Construire et lancer
docker-compose build
docker-compose up -d

# Voir les logs
docker-compose logs -f
```

---

## 💡 Fonctionnalités

### Questions Supportées

```
✓ Où augmenter les stocks de ThinkPad Laptop ?
✓ Compare la demande entre Dallas et Austin
✓ Quelle ville montre la plus forte progression ?
✓ Top 5 des villes avec la plus forte demande
```

### Capacités

- 🤖 **Chat IA** avec OpenAI GPT-4o-mini
- 📊 **Visualisations** interactives (Plotly)
- 📈 **Analyses** de croissance et comparaisons
- 🎯 **Recommandations** d'approvisionnement

---

## 📁 Structure

```
produit-geospatial/
├── notebook/                    # Génération des prédictions XGBoost
│   └── product_geospatial.ipynb
├── prediction/                  # Données CSV
│   ├── predictions_3_mois.csv   # Agrégation mensuelle
│   └── predictions_60_jours.csv # Prédictions journalières
└── LLM/                         # Application Streamlit
    ├── app/                     # Code source
    ├── config/                  # Configuration
    └── requirements.txt         # Dépendances
```

---

## 🔧 Technologies

- **Prédictions** : Python, XGBoost, Pandas, Scikit-learn
- **IA** : OpenAI GPT-4o-mini
- **Interface** : Streamlit, Plotly
- **Déploiement** : Docker, Docker Compose

---

## 📊 Données

- **Produits** : ThinkPad Laptop, AAA Batteries (4-pack)
- **Villes** : 10 villes US (San Francisco, New York, Dallas, etc.)
- **Période de prédiction** : 3 mois apres dernier date historiques
---

## ⚙️ Configuration

### Variables d'Environnement

**Pour l'installation locale :**

Créer le fichier `LLM/.env` :

```bash
cd LLM
echo "OPENAI_API_KEY=sk-votre-cle-api-ici" > .env
```

**Pour Docker :**

Le fichier `.env` existe déjà à la racine du projet. Vérifiez qu'il contient :

```bash
OPENAI_API_KEY=sk-votre-cle-api-ici
```

> 🔑 **Obtenir une clé API** : [platform.openai.com/api-keys](https://platform.openai.com/api-keys)

### Configuration LLM

```yaml
# LLM/config/llm_config.yaml
llm:
  model: "gpt-4o-mini"
  temperature: 0.1
  max_tokens: 2000
```

---

## 🚨 Dépannage

### Vérifier la Configuration

**Vérifier que le fichier .env existe et contient la clé API :**

```bash
# Pour local
cat LLM/.env

# Pour Docker
cat .env

# Doit afficher:
# OPENAI_API_KEY=sk-proj-...
```

### Application Locale

```bash
# Tester l'environnement
cd LLM
python test_setup.py

# Vérifier les dépendances
pip list | grep streamlit
```

### Docker

```bash
# Voir les logs
docker-compose logs -f

# Reconstruire
docker-compose build --no-cache
docker-compose up -d
```


---

## ✅ Status

- ✅ Prédictions XGBoost optimisées
- ✅ Assistant IA fonctionnel
- ✅ Interface Streamlit interactive
- ✅ Visualisations Plotly
- ✅ Documentation complète
