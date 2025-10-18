import faiss
import json
import numpy as np
from sentence_transformers import SentenceTransformer
import os

class RagVectorService:
    def __init__(self, vector_store_path):
        self.model = SentenceTransformer('all-MiniLM-L6-v2')
        
        # Vérification que les fichiers existent
        if not os.path.exists(vector_store_path):
            raise FileNotFoundError(f"Dossier introuvable: {vector_store_path}")
        
        # Chargement de l'index FAISS
        index_path = os.path.join(vector_store_path, "vector_index.faiss")
        if not os.path.exists(index_path):
            raise FileNotFoundError(f"Index FAISS introuvable: {index_path}")
        
        self.index = faiss.read_index(index_path)
        
        # Chargement des chunks et métadonnées
        chunks_path = os.path.join(vector_store_path, "chunks.json")
        metadata_path = os.path.join(vector_store_path, "metadata.json")
        
        with open(chunks_path, "r", encoding='utf-8') as f:
            self.chunks = json.load(f)
        
        with open(metadata_path, "r", encoding='utf-8') as f:
            self.metadata = json.load(f)
        
        print(f"✅ RagVectorService initialisé avec {len(self.chunks)} chunks")
    
    def search(self, query, k=4):
        """Recherche sémantique dans les documents"""
        try:
            # Embedding de la requête
            query_embedding = self.model.encode([query]).astype('float32')
            
            # Recherche dans FAISS
            distances, indices = self.index.search(query_embedding, k)
            
            # Récupération des résultats
            results = []
            sources = set()
            
            for i, idx in enumerate(indices[0]):
                if idx < len(self.chunks) and idx >= 0:
                    chunk = self.chunks[idx]
                    meta = self.metadata[idx]
                    
                    results.append({
                        "content": chunk,
                        "source": meta["source"],
                        "chunk_id": meta["chunk_id"],
                        "distance": float(distances[0][i]),  # Convertir pour JSON
                        "score": 1 / (1 + distances[0][i])  # Score de similarité
                    })
                    sources.add(meta["source"])
            
            # Formatage du contexte
            context = "\n\n---\n\n".join([
                f"📄 Source: {r['source']} (Chunk {r['chunk_id']})\n"
                f"📊 Score: {r['score']:.3f}\n"
                f"📝 Contenu:\n{r['content']}"
                for r in results
            ])
            
            return {
                "context": context,
                "sources": list(sources),
                "found_documents": len(results),
                "method": "vectoriel",
                "results": results
            }
            
        except Exception as e:
            print(f"❌ Erreur lors de la recherche: {e}")
            return {
                "context": "",
                "sources": [],
                "found_documents": 0,
                "method": "vectoriel",
                "results": []
            }

# Test direct
if __name__ == "__main__":
    try:
        rag = RagVectorService("../data/vector_store")
        result = rag.search("tabac addiction traitement")
        print(f"🔍 Résultats: {result['found_documents']} documents trouvés")
        print(f"📚 Sources: {result['sources']}")
        print(f"📄 Contexte:\n{result['context'][:500]}...")
    except Exception as e:
        print(f"❌ Test échoué: {e}")