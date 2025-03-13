# -*- coding: utf-8 -*-
"""
Created on Tue Mar 11 10:25:02 2025

@author: jacob
"""

import pandas as pd
import plotly.express as px
import dash
from dash import dcc, html
from dash.dependencies import Input, Output


# Load the data
df = pd.read_csv("C:/Users/jacob/OneDrive/Documents/Data Visualization/4433 project/Project_2/Provisional_COVID-19_Death_Counts_by_Week_Ending_Date_and_State_20250311.csv")

# Clean and preprocess the data
# Convert 'Week Ending Date' to datetime
df['Week Ending Date'] = pd.to_datetime(df['Week Ending Date'])

# Rename columns for clarity (optional)
df.rename(columns={'State': 'state', 'COVID-19 Deaths': 'covid_deaths'}, inplace=True)

# Handle missing values (e.g., replace 'Missing' with NaN)
df['covid_deaths'] = pd.to_numeric(df['covid_deaths'], errors='coerce')

# Filter out United States data if needed
df = df[df['state'] != 'United States']

# Create a 'Year-Week' column for easier aggregation
df['Year-Week'] = df['Week Ending Date'].dt.strftime('%Y-W%U')

# Calculate cumulative deaths
df['cumulative_deaths'] = df.groupby('state')['covid_deaths'].cumsum()

# State abbreviation to name mapping
state_name_to_code = {
    'Alabama': 'AL', 'Alaska': 'AK', 'Arizona': 'AZ', 'Arkansas': 'AR', 'California': 'CA',
    'Colorado': 'CO', 'Connecticut': 'CT', 'Delaware': 'DE', 'District of Columbia': 'DC',
    'Florida': 'FL', 'Georgia': 'GA', 'Hawaii': 'HI', 'Idaho': 'ID', 'Illinois': 'IL',
    'Indiana': 'IN', 'Iowa': 'IA', 'Kansas': 'KS', 'Kentucky': 'KY', 'Louisiana': 'LA',
    'Maine': 'ME', 'Maryland': 'MD', 'Massachusetts': 'MA', 'Michigan': 'MI',
    'Minnesota': 'MN', 'Mississippi': 'MS', 'Missouri': 'MO', 'Montana': 'MT',
    'Nebraska': 'NE', 'Nevada': 'NV', 'New Hampshire': 'NH', 'New Jersey': 'NJ',
    'New Mexico': 'NM', 'New York': 'NY', 'North Carolina': 'NC', 'North Dakota': 'ND',
    'Ohio': 'OH', 'Oklahoma': 'OK', 'Oregon': 'OR', 'Pennsylvania': 'PA',
    'Rhode Island': 'RI', 'South Carolina': 'SC', 'South Dakota': 'SD', 'Tennessee': 'TN',
    'Texas': 'TX', 'Utah': 'UT', 'Vermont': 'VT', 'Virginia': 'VA', 'Washington': 'WA',
    'West Virginia': 'WV', 'Wisconsin': 'WI', 'Wyoming': 'WY'
}

df['state_code'] = df['state'].map(state_name_to_code)

app = dash.Dash(__name__)

app.layout = html.Div([
    html.H1("COVID-19 Deaths by State and Week"),

    # Dropdown for state selection
    dcc.Dropdown(
        id='state-dropdown',
        options=[{'label': state, 'value': state} for state in df['state'].unique()],
        multi=True,
        value=['California', 'Texas']  # Default selected states
    ),
     # Death type dropdown
    dcc.Dropdown(
        id='death-type-dropdown',
        options=[
            {'label': 'Cumulative Deaths', 'value': 'cumulative_deaths'},
            {'label': 'Weekly COVID-19 Deaths', 'value': 'covid_deaths'}
        ],
        value='cumulative_deaths',  # Default to cumulative deaths
        clearable=False
    ),
    # Date range picker
    dcc.DatePickerRange(
        id='date-picker-range',
        min_date_allowed=df['Week Ending Date'].min(),
        max_date_allowed=df['Week Ending Date'].max(),
        start_date=df['Week Ending Date'].min(),
        end_date=df['Week Ending Date'].max()
    ),

    # Time-series chart
    dcc.Graph(id='time-series-chart'),

    # Animated Choropleth map
    dcc.Graph(id='animated-choropleth')
])
@app.callback(
    Output('time-series-chart', 'figure'),
    [Input('state-dropdown', 'value'),
     Input('death-type-dropdown', 'value'),
     Input('date-picker-range', 'start_date'),
     Input('date-picker-range', 'end_date')]
)
def update_time_series(selected_states, death_type, start_date, end_date):
    filtered_df = df[df['state'].isin(selected_states)]
    filtered_df = filtered_df[(filtered_df['Week Ending Date'] >= start_date) & (filtered_df['Week Ending Date'] <= end_date)]

    fig = px.line(filtered_df, x='Week Ending Date', y=death_type, color='state',
                  title='COVID-19 Deaths Over Time')
    return fig
@app.callback(
    Output('animated-choropleth', 'figure'),
    [Input('death-type-dropdown', 'value'),
     Input('date-picker-range', 'start_date'),
     Input('date-picker-range', 'end_date')]
)
def update_animated_choropleth(death_type,start_date, end_date):
    start_date = pd.to_datetime(start_date)
    end_date = pd.to_datetime(end_date)
    filtered_df = df[(df['Week Ending Date'] >= start_date) & (df['Week Ending Date'] <= end_date)]
    
    
    
    fig = px.choropleth(filtered_df,
                        locations='state_code',
                        locationmode='USA-states',
                        color=death_type,
                        scope='usa',
                        color_continuous_scale='Viridis',
                        animation_frame='Week Ending Date',
                        title='COVID-19 Cumulative Deaths Over Time')

    return fig

if __name__ == '__main__':
    app.run_server(debug=True)
