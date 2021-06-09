import plotly.graph_objects as go


def get_stacked_bar_chart(df, feature):
    """Takes dataframe and feature name (str) and returns a graph figure
    in json format for that feature as the x-axis"""

    outcomes_list = ['Denied', 'Granted', 'Remanded', 'Sustained', 'Terminated']
    df = df.groupby(feature)['case_outcome'].value_counts().unstack(fill_value=0)

    fig_data = []
    for outcome in outcomes_list:
        if outcome in df.columns:
            # attempt to change y-axis from floats to ints
            # set y axis start at 0, step by 10
            # Look for NaNs and replace with zeroes. 

            temp = go.Bar(name= outcome,
                            x=list(df.index),
                            y=df[outcome], y0=0, dy=10)
            fig_data.append(temp)

    fig = go.Figure(fig_data, layout=go.Layout(barmode='stack', yaxis={'tickformat': ',d'}))

    return fig.to_json()
