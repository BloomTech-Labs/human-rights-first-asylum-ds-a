from plotly.graph_objects import Figure
import plotly.graph_objects as go
from app.db_ops import get_df
import pandas as pd


def get_judge_vis(judge_id: int) -> Figure:
    df = get_df()
    judge_df = df[df["judge_id"] == judge_id]
    cross_tab = pd.crosstab(judge_df["protected_grounds"], judge_df["outcome"])
    data = [
        go.Bar(name=col, x=cross_tab.index, y=cross_tab[col])
        for col in cross_tab.columns
    ]
    layout = go.Layout(
        title="Outcome by Protected Grounds",
        barmode="group",
    )
    return go.Figure(data, layout)


def get_judge_feature_vis(judge_id: int, feature: str) -> Figure:
    feature_name = feature.title().replace('_', ' ')
    df = get_df()
    judge_df = df[df["judge_id"] == judge_id]
    cross_tab = pd.crosstab(judge_df[feature], judge_df["outcome"])
    data = [
        go.Bar(name=col, x=cross_tab.index, y=cross_tab[col])
        for col in cross_tab.columns
    ]
    layout = go.Layout(
        title=f"Outcome by {feature_name}",
        barmode="group",
    )
    return go.Figure(data, layout)


def get_feature_vis(feature: str) -> Figure:
    df = get_df()
    cross_tab = pd.crosstab(df[feature], df["outcome"])
    data = [
        go.Bar(name=col, x=cross_tab.index, y=cross_tab[col])
        for col in cross_tab.columns
    ]
    layout = go.Layout(
        title=f"Outcome by {feature.title().replace('_', ' ')}",
        barmode="group",
    )
    return go.Figure(data, layout)
