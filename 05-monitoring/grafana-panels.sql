-- Course lesson 12: Grafana panel queries (PostgreSQL datasource).
-- Grafana macros: $__timeFrom(), $__timeTo(), $__timeGroup(column, $__interval)

-- Response Time (Time series)
SELECT timestamp AS time, response_time
FROM conversations
WHERE timestamp BETWEEN $__timeFrom() AND $__timeTo()
ORDER BY timestamp;

-- Token Usage (Time series)
SELECT $__timeGroup(timestamp, $__interval) AS time, AVG(total_tokens) AS avg_tokens
FROM conversations
WHERE timestamp BETWEEN $__timeFrom() AND $__timeTo()
GROUP BY 1
ORDER BY 1;

-- Cost (Time series)
SELECT $__timeGroup(timestamp, $__interval) AS time, SUM(cost) AS total_cost
FROM conversations
WHERE timestamp BETWEEN $__timeFrom() AND $__timeTo()
  AND cost > 0
GROUP BY 1
ORDER BY 1;

-- Model Usage (Bar chart)
SELECT model, COUNT(*) AS count
FROM conversations
WHERE timestamp BETWEEN $__timeFrom() AND $__timeTo()
GROUP BY model;

-- Relevance Distribution (Pie chart)
SELECT relevance, COUNT(*) AS count
FROM feedback
WHERE source = 'judge'
  AND timestamp BETWEEN $__timeFrom() AND $__timeTo()
GROUP BY relevance;

-- User Feedback (Gauge / Pie)
SELECT
  SUM(CASE WHEN score > 0 THEN 1 ELSE 0 END) AS thumbs_up,
  SUM(CASE WHEN score < 0 THEN 1 ELSE 0 END) AS thumbs_down
FROM feedback
WHERE source = 'user'
  AND timestamp BETWEEN $__timeFrom() AND $__timeTo();

-- Recent Conversations (Table)
SELECT timestamp AS time, question, answer, response_time, cost
FROM conversations
WHERE timestamp BETWEEN $__timeFrom() AND $__timeTo()
ORDER BY timestamp DESC
LIMIT 5;
