-- fct_sel_player holds exactly one (gameweek, season) at a time -- the most
-- recent selection run -- so no filter is needed. Keep every candidate
-- (both xv values): create_value_plot needs the unpicked players too.
SELECT
    player_id,
    web_name,
    team_name,
    position,
    value,
    gameweek,
    season,
    points_pred,
    xv,
    xi,
    captain
FROM fct_sel_player
ORDER BY position, points_pred DESC
