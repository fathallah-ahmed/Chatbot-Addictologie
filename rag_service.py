"""
rag_service.py (amélioré)
- Chunking, métadonnées, embeddings persistés
- FAISS Index optimisé pour similarité cosinus (IndexFlatIP + normalisation)
- Retrieval dense + MMR (diversity)
- Optionnel re-ranking via cross-encoder
- API: rebuild_index(), add_documents(), retrieve_with_scores()
"""

import os
import json
import math
import numpy as np
import faiss
from typing import List, Dict, Any, Optional
from sentence_transformers import SentenceTransformer, util

# CONFIG
EMBEDDING_MODEL = os.getenv("RAG_EMBEDDING_MODEL", "all-MiniLM-L6-v2")
CROSS_ENCODER_MODEL = os.getenv("RAG_CROSS_ENCODER", "cross-encoder/ms-marco-MiniLM-L-6-v2")
DATA_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "data"))
INDEX_DIR = os.path.join(os.path.dirname(__file__), "faiss_index")
INDEX_FILE = os.path.join(INDEX_DIR, "rag.index")
EMBEDDINGS_FILE = os.path.join(INDEX_DIR, "embeddings.npy")
METADATA_FILE = os.path.join(INDEX_DIR, "metadata.json")
CHUNK_SIZE = 250      # tokens/words approx (tuneable)
CHUNK_OVERLAP = 50
TOP_K = 8             # retrieval top-k
MMR_LAMBDA = 0.6      # trade-off relevance/diversity (0..1)
USE_CROSS_ENCODER = True  # set False to avoid loading the cross-encoder (faster)

# Initialize embedding model (global)
_embed_model = SentenceTransformer(EMBEDDING_MODEL)
_cross_encoder = None
if USE_CROSS_ENCODER:
    try:
        from sentence_transformers import CrossEncoder
        _cross_encoder = CrossEncoder(CROSS_ENCODER_MODEL)
    except Exception as e:
        print("[RAG] Warning: Cross-encoder unavailable:", e)
        _cross_encoder = None


def _ensure_index_dir():
    os.makedirs(INDEX_DIR, exist_ok=True)


def _normalize_embeddings(emb: np.ndarray) -> np.ndarray:
    """Normalize vectors for cosine similarity with IndexFlatIP"""
    norms = np.linalg.norm(emb, axis=1, keepdims=True)
    norms[norms == 0] = 1e-9
    return emb / norms


def _chunk_text(text: str, chunk_size: int = CHUNK_SIZE, overlap: int = CHUNK_OVERLAP) -> List[str]:
    """
    Chunk a long text into overlapping chunks roughly by words.
    This is a simple heuristic (by words), suitable for small docs.
    """
    words = text.split()
    chunks = []
    i = 0
    while i < len(words):
        chunk = words[i:i+chunk_size]
        chunks.append(" ".join(chunk))
        i += chunk_size - overlap
    return chunks


class RAGRetriever:
    def __init__(self, data_path: str = DATA_DIR, rebuild: bool = False):
        _ensure_index_dir()
        self.data_path = data_path
        self.model = _embed_model
        self.docs: List[str] = []
        self.metadata: List[Dict[str, Any]] = []
        self.index: Optional[faiss.Index] = None

        if os.path.exists(INDEX_FILE) and os.path.exists(EMBEDDINGS_FILE) and not rebuild:
            self._load_index()
        else:
            self.rebuild_index()

    # -----------------------
    # Index / persistence
    # -----------------------
    def _load_index(self):
        try:
            print("[RAG] Chargement index FAISS et métadonnées...")
            self.index = faiss.read_index(INDEX_FILE)
            emb = np.load(EMBEDDINGS_FILE)
            with open(METADATA_FILE, "r", encoding="utf-8") as f:
                self.metadata = json.load(f)
            self.docs = [m["text"] for m in self.metadata]
            # index already contains normalized vectors; we keep embeddings for re-ranking if needed
            self.embeddings = emb
            print(f"[RAG] Index chargé ({len(self.metadata)} passages).")
        except Exception as e:
            print("[RAG] Erreur chargement index:", e)
            print("[RAG] Reconstruction de l'index...")
            self.rebuild_index()

    def rebuild_index(self):
        """
        Recrée l'index à partir des fichiers JSON du dossier data.
        Convertit chaque 'answer' en chunks et sauvegarde embeddings + metadata.
        """
        print("[RAG] Reconstruction de l'index à partir de", self.data_path)
        texts = []
        metadata = []

        # load and chunk
        for file in sorted(os.listdir(self.data_path)):
            if not file.endswith(".json"):
                continue
            path = os.path.join(self.data_path, file)
            try:
                with open(path, "r", encoding="utf-8") as f:
                    entries = json.load(f)
            except Exception as e:
                print(f"[RAG] Erreur JSON {file} :", e)
                continue

            for i, entry in enumerate(entries):
                text = entry.get("answer") or entry.get("text") or ""
                if not text:
                    continue
                source = entry.get("source", file)
                title = entry.get("question", "")[:80]
                chunks = _chunk_text(text)
                for idx, chunk in enumerate(chunks):
                    metadata.append({
                        "doc_id": f"{file}::{i}",
                        "chunk_id": idx,
                        "text": chunk,
                        "source": source,
                        "title": title,
                        "orig_file": file
                    })
                    texts.append(chunk)

        if not texts:
            print("[RAG] Aucun texte trouvé pour indexer.")
            self.docs = []
            self.metadata = []
            self.index = None
            return

        # compute embeddings in batches
        print("[RAG] Calcul des embeddings pour", len(texts), "passages...")
        embeddings = self.model.encode(texts, batch_size=64, show_progress_bar=True, convert_to_numpy=True)
        embeddings = _normalize_embeddings(embeddings.astype(np.float32))

        # create FAISS index with inner product (cosine)
        dim = embeddings.shape[1]
        self.index = faiss.IndexFlatIP(dim)
        self.index.add(embeddings)
        self.embeddings = embeddings
        self.docs = texts
        self.metadata = metadata

        # persist
        _ensure_index_dir()
        faiss.write_index(self.index, INDEX_FILE)
        np.save(EMBEDDINGS_FILE, embeddings)
        with open(METADATA_FILE, "w", encoding="utf-8") as f:
            json.dump(self.metadata, f, ensure_ascii=False, indent=2)

        print("[RAG] Index construit et sauvegardé:", INDEX_FILE)

    def add_documents(self, entries: List[Dict[str, Any]], persist: bool = True):
        """
        Ajouter de nouveaux documents (list of dict with 'answer' and optional metadata) et mettre à jour l'index.
        entries: [{"answer": "...", "source":"...", "question":"..."}]
        """
        new_texts = []
        new_meta = []
        for e in entries:
            text = e.get("answer") or e.get("text") or ""
            source = e.get("source", "unknown")
            title = e.get("question", "")[:80]
            chunks = _chunk_text(text)
            for idx, chunk in enumerate(chunks):
                new_meta.append({
                    "doc_id": e.get("id", "new"),
                    "chunk_id": idx,
                    "text": chunk,
                    "source": source,
                    "title": title,
                    "orig_file": e.get("id", "new")
                })
                new_texts.append(chunk)

        if not new_texts:
            return

        embs = self.model.encode(new_texts, batch_size=64, convert_to_numpy=True)
        embs = _normalize_embeddings(embs.astype(np.float32))

        if self.index is None:
            # create new index
            dim = embs.shape[1]
            self.index = faiss.IndexFlatIP(dim)
            self.embeddings = embs
            self.docs = new_texts
            self.metadata = new_meta
            self.index.add(embs)
        else:
            # append to existing index
            self.index.add(embs)
            self.embeddings = np.vstack([self.embeddings, embs])
            self.docs.extend(new_texts)
            self.metadata.extend(new_meta)

        if persist:
            faiss.write_index(self.index, INDEX_FILE)
            np.save(EMBEDDINGS_FILE, self.embeddings)
            with open(METADATA_FILE, "w", encoding="utf-8") as f:
                json.dump(self.metadata, f, ensure_ascii=False, indent=2)

        print(f"[RAG] {len(new_texts)} passages ajoutés à l'index.")

    # -----------------------
    # Retrieval utilities
    # -----------------------
    def _mmr(self, query_emb: np.ndarray, candidate_embs: np.ndarray, candidate_ids: List[int], k: int, lambda_param: float = MMR_LAMBDA):
        """
        Simple MMR implementation to pick k results balancing relevance and diversity.
        query_emb: (d,)
        candidate_embs: (n, d)
        candidate_ids: ids of candidates
        """
        selected = []
        selected_ids = []
        # relevance scores:
        sim_to_query = util.cos_sim(query_emb, candidate_embs)[0].cpu().numpy()
        # candidate similarity matrix
        candidate_sim = util.cos_sim(candidate_embs, candidate_embs).cpu().numpy()

        # pick first: highest relevance
        first = int(np.argmax(sim_to_query))
        selected.append(candidate_embs[first])
        selected_ids.append(candidate_ids[first])

        while len(selected_ids) < k and len(selected_ids) < len(candidate_ids):
            mmr_scores = []
            for idx in range(len(candidate_ids)):
                if candidate_ids[idx] in selected_ids:
                    mmr_scores.append(-9999)
                    continue
                relevance = sim_to_query[idx]
                diversity = max([candidate_sim[idx][list(candidate_ids).index(sid)] if sid in candidate_ids else 0 for sid in selected_ids]) if selected_ids else 0
                mmr_score = lambda_param * relevance - (1 - lambda_param) * diversity
                mmr_scores.append(mmr_score)
            next_idx = int(np.argmax(mmr_scores))
            selected_ids.append(candidate_ids[next_idx])

        return selected_ids

    def retrieve(self, query: str, top_k: int = TOP_K, rerank: bool = True, mmr: bool = True, min_score: float = 0.15):
        """
        Retrieve passages for a query.
        Returns list of dicts: [{"text": ..., "score": ..., "metadata": {...}}, ...]
        """
        if self.index is None or not self.metadata:
            return []

        q_emb = self.model.encode([query], convert_to_numpy=True)
        q_emb = _normalize_embeddings(q_emb.astype(np.float32))

        # FAISS search (returns inner product scores for normalized vectors => cosine)
        D, I = self.index.search(q_emb, min(self.index.ntotal, max(top_k * 4, 10)))  # retrieve more for rerank/MMR
        candidate_ids = I[0].tolist()
        candidate_scores = D[0].tolist()

        # Build candidate list
        candidates = []
        valid_ids = []
        candidate_embs = []
        for cid, score in zip(candidate_ids, candidate_scores):
            if cid < 0 or cid >= len(self.metadata):
                continue
            text = self.metadata[cid]["text"]
            meta = self.metadata[cid].copy()
            candidates.append({"id": cid, "text": text, "meta": meta, "score": float(score)})
            valid_ids.append(cid)
            candidate_embs.append(self.embeddings[cid])

        if not candidates:
            return []

        candidate_embs = np.vstack(candidate_embs)

        # optional MMR selection
        if mmr and len(valid_ids) > top_k:
            selected_ids = self._mmr(q_emb, candidate_embs, valid_ids, top_k)
        else:
            # pick top by score
            sorted_pairs = sorted(zip(valid_ids, [c["score"] for c in candidates]), key=lambda x: x[1], reverse=True)
            selected_ids = [pid for pid, _ in sorted_pairs[:top_k]]

        # filter and build selected candidates
        selected = []
        for sid in selected_ids:
            meta = self.metadata[sid]
            score = float(util.cos_sim(q_emb, self.embeddings[sid].reshape(1, -1)).item())
            if score < min_score:
                continue
            item = {
                "text": meta["text"],
                "score": score,
                "metadata": meta
            }
            selected.append(item)

        # optional rerank with cross-encoder (higher quality but slower)
        if rerank and _cross_encoder is not None and selected:
            try:
                pairs = [(query, s["text"]) for s in selected]
                rerank_scores = _cross_encoder.predict(pairs)

                # attach and sort
                for s, rs in zip(selected, rerank_scores):
                    s["rerank_score"] = float(rs)
                selected.sort(key=lambda x: x["rerank_score"], reverse=True)
            except Exception as e:
                print("[RAG] Cross-encoder rerank failed:", e)

        return selected

    def get_metadata(self, idx: int):
        if 0 <= idx < len(self.metadata):
            return self.metadata[idx]
        return None

    def get_all_docs(self):
        return self.docs

# Example usage
if __name__ == "__main__":
    r = RAGRetriever(rebuild=False)
    q = "Quels sont les effets du tabac ?"
    res = r.retrieve(q, top_k=4, rerank=True)
    print("Résultats RAG :")
    for i, ritem in enumerate(res):
        print(i+1, f"(score={ritem['score']:.3f})", ritem["metadata"].get("source"), "-", ritem["text"][:120])
