import streamlit as st
from db import scoreline_grid
from plot_team import build_scoreline_heatmap
from utils import FAVICON, setup_logger

logger = setup_logger(__name__)
logger.debug("Running from top")


def get_matches(df_grid):
    return (
        df_grid[["home", "away", "kickoff_time"]]
        .drop_duplicates()
        .sort_values("kickoff_time")
    )


def initialise_session_vars(matches):
    if "match" not in st.session_state:
        st.session_state.match = (matches["home"] + " vs " + matches["away"]).iloc[0]


def main(df_grid, matches):
    st.title("🦁 Scoreline Predictions")
    with st.expander("More about scoreline predictions"):
        st.write(
            "The following plot shows the posterior distribution of goals for the selected home and away team, "
            "for the upcoming gameweek. These values show the posterior distribution of the number of goals scored, "
            "for given home and away strengths, in the following statistical model:"
        )

        st.latex(
            r"""\text{goals}_{\text{home}} \sim \text{Poisson}(\lambda_{\text{home}})"""
        )
        st.latex(
            r"""\text{goals}_{\text{away}} \sim \text{Poisson}(\lambda_{\text{away}})"""
        )

        st.write("Where:")
        st.latex(
            r"""
            \begin{align*}
                \text{log}(\lambda_{\text{home}}) &= \beta_0 + \beta_{\text{home advantage}} + \beta_{\text{attack, home team}} + \beta_{\text{defence, away team}} \\
                \text{log}(\lambda_{\text{away}}) &= \beta_0 + \beta_{\text{defence, home team}} + \beta_{\text{attack, away team}}

            \end{align*}
            """
        )

    home_team, away_team = st.session_state.match.split(" vs ")
    st.plotly_chart(build_scoreline_heatmap(df_grid, home_team, away_team), width="content")


def sidebar(matches):
    match_options = (matches["home"] + " vs " + matches["away"]).tolist()
    with st.sidebar:
        st.title("Filter the forecasts")
        st.selectbox("Match", match_options, key="match", index=0)


if __name__ == "__main__":
    st.set_page_config(
        page_title="lionel - Scoreline Predictions",
        page_icon=str(FAVICON),
    )
    df_grid = scoreline_grid()
    matches = get_matches(df_grid)
    initialise_session_vars(matches)
    main(df_grid, matches)
    sidebar(matches)
