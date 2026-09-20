import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
from pathlib import Path


def show_player_fig(data, names=[], teams=[], positions=[]):
    df_1 = data.copy()
    if names:
        df_1 = df_1[df_1["name"].isin(names)]
    if teams:
        df_1 = df_1[df_1["team_name"].isin(teams)]
    if positions:
        df_1 = df_1[df_1["position"].isin(positions)]

    l = []
    fig = go.Figure()
    for pred_type in [
        "y",
        "y_Naive",
        "y_LGBMRegressor_no_exog",
        "y_LGBMRegressor_with_exog",
        "y_LSTMWithReLU",
    ]:
        l.append(
            go.Scatter(
                x=[df_1["season"], df_1["gameweek"]],
                y=df_1[pred_type],
                mode="lines",
                line=dict(width=2),
                name=pred_type,
                customdata=df_1[["name", "team_name", "position"]],
                hovertemplate="<b>%{customdata[0]}</b>"
                + "<br><br><b>Team:</b> %{customdata[1]}"
                + "<br><b>Position:</b> %{customdata[2]}"
                # + "<br><b>Opponent:</b> %{customdata[3]}"
                + "<extra></extra>",
            )
        )
    layout = go.Layout(
        legend=dict(orientation="h", x=0, y=1),
        xaxis_title="Season | Gameweek",
        yaxis_title="Points",
    )

    fig = go.Figure(data=l, layout=layout)
    return fig


def build_player_inf_plot(df_players, min_minutes):
    # min_minutes=45
    df_plot = df_players[df_players["minutes"] > min_minutes]
    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=df_plot[df_plot.position == "GK"]["assists"],
            y=df_plot[df_plot.position == "GK"]["goals_scored"],
            mode="markers",
            marker=dict(color="#abb8f1"),
            customdata=df_plot[df_plot.position == "GK"][
                ["web_name", "position", "team_name", "minutes"]
            ],
            hovertemplate="<b>%{customdata[0]}</b><br>Position: %{customdata[1]}<br>Team: %{customdata[2]}<br>Avg Minutes: %{customdata[3]}<br>Goals: %{y}<br>Assists: %{x}",
            name="Goalkeepers",
            showlegend=True,
        )
    )
    fig.add_trace(
        go.Scatter(
            x=df_plot[df_plot.position == "DEF"]["assists"],
            y=df_plot[df_plot.position == "DEF"]["goals_scored"],
            mode="markers",
            marker=dict(color="#818cb6"),
            customdata=df_plot[df_plot.position == "DEF"][
                ["web_name", "position", "team_name", "minutes"]
            ],
            hovertemplate="<b>%{customdata[0]}</b><br>Position: %{customdata[1]}<br>Team: %{customdata[2]}<br>Avg Minutes: %{customdata[3]}<br>Goals: %{y}<br>Assists: %{x}",
            name="Defenders",
            showlegend=True,
        )
    )
    fig.add_trace(
        go.Scatter(
            x=df_plot[df_plot.position == "MID"]["assists"],
            y=df_plot[df_plot.position == "MID"]["goals_scored"],
            mode="markers",
            marker=dict(color="#58617b"),
            customdata=df_plot[df_plot.position == "MID"][
                ["web_name", "position", "team_name", "minutes"]
            ],
            hovertemplate="<b>%{customdata[0]}</b><br>Position: %{customdata[1]}<br>Team: %{customdata[2]}<br>Avg Minutes: %{customdata[3]}<br>Goals: %{y}<br>Assists: %{x}",
            name="Midfielders",
            showlegend=True,
        )
    )

    fig.add_trace(
        go.Scatter(
            x=df_plot[df_plot.position == "FWD"]["assists"],
            y=df_plot[df_plot.position == "FWD"]["goals_scored"],
            mode="markers",
            marker=dict(color="black"),
            customdata=df_plot[df_plot.position == "FWD"][
                ["web_name", "position", "team_name", "minutes"]
            ],
            hovertemplate="<b>%{customdata[0]}</b><br>Position: %{customdata[1]}<br>Team: %{customdata[2]}<br>Avg Minutes: %{customdata[3]}<br>Goals: %{y}<br>Assists: %{x}",
            name="Forwards",
            showlegend=True,
        )
    )
    fig.update_layout(
        # add horizontal legend
        legend_orientation="h",
        legend=dict(x=0.1, y=-0.15),
        xaxis_title="Assist Probability",
        yaxis_title="Goal Probability",
        height=600,
    )
    return fig
