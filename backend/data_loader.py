import json
import os

# Répertoire racine des données
DATA_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "data"))

def _load_json_file(path):
    """
    Tente de charger un fichier JSON, sinon renvoie une liste vide.
    """
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"[⚠️] Fichier non trouvé : {path}")
        return []
    except json.JSONDecodeError:
        print(f"[⚠️] Erreur de parsing JSON : {path}")
        return []

def load_data():
    """
    Charge les données de tabac, alcool et drogue depuis /data.
    Si un fichier n'existe pas, une mock data est générée automatiquement.
    """
    themes = ["tabac", "alcool", "drogue"]
    data = {}

    for theme in themes:
        path = os.path.join(DATA_DIR, f"{theme}.json")
        entries = _load_json_file(path)

        # Génère des données fictives si le fichier est vide ou absent
        if not entries:
            entries = [
                {"question": f"Test question {theme} 1", "answer": f"Ceci est une réponse fictive sur {theme}."},
                {"question": f"Test question {theme} 2", "answer": f"Deuxième réponse factice liée à {theme}."}
            ]
            print(f"[ℹ️] Mock data générée pour {theme}.json")

        data[theme] = entries

    return data

def load_training_data():
    """
    Charge les données d'entraînement locales, sinon renvoie des exemples factices.
    """
    path = os.path.join(DATA_DIR, "training_data.json")
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        print("[ℹ️] Mock training data utilisée.")
        return [
            {"prompt": "Comment arrêter de fumer ?", "response": "Mock: Essayez de réduire progressivement et cherchez du soutien."},
            {"prompt": "Quels sont les effets de l'alcool ?", "response": "Mock: Une consommation excessive peut nuire à la santé du foie et du cœur."}
        ]
