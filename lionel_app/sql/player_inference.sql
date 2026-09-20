-- Player goal/assist/no-contribution probabilities, enriched with current
-- team and average minutes for the current season.
--
-- fct_ml_player_inference is already one row per player (single model_date),
-- so no aggregation is needed there. Team name and "current" status come
-- from dim_players_current / dim_teams, not from fct_stats, since a
-- player's most recent stats row can lag a transfer. Minutes are averaged
-- over the current season only -- averaging across all seasons mixes in
-- players' time at other clubs and is misleading for a minutes filter.
SELECT
    i.player_id,
    i.web_name,
    i.position,
    t.name AS team_name,
    i.goals_scored,
    i.assists,
    i.no_contribution,
    ROUND(AVG(s.minutes)) AS minutes
FROM fct_ml_player_inference i
JOIN dim_players_current d USING (player_id)
LEFT JOIN dim_teams t ON t.team_id = d.team_id
LEFT JOIN fct_stats s ON s.player_id = i.player_id AND s.season = ?
WHERE d.latest_season = ?
GROUP BY ALL
