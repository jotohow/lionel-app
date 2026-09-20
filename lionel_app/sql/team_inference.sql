-- Team attack/defence strength for the current league.
-- fct_ml_team_inference carries every team that has ever been modelled
-- (25 rows), including clubs no longer in the top flight; filter to teams
-- with a fixture in the current season.
SELECT team_name, attack, defence
FROM fct_ml_team_inference
WHERE team_id IN (SELECT team_h_id FROM fct_fixtures WHERE season = ?)
