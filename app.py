"""
FICHIER: app.py
STATUT: PRODUCTION - Point d'entrée principal de l'API Flask
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
from llm_service import call_llm
from router_service import RouterService
from response_formatter import format_response
from typing import Dict, List, Any, Tuple
import traceback
import logging

# --- Configuration du logging ---
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# --- Initialisation de Flask et du Router ---
app = Flask(__name__)
CORS(app)
router = RouterService()

def generate_greeting_response(question: str) -> Dict[str, Any]:
    """Génère une réponse pour les salutations simples"""
    question_lower = question.lower().strip()
    
    greetings = {
        'bonjour': 'Bonjour ! Je suis Nafass, votre assistant en addictologie. Comment puis-je vous aider aujourd\'hui ?',
        'bonsoir': 'Bonsoir ! Je suis Nafass, spécialiste en addictologie. Que souhaitez-vous savoir ?',
        'salut': 'Salut ! Je suis Nafass, assistant en addictologie. En quoi puis-je vous assister ?',
        'coucou': 'Coucou ! Nafass à votre service pour toute question sur les addictions.',
        'hello': 'Hello ! Je suis Nafass, expert en addictologie. Comment puis-je vous aider ?',
        'ça va': 'Je vais bien, merci ! Et vous ? Je suis prêt à répondre à vos questions sur les addictions.',
        'comment ça va': 'Je fonctionne parfaitement, merci ! En quoi puis-je vous aider concernant les addictions ?',
        'comment vas-tu': 'Je vais bien, prêt à vous aider sur les questions d\'addictologie !',
        'merci': 'Je vous en prie ! N\'hésitez pas si vous avez d\'autres questions sur les addictions.',
        'merci beaucoup': 'Avec plaisir ! Je reste à votre disposition pour toute question addictologique.',
        'ok': 'D\'accord ! Si vous avez des questions sur les addictions, n\'hésitez pas.',
        'au revoir': 'Au revoir ! Prenez soin de vous. Revenez quand vous voulez pour des questions addictologiques.',
        'bye': 'Bye ! N\'hésitez pas à revenir pour des conseils en addictologie.',
        'qui es-tu': 'Je suis Nafass, un assistant spécialisé en addictologie. Je peux vous aider avec des informations sur les addictions, traitements et prévention.',
        'quelle est ton nom': 'Je m\'appelle Nafass, assistant expert en addictologie.',
        'que fais-tu': 'Je fournis des informations et conseils sur les addictions (tabac, alcool, drogues, etc.).',
        'aide': 'Je peux vous aider avec : statistiques de consommation, mécanismes des addictions, traitements, prévention. Que souhaitez-vous savoir ?',
        'help': 'I can help with: addiction statistics, treatment methods, prevention strategies. What would you like to know?'
    }
    
    for key, response in greetings.items():
        if question_lower.startswith(key):
            return {
                "content": response,
                "title": "Salutation",
                "icon": "👋",
                "lines_count": 2
            }
    
    # Réponse par défaut pour les salutations non reconnues
    return {
        "content": "Bonjour ! Je suis Nafass, votre assistant en addictologie. Comment puis-je vous aider concernant les addictions ?",
        "title": "Salutation",
        "icon": "👋", 
        "lines_count": 2
    }

def generate_off_topic_response(question: str) -> Dict[str, Any]:
    """Génère une réponse pour les questions hors sujet"""
    return {
        "content": "Je suis spécialisé dans les questions d'addictologie (tabac, alcool, drogues, dépendances). Pour d'autres sujets, je ne suis pas le plus compétent. Souhaitez-vous plutôt des informations sur les addictions ?",
        "title": "Hors domaine",
        "icon": "🚫",
        "lines_count": 3
    }

@app.route("/ask", methods=["POST"])
def ask():
    """
    Endpoint principal : utilise le Router pour choisir les bons systèmes RAG
    """
    try:
        # 1️⃣ Récupération de la question
        q = request.json.get("question", "").strip()
        if not q:
            return jsonify({"error": "Aucune question fournie"}), 400

        logging.info(f"[QUESTION] {q}")

        # 2️⃣ ROUTAGE INTELLIGENT vers les systèmes RAG appropriés
        routing_result = router.route_question(q)
        analysis = routing_result["question_analysis"]
        
        # 3️⃣ Gestion des cas spéciaux (salutations, hors sujet)
        if analysis["type"] == "greeting":
            formatted = generate_greeting_response(q)
            return jsonify({
                "question": q,
                "title": formatted["title"],
                "icon": formatted["icon"],
                "answer": formatted["content"],
                "lines_count": formatted["lines_count"],
                "context_used": "",
                "sources": [],
                "question_analysis": analysis,
                "methods_used": []
            })
        
        elif analysis["type"] == "off_topic":
            formatted = generate_off_topic_response(q)
            return jsonify({
                "question": q,
                "title": formatted["title"],
                "icon": formatted["icon"],
                "answer": formatted["content"],
                "lines_count": formatted["lines_count"],
                "context_used": "",
                "sources": [],
                "question_analysis": analysis,
                "methods_used": []
            })
        
        # 4️⃣ Vérifier si on a des données pour les questions addictologie
        if not routing_result["context_result"]["has_data"]:
            return jsonify({
                "error": "Aucune information trouvée dans nos bases de données pour cette question"
            }), 404

        # 5️⃣ Préparation des messages pour le LLM avec contexte enrichi
        messages = [
            {
                "role": "system",
                "content": """Tu es Nafass, assistant expert en addictologie. 
                Utilise UNIQUEMENT les informations fournies dans le contexte pour répondre.
                Sois précis, empathique et concis.
                Si le contexte ne contient pas l'information, dis que tu ne sais pas."""
            },
            {
                "role": "user", 
                "content": f"""CONTEXTE DISPONIBLE:
{routing_result['final_context']}

QUESTION: {q}

Réponds en français en utilisant uniquement les informations du contexte."""
            }
        ]

        # 6️⃣ Appel du modèle LLM
        answer = call_llm(messages)

        # 7️⃣ Formatage intelligent de la réponse
        formatted = format_response(answer, q)

        # 8️⃣ Journalisation + retour enrichi
        logging.info(f"[ROUTING] Type: {analysis['type']}")
        logging.info(f"[ANSWER] {formatted['content'][:200]}...")

        return jsonify({
            "question": q,
            "title": formatted["title"],
            "icon": formatted["icon"],
            "answer": formatted["content"],
            "lines_count": formatted["lines_count"],
            "context_used": routing_result["final_context"],
            "sources": routing_result["sources"],
            "question_analysis": analysis,
            "methods_used": routing_result["context_result"]["methods_used"]
        })

    except Exception as e:
        logging.error(f"[ERROR] {str(e)}")
        traceback.print_exc()
        return jsonify({"error": f"Erreur serveur : {str(e)}"}), 500

# [Les autres endpoints restent identiques...]

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)