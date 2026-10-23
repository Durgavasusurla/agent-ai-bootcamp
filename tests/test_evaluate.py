from pathlib import Path

from agent.agent import Agent
from agent.config import Settings
from agent.evaluate import Case, grade, load_cases
from agent.memory import ConversationMemory
from tests.fakes import ScriptedCompleter, message, text_block, tool_use_block

ROOT = Path(__file__).resolve().parents[1]


def test_eval_file_loads():
    cases = load_cases()
    assert len(cases) >= 3 and all(c.question for c in cases)


def test_grade_pass_and_fail(tmp_path):
    settings = Settings(docs_dir=ROOT / "data" / "docs", memory_dir=tmp_path)
    completer = ScriptedCompleter(
        [
            message("tool_use", tool_use_block("t1", "calculator", {"expression": "2+2"})),
            message("end_turn", text_block("4")),
            message("end_turn", text_block("I think it is 5")),
        ]
    )
    agent = Agent(settings=settings, completer=completer, memory=ConversationMemory(tmp_path / "m.json"))
    ok, _ = grade(agent, Case("2+2?", expect_tool="calculator", expect_substring="4"))
    assert ok
    ok, detail = grade(agent, Case("2+2?", expect_tool="calculator", expect_substring="4"))
    assert not ok and "expected tool calculator" in detail
