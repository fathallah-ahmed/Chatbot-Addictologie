"""
FICHIER: app.py
STATUT: PRODUCTION - Point d'entrée principal de l'API Flask
"""

from flask import Flask, request, jsonify
from flask_cors import CORS  # AJOUT
from llm_service import call_llm
from rag_service import RAGRetriever

app = Flask(__name__)
CORS(app)  # AJOUT: Autorise toutes les origines

rag = RAGRetriever("../data")

@app.route("/ask", methods=["POST"])
def ask():
    q = request.json.get("question", "")
    if not q:
        return jsonify({"error": "Aucune question fournie"}), 400
    
    context = "\n".join(rag.retrieve(q))
    
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
    
    answer = call_llm(messages)
    
    return jsonify({"answer": answer})

if __name__ == "__main__":
    app.run(debug=True)