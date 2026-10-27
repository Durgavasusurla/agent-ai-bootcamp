"""Evaluation helpers (course 04-evaluation/code/evaluation_utils.py), adapted for Groq.

Changes from the course version:
- Default model: openai/gpt-oss-120b on Groq (course: gpt-5.4-mini on OpenAI).
- Prices: Groq gpt-oss-120b $0.15 input / $0.60 output per 1M tokens
  (course: $0.75 / $4.50 for gpt-5.4-mini).
- Retry: Groq free tier allows 8,000 tokens/minute and 1,000 requests/day,
  so rate-limit (429) errors are expected. The retry waits longer and
  honours the server's retry-after hint (course: 3 tries, 1-4 s waits).

Groq supports the OpenAI Responses API, including responses.parse with a
Pydantic text_format, so the call code itself is unchanged.
"""

import time

import openai
from tqdm.auto import tqdm
from rag_helper import RAGBase

MODEL = "openai/gpt-oss-120b"
INPUT_PRICE_PER_MILLION = 0.15
OUTPUT_PRICE_PER_MILLION = 0.60


def calc_price(usage):
    input_cost = (usage.input_tokens / 1_000_000) * INPUT_PRICE_PER_MILLION
    output_cost = (usage.output_tokens / 1_000_000) * OUTPUT_PRICE_PER_MILLION
    total_cost = input_cost + output_cost

    return {
        "input_cost": input_cost,
        "output_cost": output_cost,
        "total_cost": total_cost,
    }


def calc_total_price(usages):
    total_cost = 0.0

    for usage in usages:
        cost = calc_price(usage)
        total_cost = total_cost + cost["total_cost"]

    return total_cost


def llm_structured(client, instructions, user_prompt, output_type, model=MODEL):
    messages = [
        {"role": "developer", "content": instructions},
        {"role": "user", "content": user_prompt}
    ]

    response = client.responses.parse(
        model=model,
        input=messages,
        text_format=output_type
    )

    return response.output_parsed, response.usage


def _wait_seconds(error, attempt):
    """How long to wait before the next try."""
    if isinstance(error, openai.RateLimitError):
        retry_after = None
        try:
            retry_after = float(error.response.headers.get("retry-after"))
        except (AttributeError, TypeError, ValueError):
            pass
        return max(retry_after or 0, 10 * (attempt + 1))
    return 2 ** attempt


def with_retry(fn, max_retries=8):
    """Call fn(); on failure wait and try again (longer waits for 429)."""
    for attempt in range(max_retries):
        try:
            return fn()
        except Exception as e:
            if attempt == max_retries - 1:
                raise
            time.sleep(_wait_seconds(e, attempt))


def llm_structured_retry(
    client,
    instructions,
    user_prompt,
    output_type,
    model=MODEL,
    max_retries=8,
):
    return with_retry(
        lambda: llm_structured(client, instructions, user_prompt, output_type, model=model),
        max_retries=max_retries,
    )


class RAGWithUsage(RAGBase):

    def __init__(self, *args, **kwargs):
        kwargs.setdefault("model", MODEL)
        super().__init__(*args, **kwargs)
        self.usages = []
        self.last_usage = None

    def reset_usage(self):
        self.usages = []
        self.last_usage = None

    def search(self, query, num_results=5):
        boost_dict = {"question": 1.0, "answer": 2.0, "section": 0.1}
        filter_dict = {"course": self.course}

        return self.index.search(
            query,
            num_results=num_results,
            boost_dict=boost_dict,
            filter_dict=filter_dict
        )

    def llm(self, prompt):
        input_messages = [
            {"role": "developer", "content": self.instructions},
            {"role": "user", "content": prompt}
        ]

        response = with_retry(lambda: self.llm_client.responses.create(
            model=self.model,
            input=input_messages
        ))

        self.last_usage = response.usage
        self.usages.append(response.usage)

        return response.output_text

    def total_cost(self):
        return calc_total_price(self.usages)


def map_progress(pool, seq, f):
    results = []

    with tqdm(total=len(seq)) as progress:
        futures = []

        for el in seq:
            future = pool.submit(f, el)
            future.add_done_callback(lambda p: progress.update())
            futures.append(future)

        for future in futures:
            result = future.result()
            results.append(result)

    return results
