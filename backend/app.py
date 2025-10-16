"""
FICHIER: app.py
STATUT: PRODUCTION - Point d'entrée principal de l'API Flask

FONCTION: Exposition des endpoints REST pour le chatbot d'addictions
ARCHITECTURE: API Flask avec intégration RAG + LLM
ENDPOINT: /ask (POST) - Réception des questions et retour des réponses contextualisées

FLUX: Question → RAG  → LLM (génération) → Réponse enrichie
Validation des entrées + gestion d'erreurs complète
"""

from flask import Flask, request, jsonify
from llm_service import call_llm
from rag_service import RAGRetriever

app = Flask(__name__)
rag = RAGRetriever("../data")  # assure-toi que le chemin ../data est correct

@app.route("/ask", methods=["POST"])
def ask():
    q = request.json.get("question", "")
    if not q:
        return jsonify({"error": "Aucune question fournie"}), 400
    
    context = "\n".join(rag.retrieve(q))
    
    # CORRECTION : Utiliser le format LISTE de messages attendu par call_llm
    messages = [
        {
            "role": "system", 
            "content": "Tu es un assistant utile. Réponds en utilisant le contexte fourni."
        },
        {
            "role": "user", 
            "content": f"Contexte : {context}\n\nQuestion : {q}\nRéponse :"
        }
    ]
    
    answer = call_llm(messages)  # Maintenant on passe une liste, pas une string
    
    return jsonify({"answer": answer})

if __name__ == "__main__":
    app.run(debug=True)