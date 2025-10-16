"""
FICHIER: rag_service.py
STATUT: PRODUCTION - Système RAG (Retrieval-Augmented Generation)

FONCTION: Recherche sémantique dans la base de connaissances des addictions
ARCHITECTURE: Embeddings + FAISS pour la recherche vectorielle
MODÈLE: all-MiniLM-L6-v2 (optimisé pour le français, léger et performant)

STRATÉGIE: Indexation des réponses existantes pour enrichir le contexte du LLM
AVANTAGE: Réponses précises basées sur des données validées, réduit les hallucinations
"""
from sentence_transformers import SentenceTransformer
import numpy as np, faiss, json, os

class RAGRetriever:
    def __init__(self, data_path="../data"):
        self.model = SentenceTransformer("all-MiniLM-L6-v2")
        self.docs, self.index = [], None
        self._load_data(data_path)

    def _load_data(self, data_path):
        texts = []
        for file in os.listdir(data_path):
            if file.endswith(".json"):
                with open(os.path.join(data_path, file), encoding="utf-8") as f:
                    try:
                        d = json.load(f)
                        for e in d:
                            answer = e.get("answer")
                            if answer:
                                texts.append(answer)
                    except json.JSONDecodeError:
                        print(f"Erreur JSON dans {file}")
        self.docs = texts

        if texts:
            emb = self.model.encode(texts)
            self.index = faiss.IndexFlatL2(emb.shape[1])
            self.index.add(np.array(emb))
        else:
            print("Aucune donnée chargée depuis", data_path)

    def retrieve(self, query, top_k=2):
        if not self.docs:
            return ["Aucun document disponible"]
        q_emb = self.model.encode([query])
        _, idxs = self.index.search(q_emb, top_k)
        return [self.docs[i] for i in idxs[0]]
