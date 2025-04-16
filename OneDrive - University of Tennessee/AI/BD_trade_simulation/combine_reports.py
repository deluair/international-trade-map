"""
Generates a combined HTML report showing both real data analysis and scenario projections.
"""

import os
import sys
import json
import glob
import pandas as pd
from datetime import datetime
import plotly.graph_objects as go
import plotly.io as pio
from plotly.subplots import make_subplots
import plotly.express as px

# Add project root to path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

# --- Import functions from other scripts --- 

# From bd_trade_report (Real Data Handling)
try:
    from bd_trade_report import load_trade_data, prepare_data_for_report, get_top_products_and_partners, generate_plotly_figures as generate_real_data_plots
except ImportError as e:
    print(f"Error importing from bd_trade_report: {e}")
    sys.exit(1)

# From generate_comparison_report (Scenario Handling)
try:
    from generate_comparison_report import find_latest_scenario_files, load_results as load_scenario_results, generate_comparison_plotly_figures
except ImportError as e:
    print(f"Error importing from generate_comparison_report: {e}")
    sys.exit(1)

# From visualization.plot_utils (DataFrame creation)
try:
    from visualization.plot_utils import create_dataframe_from_results
except ImportError as e:
    print(f"Error importing from visualization.plot_utils: {e}")
    sys.exit(1)

# Define constants
REAL_DATA_FILE = "data/bd_trade_data.csv"
RESULTS_DIR = os.path.join(project_root, 'results')
REPORTS_DIR = os.path.join(project_root, 'reports')

# --- HTML Generation Function (to be implemented) --- 
def generate_combined_html(real_data_summary, real_data_plots, scenario_dataframes, scenario_plots, output_file):
    """Generates the combined HTML report."""
    print("Constructing Combined HTML report...")

    # Start HTML
    html_content = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Combined Trade Report: Real Data & Scenarios</title>
    <script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
    <style>
        body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; margin: 20px; background-color: #f4f7f6; color: #333; }
        .container { max-width: 1200px; margin: auto; background-color: #fff; padding: 30px; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); } 
        h1, h2, h3 { color: #0056b3; border-bottom: 2px solid #007bff; padding-bottom: 8px; margin-top: 30px; margin-bottom: 20px; } 
        h1 { text-align: center; margin-bottom: 30px; }
        h2 { font-size: 1.8em; }
        h3 { font-size: 1.4em; color: #17a2b8; border-bottom: none; margin-bottom: 10px;}
        .section { margin-bottom: 40px; padding-bottom: 20px; border-bottom: 1px dashed #ccc; } 
        .figure-container { margin-bottom: 25px; border: 1px solid #ddd; padding: 15px; border-radius: 5px; background-color: #fff; } 
        table { width: 100%; border-collapse: collapse; margin-top: 20px; margin-bottom: 30px; } 
        th, td { border: 1px solid #ccc; padding: 10px 12px; text-align: left; vertical-align: top; } 
        th { background-color: #e9ecef; font-weight: 600; position: sticky; top: 0; } 
        tr:nth-child(even) { background-color: #f8f9fa; } 
        td:nth-child(n+2):not(.text-left) { text-align: right; } /* Right-align numeric data, allow override */
        .footer { text-align: center; margin-top: 40px; font-size: 0.9em; color: #666; }
        .plot-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(500px, 1fr)); gap: 20px; } /* Basic grid layout */
    </style>
</head>
<body>
<div class="container">
    <h1>Combined Trade Report: Real Data Analysis & Scenario Projections</h1>
"""

    # --- Section 1: Real Data Analysis --- 
    html_content += """
    <div class="section">
        <h2>Real Data Analysis (Based on Loaded Historical Data)</h2>
    """
    # Add Real Data Summary (Top Products/Partners Tables)
    # This reuses parts of the HTML generation logic from bd_trade_report.py's create_html_report
    top_data = real_data_summary.get('top_data', {})
    yearly_data = real_data_summary.get('yearly', pd.DataFrame())
    
    if not yearly_data.empty:
        recent_data = yearly_data.iloc[-1]
        html_content += f"""
        <p>Analysis based on data up to {int(recent_data['year'])}.</p>
        <div class="metrics-container" style="display: flex; flex-wrap: wrap; justify-content: space-around; margin-bottom: 20px;">
             <div style="background-color: #f8f9fa; padding: 10px; border-radius: 5px; margin: 5px; min-width: 150px; text-align: center;">
                 <div>{int(recent_data['year'])} Exports</div><div style="font-size: 1.5em; font-weight: bold;">${recent_data['export_billion']:.2f}B</div>
             </div>
             <div style="background-color: #f8f9fa; padding: 10px; border-radius: 5px; margin: 5px; min-width: 150px; text-align: center;">
                 <div>{int(recent_data['year'])} Imports</div><div style="font-size: 1.5em; font-weight: bold;">${recent_data['import_billion']:.2f}B</div>
             </div>
              <div style="background-color: #f8f9fa; padding: 10px; border-radius: 5px; margin: 5px; min-width: 150px; text-align: center;">
                 <div>{int(recent_data['year'])} Trade Balance</div><div style="font-size: 1.5em; font-weight: bold;">${recent_data['trade_balance_billion']:.2f}B</div>
             </div>
        </div>
        """

    # Helper to generate tables for top items
    def generate_top_table(title, data_frame, value_col_name, name_col_name):
        table_html = f"<h3>{title}</h3>"
        
        # --- DIAGNOSTIC PRINT ---
        if title == "Top Import Partners":
            print(f"DEBUG: Columns for Top Import Partners table: {data_frame.columns.tolist() if data_frame is not None else 'None'}")
        # --- END DIAGNOSTIC ---
        
        if data_frame is not None and not data_frame.empty:
            table_html += "<table><thead><tr><th>Name</th><th>Value (Billion USD)</th><th>Share (%)</th></tr></thead><tbody>"
            for _, row in data_frame.iterrows():
                 # Use the name column dynamically
                 name = row.get(name_col_name, 'N/A') 
                 value = row.get(f'{value_col_name}_billion', 0) # Assuming billion column exists
                 share = row.get('share', 0)
                 table_html += f"<tr><td class='text-left'>{name}</td><td>${value:.3f}B</td><td>{share:.1f}%</td></tr>"
            table_html += "</tbody></table>"
        else:
            table_html += "<p>Data not available.</p>"
        return table_html
        
    html_content += generate_top_table("Top Export Products", top_data.get('top_exports'), 'export', 'product_name')
    html_content += generate_top_table("Top Import Products", top_data.get('top_imports'), 'import', 'product_name')
    html_content += generate_top_table("Top Export Partners", top_data.get('top_export_partners'), 'export', 'country_name')
    html_content += generate_top_table("Top Import Partners", top_data.get('top_import_partners'), 'import', 'country_name')

    # Add Real Data Plots
    html_content += "<h3>Real Data Trends</h3><div class='plot-grid'>"
    if real_data_plots:
        for i, fig in enumerate(real_data_plots):
            fig_html = pio.to_html(fig, full_html=False, include_plotlyjs=False)
            html_content += f"<div class='figure-container'>{fig_html}</div>"
    else:
        html_content += "<p>No plots generated for real data.</p>"
    html_content += "</div></div>"

    # --- Section 2: Scenario Projections --- 
    html_content += """
    <div class="section">
        <h2>Scenario Projections (2024-2030)</h2>
    """
    # Add Scenario Summary Table (Copy/adapt from generate_comparison_report)
    html_summary = """
    <h3>Final Year (2030) Summary Comparison</h3>
    <table>
        <thead>
            <tr><th>Metric</th><th>Baseline</th><th>Optimistic</th><th>Pessimistic</th></tr>
        </thead>
        <tbody>
    """
    summary_metrics = [
        'Total Exports (billion USD)',
        'Capability Index',
        'Export Diversification HHI',
        'Industrial Policy Effectiveness'
    ]
    final_year = 2030 
    summary_data = {metric: {} for metric in summary_metrics}
    for scenario, df in scenario_dataframes.items():
        final_row = df[df['Year'] == final_year]
        if not final_row.empty:
            for metric in summary_metrics:
                if metric in df.columns:
                    value = final_row[metric].iloc[0]
                    summary_data[metric][scenario] = value if pd.notna(value) else 'N/A'
                else: summary_data[metric][scenario] = 'N/A'
        else: 
             for metric in summary_metrics: summary_data[metric][scenario] = 'N/A'

    def format_summary(value):
        if value == 'N/A': return value
        try:
            if abs(float(value)) < 1: return f"{float(value):.3f}"
            else: return f"{float(value):.2f}"
        except: return 'N/A'

    for metric in summary_metrics:
        html_summary += f"<tr><td class='text-left'>{metric}</td><td>{format_summary(summary_data[metric].get('baseline', 'N/A'))}</td><td>{format_summary(summary_data[metric].get('optimistic', 'N/A'))}</td><td>{format_summary(summary_data[metric].get('pessimistic', 'N/A'))}</td></tr>"
    html_summary += "</tbody></table>"
    html_content += html_summary

    # Add Scenario Comparison Plots
    html_content += "<h3>Scenario Comparison Plots</h3><div class='plot-grid'>"
    if scenario_plots:
        for fig_key, fig in scenario_plots.items():
            fig_html = pio.to_html(fig, full_html=False, include_plotlyjs=False)
            title = fig.layout.title.text if fig.layout.title.text else fig_key.replace("_", " ").title()
            html_content += f"<div class='figure-container'><h4>{title}</h4>{fig_html}</div>"
    else:
         html_content += "<p>No scenario comparison plots generated.</p>"
    html_content += "</div></div>"

    # --- Footer --- 
    html_content += f"""
    <div class="footer">
        Report generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
    </div>
</div> <!-- Close container -->
</body>
</html>
"""
    
    # Write to file
    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(html_content)
        print(f"Combined HTML report saved to: {output_file}")
    except Exception as e:
        print(f"Error writing combined HTML file: {e}")

def main():
    print("Generating Combined Trade Report (Real Data + Scenarios)...")
    os.makedirs(REPORTS_DIR, exist_ok=True)

    # --- 1. Process Real Data --- 
    print("\nProcessing Real Data...")
    real_data_summary = {'yearly': pd.DataFrame(), 'top_data': {}}
    real_data_plots = []
    try:
        trade_data = load_trade_data(REAL_DATA_FILE)
        if not trade_data.empty:
            yearly_data = prepare_data_for_report(trade_data)
            real_data_summary['yearly'] = yearly_data
            
            recent_year = trade_data['year'].max() if 'year' in trade_data.columns else None
            top_data = get_top_products_and_partners(trade_data, year=recent_year)
            real_data_summary['top_data'] = top_data
            
            if not yearly_data.empty:
                real_data_plots = generate_real_data_plots(yearly_data, top_data)
                print(f"Generated {len(real_data_plots)} plots for real data.")
            else:
                 print("Warning: No yearly real data to generate plots.")
        else:
            print("Warning: Real trade data is empty.")
    except Exception as e:
        print(f"Error processing real data: {e}")
        
    # --- 2. Process Scenario Data --- 
    print("\nProcessing Scenario Projections...")
    scenario_dataframes = {}
    scenario_plots = {}
    try:
        latest_files = find_latest_scenario_files(RESULTS_DIR)
        if latest_files:
            for scenario, file_path in latest_files.items():
                results = load_scenario_results(file_path)
                if results:
                    df = create_dataframe_from_results(results) 
                    if not df.empty:
                        scenario_dataframes[scenario] = df
                    else:
                        print(f"Warning: DataFrame created from {os.path.basename(file_path)} is empty.")
                else:
                     print(f"Skipping scenario {scenario} due to loading error.")
            
            if scenario_dataframes:
                scenario_plots = generate_comparison_plotly_figures(scenario_dataframes)
            else:
                print("Warning: No valid scenario data loaded.")
        else:
            print("Warning: No scenario result files found.")
    except Exception as e:
        print(f"Error processing scenario data: {e}")
        
    # --- 3. Generate Combined HTML Report --- 
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    report_file_path = os.path.join(REPORTS_DIR, f"combined_trade_report_{timestamp}.html")
    
    print(f"\nGenerating combined HTML report: {report_file_path}")
    try:
        generate_combined_html(real_data_summary, real_data_plots, scenario_dataframes, scenario_plots, report_file_path)
        print("Combined report generation complete.")
    except Exception as e:
        print(f"Error during combined HTML generation: {e}")

if __name__ == "__main__":
    main() 