"""Save an LLMCallRecord (course lesson 05)."""

from db_init import get_db_connection, now_value, sql


def save_conversation(record, question, course):
    timestamp = now_value()

    conn = get_db_connection()
    try:
        cur = conn.cursor()
        cur.execute(
            sql("""
            INSERT INTO conversations (
                question, answer, course, model, instructions, prompt,
                prompt_tokens, completion_tokens, total_tokens,
                response_time, cost, timestamp
            ) VALUES (
                %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
            )
            RETURNING id
            """),
            (
                question,
                record.answer,
                course,
                record.model,
                record.instructions,
                record.prompt,
                record.prompt_tokens,
                record.completion_tokens,
                record.total_tokens,
                record.response_time,
                record.cost,
                timestamp,
            ),
        )
        conversation_id = cur.fetchone()[0]
        conn.commit()
    finally:
        conn.close()
    return conversation_id
