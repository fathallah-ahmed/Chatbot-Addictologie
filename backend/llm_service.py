"""
FICHIER: llm_service.py
STATUT: PRODUCTION - Service principal pour appels LLM via Hugging Face

FONCTION: Interface unifiée avec fallback automatique:
  1. D'abord chat_completion (API moderne OpenAI-like)
  2. Puis conversational (API legacy) si échec

ARCHITECTURE: Stable et robuste, utilisée pour la génération de réponses contextuelles
              dans le projet Nafass ChatBot.
STRATÉGIE: Réponses précises, empathiques et contextualisées grâce à un prompt système enrichi.
"""

import json
from typing import List, Optional
from huggingface_hub import InferenceClient
from huggingface_hub.errors import HfHubHTTPError

# --- Configuration du modèle ---
HF_TOKEN = "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"  # ⚠️ Remplacer par ton token Hugging Face
MODEL_ID = "google/gemma-2-9b-it"  # Tu peux aussi utiliser TinyLlama ou Mistral selon la perf souhaitée

# --- Paramètres par défaut ---
DEFAULT_MAX_TOKENS = 160
DEFAULT_TEMPERATURE = 0.65  # Moins de variabilité → plus de cohérence
DEFAULT_TOP_P = 0.92
DEFAULT_SYSTEM_PROMPT = (
    "Tu es Nafass, un assistant empathique et expert en addictologie. "
    "Réponds en français clair et professionnel. "
    "Tes réponses doivent être précises, bienveillantes et scientifiquement fiables. "
    "Ne répète pas la question, ne mentionne pas tes sources sauf si on te le demande explicitement."
)

def call_llm(
    messages: List[dict],
    model_id: str = MODEL_ID,
    token: Optional[str] = HF_TOKEN,
    max_tokens: int = DEFAULT_MAX_TOKENS,
    temperature: float = DEFAULT_TEMPERATURE,
    top_p: float = DEFAULT_TOP_P,
) -> str:
    """
    Appelle un modèle de langage via Hugging Face avec fallback automatique.
    Gère à la fois l’API 'chat_completion' (nouvelle) et 'conversational' (ancienne).
    """
    if not token:
        raise ValueError("Le token Hugging Face (HF_TOKEN) n'est pas défini. Configure-le avant utilisation.")

    client = InferenceClient(model=model_id, token=token)

    # --- Tentative 1 : API moderne chat_completion ---
    try:
        resp = client.chat_completion(
            messages=messages,
            max_tokens=max_tokens,
            temperature=temperature,
            top_p=top_p,
        )
        try:
            return resp.choices[0].message.content.strip()
        except Exception:
            return json.dumps(resp, ensure_ascii=False, indent=2)
    except AttributeError:
        pass
    except HfHubHTTPError as e:
        if "Supported task: conversational" not in str(e):
            return f"⚠️ Erreur HuggingFace API: {e}"
    except Exception:
        pass

    # --- Tentative 2 : Fallback API conversationnelle ---
    try:
        conv = [{"role": m.get("role"), "content": m.get("content", "")} for m in messages]
        out = client.conversational(
            conversation=conv,
            temperature=temperature,
            max_new_tokens=max_tokens,
            top_p=top_p,
        )

        if isinstance(out, str):
            return out.strip()
        if isinstance(out, dict):
            for key in ("generated_text", "answer", "content", "text"):
                if key in out and isinstance(out[key], str):
                    return out[key].strip()
            if "conversation" in out and isinstance(out["conversation"], list):
                for msg in reversed(out["conversation"]):
                    if isinstance(msg, dict) and msg.get("role") == "assistant" and "content" in msg:
                        return msg["content"].strip()
        return json.dumps(out, ensure_ascii=False, indent=2)
    except HfHubHTTPError as e:
        return f"⚠️ Erreur HuggingFace (conversational): {e}"
    except Exception as e:
        return f"⚠️ Erreur InferenceClient: {e}"


# --- Mode test local ---
if __name__ == "__main__":
    messages = [
        {"role": "system", "content": DEFAULT_SYSTEM_PROMPT},
        {"role": "user", "content": "Quels sont les effets du tabac sur la santé mentale ?"},
    ]

    print(f"🧠 Modèle : {MODEL_ID}")
    print("📤 Envoi de la requête au LLM...")

    answer = call_llm(
        messages=messages,
        model_id=MODEL_ID,
        token=HF_TOKEN,
        max_tokens=160,
        temperature=DEFAULT_TEMPERATURE,
        top_p=DEFAULT_TOP_P,
    )

    print("✅ Réponse :\n", answer)
