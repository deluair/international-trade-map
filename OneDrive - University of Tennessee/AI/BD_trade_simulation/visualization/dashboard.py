"""
Interactive dashboard for Bangladesh Trade Dynamics Simulation.
"""
import os
import json
import glob
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import dash
from dash import dcc, html, callback, Input, Output, State
from dash.exceptions import PreventUpdate


def create_dataframe_from_results(results_path):
    """
    Create a pandas DataFrame from simulation results.
    
    Args:
        results_path (str): Path to the JSON results file
        
    Returns:
        pd.DataFrame: DataFrame with simulation results
    """
    # Load the results file
    with open(results_path, 'r') as f:
        results = json.load(f)
    
    # Extract metadata
    scenario = results['metadata']['scenario']
    start_year = results['metadata']['start_year']
    end_year = results['metadata']['end_year']
    
    # Create DataFrame
    yearly_data = []
    
    for year, year_data in results['yearly_data'].items():
        year = int(year)
        
        # Extract key metrics for this year
        row = {
            'Year': year,
            'Scenario': scenario,
            'GDP (billion USD)': year_data['investment'].get('gdp', 0),
            'Total Exports (billion USD)': year_data['export'].get('total_exports', 0),
            'Total Imports (billion USD)': year_data['import'].get('total_imports', 0),
            'Trade Balance (billion USD)': year_data['aggregate_metrics'].get('trade_balance', 0),
            'Trade Openness (%)': year_data['aggregate_metrics'].get('trade_openness', 0) * 100,
            'Exchange Rate (BDT/USD)': year_data['exchange_rate'].get('exchange_rate', 0),
        }
        
        # Add sector-specific exports if available
        if 'sector_data' in year_data['export']:
            for sector, sector_data in year_data['export']['sector_data'].items():
                row[f'{sector} Exports (million USD)'] = sector_data.get('export_volume', 0)
        
        yearly_data.append(row)
    
    # Create DataFrame
    df = pd.DataFrame(yearly_data)
    
    return df


def create_scenario_comparison_dataframe(results_dir):
    """
    Create a DataFrame for comparing multiple scenarios.
    
    Args:
        results_dir (str): Directory containing result files
        
    Returns:
        pd.DataFrame: Combined DataFrame with all scenarios
    """
    # Find all result files
    result_files = glob.glob(os.path.join(results_dir, 'simulation_results_*.json'))
    
    # Load and combine data from all files
    all_data = []
    
    for file_path in result_files:
        df = create_dataframe_from_results(file_path)
        all_data.append(df)
    
    # Combine all DataFrames
    if all_data:
        combined_df = pd.concat(all_data, ignore_index=True)
        return combined_df
    else:
        return pd.DataFrame()


def create_dashboard(results_dir):
    """
    Create and launch an interactive dashboard for simulation results.
    
    Args:
        results_dir (str): Directory containing the simulation results
    """
    # Create dataframe from results
    df = create_scenario_comparison_dataframe(results_dir)
    
    if df.empty:
        print(f"No results found in {results_dir}")
        return
    
    # Get list of available scenarios
    scenarios = df['Scenario'].unique().tolist()
    
    # Get list of available metrics
    metrics = [col for col in df.columns if col not in ['Year', 'Scenario']]
    
    # Create Dash app
    app = dash.Dash(__name__, title="Bangladesh Trade Dynamics Dashboard")
    
    app.layout = html.Div([
        html.H1("Bangladesh Trade Dynamics Simulation (2025-2050)"),
        
        html.Div([
            html.Div([
                html.H3("Scenario Selection"),
                dcc.Checklist(
                    id='scenario-checklist',
                    options=[{'label': s, 'value': s} for s in scenarios],
                    value=[scenarios[0]],
                    inline=True
                ),
            ], style={'width': '48%', 'display': 'inline-block'}),
            
            html.Div([
                html.H3("Metric Selection"),
                dcc.Dropdown(
                    id='metric-dropdown',
                    options=[{'label': m, 'value': m} for m in metrics],
                    value='Total Exports (billion USD)',
                ),
            ], style={'width': '48%', 'display': 'inline-block'}),
        ]),
        
        html.Div([
            html.H3("Simulation Results Over Time"),
            dcc.Graph(id='time-series-graph'),
        ]),
        
        html.Div([
            html.Div([
                html.H3("Trade Balance"),
                dcc.Graph(id='trade-balance-graph'),
            ], style={'width': '48%', 'display': 'inline-block'}),
            
            html.Div([
                html.H3("Export Composition"),
                dcc.Graph(id='export-composition-graph'),
            ], style={'width': '48%', 'display': 'inline-block'}),
        ]),
        
        html.Div([
            html.H3("Scenario Comparison"),
            html.Div([
                html.Label("Select Year:"),
                dcc.Slider(
                    id='year-slider',
                    min=df['Year'].min(),
                    max=df['Year'].max(),
                    value=df['Year'].min() + 10,
                    marks={str(year): str(year) for year in range(df['Year'].min(), df['Year'].max() + 1, 5)},
                    step=1
                ),
            ]),
            dcc.Graph(id='scenario-comparison-graph'),
        ]),
    ])
    
    # Callback for time series graph
    @app.callback(
        Output('time-series-graph', 'figure'),
        [Input('scenario-checklist', 'value'),
         Input('metric-dropdown', 'value')]
    )
    def update_time_series(selected_scenarios, selected_metric):
        filtered_df = df[df['Scenario'].isin(selected_scenarios)]
        
        fig = px.line(
            filtered_df, 
            x='Year', 
            y=selected_metric, 
            color='Scenario',
            title=f"{selected_metric} Over Time",
            labels={selected_metric: selected_metric, 'Year': 'Year'},
            markers=True
        )
        
        fig.update_layout(
            xaxis=dict(tickmode='linear', dtick=5),
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
        )
        
        return fig
    
    # Callback for trade balance graph
    @app.callback(
        Output('trade-balance-graph', 'figure'),
        [Input('scenario-checklist', 'value')]
    )
    def update_trade_balance(selected_scenarios):
        filtered_df = df[df['Scenario'].isin(selected_scenarios)]
        
        fig = px.line(
            filtered_df, 
            x='Year', 
            y='Trade Balance (billion USD)', 
            color='Scenario',
            title="Trade Balance Over Time",
            labels={'Trade Balance (billion USD)': 'Trade Balance (billion USD)', 'Year': 'Year'},
            markers=True
        )
        
        # Add a horizontal line at y=0
        fig.add_shape(
            type="line",
            x0=filtered_df['Year'].min(),
            y0=0,
            x1=filtered_df['Year'].max(),
            y1=0,
            line=dict(color="black", width=1, dash="dash"),
        )
        
        fig.update_layout(
            xaxis=dict(tickmode='linear', dtick=5),
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
        )
        
        return fig
    
    # Callback for export composition graph
    @app.callback(
        Output('export-composition-graph', 'figure'),
        [Input('scenario-checklist', 'value'),
         Input('year-slider', 'value')]
    )
    def update_export_composition(selected_scenarios, selected_year):
        if len(selected_scenarios) != 1:
            # Only show composition for a single scenario
            selected_scenario = selected_scenarios[0]
        else:
            selected_scenario = selected_scenarios[0]
        
        # Filter for the selected scenario and year
        filtered_df = df[(df['Scenario'] == selected_scenario) & (df['Year'] == selected_year)]
        
        if filtered_df.empty:
            return go.Figure()
        
        # Get export sectors
        export_columns = [col for col in df.columns if 'Exports (million USD)' in col]
        
        if not export_columns:
            return go.Figure()
        
        # Prepare data for pie chart
        labels = [col.split(' Exports')[0] for col in export_columns]
        values = [filtered_df[col].iloc[0] for col in export_columns]
        
        # Create pie chart
        fig = px.pie(
            names=labels,
            values=values,
            title=f"Export Composition in {selected_year} - {selected_scenario} Scenario"
        )
        
        return fig
    
    # Callback for scenario comparison graph
    @app.callback(
        Output('scenario-comparison-graph', 'figure'),
        [Input('metric-dropdown', 'value'),
         Input('year-slider', 'value')]
    )
    def update_scenario_comparison(selected_metric, selected_year):
        # Filter for the selected year
        filtered_df = df[df['Year'] == selected_year]
        
        if filtered_df.empty:
            return go.Figure()
        
        # Group by scenario
        scenario_data = filtered_df.groupby('Scenario')[selected_metric].mean().reset_index()
        
        # Create bar chart
        fig = px.bar(
            scenario_data,
            x='Scenario',
            y=selected_metric,
            color='Scenario',
            title=f"{selected_metric} by Scenario in {selected_year}"
        )
        
        return fig
    
    # Run the app
    app.run_server(debug=True, use_reloader=False)


if __name__ == "__main__":
    # Example usage
    create_dashboard("../results") 