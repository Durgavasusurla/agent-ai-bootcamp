"""Interactive chat. Run with:  python -m agent"""

from __future__ import annotations

import sys

from .agent import Agent


def main() -> None:
    session = sys.argv[1] if len(sys.argv) > 1 else "default"
    agent = Agent(session=session)
    print(f"agent-ai-bootcamp | model={agent.settings.model} | session={session}")
    print("type 'exit' to quit, '/reset' to clear memory, '/trace' to see last tool calls\n")
    while True:
        try:
            user = input("you > ").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            break
        if not user:
            continue
        if user.lower() in {"exit", "quit"}:
            break
        if user == "/reset":
            agent.reset()
            print("memory cleared\n")
            continue
        if user == "/trace":
            for call in agent.last_trace.tool_calls:
                print(f"  {call['name']}({call['input']}) -> {call['output'][:80]!r}")
            print()
            continue
        answer = agent.ask(user)
        print(f"\nagent > {answer}\n")


if __name__ == "__main__":
    main()
