"""Save user / judge feedback (course lesson 08)."""

from db_init import get_db_connection, now_value, sql


def save_feedback(conversation_id, source, relevance=None,
                  explanation=None, score=None):
    timestamp = now_value()

    conn = get_db_connection()
    try:
        cur = conn.cursor()
        cur.execute(
            sql("""
            INSERT INTO feedback (
                conversation_id, source, relevance,
                explanation, score, timestamp
            ) VALUES (
                %s, %s, %s, %s, %s, %s
            )
            """),
            (conversation_id, source, relevance,
             explanation, score, timestamp),
        )
        conn.commit()
    finally:
        conn.close()
