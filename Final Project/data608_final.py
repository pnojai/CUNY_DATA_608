#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Nov 29 11:39:28 2020

@author: jai
"""

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import os
import subprocess
from datetime import datetime

#%% Reference data
# =============================================================================
#                              LOOKUPS
# =============================================================================

# United States of America Python Dictionary to translate States,
# Districts & Territories to Two-Letter codes and vice versa.
#
# https://gist.github.com/rogerallen/1583593
#
# Dedicated to the public domain.  To the extent possible under law,
# Roger Allen has waived all copyright and related or neighboring
# rights to this code.
us_state_abbrev = {
    'Alabama': 'AL',
    'Alaska': 'AK',
    'American Samoa': 'AS',
    'Arizona': 'AZ',
    'Arkansas': 'AR',
    'California': 'CA',
    'Colorado': 'CO',
    'Connecticut': 'CT',
    'Delaware': 'DE',
    'District of Columbia': 'DC',
    'Florida': 'FL',
    'Georgia': 'GA',
    'Guam': 'GU',
    'Hawaii': 'HI',
    'Idaho': 'ID',
    'Illinois': 'IL',
    'Indiana': 'IN',
    'Iowa': 'IA',
    'Kansas': 'KS',
    'Kentucky': 'KY',
    'Louisiana': 'LA',
    'Maine': 'ME',
    'Maryland': 'MD',
    'Massachusetts': 'MA',
    'Michigan': 'MI',
    'Minnesota': 'MN',
    'Mississippi': 'MS',
    'Missouri': 'MO',
    'Montana': 'MT',
    'Nebraska': 'NE',
    'Nevada': 'NV',
    'New Hampshire': 'NH',
    'New Jersey': 'NJ',
    'New Mexico': 'NM',
    'New York': 'NY',
    'New York City': 'NY',
    'North Carolina': 'NC',
    'North Dakota': 'ND',
    'Northern Mariana Islands':'MP',
    'Ohio': 'OH',
    'Oklahoma': 'OK',
    'Oregon': 'OR',
    'Pennsylvania': 'PA',
    'Puerto Rico': 'PR',
    'Rhode Island': 'RI',
    'South Carolina': 'SC',
    'South Dakota': 'SD',
    'Tennessee': 'TN',
    'Texas': 'TX',
    'Utah': 'UT',
    'United States': 'US',
    'Vermont': 'VT',
    'Virgin Islands': 'VI',
    'Virginia': 'VA',
    'Washington': 'WA',
    'West Virginia': 'WV',
    'Wisconsin': 'WI',
    'Wyoming': 'WY'
}

# thank you to @kinghelix and @trevormarburger for this idea
# Invalid, since adding a 2nd key to NY.
# abbrev_us_state = dict(map(reversed, us_state_abbrev.items()))

#%% Socrata functions
# =============================================================================
#                          SOCRATA FUNCTIONS
# =============================================================================
def build_soql_url(data_url, query):
    soql_url = (data_url + '?' + query)
    soql_url = soql_url.replace(' ', '%20')
    return soql_url

def fetch_soql_data(data_url, query):
    soql_url = build_soql_url(data_url, query)
    soql_out = pd.read_json(soql_url)
    return soql_out

def transform_soql_data(soql_data):
    soql_data['state'] = soql_data['state'].map(us_state_abbrev)
    return soql_data

def fetch_locales(data_url):
    query = '$select=distinct state'
    locales = fetch_soql_data(data_url, query)
    locales = locales.sort_values(by='state')
    
    return list(locales['state'])

def fetch_weeks(data_url):
    query = '$select=distinct week_ending_date'
    weeks = fetch_soql_data(data_url, query)
    weeks = weeks.sort_values(by='week_ending_date')
    
    return list(weeks['week_ending_date'])

def fetch_combos(data_url):
    locales = fetch_locales(data_url)
    weeks = fetch_weeks(data_url)
    
    return locales, weeks

def fetch_map_data(data_url, wk):
    query = '$select=state,percent_excess_higher_estimate' +\
        '&$where=week_ending_date=\'' + wk +'\''+\
        'and outcome=\'All causes\'' +\
        'and type=\'Predicted (weighted)\''
    soql_out = fetch_soql_data(data_url, query)
    soql_out = transform_soql_data(soql_out)

    return soql_out

def fetch_locale_data(data_url, locale):
    query = '&$where=state=\'' + locale + '\'' +\
        'and week_ending_date > \'2018-12-29\'' +\
        'and outcome=\'All causes\'' +\
        'and type=\'Predicted (weighted)\''

    soql_out = fetch_soql_data(data_url, query)    
    
    return soql_out

#%% Plotly functions
def plot_map(data_url, wk):
    soql_out = fetch_map_data(data_url, wk)
    
    fig = px.choropleth(soql_out,  # Input Pandas DataFrame
                    locations="state",  # DataFrame column with locations
                    color="percent_excess_higher_estimate",  # DataFrame column with color values
                    #color_continuous_scale=px.colors.diverging.RdYlGn[::-1],
                    #color_continuous_scale=px.colors.sequential.Hot[::-1],
                    color_continuous_scale=px.colors.sequential.amp,
                    hover_name="state", # DataFrame column hover info
                    locationmode = 'USA-states', # Set to plot as US States
                    labels ={
                        "percent_excess_higher_estimate": "Proportion of excess deaths"
                        }) 
    fig.update_layout(
        title_text = 'U.S. Excess All-Cause Deaths by State',
        geo_scope='usa',  # Plot only the USA instead of globe
    )
    
    return fig

def plot_death_counts(soql_data):
    fig = go.Figure()
    fig.add_trace(go.Bar(x=soql_data['week_ending_date'],
                         y=soql_data['observed_number'],
                         name='Observed deaths'))
            # labels=dict(week_ending_date='Week',
            #         observed_number='Deaths')
    fig.add_trace(go.Scatter(x=soql_data['week_ending_date'],
                             y=soql_data['upper_bound_threshold'],
                             mode='lines',
                             name='Threshold of expected deaths'))
    fig.update_layout(
        title_text = 'Observed Deaths by Week',
    )

    return fig

def plot_excess_percent(soql_data):
    fig = px.bar(soql_data, x='week_ending_date', y='percent_excess_higher_estimate',
                 labels=dict(week_ending_date='Week', percent_excess_higher_estimate='Estimated proportion of excess')
                 )
    fig.update_layout(
        title_text = 'Proportion of Excess Deaths by Week'
    )
    
    return fig

#%% Deployment
def deploy_heroku():
# =============================================================================
#                            INITIALIZATIONS
# =============================================================================
    import heroku_config as cfg                       # Read config file
        
    source_dir = os.getcwd()                          # Set directories
    deploy_dir = os.path.join(os.path.expanduser(cfg.deploy_path), cfg.deploy_dir)
    temp_dir = os.path.join(source_dir, 'temp')
    if not os.path.exists(temp_dir):
        os.mkdir(temp_dir)
    
# =============================================================================
#                          BUILD SHELL SCRIPT
# =============================================================================
    # Create a shell script.
    lines = []
    
    lines.append('#!/bin/bash')                       # Shebang
    
    if not os.path.exists(deploy_dir):                # Make deploy directory
        lines.append('mkdir ' + deploy_dir)
        
    lines.append('cd ' + deploy_dir)                  # Go there
    
    git_dir = os.path.join(deploy_dir, '.git')        # Initialize git
    if not os.path.exists(git_dir):                   
        lines.append('git init')
        
                                                      # Create virtual env
    lines.append('conda create -n ' + cfg.virtual_env + ' python=' + \
                 cfg.python_version + ' -y')          
    
                                                      # Init shell for conda
    conda_path = os.path.expanduser('~/anaconda3/etc/profile.d/conda.sh')
    lines.append('source ' + conda_path)              
    lines.append('conda activate ' + cfg.virtual_env) # Activate env
    
    # Fun list tricks.
    #   List comprehension to cat all elements.
    #   extend() to add them singly to list of lines list.
                                                      # Install dependencies
    lines.extend(['pip install ' + dep for dep in cfg.dependencies])

                                                      # Deploy Python files 
    deploy_files = [fn for fn in os.listdir(source_dir) if fn.endswith('py')]
    deploy_files.remove('heroku_config.py')
    for fn in cfg.exclude:
        deploy_files.remove(fn)
    for fn in deploy_files:                           
        fn_src = os.path.join(source_dir, fn)
        lines.append('cp "' + fn_src + '" .')
    
                                                      # Create .gitignore
    gitignore_f = os.path.join(temp_dir, '.gitignore')    
    with open(gitignore_f, 'w') as f:                
        f.writelines(['%s\n' % pat for pat in cfg.gitignore])
    lines.append('cp "' + gitignore_f + '" "' + deploy_dir + '"')
    
    Procfile_f = os.path.join(temp_dir, 'Procfile')   # Create Procfile
    with open(Procfile_f, 'w') as f:                    
        f.writelines('web: gunicorn app:server')
    lines.append('cp "' + Procfile_f + '" "' + deploy_dir + '"')
    
    lines.append('pip freeze > requirements.txt')     # Create requirements
    
    lines.append('heroku create ' + cfg.app_name)     # Create Heroku app
    
    lines.append('git add .')                         # Add to Git repo
    msg = 'Heroku deployment: ' + datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    lines.append('git commit -m \'' + msg + '\'')
                                                      
    lines.append('git push heroku master')            # Deploy to Heroku
    lines.append('heroku ps:scale web=1')
    
    lines.append('conda deactivate')                  # Deactivate virtual env
    
    with open('deploy_heroku.sh', 'w') as f:          # Generate shell script
        f.writelines('%s\n' % ln for ln in lines)
        
# =============================================================================
#                           RUN DEPLOYMENT
# =============================================================================    
    subprocess.call(['./deploy_heroku.sh'])           # Execute shell script

# =============================================================================
#                               REFERENCES
# =============================================================================
# Config files:
#   https://martin-thoma.com/configuration-files-in-python/
# Platform independent paths:
#   https://stackoverflow.com/questions/10918682/platform-independent-path-concatenation-using
# Calls to command line:
#   https://stackoverflow.com/questions/11113896/use-git-commands-within-python-code
# Conda subshell:
#   https://erictleung.com/conda-in-subshell-script
# Simple directory listing filter with list comprehension:
#   https://stackoverflow.com/questions/2225564/get-a-filtered-list-of-files-in-a-directory

    return        

# Simple test examples
if __name__ == '__main__':
    print("Wisconin --> WI?", us_state_abbrev['Wisconsin'] == 'WI')
#    print("WI --> Wisconin?", abbrev_us_state['WI'] == 'Wisconsin')
    print("Number of entries (50 states, DC, 5 Territories) == 56? ", 56 == len(us_state_abbrev))
