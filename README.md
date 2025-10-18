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

### 🔍 Système RAG (Retrieval-Augmented Generation)
Question → RAG (Recherche) → Contexte → LLM → Réponse Contextualisée

- **Embeddings** : `all-MiniLM-L6-v2` (optimisé français)
- **Base Vectorielle** : FAISS pour recherche rapide
- **Sources** : Données OMS, INCa, santé.gouv

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
git clone https://github.com/Mey-Youssef/NAFASS.git
cd Nafass-ChatBot

# 2. Installer les dépendances
python -m pip install -r requirements.txt

# 3. Lancer l'API
python app.py
Utilisation API - postman
http://127.0.0.1:5000/ask
{
    "question": "entrer votre prompt"
}
"Nafass-ChatBot : un assistant IA pour l’accompagnement addictologique intelligent et responsable."
— Équipe Nafass, 2025
