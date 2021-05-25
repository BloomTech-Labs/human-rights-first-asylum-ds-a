import plotly.graph_objects as go


def get_stacked_bar_chart(df, feature):
    """Takes dataframe and feature name (str) and returns a graph figure
    in json format for that feature as the x-axis"""

    outcomes_list = ['Denied', 'Granted', 'Remanded', 'Sustained', 'Terminated']
    df = df.groupby(feature)['case_outcome'].value_counts().unstack(fill_value=0)

    fig_data = []
    for outcome in outcomes_list:
        if outcome in df.columns:
            temp = go.Bar(name= outcome,
                            x=list(df.index),
                            y=df[outcome])
            fig_data.append(temp)

    fig = go.Figure(fig_data)
    fig.update_layout(barmode='stack')

    return fig.to_json()
