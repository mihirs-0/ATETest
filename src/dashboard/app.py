import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import dash_bootstrap_components as dbc

from src.analysis.metrics import ATEMetrics
from src.data_generation.wafer_simulator import WaferSimulator

# Initialize the app
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

# Generate sample data
simulator = WaferSimulator()
df = simulator.generate_test_data()
metrics = ATEMetrics(df)

# Layout
app.layout = dbc.Container([
    dbc.Row([
        dbc.Col(html.H1("ATE Test Data Analysis Dashboard", className="text-center my-4"))
    ]),
    
    # Yield Trend
    dbc.Row([
        dbc.Col([
            html.H3("Yield Trend Over Time", className="text-center"),
            dcc.Graph(id='yield-trend')
        ], width=12)
    ]),
    
    # Test Bin Correlation
    dbc.Row([
        dbc.Col([
            html.H3("Test Bin Correlation", className="text-center"),
            dcc.Graph(id='correlation-heatmap')
        ], width=12)
    ]),
    
    # Cost Analysis
    dbc.Row([
        dbc.Col([
            html.H3("Cost Analysis", className="text-center"),
            dcc.Graph(id='cost-breakdown')
        ], width=12)
    ]),
    
    # Alerts
    dbc.Row([
        dbc.Col([
            html.H3("Recent Alerts", className="text-center"),
            html.Div(id='alerts-table')
        ], width=12)
    ]),
    
    # Refresh interval
    dcc.Interval(
        id='interval-component',
        interval=60*1000,  # Update every minute
        n_intervals=0
    )
], fluid=True)

# Callbacks
@app.callback(
    Output('yield-trend', 'figure'),
    Input('interval-component', 'n_intervals')
)
def update_yield_trend(n):
    yield_df = metrics.calculate_yield()
    fig = px.line(
        yield_df,
        x='wafer_id',
        y='yield',
        title='Yield Trend by Wafer',
        labels={'yield': 'Yield (%)', 'wafer_id': 'Wafer ID'}
    )
    fig.update_yaxes(tickformat=".2%")
    return fig

@app.callback(
    Output('correlation-heatmap', 'figure'),
    Input('interval-component', 'n_intervals')
)
def update_correlation_heatmap(n):
    corr_matrix = metrics.analyze_correlations()
    fig = go.Figure(data=go.Heatmap(
        z=corr_matrix.values,
        x=corr_matrix.columns,
        y=corr_matrix.index,
        colorscale='RdBu',
        zmin=-1,
        zmax=1
    ))
    fig.update_layout(title='Test Bin Correlation Matrix')
    return fig

@app.callback(
    Output('cost-breakdown', 'figure'),
    Input('interval-component', 'n_intervals')
)
def update_cost_breakdown(n):
    _, cost_df = metrics.calculate_cost_per_unit()
    fig = px.bar(
        cost_df,
        x='metric',
        y='value',
        title='Cost Breakdown',
        labels={'value': 'Cost ($)', 'metric': 'Metric'}
    )
    return fig

@app.callback(
    Output('alerts-table', 'children'),
    Input('interval-component', 'n_intervals')
)
def update_alerts_table(n):
    alerts = metrics.detect_yield_drops()
    if alerts.empty:
        return html.Div("No recent alerts")
    
    table = dbc.Table.from_dataframe(
        alerts,
        striped=True,
        bordered=True,
        hover=True
    )
    return table

if __name__ == '__main__':
    print("Access the dashboard at: http://localhost:8050")
    app.run(debug=True) 