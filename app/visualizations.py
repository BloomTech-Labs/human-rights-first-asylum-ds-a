
from plotly.graph_objects import Figure
import plotly.graph_objects as go
import plotly.express as px
from app.db_ops import get_judge_df, get_table, get_df
import pandas as pd

# def get_judge_side_bar(judge_name: str) -> go.Figure:
#         """
#         Function grabs data from database by judge and creates a
#         side-by-side bar chart for visualization.
#         Input: judge_name (name of judge to filter by)
#         Output: fig (object with visualization data)
#         """
#         df = get_judge_df(judge_name)
#         df["count"] = 1
#         grouped_df = df.groupby(by=["protected_grounds",
#                                     "outcome"]).agg({
#                                                     "count": ["sum"]
#                                                     }).reset_index()
#         fig = px.bar(grouped_df, x="protected_grounds", y="count",
#                      color="outcome",
#                      color_discrete_map={"granted": '#00D100',
#                                          "denied": "#D10000"},
#                      barmode="group", title="Side-by-Side Bar Chart")
#         return fig

def get_judge_vis(judge_id: int) -> Figure:
    df = get_df()
    judge_df = df[df["judge_id"] == judge_id]
    cross_tab = pd.crosstab(
        judge_df["protected_grounds"],
        judge_df["outcome"],
    )
    data = [
        go.Bar(name=col, x=cross_tab.index, y=cross_tab[col])
        for col in cross_tab.columns
    ]
    layout = go.Layout(
        title="Outcome by Protected Grounds",
        barmode="group",
    )
    return go.Figure(data, layout)