# Prédiction de Réussite Scolaire 🎓

Ce projet implémente une solution complète de **Machine Learning** (MLOps) pour prédire la réussite scolaire des élèves du secondaire (note G3). Il intègre et déploie un modèle prédictif dans une architecture conteneurisée, monitorée et orchestrée.

## Architecture & Technologies

Le projet repose sur une stack moderne et robuste :

- **API** : [FastAPI](https://fastapi.tiangolo.com/) (Inférence, Instrumentation Prometheus, MLFlow tracking)
- **Frontend** : [Streamlit](https://streamlit.io/) (Interface Utilisateur interactive pour saisir les données et visualiser les résultats)
- **Orchestration** : [Prefect](https://www.prefect.io/) (Gestion des flux de ré-entraînement automatique)
- **Tracking** : [MLFlow](https://mlflow.org/) (Versioning des modèles et logs des prédictions)
- **Monitoring** :
  - [Prometheus](https://prometheus.io/) (Collecte des métriques)
  - [cAdvisor](https://github.com/google/cadvisor) (Métriques des conteneurs - compatible Debian 13/cgroupv2)
  - [Grafana](https://grafana.com/) (Dashboards de visualisation)
- **Proxy** : [Traefik](https://traefik.io/) (Reverse Proxy, SSL termination, et routage)
- **Infrastructure** : Docker / Podman Compose

## Installation & Démarrage

### Prérequis

- Docker ou Podman
- Docker Compose ou Podman Compose

### Démarrage Rapide

1. Cloner ce dépôt.
2. Aller dans le dossier de déploiement :
   ```bash
   cd deployment
   ```
3. Lancer la stack complète :

   ```bash
   # Avec Podman
   podman-compose up -d --build

   # Ou avec Docker
   docker-compose up -d --build
   ```

## 🌐 Accès aux Services

Une fois la stack démarrée, les services sont accessibles via les URLs configurées (Traefik) :

| Service        | URL                                            | Description                                |
| :------------- | :--------------------------------------------- | :----------------------------------------- |
| **Frontend**   | `https://simplon.votre-domaine.com`            | Interface principale pour les utilisateurs |
| **API Docs**   | `https://simplon-api.votre-domaine.com/docs`   | Swagger UI pour tester l'API               |
| **Grafana**    | `https://simplon-grafana.votre-domaine.com`    | Monitoring (Login: `admin` / `picoro`)     |
| **Prefect**    | `https://simplon-prefect.votre-domaine.com`    | Dashboard d'orchestration des flux         |
| **MLFlow**     | `https://simplon-mlflow.votre-domaine.com`     | Experiment Tracking & Model Registry       |
| **Prometheus** | `https://simplon-prometheus.votre-domaine.com` | Accès brut aux métriques                   |

## 🧪 Fonctionnalités Clés

1. **Prédiction en Temps Réel** : via le Frontend ou l'API directe.
2. **Administration & Ré-entraînement** : Une page "Administration" sur le frontend permet de déclencher le ré-entraînement du modèle sur de nouvelles données.
3. **Automatic Versioning** : Chaque ré-entraînement génère un nouveau modèle (`model_TIMESTAMP.pkl`) automatiquement chargé par l'API.
4. **Full Observability** : Suivi des performances API (RPS, Latence) et des ressources système (CPU/RAM conteneurs).

## 📝 Auteurs & Contexte

Projet réalisé dans le cadre de la certification **Simplon - Développeur IA**.
Objectif : Mettre en production un modèle de ML dans un environnement réaliste et contraint.
