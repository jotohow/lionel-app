import streamlit as st
from About import NEXT_GW
from connector import get_player_preds
from plot_team import create_plot, create_value_plot
from utils import setup_logger

logger = setup_logger(__name__)
logger.debug("Running from top")


@st.cache_data(ttl=600, show_spinner="Pulling data...")
def get_df_sel():
    df = get_player_preds()
    return df[df["gameweek"] == NEXT_GW]


def main():
    st.title("🦁 Team Selections")
    df_sel = get_df_sel()

    tab1, tab2 = st.tabs(["🤖 Team Selection", ":chart: Team Forecasts and Values"])
    with tab1:
        st.subheader(f"Team Selections for Gameweek {NEXT_GW}")
        st.plotly_chart(create_plot(df_sel))

    with tab2:
        st.subheader(f"Team Forecasts and Values for Gameweek {NEXT_GW}")
        st.plotly_chart(create_value_plot(df_sel))


if __name__ == "__main__":
    st.set_page_config(
        page_title="lionel - Selections",
    )
    main()
