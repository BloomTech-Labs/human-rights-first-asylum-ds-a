import pandas as pd
import numpy as np
from sklearn.preprocessing import LabelEncoder
import plotly.express as px
import dash
import dash_core_components as dcc
import dash_html_components as html

"""
This is the beginning of a Parallel Categories graph application that built with Plotly, deployable with Dash.
The CSV included is example data. Future work should include using endpoints to connect with the backend so that
information can be used dynamically.  The Outcome_enc feature is so the coloring can work. refer to the documentation 
on Plotly.com to further build functionality and for deployment.

To test locally run:
$ python3 par_cat.py
"""

df = pd.read_csv("https://raw.githubusercontent.com/Lambda-School-Labs/human-rights-first-asylum-ds-a/main/visualizations/test_data_v4.csv")

df["Outcome"] = df["Outcome"].fillna("Denied")
df["Outcome"] = df["Outcome"].replace(to_replace="Pending", value="Appealed")

# Creating Appellate results to use in visuals if requested
df["Appellate"] = np.random.randint(1,3, size=len(df))
df.loc[df['Outcome'] == 'Granted', 'Appellate'] = 'N/A'
df.loc[df['Outcome'] == 'Denied', 'Appellate'] = 'N/A'
df.loc[df['Appellate'] == 1, 'Appellate'] = 'Appeal Granted'
df.loc[df['Appellate'] == 2, 'Appellate'] = 'Appeal Denied'

number=LabelEncoder()
df['Outcome_enc'] = number.fit_transform(df['Outcome'])

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

fig = px.parallel_categories(df, dimensions=[ "Outcome", "Protected Ground", "Country"],
                             color="Outcome_enc", 
                             color_continuous_scale=px.colors.sequential.Viridis
                             )

app.layout = html.Div(children=[
    html.H1(children='Hello Dash'),

    html.Div(children='''
        Dash: A web application framework for Python.
    '''),

    dcc.Graph(
        id='example-graph',
        figure=fig
    )
])

if __name__ == '__main__':
    app.run_server(debug=True)