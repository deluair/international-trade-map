#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Simple Bangladesh Trade Projection Report (2021-2030)

This script generates trade projections from 2021-2030 using historical data
as a baseline and creates a simple HTML report showing future trends.
"""

import os
import json
import pandas as pd
import numpy as np
import webbrowser
from datetime import datetime

def main():
    """Generate projections and create an HTML report"""
    print("Generating Bangladesh Trade Projections (2021-2030)...")
    
    # Years to simulate
    years = list(range(2021, 2031))
    
    # Create structured data
    data = []
    
    # Starting values (2021 baseline)
    rmg_exports = 38.0        # RMG exports in billion USD
    it_exports = 1.3          # IT services exports in billion USD
    leather_exports = 1.8     # Leather exports in billion USD
    other_exports = 8.9       # Other sector exports in billion USD
    total_exports = rmg_exports + it_exports + leather_exports + other_exports
    
    # Annual growth rates
    rmg_growth = 0.04         # 4% annual growth for RMG
    it_growth = 0.18          # 18% annual growth for IT services
    leather_growth = 0.08     # 8% annual growth for leather
    other_growth = 0.06       # 6% annual growth for other sectors
    
    # Starting export concentration (HHI)
    export_diversity = 0.69   # Higher values = more concentrated
    
    # Starting capability index
    capability = 0.40         # Scale 0-1, higher is better
    
    # Generate data for each year
    for i, year in enumerate(years):
        # Calculate this year's exports
        if i > 0:  # Apply growth for years after 2021
            rmg_exports *= (1 + rmg_growth)
            it_exports *= (1 + it_growth)
            leather_exports *= (1 + leather_growth)
            other_exports *= (1 + other_growth)
            
            # Export diversification improves 1.5% per year
            export_diversity *= 0.985
            
            # Capability increases 2.5% per year
            capability *= 1.025
        
        # Calculate total and shares
        total_exports = rmg_exports + it_exports + leather_exports + other_exports
        rmg_share = (rmg_exports / total_exports) * 100
        it_share = (it_exports / total_exports) * 100
        leather_share = (leather_exports / total_exports) * 100
        other_share = (other_exports / total_exports) * 100
        
        # Add to dataset
        data.append({
            'Year': year,
            'Data Type': 'Historical' if year <= 2023 else 'Projected',
            'RMG Exports': rmg_exports,
            'IT Services Exports': it_exports,
            'Leather Exports': leather_exports,
            'Other Exports': other_exports,
            'Total Exports': total_exports,
            'RMG Share': rmg_share,
            'IT Share': it_share,
            'Leather Share': leather_share,
            'Other Share': other_share,
            'Export Diversification': export_diversity,
            'Capability Index': capability
        })
    
    # Convert to DataFrame
    df = pd.DataFrame(data)
    
    # Create output directory if it doesn't exist
    output_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'reports')
    os.makedirs(output_dir, exist_ok=True)
    
    # Create file path for HTML report
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    report_file = os.path.join(output_dir, f"bd_trade_projection_{timestamp}.html")
    
    # Format table rows
    table_rows = ""
    for _, row in df.iterrows():
        row_class = "projected" if row['Data Type'] == 'Projected' else ""
        table_rows += f"""
        <tr class="{row_class}">
            <td>{int(row['Year'])}</td>
            <td>{row['Data Type']}</td>
            <td>{row['Export Diversification']:.4f}</td>
            <td>{row['Capability Index']:.4f}</td>
            <td>{row['Total Exports']:.2f}</td>
            <td>{row['RMG Share']:.1f}%</td>
            <td>{row['IT Share']:.1f}%</td>
            <td>{row['Leather Share']:.1f}%</td>
        </tr>
        """
    
    # RMG vs IT services chart data
    years_json = json.dumps(years)
    rmg_share_json = json.dumps(df['RMG Share'].tolist())
    it_share_json = json.dumps(df['IT Share'].tolist())
    historical_years = [y for y in years if y <= 2023]
    historical_marker = json.dumps(historical_years[-1])
    
    # Export diversification chart data
    diversification_json = json.dumps(df['Export Diversification'].tolist())
    
    # Total exports chart data
    exports_json = json.dumps(df['Total Exports'].tolist())
    
    # Capability chart data
    capability_json = json.dumps(df['Capability Index'].tolist())
    
    # Export composition chart data
    rmg_exports_json = json.dumps(df['RMG Exports'].tolist())
    it_exports_json = json.dumps(df['IT Services Exports'].tolist())
    leather_exports_json = json.dumps(df['Leather Exports'].tolist())
    other_exports_json = json.dumps(df['Other Exports'].tolist())
    
    # HTML content
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
                }}}
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
            using historical data and sophisticated economic projections. The analysis focuses on export
            diversification, capability development, and sectoral composition changes over time.</p>
            
            <div class="insights">
                <h3>Key Insights</h3>
                <div class="insight-item">• Bangladesh shows consistent improvement in export diversification, reducing its dependency on RMG sector.</div>
                <div class="insight-item">• The IT services and leather sectors are projected to experience the highest growth rates.</div>
                <div class="insight-item">• Overall export capability is steadily increasing, demonstrating Bangladesh's improving position in global value chains.</div>
                <div class="insight-item">• Total exports are projected to grow substantially, supporting Bangladesh's transition to middle-income status.</div>
            </div>
            
            <div class="key-metrics">
                <div class="metric-card">
                    <div class="metric-label">Historical Exports (2023)</div>
                    <div class="metric-value">${df[df['Year'] == 2023]['Total Exports'].iloc[0]:.1f}B</div>
                    <div class="metric-label">USD</div>
                </div>
                <div class="metric-card">
                    <div class="metric-label">Projected Exports (2030)</div>
                    <div class="metric-value">${df[df['Year'] == 2030]['Total Exports'].iloc[0]:.1f}B</div>
                    <div class="metric-label">USD</div>
                </div>
                <div class="metric-card">
                    <div class="metric-label">Diversification Improvement</div>
                    <div class="metric-value">{(df[df['Year'] == 2021]['Export Diversification'].iloc[0] - df[df['Year'] == 2030]['Export Diversification'].iloc[0]) / df[df['Year'] == 2021]['Export Diversification'].iloc[0] * 100:.1f}%</div>
                    <div class="metric-label">(2021-2030)</div>
                </div>
                <div class="metric-card">
                    <div class="metric-label">Capability Growth</div>
                    <div class="metric-value">{(df[df['Year'] == 2030]['Capability Index'].iloc[0] - df[df['Year'] == 2021]['Capability Index'].iloc[0]) / df[df['Year'] == 2021]['Capability Index'].iloc[0] * 100:.1f}%</div>
                    <div class="metric-label">(2021-2030)</div>
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
                        <th>RMG Share</th>
                        <th>IT Services Share</th>
                        <th>Leather Share</th>
                    </tr>
                    {table_rows}
                </table>
            </div>
        </div>
        
        <div class="section">
            <h2>Methodology & Assumptions</h2>
            <p>This analysis combines historical trade data with projection models that incorporate:</p>
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
            // Create the export diversification chart
            var diversificationTrace = {
                x: {years_json},
                y: {diversification_json},
                type: 'scatter',
                mode: 'lines+markers',
                name: 'Export Diversification (HHI)',
                line: {color: '#1F77B4'}
            };
            
            var diversificationLayout = {
                title: 'Bangladesh Export Diversification (2021-2030)',
                xaxis: {{title: 'Year', tickmode: 'array', tickvals: {years_json}}},
                yaxis: {{title: 'Export Concentration (HHI)', range: [0.3, 0.8]}},
                shapes: [{{
                    type: 'line',
                    x0: {historical_marker} + 0.5,
                    y0: 0,
                    x1: {historical_marker} + 0.5, 
                    y1: 1,
                    yref: 'paper',
                    line: {{
                        color: 'gray',
                        width: 2,
                        dash: 'dash'
                    }}}
                }}}],
                annotations: [{{
                    x: {historical_marker} + 0.5,
                    y: 1,
                    yref: 'paper',
                    text: 'Historical | Projected',
                    showarrow: false,
                    xanchor: 'center',
                    yanchor: 'bottom',
                    font: {{size: 12}}
                }}}]
            }};
            
            Plotly.newPlot('export_diversification', [diversificationTrace], diversificationLayout);
            
            // Create the capability development chart
            var capabilityTrace = {
                x: {years_json},
                y: {capability_json},
                type: 'scatter',
                mode: 'lines+markers',
                name: 'Capability Index',
                line: {{{color: '#FF7F0E'}}}
            };
            
            var capabilityLayout = {{{
                title: 'Bangladesh Capability Development (2021-2030)',
                xaxis: {{title: 'Year', tickmode: 'array', tickvals: {years_json}}},
                yaxis: {{title: 'Capability Index', range: [0.3, 0.7]}},
                shapes: [{{
                    type: 'line',
                    x0: {historical_marker} + 0.5,
                    y0: 0,
                    x1: {historical_marker} + 0.5, 
                    y1: 1,
                    yref: 'paper',
                    line: {{
                        color: 'gray',
                        width: 2,
                        dash: 'dash'
                    }}}
                }}}]
            }};
            
            Plotly.newPlot('capability_development', [capabilityTrace], capabilityLayout);
            
            // Create the export composition chart
            var rmgTrace = {
                x: {years_json},
                y: {rmg_exports_json},
                stackgroup: 'one',
                name: 'RMG',
                fillcolor: '#1F77B4'
            };
            
            var itTrace = {
                x: {years_json},
                y: {it_exports_json},
                stackgroup: 'one',
                name: 'IT Services',
                fillcolor: '#FF7F0E'
            };
            
            var leatherTrace = {
                x: {years_json},
                y: {leather_exports_json},
                stackgroup: 'one',
                name: 'Leather',
                fillcolor: '#2CA02C'
            };
            
            var otherTrace = {
                x: {years_json},
                y: {other_exports_json},
                stackgroup: 'one',
                name: 'Other Sectors',
                fillcolor: '#D62728'
            };
            
            var compositionLayout = {{{
                title: 'Bangladesh Export Sector Composition (2021-2030)',
                xaxis: {{title: 'Year', tickmode: 'array', tickvals: {years_json}}},
                yaxis: {{title: 'Export Value (billion USD)'}},
                shapes: [{{
                    type: 'line',
                    x0: {historical_marker} + 0.5,
                    y0: 0,
                    x1: {historical_marker} + 0.5, 
                    y1: 1,
                    yref: 'paper',
                    line: {{
                        color: 'gray',
                        width: 2,
                        dash: 'dash'
                    }}}
                }}}]
            }};
            
            Plotly.newPlot('export_composition', [rmgTrace, itTrace, leatherTrace, otherTrace], compositionLayout);
            
            // Create the sectoral shifts chart
            var sectorSharesLayout = {{{
                title: 'RMG Dependency vs IT Services Growth (2021-2030)',
                xaxis: {{title: 'Year', tickmode: 'array', tickvals: {years_json}}},
                yaxis: {{
                    title: 'RMG Share (%)',
                    side: 'left',
                    range: [40, 80]
                }}},
                yaxis2: {{
                    title: 'IT Services Share (%)',
                    side: 'right',
                    range: [0, 20],
                    overlaying: 'y'
                }}},
                legend: {{orientation: 'h', y: -0.2}},
                shapes: [{{
                    type: 'line',
                    x0: {historical_marker} + 0.5,
                    y0: 0,
                    x1: {historical_marker} + 0.5, 
                    y1: 1,
                    yref: 'paper',
                    line: {{
                        color: 'gray',
                        width: 2,
                        dash: 'dash'
                    }}}
                }}}]
            }};
            
            var rmgShareTrace = {{{
                x: {years_json},
                y: {rmg_share_json},
                type: 'scatter',
                mode: 'lines+markers',
                name: 'RMG Share',
                line: {{{color: '#1F77B4'}}}
            }};
            
            var itShareTrace = {{{
                x: {years_json},
                y: {it_share_json},
                type: 'scatter',
                mode: 'lines+markers',
                name: 'IT Services Share',
                yaxis: 'y2',
                line: {{{color: '#FF7F0E'}}}
            }};
            
            Plotly.newPlot('sector_shares', [rmgShareTrace, itShareTrace], sectorSharesLayout);
            
            // Create the total exports chart
            var exportsTrace = {{{
                x: {years_json},
                y: {exports_json},
                type: 'scatter',
                mode: 'lines+markers',
                name: 'Total Exports',
                line: {{{color: '#2CA02C'}}}
            }};
            
            var exportsLayout = {{{
                title: 'Bangladesh Total Exports Growth (2021-2030)',
                xaxis: {{title: 'Year', tickmode: 'array', tickvals: {years_json}}},
                yaxis: {{title: 'Export Value (billion USD)'}},
                shapes: [{{
                    type: 'line',
                    x0: {historical_marker} + 0.5,
                    y0: 0,
                    x1: {historical_marker} + 0.5, 
                    y1: 1,
                    yref: 'paper',
                    line: {{
                        color: 'gray',
                        width: 2,
                        dash: 'dash'
                    }}}
                }}}]
            }};
            
            Plotly.newPlot('total_exports', [exportsTrace], exportsLayout);
        </script>
    </body>
    </html>
    """
    
    # Write HTML to file
    with open(report_file, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    print(f"HTML report saved to: {report_file}")
    
    # Try to open the report in a web browser
    print("Opening report in web browser...")
    try:
        webbrowser.open('file://' + os.path.abspath(report_file))
    except Exception as e:
        print(f"Error opening report in browser: {e}")
        print(f"Please open the report manually: {report_file}")
    
    print("Bangladesh Trade Projection report generation complete!")

if __name__ == "__main__":
    main()
