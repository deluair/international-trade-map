#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Custom HTML Report Generator for Bangladesh Trade Projections

This script creates a beautiful HTML report specifically for the Bangladesh 
trade projection data, showing trends from 2021-2030 across key metrics.
"""

import os
import sys
import json
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime
import webbrowser

def load_projection_results(file_path):
    """
    Load projection results from JSON file
    
    Args:
        file_path (str): Path to the results JSON file
        
    Returns:
        dict: The loaded results data
    """
    print(f"Loading projection results from {file_path}")
    with open(file_path, 'r') as f:
        results = json.load(f)
    
    print(f"Loaded data for {len(results['yearly_data'])} years")
    return results

def create_dataframe_from_results(results):
    """
    Create a pandas DataFrame from the simulation results
    
    Args:
        results (dict): Simulation results
        
    Returns:
        pd.DataFrame: DataFrame with yearly data
    """
    yearly_data = []
    
    # Process each year's data
    for year_str, year_data in results['yearly_data'].items():
        year = int(year_str)
        
        # Extract structural transformation data
        if 'structural_transformation' in year_data:
            structural_data = year_data['structural_transformation']
            
            # Create a row for this year
            row = {
                'Year': year,
                'Export Diversification HHI': structural_data.get('export_diversity_hhi', None),
                'Capability Index': structural_data.get('capability_index', None),
                'Industrial Policy Effectiveness': structural_data.get('industrial_policy_effectiveness', None),
            }
            
            # Extract export data by sector
            if 'export_sectors' in structural_data:
                export_sectors = structural_data['export_sectors']
                total_exports = sum(export_sectors.values())
                
                # Add total exports
                row['Total Exports (billion USD)'] = total_exports
                
                # Add export data for each sector
                for sector, value in export_sectors.items():
                    row[f'{sector.title()} Exports (billion USD)'] = value
                    row[f'{sector.title()} Share (%)'] = (value / total_exports * 100) if total_exports > 0 else 0
            
            yearly_data.append(row)
    
    # Create DataFrame and sort by year
    df = pd.DataFrame(yearly_data)
    
    # Determine if each year is historical or projected
    if 'historical_years' in results['metadata']:
        historical_years = [int(year) for year in results['metadata']['historical_years']]
        df['Data Type'] = df['Year'].apply(lambda x: 'Historical' if x in historical_years else 'Projected')
    else:
        # If not specified, assume years before 2024 are historical
        df['Data Type'] = df['Year'].apply(lambda x: 'Historical' if x < 2024 else 'Projected')
    
    # Sort by year
    df = df.sort_values('Year')
    
    return df

def generate_plotly_figures(df):
    """
    Generate Plotly figures for the HTML report
    
    Args:
        df (pd.DataFrame): DataFrame with yearly data
        
    Returns:
        dict: Dictionary of Plotly figures
    """
    figures = {}
    
    # Use a consistent color scheme
    colors = px.colors.qualitative.Plotly
    historical_color = '#1F77B4'  # Blue
    projected_color = '#FF7F0E'  # Orange
    
    # 1. Export Diversification HHI Trend
    fig_hhi = px.line(df, x='Year', y='Export Diversification HHI', 
                      title='Bangladesh Export Diversification (2021-2030)',
                      color='Data Type',
                      color_discrete_map={'Historical': historical_color, 'Projected': projected_color})
    
    fig_hhi.update_layout(
        xaxis_title='Year',
        yaxis_title='Export Concentration (HHI)',
        yaxis=dict(tickformat='.2f'),
        xaxis=dict(tickangle=0, dtick=1),
        legend_title='Data Type',
        hovermode='x unified'
    )
    
    # Add annotation for interpretation
    fig_hhi.add_annotation(
        x=0.5, y=-0.15,
        text="Lower values indicate greater export diversification",
        showarrow=False,
        xref='paper', yref='paper',
        font=dict(size=12, color="gray")
    )
    
    figures['export_diversification'] = fig_hhi
    
    # 2. Capability Development Trend
    fig_capability = px.line(df, x='Year', y='Capability Index', 
                             title='Bangladesh Capability Development (2021-2030)',
                             color='Data Type',
                             color_discrete_map={'Historical': historical_color, 'Projected': projected_color})
    
    fig_capability.update_layout(
        xaxis_title='Year',
        yaxis_title='Capability Index',
        yaxis=dict(tickformat='.2f'),
        xaxis=dict(tickangle=0, dtick=1),
        legend_title='Data Type',
        hovermode='x unified'
    )
    
    figures['capability_development'] = fig_capability
    
    # 3. Export Sector Composition
    # Filter columns for sector exports
    sector_columns = [col for col in df.columns if 'Exports (billion USD)' in col and col != 'Total Exports (billion USD)']
    sectors_df = df[['Year', 'Data Type'] + sector_columns]
    
    # Reshape for stacked area chart
    sectors_long = pd.melt(sectors_df, 
                           id_vars=['Year', 'Data Type'], 
                           value_vars=sector_columns,
                           var_name='Sector', 
                           value_name='Export Value')
    
    # Clean up sector names
    sectors_long['Sector'] = sectors_long['Sector'].str.replace(' Exports (billion USD)', '')
    
    # Create stacked area chart
    fig_sectors = px.area(sectors_long, x='Year', y='Export Value', color='Sector',
                          title='Bangladesh Export Sector Composition (2021-2030)',
                          color_discrete_sequence=colors)
    
    fig_sectors.update_layout(
        xaxis_title='Year',
        yaxis_title='Export Value (billion USD)',
        xaxis=dict(tickangle=0, dtick=1),
        legend_title='Sector',
        hovermode='x unified'
    )
    
    # Add line to separate historical and projected data
    if 'historical_years' in df.columns:
        max_historical_year = df[df['Data Type'] == 'Historical']['Year'].max()
        fig_sectors.add_vline(x=max_historical_year + 0.5, line_dash="dash", line_color="gray")
    
    figures['export_composition'] = fig_sectors
    
    # 4. RMG Dependency vs IT Services Growth
    if 'Rmg Share (%)' in df.columns and 'It_services Share (%)' in df.columns:
        fig_sectors_share = make_subplots(specs=[[{"secondary_y": True}]])
        
        # Add RMG share on primary y-axis
        fig_sectors_share.add_trace(
            go.Scatter(x=df['Year'], y=df['Rmg Share (%)'], name='RMG Share',
                      line=dict(color=colors[0]), mode='lines+markers'),
            secondary_y=False,
        )
        
        # Add IT Services share on secondary y-axis
        fig_sectors_share.add_trace(
            go.Scatter(x=df['Year'], y=df['It_services Share (%)'], name='IT Services Share',
                      line=dict(color=colors[1]), mode='lines+markers'),
            secondary_y=True,
        )
        
        # Add layout details
        fig_sectors_share.update_layout(
            title_text='RMG Dependency vs IT Services Growth (2021-2030)',
            xaxis=dict(tickangle=0, dtick=1),
            legend=dict(x=0.01, y=0.99, bordercolor="Black", borderwidth=1),
            hovermode='x unified'
        )
        
        # Set y-axes titles
        fig_sectors_share.update_yaxes(title_text="RMG Share (%)", secondary_y=False)
        fig_sectors_share.update_yaxes(title_text="IT Services Share (%)", secondary_y=True)
        
        figures['sector_shares'] = fig_sectors_share
    
    # 5. Total Exports Growth
    if 'Total Exports (billion USD)' in df.columns:
        fig_total = px.line(df, x='Year', y='Total Exports (billion USD)', 
                           title='Bangladesh Total Exports Growth (2021-2030)',
                           color='Data Type',
                           color_discrete_map={'Historical': historical_color, 'Projected': projected_color})
        
        fig_total.update_layout(
            xaxis_title='Year',
            yaxis_title='Export Value (billion USD)',
            xaxis=dict(tickangle=0, dtick=1),
            legend_title='Data Type',
            hovermode='x unified'
        )
        
        figures['total_exports'] = fig_total
    
    return figures

def create_html_report(results_file):
    """
    Create an HTML report from the simulation results
    
    Args:
        results_file (str): Path to the results JSON file
        
    Returns:
        str: Path to the HTML report file
    """
    # Load results
    results = load_projection_results(results_file)
    
    # Convert to DataFrame
    df = create_dataframe_from_results(results)
    
    # Generate figures
    figures = generate_plotly_figures(df)
    
    # Create output directory if it doesn't exist
    output_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'reports')
    os.makedirs(output_dir, exist_ok=True)
    
    # Generate timestamp for the report filename
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    report_file = os.path.join(output_dir, f"bd_trade_projection_report_{timestamp}.html")
    
    # Create the HTML content
    html_content = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Bangladesh Trade Projection Report (2021-2030)</title>
        <script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
        <style>
            body {{
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                line-height: 1.6;
                color: #333;
                max-width: 1200px;
                margin: 0 auto;
                padding: 20px;
                background-color: #f9f9f9;
            }}
            .header {{
                background-color: #044a87;
                color: white;
                padding: 20px;
                text-align: center;
                border-radius: 5px;
                margin-bottom: 30px;
                box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
            }}
            .header h1 {{
                margin: 0;
                font-size: 36px;
            }}
            .header p {{
                margin: 10px 0 0;
                font-size: 18px;
                opacity: 0.9;
            }}
            .section {{
                background-color: white;
                border-radius: 5px;
                padding: 25px;
                margin-bottom: 30px;
                box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
            }}
            .section h2 {{
                color: #044a87;
                border-bottom: 2px solid #f0f0f0;
                padding-bottom: 10px;
                margin-top: 0;
            }}
            .insights {{
                background-color: #f0f7ff;
                border-left: 4px solid #044a87;
                padding: 15px;
                margin: 20px 0;
            }}
            .insight-item {{
                margin-bottom: 10px;
            }}
            .plot-container {{
                margin: 20px 0;
                height: 500px;
            }}
            table {{
                width: 100%;
                border-collapse: collapse;
                margin: 20px 0;
            }}
            th, td {{
                padding: 12px 15px;
                border-bottom: 1px solid #ddd;
                text-align: left;
            }}
            th {{
                background-color: #f2f2f2;
                font-weight: bold;
            }}
            tr:hover {{
                background-color: #f5f5f5;
            }}
            .projected {{
                background-color: #fff8e6;
            }}
            .key-metrics {{
                display: flex;
                flex-wrap: wrap;
                justify-content: space-between;
                margin: 20px 0;
            }}
            .metric-card {{
                background-color: white;
                border-radius: 5px;
                padding: 20px;
                width: 23%;
                margin-bottom: 20px;
                box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
                text-align: center;
            }}
            .metric-value {{
                font-size: 24px;
                font-weight: bold;
                color: #044a87;
                margin: 10px 0;
            }}
            .metric-label {{
                font-size: 14px;
                color: #666;
            }}
            .footer {{
                text-align: center;
                margin-top: 30px;
                padding-top: 20px;
                border-top: 1px solid #ddd;
                color: #666;
                font-size: 14px;
            }}
            @media (max-width: 768px) {{
                .metric-card {{
                    width: 48%;
                }}
            }}
        </style>
    </head>
    <body>
        <div class="header">
            <h1>Bangladesh Trade Projection Report</h1>
            <p>Historical Analysis and Future Projections (2021-2030)</p>
            <p>Generated on {datetime.now().strftime('%B %d, %Y')}</p>
        </div>
        
        <div class="section">
            <h2>Executive Summary</h2>
            <p>This report presents a comprehensive analysis of Bangladesh's trade dynamics from 2021 to 2030, 
            using real historical data and sophisticated economic projections. The analysis focuses on export 
            diversification, capability development, and sectoral composition changes over time.</p>
            
            <div class="insights">
                <h3>Key Insights</h3>
                <div class="insight-item">• Bangladesh shows consistent improvement in export diversification, reducing its dependency on RMG sector.</div>
                <div class="insight-item">• The IT services and pharmaceutical sectors are projected to experience the highest growth rates.</div>
                <div class="insight-item">• Overall export capability is steadily increasing, demonstrating Bangladesh's improving position in global value chains.</div>
                <div class="insight-item">• Total exports are projected to grow substantially, supporting Bangladesh's transition to middle-income status.</div>
            </div>
            
            <div class="key-metrics">
                <div class="metric-card">
                    <div class="metric-label">Latest Historical Exports</div>
                    <div class="metric-value">${df[df['Data Type'] == 'Historical']['Total Exports (billion USD)'].iloc[-1]:.1f}B</div>
                    <div class="metric-label">USD (2023)</div>
                </div>
                <div class="metric-card">
                    <div class="metric-label">Projected Exports 2030</div>
                    <div class="metric-value">${df[df['Year'] == 2030]['Total Exports (billion USD)'].iloc[0]:.1f}B</div>
                    <div class="metric-label">USD</div>
                </div>
                <div class="metric-card">
                    <div class="metric-label">HHI Improvement</div>
                    <div class="metric-value">{(df[df['Year'] == 2021]['Export Diversification HHI'].iloc[0] - df[df['Year'] == 2030]['Export Diversification HHI'].iloc[0]) / df[df['Year'] == 2021]['Export Diversification HHI'].iloc[0] * 100:.1f}%</div>
                    <div class="metric-label">2021-2030</div>
                </div>
                <div class="metric-card">
                    <div class="metric-label">Capability Growth</div>
                    <div class="metric-value">{(df[df['Year'] == 2030]['Capability Index'].iloc[0] - df[df['Year'] == 2021]['Capability Index'].iloc[0]) / df[df['Year'] == 2021]['Capability Index'].iloc[0] * 100:.1f}%</div>
                    <div class="metric-label">2021-2030</div>
                </div>
            </div>
        </div>
        
        <div class="section">
            <h2>Export Diversification Trend</h2>
            <p>The Herfindahl-Hirschman Index (HHI) measures export concentration, with lower values indicating greater diversification.
               Bangladesh's export diversification is projected to improve steadily as the economy reduces its dependency on a few key sectors.</p>
            <div class="plot-container" id="export_diversification"></div>
        </div>
        
        <div class="section">
            <h2>Capability Development</h2>
            <p>The Capability Index measures Bangladesh's ability to produce complex, high-value products and participate in global value chains.
               This metric is projected to improve consistently as Bangladesh invests in skills development, technology adoption, and quality infrastructure.</p>
            <div class="plot-container" id="capability_development"></div>
        </div>
        
        <div class="section">
            <h2>Export Sector Composition</h2>
            <p>Bangladesh's export composition is projected to gradually shift, with increased contribution from non-traditional sectors like IT services, 
               pharmaceuticals, and light engineering, while RMG continues to grow at a more moderate pace.</p>
            <div class="plot-container" id="export_composition"></div>
        </div>
        
        <div class="section">
            <h2>Sectoral Shifts: RMG vs. IT Services</h2>
            <p>This comparison highlights the projected shift in Bangladesh's export structure, with RMG share gradually declining while
               IT services capture an increasing portion of export value, reflecting Bangladesh's digital transformation.</p>
            <div class="plot-container" id="sector_shares"></div>
        </div>
        
        <div class="section">
            <h2>Total Exports Growth</h2>
            <p>Bangladesh's total exports are projected to grow substantially over the period, supporting the country's economic development goals
               and its aspiration to become an upper-middle-income country.</p>
            <div class="plot-container" id="total_exports"></div>
        </div>
        
        <div class="section">
            <h2>Detailed Projections Data</h2>
            <p>The table below provides detailed yearly projections for key metrics:</p>
            <div style="overflow-x:auto;">
                <table>
                    <tr>
                        <th>Year</th>
                        <th>Data Type</th>
                        <th>Export Diversification (HHI)</th>
                        <th>Capability Index</th>
                        <th>Total Exports (B USD)</th>
                        <th>RMG Share (%)</th>
                        <th>IT Services Share (%)</th>
                    </tr>
                    {table_rows}
                </table>
            </div>
        </div>
        
        <div class="section">
            <h2>Methodology & Assumptions</h2>
            <p>This analysis combines real historical trade data with projection models that incorporate:</p>
            <ul>
                <li>Historical export performance and sector-specific growth rates</li>
                <li>Global market trends and demand projections</li>
                <li>Bangladesh's industrial policy and development strategies</li>
                <li>Structural transformation and value chain upgrading trajectories</li>
            </ul>
            <p>Key assumptions include:</p>
            <ul>
                <li>Continued political stability and policy consistency</li>
                <li>Sustained investment in infrastructure and digital capabilities</li>
                <li>Progressive implementation of trade facilitation measures</li>
                <li>Gradual improvements in business environment and ease of doing business</li>
            </ul>
        </div>
        
        <div class="footer">
            <p>Generated by Bangladesh Trade Dynamics Simulation Engine</p>
            <p>© 2025 University of Tennessee</p>
        </div>
        
        <script>
            {plotly_js}
        </script>
    </body>
    </html>
    """
    
    # Generate table rows
    table_rows = ""
    for _, row in df.iterrows():
        row_class = "projected" if row['Data Type'] == 'Projected' else ""
        table_rows += f"""
        <tr class="{row_class}">
            <td>{int(row['Year'])}</td>
            <td>{row['Data Type']}</td>
            <td>{row['Export Diversification HHI']:.4f}</td>
            <td>{row['Capability Index']:.4f}</td>
            <td>{row.get('Total Exports (billion USD)', 0):.2f}</td>
            <td>{row.get('Rmg Share (%)', 0):.1f}</td>
            <td>{row.get('It_services Share (%)', 0):.1f}</td>
        </tr>
        """
    
    # Generate Plotly JavaScript
    plotly_js = ""
    for name, fig in figures.items():
        plotly_js += f"""
        var {name}_data = {fig.to_json()};
        Plotly.newPlot('{name}', {name}_data.data, {name}_data.layout);
        """
    
    # Replace placeholders in HTML template
    html_content = html_content.format(table_rows=table_rows, plotly_js=plotly_js)
    
    # Write HTML to file
    with open(report_file, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    print(f"HTML report saved to {report_file}")
    return report_file

def main():
    """Main entry point for the script"""
    # Check if a results file was provided as an argument
    if len(sys.argv) > 1:
        results_file = sys.argv[1]
    else:
        # Find the most recent results file
        results_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'results')
        result_files = [os.path.join(results_dir, f) for f in os.listdir(results_dir) 
                        if f.startswith('bd_projection_results_') and f.endswith('.json')]
        
        if not result_files:
            print("No projection results files found. Please run the simulation first.")
            return
        
        # Sort by modification time (newest first)
        result_files.sort(key=lambda x: os.path.getmtime(x), reverse=True)
        results_file = result_files[0]
    
    print(f"Using results file: {results_file}")
    
    # Create HTML report
    report_file = create_html_report(results_file)
    
    # Try to open the report in a web browser
    print("Attempting to open the report in your web browser...")
    try:
        webbrowser.open('file://' + os.path.abspath(report_file))
    except Exception as e:
        print(f"Error opening report in browser: {e}")
        print(f"Please open the report manually: {report_file}")

if __name__ == "__main__":
    main()
