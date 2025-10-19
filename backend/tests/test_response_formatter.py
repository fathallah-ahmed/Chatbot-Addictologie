import sys
from pathlib import Path

import pytest

ROOT_DIR = Path(__file__).resolve().parents[2]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from backend.response_formatter import PremiumResponseFormatter, format_response


def test_analyze_query_intent_identifies_guide():
    formatter = PremiumResponseFormatter()
    scores = formatter.analyze_query_intent("Comment arrêter de fumer en plusieurs étapes ?")

    guide_score = scores["guide"]
    assert guide_score >= 0.6
    assert guide_score >= scores["general"]


def test_filter_unwanted_response_removes_disclaimers():
    formatter = PremiumResponseFormatter()
    text = "\n".join([
        "En tant qu'intelligence artificielle, je ne peux pas fournir cette information.",
        "Cependant, voici un conseil utile.",
    ])

    filtered = formatter._filter_unwanted_response(text)

    assert "intelligence artificielle" not in filtered.lower()
    assert "conseil" in filtered.lower()


def test_enhance_emotional_intelligence_returns_fallback_when_empty():
    formatter = PremiumResponseFormatter()
    unwanted = "En tant qu'assistant, je ne peux pas répondre."

    enhanced = formatter.enhance_emotional_intelligence(unwanted, "guide")

    assert "Je n'ai pas assez d'informations" in enhanced


def test_format_response_produces_structured_payload():
    answer = (
        "Pour arrêter de fumer, fixez une date, demandez du soutien et remplacez progressivement vos habitudes."
    )
    question = "Comment arrêter de fumer ?"

    formatted = format_response(answer, question)

    assert formatted["title"]
    assert formatted["icon"]
    assert "💪" in formatted["content"]
    assert formatted["processing_tier"] in {"EXCELLENCE", "FALLBACK"}