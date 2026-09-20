import streamlit as st
from db import player_selection
from plot_team import create_plot, create_value_plot
from utils import get_gameweek, setup_logger

logger = setup_logger(__name__)
logger.debug("Running from top")


def main():
    st.title("🦁 Team Selections")
    df_sel = player_selection()

    # The gameweek this selection was made for comes from the selection
    # rows themselves, so the heading always matches what's on screen even
    # if the pipeline's next-gameweek run lags a day behind the fixture
    # calendar.
    selection_gw = int(df_sel["gameweek"].iloc[0])
    upcoming_gw = get_gameweek()
    if selection_gw != upcoming_gw:
        st.caption(
            f"Showing the most recent selection (gameweek {selection_gw}). "
            f"The upcoming gameweek is {upcoming_gw} — the pipeline may not "
            "have run for it yet."
        )

    tab1, tab2 = st.tabs(["🤖 Team Selection", ":chart: Team Forecasts and Values"])
    with tab1:
        st.subheader(f"Team Selections for Gameweek {selection_gw}")
        st.plotly_chart(create_plot(df_sel))

    with tab2:
        st.subheader(f"Team Forecasts and Values for Gameweek {selection_gw}")
        st.plotly_chart(create_value_plot(df_sel))


if __name__ == "__main__":
    st.set_page_config(
        page_title="lionel - Selections",
    )
    main()
