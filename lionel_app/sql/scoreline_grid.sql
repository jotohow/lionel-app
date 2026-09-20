-- Scoreline probability grid for the fixtures in one gameweek.
--
-- fct_ml_fixture_preds is raw MCMC posterior draws at match x chain x draw
-- grain (~1500 draws per fixture, ~570k rows across the season). Never
-- SELECT * from it -- see docs/DATA_CONTRACTS.md #6. This aggregates to a
-- probability per (home, away, home_goals, away_goals) before it ever
-- leaves DuckDB, so the app receives ~49 rows per fixture instead of ~1500.
--
-- fct_ml_fixture_preds.match is a model-internal index, not a fixture id,
-- so fixtures for the target gameweek are matched by team pair instead.
WITH gw_fixtures AS (
    SELECT team_h_id, team_a_id, kickoff_time
    FROM fct_fixtures
    WHERE gameweek = ? AND season = ?
),
draws AS (
    SELECT
        p.home_team AS home,
        p.away_team AS away,
        LEAST(p.home_goals, 6) AS home_goals,
        LEAST(p.away_goals, 6) AS away_goals,
        f.kickoff_time
    FROM fct_ml_fixture_preds p
    JOIN gw_fixtures f
        ON f.team_h_id = p.home_team_id AND f.team_a_id = p.away_team_id
)
SELECT
    home,
    away,
    home_goals,
    away_goals,
    kickoff_time,
    COUNT(*)::DOUBLE / SUM(COUNT(*)) OVER (PARTITION BY home, away) AS probability
FROM draws
GROUP BY home, away, home_goals, away_goals, kickoff_time
