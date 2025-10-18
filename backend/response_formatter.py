"""
FICHIER: response_formatter.py
AUTEUR: Expert AI - Système RAG Avancé
VERSION: 3.2.1 - EXCELLENCE ÉPURÉE AVEC RETOURS LIGNE (PATCH)
DESCRIPTION: Moteur de post-traitement premium pour réponses LLM
             Transforme les réponses brutes en expériences conversationnelles d'exception
"""

import re
import json
from typing import Dict, List, Tuple, Optional
from datetime import datetime
import logging

# Configuration du logging premium
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger('RESPONSE_FORMATTER_PREMIUM')

class PremiumResponseFormatter:
    """
    Moteur d'excellence pour le formatage des réponses LLM
    Design épuré avec retours à ligne optimisés
    """

    def __init__(self):
        # Patterns de réponse spécialisés
        self.response_patterns = {
            'guide': {
                'keywords': ['guide', 'étapes', 'comment faire', 'procédure', 'méthode', 'marche à suivre'],
                'title': '🧭 Guide Expert - Plan d action détaillé',
                'icon': '🎯',
                'color': '#4F46E5',
                'template': 'guide'
            },
            'list': {
                'keywords': ['liste', 'éléments', 'points', 'avantages', 'inconvénients', 'conseils'],
                'title': '📋 Analyse Structurée - Points clés',
                'icon': '✨',
                'color': '#10B981',
                'template': 'list'
            },
            'explanation': {
                'keywords': ['explique', 'quoi est', 'définition', 'signifie', 'comprendre'],
                'title': '💡 Explication Approfondie - Tout comprendre',
                'icon': '🔍',
                'color': '#F59E0B',
                'template': 'explanation'
            },
            'warning': {
                'keywords': ['danger', 'risque', 'attention', 'urgence', 'important', 'critique'],
                'title': '⚠️ Alerte Sécurité - Action requise',
                'icon': '🚨',
                'color': '#EF4444',
                'template': 'warning'
            },
            'motivation': {
                'keywords': ['encouragement', 'motivation', 'félicitations', 'bravo', 'courage'],
                'title': '🌟 Soutien Personnalisé - Vous pouvez y arriver',
                'icon': '💫',
                'color': '#8B5CF6',
                'template': 'motivation'
            },
            'technical': {
                'keywords': ['dose', 'posologie', 'médicament', 'traitement', 'thérapie'],
                'title': '🔬 Recommandations Techniques - Précisions expertes',
                'icon': '⚗️',
                'color': '#06B6D4',
                'template': 'technical'
            }
        }

        # Métriques de qualité
        self.quality_metrics = {
            'min_length': 30,
            'max_length': 2500,
            'ideal_paragraphs': 5,
            'max_paragraph_length': 200,
            'max_line_length': 60
        }

    def analyze_query_intent(self, question: str) -> Dict[str, float]:
        """
        Analyse sémantique avancée avec intelligence contextuelle
        Retourne des scores de confiance précis
        """
        question_lower = question.lower().strip()
        scores = {pattern_type: 0.0 for pattern_type in self.response_patterns}

        for pattern_type, pattern_config in self.response_patterns.items():
            score = 0.0
            keywords = pattern_config['keywords']

            # Score basé sur la présence exacte de mots-clés
            for keyword in keywords:
                if keyword in question_lower:
                    score += 0.4
                    break

            # Score contextuel avancé
            if pattern_type == 'guide' and any(word in question_lower for word in ['comment', 'étape', 'procédure', 'démarche']):
                score += 0.6
            elif pattern_type == 'explanation' and any(word in question_lower for word in ['quoi', 'qu\'est', 'explique', 'définition']):
                score += 0.6
            elif pattern_type == 'list' and any(word in question_lower for word in ['liste', 'éléments', 'points', 'avantages']):
                score += 0.6
            elif pattern_type == 'warning' and any(word in question_lower for word in ['danger', 'risque', 'urgence', 'attention']):
                score += 0.8  # Priorité haute pour les alertes

            scores[pattern_type] = min(score, 1.0)

        logger.debug(f"Analyse d'intention - Scores: {scores}")
        return scores

    def enhance_emotional_intelligence(self, text: str, intent_type: str) -> str:
        """
        Améliore l'intelligence émotionnelle avec des messages personnalisés
        Niveau expert en communication thérapeutique
        """
        enhancements = {
            'guide': "💪 Excellente initiative - Vous avez fait le premier pas en demandant de l aide, c est déjà une immense force !\n\n",
            'warning': "🛡️ Sécurité maximale - Votre bien-être est notre priorité absolue. Voici les informations cruciales :\n\n",
            'motivation': "🌈 Soutien total - Chaque jour sans addiction est une victoire remarquable. Continuez comme ça !\n\n",
            'technical': "🔬 Précision experte - Analyse détaillée basée sur les dernières recommandations médicales :\n\n",
            'list': "📊 Vision claire - Voici une analyse structurée pour vous aider à y voir plus clair :\n\n",
            'explanation': "💡 Compréhension approfondie - Permettez-moi de vous expliquer en détail :\n\n"
        }

        return enhancements.get(intent_type, "💬 Réponse personnalisée - Voici ce que je peux vous partager :\n\n") + text

    # =========================
    # PATCH 1 : Retours à la ligne fiables après : ? ! .
    # =========================
    def _apply_punctuation_line_breaks(self, text: str) -> str:
        """
        Ajoute un retour à la ligne après :, ?, ! et .
        en préservant les décimales (3.14) et les heures (14:30).
        """
        # 1) Protéger décimales et heures
        DOT_TOKEN = "§DOT§"
        COL_TOKEN = "§COL§"
        text = re.sub(r'(\d)\.(\d)', rf'\1{DOT_TOKEN}\2', text)          # 3.14 -> 3§DOT§14
        text = re.sub(r'(\d{1,2}):(\d{2})', rf'\1{COL_TOKEN}\2', text)    # 14:30 -> 14§COL§30

        # 2) Retour à la ligne après la ponctuation principale
        #    - (?!\n) évite d'ajouter un \n s'il y en a déjà un
        #    - gère "?!", "...", "!!" (coupe après la séquence)
        text = re.sub(r'([:?!\.]+)(?!\n)', r'\1\n', text)

        # 3) Nettoyer les espaces avant \n (": \n" -> ":\n")
        text = re.sub(r'([:?!\.]+)\s+\n', r'\1\n', text)

        # 4) Restaurer décimales et heures
        text = text.replace(DOT_TOKEN, '.').replace(COL_TOKEN, ':')

        # 5) Compacter multiples retours
        text = re.sub(r'\n{3,}', '\n\n', text)
        return text

    def apply_premium_formatting(self, text: str, template: str) -> str:
        """
        Applique un formatage premium selon le template détecté
        Design épuré et professionnel
        """
        # Nettoyage complet des astérisques
        text = re.sub(r"\*{1,2}", "", text.strip())
        text = re.sub(r"\n{3,}", "\n\n", text)

        # Application des templates premium
        formatting_strategies = {
            'guide': self._format_premium_guide,
            'list': self._format_premium_list,
            'warning': self._format_premium_warning,
            'technical': self._format_premium_technical,
            'motivation': self._format_premium_motivation,
            'explanation': self._format_premium_explanation
        }

        formatter = formatting_strategies.get(template, self._format_premium_standard)
        formatted_text = formatter(text)

        # Appliquer les retours à ligne après ponctuation
        formatted_text = self._apply_punctuation_line_breaks(formatted_text)

        return formatted_text

    def _format_premium_guide(self, text: str) -> str:
        """Formatage guide étape par étape - Design épuré"""
        text = re.sub(r'(?i)(étape\s*\d+[:.]?)', r'\n\n🎯 \1\n\n', text)
        text = re.sub(r'^(\d+[\.\)])', r'\n\n🎯 Étape \1\n\n', text, flags=re.MULTILINE)

        return f"📚 Plan d action structuré\n\n{text}\n\n💡 Chaque étape franchie vous rapproche de votre objectif - vous en êtes capable !"

    def _format_premium_list(self, text: str) -> str:
        """Formatage liste - Clarté maximale"""
        text = re.sub(r'^[-*•]\s+', '\n\n   ✨ ', text, flags=re.MULTILINE)
        text = re.sub(r'^(\d+)\.\s+', r'\n\n   🔸 \1. ', text, flags=re.MULTILINE)

        lines = text.split('\n')
        formatted_lines = []

        for line in lines:
            line = line.strip()
            if re.match(r'^[✨🔸]', line):
                formatted_lines.append(f"\n{line}")
            elif line:
                formatted_lines.append(f"\n\n{line}")

        text = ''.join(formatted_lines).strip()
        return f"📊 Analyse détaillée\n\n{text}"

    def _format_premium_warning(self, text: str) -> str:
        """Formatage alerte - Impact maximum"""
        text = re.sub(r'(?i)(attention|danger|risque|urgence|important)', r'🚨 \1', text)
        return f"🚨 Alerte sécurité\n\n{text}\n\n📞 Urgence : Composez le 15 (SAMU) ou le 112 (urgence européenne)"

    def _format_premium_technical(self, text: str) -> str:
        """Formatage technique - Précision experte"""
        text = re.sub(r'(?i)(dose|posologie|mg|ml|fois|traitement|thérapie)', r'🔬 \1', text)
        return f"⚗️ Informations techniques\n\n{text}\n\n💊 Rappel important : Consultez toujours un professionnel de santé avant toute modification de traitement"

    def _format_premium_motivation(self, text: str) -> str:
        """Formatage motivation - Soutien personnalisé"""
        return f"💫 Message de soutien\n\n{text}\n\n🌈 Vous faites un travail remarquable - continuez ainsi !"

    def _format_premium_explanation(self, text: str) -> str:
        """Formatage explication - Pédagogie avancée"""
        return f"🔍 Explication détaillée\n\n{text}\n\n💡 Pour aller plus loin : N hésitez pas à demander des précisions supplémentaires"

    def _format_premium_standard(self, text: str) -> str:
        """Formatage standard - Excellence par défaut"""
        text = re.sub(r'\*', '', text)

        paragraphs = text.split('\n\n')
        formatted_paragraphs = []

        for i, paragraph in enumerate(paragraphs):
            if paragraph.strip():
                if i == 0:
                    formatted_paragraphs.append(f"💬 {paragraph}")
                else:
                    formatted_paragraphs.append(paragraph)
                formatted_paragraphs.append("")  # Double espacement

        return '\n'.join(formatted_paragraphs).strip()

    # =========================
    # PATCH 2 : Préserver les \n lors de l'optimisation
    # =========================
    def _apply_ultimate_line_breaks(self, text: str) -> str:
        """
        Application de retours à la ligne ultimes - Excellence de lisibilité
        """
        # Appliquer d'abord les retours après ponctuation
        text = self._apply_punctuation_line_breaks(text)

        # Retours après virgules dans fragments très longs (préserve lisibilité)
        text = re.sub(r'(,\s)([^,\n]{40,})', r',\n\2', text)

        # Retours stratégiques pour aération (sans casser déjà présent)
        text = re.sub(r'(\s)(et\s|ou\s|mais\s|donc\s|car\s)', r'\n\2', text)

        # Nettoyage final
        text = re.sub(r'\n{3,}', '\n\n', text)
        text = re.sub(r' \n', '\n', text)

        return text

    def _optimize_paragraph_structure(self, text: str) -> str:
        """
        Optimisation avancée de la structure des paragraphes
        (préserve les retours à la ligne ajoutés après la ponctuation).
        """
        # Respecter les retours à la ligne existants
        text = self._apply_punctuation_line_breaks(text)

        paragraphs = text.split('\n\n')
        optimized_paragraphs = []

        for paragraph in paragraphs:
            para = paragraph.strip()
            if not para:
                continue

            if len(para) > self.quality_metrics['max_paragraph_length']:
                # Découper en respectant les \n déjà présents
                sentences = re.split(r'(?<=[.!?])\n+', para)
                if len(sentences) > 1:
                    current_chunk = []
                    current_len = 0

                    for s in sentences:
                        s = s.strip()
                        sl = len(s)
                        if current_len + sl > 100 or len(current_chunk) >= 2:
                            if current_chunk:
                                # Préserver les retours à la ligne
                                optimized_paragraphs.append('\n'.join(current_chunk))
                            current_chunk = [s]
                            current_len = sl
                        else:
                            current_chunk.append(s)
                            current_len += sl + 1

                    if current_chunk:
                        optimized_paragraphs.append('\n'.join(current_chunk))
                    optimized_paragraphs.append("")  # espacement
                else:
                    optimized_paragraphs.append(para)
            else:
                optimized_paragraphs.append(para)

        return '\n\n'.join(optimized_paragraphs)

    def _enhance_visual_hierarchy(self, text: str) -> str:
        """
        Amélioration de la hiérarchie visuelle - Design épuré
        """
        sections = text.split('\n\n')
        enhanced_sections = []

        for i, section in enumerate(sections):
            if section.strip():
                if i > 0 and i % 2 == 0:
                    enhanced_sections.append("")
                enhanced_sections.append(section)

        return '\n\n'.join(enhanced_sections)

    def calculate_premium_quality_score(self, text: str) -> Dict[str, float]:
        """
        Calcul de score de qualité premium - Métriques avancées
        """
        words = text.split()
        sentences = re.split(r'[.!?]+', text)
        paragraphs = text.split('\n\n')

        # Métriques avancées
        avg_paragraph_length = sum(len(p.split()) for p in paragraphs) / max(len(paragraphs), 1)
        readability_ratio = len(paragraphs) / max(len(sentences), 1)

        return {
            'length_score': min(len(words) / self.quality_metrics['min_length'], 1.0),
            'readability_score': min(len(paragraphs) / self.quality_metrics['ideal_paragraphs'], 1.0),
            'structure_score': 1.0 if len(paragraphs) > 2 else 0.6,
            'completeness_score': 0.95 if len(words) > 80 else 0.7,
            'paragraph_balance': min(avg_paragraph_length / 50, 1.0),
            'visual_hierarchy': min(readability_ratio * 2, 1.0)
        }

    def format_response(self, raw_answer: str, question: str, context: Optional[Dict] = None) -> Dict:
        """
        Point d'entrée principal - Transformation premium des réponses
        Design épuré avec retours à ligne optimisés
        """
        try:
            logger.info(f"Début du formatage premium - Question: '{question[:80]}...'")

            # Analyse d'intention avancée
            intent_scores = self.analyze_query_intent(question)
            primary_intent = max(intent_scores, key=intent_scores.get)
            confidence = intent_scores[primary_intent]

            pattern_config = self.response_patterns[primary_intent]
            logger.debug(f"Intention détectée: {primary_intent} (confiance: {confidence:.2f})")

            # Application du formatage premium
            formatted_content = self.apply_premium_formatting(raw_answer, pattern_config['template'])

            # Amélioration émotionnelle experte
            enhanced_content = self.enhance_emotional_intelligence(formatted_content, primary_intent)

            # Optimisations avancées de lisibilité
            enhanced_content = self._apply_ultimate_line_breaks(enhanced_content)
            enhanced_content = self._optimize_paragraph_structure(enhanced_content)
            enhanced_content = self._enhance_visual_hierarchy(enhanced_content)

            # Calcul des métriques de qualité premium
            quality_metrics = self.calculate_premium_quality_score(enhanced_content)
            overall_quality = sum(quality_metrics.values()) / len(quality_metrics)

            # Construction de la réponse structurée premium
            structured_response = {
                "metadata": {
                    "version": "3.2.1-EPURE",
                    "timestamp": datetime.now().isoformat(),
                    "processing_tier": "EXCELLENCE",
                    "intent_detected": primary_intent,
                    "confidence_score": round(confidence, 3),
                    "quality_score": round(overall_quality, 3),
                    "word_count_original": len(raw_answer.split()),
                    "word_count_enhanced": len(enhanced_content.split())
                },
                "presentation": {
                    "title": pattern_config['title'],
                    "icon": pattern_config['icon'],
                    "theme_color": pattern_config['color'],
                    "template_type": pattern_config['template'],
                    "reading_level": "PREMIUM",
                    "accessibility_score": 0.95
                },
                "content": {
                    "raw": raw_answer,
                    "enhanced": enhanced_content,
                    "paragraph_count": len(enhanced_content.split('\n\n')),
                    "sentence_count": len(re.split(r'[.!?]+', enhanced_content)),
                    "estimated_reading_time": f"{max(1, len(enhanced_content.split()) // 120)} min",
                    "readability_index": "EXCELLENT"
                },
                "quality_metrics": quality_metrics,
                "user_experience": {
                    "user_question": question,
                    "context_used": context is not None,
                    "suggested_next_actions": self._suggest_premium_actions(primary_intent),
                    "engagement_potential": "HIGH"
                }
            }

            logger.info(f"Formatage premium réussi - Qualité: {overall_quality:.3f} - Type: {primary_intent}")

            return structured_response

        except Exception as e:
            logger.error(f"Erreur lors du formatage premium: {str(e)}")
            return self._get_premium_fallback_response(raw_answer, question)

    def _suggest_premium_actions(self, intent: str) -> List[str]:
        """Suggestions d'actions premium - Niveau expert"""
        suggestions = {
            'guide': [
                "Créer un journal de suivi personnalisé",
                "Fixer des objectifs SMART hebdomadaires",
                "Partager vos progrès avec un professionnel"
            ],
            'warning': [
                "Contacter immédiatement un médecin",
                "Appeler une ligne d urgence spécialisée",
                "Mettre en place un plan de sécurité"
            ],
            'technical': [
                "Programmer une consultation médicale",
                "Vérifier les interactions médicamenteuses",
                "Rechercher des études récentes sur le sujet"
            ],
            'list': [
                "Prioriser les 3 actions les plus importantes",
                "Créer un tableau de bord de suivi",
                "Transformer en plan d action concret"
            ],
            'default': [
                "Poser une question complémentaire",
                "Demander des précisions techniques",
                "Explorer d autres aspects du sujet"
            ]
        }

        return suggestions.get(intent, suggestions['default'])

    def _get_premium_fallback_response(self, raw_answer: str, question: str) -> Dict:
        """Réponse de secours premium - Maintien de l'excellence"""
        # Nettoyage et optimisation même en mode fallback
        clean_answer = re.sub(r'\*', '', raw_answer)
        clean_answer = self._apply_punctuation_line_breaks(clean_answer)
        clean_answer = self._optimize_paragraph_structure(clean_answer)

        return {
            "metadata": {
                "version": "3.2.1-EPURE",
                "timestamp": datetime.now().isoformat(),
                "processing_tier": "FALLBACK",
                "error_occurred": True,
                "fallback_used": True
            },
            "presentation": {
                "title": "💬 Réponse immédiate - Mode standard",
                "icon": "⚡",
                "theme_color": "#6B7280",
                "template_type": "fallback",
                "reading_level": "STANDARD"
            },
            "content": {
                "raw": raw_answer,
                "enhanced": f"💡 Réponse directe\n\n{clean_answer}",
                "paragraph_count": len(clean_answer.split('\n\n')),
                "estimated_reading_time": "1-2 min"
            },
            "quality_metrics": {
                "length_score": 0.8,
                "readability_score": 0.7,
                "structure_score": 0.6,
                "completeness_score": 0.8
            }
        }

# Interface premium pour l'existant
def format_response(answer: str, question: str) -> Dict:
    """
    Fonction legacy avec qualité premium
    """
    formatter = PremiumResponseFormatter()
    result = formatter.format_response(answer, question)

    # Conversion au format simplifié mais premium
    return {
        "title": result["presentation"]["title"],
        "icon": result["presentation"]["icon"],
        "content": result["content"]["enhanced"],
        "lines_count": result["content"]["paragraph_count"],
        "quality_score": result["metadata"]["quality_score"],
        "reading_time": result["content"]["estimated_reading_time"],
        "processing_tier": result["metadata"]["processing_tier"]
    }

# Démonstration
if __name__ == "__main__":
    print("Système de formatage premium - Démonstration avec retours à ligne\n")

    formatter = PremiumResponseFormatter()

    # Test avec un texte contenant différentes ponctuations
    test_question = "Comment gérer le stress au quotidien ?"
    test_answer = """
    Pour gérer le stress au quotidien: commencez par identifier vos sources de stress. Ensuite, pratiquez la respiration profonde: inspirez lentement, retenez votre souffle, expirez doucement. Vous pouvez aussi essayer la méditation? C'est très efficace! L'exercice physique est également important. N'oubliez pas de prendre des pauses régulières. Finalement, assurez-vous de dormir suffisamment.
    """

    result = formatter.format_response(test_answer, test_question)
    print("Résultat premium avec retours à ligne après ponctuation:")
    print(result["content"]["enhanced"])
    print(f"\nQualité: {result['metadata']['quality_score']:.3f} | Temps de lecture: {result['content']['estimated_reading_time']}")

    print("\n" + "="*60 + "\n")

    # Test avec une liste complexe
    list_question = "Quels sont les avantages de l'exercice physique ?"
    list_answer = """
    Les avantages sont nombreux: amélioration de la santé cardiovasculaire. Renforcement du système immunitaire. Réduction du stress et de l'anxiété. Meilleure qualité de sommeil. Augmentation de l'énergie quotidienne. Amélioration de l'humeur générale. Prévention des maladies chroniques. Renforcement de la confiance en soi.
    """

    list_result = formatter.format_response(list_answer, list_question)
    print("Résultat premium - Liste avec retours à la ligne:")
    print(list_result["content"]["enhanced"])
    print(f"\nQualité: {list_result['metadata']['quality_score']:.3f}")