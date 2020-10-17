#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Run this app with `python app.py` and
# visit http://127.0.0.1:8050/ in your web browser.

# =============================================================================
#                            LOAD MODULES
# =============================================================================
import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import plotly.express as px
import pandas as pd
import numpy as np

# =============================================================================
#                            INITIALIZE
# =============================================================================
data_url = 'https://data.cityofnewyork.us/resource/nwxe-4ae8.json?'
external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

# Get species. Will populate the combobox.
soql_url = (data_url +\
            '$query=select distinct spc_common order by spc_common').replace(' ', '%20')
soql_species = pd.read_json(soql_url)
species = soql_species['spc_common'].dropna()

# =============================================================================
#                          PAGE TEXT
# =============================================================================
markdown_text = '''
### NYC Tree Health
Review the health of New York City trees as recorded by volunteers for
the 2015 Tree Census conducted by NYC Parks & Recreation and partner
organizations.

- Figure 1: Break down the health level by tree species and borough.
- Figure 2: Compare the percentage of health levels between the number of stewards.

*Note*: The visual comparison of the health levels by steward may be sufficient for management decisions. If necessary, a finer distinction about the effectiveness of stewards is possible by conducting a Fisher Exact Test.

Data source: [2015 Street Tree Census - Tree Data](https://data.cityofnewyork.us/Environment/2015-Street-Tree-Census-Tree-Data/uvpi-gqnh/)
'''

# =============================================================================
#                              APP
# =============================================================================
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
server = app.server

app.layout = html.Div([
    dcc.Markdown(children=markdown_text),

    html.H4(children='Filters'),

    html.Div([
        html.Label('Borough'),
        dcc.Dropdown(
            id='borough_combo',
            options=[
                {'label': 'Brooklyn', 'value': 'Brooklyn'},
                {'label': 'Bronx', 'value': 'Bronx'},
                {'label': 'Manhattan', 'value': 'Manhattan'},
                {'label': 'Queens', 'value': 'Queens'},
                {'label': 'Staten Island', 'value': 'Staten Island'}
            ],
            value='Manhattan'
        ),

        html.Label('Species'),
        dcc.Dropdown(
            id='species_combo',
            options=[{'label': i, 'value': i} for i in species],
            value='crab apple'
        )
    ],
    style={'width': '48%', 'display': 'inline-block'}),

    dcc.Graph(
        id='hist1'
    ),

        dcc.Graph(
        id='hist2'
    )

])

# =============================================================================
#                             DATA RETRIEVAL
# =============================================================================
def get_health_counts(borough, species):
    soql_url = (data_url +\
                '$select=health,count(tree_id)' +\
                '&$where=boroname=\'' + borough + '\' ' +\
                'and spc_common=\'' + species + '\'' +\
                '&$group=health').replace(' ', '%20')

    return pd.read_json(soql_url)

def get_steward_pcts(borough, species):
    # Fetch data
    soql_url = (data_url +\
            '$select=steward,health,count(tree_id)' +\
            '&$where=boroname=\'' + borough + '\' ' +\
            'and spc_common=\'' + species + '\'' +\
            '&$group=steward,health').replace(' ', '%20')
    soql_result = pd.read_json(soql_url)

    # Totals by steward.
    steward_tot = soql_result.groupby(['steward']).count_tree_id.sum()

    # Join totals.
    steward_pcts = pd.merge(soql_result, steward_tot, on='steward')
    steward_pcts.rename(
        columns={'count_tree_id_x':'count_tree_id',
                 'count_tree_id_y':'tree_tot'},
        inplace=True)

    # Calculate percentages by steward
    steward_pcts['pct'] = (steward_pcts.count_tree_id / steward_pcts.tree_tot) * 100

    return steward_pcts

# =============================================================================
#                                 PLOTS
# =============================================================================
def plot_fig1(query_result):
    fig = px.bar(query_result, x = 'health', y = 'count_tree_id',
        title='Tree Counts by Health',
        labels={
            'health': 'Health',  'count_tree_id': 'Count'
        },
        category_orders={
            'health': ['Good', 'Fair', 'Poor']
        }
)
    return fig

def plot_fig2(query_result):
    fig = px.bar(query_result, x = 'steward', y = 'pct', color = 'health',
        title='Relative Tree Health by Stewards',
        labels={
            'steward': 'Stewards',
            'health': 'Health',
            'pct': 'Percent'
        },
        category_orders={
            'steward': ['None', '1or2', '3or4', '4orMore'],
            'health': ['Good', 'Fair', 'Poor']
        },
        color_discrete_sequence=['rgb(40,135,161)',
                                 'rgb(237,234,194)',
                                 'rgb(161,105,40)']
    )
    fig.update_layout(barmode='relative')

    return fig
    
# =============================================================================
#                               CALLBACK
# =============================================================================
@app.callback(
    Output(component_id='hist1', component_property='figure'),
    Output(component_id='hist2', component_property='figure'),    
    [Input(component_id='borough_combo', component_property='value'),
     Input(component_id='species_combo', component_property='value')]
)
def update_figure(borough, species):
    query_result = get_health_counts(borough, species)
    fig1 = plot_fig1(query_result)

    query_result = get_steward_pcts(borough, species)
    fig2 = plot_fig2(query_result)

    return fig1 , fig2 #'Debug Output: {}'.format(soql_result)

# =============================================================================
#                               REFERENCES
# =============================================================================
# Showed me the data shape I needed for the percent barplot.
#https://stackoverflow.com/questions/40814840/r-percentage-stack-bar-chart-in-plotly

# Built the summaries
#https://www.statology.org/sum-rows-pandas-dataframe/

# Proof of concept, but I used Plotly Express with a relative barmode instead.
#https://www.weirdgeek.com/2020/04/plotting-100-stacked-column-chart-in-tableau/
#https://www.weirdgeek.com/2020/05/plot-100-percent-stacked-column-chart-using-plotly-in-python/

if __name__ == '__main__':
    app.run_server(debug=True)
