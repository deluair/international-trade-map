"""
Generates a comparison report for multiple trade simulation scenarios.

Finds simulation result JSON files in the 'results/' directory,
loads them, creates DataFrames, and generates comparison plots.
"""

import os
import sys
import json
import glob
import pandas as pd
from datetime import datetime
# Import Plotly libraries
import plotly.graph_objects as go
import plotly.io as pio
from plotly.subplots import make_subplots
import plotly.express as px

# Add project root to path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

# Import necessary functions from plot_utils
try:
    from visualization.plot_utils import create_dataframe_from_results
except ImportError as e:
    print(f"Error importing from visualization.plot_utils: {e}")
    print("Please ensure plot_utils.py is in the visualization directory and accessible.")
    # Provide fallback definitions if needed, or exit
    sys.exit(1)

RESULTS_DIR = os.path.join(project_root, 'results')
REPORTS_DIR = os.path.join(project_root, 'reports')

def find_latest_scenario_files(results_dir):
    """Find the latest result file for each scenario (baseline, optimistic, pessimistic)."""
    scenario_files = {}
    scenarios = ['baseline', 'optimistic', 'pessimistic']
    
    for scenario in scenarios:
        pattern = os.path.join(results_dir, f"bd_projection_results_{scenario}_*.json")
        files = glob.glob(pattern)
        if files:
            latest_file = max(files, key=os.path.getctime)
            scenario_files[scenario] = latest_file
            print(f"Found latest file for {scenario}: {os.path.basename(latest_file)}")
        else:
            print(f"Warning: No result file found for scenario: {scenario}")
            
    return scenario_files

def load_results(file_path):
    """Load simulation results from a single JSON file."""
    try:
        with open(file_path, 'r') as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading {file_path}: {e}")
        return None

def main():
    print("Generating Scenario Comparison Report...")
    os.makedirs(REPORTS_DIR, exist_ok=True)
    
    # 1. Find the latest result files for each scenario
    latest_files = find_latest_scenario_files(RESULTS_DIR)
    
    if not latest_files:
        print("Error: No scenario result files found in the 'results' directory. Cannot generate comparison.")
        return

    # 2. Load results and create DataFrames
    scenario_dataframes = {}
    for scenario, file_path in latest_files.items():
        results = load_results(file_path)
        if results:
            df = create_dataframe_from_results(results) # Use imported function
            if not df.empty:
                scenario_dataframes[scenario] = df
            else:
                print(f"Warning: DataFrame created from {os.path.basename(file_path)} is empty.")
        else:
             print(f"Skipping scenario {scenario} due to loading error.")
             
    if not scenario_dataframes:
        print("Error: No valid data loaded from scenario files. Cannot generate comparison.")
        return
        
    # 3. Generate comparison plots (saving to PDF) - REMOVED PDF logic
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    # report_file_path = os.path.join(REPORTS_DIR, f"scenario_comparison_report_{timestamp}.pdf") # Old PDF path
    html_report_file_path = os.path.join(REPORTS_DIR, f"scenario_comparison_report_{timestamp}.html") # New HTML path
    
    # print(f"\nGenerating comparison plots and saving to: {report_file_path}") # Old message
    print(f"\nGenerating comparison figures for HTML report...")
    
    try:
        # ---- START: New Plotly and HTML Generation ----
        comparison_figures = generate_comparison_plotly_figures(scenario_dataframes)
        
        print(f"Generating HTML report: {html_report_file_path}")
        generate_comparison_html(scenario_dataframes, comparison_figures, html_report_file_path)
        
        print("Successfully generated comparison HTML report.")
        # ---- END: New Plotly and HTML Generation ----
            
    except Exception as e:
        print(f"Error during plot or HTML generation: {e}")

# Placeholder for new functions (will be added next)
def generate_comparison_plotly_figures(scenario_dataframes):
    """Generates Plotly figures comparing scenarios."""
    figures = {}
    metrics_to_plot = [
        'Total Exports (billion USD)',
        'Capability Index',
        'Export Diversification HHI',
        # Add more metrics if they are consistently available and desired
        # 'Trade Balance (billion USD)', 
        # 'Industrial Policy Effectiveness',
    ]
    colors = px.colors.qualitative.Plotly # Get a default color sequence
    
    print("Creating comparison plots...")
    for i, metric in enumerate(metrics_to_plot):
        fig = go.Figure()
        color_idx = 0
        for scenario, df in scenario_dataframes.items():
            if metric in df.columns:
                # Ensure data is numeric and drop NAs for plotting lines
                plot_df = df[['Year', metric]].copy()
                plot_df[metric] = pd.to_numeric(plot_df[metric], errors='coerce')
                plot_df = plot_df.dropna(subset=[metric])
                
                if not plot_df.empty:
                    fig.add_trace(go.Scatter(
                        x=plot_df['Year'], 
                        y=plot_df[metric], 
                        mode='lines+markers',
                        name=scenario.capitalize(),
                        line=dict(color=colors[color_idx % len(colors)])
                    ))
                    color_idx += 1
            else:
                print(f"Metric '{metric}' not found in scenario '{scenario}'. Skipping.")

        # Basic layout customization
        y_title = metric
        if '(billion USD)' in metric:
             y_title = 'Billion USD'
        elif '(%)' in metric:
             y_title = 'Percentage (%)'
        elif 'HHI' in metric:
             y_title = 'HHI Value'
             
        fig.update_layout(
            title=f'{metric} Comparison', 
            xaxis_title='Year', 
            yaxis_title=y_title, 
            hovermode='x unified',
            legend_title='Scenario'
        )
        figures[metric.replace(' ', '_').lower()] = fig # Use a key based on metric name
        
    print(f"Generated {len(figures)} comparison figures.")
    return figures

def generate_comparison_html(scenario_dataframes, figures, output_file):
    """Generates an HTML report comparing scenarios with embedded Plotly figures."""
    print("Constructing HTML report...")
    # Basic HTML structure and CSS (can be enhanced)
    html_start = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Scenario Comparison Report</title>
    <script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
    <style>
        body { 
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; 
            margin: 20px; 
            background-color: #f4f7f6; 
            color: #333; 
        }
        .container { 
            max-width: 1200px; 
            margin: auto; 
            background-color: #fff; 
            padding: 30px; 
            border-radius: 8px; 
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        } 
        h1, h2, h3 { 
            color: #0056b3; /* Dark blue */
            border-bottom: 2px solid #007bff; /* Lighter blue border */
            padding-bottom: 8px;
            margin-top: 25px;
            margin-bottom: 15px;
        } 
        h1 { text-align: center; margin-bottom: 30px; }
        .figure-container { 
            margin-bottom: 30px; 
            border: 1px solid #ddd; 
            padding: 20px; 
            border-radius: 5px; 
            background-color: #fff; 
        } 
        table { 
            width: 100%; 
            border-collapse: collapse; 
            margin-top: 20px; 
            margin-bottom: 30px;
        }
        th, td { 
            border: 1px solid #ccc; 
            padding: 10px 12px; 
            text-align: left; 
            vertical-align: top;
        }
        th { 
            background-color: #e9ecef; 
            font-weight: 600;
            position: sticky; /* Make header sticky */
            top: 0; /* Stick to the top */
        }
        tr:nth-child(even) { background-color: #f8f9fa; }
        td:nth-child(n+2) { text-align: right; } /* Right-align numeric data */
        .footer { text-align: center; margin-top: 40px; font-size: 0.9em; color: #666; }
    </style>
</head>
<body>
<div class="container">
    <h1>Simulation Scenario Comparison</h1>
    <p>Comparison of baseline, optimistic, and pessimistic scenarios for Bangladesh trade dynamics (2024-2030 projections based on 2023 simulation).</p>
"""
    
    # --- Summary Table Implementation --- 
    html_summary = """
    <h2>Final Year (2030) Summary</h2>
    <table>
        <thead>
            <tr>
                <th>Metric</th>
                <th>Baseline</th>
                <th>Optimistic</th>
                <th>Pessimistic</th>
            </tr>
        </thead>
        <tbody>
    """
    
    summary_metrics = [
        'Total Exports (billion USD)',
        'Capability Index',
        'Export Diversification HHI',
        'Industrial Policy Effectiveness' # Example: add if available
    ]
    
    final_year = 2030 # Hardcoded for now, could be dynamic
    summary_data = {metric: {} for metric in summary_metrics}
    
    for scenario, df in scenario_dataframes.items():
        final_row = df[df['Year'] == final_year]
        if not final_row.empty:
            for metric in summary_metrics:
                if metric in df.columns:
                     # Get the value, convert NA to 'N/A' string for display
                    value = final_row[metric].iloc[0]
                    summary_data[metric][scenario] = value if pd.notna(value) else 'N/A'
                else:
                    summary_data[metric][scenario] = 'N/A' # Metric not in DataFrame
        else:
             for metric in summary_metrics:
                 summary_data[metric][scenario] = 'N/A' # No data for final year

    # Function to format summary numbers
    def format_summary(value):
        if value == 'N/A': return value
        try:
            # Basic formatting, adjust precision as needed
            if abs(float(value)) < 1: return f"{float(value):.3f}"
            else: return f"{float(value):.2f}"
        except: return 'N/A'

    # Populate table rows
    for metric in summary_metrics:
        html_summary += f"""
            <tr>
                <td>{metric}</td>
                <td>{format_summary(summary_data[metric].get('baseline', 'N/A'))}</td>
                <td>{format_summary(summary_data[metric].get('optimistic', 'N/A'))}</td>
                <td>{format_summary(summary_data[metric].get('pessimistic', 'N/A'))}</td>
            </tr>
        """
        
    html_summary += """
        </tbody>
    </table>
    """
    # --- End Summary Table --- 

    html_figures = """
    <h2>Comparison Plots</h2>
"""
    # Embed each figure
    for fig_key, fig in figures.items():
        fig_html = pio.to_html(fig, full_html=False, include_plotlyjs=False)
        # You can use the fig_key or the figure's title for a heading
        title = fig.layout.title.text if fig.layout.title.text else fig_key.replace("_", " ").title()
        html_figures += f"""
    <div class="figure-container">
        <h3>{title}</h3>
        {fig_html}
    </div>
"""

    html_end = f"""
    <div class="footer">
        Report generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
    </div>
</div> <!-- Close container -->
</body>
</html>
"""
    
    # Combine parts (Summary first, then figures)
    full_html = html_start + html_summary + html_figures + html_end
    
    # Write to file
    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(full_html)
        print(f"HTML report saved to: {output_file}")
    except Exception as e:
        print(f"Error writing HTML file: {e}")

if __name__ == "__main__":
    main() 