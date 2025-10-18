"""
FICHIER: app.py
STATUT: PRODUCTION - Point d'entrée principal de l'API Flask
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
from llm_service import call_llm
from rag_service import RAGRetriever
from response_formatter import format_response  # ✅ Ajout
import traceback
import logging

# --- Configuration du logging ---
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# --- Initialisation de Flask et du RAG ---
app = Flask(__name__)
CORS(app)
rag = RAGRetriever("../data")

@app.route("/ask", methods=["POST"])
def ask():
    """
    Endpoint principal : reçoit une question, récupère le contexte via RAG,
    envoie la requête au LLM, et renvoie la réponse enrichie et formatée.
    """
    try:
        # 1️⃣ Récupération de la question
        q = request.json.get("question", "").strip()
        if not q:
            return jsonify({"error": "Aucune question fournie"}), 400

        logging.info(f"[QUESTION] {q}")

        # 2️⃣ Récupération du contexte via RAG
        results = rag.retrieve(q)
        if isinstance(results[0], dict):
            context = "\n".join([r.get("text", "") for r in results])
            sources = [r.get("metadata", {}).get("source", "inconnue") for r in results]
        else:
            context = "\n".join(results)
            sources = ["source inconnue"] * len(results)

        # 3️⃣ Préparation des messages pour le LLM
        messages = [
            {
                "role": "system",
                "content": "Tu es un assistant expert en addictologie. Sois précis, empathique et concis."
            },
            {
                "role": "user",
                "content": f"Contexte : {context}\n\nQuestion : {q}\nRéponse :"
            }
        ]

        # 4️⃣ Appel du modèle LLM
        answer = call_llm(messages)

        # 5️⃣ Formatage intelligent de la réponse
        formatted = format_response(answer, q)

        # 6️⃣ Journalisation + retour enrichi
        logging.info(f"[ANSWER] {formatted['content'][:200]}...")

        return jsonify({
            "question": q,
            "title": formatted["title"],
            "icon": formatted["icon"],
            "answer": formatted["content"],
            "lines_count": formatted["lines_count"],
            "context_used": context,
            "sources": sources
        })

    except Exception as e:
        logging.error(f"[ERROR] {str(e)}")
        traceback.print_exc()
        return jsonify({"error": f"Erreur serveur : {str(e)}"}), 500


@app.route("/health", methods=["GET"])
def health():
    """Simple endpoint de vérification de l’état du serveur."""
    return jsonify({"status": "OK", "message": "Nafass API en ligne"}), 200


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
