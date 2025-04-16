#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Generate HTML Report for Bangladesh Trade Dynamics Simulation

This script generates an HTML report based on the simulation results.
It works with existing data or sample data if no results are available.
"""

import os
import sys
import json
import glob
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import plotly.express as px
from datetime import datetime

# Add the project root to the Python path to fix import issues
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Try to import visualization tools, but provide alternatives if they fail
try:
    from visualization.plot_utils import create_dataframe_from_results
except ImportError:
    # Define a simplified version of the function if import fails
    def create_dataframe_from_results(results):
        """Create a DataFrame from simulation results"""
        yearly_data = []
        
        for year, year_data in results['yearly_data'].items():
            year = int(year)
            
            row = {
                'Year': year,
                'Scenario': results['metadata']['scenario'],
                'Total Exports (billion USD)': year_data.get('export', {}).get('total_exports', 0),
                'Total Imports (billion USD)': year_data.get('import', {}).get('total_imports', 0),
                'Trade Balance (billion USD)': year_data.get('aggregate_metrics', {}).get('trade_balance', 0),
                'Trade Openness (%)': year_data.get('aggregate_metrics', {}).get('trade_openness', 0) * 100,
            }
            
            # Add sector-specific exports if available
            if 'sector_data' in year_data.get('export', {}):
                for sector, sector_data in year_data['export']['sector_data'].items():
                    row[f'{sector} Exports (million USD)'] = sector_data.get('export_volume', 0)
            
            yearly_data.append(row)
        
        return pd.DataFrame(yearly_data)


def generate_sample_data():
    """Generate sample data if no real simulation results are available"""
    start_year = 2025
    end_year = 2050
    
    # Create sample metadata
    sample_data = {
        'metadata': {
            'scenario': 'sample',
            'start_year': start_year,
            'end_year': end_year,
            'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        },
        'yearly_data': {}
    }
    
    # Define base values
    base_exports = 40
    base_imports = 60
    base_gdp = 350
    export_growth = 0.08
    import_growth = 0.07
    gdp_growth = 0.06
    
    # Create sector data
    sectors = {
        'rmg': {'name': 'Ready-Made Garments', 'volume': 35000, 'growth': 0.08},
        'pharma': {'name': 'Pharmaceuticals', 'volume': 1500, 'growth': 0.12},
        'it_services': {'name': 'IT Services', 'volume': 1200, 'growth': 0.15},
        'leather': {'name': 'Leather and Footwear', 'volume': 1000, 'growth': 0.10},
        'jute': {'name': 'Jute and Jute Products', 'volume': 800, 'growth': 0.05},
        'agro_products': {'name': 'Agricultural Products', 'volume': 700, 'growth': 0.06}
    }
    
    # Generate yearly data
    for year in range(start_year, end_year + 1):
        year_idx = year - start_year
        
        # Calculate values with some random variation
        exports = base_exports * (1 + export_growth) ** year_idx * (1 + np.random.normal(0, 0.02))
        imports = base_imports * (1 + import_growth) ** year_idx * (1 + np.random.normal(0, 0.02))
        gdp = base_gdp * (1 + gdp_growth) ** year_idx * (1 + np.random.normal(0, 0.01))
        
        # Calculate trade balance and openness
        trade_balance = exports - imports
        trade_openness = (exports + imports) / gdp
        
        # Calculate sector values
        sector_data = {}
        for sector_key, sector_info in sectors.items():
            volume = sector_info['volume'] * (1 + sector_info['growth']) ** year_idx * (1 + np.random.normal(0, 0.03))
            sector_data[sector_key] = {
                'export_volume': volume,
                'growth_rate': sector_info['growth'] * (1 + np.random.normal(0, 0.1)),
                'competitiveness': 0.6 + 0.2 * (year - start_year) / (end_year - start_year)
            }
        
        # Store yearly data
        sample_data['yearly_data'][str(year)] = {
            'export': {
                'total_exports': exports,
                'sector_data': sector_data
            },
            'import': {
                'total_imports': imports
            },
            'investment': {
                'gdp': gdp
            },
            'aggregate_metrics': {
                'trade_balance': trade_balance,
                'trade_openness': trade_openness,
                'export_to_gdp': exports / gdp,
                'import_to_gdp': imports / gdp
            }
        }
    
    return sample_data


def find_result_files():
    """Find all simulation result files in the results directory"""
    result_dir = 'results'
    if not os.path.exists(result_dir):
        os.makedirs(result_dir, exist_ok=True)
        return []
    
    return glob.glob(os.path.join(result_dir, 'simulation_results_*.json'))


def load_results(file_path=None):
    """Load simulation results from a file or use real data from CSV"""
    # First try to load real data from CSV
    real_data_path = "data/bd_trade_data.csv"
    if os.path.exists(real_data_path):
        try:
            print(f"Loading real data from {real_data_path}")
            # Import the function from bd_trade_report.py to load and process real data
            from bd_trade_report import load_trade_data, prepare_data_for_report, get_top_products_and_partners
            
            # Load and process the real data
            trade_data = load_trade_data(real_data_path)
            yearly_data = prepare_data_for_report(trade_data)
            
            if not yearly_data.empty:
                print("Successfully loaded real trade data")
                # Convert to the format expected by the rest of the code
                start_year = yearly_data['year'].min()
                end_year = yearly_data['year'].max()
                
                # Create a results dictionary in the format expected by create_dataframe_from_results
                results = {
                    'metadata': {
                        'scenario': 'real_data',
                        'start_year': int(start_year),
                        'end_year': int(end_year),
                        'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    },
                    'yearly_data': {}
                }
                
                # Approximate values for GDP and exchange rate to avoid errors
                base_gdp = 350  # Billion USD (approximate for Bangladesh)
                base_exchange_rate = 110  # BDT per USD (approximate for recent years)
                gdp_growth = 0.06  # 6% annual growth rate
                
                # Convert yearly_data DataFrame to the expected dictionary format
                for _, row in yearly_data.iterrows():
                    year = int(row['year'])
                    year_idx = year - start_year
                    
                    # Calculate approximate GDP and exchange rate for this year
                    gdp = base_gdp * (1 + gdp_growth) ** year_idx
                    exchange_rate = base_exchange_rate + (year_idx * 2)  # Simple linear increase
                    
                    # Create the yearly data entry with all required fields
                    results['yearly_data'][str(year)] = {
                        'export': {
                            'total_exports': float(row['export_value'] / 1e6),  # Convert from thousands to billions
                            'sector_data': {
                                # Add dummy sector data 
                                'rmg': {'export_volume': float(row['export_value'] * 0.8 / 1e6)},  # 80% RMG, convert to millions
                                'other': {'export_volume': float(row['export_value'] * 0.2 / 1e6)}   # 20% Other
                            }
                        },
                        'import': {
                            'total_imports': float(row['import_value'] / 1e6)  # Convert from thousands to billions
                        },
                        'investment': {
                            'gdp': gdp  # Add GDP data
                        },
                        'exchange_rate': {
                            'exchange_rate': exchange_rate  # Add exchange rate data
                        },
                        'aggregate_metrics': {
                            'trade_balance': float(row['trade_balance'] / 1e6),  # Convert from thousands to billions
                            'trade_openness': float((row['export_value'] + row['import_value']) / (gdp * 1e9)),
                            'export_to_gdp': float(row['export_value'] / (gdp * 1e9)),
                            'import_to_gdp': float(row['import_value'] / (gdp * 1e9))
                        }
                    }
                
                return results
            else:
                print("Failed to process real data, trying simulation results...")
        except Exception as e:
            print(f"Error processing real data: {e}")
            print("Falling back to simulation results or sample data...")
    
    # If real data loading failed, try simulation results
    if file_path and os.path.exists(file_path):
        try:
            with open(file_path, 'r') as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading results file: {e}")
            print("Falling back to sample data...")
            return generate_sample_data()
    else:
        print("No simulation results file found, using sample data...")
        return generate_sample_data()


def generate_plotly_figures(df, scenario):
    """Generate Plotly figures for the HTML report"""
    import plotly.graph_objects as go
    from plotly.subplots import make_subplots
    
    figures = []
    
    # 1. Trade Overview (Exports, Imports, Balance)
    fig1 = go.Figure()
    fig1.add_trace(go.Scatter(x=df['Year'], y=df['Total Exports (billion USD)'], mode='lines+markers', name='Exports', line=dict(color='#1f77b4')))
    fig1.add_trace(go.Scatter(x=df['Year'], y=df['Total Imports (billion USD)'], mode='lines+markers', name='Imports', line=dict(color='#ff7f0e')))
    fig1.add_trace(go.Scatter(x=df['Year'], y=df['Trade Balance (billion USD)'], mode='lines+markers', name='Trade Balance', line=dict(color='#2ca02c')))
    fig1.add_shape(type="line", x0=df['Year'].min(), x1=df['Year'].max(), y0=0, y1=0, line=dict(color="black", width=1, dash="dash"))
    
    fig1.update_layout(
        title=f'Bangladesh Trade Overview ({df["Year"].min()}-{df["Year"].max()}) - {scenario} Scenario',
        xaxis_title='Year',
        yaxis_title='Billion USD',
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        template='plotly_white'
    )
    figures.append(fig1)
    
    # 2. Export Composition (if available)
    export_columns = [col for col in df.columns if 'Exports (million USD)' in col]
    if export_columns:
        # Create data for stacked area chart
        end_year = df['Year'].max()
        final_year_data = df[df['Year'] == end_year][export_columns].iloc[0]
        labels = [col.split(' Exports')[0] for col in export_columns]
        values = [final_year_data[col] for col in export_columns]
        
        # Create pie chart for export composition in the final year
        fig2 = go.Figure(data=[go.Pie(
            labels=labels,
            values=values,
            hole=0.3,
            textinfo='label+percent',
            insidetextorientation='radial',
            marker=dict(
                colors=px.colors.qualitative.Plotly
            )
        )])
        
        fig2.update_layout(
            title=f'Export Composition in {end_year} - {scenario} Scenario',
            template='plotly_white'
        )
        figures.append(fig2)
    
    # 3. Trade Indicators (Trade Openness)
    if 'Trade Openness (%)' in df.columns:
        fig3 = go.Figure()
        fig3.add_trace(go.Scatter(x=df['Year'], y=df['Trade Openness (%)'], mode='lines+markers', name='Trade Openness', line=dict(color='#1f77b4')))
        
        fig3.update_layout(
            title=f'Bangladesh Trade Openness ({df["Year"].min()}-{df["Year"].max()}) - {scenario} Scenario',
            xaxis_title='Year',
            yaxis_title='Percentage (%)',
            template='plotly_white'
        )
        figures.append(fig3)
    
    # 4. Export Trends by Sector (if available)
    if len(export_columns) > 0:
        fig4 = go.Figure()
        
        for col in export_columns:
            sector_name = col.split(' Exports')[0]
            fig4.add_trace(go.Scatter(x=df['Year'], y=df[col] / 1000, mode='lines+markers', name=sector_name))
        
        fig4.update_layout(
            title=f'Export Sector Trends ({df["Year"].min()}-{df["Year"].max()}) - {scenario} Scenario',
            xaxis_title='Year',
            yaxis_title='Billion USD',
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
            template='plotly_white'
        )
        figures.append(fig4)
    
    # 5. Key metrics dashboard
    fig5 = make_subplots(
        rows=2, cols=2,
        subplot_titles=(
            'Trade Balance (billion USD)', 
            'Trade Openness (%)',
            'Export Growth', 
            'Export to Import Ratio'
        )
    )
    
    # Trade Balance
    fig5.add_trace(
        go.Scatter(x=df['Year'], y=df['Trade Balance (billion USD)'], mode='lines+markers', name='Trade Balance'),
        row=1, col=1
    )
    
    # Trade Openness
    if 'Trade Openness (%)' in df.columns:
        fig5.add_trace(
            go.Scatter(x=df['Year'], y=df['Trade Openness (%)'], mode='lines+markers', name='Trade Openness'),
            row=1, col=2
        )
    
    # Export Growth
    start_year = df['Year'].min()
    df['Relative Export Growth'] = df['Total Exports (billion USD)'] / df[df['Year'] == start_year]['Total Exports (billion USD)'].values[0]
    fig5.add_trace(
        go.Scatter(x=df['Year'], y=df['Relative Export Growth'], mode='lines+markers', name='Export Growth Index'),
        row=2, col=1
    )
    
    # Export to Import Ratio
    df['Export to Import Ratio'] = df['Total Exports (billion USD)'] / df['Total Imports (billion USD)']
    fig5.add_trace(
        go.Scatter(x=df['Year'], y=df['Export to Import Ratio'], mode='lines+markers', name='Export/Import Ratio'),
        row=2, col=2
    )
    
    fig5.update_layout(
        title=f'Key Trade Metrics ({df["Year"].min()}-{df["Year"].max()}) - {scenario} Scenario',
        height=800,
        template='plotly_white'
    )
    figures.append(fig5)
    
    return figures


def create_html_report(results_file=None):
    """Create an HTML report from simulation results"""
    # Import plotly here to avoid dependency issues at module level
    import plotly.express as px
    import plotly.graph_objects as go
    import plotly.io as pio
    from plotly.subplots import make_subplots
    
    # Load results or generate sample data
    results = load_results(results_file)
    scenario = results['metadata']['scenario']
    start_year = results['metadata']['start_year']
    end_year = results['metadata']['end_year']
    
    # Convert results to DataFrame
    df = create_dataframe_from_results(results)
    
    # Generate plotly figures
    figures = generate_plotly_figures(df, scenario)
    
    # Initialize dictionaries for summaries
    kpis = {}
    growth_rates = {}
    forecast = {}
    
    # Calculate KPIs and growth rates if DataFrame is not empty
    if not df.empty:
        # Select the first and last available year
        start_year_actual = df['Year'].min()
        end_year_actual = df['Year'].max()
        start_row = df[df['Year'] == start_year_actual].iloc[0]
        end_row = df[df['Year'] == end_year_actual].iloc[0]
        
        # Calculate key performance indicators (KPIs)
        kpis = {
            'Scenario': scenario,
            'Start Year': start_year_actual,
            'End Year': end_year_actual,
            'Total Exports (billion USD)': end_row['Total Exports (billion USD)'],
            'Total Imports (billion USD)': end_row['Total Imports (billion USD)'],
            'Trade Balance (billion USD)': end_row['Trade Balance (billion USD)'],
            'Trade Openness (%)': end_row['Trade Openness (%)'],
        }
        
        # Calculate growth rates if we have multiple years
        if start_year_actual != end_year_actual:
            export_growth = ((end_row['Total Exports (billion USD)'] / start_row['Total Exports (billion USD)']) ** (1 / (end_year_actual - start_year_actual)) - 1) * 100
            import_growth = ((end_row['Total Imports (billion USD)'] / start_row['Total Imports (billion USD)']) ** (1 / (end_year_actual - start_year_actual)) - 1) * 100
        else:
            # If we only have one year of data, we can't calculate growth rate
            export_growth = 0
            import_growth = 0
        
        # Add growth rates to kpis
        kpis['Annual Export Growth'] = export_growth
        kpis['Annual Import Growth'] = import_growth
    
    # Create HTML content
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Bangladesh Trade Dynamics Simulation Report - {scenario} Scenario</title>
        <script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
        <style>
            body {{
                font-family: Arial, sans-serif;
                max-width: 1200px;
                margin: 0 auto;
                padding: 20px;
                color: #333;
            }}
            h1, h2, h3 {{
                color: #2c3e50;
            }}
            .header {{
                text-align: center;
                margin-bottom: 30px;
                padding-bottom: 20px;
                border-bottom: 1px solid #eee;
            }}
            .figure-container {{
                margin-bottom: 40px;
            }}
            .metrics-container {{
                display: flex;
                flex-wrap: wrap;
                justify-content: space-between;
                margin-bottom: 30px;
            }}
            .metric-box {{
                width: 23%;
                background-color: #f8f9fa;
                border-radius: 5px;
                padding: 15px;
                margin-bottom: 15px;
                box-shadow: 0 2px 5px rgba(0,0,0,0.1);
            }}
            .metric-value {{
                font-size: 24px;
                font-weight: bold;
                margin: 10px 0;
                color: #3498db;
            }}
            .metric-title {{
                font-size: 14px;
                color: #7f8c8d;
            }}
            .footer {{
                text-align: center;
                margin-top: 50px;
                padding-top: 20px;
                border-top: 1px solid #eee;
                color: #7f8c8d;
                font-size: 14px;
            }}
        </style>
    </head>
    <body>
        <div class="header">
            <h1>Bangladesh Trade Dynamics Report - {scenario.capitalize()} Scenario</h1>
            <p>Report generated on: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}</p>
            <p>Simulation period: {start_year} - {end_year}</p>
        </div>
    """
    
    # Add key metrics
    if not df.empty:
        initial_year_data = df[df['Year'] == start_year_actual].iloc[0]
        final_year_data = df[df['Year'] == end_year_actual].iloc[0]
        
        # Calculate growth rates if we have multiple years
        if start_year_actual != end_year_actual:
            export_growth = ((final_year_data['Total Exports (billion USD)'] / initial_year_data['Total Exports (billion USD)']) ** (1 / (end_year_actual - start_year_actual)) - 1) * 100
            import_growth = ((final_year_data['Total Imports (billion USD)'] / initial_year_data['Total Imports (billion USD)']) ** (1 / (end_year_actual - start_year_actual)) - 1) * 100
        else:
            # If we only have one year of data, we can't calculate growth rate
            export_growth = 0
            import_growth = 0
        
        html_content += """
        <h2>Key Trade Metrics</h2>
        <div class="metrics-container">
        """
        
        # Add metric boxes
        metrics = [
            {"title": f"{end_year_actual} Exports", "value": f"${final_year_data['Total Exports (billion USD)']:.2f}B"},
            {"title": f"{end_year_actual} Imports", "value": f"${final_year_data['Total Imports (billion USD)']:.2f}B"},
            {"title": f"{end_year_actual} Trade Balance", "value": f"${final_year_data['Trade Balance (billion USD)']:.2f}B"},
        ]
        
        # Only add growth metrics if we have multiple years
        if start_year_actual != end_year_actual:
            metrics.append({"title": "Annual Export Growth", "value": f"{export_growth:.1f}%"})
            metrics.append({"title": "Annual Import Growth", "value": f"{import_growth:.1f}%"})
        
        # Add trade openness if available
        if 'Trade Openness (%)' in df.columns:
            metrics.append({"title": "Trade Openness", "value": f"{final_year_data['Trade Openness (%)']:.1f}%"})
        
        for metric in metrics:
            html_content += f"""
            <div class="metric-box">
                <div class="metric-title">{metric['title']}</div>
                <div class="metric-value">{metric['value']}</div>
            </div>
            """
        
        html_content += """
        </div>
        """
    
    html_content += """
        <h2>Trade Overview</h2>
    """
    
    # Add figures
    for i, fig in enumerate(figures):
        # Convert the figure to HTML
        fig_html = pio.to_html(fig, full_html=False, include_plotlyjs=False)
        html_content += f"""
        <div class="figure-container">
            {fig_html}
        </div>
        """
    
    # Add export sector data table if available
    export_columns = [col for col in df.columns if 'Exports (million USD)' in col]
    if export_columns:
        html_content += """
        <h2>Export Sector Performance</h2>
        <table>
            <tr>
                <th>Sector</th>
                <th>Initial Value (Million USD)</th>
                <th>Final Value (Million USD)</th>
                <th>Growth</th>
                <th>Share in Final Year</th>
            </tr>
        """
        
        # Calculate total exports in final year
        total_exports_final = final_year_data['Total Exports (billion USD)'] * 1000
        
        for col in export_columns:
            sector_name = col.split(' Exports')[0]
            initial_value = initial_year_data[col]
            final_value = final_year_data[col]
            if start_year_actual != end_year_actual:
                annual_growth = ((final_value / initial_value) ** (1 / (end_year_actual - start_year_actual)) - 1) * 100
            else:
                annual_growth = 0  # No growth rate calculation possible for single year
            growth_rates[sector_name] = annual_growth
            share = (final_value / total_exports_final) * 100
            
            html_content += f"""
            <tr>
                <td>{sector_name}</td>
                <td>{initial_value:.1f}</td>
                <td>{final_value:.1f}</td>
                <td>{annual_growth:.1f}%</td>
                <td>{share:.1f}%</td>
            </tr>
            """
        
        html_content += """
        </table>
        """
    
    # Add export sector growth rates if multiple years are available
    export_columns = [col for col in df.columns if 'Exports (million USD)' in col]
    if export_columns and start_year_actual != end_year_actual:
        # Only display fastest and largest sectors if we have data
        if growth_rates:
            fastest_sector = max(growth_rates.items(), key=lambda x: x[1])
            largest_sector = max([(col.split(' Exports')[0], final_year_data[col]) for col in export_columns], key=lambda x: x[1])
            
            html_content += f"""
                <li>The fastest growing export sector is {fastest_sector[0]} with an average annual growth rate of {fastest_sector[1]:.1f}%.</li>
                <li>The largest export sector in {end_year_actual} is {largest_sector[0]} with exports of ${largest_sector[1]/1000:.2f} billion.</li>
            """
    
    html_content += """
        </ul>
        
        <h2>Policy Implications</h2>
        <p>
            Based on the simulation results, the following policy recommendations can be considered:
        </p>
        <ul>
            <li>Continue to focus on export diversification to reduce dependency on a limited number of sectors.</li>
            <li>Invest in logistics infrastructure to improve trade facilitation and reduce costs.</li>
            <li>Develop strategic trade agreements to mitigate the impact of LDC graduation.</li>
            <li>Enhance competitiveness through technology adoption, skill development, and quality improvements.</li>
            <li>Strengthen backward linkages to reduce import dependency for export production.</li>
        </ul>
        
        <div class="footer">
            <p>Bangladesh Trade Dynamics Simulation Report</p>
            <p>© 2023 All Rights Reserved</p>
        </div>
    </body>
    </html>
    """
    
    # Write HTML report to file
    os.makedirs('reports', exist_ok=True)
    output_file = f"reports/bd_trade_simulation_{scenario}_report.html"
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    print(f"HTML report generated: {output_file}")
    return output_file


if __name__ == "__main__":
    # Find available result files
    result_files = find_result_files()
    
    if result_files:
        print(f"Found {len(result_files)} result files:")
        for i, file in enumerate(result_files):
            print(f"{i+1}. {os.path.basename(file)}")
        
        choice = input("\nEnter the number of the file to use (or press Enter to use the first one): ")
        if choice and choice.isdigit() and 1 <= int(choice) <= len(result_files):
            selected_file = result_files[int(choice) - 1]
        else:
            selected_file = result_files[0]
        
        print(f"Using result file: {selected_file}")
        report_file = create_html_report(selected_file)
    else:
        print("No result files found. Generating report with sample data.")
        report_file = create_html_report()
    
    # Try to open the report in a web browser
    import webbrowser
    try:
        webbrowser.open('file://' + os.path.abspath(report_file))
    except Exception as e:
        print(f"Error opening report in browser: {e}")
        print(f"Please open the report manually: {report_file}") 