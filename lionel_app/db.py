"""Direct DuckDB access to the published lionel database.

Replaces connector.py's HTTP calls to a FastAPI backend that is no longer
deployed anywhere. Streamlit is already a persistent server-side process,
so it queries the database directly -- see ../../docs/STREAMLIT_RECONNECT.md
and ../../docs/R2_ACCESS.md for the background and the exact ATTACH syntax
this depends on.

Each public function opens its own short-lived connection rather than
reusing a cached one. The pipeline overwrites latest.duckdb in place once a
day; a connection attached over httpfs holds cached block offsets, so a
long-lived connection would start returning corruption errors after the
file underneath it changes. At a handful of queries per hour (each wrapped
in @st.cache_data), the extra connection overhead is irrelevant.
"""

import os
from contextlib import contextmanager
from pathlib import Path

import duckdb
import pandas as pd
import streamlit as st

SQL_DIR = Path(__file__).parent / "sql"

R2_BUCKET_PATH = "db/latest.duckdb"


def _secret(name: str) -> str | None:
    """Read a config value from st.secrets, falling back to an env var.

    The env fallback lets query functions be exercised from a plain script
    or CI without a .streamlit/secrets.toml file.
    """
    try:
        if name in st.secrets:
            return st.secrets[name]
    except Exception:
        pass
    return os.environ.get(name.upper())


def _escape(value: str) -> str:
    return value.replace("'", "''")


@contextmanager
def connection():
    """Yield a DuckDB connection attached to the published database.

    If `lionel_db_path` (or LIONEL_DB_PATH) is set, opens that local file
    read-only instead of going to R2 -- useful for offline development and
    for verifying the SQL independently of network/credentials.
    """
    local_path = _secret("lionel_db_path")
    if local_path:
        con = duckdb.connect(str(local_path), read_only=True)
        try:
            yield con
        finally:
            con.close()
        return

    key_id = _secret("r2_access_key_id")
    secret = _secret("r2_secret_access_key")
    account_id = _secret("r2_account_id")
    bucket = _secret("r2_bucket")
    missing = [
        n
        for n, v in [
            ("r2_access_key_id", key_id),
            ("r2_secret_access_key", secret),
            ("r2_account_id", account_id),
            ("r2_bucket", bucket),
        ]
        if not v
    ]
    if missing:
        raise RuntimeError(
            "Missing R2 config: "
            + ", ".join(missing)
            + ". Set these in .streamlit/secrets.toml (see "
            ".streamlit/secrets.toml.example) or as environment variables."
        )

    # Connect to memory first, configure, THEN attach. Opening the remote
    # file directly (duckdb.connect("r2://...")) fails during process
    # startup, before httpfs is loaded or any secret exists -- see
    # docs/R2_ACCESS.md "What doesn't work".
    con = duckdb.connect()
    try:
        con.execute("INSTALL httpfs; LOAD httpfs;")
        con.execute(
            f"""
            CREATE OR REPLACE SECRET r2_secret (
                TYPE R2,
                KEY_ID '{_escape(key_id)}',
                SECRET '{_escape(secret)}',
                ACCOUNT_ID '{_escape(account_id)}'
            )
            """
        )
        con.execute(f"ATTACH 'r2://{bucket}/{R2_BUCKET_PATH}' AS lionel (READ_ONLY)")
        con.execute("USE lionel")
        yield con
    finally:
        con.close()


def _query(sql_file: str, params: tuple = ()) -> pd.DataFrame:
    query = (SQL_DIR / sql_file).read_text()
    try:
        with connection() as con:
            return con.execute(query, params).fetchdf()
    except Exception as exc:
        st.error(f"Could not load data from the database: {exc}")
        st.stop()
        raise  # unreachable; keeps type checkers happy


def next_gameweek() -> tuple[int, int]:
    """Return (gameweek, season) for the next gameweek with an upcoming deadline.

    Falls back to the latest known gameweek if none are upcoming (e.g.
    between seasons). Port of lionel-backend/pipeline/db.py::get_next_gameweek.
    """
    with connection() as con:
        row = con.execute(
            """
            SELECT gameweek, season
            FROM dim_gameweeks
            WHERE deadline > now()
            ORDER BY deadline
            LIMIT 1
            """
        ).fetchone()
        if row is None:
            row = con.execute(
                """
                SELECT gameweek, season
                FROM dim_gameweeks
                ORDER BY season DESC, gameweek DESC
                LIMIT 1
                """
            ).fetchone()
    if row is None:
        raise RuntimeError("No gameweeks found in dim_gameweeks.")
    return row[0], row[1]


@st.cache_data(ttl=3600, show_spinner="Pulling team inference...")
def team_inference() -> pd.DataFrame:
    _, season = next_gameweek()
    return _query("team_inference.sql", (season,))


@st.cache_data(ttl=3600, show_spinner="Pulling player inference...")
def player_inference() -> pd.DataFrame:
    _, season = next_gameweek()
    return _query("player_inference.sql", (season, season))


@st.cache_data(ttl=3600, show_spinner="Pulling team selection...")
def player_selection() -> pd.DataFrame:
    return _query("player_selection.sql")


@st.cache_data(ttl=3600, show_spinner="Pulling scoreline predictions...")
def scoreline_grid() -> pd.DataFrame:
    gameweek, season = next_gameweek()
    return _query("scoreline_grid.sql", (gameweek, season))
