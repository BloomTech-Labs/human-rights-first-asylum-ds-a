import plotly.graph_objects as go
import ployly.express as px

from app.db_ops import get_judge_df

def get_judge_plot(judge_name: str) -> go.figure:
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
        return go.figure(data, layout)