"""Capturing metrics for every LLM call (course lesson 04), Groq prices."""

import time
from dataclasses import dataclass, field
from datetime import datetime

from rag_helper import RAGBase


@dataclass
class LLMCallRecord:
    model: str
    prompt: str
    instructions: str
    answer: str
    prompt_tokens: int
    completion_tokens: int
    total_tokens: int
    response_time: float
    cost: float
    timestamp: datetime = field(default_factory=datetime.now)


# USD per 1M tokens (input, output)
PRICES = {
    "gpt-oss-120b": (0.15, 0.60),   # Groq, console.groq.com/docs/model/openai/gpt-oss-120b
    "gpt-5.4-mini": (0.15, 0.60),   # numbers used in the course lesson
}


def calculate_cost(model, usage):
    for name, (inp, out) in PRICES.items():
        if name in model:
            return (usage.input_tokens * inp + usage.output_tokens * out) / 1_000_000
    return 0


class RAGWithMetrics(RAGBase):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.last_call: LLMCallRecord = None

    def llm(self, prompt):
        start_time = time.time()
        response = self._call_llm(prompt)
        response_time = time.time() - start_time
        self._log_response(prompt, response, response_time)
        return response.output_text

    def _call_llm(self, prompt):
        input_messages = [
            {"role": "developer", "content": self.instructions},
            {"role": "user", "content": prompt}
        ]
        # Groq supports the Responses API, so the call is the course code.
        # Extra: retry on Groq free-tier 429s; the wait counts in response_time,
        # because the user really waits that long.
        from evaluation_utils import with_retry

        response = with_retry(lambda: self.llm_client.responses.create(
            model=self.model,
            input=input_messages
        ))
        return response

    def _log_response(self, prompt, response, response_time):
        usage = response.usage
        cost = calculate_cost(self.model, usage)

        call_record = LLMCallRecord(
            model=self.model,
            prompt=prompt,
            instructions=self.instructions,
            answer=response.output_text,
            prompt_tokens=usage.input_tokens,
            completion_tokens=usage.output_tokens,
            total_tokens=usage.total_tokens,
            response_time=response_time,
            cost=cost,
        )

        print(call_record)
        self.last_call = call_record
