import importlib.util
import sys
import types
from pathlib import Path

BACKEND_DIR = Path(__file__).resolve().parents[1]
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))


def load_app_module():
    module_name = "app_for_tests"
    if module_name in sys.modules:
        return sys.modules[module_name]

    dummy_router = types.ModuleType("router_service")

    class DummyRouterService:
        def route_question(self, question):
            return {
                "question": question,
                "question_analysis": {"type": "statistics"},
                "context_result": {"has_data": True, "methods_used": []},
                "final_context": "",
                "sources": [],
            }

    dummy_router.RouterService = DummyRouterService
    sys.modules["router_service"] = dummy_router

    dummy_llm = types.ModuleType("llm_service")
    dummy_llm.call_llm = lambda messages: "Réponse simulée"
    sys.modules["llm_service"] = dummy_llm

    dummy_flask = types.ModuleType("flask")

    class DummyFlask:
        def __init__(self, *args, **kwargs):
            pass

        def route(self, *args, **kwargs):
            def decorator(func):
                return func

            return decorator

        def run(self, *args, **kwargs):
            return None

    dummy_flask.Flask = DummyFlask
    dummy_flask.request = types.SimpleNamespace(json={})

    def jsonify(obj):
        return obj

    dummy_flask.jsonify = jsonify
    sys.modules["flask"] = dummy_flask

    dummy_cors = types.ModuleType("flask_cors")
    dummy_cors.CORS = lambda app: app
    sys.modules["flask_cors"] = dummy_cors

    spec = importlib.util.spec_from_file_location(module_name, BACKEND_DIR / "app.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    sys.modules[module_name] = module
    return module


def test_generate_greeting_response_returns_salutation():
    app = load_app_module()

    response = app.generate_greeting_response("Bonjour Nafass")

    assert response["title"] == "Salutation"
    assert "Bonjour" in response["content"]


def test_generate_off_topic_response_has_warning_icon():
    app = load_app_module()

    response = app.generate_off_topic_response("Parle-moi de cuisine")

    assert response["icon"] == "🚫"
    assert "addictologie" in response["content"].lower()