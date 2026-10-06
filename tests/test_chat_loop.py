import json
from types import SimpleNamespace
from unittest.mock import MagicMock

import pytest

from agent import chat_loop


def tool_call(name, arguments, call_id="call_1"):
    return SimpleNamespace(id=call_id, function=SimpleNamespace(name=name, arguments=arguments))


def response(content=None, tool_calls=None):
    message = SimpleNamespace(role="assistant", content=content, tool_calls=tool_calls)
    return SimpleNamespace(choices=[SimpleNamespace(message=message)])


def mock_client(*responses):
    client = MagicMock()
    client.chat.completions.create.side_effect = list(responses)
    return client


def tool_messages(client):
    messages = client.chat.completions.create.call_args.kwargs["messages"]
    return [m for m in messages if isinstance(m, dict) and m["role"] == "tool"]


@pytest.fixture(autouse=True)
def no_retrieval(monkeypatch):
    monkeypatch.setattr(chat_loop, "top_k", lambda query, chunks, k=3: [])


def test_normal_tool_call(monkeypatch):
    monkeypatch.setitem(chat_loop.TOOL_FUNCTIONS, "ping_host", lambda host: {"host": host, "avg_latency_ms": 12.0})
    client = mock_client(
        response(tool_calls=[tool_call("ping_host", '{"host": "vpn-gw-01"}')]),
        response(content="Gateway is reachable."),
    )

    _, tool_calls_made, answer = chat_loop.run_agent("ping vpn-gw-01", chunks=[], llm_client=client)

    assert answer == "Gateway is reachable."
    assert tool_calls_made == [
        {"name": "ping_host", "args": {"host": "vpn-gw-01"}, "result": {"host": "vpn-gw-01", "avg_latency_ms": 12.0}}
    ]
    [tool_msg] = tool_messages(client)
    assert tool_msg["tool_call_id"] == "call_1"
    assert json.loads(tool_msg["content"]) == {"host": "vpn-gw-01", "avg_latency_ms": 12.0}


def test_unknown_tool_name_is_returned_as_error():
    client = mock_client(
        response(tool_calls=[tool_call("reboot_router", '{"device_id": "r1"}')]),
        response(content="I cannot reboot devices."),
    )

    _, tool_calls_made, answer = chat_loop.run_agent("reboot r1", chunks=[], llm_client=client)

    assert answer == "I cannot reboot devices."
    error = json.loads(tool_messages(client)[0]["content"])["error"]
    assert "Unknown tool 'reboot_router'" in error
    assert "ping_host" in error
    assert tool_calls_made[0]["args"] is None


def test_invalid_json_arguments_are_returned_as_error():
    client = mock_client(
        response(tool_calls=[tool_call("ping_host", '{"host": ')]),
        response(content="Retried and recovered."),
    )

    _, _, answer = chat_loop.run_agent("ping something", chunks=[], llm_client=client)

    assert answer == "Retried and recovered."
    error = json.loads(tool_messages(client)[0]["content"])["error"]
    assert error.startswith("Invalid JSON arguments")


def test_tool_exception_is_returned_as_error():
    client = mock_client(
        response(tool_calls=[tool_call("ping_host", '{"hostname": "x"}')]),
        response(content="done"),
    )

    chat_loop.run_agent("ping x", chunks=[], llm_client=client)

    error = json.loads(tool_messages(client)[0]["content"])["error"]
    assert error.startswith("Tool 'ping_host' failed: TypeError")


def test_step_cap_reached(monkeypatch):
    monkeypatch.setitem(chat_loop.TOOL_FUNCTIONS, "ping_host", lambda host: {"host": host})
    endless = [response(tool_calls=[tool_call("ping_host", '{"host": "x"}')]) for _ in range(chat_loop.MAX_STEPS + 1)]
    client = mock_client(*endless)

    _, tool_calls_made, answer = chat_loop.run_agent("loop forever", chunks=[], llm_client=client)

    assert answer == chat_loop.CAP_REACHED_ANSWER
    assert client.chat.completions.create.call_count == chat_loop.MAX_STEPS
    assert len(tool_calls_made) == chat_loop.MAX_STEPS
