"""Lab 05 - evaluation.

Agents fail quietly: wrong tool, no tool, hallucinated source. A tiny eval set
with deterministic checks catches regressions every time you change the prompt
or the tools. This mirrors what MLflow's agent evaluation does at scale.

Run:  python -m agent.evaluate
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

from .agent import Agent

EVAL_FILE = Path(__file__).resolve().parents[2] / "data" / "evals.json"


@dataclass
class Case:
    question: str
    expect_tool: str | None = None  # a tool that must be called
    expect_substring: str | None = None  # text that must appear in the answer (case-insensitive)


def load_cases(path: Path = EVAL_FILE) -> list[Case]:
    return [Case(**c) for c in json.loads(path.read_text(encoding="utf-8"))]


def grade(agent: Agent, case: Case) -> tuple[bool, str]:
    agent.reset()
    answer = agent.ask(case.question)
    used = {c["name"] for c in agent.last_trace.tool_calls}
    problems = []
    if case.expect_tool and case.expect_tool not in used:
        problems.append(f"expected tool {case.expect_tool}, used {sorted(used) or 'none'}")
    if case.expect_substring and case.expect_substring.lower() not in answer.lower():
        problems.append(f"expected '{case.expect_substring}' in answer: {answer[:120]!r}")
    return (not problems, "; ".join(problems) or "ok")


def run(agent: Agent | None = None, cases: list[Case] | None = None) -> float:
    agent = agent or Agent(session="eval")
    cases = cases or load_cases()
    passed = 0
    for case in cases:
        ok, detail = grade(agent, case)
        passed += ok
        print(f"[{'PASS' if ok else 'FAIL'}] {case.question}  ->  {detail}")
    score = passed / len(cases) if cases else 0.0
    print(f"\n{passed}/{len(cases)} passed ({score:.0%})")
    return score


if __name__ == "__main__":
    raise SystemExit(0 if run() == 1.0 else 1)
