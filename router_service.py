"""
FICHIER: router_service.py
ROLE: Orchestrateur intelligent qui choisit le bon système RAG selon le type de question
"""

import re
from typing import Dict, List, Any
from rag_service import RAGRetriever
from rag_vector_service import RagVectorService

class RouterService:
    def __init__(self):
        # Initialiser les deux systèmes RAG
        self.rag_statistics = RAGRetriever("../data")  # Votre RAG existant (statistiques)
        self.rag_scientific = RagVectorService("../data/vector_store")  # Nouveau RAG scientifique
        
        # Patterns pour détecter le type de question
        self.stat_patterns = [
            r'\b(statistiques|chiffres|données|prévalence|taux|pourcentage|proportion|nombre de|combien de|fréquence)\b',
            r'\b(évolution|tendance|augmentation|diminution|comparaison)\b',
            r'\b(enquête|étude épidémiologique|données officielles|chiffres clés)\b',
            r'\b(consommation|usage|pratique)\b.*\b(france|français|population)\b'
        ]
        
        self.science_patterns = [
            r'\b(étude scientifique|recherche|publication|article scientifique|preuves scientifiques)\b',
            r'\b(mécanisme|effet|cause|conséquence|traitement|thérapie|méthode)\b',
            r'\b(neurobiologie|pharmacologie|biochimie|physiopathologie)\b',
            r'\b(essai clinique|randomisé|contrôlé|méta-analyse|revue systématique)\b',
            r'\b(observatoire|institution|organisme officiel|santé publique)\b'
        ]
        
        self.mixed_patterns = [
            r'\b(et|ainsi que|mais aussi|également)\b',  # Questions composites
            r'\b(impact|conséquence|effet)\b.*\b(statistiques|chiffres)\b',
            r'\b(traitement)\b.*\b(efficacité|preuves)\b'
        ]
    
    def analyze_question_type(self, question: str) -> Dict[str, Any]:
        """
        Analyse la question pour déterminer quel(s) système(s) RAG utiliser
        """
        question_lower = question.lower()
        
        # Compter les patterns pour chaque type
        stat_score = sum(1 for pattern in self.stat_patterns if re.search(pattern, question_lower))
        science_score = sum(1 for pattern in self.science_patterns if re.search(pattern, question_lower))
        mixed_score = sum(1 for pattern in self.mixed_patterns if re.search(pattern, question_lower))
        
        # Décision basée sur les scores
        if mixed_score > 0 or (stat_score > 0 and science_score > 0):
            return {
                "type": "mixed",
                "confidence": min(1.0, (stat_score + science_score + mixed_score) / 10),
                "systems": ["statistics", "scientific"],
                "reason": "Question composite nécessitant données statistiques ET scientifiques"
            }
        elif stat_score > science_score:
            return {
                "type": "statistics", 
                "confidence": min(1.0, stat_score / 5),
                "systems": ["statistics"],
                "reason": "Question orientée données/chiffres/statistiques"
            }
        elif science_score > stat_score:
            return {
                "type": "scientific",
                "confidence": min(1.0, science_score / 5),
                "systems": ["scientific"],
                "reason": "Question orientée recherche scientifique/mécanismes/traitements"
            }
        else:
            # Par défaut, utiliser les deux systèmes
            return {
                "type": "default",
                "confidence": 0.5,
                "systems": ["statistics", "scientific"],
                "reason": "Question générale - utilisation des deux sources"
            }
    
    def get_context_from_both_systems(self, question: str) -> Dict[str, Any]:
        """
        Récupère le contexte des deux systèmes RAG et les combine intelligemment
        """
        # Analyser le type de question
        analysis = self.analyze_question_type(question)
        
        contexts = []
        all_sources = []
        methods_used = []
        
        # Récupérer le contexte du système statistique
        if "statistics" in analysis["systems"]:
            try:
                stat_results = self.rag_statistics.retrieve(question, top_k=3)
                if stat_results:
                    stat_context = "\n".join([r.get("text", "") for r in stat_results])
                    stat_sources = [r.get("metadata", {}).get("source", "Statistiques") for r in stat_results]
                    contexts.append(f"📊 DONNÉES STATISTIQUES:\n{stat_context}")
                    all_sources.extend(stat_sources)
                    methods_used.append("statistics")
            except Exception as e:
                print(f"❌ Erreur RAG statistiques: {e}")
        
        # Récupérer le contexte du système scientifique
        if "scientific" in analysis["systems"]:
            try:
                sci_results = self.rag_scientific.search(question, k=3)
                if sci_results["found_documents"] > 0:
                    contexts.append(f"🔬 RESSOURCES SCIENTIFIQUES:\n{sci_results['context']}")
                    all_sources.extend(sci_results['sources'])
                    methods_used.append("scientific")
            except Exception as e:
                print(f"❌ Erreur RAG scientifique: {e}")
        
        # Combiner les contextes
        combined_context = "\n\n".join(contexts) if contexts else ""
        
        return {
            "context": combined_context,
            "sources": list(set(all_sources)),
            "analysis": analysis,
            "methods_used": methods_used,
            "has_data": len(contexts) > 0
        }
    
    def route_question(self, question: str) -> Dict[str, Any]:
        """
        Point d'entrée principal : route la question vers les bons systèmes RAG
        """
        # Analyse de la question
        analysis = self.analyze_question_type(question)
        
        # Récupération du contexte combiné
        context_result = self.get_context_from_both_systems(question)
        
        return {
            "question": question,
            "question_analysis": analysis,
            "context_result": context_result,
            "final_context": context_result["context"],
            "sources": context_result["sources"]
        }


# Exemple d'utilisation et tests
if __name__ == "__main__":
    router = RouterService()
    
    test_questions = [
        "Quelles sont les statistiques de consommation de tabac en France ?",
        "Quels sont les mécanismes neurobiologiques de l'addiction au tabac ?",
        "Donne-moi les chiffres de prévalence et les traitements efficaces pour le sevrage tabagique",
        "Comment fonctionnent les thérapies comportementales pour l'addiction ?",
        "Quelle est l'évolution de la consommation d'alcool chez les jeunes ?"
    ]
    
    for question in test_questions:
        print(f"\n{'='*60}")
        print(f"🔍 QUESTION: {question}")
        print(f"{'='*60}")
        
        result = router.route_question(question)
        analysis = result["question_analysis"]
        
        print(f"📊 ANALYSE: {analysis['type']} (confiance: {analysis['confidence']:.2f})")
        print(f"🎯 SYSTÈMES: {analysis['systems']}")
        print(f"💡 RAISON: {analysis['reason']}")
        print(f"📚 SOURCES: {result['sources']}")
        print(f"📝 CONTEXTE TROUVÉ: {len(result['final_context'])} caractères")
        
        if result['final_context']:
            print(f"📄 EXTRAIT:\n{result['final_context'][:300]}...")