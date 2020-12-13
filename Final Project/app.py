#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Run this app with `python app.py` and
# visit http://127.0.0.1:8050/ in your web browser.

#%% Setup
# =============================================================================
#                            LOAD MODULES
# =============================================================================
from data608_final import *
import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import numpy as np

# =============================================================================
#                            INITIALIZE
# =============================================================================
data_url = 'https://data.cdc.gov/resource/xkkf-xrst.json'
external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

# Fetch combobox data.
locales, weeks = fetch_combos(data_url)

#%% Page
# =============================================================================
#                          PAGE TEXT
# =============================================================================
markdown_text = '''
### Data 608 Final Project
#### Excess All-Cause Deaths in the United States
#### Author: Jai Jeffryes

#### Introduction
The measure of excess deaths from all causes can serve as an indicator for when
a locale has returned to normal in the context of the SARS-CoV-2 pandemic.
This approach follows analysis of Dr. Michael Levitt, Professor of Biophysics
at Stanford University and Nobel Laureate. Dr. Levitt discusses his analyses
on [Twitter](https://twitter.com/search?q=excess%20(from%3AMLevitt_NP2013)&src=typed_query).

#### Objective
Non-pharmacological interventions for controlling epidemic outbreak, including
closings of businesses and schools, limitations of public gatherings, etc.,
take an economic toll and may adversely affect public health in dimensions in
addition to infectious disease. Such adverse public health effects may include
substance abuse, domestic violence, hunger, and more. Understanding when a
locale can ease controls is therefore a question of great interest.

Excess deaths from all causes measure the population burden of mortality. If
the burden of mortality returns to a range consistent with periods prior to
epidemic outbreak, then easing of controls appears justified. Vital statistics
data are very reliable in the United States, so observing all-cause mortality
filters data quality issues associated with attribution of cause of death by
COVID-19. In other words, when deaths return to a normal level it can be
concluded that a population no longer suffers an unusual burden from COVID-19.

The visual representation of excess deaths data supports evaluation of the
degree of normalcy in the context of the pandemic at the level of U.S. state
at a point in time and across a span of time.

#### Data
The source of the data is the National Center of Health Statistics. It is
published by the U.S. Government via the Centers of Disease Control and
Prevention.

Data Source:
[Excess Deaths Associated with COVID-19](https://data.cdc.gov/NCHS/Excess-Deaths-Associated-with-COVID-19/xkkf-xrst/)


The data are accessible through the Socrata Open Data API. Data points of
interest include the following:
    
- Reporting week.
- U.S. State.
- Estimate of percent of excess deaths.

Additional variables which may be useful include:
    
- Crude counts for deaths.
- Thresholds of expected deaths with confidence intervals.
- Crude counts for excess deaths.

#### Figures
- U.S. Excess All-Cause Deaths. A chloropleth grouped by U.S. state, which
maps the color dimension to percent of excess deaths for the purpose of
judging relative burden of mortality at a point in time. The user can select
the reporting period of interest. As the collection of vital statistics varies
in timeliness between the states, the presentation defaults to the third most
recent reporting week instead of the most recent.
- Observed Deaths by Week. Reports the counts for crude deaths and includes a
line plot of the upper threshold of expected deaths. Counts extending above
the threshold represent excess deaths. The user can select the locale of
interest.
- Proportion of Excess Deaths by Week. This figure normalizes the excess
deaths reported in the prior figure, in effect flattening its threshold line.
'''

# =============================================================================
#                              APP
# =============================================================================
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
server = app.server

app.layout = html.Div([
    dcc.Markdown(children=markdown_text),

    #html.H4(children='Filters'),

    html.Div([
        html.Label('Weeks'),
        dcc.Dropdown(
            id='week_combo',
            options=[{'label': i, 'value': i} for i in weeks],
            value=weeks[-3]
        )
        
    ],
    style={'width': '20%', 'display': 'inline-block'}),

    dcc.Graph(
        id='map'
    ) ,


    html.Div([
        html.Label('Locales'),
        dcc.Dropdown(
            id='locale_combo',
            options=[{'label': i, 'value': i} for i in locales],
            value='United States'
        )
        
    ],
    style={'width': '20%', 'display': 'inline-block'}),

    dcc.Graph(
        id='locale'
    ),
    
    dcc.Graph(
        id='percent'
    )
    
])


    
# =============================================================================
#                               CALLBACK
# =============================================================================
@app.callback(
    Output(component_id='map', component_property='figure'),
    Output(component_id='locale', component_property='figure'),
    Output(component_id='percent', component_property='figure'),    
    [Input(component_id='week_combo', component_property='value'),
     Input(component_id='locale_combo', component_property='value')]
)
def update_figure(week, locale):
    map_fig = plot_map(data_url, week)

    locale_data = fetch_locale_data(data_url, locale)
    locale_fig = plot_death_counts(locale_data)
    percent_fig = plot_excess_percent(locale_data)

    return map_fig, locale_fig, percent_fig #'Debug Output: {}'.format(soql_result)

# =============================================================================
#                               REFERENCES
# =============================================================================

if __name__ == '__main__':
    app.run_server(debug=True)
