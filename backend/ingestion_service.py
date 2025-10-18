import os
import json
import numpy as np
from sentence_transformers import SentenceTransformer
import faiss

class IngestionService:
    def __init__(self):
        self.model = SentenceTransformer('all-MiniLM-L6-v2')
        print("✅ Service d'ingestion initialisé")
    
    def extract_text_from_pdf(self, pdf_path):
        """Extrait le texte d'un PDF"""
        try:
            from pypdf import PdfReader
            text = ""
            with open(pdf_path, 'rb') as file:
                pdf_reader = PdfReader(file)
                for page_num in range(len(pdf_reader.pages)):
                    page = pdf_reader.pages[page_num]
                    page_text = page.extract_text()
                    if page_text.strip():
                        text += f"Page {page_num + 1}:\n{page_text}\n\n"
            return text if text else f"[AUCUN TEXTE EXTRAIT: {pdf_path}]"
        except Exception as e:
            return f"[ERREUR: {str(e)}]"
    
    def split_text(self, text, chunk_size=800, overlap=100):
        """Découpe le texte en chunks"""
        words = text.split()
        if len(words) <= chunk_size:
            return [text]
        
        chunks = []
        for i in range(0, len(words), chunk_size - overlap):
            chunk = " ".join(words[i:i + chunk_size])
            chunks.append(chunk)
            if i + chunk_size >= len(words):
                break
        return chunks
    
    def process_pdfs(self, pdfs_folder, output_folder):
        """Traite tous les PDFs du dossier"""
        all_chunks = []
        metadata = []
        
        os.makedirs(output_folder, exist_ok=True)
        
        # Parcours récursif de tous les sous-dossiers
        for root, dirs, files in os.walk(pdfs_folder):
            for filename in files:
                if filename.lower().endswith('.pdf'):
                    pdf_path = os.path.join(root, filename)
                    relative_path = os.path.relpath(pdf_path, pdfs_folder)
                    
                    print(f"📄 Traitement de: {relative_path}")
                    
                    # Extraction du texte
                    text = self.extract_text_from_pdf(pdf_path)
                    
                    if text.startswith("[ERREUR") or text.startswith("[AUCUN TEXTE"):
                        print(f"   ⚠️  {text}")
                        continue
                    
                    # Découpage
                    chunks = self.split_text(text)
                    
                    # Ajout aux données
                    for i, chunk in enumerate(chunks):
                        all_chunks.append(chunk)
                        metadata.append({
                            "source": relative_path,
                            "chunk_id": i,
                            "full_path": pdf_path,
                            "chunk_size": len(chunk),
                            "text_preview": chunk[:150] + "..." if len(chunk) > 150 else chunk
                        })
                    
                    print(f"   ✅ {len(chunks)} chunks créés")
        
        if not all_chunks:
            print("❌ Aucun chunk créé - vérifiez les PDFs")
            return 0
        
        # Création des embeddings
        print("🧠 Création des embeddings...")
        embeddings = self.model.encode(all_chunks)
        
        # Création de l'index FAISS
        dimension = embeddings.shape[1]
        index = faiss.IndexFlatL2(dimension)
        index.add(embeddings.astype('float32'))
        
        # Sauvegarde
        faiss.write_index(index, os.path.join(output_folder, "vector_index.faiss"))
        
        with open(os.path.join(output_folder, "chunks.json"), "w", encoding='utf-8') as f:
            json.dump(all_chunks, f, ensure_ascii=False, indent=2)
        
        with open(os.path.join(output_folder, "metadata.json"), "w", encoding='utf-8') as f:
            json.dump(metadata, f, ensure_ascii=False, indent=2)
        
        print(f"🎉 Traitement terminé: {len(all_chunks)} chunks créés")
        print(f"💾 Données sauvegardées dans: {output_folder}")
        return len(all_chunks)

# Test direct
if __name__ == "__main__":
    service = IngestionService()
    service.process_pdfs(
        pdfs_folder="../data/ressources_fiables",
        output_folder="../data/vector_store"
    )