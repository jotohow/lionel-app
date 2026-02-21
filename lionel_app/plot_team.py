import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
from pathlib import Path

DATA = Path(__file__).parents[1] / "data"


def _create_pitch():
    line_width = 3
    fig = go.Figure()

    fig.add_vrect(x0=-350, x1=350, line=dict(color="#9fbbe3", width=4))  # width=3

    fig.add_trace(
        go.Scatter(
            x=[-350, 350],
            y=[0, 0],
            marker=dict(size=25, color="#9fbbe3"),
            mode="lines",
            line=dict(color="#9fbbe3", width=line_width),
        )
    )

    fig.add_shape(
        type="circle",
        xref="x",
        yref="y",
        x0=-100,
        y0=-100,
        x1=100,
        y1=100,
        line=dict(color="#9fbbe3", width=line_width - 1),
    )

    fig.add_trace(
        go.Scatter(
            x=[-180, -180, 180, 180],
            y=[
                -550,
                -400,
                -400,
                -550,
            ],
            mode="lines",
            line_color="#9fbbe3",
            showlegend=False,
            line=dict(color="#9fbbe3", width=line_width),
        )
    )

    fig.add_trace(
        go.Scatter(
            x=[-180, -180, 180, 180],
            y=[
                550,
                400,
                400,
                550,
            ],
            mode="lines",
            line_color="#9fbbe3",
            showlegend=False,
            line=dict(color="#9fbbe3", width=line_width),
        )
    )

    fig.update_layout(
        font_family="sans-serif",
        autosize=False,
        width=600,
        height=800,
        yaxis_range=[-550, 550],
        xaxis_range=[-400, 400],
        showlegend=False,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
    )

    fig.update_xaxes(visible=False)
    fig.update_yaxes(visible=False)
    return fig


def _plot_players(first_xi, position, fig):
    df = first_xi.loc[first_xi.position == position]

    Y = {"FWD": 350, "MID": 75, "DEF": -250, "GK": -475}

    dims = [-250, 250]
    width = dims[1] - dims[0]

    if len(df) > 1:
        divisor = len(df) - 1
        jump = int(width / divisor)
        X = list(range(dims[0], dims[1] + 1, jump))
    else:
        X = [0]

    fig.add_trace(
        go.Scatter(
            x=X,
            y=[Y[position]] * len(df),
            mode="markers+text",
            marker=dict(size=25, color="#4B5563"),
            text=df["name"].str.split().str[-1],
            textposition="bottom center",
            textfont=dict(color="#4B5563"),
            textfont_size=10,
            customdata=df[["name", "team_name", "points_pred"]],
            hovertemplate="<b>%{customdata[0]}</b>"
            + "<br><br><b>Team:</b> %{customdata[1]}"
            + "<br><b>Mean Predicted Points:</b> %{customdata[2]}"
            + "<extra></extra>",
        )
    )

    return fig


def _plot_subs(team, fig):

    df = team.loc[team["xi"] == 0]

    X = [375] * 4
    Y = [-90, -30, 30, 90]

    fig.add_trace(
        go.Scatter(
            x=X,
            y=Y,
            mode="markers",
            marker=dict(size=25, color="#4B5563"),
            text=df["name"].str.split().str[-1],
            textposition="bottom left",
            textfont=dict(color="#4B5563"),
            textfont_size=10,
            customdata=df[["name", "team_name", "points_pred"]],
            hovertemplate="<b>%{customdata[0]}</b>"
            + "<br><br><b>Team:</b> %{customdata[1]}"
            + "<br><b>Mean Predicted Points:</b> %{customdata[2]}"
            + "<extra></extra>",
        )
    )
    return fig


def create_plot(players):

    # players = pd.read_csv(DATA / f"team_selection_{next_gw}_{season}.csv")
    players["points_pred"] = players["points_pred"].round(1)
    players["name"] = players["web_name"]
    team = players[players["xv"] == 1]
    first_xi = team.loc[team["xi"] == 1]

    fig = _create_pitch()
    for pos in ["FWD", "MID", "DEF", "GK"]:
        _plot_players(first_xi, pos, fig)

    fig = _plot_subs(team, fig)
    fig.update_layout(
        height=725,
        width=500,
        margin={"t": 10, "b": 0},
    )

    return fig


def create_value_plot(df_team):
    # df_team = pd.read_csv(DATA / f"team_selection_{next_gw}_{season}.csv")
    # df_team = pd.read_csv(DATA / f"team_selection_{next_gw}_{season}.csv")
    df_team["name"] = df_team["web_name"]
    df_team["points_pred"] = df_team["points_pred"].round(1)
    df_not_picked = df_team[df_team["xv"] == 0]
    df_picked = df_team[df_team["xv"] == 1]

    fig = go.Figure()

    # Plot the unpicked players
    fig.add_trace(
        go.Scatter(
            x=df_not_picked.value,
            y=df_not_picked["points_pred"],
            marker=dict(
                color="#9fbbe3",
            ),
            mode="markers",
            customdata=df_not_picked[["name", "team_name", "points_pred"]],
            hovertemplate="<b>%{customdata[0]}</b>"
            + "<br><br><b>Team:</b> %{customdata[1]}"
            + "<br><b>Mean Predicted Points:</b> %{customdata[2]}"
            + "<extra></extra>",
        )
    )

    # Plot the picked players
    fig.add_trace(
        go.Scatter(
            x=df_picked.value,
            y=df_picked["points_pred"],
            marker=dict(
                color="#4B5563",
            ),
            mode="markers",
            customdata=df_picked[["name", "team_name", "points_pred"]],
            hovertemplate="<b>%{customdata[0]}</b>"
            + "<br><br><b>Team:</b> %{customdata[1]}"
            + "<br><b>Mean Predicted Points:</b> %{customdata[2]}"
            + "<extra></extra>",
        )
    )

    fig.update_layout(
        autosize=False,
        width=700,
        height=800,
        showlegend=False,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        xaxis_title="Player Value (as of previous GW)",
        yaxis_title="Predicted Points (Mean of next 5 games)",
        yaxis_visible=True,
        yaxis_showticklabels=False,
        xaxis_visible=True,
        xaxis_showticklabels=False,
        font=dict(family="sans-serif", color="#4B5563"),
        margin={"t": 10, "b": 0},
    )
    return fig


def build_scoreline_plot(df_scoreline, home, away):
    df_plot = df_scoreline[
        (df_scoreline["home"] == home) & (df_scoreline["away"] == away)
    ]

    fig = go.Figure(
        go.Histogram2d(
            x=df_plot["home_goals"],
            y=df_plot["away_goals"],
            histnorm="probability",
            autobinx=False,
            xbins=dict(start=0, end=6, size=1),
            autobiny=False,
            ybins=dict(start=0, end=6, size=1),
            colorscale=["white", "#4b5563"],
            customdata=df_plot[["home", "away", "home_goals", "away_goals"]],
            name=f"{home} - {away} Scoreline Probability",
            hovertemplate="Probability: %{z:.01%}",  # + "<br>Home Goals: %{customdata[2]} <br>Away Goals: %{customdata[3]}",
        )
    )
    fig.update_layout(
        #     title="Plot Title",
        xaxis_title=f"Home ({home}) Goals",
        yaxis_title=f"Away ({away}) Goals",
        width=600,
        height=600,
    )

    return fig


def build_team_inf_plot(df_team_inf):
    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=df_team_inf["attack"],
            y=df_team_inf["defence"],
            mode="markers",
            marker=dict(color="#58617b"),
            customdata=df_team_inf[["team_name", "attack", "defence"]],
            hovertemplate=(
                "<b>%{customdata[0]}</b>"
                + "<br>Attack: %{customdata[1]:.1%}"
                + "<br>Defence: %{customdata[2]:.1%}"
            ),
            name="",
        )
    )
    fig.update_layout(
        xaxis_title="Attack Strength",
        yaxis_title="Defence Strength",
        width=1000,
        height=600,
    )
    return fig
