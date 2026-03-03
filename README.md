# 🏥 Nafass-ChatBot - Assistant Intelligent en Addictologie

[![Python 3.12](https://img.shields.io/badge/Python-3.12-blue.svg)](https://www.python.org/)
[![Hugging Face](https://img.shields.io/badge/Hugging%20Face-Transformers-yellow.svg)](https://huggingface.co/)
[![Flask](https://img.shields.io/badge/Flask-API-green.svg)](https://flask.palletsprojects.com/)
[![License](https://img.shields.io/badge/License-MIT-lightgrey.svg)](LICENSE)

## 📖 Description

**Nafass-ChatBot** est un assistant conversationnel intelligent spécialisé dans l'accompagnement et la prévention des addictions (tabac, alcool, cannabis). Le système combine des techniques avancées de NLP avec une base de connaissances médicale validée pour fournir des réponses précises et empathiques.

### 🎯 Objectifs Principaux

🤖 Assistance 24/7 : Offrir un soutien continu et confidentiel aux utilisateurs.

🎓 Éducation Santé : Diffuser des informations médicales validées (OMS, Santé.gouv).

🔒 Confidentialité : Traitement local des données sensibles.

🚀 Adaptabilité : Fine-tuning du modèle IA sur le domaine médical français.

🧠 Surveillance IA : Évaluer la qualité des réponses et détecter automatiquement les anomalies.

## 🏗️ Architecture Technique

### 🧠 Double Approche Modèle

| Composant | Modèle | Usage | Spécialité |
|-----------|--------|-------|------------|
| **Fine-tuning LoRA** | `google/flan-t5-small` | Réponses rapides | Addictologie |
| **LLM de Référence** | `google/gemma-2-9b-it` | Questions complexes | Généraliste + contexte |

### RAG Hybride — Architecture d’Intelligence Documentaire
Description

Le projet intègre deux services complémentaires :

rag_service.py — Récupération contextuelle simple basée sur la similarité textuelle.

rag_vector_service.py — Récupération vectorielle avancée basée sur FAISS et l’analyse sémantique des ressources fiables (PDF scientifiques et gouvernementaux).
📚 Données utilisées

Les données sont issues du dossier :/data/ressources_fiables/
⚙️ Fonctionnement

Lorsqu’une question ne nécessite pas de sources externes, le RAG standard génère la réponse contextuelle.

Si la question implique une donnée scientifique, statistique ou chiffrée, le RAG vectoriel est automatiquement sollicité.

En cas de requête mixte, les deux services collaborent : les chunks du vector store et les contextes du RAG standard sont fusionnés avant l’appel au modèle LLM.
| Service                 | Rôle                                                              | Fichiers principaux                                |
| ----------------------- | ----------------------------------------------------------------- | -------------------------------------------------- |
| `ingestion_service.py`  | Indexe les PDF, extrait les *chunks* et construit l’index FAISS   | `data/vector_store/`                               |
| `rag_vector_service.py` | Interroge l’index FAISS, renvoie les passages les plus pertinents | `vectorindex.faiss`, `metadata.json`, `chunks.pkl` |
| `rag_service.py`        | Fournit un contexte textuel basé sur les données locales          | `data/`                                            |
| `app.py`                | Orchestration globale entre les services RAG et LLM               | —                                                  |

## 🛠️ Stack Technique

### 🤖 Machine Learning & NLP

- Hugging Face Transformers
- PEFT & LoRA (Parameter-Efficient Fine-Tuning)
- Sentence Transformers
- scikit-learn (IsolationForest)
- FAISS (Facebook AI Similarity Search)
🌐 API 
- Flask (API REST)

### Installation & Démarrage
# 1. Cloner le repository
git clone https://github.com/fathallah-ahmed/Chatbot-Addictologie
cd Nafass-ChatBot

# 2. Installer les dépendances
python -m pip install -r requirements.txt

# 3. Exécuter la suite de tests backend
python -m pytest backend/tests -q

Vous devriez voir un résumé similaire à :

```
..........  [100%]
10 passed in 0.11s
```

Si `pytest` n'est pas installé en tant que commande, cette invocation via `python -m` fonctionne sur Windows.

# 4. Lancer l'API
python app.py
Utilisation API - postman
http://127.0.0.1:5000/ask
{
    "question": "entrer votre prompt"
}
"Nafass-ChatBot : un assistant IA pour l’accompagnement addictologique intelligent et responsable."
— Équipe Nafass, 2025
