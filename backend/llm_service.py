"""
FICHIER: llm_service.py
STATUT: PRODUCTION - Service principal pour appels LLM via Hugging Face

FONCTION: Interface unifiée avec fallback automatique:
  1. D'abord chat_completion (API moderne OpenAI-like) 
  2. Puis conversational (API legacy) si échec

ARCHITECTURE: Stable - Aucune modification nécessaire pendant le développement
              du fine-tuning local. Service éprouvé en production.

STRATÉGIE: Robustesse maximale avec double approche et gestion d'erreurs complète
"""

import json
from typing import List, Optional

from huggingface_hub import InferenceClient
from huggingface_hub.errors import HfHubHTTPError


HF_TOKEN = "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"  # <- remplace par ton token
MODEL_ID = "google/gemma-2-9b-it"  # ou TinyLlama/... ou meta-llama/... selon ton choix

# Paramètres par défaut
DEFAULT_MAX_TOKENS =160
DEFAULT_TEMPERATURE = 0.7
DEFAULT_TOP_P = 0.9


def call_llm(
    messages: List[dict],
    model_id: str = MODEL_ID,
    token: Optional[str] = HF_TOKEN,
    max_tokens: int = DEFAULT_MAX_TOKENS,
    temperature: float = DEFAULT_TEMPERATURE,
    top_p: float = DEFAULT_TOP_P,
) -> str:
    """
    Appelle un modèle 'conversational' via InferenceClient.
    messages: liste de dicts [{"role": "system"|"user"|"assistant", "content": "..."}, ...]
    Retourne le texte de l'assistant.
    """
    client = InferenceClient(model=model_id, token=token)

    # 1) Tentative avec chat_completion (API la plus récente)
    try:
        resp = client.chat_completion(
            messages=messages,
            max_tokens=max_tokens,
            temperature=temperature,
            top_p=top_p,
        )
        # Format OpenAI-like: resp.choices[0].message.content
        try:
            return resp.choices[0].message.content
        except Exception:
            # Si la structure diffère, retourner le brut pour inspection
            return json.dumps(resp, ensure_ascii=False, indent=2)
    except AttributeError:
        # Méthode absente dans ta version: on bascule sur conversational
        pass
    except HfHubHTTPError as e:
        # Si le provider rejette la tâche (ex: text-generation), on essaie conversational
        if "Supported task: conversational" in str(e):
            pass
        else:
            return f"⚠️ Erreur Hub: {e}"
    except Exception as e:
        # Autres erreurs: on tentera quand même conversational
        pass

    # 2) Fallback: API conversational
    try:
        # La plupart des providers attendent une liste simple des tours 'user'/'assistant'
        # On filtre/simplifie: prendre les messages en ordre et envoyer au paramètre 'conversation'
        conv = []
        for m in messages:
            role = m.get("role")
            content = m.get("content", "")
            if role in ("system", "user", "assistant"):
                # Certains endpoints ignorent "system"; on peut l’inclure comme préfixe du premier message user
                conv.append({"role": role, "content": content})

        out = client.conversational(
            conversation=conv,
            temperature=temperature,
            max_new_tokens=max_tokens,
            top_p=top_p,
        )

        # Selon les providers, out peut être:
        # - une chaîne directement (réponse)
        # - un dict avec 'generated_text' ou 'answer'
        if isinstance(out, str):
            return out
        if isinstance(out, dict):
            for key in ("generated_text", "answer", "content", "text"):
                if key in out and isinstance(out[key], str):
                    return out[key]
            # Parfois une liste d'objets messages
            if "conversation" in out and isinstance(out["conversation"], list):
                # Chercher le dernier message assistant
                for msg in reversed(out["conversation"]):
                    if isinstance(msg, dict) and msg.get("role") == "assistant" and "content" in msg:
                        return msg["content"]
        # Si format inattendu, retourner JSON
        return json.dumps(out, ensure_ascii=False, indent=2)
    except HfHubHTTPError as e:
        return f"⚠️ Erreur Hub (conversational): {e}"
    except Exception as e:
        return f"⚠️ Erreur InferenceClient (conversational): {e}"


if __name__ == "__main__":
    # Exemple de conversation
    messages = [
        {"role": "system", "content": "Tu es un assistant utile. Réponds en une seule phrase concise."},
        {"role": "user", "content": "Bonjour, peux-tu répondre en une phrase ?"},
    ]

    print(f"Model: {MODEL_ID}")
    answer = call_llm(
        messages=messages,
        model_id=MODEL_ID,
        token=HF_TOKEN,
        max_tokens=64,
        temperature=0.7,
        top_p=0.9,
    )
    print("Réponse:", answer)