from pathlib import Path

from agent.agent import Agent
from agent.config import Settings
from agent.memory import ConversationMemory
from tests.fakes import ScriptedCompleter, message, text_block, tool_use_block

ROOT = Path(__file__).resolve().parents[1]


def make_agent(tmp_path, responses):
    settings = Settings(docs_dir=ROOT / "data" / "docs", memory_dir=tmp_path, max_turns=5)
    completer = ScriptedCompleter(responses)
    agent = Agent(settings=settings, completer=completer, memory=ConversationMemory(tmp_path / "m.json"))
    return agent, completer


def test_plain_answer_without_tools(tmp_path):
    agent, completer = make_agent(tmp_path, [message("end_turn", text_block("Hello!"))])
    assert agent.ask("hi") == "Hello!"
    assert agent.last_trace.tool_calls == []
    assert len(completer.requests) == 1
    assert completer.requests[0]["messages"][0] == {"role": "user", "content": "hi"}


def test_tool_call_round_trip(tmp_path):
    agent, completer = make_agent(
        tmp_path,
        [
            message("tool_use", tool_use_block("t1", "calculator", {"expression": "6 * 7"})),
            message("end_turn", text_block("It is 42.")),
        ],
    )
    assert agent.ask("what is 6*7?") == "It is 42."
    assert agent.last_trace.tool_calls[0]["output"] == "42"
    # Second request must carry the tool_result back to the model
    second = completer.requests[1]["messages"]
    assert second[-1]["role"] == "user"
    assert second[-1]["content"][0] == {"type": "tool_result", "tool_use_id": "t1", "content": "42", "is_error": False}


def test_tool_error_is_reported_not_raised(tmp_path):
    agent, _ = make_agent(
        tmp_path,
        [
            message("tool_use", tool_use_block("t1", "calculator", {"expression": "1 / 0"})),
            message("end_turn", text_block("Division by zero.")),
        ],
    )
    agent.ask("1/0?")
    call = agent.last_trace.tool_calls[0]
    assert call["error"] is True and "ZeroDivisionError" in call["output"]


def test_max_turns_guard(tmp_path):
    loop = [message("tool_use", tool_use_block(f"t{i}", "list_notes", {})) for i in range(5)]
    agent, _ = make_agent(tmp_path, loop)
    assert "ran out of steps" in agent.ask("loop forever")
    assert agent.last_trace.turns == 5


def test_refusal_stop_reason(tmp_path):
    agent, _ = make_agent(tmp_path, [message("refusal")])
    assert "can't help" in agent.ask("...")


def test_memory_persists_across_instances(tmp_path):
    agent, _ = make_agent(tmp_path, [message("end_turn", text_block("ok"))])
    agent.ask("remember me")
    reloaded = ConversationMemory(tmp_path / "m.json")
    assert [m["role"] for m in reloaded.messages] == ["user", "assistant"]
