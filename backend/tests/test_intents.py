from app.agent.intents import DEFAULT_INTENT, INTENTS
from app.tools import registry


def test_default_intent_exists():
    assert DEFAULT_INTENT in INTENTS


def test_intent_tools_are_registered():
    registered = set(registry.names())
    for intent in INTENTS.values():
        assert set(intent.tools) <= registered, f"意图 {intent.name} 引用了未注册的工具"
