import json
import os
import argparse
import pandas as pd
import plotly.graph_objects as go
import plotly.offline as pyo
from plotly.subplots import make_subplots

def load_simulation_results(json_path):
    """Load simulation results from a JSON file."""
    try:
        with open(json_path, 'r') as f:
            results = json.load(f)
        print(f"Successfully loaded results from: {json_path}")
        return results
    except FileNotFoundError:
        print(f"Error: Results file not found at {json_path}")
        return None
    except json.JSONDecodeError:
        print(f"Error: Could not decode JSON from {json_path}")
        return None
    except Exception as e:
        print(f"An unexpected error occurred loading {json_path}: {e}")
        return None

def extract_data_for_report(results):
    """Extract and structure data needed for the HTML report."""
    if not results or 'yearly_data' not in results:
        print("Error: Invalid or empty results data.")
        return None

    yearly_data = results.get('yearly_data', {})
    if not yearly_data:
        print("Warning: No yearly data found in results.")
        return None
        
    years = sorted([int(y) for y in yearly_data.keys()])
    report_data = {'years': years, 'raw_yearly': yearly_data}

    # Extract key time series
    report_data['gdp'] = [yearly_data[str(y)].get('investment', {}).get('gdp', None) for y in years]
    report_data['total_exports'] = [yearly_data[str(y)].get('export', {}).get('total_exports', None) for y in years]
    report_data['total_imports'] = [yearly_data[str(y)].get('import', {}).get('total_imports', None) for y in years]
    report_data['trade_balance'] = [yearly_data[str(y)].get('aggregate_metrics', {}).get('trade_balance', None) for y in years]
    report_data['trade_openness'] = [yearly_data[str(y)].get('aggregate_metrics', {}).get('trade_openness', None) for y in years]
    
    # Extract export sector details (handle potential errors in sector results)
    sector_names = set()
    for year_data in yearly_data.values():
        sector_details = year_data.get('export', {}).get('sector_details', {})
        sector_names.update(sector_details.keys())
        
    report_data['export_sectors'] = {name: [] for name in sector_names}
    for year in years:
        sector_details = yearly_data[str(year)].get('export', {}).get('sector_details', {})
        for name in sector_names:
            volume = sector_details.get(name, {}).get('export_volume', None)
            report_data['export_sectors'][name].append(volume)

    # Add more extractions here as needed (e.g., logistics, policy indices)
    report_data['logistics_performance'] = [yearly_data[str(y)].get('logistics', {}).get('overall_performance', None) for y in years]
    report_data['exchange_rate'] = [yearly_data[str(y)].get('exchange_rate', {}).get('exchange_rate', None) for y in years]
    
    # Handle potential missing data (replace None with NaN for plotting/analysis)
    for key, value in report_data.items():
        if isinstance(value, list):
             report_data[key] = [v if v is not None else pd.NA for v in value]
        elif isinstance(value, dict) and key == 'export_sectors':
            for sector, sector_data in value.items():
                 report_data['export_sectors'][sector] = [v if v is not None else pd.NA for v in sector_data]
                 
    print(f"Data extracted for years: {years}")
    return report_data

def generate_plots(report_data):
    """Generate Plotly plots from the extracted report data."""
    plots = {}
    years = report_data['years']

    # --- Key Economic Indicators ---
    fig_econ = make_subplots(rows=2, cols=1, shared_xaxes=True, 
                             subplot_titles=("GDP Over Time", "Trade Balance & Openness"))

    fig_econ.add_trace(go.Scatter(x=years, y=report_data['gdp'], name='GDP (Billion USD)', mode='lines+markers'), row=1, col=1)
    
    fig_econ.add_trace(go.Scatter(x=years, y=report_data['trade_balance'], name='Trade Balance (Billion USD)', mode='lines+markers'), row=2, col=1)
    # Add secondary y-axis for Trade Openness
    # fig_econ.add_trace(go.Scatter(x=years, y=report_data['trade_openness'], name='Trade Openness (%)', mode='lines+markers', yaxis='y2'), row=2, col=1)

    fig_econ.update_layout(
        title_text="Key Economic Indicators",
        hovermode="x unified",
        height=600,
        # yaxis2=dict(title="Trade Openness (%)", overlaying='y', side='right', tickformat='.1%')
    )
    plots['key_economic_indicators'] = pyo.plot(fig_econ, include_plotlyjs=False, output_type='div')
    
    # --- Export/Import Volume ---
    fig_trade_vol = go.Figure()
    fig_trade_vol.add_trace(go.Scatter(x=years, y=report_data['total_exports'], name='Total Exports (Billion USD)', mode='lines+markers'))
    fig_trade_vol.add_trace(go.Scatter(x=years, y=report_data['total_imports'], name='Total Imports (Billion USD)', mode='lines+markers'))
    fig_trade_vol.update_layout(
        title="Total Export and Import Volumes",
        xaxis_title="Year",
        yaxis_title="Volume (Billion USD)",
        hovermode="x unified"
    )
    plots['trade_volume'] = pyo.plot(fig_trade_vol, include_plotlyjs=False, output_type='div')

    # --- Export Sector Composition (Stacked Bar) ---
    fig_sectors = go.Figure()
    for sector_name, sector_data in report_data['export_sectors'].items():
        # Ensure data is numeric for plotting, replace NA with 0 for stacked bar
        numeric_sector_data = pd.to_numeric(sector_data, errors='coerce').fillna(0)
        fig_sectors.add_trace(go.Bar(x=years, y=numeric_sector_data, name=sector_name))
        
    fig_sectors.update_layout(
        barmode='stack',
        title="Export Value by Sector Over Time",
        xaxis_title="Year",
        yaxis_title="Export Value (Billion USD)",
        legend_title="Sector"
    )
    plots['export_sectors'] = pyo.plot(fig_sectors, include_plotlyjs=False, output_type='div')

    # --- Other Indicators (Logistics, Exchange Rate) ---
    fig_other = make_subplots(rows=2, cols=1, shared_xaxes=True, 
                             subplot_titles=("Logistics Performance Index", "Exchange Rate (BDT/USD)"))
                             
    fig_other.add_trace(go.Scatter(x=years, y=report_data['logistics_performance'], name='Logistics Perf. Index', mode='lines+markers'), row=1, col=1)
    fig_other.add_trace(go.Scatter(x=years, y=report_data['exchange_rate'], name='Exchange Rate', mode='lines+markers'), row=2, col=1)
    
    fig_other.update_layout(title_text="Other Key Indicators", height=600, hovermode="x unified")
    plots['other_indicators'] = pyo.plot(fig_other, include_plotlyjs=False, output_type='div')
    
    print("Generated plots for the report.")
    return plots

def generate_html_report(report_data, plots, output_file):
    """Generates the final HTML report file."""
    
    years = report_data['years']
    latest_year = max(years)
    
    # Start HTML content
    html_content = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Holistic Trade Simulation Report ({min(years)}-{max(years)})</title>
    <script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
    <style>
        body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; line-height: 1.6; padding: 20px; max-width: 1400px; margin: auto; background-color: #f8f9fa; color: #343a40; }}
        h1, h2, h3 {{ color: #007bff; border-bottom: 2px solid #007bff; padding-bottom: 8px; margin-top: 30px; }}
        h1 {{ text-align: center; color: #0056b3; border-bottom-width: 3px; }}
        .plot-container {{ margin-bottom: 40px; padding: 25px; border: 1px solid #dee2e6; border-radius: 8px; background-color: #ffffff; box-shadow: 0 4px 8px rgba(0,0,0,0.05); }}
        table {{ width: 100%; border-collapse: collapse; margin-top: 25px; box-shadow: 0 2px 4px rgba(0,0,0,0.05); }}
        th, td {{ border: 1px solid #ced4da; padding: 12px; text-align: left; }}
        th {{ background-color: #e9ecef; color: #495057; font-weight: bold; }}
        tr:nth-child(even) {{ background-color: #f8f9fa; }}
        tr:hover {{ background-color: #e2e6ea; }}
        .summary-table td:nth-child(n+2) {{ text-align: right; }} /* Right-align numeric data */
        .details-section {{ margin-bottom: 30px; padding: 20px; border: 1px solid #e0e0e0; border-radius: 8px; background-color: #fff; }}
        .error-message {{ color: #dc3545; font-style: italic; }}
    </style>
</head>
<body>
    <h1>Holistic Trade Simulation Report ({min(years)}-{max(years)})</h1>

    <h2>Overall Trends</h2>
    <div class="plot-container">{plots.get('key_economic_indicators', '<p class="error-message">Economic indicators plot unavailable.</p>')}</div>
    <div class="plot-container">{plots.get('trade_volume', '<p class="error-message">Trade volume plot unavailable.</p>')}</div>
    <div class="plot-container">{plots.get('export_sectors', '<p class="error-message">Export sector plot unavailable.</p>')}</div>
    <div class="plot-container">{plots.get('other_indicators', '<p class="error-message">Other indicators plot unavailable.</p>')}</div>

    <h2>Yearly Summary Data</h2>
    <div class="plot-container summary-table">
        <table>
            <thead>
                <tr>
                    <th>Year</th>
                    <th>GDP (Billion USD)</th>
                    <th>Total Exports (Billion USD)</th>
                    <th>Total Imports (Billion USD)</th>
                    <th>Trade Balance (Billion USD)</th>
                    <th>Trade Openness</th>
                    <th>Logistics Perf. Index</th>
                    <th>Exchange Rate (BDT/USD)</th>
                </tr>
            </thead>
            <tbody>
"""
    # Add table rows
    df_summary = pd.DataFrame({
        'Year': report_data['years'],
        'GDP': report_data['gdp'],
        'Exports': report_data['total_exports'],
        'Imports': report_data['total_imports'],
        'Balance': report_data['trade_balance'],
        'Openness': report_data['trade_openness'],
        'Logistics': report_data['logistics_performance'],
        'ExRate': report_data['exchange_rate']
    })
    
    # Function to safely format numbers or return 'N/A'
    def format_num(value, precision, is_percent=False):
        if pd.isna(value):
            return 'N/A'
        try:
            if is_percent:
                 return f"{float(value):.{precision}%}"
            else:
                 return f"{float(value):.{precision}f}"
        except (ValueError, TypeError):
            return 'N/A'

    for i, year in enumerate(years):
        html_content += f"""
                <tr>
                    <td>{year}</td>
                    <td>{format_num(df_summary.loc[i, 'GDP'], 2)}</td>
                    <td>{format_num(df_summary.loc[i, 'Exports'], 2)}</td>
                    <td>{format_num(df_summary.loc[i, 'Imports'], 2)}</td>
                    <td>{format_num(df_summary.loc[i, 'Balance'], 2)}</td>
                    <td>{format_num(df_summary.loc[i, 'Openness'], 1, True)}</td>
                    <td>{format_num(df_summary.loc[i, 'Logistics'], 3)}</td>
                    <td>{format_num(df_summary.loc[i, 'ExRate'], 2)}</td>
                </tr>
"""

    html_content += """
            </tbody>
        </table>
    </div>

    <h2>Detailed Export Sector Data ({latest_year})</h2>
     <div class="details-section">
         <table>
            <thead>
                <tr><th>Sector</th><th>Export Value (Billion USD)</th></tr>
            </thead>
            <tbody>
"""
    # Add latest year sector data
    latest_year_idx = years.index(latest_year)
    latest_sectors = {}
    for sector_name, sector_data in report_data['export_sectors'].items():
        if latest_year_idx < len(sector_data) and pd.notna(sector_data[latest_year_idx]):
             latest_sectors[sector_name] = sector_data[latest_year_idx]
        else:
             latest_sectors[sector_name] = 0 # Or handle as 'N/A'
             
    for sector, value in sorted(latest_sectors.items(), key=lambda item: item[1], reverse=True):
         html_content += f"<tr><td>{sector}</td><td>{format_num(value, 3)}</td></tr>"
         
    html_content += """
            </tbody>
        </table>
    </div>

    {/* Add more sections here for other detailed data if needed */}

</body>
</html>
"""

    # Write to file
    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(html_content)
        print(f"HTML report generated successfully: {output_file}")
    except IOError as e:
        print(f"Error writing HTML report to {output_file}: {e}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate HTML report from simulation JSON results.")
    parser.add_argument("-i", "--input", 
                        default=os.path.join("results", "simulation_results_baseline.json"),
                        help="Path to the input simulation results JSON file.")
    parser.add_argument("-o", "--output", 
                        default="holistic_simulation_report.html",
                        help="Path to save the output HTML report.")
    
    args = parser.parse_args()

    # Run the report generation process
    results_data = load_simulation_results(args.input)
    if results_data:
        extracted_data = extract_data_for_report(results_data)
        if extracted_data:
            plots = generate_plots(extracted_data)
            generate_html_report(extracted_data, plots, args.output)
        else:
            print("Could not extract data, skipping report generation.")
    else:
        print("Could not load results, skipping report generation.") 