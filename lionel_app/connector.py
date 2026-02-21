import os

import pandas as pd
import requests

API_URL = os.environ.get("API_URL", "http://localhost:8000")


def get_team_inference() -> pd.DataFrame:
    return pd.DataFrame(requests.get(f"{API_URL}/inference/teams").json())


def get_player_inference() -> pd.DataFrame:
    return pd.DataFrame(requests.get(f"{API_URL}/inference/players").json())


def get_team_preds() -> pd.DataFrame:
    return pd.DataFrame(requests.get(f"{API_URL}/prediction/teams").json())


def get_player_preds() -> pd.DataFrame:
    return pd.DataFrame(requests.get(f"{API_URL}/prediction/players").json())
