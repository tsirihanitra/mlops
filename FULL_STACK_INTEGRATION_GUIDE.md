# Guide de Lancement Full-Stack (Jenkins + Harbor + Airflow)

Ce guide explique comment faire fonctionner l'ensemble de la chaîne MLOps pour votre projet Wine Quality.

## 1. Préparation du Registre (Harbor)
- Assurez-vous que votre projet `mlops` est créé dans Harbor à l'adresse `192.168.43.53`.
- Vérifiez que les identifiants sont corrects dans Jenkins (`harbor-credentials`).

## 2. Automatisation CI/CD (Jenkins)
- **Déclenchement** : Poussez votre code sur la branche `main` de votre dépôt Git.
- **Vérification** : Jenkins va :
    1. Lancer les tests unitaires.
    2. Construire l'image Docker (incluant l'entraînement du modèle).
    3. Scanner l'image avec Trivy.
    4. Pousser l'image vers Harbor : `192.168.43.53/mlops/wine-quality:latest`.

## 3. Orchestration et Déploiement (Airflow)
- **Déploiement** : Le DAG `wine_quality_mlops_pipeline` dans Airflow est configuré pour déployer l'application.
- **Mise à jour (Prod)** : Pour utiliser l'image de Harbor en production au lieu de la construction locale :
    - Modifiez `docker-compose.yml` pour décommenter la ligne `image: 192.168.43.53/mlops/wine-quality:latest`.
    - Airflow exécutera `docker compose pull` avant de relancer le conteneur.

## 4. cycle de vie MLOps
1. **Nouvelles données** : Ajoutez des données dans `data/winequality-red.csv`.
2. **Ré-entraînement** : Lancez le pipeline Jenkins (CI) pour créer une nouvelle image avec le modèle mis à jour.
3. **Déploiement** : Activez le DAG Airflow pour mettre à jour votre API de production avec la nouvelle image.

## Commandes Utiles
- **Lancer Airflow** : 
  ```bash
  airflow scheduler & airflow webserver --port 8081
  ```
- **Vérifier les conteneurs** : 
  ```bash
  docker ps
  ```
- **Logs de l'API** : 
  ```bash
  docker compose logs -f app
  ```
