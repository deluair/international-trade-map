"""
Test script for the structural transformation model.
"""
import os
import sys
import pandas as pd # Ensure pandas is imported
import plotly.graph_objects as go
import plotly.offline as pyo

# Add the project root directory to the Python path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

# Now import the model
from models.structural_transformation import StructuralTransformationModel

def generate_html_report(all_results, output_file="simulation_report_visuals.html"):
    """Generates an HTML report with visualizations from the simulation results."""

    # Prepare data for plotting
    years = sorted(all_results.keys())
    hhi = [all_results[y]['export_diversity_hhi'] for y in years]
    capability = [all_results[y]['capability_index'] for y in years]
    policy_effectiveness = [all_results[y]['industrial_policy_effectiveness'] for y in years]

    # Create plots
    # --- Metric Trends ---
    fig_metrics = go.Figure()
    fig_metrics.add_trace(go.Scatter(x=years, y=hhi, mode='lines+markers', name='Export Diversity HHI'))
    fig_metrics.add_trace(go.Scatter(x=years, y=capability, mode='lines+markers', name='Capability Index'))
    fig_metrics.add_trace(go.Scatter(x=years, y=policy_effectiveness, mode='lines+markers', name='Policy Effectiveness'))
    fig_metrics.update_layout(
        title='Key Metrics Over Time',
        xaxis_title='Year',
        yaxis_title='Index Value',
        legend_title='Metric',
        hovermode='x unified'
    )
    metrics_plot_div = pyo.plot(fig_metrics, include_plotlyjs=False, output_type='div')

    # --- Sector Exports (Example: Bar chart for the latest year) ---
    latest_year = max(years)
    latest_results = all_results[latest_year]
    sorted_sectors = sorted(latest_results['export_sectors'].items(), key=lambda x: x[1], reverse=True)
    sectors = [s[0] for s in sorted_sectors]
    values = [s[1] for s in sorted_sectors]

    fig_latest_exports = go.Figure([go.Bar(x=sectors, y=values)])
    fig_latest_exports.update_layout(
        title=f'Export Values by Sector ({latest_year})',
        xaxis_title='Sector',
        yaxis_title='Export Value (billion USD)'
    )
    latest_exports_plot_div = pyo.plot(fig_latest_exports, include_plotlyjs=False, output_type='div')

    # --- HTML Content ---
    html_content = f'''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Structural Transformation Simulation Report (2025-2030)</title>
    <script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
    <style>
        body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; line-height: 1.6; padding: 20px; max-width: 1200px; margin: auto; background-color: #f4f7f6; color: #333; }}
        h1, h2, h3 {{ color: #005f73; border-bottom: 2px solid #0a9396; padding-bottom: 8px; }}
        h1 {{ text-align: center; color: #003459; border-bottom: 3px solid #007ea7; }}
        .year-section {{ margin-bottom: 40px; padding: 20px; border: 1px solid #e0e0e0; border-radius: 8px; background-color: #ffffff; box-shadow: 0 2px 5px rgba(0,0,0,0.1); }}
        .summary-metrics ul {{ list-style-type: none; padding: 0; }}
        .summary-metrics li {{ margin-bottom: 8px; font-size: 1.1em; }}
        .summary-metrics strong {{ color: #007ea7; min-width: 250px; display: inline-block; }}
        table {{ width: 100%; border-collapse: collapse; margin-top: 20px; box-shadow: 0 1px 3px rgba(0,0,0,0.05); }}
        th, td {{ border: 1px solid #ccc; padding: 12px; text-align: left; }}
        th {{ background-color: #94d2bd; color: #005f73; font-weight: bold; }}
        tr:nth-child(even) {{ background-color: #e9f5f1; }}
        tr:hover {{ background-color: #d0e8e1; }}
        .plot-container {{ margin-top: 30px; padding: 20px; border: 1px solid #e0e0e0; border-radius: 8px; background-color: #ffffff; box-shadow: 0 2px 5px rgba(0,0,0,0.1); }}
    </style>
</head>
<body>
    <h1>Structural Transformation Simulation Report (2025-2030)</h1>

    <div class="plot-container">
        <h2>Overall Trends</h2>
        {metrics_plot_div}
    </div>

    <div class="plot-container">
        <h2>Latest Year Sector Performance ({latest_year})</h2>
        {latest_exports_plot_div}
    </div>
'''

    # Add yearly details
    for year in years:
        results = all_results[year]
        html_content += f'''
    <div class="year-section">
        <h2>Simulation Details for {year}</h2>
        <div class="summary-metrics">
            <h3>Summary Metrics:</h3>
            <ul>
                <li><strong>Export Diversification HHI:</strong> {results['export_diversity_hhi']:.4f}</li>
                <li><strong>Capability Index:</strong> {results['capability_index']:.4f}</li>
                <li><strong>Industrial Policy Effectiveness:</strong> {results['industrial_policy_effectiveness']:.4f}</li>
            </ul>
        </div>

        <h3>Export Values by Sector (billion USD):</h3>
        <table>
            <thead>
                <tr>
                    <th>Sector</th>
                    <th>Export Value (billion USD)</th>
                </tr>
            </thead>
            <tbody>
'''
        sorted_sectors = sorted(results['export_sectors'].items(), key=lambda x: x[1], reverse=True)
        for sector, value in sorted_sectors:
            html_content += f'''
                <tr>
                    <td>{sector}</td>
                    <td>{value:.3f}</td>
                </tr>
'''
        html_content += '''
            </tbody>
        </table>
    </div>
'''

    html_content += '''
</body>
</html>
'''
    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(html_content)
        print(f"\nHTML report with visuals generated: {output_file}")
    except IOError as e:
        print(f"\nError writing HTML report: {e}")


def main():
    """Run a test of the structural transformation model."""
    print("Testing Structural Transformation Model with real trade data")
    print("-" * 70)
    
    # Create config
    print("Creating configuration...")
    config = {
        'data_path': os.path.join('data', 'bd_trade_data.csv'),
        # Add any other config parameters needed
    }
    print(f"Configuration created: {config}")
    
    # Initialize model
    print("Initializing StructuralTransformationModel...")
    try:
        model = StructuralTransformationModel(config)
        print("Model initialized successfully.")
    except Exception as e:
        print(f"ERROR initializing model: {e}")
        return
    
    # Test for multiple years
    test_years = list(range(2025, 2031))
    all_results = {} # Store results for all years

    print(f"\nSimulating for years: {test_years}")

    for year in test_years:
        print("\n" + "=" * 50)
        print(f"SIMULATING YEAR {year}")
        print("=" * 50)
        
        # Run simulation for this year
        print(f"Running simulate_step for {year}...")
        try:
            results = model.simulate_step(year)
            print(f"Simulation step for {year} completed.")
        except Exception as e:
            print(f"ERROR during simulate_step for {year}: {e}")
            print(f"Skipping year {year} due to error.")
            continue
            
        all_results[year] = results # Store results
        
        # Display results
        print("\nSummary of Results:")
        print(f"Export Diversification HHI: {results['export_diversity_hhi']:.4f}")
        print(f"Capability Index: {results['capability_index']:.4f}")
        print(f"Industrial Policy Effectiveness: {results['industrial_policy_effectiveness']:.4f}")
        
        print("\nExport Values by Sector (billion USD):")
        for sector, value in sorted(results['export_sectors'].items(), key=lambda x: x[1], reverse=True):
            print(f"  - {sector}: ${value:.3f} billion")

    # Generate the HTML report after the loop only if there are results
    if all_results:
        print("\nGenerating HTML report with visuals...")
        generate_html_report(all_results)
        print("HTML report generation process finished.")
    else:
        print("\nNo simulation results were generated. Skipping report generation.")

if __name__ == "__main__":
    main()
