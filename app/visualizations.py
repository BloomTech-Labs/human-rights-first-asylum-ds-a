import plotly.graph_objects as go
import plotly.express as px
from app.db_ops import get_judge_df


def get_judge_plot(judge_name: str) -> go.Figure:
        ''' 
        Takes a judge name and returns a plot of decisions
        '''
        df = get_judge_df(judge_name)['outcome'].value_counts()
        labels = df.index
        values = df.values
        data = go.Pie(labels= labels, values= values, hole= 0.5)
        layout = go.Layout(
                title = "Outcome by Judge",
                colorway = px.colors.qualitative.Antique,
                height = 500,
                width = 600
        )
        return go.Figure(data, layout)


def get_judge_bar(judge_name: str) -> go.Figure:
        df = get_judge_df(judge_name)
        df["count"] = 1
        grouped_df = df.groupby(by=["protected_grounds", "outcome"]).agg({"count": ["sum"]}).reset_index()
        fig = px.bar(grouped_df, x="protected_grounds", y="count", color="outcome", title="Stack Bar Chart")
        return fig


def get_judge_side_bar(judge_name: str) -> go.Figure:
        df = get_judge_df(judge_name)
        df["count"] = 1
        grouped_df = df.groupby(by=["protected_grounds", "outcome"]).agg({"count": ["sum"]}).reset_index()
        fig = px.bar(grouped_df, x="protected_grounds", y="count", color="outcome", 
                 color_discrete_map={"granted": '#00D100', "denied": "#D10000"}, 
                 barmode="group")
        return fig
