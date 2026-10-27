"""Synthetic monitoring data (course lesson 11).

Run:  uv run python generate_data.py            # one row per second until Ctrl+C
      uv run python generate_data.py --count 60 # stop after 60 rows (extra option)
"""

import random
import sys
import time

from metrics import LLMCallRecord
from db_save import save_conversation
from db_feedback import save_feedback

SAMPLE_QUESTIONS = [
    "How do I install Docker?",
    "Can I still join the course?",
    "What are the prerequisites?",
    "How do I submit homework?",
    "When are the office hours?",
]

SAMPLE_ANSWERS = [
    "You can install Docker by downloading Docker Desktop from the official website.",
    "Yes, you can join at any time. The materials remain available.",
    "You need basic Python knowledge and familiarity with the command line.",
    "Submit your homework through the course portal before the deadline.",
    "Office hours are held weekly. Check the calendar for details.",
]

RELEVANCE = ["RELEVANT", "PARTLY_RELEVANT", "NON_RELEVANT"]


def fake_record(question, answer):
    return LLMCallRecord(
        model="gpt-5.4-mini",
        prompt=question,
        instructions="",
        answer=answer,
        prompt_tokens=random.randint(50, 200),
        completion_tokens=random.randint(50, 300),
        total_tokens=random.randint(100, 500),
        response_time=random.uniform(0.5, 5.0),
        cost=random.uniform(0.0001, 0.01),
    )


def random_score():
    return random.choice([1, 1, 1, 1, -1])


def generate_one():
    question = random.choice(SAMPLE_QUESTIONS)
    answer = random.choice(SAMPLE_ANSWERS)
    record = fake_record(question, answer)

    conversation_id = save_conversation(record, question, "llm-zoomcamp")

    if random.random() < 0.7:
        relevance = random.choice(RELEVANCE)
        save_feedback(
            conversation_id, "judge",
            relevance=relevance,
            explanation=f"Answer is {relevance.lower()}.",
        )

    if random.random() < 0.5:
        save_feedback(conversation_id, "user", score=random_score())


def generate_live(count=None, delay=1.0):
    print("Starting live data generation (Ctrl+C to stop)...", flush=True)
    n = 0
    while count is None or n < count:
        generate_one()
        n += 1
        time.sleep(delay)
    print(f"Generated {n} conversations.")


if __name__ == "__main__":
    count = int(sys.argv[sys.argv.index("--count") + 1]) if "--count" in sys.argv else None
    try:
        generate_live(count=count)
    except KeyboardInterrupt:
        print("Stopped.")
