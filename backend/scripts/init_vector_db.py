import sys
import os

# Ajouter le chemin du dossier parent (backend)
current_dir = os.path.dirname(__file__)
parent_dir = os.path.dirname(current_dir)  # Remonte à backend/
sys.path.insert(0, parent_dir)

print(f"🔍 Recherche dans: {parent_dir}")
print(f"📁 Fichiers disponibles: {[f for f in os.listdir(parent_dir) if f.endswith('.py')]}")

try:
    from ingestion_service import IngestionService
    from rag_vector_service import RagVectorService
    print("✅ Import des services réussi")
except ImportError as e:
    print(f"❌ Erreur d'import: {e}")
    sys.exit(1)

def initialize_vector_database():
    """Initialise la base de données vectorielle"""
    print("🚀 Initialisation de la base de données vectorielle...")
    print("=" * 50)
    
    # Chemins - depuis backend/scripts/
    pdfs_folder = "../../data/ressources_fiables"  # data/ depuis backend/scripts/
    output_folder = "../../data/vector_store"      # data/ depuis backend/scripts/
    
    # Vérifier que le dossier PDF existe
    if not os.path.exists(pdfs_folder):
        print(f"❌ Dossier PDF introuvable: {pdfs_folder}")
        print(f"💡 Chemin actuel: {os.getcwd()}")
        return False
    
    print(f"📁 Dossier source: {pdfs_folder}")
    print(f"💾 Dossier destination: {output_folder}")
    print("-" * 50)
    
    # Lancer l'ingestion
    service = IngestionService()
    chunk_count = service.process_pdfs(pdfs_folder, output_folder)
    
    if chunk_count > 0:
        print("=" * 50)
        print("🎉 Initialisation terminée avec succès!")
        print(f"📊 {chunk_count} chunks de texte vectorisés")
        return True
    else:
        print("❌ Échec de l'initialisation")
        return False

def test_vector_system():
    """Teste le système RAG vectoriel après initialisation"""
    print("\n" + "=" * 50)
    print("🧪 Test du système RAG Vectoriel")
    print("=" * 50)
    
    try:
        # Initialiser le service RAG
        rag = RagVectorService("../../data/vector_store")  # Chemin ajusté
        print("✅ Service RAG initialisé avec succès")
        
        # Requêtes de test spécifiques à l'addictologie
        test_queries = [
            "tabac addiction",
            "dépendance cigarette traitement", 
            "risques santé tabac",
            "observatoire français des addictions",
            "santé publique France tabac",
            "sevrage tabagique",
            "addictologie tabac"
        ]
        
        print(f"\n🔍 Test de {len(test_queries)} requêtes...")
        
        for i, query in enumerate(test_queries, 1):
            print(f"\n{i}. 📝 Requête: '{query}'")
            print("-" * 40)
            
            result = rag.search(query, k=2)
            
            print(f"   📊 Documents trouvés: {result['found_documents']}")
            
            if result['found_documents'] > 0:
                print(f"   📚 Sources: {result['sources']}")
                
                # Afficher le meilleur résultat
                best_result = result['results'][0]
                print(f"   🏆 Meilleur résultat:")
                print(f"      📄 Source: {best_result['source']}")
                print(f"      ⭐ Score: {best_result['score']:.3f}")
                print(f"      📖 Extrait: {best_result['content'][:150]}...")
                
                # Vérifier la qualité du résultat
                if best_result['score'] > 0.5:
                    print("      ✅ Bonne pertinence détectée")
                else:
                    print("      ⚠️  Pertinence faible")
            else:
                print("   ❌ Aucun document trouvé pour cette requête")
                
        return True
        
    except Exception as e:
        print(f"❌ Erreur lors du test: {e}")
        return False

def main():
    """Fonction principale"""
    print("🔧 Script d'initialisation et de test du système RAG")
    print("=" * 60)
    
    # Étape 1: Initialisation
    success = initialize_vector_database()
    
    if not success:
        print("\n💥 Arrêt du script - l'initialisation a échoué")
        return
    
    # Étape 2: Tests rapides
    print("\n" + "=" * 60)
    print("PHASE DE TEST")
    print("=" * 60)
    
    test_success = test_vector_system()
    
    if test_success:
        # Étape 3: Test détaillé (optionnel)
        print("\n" + "=" * 60)
        print("TEST AVANCÉ")
        print("=" * 60)
        
        detailed_test = input("Voulez-vous exécuter le test détaillé? (o/n): ")
        if detailed_test.lower() in ['o', 'oui', 'y', 'yes']:
            test_specific_scenario()
    
    # Résumé final
    print("\n" + "=" * 60)
    print("📋 RÉSUMÉ FINAL")
    print("=" * 60)
    
    if success and test_success:
        print("🎉 SUCCÈS: Le système RAG vectoriel est opérationnel!")
        print("\n📁 Structure créée:")
        print("   📂 data/vector_store/")
        print("      📄 vector_index.faiss (index de recherche)")
        print("      📄 chunks.json (textes découpés)") 
        print("      📄 metadata.json (métadonnées)")
        print("\n🚀 Vous pouvez maintenant utiliser RagVectorService dans votre application!")
    else:
        print("❌ Des problèmes sont survenus lors de l'initialisation ou des tests")
        print("💡 Vérifiez:")
        print("   - Les fichiers PDF dans data/ressources_fiables/")
        print("   - L'installation des dépendances (pypdf, sentence-transformers, faiss)")
        print("   - Les messages d'erreur ci-dessus")

def test_specific_scenario():
    """Test un scénario spécifique avec plus de détails"""
    print("\n" + "=" * 50)
    print("🔎 Test détaillé - Scénario addictologie")
    print("=" * 50)
    
    try:
        rag = RagVectorService("../../data/vector_store")
        
        # Scénario réaliste d'utilisation
        scenario_queries = [
            "Quels sont les traitements pour la dépendance au tabac?",
            "Comment fonctionne l'observatoire français des addictions?",
            "Quels sont les risques du tabac sur la santé?"
        ]
        
        for query in scenario_queries:
            print(f"\n🎯 Scénario: '{query}'")
            print("-" * 50)
            
            result = rag.search(query, k=3)
            
            print(f"📊 Résultats: {result['found_documents']} documents pertinents")
            
            if result['found_documents'] > 0:
                print("📋 Détail des résultats trouvés:")
                for i, res in enumerate(result['results']):
                    print(f"\n   #{i+1} - {res['source']}")
                    print(f"      Score: {res['score']:.3f}")
                    print(f"      Contenu: {res['content'][:200]}...")
            else:
                print("   ❌ Aucune information pertinente trouvée")
                
        return True
        
    except Exception as e:
        print(f"❌ Erreur lors du test détaillé: {e}")
        return False

if __name__ == "__main__":
    main()