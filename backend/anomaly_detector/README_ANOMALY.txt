# 🚨 Dossier : Anomaly Detector
Ce dossier regroupe les modules d’analyse et de détection d’anomalies du projet Nafass ChatBot.

## Objectif
Surveiller la qualité, la stabilité et la sécurité du projet à travers deux niveaux d’analyse :
1. **Analyse sémantique du code (CodeBERT)**
2. **Détection statistique de performance (IsolationForest)**

Ces modules permettent de détecter des incohérences logiques dans le code et des anomalies dans les performances du modèle IA.

## Contenu
- `codebert_detector.py` : vérifie la cohérence logique du code à l’aide du modèle CodeBERT.
- `isolation_forest_detector.py` : détecte les anomalies statistiques dans les performances du modèle.
- `run_anomaly_scan.py` : orchestre les deux approches et génère un rapport global.
- `results/` : dossier contenant les fichiers JSON de détection.

## Pipeline général
Code source → CodeBERT → IsolationForest → Rapport consolidé

## Outils utilisés
- **CodeBERT (Hugging Face)** : compréhension sémantique du code.
- **IsolationForest (scikit-learn)** : détection d’outliers statistiques dans les performances IA.

## Exemple de fonctionnement
1. CodeBERT analyse un extrait du code pour repérer des incohérences sémantiques.
2. IsolationForest détecte les anomalies dans les mesures de performance (ex : latence, perte, perplexité).
3. Les résultats combinés sont enregistrés dans `results/anomaly_report.json`.

## Commande de lancement
```bash
python backend/anomaly_detector/run_anomaly_scan.py
